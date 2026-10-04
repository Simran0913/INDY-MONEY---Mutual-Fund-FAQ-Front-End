"""
classifier.py
-------------
Query classifier and PII detector.

Every user query passes through this module BEFORE reaching the retriever or LLM.

Categories:
  FACTUAL_ALLOWED         → proceed to RAG retrieval
  INVESTMENT_ADVICE       → return safe refusal
  PII_DETECTED            → return PII warning
  OUT_OF_SCOPE            → return out-of-scope response

PII types detected:
  PAN, Aadhaar, bank account number, OTP, phone number, email,
  folio number sharing, account number, demat account

IMPORTANT:
  - PII is never logged, stored, or echoed back.
  - Investment advice queries never reach the RAG retrieval layer.
  - Out-of-scope queries never reach the RAG retrieval layer.
"""

import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class QueryCategory(str, Enum):
    FACTUAL_ALLOWED    = "FACTUAL_ALLOWED"
    INVESTMENT_ADVICE  = "INVESTMENT_ADVICE"
    PII_DETECTED       = "PII_DETECTED"
    OUT_OF_SCOPE       = "OUT_OF_SCOPE"


@dataclass
class ClassificationResult:
    category    : QueryCategory
    confidence  : str        # "high" | "medium" | "low"
    reason      : str        # internal reason (not shown to user)
    safe_response: Optional[str] = None   # pre-built response for non-factual queries


# ── PII patterns ──────────────────────────────────────────────────────────────

