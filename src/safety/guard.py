"""
guard.py
--------
Safety guard — the single entry point for all safety checks.

Wraps classifier.py and provides a clean interface used by the API layer.

Usage:
    from src.safety.guard import safety_check, SafetyResult

    result = safety_check(user_query)
    if not result.is_safe:
        return result.response   # pre-built safe response
    # else: proceed to retrieval
"""

import logging
from dataclasses import dataclass
from typing import Optional

from src.safety.classifier import classify_query, QueryCategory

logger = logging.getLogger(__name__)


@dataclass
class SafetyResult:
    is_safe  : bool                   # True = proceed to RAG, False = return safe_response
    category : str                    # QueryCategory value
    response : Optional[str] = None   # Pre-built response for unsafe queries
    reason   : Optional[str] = None   # Internal reason (not exposed to user)


def safety_check(query: str) -> SafetyResult:
    """
    Run all safety checks on a user query.

    Returns SafetyResult:
      - is_safe=True  → query can proceed to RAG pipeline
      - is_safe=False → return result.response directly to user

    IMPORTANT:
      - PII values are never stored, logged, or returned.
      - Investment advice queries are blocked before retrieval.
      - Out-of-scope queries are blocked before retrieval.
    """
    classification = classify_query(query)

    if classification.category == QueryCategory.FACTUAL_ALLOWED:
        return SafetyResult(
            is_safe  = True,
            category = classification.category.value,
            reason   = classification.reason,
        )
    else:
        return SafetyResult(
            is_safe  = False,
            category = classification.category.value,
            response = classification.safe_response,
            reason   = classification.reason,
        )
