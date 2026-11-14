"""Hand-authored references over synthetic PDFs; no institutional evaluation."""
import copy
import importlib
import time
from dataclasses import replace

import pytest
from reportlab.pdfgen import canvas

from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot, bytes_sha256


@pytest.fixture
def gate():
    return importlib.import_module("backend.bintanong_tools.document_ingest.ocr_gate")


def pair(gate, tmp_path, index=0, text="Shall not pay 50 pesos."):
    path = tmp_path / f"source-{index}.pdf"
    pdf = canvas.Canvas(str(path), pagesize=(120, 80))
    pdf.drawString(1, 40, str(index))
    pdf.showPage()
    pdf.save()
    snapshot = InputSnapshot(path)
    annotation = {"origin": "human_pdf_manual", "reference_id": f"manual-{index}",
        "reviewer": "human-reviewer", "review_date": "2026-10-10", "pages": [
            {"page": 1, "printed_page_label": None, "text": text}], "critical_regions": [
            {"id": "clause-1", "kind": "negation", "page": 1, "start": 0, "end": len(text)}]}
    frozen = gate.freeze_reference(snapshot, annotation)
    candidate = {"origin": "ocr_candidate", "source_sha256": snapshot.sha256,
        "version_id": f"ver-{snapshot.sha256}", "source_format": "pdf", "page_count": 1,
        "started_at_ns": time.time_ns(), "metadata": {"engine": "tesseract", "config": "tesseract-eng",
            "lang": "eng", "engine_version": "stub-1", "device": "cpu", "images": 1, "seconds": 0.1},
        "pages": [{"binding": {"kind": "pdf_page", "page": 1}, "size": [120, 80],
            "text": text, "words": [{"text": text, "conf": 41.25, "box": [1, 1, 110, 30]}]}]}
    return snapshot, frozen, candidate, annotation


def test_identical_text_zero_cer_is_allowed(gate, tmp_path):
    snapshot, frozen, candidate, _ = pair(gate, tmp_path)
    result = gate.score_document(snapshot, frozen, candidate)
    assert result["cer"] == 0 and result["critical_errors"] == []


def test_dropped_negation_is_silent_critical_despite_tiny_cer(gate, tmp_path):
    text = "Shall not pay 50 pesos.\n" + "Neutral evidence.\n" * 500
    snapshot, frozen, candidate, _ = pair(gate, tmp_path, text=text)
    candidate["pages"][0]["text"] = text.replace("not ", "", 1)
    result = gate.score_document(snapshot, frozen, candidate)
    assert result["cer"] < 0.001
    assert result["critical_errors"][0]["kind"] == "negation"
    assert result["silent_critical"] == 1


def test_missing_and_invented_content_reported(gate, tmp_path):
    snapshot, frozen, candidate, _ = pair(gate, tmp_path, text="Shall not pay.\nRequired form.")
    candidate["pages"][0]["text"] = "Shall not pay.\nNew content."
    result = gate.score_document(snapshot, frozen, candidate)
    assert result["missing_chars"] > 0 and result["invented_chars"] > 0


def test_frozen_reference_tamper_refused(gate, tmp_path):
    snapshot, frozen, candidate, _ = pair(gate, tmp_path)
    altered = replace(frozen, payload=frozen.payload.replace(b"not pay", b"may pay"))
    with pytest.raises(ValueError, match="digest"):
        gate.score_document(snapshot, altered, candidate)


def test_candidate_cannot_be_its_own_reference(gate, tmp_path):
    snapshot, _, candidate, annotation = pair(gate, tmp_path)
    with pytest.raises(ValueError, match="manual"):
        gate.freeze_reference(snapshot, candidate)
    annotation["origin"] = "ocr_candidate"
    with pytest.raises(ValueError, match="manual"):
        gate.freeze_reference(snapshot, annotation)


def test_less_than_ten_distinct_sources_is_blocked_not_run(gate, tmp_path):
    triples = [pair(gate, tmp_path, i)[:3] for i in range(9)]
    result = gate.evaluate(triples)
    assert result["status"] == "blocked" and result["evaluation"] == "NOT RUN"


def test_duplicate_aliases_do_not_count_as_ten(gate, tmp_path):
    triple = pair(gate, tmp_path)[:3]
    result = gate.evaluate([triple] * 10)
    assert result["distinct_sources"] == 1 and result["status"] == "blocked"


def test_worst_document_next_to_pooled_metrics_and_failure(gate, tmp_path):
    triples = [pair(gate, tmp_path, i, text="Shall not pay 50 pesos. " * (1 if i == 0 else 100))[:3]
               for i in range(10)]
    triples[0][2]["pages"][0]["text"] = "Shall pay 50 pesos."
    result = gate.evaluate(triples)
    assert result["evaluation"] == "RUN" and result["status"] == "fail"
    assert result["worst_document"]["source_sha256"] == triples[0][0].sha256
    assert result["worst_document"]["cer"] > result["pooled_cer"]
    assert result["institutional_certification"] is False


@pytest.mark.parametrize("mutation", ["source", "page", "metadata", "time"])
def test_candidate_binding_and_metadata_refused(gate, tmp_path, mutation):
    snapshot, frozen, candidate, _ = pair(gate, tmp_path)
    if mutation == "source":
        candidate["source_sha256"] = "a" * 64
    elif mutation == "page":
        candidate["pages"][0]["binding"]["page"] = 2
    elif mutation == "metadata":
        del candidate["metadata"]["engine_version"]
    else:
        candidate["started_at_ns"] = frozen.frozen_at_ns - 1
    with pytest.raises(ValueError):
        gate.score_document(snapshot, frozen, candidate)


def test_source_tamper_refused(gate, tmp_path):
    snapshot, frozen, candidate, _ = pair(gate, tmp_path)
    snapshot.path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="changed"):
        gate.score_document(snapshot, frozen, candidate)


@pytest.mark.parametrize("mutation", ["page", "critical_page", "range", "empty_critical"])
def test_manual_page_map_and_critical_evidence_bound_before_freeze(gate, tmp_path, mutation):
    snapshot, _, _, annotation = pair(gate, tmp_path)
    if mutation == "page":
        annotation["pages"][0]["page"] = 2
    elif mutation == "critical_page":
        annotation["critical_regions"][0]["page"] = 2
    elif mutation == "range":
        annotation["critical_regions"][0]["end"] = 999
    else:
        annotation["critical_regions"] = []
    with pytest.raises(ValueError):
        gate.freeze_reference(snapshot, annotation)


def test_same_phrase_elsewhere_does_not_hide_dropped_negation(gate, tmp_path):
    text = "Applicants shall not pay.\nOfficers shall not pay."
    snapshot, frozen, candidate, annotation = pair(gate, tmp_path, text=text)
    annotation["critical_regions"][0]["end"] = len("Applicants shall not pay.")
    frozen = gate.freeze_reference(snapshot, annotation)
    candidate["started_at_ns"] = time.time_ns()
    candidate["pages"][0]["text"] = "Applicants shall pay.\nOfficers shall not pay."
    result = gate.score_document(snapshot, frozen, candidate)
    assert len(result["critical_errors"]) == 1


def test_candidate_provided_critical_values_are_never_oracle(gate, tmp_path):
    snapshot, frozen, candidate, _ = pair(gate, tmp_path)
    candidate["critical_regions"] = [{"text": "Shall not pay 50 pesos."}]
    candidate["pages"][0]["text"] = "Shall pay 50 pesos."
    assert gate.score_document(snapshot, frozen, candidate)["critical_errors"]
