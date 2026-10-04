"""
extractor.py
------------
Extracts useful text from raw HTML bytes or PDF bytes.

HTML: BeautifulSoup — removes nav/footer/cookie banners, preserves headings and tables.
PDF:  pdfplumber    — extracts text page by page, preserves tables as plain text.

IMPORTANT: Numbers, percentages, dates, scheme names, charges, and financial values
           are NEVER altered during extraction.
"""

import io
import logging
import re
from typing import Optional

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ── HTML tags that are purely navigational / decorative ──────────────────────
_HTML_NOISE_TAGS = [
    "nav", "header", "footer", "aside", "script", "style",
    "noscript", "iframe", "form", "button", "svg", "img",
]

# ── CSS class/id fragments that typically signal navigation clutter ──────────
_NOISE_CLASS_PATTERNS = re.compile(
    r"(nav|menu|header|footer|cookie|banner|popup|modal|sidebar|breadcrumb|"
    r"social|share|ad|advertisement|promo|overlay)",
    re.IGNORECASE,
)


def _is_noisy_element(tag) -> bool:
    """Return True if the element looks like navigation / decorative content."""
    classes = " ".join(tag.get("class", []))
    tag_id  = tag.get("id", "")
    return bool(_NOISE_CLASS_PATTERNS.search(classes) or _NOISE_CLASS_PATTERNS.search(tag_id))


def extract_html(raw_bytes: bytes, url: str = "") -> str:
    """
    Extract clean text from HTML bytes.
    Preserves headings, tables (as pipe-delimited text), and paragraph text.
    Removes navigation, menus, footers, cookie banners, and scripts.
    """
    try:
        soup = BeautifulSoup(raw_bytes, "html.parser")

        # Remove noise tags entirely
        for tag_name in _HTML_NOISE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # Remove elements that look noisy by class/id
        for tag in soup.find_all(True):
            if _is_noisy_element(tag):
                tag.decompose()

        lines = []

        for element in soup.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "table", "td", "th", "tr"]
        ):
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                text = element.get_text(separator=" ", strip=True)
                if text:
                    lines.append(f"\n## {text}\n")

            elif element.name == "table":
                rows = []
                for row in element.find_all("tr"):
                    cells = [
                        cell.get_text(separator=" ", strip=True)
                        for cell in row.find_all(["td", "th"])
                    ]
                    if cells:
                        rows.append(" | ".join(cells))
                if rows:
                    lines.append("\n" + "\n".join(rows) + "\n")

            elif element.name in ["td", "th", "tr"]:
                # already handled in table block
                continue

            elif element.name in ["p", "li"]:
                text = element.get_text(separator=" ", strip=True)
                if text and len(text) > 20:  # skip trivial one-word items
                    lines.append(text)

        result = "\n".join(lines)
        result = _normalise_whitespace(result)
        logger.info(f"HTML extraction: {len(result)} chars from {url}")
        return result

    except Exception as e:
        logger.error(f"HTML extraction failed for {url}: {e}")
        return ""


def extract_pdf(raw_bytes: bytes, url: str = "") -> str:
    """
    Extract text from PDF bytes using pdfplumber.
    Preserves tables as pipe-delimited rows.
    Financial values, percentages, and dates are preserved exactly.
    """
    try:
        import pdfplumber  # imported here so HTML-only mode doesn't require it

        lines = []
        with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                # Try table extraction first
                tables = page.extract_tables()
                extracted_table_bboxes = set()

                for table in tables:
                    rows = []
                    for row in table:
                        if row:
                            cells = [str(c).strip() if c else "" for c in row]
                            rows.append(" | ".join(cells))
                    if rows:
                        lines.append(f"\n[Table on page {page_num}]")
                        lines.extend(rows)
                        lines.append("")

                # Extract remaining text (outside tables)
                text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if text:
                    lines.append(text)

        result = "\n".join(lines)
        result = _normalise_whitespace(result)
        logger.info(f"PDF extraction: {len(result)} chars from {url}")
        return result

    except ImportError:
        logger.error("pdfplumber not installed. Install with: pip install pdfplumber")
        return ""
    except Exception as e:
        logger.error(f"PDF extraction failed for {url}: {e}")
        return ""


def _normalise_whitespace(text: str) -> str:
    """Collapse multiple blank lines; normalise line endings."""
    # Replace Windows line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3+ consecutive blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract(raw_bytes: bytes, content_type: Optional[str], url: str = "") -> str:
    """
    Top-level dispatcher.
    Routes to extract_html or extract_pdf based on content type.
    """
    if not raw_bytes:
        return ""

    if content_type and "pdf" in content_type:
        return extract_pdf(raw_bytes, url)
    elif url.lower().endswith(".pdf"):
        return extract_pdf(raw_bytes, url)
    else:
        return extract_html(raw_bytes, url)
