import json

import pytest

pytest.importorskip("reportlab")
pytest.importorskip("PIL")
pytest.importorskip("pypdf")

from generator import DOCUMENT_TYPES, generate_document, generate_document_pack, generate_matter
from generator.documents import pdf_embedded_text


def test_scan_documents_have_no_embedded_text(tmp_path):
    matter = generate_matter("full-estate-administration", 9)
    artifact = generate_document(matter, "death_certificate", tmp_path, seed=2)
    assert "SYNTHETIC TEST DOCUMENT" in pdf_embedded_text(artifact.source_pdf)
    assert pdf_embedded_text(artifact.scanned_pdf).strip() == ""
    truth = json.loads(open(artifact.ground_truth, encoding="utf-8").read())
    assert truth["synthetic"] is True
    assert truth["fields"]["phone"].startswith("(207) 555-01")


def test_document_pack_is_deterministic(tmp_path):
    matter = generate_matter("full-estate-administration", 3)
    first = generate_document_pack(matter, tmp_path / "a", 4, ["bank_statement", "signed_deed"])
    second = generate_document_pack(matter, tmp_path / "b", 4, ["bank_statement", "signed_deed"])
    for left, right in zip(first["artifacts"], second["artifacts"]):
        assert left["sha256"] == right["sha256"]


def test_all_document_recipes_generate(tmp_path):
    matter = generate_matter("full-estate-administration", 1)
    pack = generate_document_pack(matter, tmp_path, 1)
    assert {item["document_type"] for item in pack["artifacts"]} == set(DOCUMENT_TYPES)
