"""
conftest.py
-----------
Shared pytest fixtures for all test modules.
"""

import sys
from pathlib import Path

# Ensure project root is on path for all tests
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (require index build)")
    config.addinivalue_line("markers", "requires_api_key: marks tests that need OPENAI_API_KEY")
