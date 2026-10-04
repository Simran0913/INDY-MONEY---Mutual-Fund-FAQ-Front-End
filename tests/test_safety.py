"""
test_safety.py
--------------
Tests for query classification and PII detection.

Tests cover:
- FACTUAL_ALLOWED classification
- INVESTMENT_ADVICE_REFUSAL classification
- PII_DETECTED classification
- OUT_OF_SCOPE classification
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.safety.classifier import classify_query, QueryCategory
from src.safety.guard import safety_check


# ── Factual questions ──────────────────────────────────────────────────────────

class TestFactualClassification:

    @pytest.mark.parametrize("question", [
        "What is the expense ratio of SBI Bluechip Fund?",
        "What is the exit load?",
        "What is the minimum SIP?",
        "What is the minimum investment?",
        "What is the ELSS lock-in period?",
        "What is the riskometer of SBI Liquid Fund?",
        "What is the benchmark for SBI Small Cap Fund?",
        "How can I download my account statement?",
        "Where can I find the capital gains statement?",
        "What is the scheme objective of SBI Balanced Advantage Fund?",
        "What is the TER of SBI Magnum Tax Gain Scheme?",
        "What is the total expense ratio for direct plan?",
        "What is the minimum lump sum investment?",
    ])
    def test_factual_classified_correctly(self, question):
        result = classify_query(question)
        assert result.category == QueryCategory.FACTUAL_ALLOWED, (
            f"Expected FACTUAL_ALLOWED for: '{question}', got: {result.category}"
        )

    def test_factual_safety_check_is_safe(self):
        result = safety_check("What is the expense ratio of SBI Bluechip Fund?")
        assert result.is_safe is True
        assert result.response is None


# ── Investment advice questions ────────────────────────────────────────────────

class TestInvestmentAdviceRefusal:

    @pytest.mark.parametrize("question", [
        "Should I buy this fund?",
        "Should I sell this fund?",
        "Which fund is best?",
        "Which fund will give the highest return?",
        "Which scheme should I invest in?",
        "Is this fund good for me?",
        "Should I invest in SBI Bluechip Fund?",
        "Which is the best SBI scheme?",
        "Will this fund give better returns?",
        "Is SBI Liquid Fund safe for me to invest?",
    ])
    def test_advice_classified_correctly(self, question):
        result = classify_query(question)
        assert result.category == QueryCategory.INVESTMENT_ADVICE, (
            f"Expected INVESTMENT_ADVICE for: '{question}', got: {result.category}"
        )

    def test_advice_safety_check_not_safe(self):
        result = safety_check("Should I buy this fund?")
        assert result.is_safe is False
        assert result.response is not None
        assert "investment advice" in result.response.lower()

    def test_advice_response_does_not_recommend(self):
        result = safety_check("Which fund is best?")
        assert result.is_safe is False
        response = result.response.lower()
        # Must NOT say "buy", "sell", or recommend a fund
        for banned in ["buy this", "sell this", "best fund is", "you should invest"]:
            assert banned not in response, f"Response contains banned phrase: '{banned}'"


# ── PII detection ──────────────────────────────────────────────────────────────

class TestPIIDetection:

    @pytest.mark.parametrize("question", [
        "Can I give you my PAN?",
        "Save my Aadhaar number",
        "Store my OTP",
        "Save my account number",
        "My PAN is ABCDE1234F",
        "Here is my Aadhaar: 1234 5678 9012",
        "my pan card number is here",
        "can i share my bank account",
    ])
    def test_pii_classified_correctly(self, question):
        result = classify_query(question)
        assert result.category == QueryCategory.PII_DETECTED, (
            f"Expected PII_DETECTED for: '{question}', got: {result.category}"
        )

    def test_pii_safety_check_not_safe(self):
        result = safety_check("Save my Aadhaar")
        assert result.is_safe is False
        assert result.response is not None

    def test_pii_response_does_not_echo_pii(self):
        """PII values must never be echoed back in the response."""
        question = "My PAN is ABCDE1234F"
        result = classify_query(question)
        # The classifier result should not contain the actual PAN value
        assert "ABCDE1234F" not in (result.safe_response or "")
        assert "ABCDE1234F" not in (result.reason or "")

    def test_pii_response_contains_warning(self):
        result = safety_check("Can I give you my PAN?")
        assert result.response is not None
        response_lower = result.response.lower()
        assert any(word in response_lower for word in ["personal", "pan", "aadhaar", "share"]), (
            "PII response should mention PII types"
        )


# ── Out of scope ───────────────────────────────────────────────────────────────

class TestOutOfScope:

    @pytest.mark.parametrize("question", [
        "Which stock should I buy?",
        "Predict tomorrow's market",
        "Which crypto should I buy?",
        "Tell me about bitcoin",
        "Should I buy Nifty 50 stocks?",
    ])
    def test_out_of_scope_classified_correctly(self, question):
        result = classify_query(question)
        assert result.category == QueryCategory.OUT_OF_SCOPE, (
            f"Expected OUT_OF_SCOPE for: '{question}', got: {result.category}"
        )

    def test_out_of_scope_not_safe(self):
        result = safety_check("Which stock should I buy?")
        assert result.is_safe is False
        assert result.response is not None

    def test_out_of_scope_mentions_correct_scope(self):
        result = safety_check("Which crypto should I buy?")
        assert "SBI" in result.response or "mutual fund" in result.response.lower()


# ── Edge cases ─────────────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_empty_query(self):
        result = classify_query("")
        assert result.category == QueryCategory.OUT_OF_SCOPE

    def test_whitespace_only(self):
        result = classify_query("   ")
        assert result.category == QueryCategory.OUT_OF_SCOPE

    def test_very_long_question_truncated_safely(self):
        long_q = "What is the expense ratio? " * 20
        result = classify_query(long_q)
        assert result.category == QueryCategory.FACTUAL_ALLOWED

    def test_mixed_factual_and_advice_prefers_advice_refusal(self):
        # "Should I invest" + "expense ratio" — advice takes priority
        q = "Should I invest in SBI Bluechip Fund because it has a low expense ratio?"
        result = classify_query(q)
        assert result.category == QueryCategory.INVESTMENT_ADVICE
