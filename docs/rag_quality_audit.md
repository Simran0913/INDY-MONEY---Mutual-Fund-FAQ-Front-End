# RAG Quality Audit Report
## Facts-Only Mutual Fund FAQ Assistant

---

## Audit Date: 2026-10-02

---

## 1. Retrieval Accuracy

### Test: Key factual queries → correct chunks retrieved

| Query | Expected Source | Scheme Filter Detected | Status |
|---|---|---|---|
| "expense ratio of SBI Bluechip Fund" | SRC001/SRC002/SRC011 | SBI Bluechip Fund | ✅ |
| "exit load SBI Small Cap Fund" | SRC007/SRC008/SRC023 | SBI Small Cap Fund | ✅ |
| "ELSS lock-in period" | SRC004/SRC017/SRC021/SRC025 | SBI Magnum Tax Gain Scheme | ✅ |
| "minimum SIP" | SRC014 + scheme KIMs | Auto-detected from query | ✅ |
| "riskometer" | SRC018 + factsheet | None (all schemes) | ✅ |
| "benchmark SBI Liquid Fund" | SRC005/SRC006/SRC011 | SBI Liquid Fund | ✅ |
| "download account statement" | SRC012 | None (all schemes) | ✅ |
| "capital gains statement" | SRC013 | None (all schemes) | ✅ |

**Min score threshold**: 0.25 — prevents irrelevant chunks from being returned.

**Scheme filter**: `extract_scheme_from_query()` detects scheme from keywords, boosting relevant chunks to top of results.

---

## 2. Grounding Check

### Verified facts in seed data vs. public domain knowledge

| Fact | Value in Seed | Source |
|---|---|---|
| SBI Bluechip Fund TER (Direct) | ~0.83% p.a. | SRC002, SRC011 |
| SBI Bluechip Fund TER (Regular) | ~1.64% p.a. | SRC002, SRC011 |
| SBI Liquid Fund TER (Direct) | ~0.20% p.a. | SRC006, SRC011 |
| SBI Magnum Tax Gain TER (Direct) | ~0.91% p.a. | SRC004, SRC011 |
| SBI Small Cap Fund TER (Direct) | ~0.70% p.a. | SRC008, SRC011 |
| SBI Balanced Advantage TER (Direct) | ~0.45% p.a. | SRC010, SRC011 |
| SBI Bluechip Fund Exit Load | 1% within 1 yr (>10%) | SRC001, SRC002, SRC023 |
| ELSS Lock-in | 3 years (statutory) | SRC004, SRC017, SRC021, SRC025 |
| SBI Liquid Fund Exit Load | Graded (D1: 0.007%, Nil from D7) | SRC006, SRC023 |
| SBI Magnum Tax Gain Exit Load | Nil | SRC004, SRC023 |
| SBI Bluechip Fund Min SIP | Rs. 500 | SRC002, SRC014 |
| SBI Liquid Fund Min SIP | Rs. 1,000 | SRC006, SRC014 |
| SBI Bluechip Fund Benchmark | S&P BSE 100 TRI | SRC001, SRC002, SRC024 |
| SBI Liquid Fund Riskometer | Low to Moderate | SRC005, SRC011, SRC018 |
| ELSS 80C benefit | Up to Rs. 1,50,000 | SRC017, SRC021, SRC025 |

**Result: All seeded facts are consistent across multiple sources. No contradictions found.**

---

## 3. Citation Accuracy

### Validation rules (enforced by `validator.py`):

| Rule | Enforcement | Status |
|---|---|---|
| Source URL in every factual answer | Auto-repair from chunk if missing | ✅ |
| URL from approved domain only | `_is_approved_url()` check | ✅ |
| URL cross-checked against sources.csv | Domain + CSV check | ✅ |
| Third-party URLs rejected | Domain blocklist | ✅ |
| Last updated date required | Auto-repair from chunk if missing | ✅ |
| Standard disclaimer appended | Always appended | ✅ |

---

## 4. Scheme Matching Accuracy

### Scheme detection keywords tested:

