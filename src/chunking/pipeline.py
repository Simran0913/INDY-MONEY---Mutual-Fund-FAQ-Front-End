"""
chunking/pipeline.py
--------------------
Orchestrates: Load processed docs → Clean → Chunk → Save chunks.jsonl

Run directly:
    python -m src.chunking.pipeline
    python -m src.chunking.pipeline --force
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config.settings   import PROCESSED_DIR, DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, LOGS_DIR
from src.chunking.cleaner  import clean_text
from src.chunking.chunker  import chunk_document, save_chunks

CHUNKS_OUTPUT = PROCESSED_DIR / "chunks.jsonl"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / "chunking.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def run_chunking_pipeline(force: bool = False) -> dict:
    """
    Full clean-and-chunk pipeline.

    Returns:
        Summary dict: total docs, total chunks, skipped, failed.
    """
    if not force and CHUNKS_OUTPUT.exists():
        logger.info(f"chunks.jsonl already exists. Use --force to regenerate.")
        # Count existing chunks
        with CHUNKS_OUTPUT.open() as f:
            n = sum(1 for line in f if line.strip())
        return {"status": "cached", "total_chunks": n, "chunks_file": str(CHUNKS_OUTPUT)}

    json_files = sorted(PROCESSED_DIR.glob("SRC*.json"))
    if not json_files:
        logger.error(f"No processed SRC*.json files found in {PROCESSED_DIR}. Run ingestion first.")
        return {"status": "error", "message": "No processed documents found"}

    all_chunks = []
    doc_count  = 0
    failed     = 0

    for jf in json_files:
        try:
            doc = json.loads(jf.read_text(encoding="utf-8"))
            source_id = doc.get("source_id", jf.stem)

            # Clean
            original_text = doc.get("text", "")
            cleaned_text  = clean_text(original_text, source_id)
            doc["text"]   = cleaned_text

            # Chunk
            chunks = chunk_document(doc, CHUNK_SIZE, CHUNK_OVERLAP)
            all_chunks.extend(chunks)
            doc_count += 1
            logger.info(f"[{source_id}] cleaned+chunked → {len(chunks)} chunks")

        except Exception as e:
            logger.error(f"Error processing {jf.name}: {e}")
            failed += 1

    # Save
    save_chunks(all_chunks, CHUNKS_OUTPUT)

    summary = {
        "status"      : "success",
        "documents"   : doc_count,
        "failed"      : failed,
        "total_chunks": len(all_chunks),
        "chunks_file" : str(CHUNKS_OUTPUT),
        "chunk_size"  : CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
    }
    logger.info(f"Chunking pipeline done: {summary}")
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run cleaning and chunking pipeline")
    parser.add_argument("--force", action="store_true", help="Regenerate even if chunks.jsonl exists")
    args = parser.parse_args()
    result = run_chunking_pipeline(force=args.force)
    print(json.dumps(result, indent=2))
