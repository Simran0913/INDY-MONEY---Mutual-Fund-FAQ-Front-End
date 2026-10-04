"""
test_citations.py
-----------------
Tests for citation validation layer.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.citations.validator import (
    validate_and_format,
    format_final_response,
    _is_approved_url,
    _extract_domain,
    DISCLAIMER,
)


class TestApprovedDomains:

    @pytest.mark.parametrize("url,expected", [
        ("https://www.sbimf.com/en-us/equity-funds/sbi-bluechip-fund", True),
        ("https://www.amfiindia.com/investor-corner/knowledge-center/elss.html", True),
        ("https://www.sebi.gov.in/legal/circulars/sep-2018/ter_40276.html", True),
        ("https://groww.in/mutual-funds/sbi-bluechip-fund", False),
        ("https://moneycontrol.com/mutual-funds", False),
        ("https://etmoney.com/mutual-funds", False),
        ("https://zerodha.com/mutualfund/sbi-bluechip", False),
        ("https://reddit.com/r/mutualfunds", False),
        ("https://random-blog.com/sbi-mf-review", False),
    ])
    def test_domain_approval(self, url, expected):
        assert _is_approved_url(url) == expected, (
            f"URL {'should' if expected else 'should NOT'} be approved: {url}"
        )

    def test_extract_domain(self):
        assert _extract_domain("https://www.sbimf.com/page") == "www.sbimf.com"
        assert _extract_domain("https://sebi.gov.in/circular") == "sebi.gov.in"
        assert _extract_domain("not-a-url") == ""


class TestValidateAndFormat:

    def _make_chunk(self, url="https://www.sbimf.com/test", last_updated="2024-03-31"):
        return {
            "chunk_id"   : "SRC001_chunk_0000",
            "source_id"  : "SRC001",
            "scheme"     : "SBI Bluechip Fund",
            "title"      : "SBI Bluechip Fund - Scheme Page",
            "source_url" : url,
            "organization": "SBI Mutual Fund",
            "source_type": "scheme_page",
            "last_updated": last_updated,
            "text"       : "The exit load is 1% within 1 year.",
            "score"      : 0.85,
        }

    def test_valid_answer_passes(self):
        result = validate_and_format(
            answer      = "The exit load is 1% if redeemed within 1 year.",
            source_url  = "https://www.sbimf.com/en-us/equity-funds/sbi-bluechip-fund",
            last_updated= "2024-03-31",
            chunks      = [self._make_chunk()],
        )
        assert result.is_valid is True
        assert result.issues == []

    def test_missing_source_url_repaired_from_chunk(self):
        result = validate_and_format(
            answer      = "The exit load is 1% if redeemed within 1 year.",
            source_url  = None,
            last_updated= "2024-03-31",
            chunks      = [self._make_chunk()],
        )
        assert result.source_url == "https://www.sbimf.com/test"
        assert "missing_source_url" in result.issues

    def test_unapproved_url_repaired_from_chunk(self):
        result = validate_and_format(
            answer      = "The exit load is 1%.",
            source_url  = "https://groww.in/sbi-bluechip",
            last_updated= "2024-03-31",
            chunks      = [self._make_chunk()],
        )
        assert _is_approved_url(result.source_url or "")
        assert "unapproved_domain" in " ".join(result.issues)

    def test_missing_last_updated_repaired_from_chunk(self):
        result = validate_and_format(
            answer      = "The exit load is 1%.",
            source_url  = "https://www.sbimf.com/test",
            last_updated= None,
            chunks      = [self._make_chunk(last_updated="2024-03-31")],
        )
        assert result.last_updated == "2024-03-31"
        assert "missing_last_updated" in result.issues

    def test_empty_answer_uses_fallback(self):
        result = validate_and_format(
            answer      = "",
            source_url  = "https://www.sbimf.com/test",
            last_updated= "2024-03-31",
            chunks      = [self._make_chunk()],
        )
        assert "couldn't verify" in result.answer.lower() or len(result.answer) > 0

    def test_disclaimer_always_present(self):
        result = validate_and_format(
            answer      = "The expense ratio is 0.83%.",
            source_url  = "https://www.sbimf.com/test",
            last_updated= "2024-03-31",
            chunks      = [self._make_chunk()],
        )
        assert result.disclaimer == DISCLAIMER

    def test_format_final_response_structure(self):
        result = validate_and_format(
            answer      = "The expense ratio is 0.83% for direct plan.",
            source_url  = "https://www.sbimf.com/test",
            last_updated= "2024-03-31",
            chunks      = [self._make_chunk()],
        )
        response = format_final_response(result)
        assert "answer"       in response
        assert "source_url"   in response
        assert "last_updated" in response
        assert "disclaimer"   in response
        assert "is_valid"     in response
        assert "issues"       in response

    def test_third_party_url_not_in_final_response(self):
        """Final response must never contain a third-party URL."""
        result = validate_and_format(
            answer      = "Info from groww.",
            source_url  = "https://groww.in/sbi",
            last_updated= "2024-03-31",
            chunks      = [self._make_chunk()],
        )
        response = format_final_response(result)
        assert "groww.in" not in (response["source_url"] or "")
