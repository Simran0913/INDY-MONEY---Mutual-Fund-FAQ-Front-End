"""
generator.py
------------
RAG answer generator.

Flow:
  1. Build context block from retrieved chunks.
  2. Send [system prompt] + [user prompt with context] to OpenAI LLM.
  3. Parse the structured response (Answer / Source / Last updated).
  4. Return GenerationResult.

If the LLM output doesn't contain a valid source → citation validation will catch it.
If retrieval returned no chunks → return FALLBACK_RESPONSE without calling the LLM.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    answer          : str
    source_url      : Optional[str]   = None
    last_updated    : Optional[str]   = None
    raw_llm_output  : Optional[str]   = None
    used_fallback   : bool            = False
    chunks_used     : int             = 0
    error           : Optional[str]   = None


# ── Response parser ───────────────────────────────────────────────────────────

_ANSWER_PATTERN      = re.compile(r"Answer:\s*(.+?)(?=Source:|Last updated|$)", re.DOTALL | re.IGNORECASE)
_SOURCE_PATTERN      = re.compile(r"Source:\s*(https?://\S+)", re.IGNORECASE)
_LAST_UPDATED_PATTERN= re.compile(r"Last updated from sources:\s*(.+?)(?:\n|$)", re.IGNORECASE)


def _parse_llm_response(text: str) -> dict:
    """
    Parse structured LLM output into answer, source_url, last_updated.
    Returns dict with those three keys (values may be None if not found).
    """
    answer_match      = _ANSWER_PATTERN.search(text)
    source_match      = _SOURCE_PATTERN.search(text)
    last_updated_match= _LAST_UPDATED_PATTERN.search(text)

    answer = answer_match.group(1).strip() if answer_match else text.strip()
    # Remove trailing disclaimer from answer body (will be added by citation layer)
    answer = re.sub(
        r"mutual fund investments? (are )?subject to market risks.*",
        "",
        answer,
        flags=re.IGNORECASE | re.DOTALL,
    ).strip()

    return {
        "answer"      : answer,
        "source_url"  : source_match.group(1).strip() if source_match else None,
        "last_updated": last_updated_match.group(1).strip() if last_updated_match else None,
    }


# ── Generator ─────────────────────────────────────────────────────────────────

def generate_answer(
    question: str,
    chunks: List[dict],
    api_key: str = "",
    model: str = "gpt-4o-mini",
    temperature: float = 0.0,
    max_tokens: int = 512,
) -> GenerationResult:
    """
    Generate a grounded factual answer from retrieved chunks.

    Args:
        question:    The user's question (already classified as FACTUAL_ALLOWED).
        chunks:      Retrieved chunks from the vector store.
        api_key:     OpenAI API key.
        model:       OpenAI model name.
        temperature: LLM temperature (0.0 = deterministic).
        max_tokens:  Max tokens for the response.

    Returns:
        GenerationResult with answer, source_url, last_updated, metadata.
    """
    from src.generation.prompt import (
        SYSTEM_PROMPT, FALLBACK_RESPONSE, build_user_prompt
    )

    # ── No chunks → fallback immediately ──────────────────────────────────────
    if not chunks:
        logger.warning(f"No chunks for question: '{question[:60]}'. Returning fallback.")
        return GenerationResult(
            answer       = FALLBACK_RESPONSE,
            used_fallback= True,
            chunks_used  = 0,
        )

    # ── Build prompt ───────────────────────────────────────────────────────────
    user_prompt = build_user_prompt(question, chunks)

    # ── Call OpenAI API ────────────────────────────────────────────────────────
    if not api_key:
        logger.error("OPENAI_API_KEY not set. Cannot call LLM.")
        return GenerationResult(
            answer= FALLBACK_RESPONSE,
            used_fallback= True,
            error= "OPENAI_API_KEY not configured",
            chunks_used= len(chunks),
        )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model      = model,
            temperature= temperature,
            max_tokens = max_tokens,
            messages   = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
        )

        raw_output = response.choices[0].message.content.strip()
        logger.info(f"LLM response ({len(raw_output)} chars) for: '{question[:60]}'")

    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        # Fallback: build answer directly from best chunk without LLM
        return _build_fallback_from_chunks(chunks, question, error=str(e))

    # ── Parse structured response ──────────────────────────────────────────────
    parsed = _parse_llm_response(raw_output)

    # If source not parsed from LLM output, use source from top chunk
    source_url = parsed["source_url"]
    if not source_url and chunks:
        source_url = chunks[0].get("source_url")

    # If last_updated not parsed, use from top chunk
    last_updated = parsed["last_updated"]
    if not last_updated and chunks:
        last_updated = chunks[0].get("last_updated")

    return GenerationResult(
        answer        = parsed["answer"],
        source_url    = source_url,
        last_updated  = last_updated,
        raw_llm_output= raw_output,
        chunks_used   = len(chunks),
    )


def _build_fallback_from_chunks(
    chunks: List[dict],
    question: str,
    error: Optional[str] = None,
) -> GenerationResult:
    """
    Build a best-effort answer from the top chunk when LLM is unavailable.
    Used as a graceful degradation path.

    The answer is taken verbatim from the source — no invention.
    """
    from src.generation.prompt import FALLBACK_RESPONSE

    if not chunks:
        return GenerationResult(
            answer       = FALLBACK_RESPONSE,
            used_fallback= True,
            error        = error,
        )

    top = chunks[0]
    # Take first 3 sentences from the top chunk text as the answer
    text  = top.get("text", "").strip()
    sents = re.split(r"(?<=[.!?])\s+", text)
    answer_text = " ".join(sents[:3]).strip()

    if not answer_text:
        answer_text = FALLBACK_RESPONSE

    return GenerationResult(
        answer        = answer_text,
        source_url    = top.get("source_url"),
        last_updated  = top.get("last_updated"),
        used_fallback = True,
        chunks_used   = len(chunks),
        error         = error,
    )
