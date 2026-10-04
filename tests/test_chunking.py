"""
test_chunking.py
----------------
Tests for text cleaning and chunking pipeline.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.chunking.cleaner import clean_text
from src.chunking.chunker import chunk_document, _split_by_headings


class TestCleaner:

    def test_removes_cookie_banner(self):
        text = "We use cookies to improve experience. accept\n## Expense Ratio\n1.64%"
        cleaned = clean_text(text, "TEST")
        assert "cookie" not in cleaned.lower()
        assert "1.64%" in cleaned

    def test_preserves_financial_values(self):
        text = "Exit load: 1%. Expense ratio: 0.83%. Lock-in: 3 years. Min SIP: Rs. 500."
        cleaned = clean_text(text, "TEST")
        assert "1%" in cleaned
        assert "0.83%" in cleaned
        assert "3 years" in cleaned
        assert "Rs. 500" in cleaned

    def test_preserves_scheme_names(self):
        text = "SBI Bluechip Fund has benchmark S&P BSE 100 TRI."
        cleaned = clean_text(text, "TEST")
        assert "SBI Bluechip Fund" in cleaned
        assert "S&P BSE 100 TRI" in cleaned

    def test_removes_page_numbers(self):
        text = "## Exit Load\nPage 1 of 5\n1% if redeemed within 1 year"
        cleaned = clean_text(text, "TEST")
        assert "Page 1 of 5" not in cleaned
        assert "1% if redeemed within 1 year" in cleaned

    def test_deduplicates_consecutive_lines(self):
        text = "Exit Load\nExit Load\n1% within 1 year"
        cleaned = clean_text(text, "TEST")
        assert cleaned.count("Exit Load") == 1

    def test_does_not_alter_numbers(self):
        numbers = ["0.83%", "1.64%", "0.70%", "1.73%", "Rs. 5,000", "Rs. 500", "3 years"]
        text = " | ".join(numbers)
        cleaned = clean_text(text, "TEST")
        for num in numbers:
            assert num in cleaned, f"Number altered or removed: {num}"


class TestChunker:

    def test_splits_by_headings(self):
        text = "## Expense Ratio\n0.83% direct\n## Exit Load\n1% within 1 year"
        sections = _split_by_headings(text)
        assert len(sections) == 2
        assert sections[0]["heading"] == "Expense Ratio"
        assert sections[1]["heading"] == "Exit Load"

    def test_chunk_has_required_metadata(self):
        doc = {
            "source_id"   : "SRC001",
            "title"       : "Test Doc",
            "scheme"      : "SBI Bluechip Fund",
            "source_url"  : "https://www.sbimf.com/test",
            "organization": "SBI Mutual Fund",
            "source_type" : "scheme_page",
            "last_updated": "2024-03-31",
            "text"        : "## Expense Ratio\nDirect: 0.83%\n\n## Exit Load\n1% within 1 year",
        }
        chunks = chunk_document(doc)
        assert len(chunks) > 0
        for chunk in chunks:
            for field in ["chunk_id", "source_id", "scheme", "title", "source_url",
                          "organization", "source_type", "section", "last_updated", "text"]:
                assert field in chunk, f"Missing field: {field}"

    def test_chunk_id_unique(self):
        doc = {
            "source_id"   : "SRC001",
            "title"       : "Test",
            "scheme"      : "SBI Bluechip Fund",
            "source_url"  : "https://www.sbimf.com",
            "organization": "SBI Mutual Fund",
            "source_type" : "scheme_page",
            "last_updated": "2024-03-31",
            "text"        : "## A\nSome text here.\n\n## B\nMore text here.\n\n## C\nEven more.",
        }
        chunks = chunk_document(doc)
        ids = [c["chunk_id"] for c in chunks]
        assert len(ids) == len(set(ids)), "Duplicate chunk IDs found"

    def test_chunk_preserves_source_url(self):
        doc = {
            "source_id"   : "SRC001",
            "title"       : "Test",
            "scheme"      : "SBI Bluechip Fund",
            "source_url"  : "https://www.sbimf.com/bluechip",
            "organization": "SBI Mutual Fund",
            "source_type" : "scheme_page",
            "last_updated": "2024-03-31",
            "text"        : "## Expense Ratio\nDirect plan: 0.83% per annum",
        }
        chunks = chunk_document(doc)
        for chunk in chunks:
            assert chunk["source_url"] == "https://www.sbimf.com/bluechip"

    def test_empty_document_produces_no_chunks(self):
        doc = {
            "source_id": "SRC999",
            "text": "",
        }
        chunks = chunk_document(doc)
        assert chunks == []

    def test_chunk_size_respected(self):
        long_text = "## Section\n" + ("This is a sentence about mutual funds. " * 50)
        doc = {
            "source_id"   : "SRC001",
            "title"       : "T",
            "scheme"      : "SBI",
            "source_url"  : "https://sbimf.com",
            "organization": "SBI",
            "source_type" : "test",
            "last_updated": "2024-01-01",
            "text"        : long_text,
        }
        chunks = chunk_document(doc, chunk_size=300, chunk_overlap=50)
        for chunk in chunks:
            # Allow some slack for overlap
            assert len(chunk["text"]) <= 400, f"Chunk too large: {len(chunk['text'])} chars"
