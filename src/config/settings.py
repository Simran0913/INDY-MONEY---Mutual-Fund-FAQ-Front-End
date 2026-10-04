"""
Central configuration loaded from environment variables.
Never hardcode API keys here.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT_DIR        = Path(__file__).resolve().parents[2]
DATA_DIR        = ROOT_DIR / "data"
RAW_DIR         = DATA_DIR / "raw"
PROCESSED_DIR   = DATA_DIR / "processed"
VECTOR_STORE_DIR= DATA_DIR / "vector_store"
LOGS_DIR        = ROOT_DIR / "logs"
SOURCES_CSV     = DATA_DIR / "sources.csv"

# ── LLM ────────────────────────────────────────────────────────────────────
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL       = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
LLM_MAX_TOKENS  = int(os.getenv("LLM_MAX_TOKENS", "512"))

# ── Embeddings ─────────────────────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ── Chunking ───────────────────────────────────────────────────────────────
CHUNK_SIZE      = int(os.getenv("CHUNK_SIZE", "600"))
CHUNK_OVERLAP   = int(os.getenv("CHUNK_OVERLAP", "100"))

# ── Retrieval ──────────────────────────────────────────────────────────────
TOP_K           = int(os.getenv("TOP_K", "5"))
MIN_SCORE       = float(os.getenv("MIN_SCORE", "0.25"))

# ── CORS / API ──────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
API_HOST        = os.getenv("API_HOST", "0.0.0.0")
API_PORT        = int(os.getenv("API_PORT", "8000"))

# ── Project metadata ────────────────────────────────────────────────────────
AMC_NAME        = "SBI Mutual Fund"
SCHEMES         = [
    "SBI Bluechip Fund",
    "SBI Magnum Tax Gain Scheme",
    "SBI Liquid Fund",
    "SBI Small Cap Fund",
    "SBI Balanced Advantage Fund",
]
