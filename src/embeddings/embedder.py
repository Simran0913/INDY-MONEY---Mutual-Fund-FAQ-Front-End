"""
embedder.py
-----------
Creates embeddings for text chunks using sentence-transformers.

Model: all-MiniLM-L6-v2 (fast, good quality, no API key needed, 384-dim)
- Runs fully locally
- ~80MB model download on first use
- Suitable for a corpus of 15-25 sources / ~200-400 chunks

No API key required for embeddings.
"""

import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)

_model_instance = None   # singleton


def _get_model(model_name: str = "all-MiniLM-L6-v2"):
    """Load (or reuse) the sentence-transformer model singleton."""
    global _model_instance
    if _model_instance is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {model_name} ...")
            _model_instance = SentenceTransformer(model_name)
            logger.info(f"Embedding model loaded. Dimension: {_model_instance.get_sentence_embedding_dimension()}")
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
    return _model_instance


def embed_texts(
    texts: List[str],
    model_name: str = "all-MiniLM-L6-v2",
    batch_size: int = 32,
    show_progress: bool = True,
) -> np.ndarray:
    """
    Embed a list of text strings.

    Args:
        texts:        List of strings to embed.
        model_name:   Sentence-transformer model name.
        batch_size:   Batch size for encoding.
        show_progress: Show tqdm progress bar.

    Returns:
        numpy array of shape (len(texts), embedding_dim)
    """
    if not texts:
        return np.array([])

    model = _get_model(model_name)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=True,   # L2-normalise → cosine = dot product
    )
    logger.info(f"Embedded {len(texts)} texts → shape {embeddings.shape}")
    return embeddings


def embed_query(query: str, model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """
    Embed a single query string.

    Returns:
        1D numpy array of shape (embedding_dim,)
    """
    model = _get_model(model_name)
    vec = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return vec


def get_embedding_dim(model_name: str = "all-MiniLM-L6-v2") -> int:
    """Return the embedding dimension for the loaded model."""
    return _get_model(model_name).get_sentence_embedding_dimension()
