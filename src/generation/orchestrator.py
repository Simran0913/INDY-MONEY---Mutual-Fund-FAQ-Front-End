"""
orchestrator.py
---------------
Single entry point for the full RAG pipeline.

Flow:
  User Query
    → Safety check (PII / advice / out-of-scope)
    → Scheme detection
    → Retrieval (FAISS)
    → LLM generation
    → Citation validation
    → Final response

Usage:
    from src.generation.orchestrator import ask

    result = ask("What is the exit load of SBI Bluechip Fund?")
    print(result["answer"])
    print(result["source_url"])
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def ask(
    question        : str,
    api_key         : str = "",
    model           : str = "gpt-4o-mini",
    temperature     : float = 0.0,
    max_tokens      : int = 512,
    top_k           : int = 5,
    min_score       : float = 0.25,
    embedding_model : str = "all-MiniLM-L6-v2",
) -> dict:
    """
    Full RAG pipeline for a single user question.

    Args:
        question:         Raw user question.
        api_key:          OpenAI API key.
        model:            OpenAI model name.
        temperature:      LLM temperature.
        max_tokens:       Max LLM output tokens.
        top_k:            Number of chunks to retrieve.
        min_score:        Minimum retrieval score threshold.
        embedding_model:  Sentence-transformer model name.

    Returns:
        dict with:
          answer        str    The answer text (max 3 sentences for factual)
          source_url    str    ONE official source URL
          last_updated  str    Last-updated date from source
          disclaimer    str    Standard risk disclaimer
          category      str    QueryCategory (for frontend display logic)
          is_safe       bool   Whether query passed safety check
          is_valid      bool   Whether citation validation passed
          chunks_used   int    Number of chunks used for generation
          issues        list   Any citation issues (empty if clean)
    """
    from src.safety.guard         import safety_check
    from src.retrieval.retriever  import retrieve_with_dedup, extract_scheme_from_query
    from src.generation.generator import generate_answer
    from src.citations.validator  import validate_and_format, format_final_response, DISCLAIMER

    # ── Step 1: Safety check ───────────────────────────────────────────────────
    safety = safety_check(question)

    if not safety.is_safe:
        return {
            "answer"      : safety.response,
            "source_url"  : None,
            "last_updated": None,
            "disclaimer"  : DISCLAIMER,
            "category"    : safety.category,
            "is_safe"     : False,
            "is_valid"    : True,   # safe responses are always "valid"
            "chunks_used" : 0,
            "issues"      : [],
        }

    # ── Step 2: Detect scheme ──────────────────────────────────────────────────
    scheme_filter = extract_scheme_from_query(question)
    logger.info(f"Scheme detected: {scheme_filter or 'None (all schemes)'}")

    # ── Step 3: Retrieve chunks ────────────────────────────────────────────────
    try:
        chunks = retrieve_with_dedup(
            query        = question,
            top_k        = top_k,
            min_score    = min_score,
            scheme_filter= scheme_filter,
            model_name   = embedding_model,
        )
        logger.info(f"Retrieved {len(chunks)} chunks")
    except FileNotFoundError:
        # Index not built yet
        logger.error("FAISS index not found. Run: python -m src.embeddings.build_index")
        return {
            "answer"      : (
                "The knowledge base is not ready yet. "
                "Please run the index build step: python -m src.embeddings.build_index"
            ),
            "source_url"  : None,
            "last_updated": None,
            "disclaimer"  : DISCLAIMER,
            "category"    : "FACTUAL_ALLOWED",
            "is_safe"     : True,
            "is_valid"    : False,
            "chunks_used" : 0,
            "issues"      : ["index_not_built"],
        }
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        return {
            "answer"      : "I encountered an error while searching the knowledge base. Please try again.",
            "source_url"  : None,
            "last_updated": None,
            "disclaimer"  : DISCLAIMER,
            "category"    : "FACTUAL_ALLOWED",
            "is_safe"     : True,
            "is_valid"    : False,
            "chunks_used" : 0,
            "issues"      : [f"retrieval_error: {str(e)}"],
        }

    # ── Step 4: Generate answer ────────────────────────────────────────────────
    gen_result = generate_answer(
        question   = question,
        chunks     = chunks,
        api_key    = api_key,
        model      = model,
        temperature= temperature,
        max_tokens = max_tokens,
    )

    # ── Step 5: Citation validation ────────────────────────────────────────────
    validation = validate_and_format(
        answer      = gen_result.answer,
        source_url  = gen_result.source_url,
        last_updated= gen_result.last_updated,
        chunks      = chunks,
    )

    # ── Step 6: Format and return ──────────────────────────────────────────────
    formatted = format_final_response(validation)
    formatted.update({
        "category"  : "FACTUAL_ALLOWED",
        "is_safe"   : True,
        "chunks_used": gen_result.chunks_used,
    })

    return formatted
