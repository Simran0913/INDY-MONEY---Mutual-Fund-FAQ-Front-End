"""
main.py
-------
FastAPI backend for the Facts-Only Mutual Fund FAQ Assistant.

Endpoints:
  POST /api/chat        → main RAG pipeline
  POST /api/build-index → trigger index build
  GET  /api/health      → health check
  GET  /api/schemes     → list of covered schemes
  GET  /api/sources     → list of official sources

CORS is configured for the Next.js frontend (localhost:3000 + env-configured origins).
"""

import logging
import os
import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
import pandas as pd

from src.config.settings import (
    OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    EMBEDDING_MODEL, TOP_K, MIN_SCORE, ALLOWED_ORIGINS, AMC_NAME, SCHEMES,
    SOURCES_CSV, VECTOR_STORE_DIR, LOGS_DIR
)

# ── Logging ────────────────────────────────────────────────────────────────────
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / "api.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "Facts-Only Mutual Fund FAQ Assistant",
    description = (
        "A RAG-based chatbot that answers verified factual questions about "
        "selected SBI Mutual Fund schemes. No investment advice. Facts only."
    ),
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ALLOWED_ORIGINS,
    allow_credentials = True,
    allow_methods     = ["GET", "POST"],
    allow_headers     = ["Content-Type", "Authorization"],
)


# ── Request / Response models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="User question")

    @field_validator("question")
    @classmethod
    def no_pii_in_request(cls, v: str) -> str:
        """Lightweight server-side check — full PII detection happens in classifier."""
        import re
        # Block obvious PAN patterns at request level before they hit logs
        pan_pattern = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
        if pan_pattern.search(v):
            raise ValueError("Request contains PII. Please do not share personal information.")
        return v.strip()


class ChatResponse(BaseModel):
    answer      : str
    source_url  : str | None
    last_updated: str | None
    disclaimer  : str
    category    : str
    is_safe     : bool
    is_valid    : bool
    chunks_used : int


class BuildIndexResponse(BaseModel):
    status         : str
    message        : str
    total_chunks   : int | None = None
    embedding_model: str | None = None


# ── Startup event ──────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Check that the FAISS index is built on startup."""
    index_file = VECTOR_STORE_DIR / "index.faiss"
    if not index_file.exists():
        logger.warning(
            "FAISS index not found. Run: python -m src.embeddings.build_index\n"
            "Or call POST /api/build-index"
        )
    else:
        meta_file = VECTOR_STORE_DIR / "metadata.json"
        import json
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            logger.info(f"FAISS index ready: {len(meta)} chunks indexed.")
        except Exception:
            logger.info("FAISS index file found.")

    if not OPENAI_API_KEY:
        logger.warning(
            "OPENAI_API_KEY not set. LLM generation will use chunk-based fallback. "
            "Set OPENAI_API_KEY in your .env file."
        )


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    index_ready = (VECTOR_STORE_DIR / "index.faiss").exists()
    return {
        "status"          : "ok",
        "amc"             : AMC_NAME,
        "schemes_covered" : len(SCHEMES),
        "index_ready"     : index_ready,
        "llm_configured"  : bool(OPENAI_API_KEY),
        "embedding_model" : EMBEDDING_MODEL,
    }


@app.get("/api/schemes", tags=["Info"])
async def list_schemes():
    """List all covered mutual fund schemes."""
    return {
        "amc"    : AMC_NAME,
        "schemes": SCHEMES,
        "count"  : len(SCHEMES),
    }


@app.get("/api/sources", tags=["Info"])
async def list_sources():
    """List all official sources used by the RAG system."""
    if not SOURCES_CSV.exists():
        raise HTTPException(status_code=404, detail="sources.csv not found")
    try:
        df = pd.read_csv(SOURCES_CSV)
        sources = df.to_dict(orient="records")
        return {
            "total"  : len(sources),
            "sources": sources,
        }
    except Exception as e:
        logger.error(f"Error reading sources.csv: {e}")
        raise HTTPException(status_code=500, detail="Error reading sources")


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main RAG pipeline endpoint.

    Accepts a user question, runs the full safety → retrieval → generation →
    citation validation pipeline, and returns a grounded factual answer with
    exactly one official source URL.

    Investment advice questions and PII are refused at the safety layer.
    """
    try:
        from src.generation.orchestrator import ask

        logger.info(f"Chat request received. Question length: {len(request.question)} chars.")

        result = ask(
            question        = request.question,
            api_key         = OPENAI_API_KEY,
            model           = LLM_MODEL,
            temperature     = LLM_TEMPERATURE,
            max_tokens      = LLM_MAX_TOKENS,
            top_k           = TOP_K,
            min_score       = MIN_SCORE,
            embedding_model = EMBEDDING_MODEL,
        )

        logger.info(
            f"Chat response: category={result.get('category')}, "
            f"is_safe={result.get('is_safe')}, chunks={result.get('chunks_used', 0)}"
        )

        return ChatResponse(
            answer      = result["answer"],
            source_url  = result.get("source_url"),
            last_updated= result.get("last_updated"),
            disclaimer  = result.get("disclaimer", ""),
            category    = result.get("category", "FACTUAL_ALLOWED"),
            is_safe     = result.get("is_safe", True),
            is_valid    = result.get("is_valid", True),
            chunks_used = result.get("chunks_used", 0),
        )

    except ValueError as e:
        # Pydantic validation errors (e.g. PII in question)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in /api/chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error. Please try again.")


@app.post("/api/build-index", response_model=BuildIndexResponse, tags=["System"])
async def build_index_endpoint():
    """
    Trigger the full index build pipeline.
    Seeds documents → chunks → embeds → builds FAISS index.
    This may take 1-2 minutes on first run (model download + embedding).
    """
    try:
        from src.embeddings.build_index import run_build_index
        result = run_build_index(force=True)
        # Invalidate cached index after rebuild
        from src.embeddings.vector_store import invalidate_cache
        invalidate_cache()

        return BuildIndexResponse(
            status         = result.get("status", "success"),
            message        = f"Index built: {result.get('total_chunks', 0)} chunks indexed.",
            total_chunks   = result.get("total_chunks"),
            embedding_model= result.get("embedding_model"),
        )
    except Exception as e:
        logger.error(f"Index build error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Index build failed: {str(e)}")


# ── Error handlers ─────────────────────────────────────────────────────────────

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Endpoint not found"})


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again."},
    )


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    from src.config.settings import API_HOST, API_PORT
    uvicorn.run("api.main:app", host=API_HOST, port=API_PORT, reload=True)
