"""
chunker.py
----------
Splits cleaned document text into overlapping chunks.

Design goals:
- Respect heading boundaries (## headings) — never split in the middle of a section.
- Use character-level sliding window with overlap for sections that exceed chunk_size.
- Every chunk retains full source metadata so retrieval can cite it.
- Financial values, percentages, and key facts are never split across chunks
  wherever possible (heading-aware splitting prevents this).

Chunk schema:
  chunk_id      str   unique ID: "{source_id}_chunk_{n}"
  source_id     str
  scheme        str
  title         str
  source_url    str
  organization  str
  source_type   str
  section       str   heading of the section this chunk belongs to
  last_updated  str
  text          str   chunk text content
"""

import hashlib
import json
import logging
import re
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

# ── Default chunking params (overridden by settings) ─────────────────────────
DEFAULT_CHUNK_SIZE    = 600   # characters
DEFAULT_CHUNK_OVERLAP = 100   # characters

# ── Heading splitter: matches lines beginning with ## ─────────────────────────
_HEADING_PATTERN = re.compile(r"^(#{1,4}\s+.+)$", re.MULTILINE)


def _split_by_headings(text: str) -> List[Dict[str, str]]:
    """
    Split text into sections by Markdown headings (## Heading).
    Returns list of dicts: {"heading": str, "body": str}
    """
    sections = []
    parts = _HEADING_PATTERN.split(text)

    # parts alternates between non-heading text and heading lines
    # e.g. ["preamble", "## Heading 1", "body1", "## Heading 2", "body2"]
    current_heading = "General"
    current_body = []

    i = 0
    while i < len(parts):
        part = parts[i].strip()
        if _HEADING_PATTERN.match(parts[i]):
            # Save previous section
            if current_body:
                body = "\n".join(current_body).strip()
                if body:
                    sections.append({"heading": current_heading, "body": body})
            current_heading = part.lstrip("#").strip()
            current_body = []
        else:
            if part:
                current_body.append(part)
        i += 1

    # Save last section
    if current_body:
        body = "\n".join(current_body).strip()
        if body:
            sections.append({"heading": current_heading, "body": body})

    return sections


def _sliding_window(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split a long text body into overlapping character-level chunks.
    Tries to break at sentence boundaries (". ") within ±50 chars of the target size.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Try to break at a sentence boundary near the end of this chunk
        search_start = max(start, end - 50)
        boundary = text.rfind(". ", search_start, end + 50)
        if boundary != -1:
            end = boundary + 1  # include the period

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap  # slide back by overlap
        if start >= len(text):
            break

    return chunks


def chunk_document(
    doc: dict,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[dict]:
    """
    Chunk a single processed document into metadata-preserving chunks.

    Args:
        doc:          Processed document dict (from data/processed/*.json)
        chunk_size:   Max characters per chunk
        chunk_overlap: Overlap between consecutive chunks

    Returns:
        List of chunk dicts, each with full metadata + text.
    """
    text       = doc.get("text", "").strip()
    source_id  = doc.get("source_id", "unknown")

    if not text:
        logger.warning(f"[{source_id}] Empty text — no chunks produced.")
        return []

    # Split into sections by heading
    sections = _split_by_headings(text)
    if not sections:
        sections = [{"heading": "General", "body": text}]

    # Base metadata shared across all chunks from this document
    base_meta = {
        "source_id"   : doc.get("source_id", ""),
        "scheme"      : doc.get("scheme", ""),
        "title"       : doc.get("title", ""),
        "source_url"  : doc.get("source_url", ""),
        "organization": doc.get("organization", ""),
        "source_type" : doc.get("source_type", ""),
        "last_updated": doc.get("last_updated", ""),
    }

    chunks = []
    chunk_index = 0

    for section in sections:
        heading = section["heading"]
        body    = section["body"]

        # Prepend the heading into each chunk so context is self-contained
        full_section_text = f"{heading}\n\n{body}"

        # Split into overlapping windows if too large
        sub_chunks = _sliding_window(full_section_text, chunk_size, chunk_overlap)

        for sub in sub_chunks:
            if not sub.strip():
                continue

            chunk_id = f"{source_id}_chunk_{chunk_index:04d}"

            chunk = {
                **base_meta,
                "chunk_id"  : chunk_id,
                "section"   : heading,
                "text"      : sub,
                "char_count": len(sub),
            }
            chunks.append(chunk)
            chunk_index += 1

    logger.debug(f"[{source_id}] → {len(chunks)} chunks from {len(sections)} sections")
    return chunks


def chunk_all_documents(
    processed_dir: Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[dict]:
    """
    Load all processed documents from processed_dir and chunk them.

    Returns:
        Flat list of all chunks across all documents.
    """
    processed_dir = Path(processed_dir)
    json_files    = sorted(processed_dir.glob("*.json"))

    if not json_files:
        logger.warning(f"No processed documents found in {processed_dir}")
        return []

    all_chunks = []
    for json_path in json_files:
        try:
            doc = json.loads(json_path.read_text(encoding="utf-8"))
            doc_chunks = chunk_document(doc, chunk_size, chunk_overlap)
            all_chunks.extend(doc_chunks)
            logger.info(f"[{doc.get('source_id')}] {len(doc_chunks)} chunks")
        except Exception as e:
            logger.error(f"Error chunking {json_path.name}: {e}")

    logger.info(
        f"Chunking complete: {len(all_chunks)} total chunks "
        f"from {len(json_files)} documents"
    )
    return all_chunks


def save_chunks(chunks: List[dict], output_path: Path) -> None:
    """Save all chunks to a single JSONL file (one chunk per line)."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    logger.info(f"Saved {len(chunks)} chunks → {output_path}")


def load_chunks(chunks_path: Path) -> List[dict]:
    """Load chunks from a JSONL file."""
    chunks_path = Path(chunks_path)
    if not chunks_path.exists():
        logger.warning(f"Chunks file not found: {chunks_path}")
        return []
    chunks = []
    with chunks_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    logger.info(f"Loaded {len(chunks)} chunks from {chunks_path}")
    return chunks


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.config.settings import PROCESSED_DIR, DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP
    from src.chunking.cleaner import clean_text
    import json

    logging.basicConfig(level=logging.INFO)

    # Load, clean, chunk, save
    json_files = sorted(PROCESSED_DIR.glob("*.json"))
    all_chunks = []
    for jf in json_files:
        doc = json.loads(jf.read_text(encoding="utf-8"))
        doc["text"] = clean_text(doc.get("text", ""), doc.get("source_id", ""))
        chunks = chunk_document(doc, CHUNK_SIZE, CHUNK_OVERLAP)
        all_chunks.extend(chunks)

    output = DATA_DIR / "processed" / "chunks.jsonl"
    save_chunks(all_chunks, output)
    print(f"Done. {len(all_chunks)} chunks saved to {output}")
