"""
retriever.py
------------
Semantic retrieval over the FAISS vector store.

Flow:
  1. Embed the user query.
  2. Search FAISS index (optionally filtered by scheme).
  3. Apply minimum relevance score threshold.
  4. Return ranked results with full metadata.

If no results meet the minimum score threshold → returns empty list.
The caller (generation layer) must handle this gracefully and NOT guess.
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    top_k: int = 5,
    min_score: float = 0.25,
    scheme_filter: Optional[str] = None,
    model_name: str = "all-MiniLM-L6-v2",
) -> List[dict]:
    """
    Retrieve the most relevant chunks for a given query.

    Args:
        query:         Natural language question.
        top_k:         Number of results to return (before score filtering).
        min_score:     Minimum cosine similarity score (0-1). Chunks below this
                       are discarded. Prevents hallucination from irrelevant context.
        scheme_filter: If provided, boost/filter results for this scheme name.
        model_name:    Sentence-transformer model for query embedding.

    Returns:
        List of relevant chunk dicts, each with:
          chunk_id, source_id, scheme, title, source_url, organization,
          source_type, section, last_updated, text, score

        Returns empty list if no chunks meet the min_score threshold.
    """
    from src.embeddings.embedder      import embed_query
    from src.embeddings.vector_store  import search

    if not query or not query.strip():
        logger.warning("Empty query passed to retriever.")
        return []

    # 1. Embed query
    query_embedding = embed_query(query.strip(), model_name=model_name)

    # 2. Search FAISS
    results = search(
        query_embedding=query_embedding,
        top_k=top_k,
        scheme_filter=scheme_filter,
    )

    # 3. Filter by minimum score
    filtered = [r for r in results if r.get("score", 0.0) >= min_score]

    if not filtered:
        logger.info(
            f"No results above min_score={min_score} for query: '{query[:80]}...'"
            if len(query) > 80 else
            f"No results above min_score={min_score} for query: '{query}'"
        )
    else:
        logger.info(
            f"Retrieved {len(filtered)} chunks (top score: {filtered[0]['score']}) "
            f"for query: '{query[:60]}'"
        )

    return filtered


def retrieve_with_dedup(
    query: str,
    top_k: int = 5,
    min_score: float = 0.25,
    scheme_filter: Optional[str] = None,
    model_name: str = "all-MiniLM-L6-v2",
) -> List[dict]:
    """
    Same as retrieve() but deduplicates by source_id — useful when the same source
    produces multiple highly-similar chunks.

    Returns at most one chunk per source_id (the highest-scoring one).
    Still returns up to top_k total results.
    """
    results = retrieve(
        query=query,
        top_k=top_k * 2,   # fetch extra to compensate for dedup
        min_score=min_score,
        scheme_filter=scheme_filter,
        model_name=model_name,
    )

    seen_sources = set()
    deduped = []
    for r in results:
        sid = r.get("source_id", "")
        if sid not in seen_sources:
            seen_sources.add(sid)
            deduped.append(r)
        if len(deduped) >= top_k:
            break

    return deduped


def extract_scheme_from_query(query: str) -> Optional[str]:
    """
    Simple keyword-based scheme detector.
    Returns the matched scheme name string if found in query, else None.
    Used to set scheme_filter automatically.
    """
    query_lower = query.lower()

    scheme_keywords = {
        "SBI Bluechip Fund"            : ["bluechip", "blue chip", "large cap", "sbi bluechip"],
        "SBI Magnum Tax Gain Scheme"   : ["magnum tax", "tax gain", "elss", "80c", "tax saving",
                                           "taxgain", "tax saver"],
        "SBI Liquid Fund"              : ["liquid fund", "sbi liquid", "liquid scheme"],
        "SBI Small Cap Fund"           : ["small cap", "smallcap", "sbi small cap"],
        "SBI Balanced Advantage Fund"  : ["balanced advantage", "dynamic asset allocation",
                                           "balanced fund", "sbi balanced"],
    }

    for scheme_name, keywords in scheme_keywords.items():
        for kw in keywords:
            if kw in query_lower:
                logger.debug(f"Scheme detected from query: {scheme_name}")
                return scheme_name

    return None  # No specific scheme mentioned → search all
