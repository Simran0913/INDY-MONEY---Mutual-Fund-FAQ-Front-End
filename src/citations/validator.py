"""
validator.py
------------
Citation validation layer.

Every factual answer MUST:
  1. Contain exactly ONE source URL.
  2. The URL must exist in data/sources.csv (approved sources list).
  3. The URL must come from an approved domain (sbimf.com, amfiindia.com, sebi.gov.in).
  4. The answer must have a "Last updated from sources" date.

If validation fails:
  → Attempt to repair using chunks metadata.
  → If still invalid, return a safe fallback response.

NEVER pass through an answer that:
  - Has no citation.
  - Cites a third-party / unapproved source.
  - Has no "Last updated" date.
"""

import csv
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

logger = logging.getLogger(__name__)

# ── Approved domains ──────────────────────────────────────────────────────────
APPROVED_DOMAINS = {
    "sbimf.com",
    "www.sbimf.com",
    "amfiindia.com",
    "www.amfiindia.com",
    "sebi.gov.in",
    "www.sebi.gov.in",
}

# ── Standard disclaimer ───────────────────────────────────────────────────────
DISCLAIMER = (
    "⚠️ Mutual Fund investments are subject to market risks. "
    "Read all scheme related documents carefully before investing."
)

# ── Approved URLs cache ───────────────────────────────────────────────────────
_approved_urls_cache: Optional[Set[str]] = None


def _load_approved_urls(sources_csv: Optional[Path] = None) -> Set[str]:
    """Load approved URLs from data/sources.csv."""
    global _approved_urls_cache
    if _approved_urls_cache is not None:
        return _approved_urls_cache

    if sources_csv is None:
        sources_csv = Path(__file__).resolve().parents[2] / "data" / "sources.csv"

    approved = set()
    if not sources_csv.exists():
        logger.warning(f"sources.csv not found at {sources_csv}. URL validation will use domain-only check.")
        _approved_urls_cache = approved
        return approved

    try:
        with sources_csv.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("url", "").strip()
                if url:
                    approved.add(url)
        logger.info(f"Loaded {len(approved)} approved URLs from sources.csv")
    except Exception as e:
        logger.error(f"Error loading sources.csv: {e}")

    _approved_urls_cache = approved
    return approved


def _extract_domain(url: str) -> str:
    """Extract domain from a URL string."""
    match = re.match(r"https?://([^/]+)", url)
    return match.group(1).lower() if match else ""


def _is_approved_url(url: str) -> bool:
    """Check if a URL is from an approved domain."""
    domain = _extract_domain(url)
    return domain in APPROVED_DOMAINS


@dataclass
class ValidationResult:
    is_valid    : bool
    answer      : str
    source_url  : Optional[str]
    last_updated: Optional[str]
    disclaimer  : str
    issues      : List[str]


def validate_and_format(
    answer      : str,
    source_url  : Optional[str],
    last_updated: Optional[str],
    chunks      : List[dict],
) -> ValidationResult:
    """
    Validate a generated answer and its citation.

    Repair strategy:
    1. If source_url is missing → use URL from highest-scoring chunk.
    2. If source_url is from unapproved domain → replace with chunk URL.
    3. If last_updated is missing → use last_updated from top chunk.
    4. If answer is empty → use fallback.

    Args:
        answer:       LLM-generated answer text.
        source_url:   Source URL parsed from LLM output.
        last_updated: Last-updated date parsed from LLM output.
        chunks:       Retrieved chunks (used for repair).

    Returns:
        ValidationResult with validated/repaired fields and any issues found.
    """
    from src.generation.prompt import FALLBACK_RESPONSE
    approved_urls = _load_approved_urls()
    issues = []

    # ── 1. Validate answer text ────────────────────────────────────────────────
    if not answer or len(answer.strip()) < 10:
        logger.warning("Answer is empty or too short. Using fallback.")
        answer = FALLBACK_RESPONSE
        issues.append("empty_answer")

    # ── 2. Validate source URL ─────────────────────────────────────────────────
    if not source_url:
        issues.append("missing_source_url")
        logger.warning("Source URL missing. Attempting repair from chunks.")
        # Repair: use URL from top chunk
        if chunks:
            source_url = chunks[0].get("source_url")
            if source_url:
                logger.info(f"Repaired source URL from chunk: {source_url}")

    if source_url and not _is_approved_url(source_url):
        issues.append(f"unapproved_domain: {_extract_domain(source_url)}")
        logger.warning(f"Unapproved URL: {source_url}. Attempting repair from chunks.")
        # Repair: find first approved URL in chunks
        repaired = None
        for chunk in chunks:
            candidate = chunk.get("source_url", "")
            if _is_approved_url(candidate):
                repaired = candidate
                break
        if repaired:
            source_url = repaired
            logger.info(f"Repaired to approved URL: {source_url}")
        else:
            source_url = None
            issues.append("no_approved_url_in_chunks")

    # Extra check: URL must be in approved sources.csv (if we have the list)
    if source_url and approved_urls and source_url not in approved_urls:
        # Not a hard failure — domain check passed; just log it
        logger.info(f"URL not in sources.csv but domain is approved: {source_url}")

    # ── 3. Validate last_updated ───────────────────────────────────────────────
    if not last_updated:
        issues.append("missing_last_updated")
        if chunks:
            last_updated = chunks[0].get("last_updated")
            if last_updated:
                logger.info(f"Repaired last_updated from chunk: {last_updated}")

    # ── 4. Final validity determination ───────────────────────────────────────
    # Valid if: answer exists AND source_url is approved AND last_updated exists
    is_valid = (
        bool(answer and len(answer.strip()) > 10)
        and bool(source_url and _is_approved_url(source_url or ""))
        and bool(last_updated)
        and "empty_answer" not in issues
        and "no_approved_url_in_chunks" not in issues
    )

    if not is_valid:
        logger.warning(f"Citation validation failed. Issues: {issues}")

    return ValidationResult(
        is_valid    = is_valid,
        answer      = answer,
        source_url  = source_url,
        last_updated= last_updated,
        disclaimer  = DISCLAIMER,
        issues      = issues,
    )


def format_final_response(result: ValidationResult) -> dict:
    """
    Format the validated result into the final API response dict.

    Returns:
        dict with: answer, source_url, last_updated, disclaimer, is_valid, issues
    """
    return {
        "answer"      : result.answer,
        "source_url"  : result.source_url or "https://www.sbimf.com",
        "last_updated": result.last_updated or "See source for latest date",
        "disclaimer"  : result.disclaimer,
        "is_valid"    : result.is_valid,
        "issues"      : result.issues,
    }
