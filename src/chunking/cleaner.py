"""
cleaner.py
----------
Cleans extracted text from processed documents.

RULES:
- Remove navigation residue, repeated headers, cookie banners, footer boilerplate.
- DO NOT alter any factual information:
  * Numbers, percentages, dates, scheme names, charges, amounts, lock-in periods,
    riskometer values, benchmark names — all preserved exactly.
- DO NOT summarise during cleaning.
- DO NOT change financial values.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── Patterns for boilerplate noise ────────────────────────────────────────────
_BOILERPLATE_PATTERNS = [
    # Cookie consent banners
    re.compile(r"we use cookies.*?accept", re.IGNORECASE | re.DOTALL),
    re.compile(r"this (website|site) uses cookies.*?\.", re.IGNORECASE),
    # Generic nav phrases
    re.compile(r"^(home|about us|contact us|login|sign in|register|menu|skip to content)\s*$",
               re.IGNORECASE | re.MULTILINE),
    # Social share / follow us
    re.compile(r"(follow us on|share on|like us on|subscribe to)\s+(facebook|twitter|linkedin|instagram|youtube)",
               re.IGNORECASE),
    # Copyright footers
    re.compile(r"©\s*\d{4}.*?(all rights reserved|sbimf|sbi funds)", re.IGNORECASE),
    re.compile(r"copyright\s*©?\s*\d{4}", re.IGNORECASE),
    # Page numbers artefacts from PDF
    re.compile(r"^\s*page\s+\d+\s+(of\s+\d+)?\s*$", re.IGNORECASE | re.MULTILINE),
    # Repeated dashes/underscores (PDF rulers)
    re.compile(r"[-_=]{10,}"),
    # Blank table rows like "| | | |"
    re.compile(r"(\|\s*)+\n"),
    # "Mutual fund investments are subject to market risks..." disclaimer (keep short form)
    # We keep the disclaimer once but remove duplicates handled by dedup below
]

# ── Disclaimer template (keep exactly once per document) ─────────────────────
_DISCLAIMER = "Mutual Fund investments are subject to market risks. Read all scheme related documents carefully before investing."
_DISCLAIMER_PATTERN = re.compile(
    r"mutual fund investments? (are )?subject to market risks?.*?before investing\.?",
    re.IGNORECASE | re.DOTALL,
)


def _remove_boilerplate(text: str) -> str:
    """Remove known boilerplate phrases and patterns."""
    for pattern in _BOILERPLATE_PATTERNS:
        text = pattern.sub("", text)
    return text


def _deduplicate_lines(text: str) -> str:
    """
    Remove consecutively duplicated lines (e.g. repeated headers in PDFs).
    Preserves order; only removes exact back-to-back duplicates.
    """
    lines = text.split("\n")
    cleaned = []
    prev = None
    for line in lines:
        stripped = line.strip()
        if stripped != prev:
            cleaned.append(line)
        prev = stripped
    return "\n".join(cleaned)


def _normalise_whitespace(text: str) -> str:
    """Collapse excessive blank lines; trim trailing spaces per line."""
    lines = [l.rstrip() for l in text.split("\n")]
    # Collapse 3+ consecutive blank lines → 2
    result = []
    blank_count = 0
    for line in lines:
        if line == "":
            blank_count += 1
            if blank_count <= 2:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)
    return "\n".join(result).strip()


def _collapse_disclaimer(text: str) -> str:
    """
    Keep the first occurrence of the standard disclaimer; remove subsequent duplicates.
    The factual content of the disclaimer is preserved on first occurrence.
    """
    matches = list(_DISCLAIMER_PATTERN.finditer(text))
    if len(matches) <= 1:
        return text
    # Replace all matches after the first with empty string
    # Work backwards to preserve indices
    for match in reversed(matches[1:]):
        text = text[:match.start()] + text[match.end():]
    return text


def clean_text(text: str, source_id: str = "") -> str:
    """
    Full cleaning pipeline for a single document's text.

    Steps:
    1. Normalise line endings.
    2. Remove boilerplate patterns.
    3. Collapse duplicate disclaimer.
    4. Deduplicate consecutive identical lines.
    5. Normalise whitespace.

    IMPORTANT: Financial values, percentages, numbers, dates, scheme names,
               benchmark names, and riskometer values are NEVER modified.
    """
    if not text:
        return ""

    original_len = len(text)

    # 1. Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Remove boilerplate
    text = _remove_boilerplate(text)

    # 3. Collapse duplicate disclaimers
    text = _collapse_disclaimer(text)

    # 4. Deduplicate consecutive identical lines
    text = _deduplicate_lines(text)

    # 5. Normalise whitespace
    text = _normalise_whitespace(text)

    cleaned_len = len(text)
    logger.debug(
        f"[{source_id}] Cleaned: {original_len} → {cleaned_len} chars "
        f"({original_len - cleaned_len} removed)"
    )
    return text