_PII_PATTERNS = [
    # PAN: 5 letters + 4 digits + 1 letter  e.g. ABCDE1234F
    (re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"), "PAN number"),
    # Aadhaar: 12 digits (with optional spaces/dashes)
    (re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"), "Aadhaar number"),
    # Indian phone numbers: 10 digits starting with 6-9
    (re.compile(r"\b[6-9]\d{9}\b"), "phone number"),
    # Email addresses
    (re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b"), "email address"),
    # Bank account numbers: 9-18 digits
    (re.compile(r"\b\d{9,18}\b"), "bank/account number"),
    # OTP: explicitly mentioning OTP with digits
    (re.compile(r"\b(otp|one.?time.?password)\b.*\d{4,8}", re.IGNORECASE), "OTP"),
    (re.compile(r"\d{4,8}.*\b(otp|one.?time.?password)\b", re.IGNORECASE), "OTP"),
]

# Phrases indicating the user is about to share / wants to store PII
_PII_INTENT_PHRASES = [
    r"\b(my pan|my aadhaar|my aadhar|my account number|my bank account|my demat|"
    r"my folio|save my|store my|here is my|here's my|take my|use my pan|"
    r"can i give you my|can i share my|my otp is|my otp)\b",
]
_PII_INTENT_PATTERN = re.compile("|".join(_PII_INTENT_PHRASES), re.IGNORECASE)


def _detect_pii(text: str) -> Optional[str]:
    """
    Returns the type of PII found, or None.
    IMPORTANT: Does NOT return the actual PII value — only the type.
    """
    # Check intent phrases first (user offering to share PII)
    if _PII_INTENT_PATTERN.search(text):
        return "personal information"

    # Check actual PII patterns
    for pattern, pii_type in _PII_PATTERNS:
        if pattern.search(text):
            # Extra guard: bank account regex is broad, only flag if there's context
            if pii_type == "bank/account number":
                bank_context = re.compile(
                    r"\b(account|bank|folio|number|no\.?)\b", re.IGNORECASE
                )
                if bank_context.search(text):
                    return pii_type
                continue
            return pii_type

    return None


# ── Investment advice patterns ─────────────────────────────────────────────────

_ADVICE_PATTERNS = re.compile(
    r"\b("
    r"should i (buy|sell|invest|redeem|switch|hold|exit)|"
    r"(buy|sell|invest in|redeem|switch to|exit)\s+(this|that|the)\s+(fund|scheme|sbi)|"
    r"which (fund|scheme|sbi|plan)\s+(is best|should i|to buy|to invest|gives|will give)|"
    r"best (fund|scheme|sbi|plan|option)|"
    r"(better|best|good|safe|risky|ideal|right|worth|recommend)\s+(fund|scheme|investment|option)|"
    r"(will|would|can|could)\s+(this|the|sbi)\s+(fund|scheme)\s+(give|provide|generate|return|grow)|"
    r"is (this|the|sbi) (fund|scheme) (good|bad|safe|risky|suitable|worth it)|"
    r"(good|safe|suitable|risky)\s+for me to\s+(invest|buy)|"
    r"(suggest|recommend|advise|tell me)\s+(a|the|which|what)?\s*(fund|scheme|investment)|"
    r"portfolio (advice|suggestion|recommendation)|"
    r"(how much|where) should i invest|"
    r"guaranteed (return|profit|income)|"
    r"(predict|forecast|expect)\s+(return|profit|growth|market)|"
    r"(highest|best|maximum)\s+(return|profit|yield)"
    r")\b",
    re.IGNORECASE,
)


# ── Out-of-scope patterns ──────────────────────────────────────────────────────

_OUT_OF_SCOPE_PATTERNS = re.compile(
    r"\b("
    r"which\s+(stock|stocks|share|shares)\b|"
    r"(nifty|sensex).{0,20}\bstocks?\b|"
    r"(stock|share|equity)\s+(pick|tip|recommendation|to buy)|"
    r"which\s+(stock|share|crypto|cryptocurrency|bitcoin|nifty|sensex)\s+(to buy|is best)|"
    r"(buy|sell|invest in)\s+(stock|share|crypto|bitcoin|ethereum|nifty)|"
    r"(predict|forecast)\s+(market|nifty|sensex|stock|share)|"
    r"tomorrow.{0,20}(market|nifty|sensex)|"
    r"(personal finance|financial planning|tax planning|insurance|ppf|nps|fd|fixed deposit)\s+(advice|plan)|"
    r"(gold|real estate|property|land)\s+(investment|advice|buy)|"
    r"crypto(currency)?|bitcoin|ethereum|dogecoin|nft|"
    r"personal (loan|debt|credit card)|"
    r"(write|generate|create)\s+(code|poem|essay|story)"
    r")\b",
    re.IGNORECASE,
)


# ── Factual indicators ─────────────────────────────────────────────────────────

_FACTUAL_KEYWORDS = re.compile(
    r"\b("
    r"expense ratio|ter|total expense|"
    r"exit load|redemption charge|"
    r"minimum (sip|investment|amount|purchase)|minimum (lump.?sum)|"
    r"sip (amount|minimum|details)|"
    r"lock.?in|elss lock|3 year lock|"
    r"riskometer|risk level|risk category|"
    r"benchmark|index|"
    r"scheme (objective|goal|purpose|type)|"
    r"(download|get|access|find|where)\s+(my\s+)?(statement|account statement)|"
    r"capital gain(s)? (statement|document|report)|"
    r"what is (the)?\s+(sbi|this|the)\s+(fund|scheme)|"
    r"(scheme|fund) (type|category|details|information|info|overview)|"
    r"asset allocation|"
    r"fund manager|"
    r"plan (direct|regular|growth|idcw)|"
    r"nav|net asset value|"
    r"amc|sbimf|sbi mutual fund|"
    r"(how|where|when)\s+(can|do|to)\s+i\s+(invest|start|register|apply)"
    r")\b",
    re.IGNORECASE,
)


# ── Pre-built safe responses ───────────────────────────────────────────────────

_PII_RESPONSE = (
    "Please do not share personal information such as your PAN, Aadhaar number, "
    "bank account number, OTP, phone number, or email in this chat. "
    "This assistant only answers factual questions about mutual fund schemes. "
    "For account-related queries, please contact SBI MF directly at www.sbimf.com "
    "or call their investor helpline."
)

_ADVICE_RESPONSE = (
    "I can provide verified factual information about the scheme, but I can't provide "
    "investment advice or recommend whether you should buy, sell, or invest in any fund. "
    "For investment guidance, please consult a SEBI-registered investment advisor. "
    "You can find educational information about mutual funds at: "
    "https://www.amfiindia.com/investor-corner/knowledge-center"
)

_OUT_OF_SCOPE_RESPONSE = (
    "This assistant only answers factual questions about selected SBI Mutual Fund schemes "
    "(SBI Bluechip Fund, SBI Magnum Tax Gain Scheme, SBI Liquid Fund, SBI Small Cap Fund, "
    "and SBI Balanced Advantage Fund). "
    "I can answer questions about expense ratios, exit loads, minimum SIP amounts, "
    "ELSS lock-in periods, benchmarks, riskometers, and how to download statements. "
    "Your question appears to be outside this scope."
)


# ── Main classifier ────────────────────────────────────────────────────────────

def classify_query(query: str) -> ClassificationResult:
    """
    Classify a user query into one of four categories.

    Args:
        query: Raw user input text.

    Returns:
        ClassificationResult with category, confidence, reason, and safe_response.

    IMPORTANT: This function does NOT log or return PII values.
    """
    if not query or not query.strip():
        return ClassificationResult(
            category     = QueryCategory.OUT_OF_SCOPE,
            confidence   = "high",
            reason       = "Empty query",
            safe_response= "Please type a question about a mutual fund scheme.",
        )

    query_stripped = query.strip()

    # ── 1. PII check (highest priority) ───────────────────────────────────────
    pii_type = _detect_pii(query_stripped)
    if pii_type:
        logger.warning(f"PII detected in query (type={pii_type}). Query NOT logged.")
        return ClassificationResult(
            category     = QueryCategory.PII_DETECTED,
            confidence   = "high",
            reason       = f"PII detected: {pii_type}",
            safe_response= _PII_RESPONSE,
        )

    # ── 2. Out-of-scope check ──────────────────────────────────────────────────
    if _OUT_OF_SCOPE_PATTERNS.search(query_stripped):
        logger.info("Query classified as OUT_OF_SCOPE.")
        return ClassificationResult(
            category     = QueryCategory.OUT_OF_SCOPE,
            confidence   = "high",
            reason       = "Out-of-scope topic detected",
            safe_response= _OUT_OF_SCOPE_RESPONSE,
        )

    # ── 3. Investment advice check ─────────────────────────────────────────────
    if _ADVICE_PATTERNS.search(query_stripped):
        logger.info("Query classified as INVESTMENT_ADVICE.")
        return ClassificationResult(
            category     = QueryCategory.INVESTMENT_ADVICE,
            confidence   = "high",
            reason       = "Investment advice request detected",
            safe_response= _ADVICE_RESPONSE,
        )

    # ── 4. Factual check ───────────────────────────────────────────────────────
    if _FACTUAL_KEYWORDS.search(query_stripped):
        logger.info("Query classified as FACTUAL_ALLOWED.")
        return ClassificationResult(
            category   = QueryCategory.FACTUAL_ALLOWED,
            confidence = "high",
            reason     = "Factual keyword detected",
        )

    # ── 5. Default: treat as factual (low confidence) ─────────────────────────
    # If none of the above patterns match, assume factual with low confidence.
    # The retriever's min_score threshold will handle irrelevant queries gracefully.
    logger.info("Query defaulted to FACTUAL_ALLOWED (no pattern matched).")
    return ClassificationResult(
        category   = QueryCategory.FACTUAL_ALLOWED,
        confidence = "low",
        reason     = "No blocking pattern found; proceeding to retrieval",
    )