| Keyword | Detected Scheme | Correct? |
|---|---|---|
| "bluechip" | SBI Bluechip Fund | ✅ |
| "large cap" | SBI Bluechip Fund | ✅ |
| "magnum tax" | SBI Magnum Tax Gain Scheme | ✅ |
| "elss" | SBI Magnum Tax Gain Scheme | ✅ |
| "80c" | SBI Magnum Tax Gain Scheme | ✅ |
| "tax saving" | SBI Magnum Tax Gain Scheme | ✅ |
| "liquid fund" | SBI Liquid Fund | ✅ |
| "small cap" | SBI Small Cap Fund | ✅ |
| "balanced advantage" | SBI Balanced Advantage Fund | ✅ |
| "dynamic asset allocation" | SBI Balanced Advantage Fund | ✅ |

**No scheme keyword → searches all sources** (appropriate fallback).

---

## 5. Refusal Behaviour

### Investment advice queries — classifier tested:

| Query | Category | Reaches LLM? | Status |
|---|---|---|---|
| "Should I buy this fund?" | INVESTMENT_ADVICE | ❌ No | ✅ |
| "Which fund is best?" | INVESTMENT_ADVICE | ❌ No | ✅ |
| "Will this fund give returns?" | INVESTMENT_ADVICE | ❌ No | ✅ |
| "Is this fund suitable for me?" | INVESTMENT_ADVICE | ❌ No | ✅ |
| "Recommend a good fund" | INVESTMENT_ADVICE | ❌ No | ✅ |

**All advice queries blocked at classifier layer — zero LLM calls for advice.**

---

## 6. PII Handling

See [`docs/privacy_audit.md`](privacy_audit.md) for full PII audit.

Summary: All PII checks pass. PII never logged, stored, or echoed.

---

## 7. Answer Length Check

### System prompt enforces max 3 sentences.

Tested query formats and verified output:
- Direct scheme facts (expense ratio, exit load): typically 2-3 sentences ✅
- Process questions (how to download statement): 3-4 steps described concisely ✅
- Regulatory facts (ELSS lock-in, TER limits): 2-3 sentences ✅

---

## 8. Hallucination Risk Assessment

| Risk Factor | Mitigation |
|---|---|
| LLM inventing financial values | System prompt: "ONLY use retrieved context" |
| LLM not finding answer | min_score threshold → fallback if no relevant chunks |
| LLM generating wrong URL | Citation validator auto-repairs or rejects |
| LLM giving investment advice | Safety classifier blocks before LLM call |
| Outdated data | last_updated field shown in every answer |
| Empty retrieved context | Generator returns FALLBACK_RESPONSE, not an invented answer |

**No hallucination paths identified. All paths lead to either a grounded answer or an explicit fallback.**

---

## 9. Source Freshness

| Source Type | Last Updated | Freshness Risk |
|---|---|---|
| Scheme pages | 2024-03-31 | Medium (TER changes monthly) |
| KIMs | 2024-03-31 | Medium |
| Monthly Factsheet | 2024-04-30 | Medium |
| AMFI educational pages | 2024-01-01 | Low (stable definitions) |
| SEBI circulars | 2005–2018 | Low (regulations don't change frequently) |

**Mitigation:** Every answer shows "Last updated from sources: [date]" so users know the data vintage. For latest TER, users are directed to amfiindia.com.

---

## Summary

| Quality Dimension | Result |
|---|---|
| Retrieval accuracy | ✅ High — scheme filter + min_score threshold |
| Grounding | ✅ All facts sourced from official documents |
| Citation accuracy | ✅ All answers cite approved official URLs |
| Scheme matching | ✅ 10/10 keywords correctly detected |
| Refusal behaviour | ✅ 5/5 advice queries correctly refused |
| PII handling | ✅ All PII checks pass |
| Answer length | ✅ Max 3 sentences enforced |
| Hallucination risk | ✅ Mitigated at 3 layers |
| Source freshness | ⚠️ Data as of 2024 — recommend refresh for production |

**Overall RAG quality: HIGH for a student project corpus. Ready for demo.**
