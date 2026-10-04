# Architecture Document
## Facts-Only Mutual Fund FAQ Assistant

---

## Overview

This system is a Retrieval-Augmented Generation (RAG) chatbot that answers **verified factual questions** about selected SBI Mutual Fund schemes using **only official public sources** from SBI MF, AMFI, and SEBI.

---

## Architecture Diagram

```
Official Sources (sbimf.com, amfiindia.com, sebi.gov.in)
                    │
                    ▼
         ┌──────────────────┐
         │  Document Seeds  │  ← 25 pre-extracted official documents
         │  (seed_data.py)  │    + live HTTP fetching fallback
         └──────────────────┘
                    │
                    ▼
         ┌──────────────────┐
         │   Text Cleaning  │  ← Removes nav/footer/cookies
         │   (cleaner.py)   │    Preserves all financial values
         └──────────────────┘
                    │
                    ▼
         ┌──────────────────┐
         │    Chunking      │  ← Heading-aware splitting (600 chars)
         │   (chunker.py)   │    Every chunk retains full metadata
         └──────────────────┘
                    │
                    ▼
         ┌──────────────────┐
         │   Embeddings     │  ← all-MiniLM-L6-v2 (local, 384-dim)
         │  (embedder.py)   │    L2-normalised vectors
         └──────────────────┘
                    │
                    ▼
         ┌──────────────────┐
         │   FAISS Index    │  ← IndexFlatIP (exact cosine search)
         │ (vector_store.py)│    Stored in data/vector_store/
         └──────────────────┘
                    
═══════════════════════════════════════════════════════════
                   QUERY PIPELINE
═══════════════════════════════════════════════════════════

User Question
      │
      ▼
┌─────────────────┐
│  Safety Layer   │  ← PII Detection (regex patterns)
│ (classifier.py) │    Query Classification:
│                 │    • FACTUAL_ALLOWED → proceed
│                 │    • INVESTMENT_ADVICE → safe refusal
│                 │    • PII_DETECTED → PII warning
│                 │    • OUT_OF_SCOPE → scope explanation
└─────────────────┘
      │ (FACTUAL only)
      ▼
┌─────────────────┐
│ Scheme Detector │  ← Keyword-based scheme detection
│ (retriever.py)  │    "bluechip" → SBI Bluechip Fund
└─────────────────┘
      │
      ▼
┌─────────────────┐
│   FAISS Search  │  ← Query embedded → cosine similarity
│ (vector_store)  │    min_score=0.25 threshold
│                 │    Deduplication by source_id
└─────────────────┘
      │
      ▼
┌─────────────────┐
│  LLM Generation │  ← OpenAI GPT-4o-mini
│ (generator.py)  │    System prompt: facts-only, no advice
│                 │    Context: retrieved chunks only
│                 │    Temperature: 0.0 (deterministic)
└─────────────────┘
      │
      ▼
┌─────────────────┐
│ Citation Check  │  ← Validates source URL:
│ (validator.py)  │    • Must be from approved domain
│                 │    • Auto-repairs from chunk metadata
│                 │    • Appends standard disclaimer
└─────────────────┘
      │
      ▼
   Response
   • Answer (max 3 sentences)
   • Source URL (1 official link)
   • Last updated from sources: [date]
   • Disclaimer
```

---

## Component Details

### 1. Document Seeds (`src/ingestion/seed_data.py`)
- 25 pre-extracted documents from official sources
- Covers all 5 schemes across all required topics
- Fallback when live HTTP fetch fails (CDN-gated PDFs)
- Each document preserves: scheme name, source URL, organization, last_updated

### 2. Text Cleaning (`src/chunking/cleaner.py`)
- Removes: navigation, menus, cookie banners, footers, repeated headers, page numbers
- Preserves **unchanged**: all numbers, percentages, dates, scheme names, charges, benchmarks, riskometer values
- Never summarises during cleaning

### 3. Chunking (`src/chunking/chunker.py`)
- Primary split: by `##` Markdown headings (section-aware)
- Secondary split: character-level sliding window (600 chars, 100 overlap)
- Each chunk retains all metadata: chunk_id, source_id, scheme, title, source_url, organization, source_type, section, last_updated

### 4. Embeddings (`src/embeddings/embedder.py`)
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Runs fully locally — no API key required
- 384-dimensional L2-normalised vectors
- ~80MB download on first use

### 5. Vector Store (`src/embeddings/vector_store.py`)
- FAISS `IndexFlatIP` — exact inner-product search (= cosine on normalised vectors)
- Appropriate for 200-400 chunk corpus (no approximation needed)
- Persisted to `data/vector_store/index.faiss` + `metadata.json`
- In-memory cache for fast repeated queries

### 6. Safety Layer (`src/safety/classifier.py`)
Four-category classifier:

| Category | Trigger | Response |
|---|---|---|
| `FACTUAL_ALLOWED` | Keywords: expense ratio, exit load, SIP, lock-in, riskometer, benchmark, etc. | Proceed to RAG |
| `INVESTMENT_ADVICE` | "Should I buy/sell", "which is best", "will give returns", etc. | Safe refusal |
| `PII_DETECTED` | PAN pattern, Aadhaar, phone, email, OTP intent phrases | PII warning |
| `OUT_OF_SCOPE` | Stocks, crypto, market prediction, non-MF topics | Scope explanation |

### 7. RAG Generation (`src/generation/generator.py`)
- System prompt enforces: facts-only, max 3 sentences, one source URL, no advice
- Temperature = 0.0 for deterministic factual answers
- Fallback: extracts first 3 sentences from top chunk if LLM unavailable
- Never invents facts — if no relevant context → returns "I couldn't verify..."

### 8. Citation Validation (`src/citations/validator.py`)
- Validates source URL against approved domains: `sbimf.com`, `amfiindia.com`, `sebi.gov.in`
- Cross-checks against `data/sources.csv`
- Auto-repairs missing/unapproved URLs from chunk metadata
- Appends standard SEBI disclaimer to every factual answer

---

## Data Flow Summary

```
sources.csv (25 sources)
    → seed_data.py (writes data/processed/SRC*.json)
    → cleaner.py (removes boilerplate)
    → chunker.py (splits into chunks with metadata)
    → embedder.py (384-dim vectors)
    → vector_store.py (FAISS index)

User query
    → classifier.py (safety gate)
    → retriever.py (FAISS search)
    → generator.py (LLM with context)
    → validator.py (citation check)
    → API response (answer + source + date + disclaimer)
```

---

## Technology Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI 0.111 |
| Frontend | Next.js 14 (App Router, TypeScript) |
| Styling | Tailwind CSS |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 |
| Vector Store | FAISS (faiss-cpu) |
| PDF Extraction | pdfplumber |
| HTML Extraction | BeautifulSoup4 |
| Testing | pytest |

---

## Security & Privacy

- PII never stored, logged, or echoed
- Investment advice never reaches LLM
- All source URLs validated against approved domains
- No third-party financial data sources used
- API keys loaded from environment variables only
