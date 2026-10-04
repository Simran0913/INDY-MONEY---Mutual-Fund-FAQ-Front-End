"""
fetcher.py
----------
Fetches raw content from official source URLs.
Handles HTML pages and PDF documents.
Logs failures — never silently replaces with third-party sources.
"""

import logging
import time
from pathlib import Path
from typing import Optional, Tuple

import requests

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; MutualFundFAQBot/1.0; "
        "+https://github.com/nextleap/mf-faq-bot)"
    ),
    "Accept": "text/html,application/pdf,application/xhtml+xml,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT = 30   # seconds
MAX_RETRIES     = 2
RETRY_DELAY     = 3    # seconds


def fetch_url(url: str) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Fetch a URL and return (raw_bytes, content_type).
    Returns (None, None) on failure.
    Content-type is lowercased, e.g. 'text/html', 'application/pdf'.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").lower().split(";")[0].strip()
            logger.info(f"Fetched [{response.status_code}] {url} ({content_type})")
            return response.content, content_type

        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error on attempt {attempt}/{MAX_RETRIES} for {url}: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error on attempt {attempt}/{MAX_RETRIES} for {url}: {e}")
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt}/{MAX_RETRIES} for {url}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error on attempt {attempt}/{MAX_RETRIES} for {url}: {e}")

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    logger.error(f"FAILED to fetch after {MAX_RETRIES} attempts: {url}")
    return None, None


def is_pdf(content_type: Optional[str], url: str) -> bool:
    """Detect PDF by content-type or URL extension."""
    if content_type and "pdf" in content_type:
        return True
    return url.lower().endswith(".pdf")
