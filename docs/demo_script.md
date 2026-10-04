# Demo Script — 3-Minute Demo
## Facts-Only Mutual Fund FAQ Assistant

---

## Pre-Demo Checklist

- [ ] Backend running: `uvicorn api.main:app --reload` (port 8000)
- [ ] Frontend running: `cd app && npm run dev` (port 3000)
- [ ] Browser open at: http://localhost:3000
- [ ] Index built (if first time): Click "Build / Rebuild knowledge index"
- [ ] `OPENAI_API_KEY` set in `.env`

---

## PART 1 — Problem Statement (30 seconds)

> "Mutual fund investors often need quick answers to basic factual questions — what is the expense ratio? what is the exit load? how do I download my statement? But existing tools either give investment advice they shouldn't, use unreliable third-party sources, or can't cite where the information came from.

> This project builds a Facts-Only RAG chatbot that answers verified factual questions using only official sources — from SEBI, AMFI, and the AMC itself — with one clear citation for every answer."

---

## PART 2 — AMC and Schemes (20 seconds)

> "We selected **SBI Mutual Fund** — India's largest AMC by AUM — because it has well-documented, publicly available scheme information.

> We cover 5 schemes:"

Point to the scheme drawer at the bottom of the UI:
- SBI Bluechip Fund (large cap equity)
- SBI Magnum Tax Gain Scheme (ELSS — covers lock-in questions)
- SBI Liquid Fund (covers debt/liquid questions)
- SBI Small Cap Fund (small cap equity)
- SBI Balanced Advantage Fund (hybrid)

---

## PART 3 — Official Source Corpus (20 seconds)

> "We collected 25 official public sources — zero third-party websites."

Open `data/sources.csv` briefly or `docs/source_list.md`:

> "15 sources from sbimf.com — scheme pages, KIMs, SIDs, FAQs.
> 6 sources from AMFI — educational pages, TER disclosures.
> 4 sources from SEBI — regulatory circulars on TER, ELSS lock-in, scheme categories."

---

## PART 4 — Live Demo: Factual Question (40 seconds)

Type in the chat box:

**"What is the expense ratio of SBI Bluechip Fund?"**

Wait for response. Point out:

> "The answer is grounded purely in the official source. Notice:"

- ✅ **Answer** — factual, maximum 3 sentences
- ✅ **Source** — one official sbimf.com link
- ✅ **Last updated from sources** — date from the document
- ✅ **Disclaimer** — standard SEBI disclaimer

> "No invention. No opinion. Just verified facts with a source."

---

## PART 5 — Live Demo: Investment Advice Refusal (20 seconds)

Type in the chat box:

**"Should I buy SBI Bluechip Fund?"**

Wait for response. Point out the amber refusal card:

> "The system classifies this as an investment advice request and refuses before it even reaches the retrieval layer. The LLM is never asked to give advice."

> "The refusal directs users to a SEBI-registered investment advisor — not to a random source."

---

## PART 6 — Live Demo: PII Warning (20 seconds)

Type in the chat box:

**"Can I give you my PAN number?"**

Wait for response:

> "PII is detected at the classifier layer using regex patterns. The system warns the user, never stores the PII, never logs it."

---

## PART 7 — RAG Architecture Brief (20 seconds)

> "Under the hood, the pipeline is:"

```
Official Sources → Seed Documents → Clean → Chunk → Embed → FAISS Index
User Query → Safety Check → Scheme Detect → FAISS Search → LLM → Citation Validate → Response
```

> "The embedding model runs locally — no extra API key. Only OpenAI is needed for generation, with a graceful fallback if unavailable."

---

## PART 8 — Project Deliverables (30 seconds)

Show briefly in file explorer:

- `data/sources.csv` — 25 official sources
- `docs/source_list.md` — full source documentation
- `docs/sample_qa.md` — 10 Q&A examples
- `docs/architecture.md` — full architecture diagram
- `tests/` — test suite covering safety, chunking, citations, ingestion
- `README.md` — complete setup and usage guide

---

## Key Talking Points

- **Facts only** — system prompt, classifier, and citation validator enforce this at 3 layers
- **No PII** — never stored, never logged, never echoed
- **No third-party sources** — only sbimf.com, amfiindia.com, sebi.gov.in
- **Every answer cites ONE official source**
- **Graceful degradation** — chunk-based fallback if LLM API is unavailable

---

## Demo Tips

- If the index isn't built, click the "Build / Rebuild knowledge index" button first
- First build downloads ~80MB (sentence-transformers model) — takes ~1-2 minutes
- Subsequent starts load from cache — instant
- If OpenAI API key not set, the system returns chunk-based fallback answers (still factual, still cited)
