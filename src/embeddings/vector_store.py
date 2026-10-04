"""
vector_store.py
---------------
FAISS-based local vector store.

Implements:
  build_index(chunks)   → build and persist FAISS index + metadata
  load_index()          → load index + metadata from disk
  search(query, top_k)  → semantic search returning chunks with scores

Storage layout (data/vector_store/):
  index.faiss      FAISS flat index (inner-product, since vecs are L2-normalised)
  metadata.json    Parallel list of chunk metadata (same order as FAISS index)

Why FAISS Flat (not IVF)?
  Corpus is ~200-400 chunks — flat exact search is faster and more accurate
  than approximate IVF at this scale.
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Paths
_DEFAULT_INDEX_DIR = Path(__file__).resolve().parents[2] / "data" / "vector_store"
_INDEX_FILE        = "index.faiss"
_METADATA_FILE     = "metadata.json"


# ── Build ──────────────────────────────────────────────────────────────────────

def build_index(
    chunks: List[dict],
    embeddings: np.ndarray,
    index_dir: Optional[Path] = None,
) -> None:
    """
    Build a FAISS flat index from chunk embeddings and persist to disk.

    Args:
        chunks:     List of chunk dicts (metadata, same order as embeddings).
        embeddings: numpy array shape (N, dim), L2-normalised.
        index_dir:  Directory to save index files. Defaults to data/vector_store/.
    """
    try:
        import faiss
    except ImportError:
        raise ImportError("faiss-cpu not installed. Run: pip install faiss-cpu")

    if len(chunks) != len(embeddings):
        raise ValueError(
            f"chunks ({len(chunks)}) and embeddings ({len(embeddings)}) must have same length"
        )

    index_dir = Path(index_dir or _DEFAULT_INDEX_DIR)
    index_dir.mkdir(parents=True, exist_ok=True)

    dim = embeddings.shape[1]
    # IndexFlatIP = exact inner-product search
    # Since embeddings are L2-normalised, inner product == cosine similarity
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype(np.float32))

    # Save FAISS index
    faiss_path = index_dir / _INDEX_FILE
    faiss.write_index(index, str(faiss_path))
    logger.info(f"FAISS index saved → {faiss_path} ({index.ntotal} vectors, dim={dim})")

    # Save metadata (strip 'text' to keep metadata.json small; text lives in chunks)
    metadata = []
    for chunk in chunks:
        meta = {k: v for k, v in chunk.items()}   # include text for retrieval
        metadata.append(meta)

    meta_path = index_dir / _METADATA_FILE
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Metadata saved → {meta_path} ({len(metadata)} chunks)")


# ── Load ───────────────────────────────────────────────────────────────────────

_cached_index    = None
_cached_metadata = None


def load_index(index_dir: Optional[Path] = None) -> tuple:
    """
    Load FAISS index and metadata from disk.

    Returns:
        (faiss_index, metadata_list)
    """
    global _cached_index, _cached_metadata

    if _cached_index is not None and _cached_metadata is not None:
        return _cached_index, _cached_metadata

    try:
        import faiss
    except ImportError:
        raise ImportError("faiss-cpu not installed. Run: pip install faiss-cpu")

    index_dir  = Path(index_dir or _DEFAULT_INDEX_DIR)
    faiss_path = index_dir / _INDEX_FILE
    meta_path  = index_dir / _METADATA_FILE

    if not faiss_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found at {faiss_path}. Run the index build step first."
        )
    if not meta_path.exists():
        raise FileNotFoundError(
            f"Metadata not found at {meta_path}. Run the index build step first."
        )

    _cached_index    = faiss.read_index(str(faiss_path))
    _cached_metadata = json.loads(meta_path.read_text(encoding="utf-8"))

    logger.info(
        f"Index loaded: {_cached_index.ntotal} vectors, "
        f"{len(_cached_metadata)} metadata entries"
    )
    return _cached_index, _cached_metadata


def invalidate_cache() -> None:
    """Clear the in-memory index cache (use after rebuilding index)."""
    global _cached_index, _cached_metadata
    _cached_index    = None
    _cached_metadata = None


# ── Search ─────────────────────────────────────────────────────────────────────

def search(
    query_embedding: np.ndarray,
    top_k: int = 5,
    index_dir: Optional[Path] = None,
    scheme_filter: Optional[str] = None,
) -> List[dict]:
    """
    Search the FAISS index and return the top_k most relevant chunks.

    Args:
        query_embedding: 1D numpy array (embedding_dim,), L2-normalised.
        top_k:           Number of results to return.
        index_dir:       Optional override for index directory.
        scheme_filter:   If provided, prefer results matching this scheme name.

    Returns:
        List of dicts, each containing:
          chunk_id, source_id, scheme, title, source_url, organization,
          source_type, section, last_updated, text, score
        Sorted by relevance score descending.
    """
    index, metadata = load_index(index_dir)

    # Reshape to (1, dim) for FAISS
    query_vec = query_embedding.astype(np.float32).reshape(1, -1)

    # Retrieve more candidates if filtering by scheme, to ensure top_k results
    fetch_k = min(top_k * 3 if scheme_filter else top_k, index.ntotal)

    scores, indices = index.search(query_vec, fetch_k)
    scores  = scores[0].tolist()   # flatten from (1, fetch_k)
    indices = indices[0].tolist()

    results = []
    for score, idx in zip(scores, indices):
        if idx < 0 or idx >= len(metadata):   # FAISS returns -1 for empty slots
            continue
        chunk = dict(metadata[idx])
        chunk["score"] = round(float(score), 4)
        results.append(chunk)

    # If scheme_filter, boost results matching the scheme to the top
    if scheme_filter:
        matching    = [r for r in results if scheme_filter.lower() in r.get("scheme", "").lower()]
        nonmatching = [r for r in results if scheme_filter.lower() not in r.get("scheme", "").lower()]
        # Within each group, already sorted by score
        results = matching + nonmatching

    return results[:top_k]
