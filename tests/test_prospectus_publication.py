"""process_prospectus never touches earlier outputs until conversion and audit have finished."""

from __future__ import annotations

import hashlib
import json

import pytest

from backend.bintanong_tools.prospectus_extractor import common, publish

pytestmark = pytest.mark.usefixtures("fake_docling")

EXPECTED_SCHEMA = "palsu-prospectus-v3.2"  # Phase C's value plus one minor; see "SCHEMA_VERSION change"


def leftovers(folder):
    return [p.name for p in folder.iterdir() if p.name.startswith(".")]


def test_conversion_exception_after_a_good_run_leaves_earlier_files_byte_identical(
    tmp_path, pdf_factory, converter, failing_converter, pipeline_state, process, snapshot
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    before = snapshot(out)
    assert {"a_prospectus.json", "a_essentials.json", "a_prospectus.pl", "a_rag.jsonl",
            "a_review.csv", "a_docling.json", "a_docling.meta.json", "a_publish.json"} <= set(before)

    pdf.write_bytes(b"%PDF-two")
    with pytest.raises(RuntimeError, match="converter exploded"):
        process(pdf, out, failing_converter)

    assert snapshot(out) == before
    record = json.loads((out / "failed" / "a" / "failure.json").read_text(encoding="utf-8"))
    assert record["error_type"] == "RuntimeError"
    assert leftovers(out) == []


def test_failure_after_conversion_keeps_the_new_json_only_in_failed(
    tmp_path, pdf_factory, converter, pipeline_state, process, snapshot
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)  # D6: the good run's cache stays with the good run's outputs
    before = snapshot(out)

    pdf.write_bytes(b"%PDF-two")
    pipeline_state.fail = ValueError("parser blew up")
    with pytest.raises(ValueError, match="parser blew up"):
        process(pdf, out, converter)

    assert snapshot(out) == before
    kept = json.loads((out / "failed" / "a" / "a_docling.json").read_text(encoding="utf-8"))
    assert kept["marker"] == "%PDF-two"
    assert leftovers(out) == []


def test_a_good_run_clears_older_diagnostics(
    tmp_path, pdf_factory, converter, pipeline_state, process
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    pipeline_state.fail = ValueError("first attempt fails")
    with pytest.raises(ValueError):
        process(pdf, out, converter)
    assert (out / "failed" / "a" / "failure.json").is_file()
    pipeline_state.fail = None
    process(pdf, out, converter)
    assert not (out / "failed").exists()


def test_audit_error_run_is_published_and_removes_stale_companions(
    tmp_path, pdf_factory, converter, pipeline_state, process
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    assert (out / "a_prospectus.pl").is_file() and (out / "a_rag.jsonl").is_file()

    pdf.write_bytes(b"%PDF-two")
    pipeline_state.status = "error"
    payload = process(pdf, out, converter)

    assert payload["audit"]["status"] == "error"
    assert json.loads((out / "a_prospectus.json").read_text(encoding="utf-8"))["audit"]["status"] == "error"
    assert not (out / "a_prospectus.pl").exists()
    assert not (out / "a_rag.jsonl").exists()
    assert publish.read_manifest(out / "a_publish.json")["audit_status"] == "error"


def test_publication_order_puts_the_main_json_before_the_manifest(
    tmp_path, monkeypatch, pdf_factory, converter, pipeline_state, process
):
    order = []
    real = publish.replace_file
    monkeypatch.setattr(publish, "replace_file",
                        lambda source, target, *a, **k: (order.append(target.name), real(source, target, *a, **k)))
    pdf = pdf_factory(tmp_path / "in")
    process(pdf, tmp_path / "out", converter)
    assert order == ["a_docling.json", "a_docling.meta.json", "a_essentials.json", "a_prospectus.pl",
                     "a_rag.jsonl", "a_review.csv", "a_prospectus.json", "a_publish.json"]


def test_a_crash_between_replaces_is_detected_by_the_manifest(
    tmp_path, monkeypatch, pdf_factory, converter, pipeline_state, process, snapshot
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    old_manifest = (out / "a_publish.json").read_bytes()

    real = publish.replace_file

    def dies_at_the_main_json(source, target, *a, **k):
        if target.name == "a_prospectus.json":
            raise OSError("disk pulled")
        real(source, target, *a, **k)

    monkeypatch.setattr(publish, "replace_file", dies_at_the_main_json)
    pdf.write_bytes(b"%PDF-two")
    with pytest.raises(OSError, match="disk pulled"):
        process(pdf, out, converter)

    assert (out / "a_publish.json").read_bytes() == old_manifest  # manifest is written last
    manifest = publish.read_manifest(out / "a_publish.json")
    ok, why = publish.verify_published(out, manifest)
    assert ok is False and "changed since it was published" in why
    assert leftovers(out) == []


def test_payload_records_how_it_was_made(
    tmp_path, pdf_factory, converter, pipeline_state, process
):
    pdf = pdf_factory(tmp_path / "in", body=b"%PDF-one")
    out = tmp_path / "out"
    first = process(pdf, out, converter, force_reconvert=False)
    identity_block = first["run_identity"]
    assert identity_block["input_kind"] == "pdf"
    assert identity_block["pdf_sha256"] == hashlib.sha256(b"%PDF-one").hexdigest()
    assert identity_block["cache"] == "converted"
    assert identity_block["review_input_only"] is False
    assert json.loads((out / "a_prospectus.json").read_text(encoding="utf-8"))["run_identity"] == identity_block
    assert publish.read_manifest(out / "a_publish.json")["run_key"] == identity_block["run_key"]

    second = process(pdf, out, converter, force_reconvert=False)
    assert second["run_identity"]["cache"] == "reused"
    assert second["run_identity"]["run_key"] == identity_block["run_key"]
    assert len(converter.calls) == 1


def test_docling_json_input_is_marked_as_a_review_input(
    tmp_path, pipeline_state, process, snapshot
):
    raw = tmp_path / "in" / "a_docling.json"
    raw.parent.mkdir()
    raw.write_text(json.dumps({"texts": [{"text": "BS", "label": "text"}], "tables": []}), encoding="utf-8")
    out = tmp_path / "out"
    payload = process(raw, out, None)

    block = payload["run_identity"]
    assert block["input_kind"] == "docling-json"
    assert block["review_input_only"] is True
    assert block["cache"] == "not-applicable"
    assert "review input only" in block["review_note"]
    assert "a_essentials.json" not in snapshot(out)  # essentials still require a source PDF


def test_schema_version_names_the_new_payload_shape():
    assert common.SCHEMA_VERSION == EXPECTED_SCHEMA


def test_output_inside_the_input_folder_is_still_refused(tmp_path, pdf_factory, converter, pipeline_state):
    from backend.bintanong_tools.prospectus_extractor import pipeline

    pdf = pdf_factory(tmp_path / "in")
    with pytest.raises(ValueError, match="distinct from the source"):
        pipeline.process_prospectus(pdf, output_path=pdf, converter=converter, quiet=True)


# --- Phase B markup twin and output sets written before Phase D (no publish manifest)


def test_markup_twin_is_published_just_before_the_main_json(
    tmp_path, monkeypatch, pdf_factory, converter, pipeline_state, process
):
    from backend.bintanong_tools.prospectus_extractor import pipeline

    monkeypatch.setattr(pipeline, "render_prospectus_markup", lambda document, payload: "twin\n")
    order = []
    real = publish.replace_file
    monkeypatch.setattr(publish, "replace_file",
                        lambda source, target, *a, **k: (order.append(target.name), real(source, target, *a, **k)))
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, export_md=True)
    assert order[-3:] == ["a_prospectus.md", "a_prospectus.json", "a_publish.json"]
    assert (out / "a_prospectus.md").read_bytes() == b"twin\n"
    assert "a_prospectus.md" in publish.read_manifest(out / "a_publish.json")["files"]


def test_companions_of_an_output_set_without_a_manifest_are_removed_after_publication(
    tmp_path, pdf_factory, converter, pipeline_state
):
    from backend.bintanong_tools.prospectus_extractor import pipeline

    out = tmp_path / "out"
    out.mkdir()
    for name in ("a_prospectus.pl", "a_rag.jsonl", "a_prospectus.md", "a_review.csv"):
        (out / name).write_text("written before Phase D", encoding="utf-8")
    pdf = pdf_factory(tmp_path / "in")
    pipeline_state.status = "error"
    pipeline.process_prospectus(
        pdf, output_path=out / "a_prospectus.json", export_pl=True, export_jsonl=True,
        export_csv=False, converter=converter, semantic_doc_path=None, quiet=True,
    )
    for name in ("a_prospectus.pl", "a_rag.jsonl", "a_prospectus.md", "a_review.csv"):
        assert not (out / name).exists(), name
    assert (out / "a_docling.json").is_file()  # the cache is never a stale companion


def test_the_b2_fixer_reads_the_pdf_hash_this_run_recorded(
    tmp_path, pdf_factory, converter, pipeline_state, process
):
    from backend.bintanong_tools.prospectus_extractor.fixer_cli import resolve_identity

    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    written = json.loads((out / "a_prospectus.json").read_text(encoding="utf-8"))
    found = resolve_identity(written)
    assert found["how"] == "run_identity"
    assert found["pdf_sha256"] == hashlib.sha256(b"%PDF-one").hexdigest()


def test_outputs_are_written_with_lf_line_endings(tmp_path, pdf_factory, converter, pipeline_state, process):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    for name in ("a_prospectus.json", "a_essentials.json", "a_prospectus.pl", "a_rag.jsonl", "a_publish.json"):
        assert b"\r\n" not in (out / name).read_bytes(), name
