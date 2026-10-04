"""
test_ingestion.py
-----------------
Tests for seed data and document ingestion pipeline.
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.ingestion.seed_data import SEED_DOCUMENTS, seed_processed_documents


class TestSeedData:

    def test_seed_documents_count(self):
        """Must have exactly 25 seed documents matching sources.csv."""
        assert len(SEED_DOCUMENTS) == 25, (
            f"Expected 25 seed documents, got {len(SEED_DOCUMENTS)}"
        )

    def test_all_required_fields_present(self):
        required = ["source_id", "title", "scheme", "source_url",
                    "organization", "source_type", "last_updated", "date_accessed", "text"]
        for doc in SEED_DOCUMENTS:
            for field in required:
                assert field in doc, f"[{doc.get('source_id')}] Missing field: {field}"

    def test_source_ids_unique(self):
        ids = [d["source_id"] for d in SEED_DOCUMENTS]
        assert len(ids) == len(set(ids)), "Duplicate source IDs in seed data"

    def test_source_ids_match_csv_pattern(self):
        for doc in SEED_DOCUMENTS:
            sid = doc["source_id"]
            assert sid.startswith("SRC"), f"Source ID doesn't start with SRC: {sid}"
            assert sid[3:].isdigit(), f"Source ID suffix not numeric: {sid}"

    def test_all_urls_from_approved_domains(self):
        from src.citations.validator import _is_approved_url
        for doc in SEED_DOCUMENTS:
            url = doc["source_url"]
            assert _is_approved_url(url), (
                f"[{doc['source_id']}] URL not from approved domain: {url}"
            )

    def test_no_third_party_urls(self):
        banned = ["groww.in", "moneycontrol.com", "etmoney.com", "zerodha.com",
                  "reddit.com", "quora.com", "economictimes"]
        for doc in SEED_DOCUMENTS:
            url = doc["source_url"].lower()
            for banned_domain in banned:
                assert banned_domain not in url, (
                    f"[{doc['source_id']}] Third-party URL found: {url}"
                )

    def test_text_not_empty(self):
        for doc in SEED_DOCUMENTS:
            assert len(doc["text"].strip()) >= 100, (
                f"[{doc['source_id']}] Text too short: {len(doc['text'])} chars"
            )

    def test_all_five_schemes_covered(self):
        schemes_in_data = {d["scheme"] for d in SEED_DOCUMENTS}
        required_schemes = {
            "SBI Bluechip Fund",
            "SBI Magnum Tax Gain Scheme",
            "SBI Liquid Fund",
            "SBI Small Cap Fund",
            "SBI Balanced Advantage Fund",
        }
        for scheme in required_schemes:
            covered = any(
                scheme in d["scheme"] or d["scheme"] == "All Schemes"
                for d in SEED_DOCUMENTS
            )
            assert covered, f"No seed document covers scheme: {scheme}"

    def test_key_topics_covered(self):
        """Verify key financial topics are present in seed text corpus."""
        all_text = " ".join(d["text"].lower() for d in SEED_DOCUMENTS)
        topics = {
            "expense ratio"  : "expense ratio" in all_text or "ter" in all_text,
            "exit load"      : "exit load" in all_text,
            "minimum sip"    : "minimum sip" in all_text or "sip amount" in all_text,
            "elss lock-in"   : "lock-in" in all_text or "3 years" in all_text,
            "riskometer"     : "riskometer" in all_text,
            "benchmark"      : "benchmark" in all_text,
            "account statement": "account statement" in all_text,
            "capital gains"  : "capital gain" in all_text,
        }
        for topic, found in topics.items():
            assert found, f"Key topic not found in seed corpus: {topic}"

    def test_seed_writes_json_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = seed_processed_documents(Path(tmpdir), force=True)
            assert result["written"] == 25
            files = list(Path(tmpdir).glob("SRC*.json"))
            assert len(files) == 25

    def test_seed_json_valid_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            seed_processed_documents(Path(tmpdir), force=True)
            for jf in Path(tmpdir).glob("SRC*.json"):
                data = json.loads(jf.read_text(encoding="utf-8"))
                assert "text" in data
                assert "source_url" in data
                assert "source_id" in data

    def test_no_pii_in_seed_text(self):
        """Seed text must not contain PAN, Aadhaar, phone numbers, or emails."""
        import re
        pan_pattern     = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
        aadhaar_pattern = re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b")
        # Phone: 10 digits starting with 6-9 (excluding financial values)
        phone_pattern   = re.compile(r"\b[6-9]\d{9}\b")

        for doc in SEED_DOCUMENTS:
            text = doc["text"]
            assert not pan_pattern.search(text), f"[{doc['source_id']}] PAN found in seed text"
            assert not aadhaar_pattern.search(text), f"[{doc['source_id']}] Aadhaar found in seed text"
            assert not phone_pattern.search(text), f"[{doc['source_id']}] Phone number found in seed text"
