"""
pipeline.py
-----------
Main ingestion pipeline.

Reads data/sources.csv → fetches each source → extracts text →
saves processed document as JSON to data/processed/.

Each saved document retains:
  source_id, title, scheme, source_url, organization, source_type,
  last_updated, date_accessed, text

Failed sources are recorded in logs/ingestion_failures.log.
Failed sources are NEVER silently replaced with third-party sources.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Allow running as script from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.config.settings import SOURCES_CSV, RAW_DIR, PROCESSED_DIR, LOGS_DIR
from src.ingestion.fetcher  import fetch_url, is_pdf
from src.ingestion.extractor import extract

# ── Logging setup ─────────────────────────────────────────────────────────────
LOGS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / "ingestion.log", encoding="utf-8"),
    ],
)
failure_logger = logging.getLogger("ingestion.failures")
failure_handler = logging.FileHandler(LOGS_DIR / "ingestion_failures.log", encoding="utf-8")
failure_logger.addHandler(failure_handler)

logger = logging.getLogger(__name__)


# ── Minimum acceptable text length ───────────────────────────────────────────
MIN_TEXT_LENGTH = 100  # characters


def ingest_source(row: dict) -> dict | None:
    """
    Process a single source row from sources.csv.
    Returns a document dict or None on failure.
    """
    source_id  = row["source_id"]
    url        = str(row["url"]).strip()
    title      = str(row["title"]).strip()
    scheme     = str(row["scheme"]).strip()
    org        = str(row["organization"]).strip()
    src_type   = str(row["source_type"]).strip()
    last_upd   = str(row.get("last_updated", "")).strip()
    accessed   = str(row.get("date_accessed", datetime.now().strftime("%Y-%m-%d"))).strip()

    logger.info(f"Ingesting [{source_id}] {title} — {url}")

    # ── Fetch ──────────────────────────────────────────────────────────────
    raw_bytes, content_type = fetch_url(url)

    if raw_bytes is None:
        failure_logger.error(
            f"FETCH_FAILED | {source_id} | {title} | {url}"
        )
        logger.error(f"[SKIP] {source_id}: fetch failed. See ingestion_failures.log.")
        return None

    # ── Save raw bytes ──────────────────────────────────────────────────────
    ext = ".pdf" if is_pdf(content_type, url) else ".html"
    raw_path = RAW_DIR / f"{source_id}{ext}"
    raw_path.write_bytes(raw_bytes)

    # ── Extract text ────────────────────────────────────────────────────────
    text = extract(raw_bytes, content_type, url)

    if not text or len(text) < MIN_TEXT_LENGTH:
        failure_logger.error(
            f"EXTRACT_FAILED | {source_id} | {title} | {url} | "
            f"text_len={len(text) if text else 0}"
        )
        logger.warning(f"[SKIP] {source_id}: extracted text too short ({len(text) if text else 0} chars).")
        return None

    # ── Build document ──────────────────────────────────────────────────────
    doc = {
        "source_id"   : source_id,
        "title"       : title,
        "scheme"      : scheme,
        "source_url"  : url,
        "organization": org,
        "source_type" : src_type,
        "last_updated": last_upd,
        "date_accessed": accessed,
        "text"        : text,
        "char_count"  : len(text),
    }

    # ── Save processed JSON ─────────────────────────────────────────────────
    out_path = PROCESSED_DIR / f"{source_id}.json"
    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"[OK] {source_id} saved → {out_path} ({len(text)} chars)")
    return doc


def run_ingestion(force: bool = False) -> dict:
    """
    Run full ingestion pipeline over all sources in sources.csv.

    Args:
        force: Re-ingest even if processed file already exists.

    Returns:
        Summary dict with counts.
    """
    if not SOURCES_CSV.exists():
        raise FileNotFoundError(f"sources.csv not found at {SOURCES_CSV}")

    df = pd.read_csv(SOURCES_CSV)
    logger.info(f"Starting ingestion of {len(df)} sources from {SOURCES_CSV}")

    success, skipped, failed = 0, 0, 0
    results = []

    for _, row in df.iterrows():
        source_id = row["source_id"]
        out_path  = PROCESSED_DIR / f"{source_id}.json"

        if not force and out_path.exists():
            logger.info(f"[CACHED] {source_id} already processed, skipping.")
            skipped += 1
            continue

        doc = ingest_source(row.to_dict())
        if doc:
            success += 1
            results.append(doc)
        else:
            failed += 1

    summary = {
        "total"  : len(df),
        "success": success,
        "skipped": skipped,
        "failed" : failed,
        "timestamp": datetime.now().isoformat(),
    }

    # Save summary
    summary_path = LOGS_DIR / "ingestion_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    logger.info(
        f"Ingestion complete — "
        f"success={success}, skipped={skipped}, failed={failed}"
    )
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run document ingestion pipeline")
    parser.add_argument("--force", action="store_true", help="Re-ingest all sources")
    args = parser.parse_args()
    summary = run_ingestion(force=args.force)
    print(json.dumps(summary, indent=2))
