"""
build_index.py
--------------
End-to-end index builder:
  1. Seed processed documents (if not already present)
  2. Run chunking pipeline (clean + chunk)
  3. Embed all chunks
  4. Build and save FAISS index

Run:
    python -m src.embeddings.build_index
    python -m src.embeddings.build_index --force   # force rebuild
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config.settings       import (
    PROCESSED_DIR, VECTOR_STORE_DIR, EMBEDDING_MODEL,
    CHUNK_SIZE, CHUNK_OVERLAP, LOGS_DIR
)
from src.ingestion.seed_data   import seed_processed_documents
from src.chunking.cleaner      import clean_text
from src.chunking.chunker      import chunk_document, save_chunks, load_chunks
from src.embeddings.embedder   import embed_texts
from src.embeddings.vector_store import build_index, invalidate_cache

CHUNKS_FILE = PROCESSED_DIR / "chunks.jsonl"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / "build_index.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def run_build_index(force: bool = False) -> dict:
    """
    Full pipeline: seed → chunk → embed → index.

    Args:
        force: If True, re-run all steps even if artifacts exist.

    Returns:
        Summary dict.
    """
    logger.info("=" * 60)
    logger.info("Starting index build pipeline")
    logger.info("=" * 60)

    # ── Step 1: Seed processed documents ─────────────────────────────────────
    logger.info("Step 1/4: Seeding processed documents...")
    seed_result = seed_processed_documents(PROCESSED_DIR, force=force)
    logger.info(f"Seed result: {seed_result}")

    # ── Step 2: Clean and chunk all documents ─────────────────────────────────
    if not force and CHUNKS_FILE.exists():
        logger.info(f"Step 2/4: Loading cached chunks from {CHUNKS_FILE}")
        all_chunks = load_chunks(CHUNKS_FILE)
    else:
        logger.info("Step 2/4: Cleaning and chunking documents...")
        json_files = sorted(PROCESSED_DIR.glob("SRC*.json"))

        if not json_files:
            return {"status": "error", "message": "No processed documents found"}

        all_chunks = []
        for jf in json_files:
            doc = json.loads(jf.read_text(encoding="utf-8"))
            doc["text"] = clean_text(doc.get("text", ""), doc.get("source_id", ""))
            chunks = chunk_document(doc, CHUNK_SIZE, CHUNK_OVERLAP)
            all_chunks.extend(chunks)
            logger.info(f"[{doc.get('source_id')}] → {len(chunks)} chunks")

        save_chunks(all_chunks, CHUNKS_FILE)
        logger.info(f"Total chunks: {len(all_chunks)} saved to {CHUNKS_FILE}")

    if not all_chunks:
        return {"status": "error", "message": "No chunks produced"}

    # ── Step 3: Embed all chunks ───────────────────────────────────────────────
    logger.info(f"Step 3/4: Embedding {len(all_chunks)} chunks with {EMBEDDING_MODEL}...")
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = embed_texts(texts, model_name=EMBEDDING_MODEL, show_progress=True)
    logger.info(f"Embeddings shape: {embeddings.shape}")

    # ── Step 4: Build FAISS index ─────────────────────────────────────────────
    logger.info("Step 4/4: Building FAISS index...")
    invalidate_cache()
    build_index(all_chunks, embeddings, index_dir=VECTOR_STORE_DIR)

    summary = {
        "status"          : "success",
        "documents_seeded": seed_result.get("written", 0) + seed_result.get("skipped", 0),
        "total_chunks"    : len(all_chunks),
        "embedding_model" : EMBEDDING_MODEL,
        "embedding_dim"   : embeddings.shape[1],
        "index_dir"       : str(VECTOR_STORE_DIR),
    }

    logger.info(f"Index build complete: {summary}")
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build FAISS vector index")
    parser.add_argument("--force", action="store_true", help="Force full rebuild")
    args = parser.parse_args()
    result = run_build_index(force=args.force)
    print(json.dumps(result, indent=2))
