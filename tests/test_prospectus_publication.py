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
    assert order == ["a_essentials.json", "a_prospectus.pl", "a_rag.jsonl", "a_review.csv",
                     "a_prospectus.json", "a_docling.json", "a_docling.meta.json", "a_publish.json"]


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
    assert block["cache_files"] == {}
    manifest = publish.read_manifest(out / "a_publish.json")
    assert manifest["cache_files"] == {}
    assert publish.verify_published(out, manifest) == (True, "all files match")
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

    monkeypatch.setattr(pipeline, "render_prospectus_markup", lambda document, payload, *, pdf_sha256=None: "twin\n")
    order = []
    real = publish.replace_file
    monkeypatch.setattr(publish, "replace_file",
                        lambda source, target, *a, **k: (order.append(target.name), real(source, target, *a, **k)))
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, export_md=True)
    assert order[-5:] == ["a_prospectus.md", "a_prospectus.json", "a_docling.json",
                          "a_docling.meta.json", "a_publish.json"]
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


@pytest.mark.parametrize("reuse", [False, True])
def test_publish_v2_binds_the_exact_loaded_cache(tmp_path, monkeypatch, pdf_factory, converter,
                                              pipeline_state, process, reuse):
    from backend.bintanong_tools.prospectus_extractor import pipeline
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    if reuse:
        process(pdf, out, converter)
    captures = []
    real = pipeline.load_document_result
    def capture(*args, **kwargs):
        loaded = real(*args, **kwargs)
        captures.append(loaded)
        return loaded
    monkeypatch.setattr(pipeline, "load_document_result", capture)
    payload = process(pdf, out, converter)
    loaded = captures[0]
    manifest = publish.read_manifest(out / "a_publish.json")
    assert manifest["schema"] == "palsu-prospectus-publish-v2"
    assert manifest["main_file"] == "a_prospectus.json"
    assert manifest["cache_files"] == {
        "a_docling.json": hashlib.sha256(loaded.raw_json_bytes).hexdigest(),
        "a_docling.meta.json": hashlib.sha256(loaded.meta_bytes).hexdigest(),
    } == payload["run_identity"]["cache_files"]
    assert not set(manifest["files"]) & set(manifest["cache_files"])
    assert payload["run_identity"]["cache"] == ("reused" if reuse else "converted")
    assert len(converter.calls) == 1
    assert publish.verify_published(out, manifest) == (True, "all files match")


@pytest.mark.parametrize("part", ["a_docling.json", "a_docling.meta.json"])
def test_changed_staged_cache_is_refused_before_publication(tmp_path, monkeypatch, pdf_factory,
                                                           converter, pipeline_state, process,
                                                           snapshot, part):
    from backend.bintanong_tools.prospectus_extractor import pipeline
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    before = snapshot(out)
    real = pipeline._stage_outputs
    def tamper(stage, *args, **kwargs):
        outputs = real(stage, *args, **kwargs)
        (stage / part).write_bytes(b"{}")
        return outputs
    monkeypatch.setattr(pipeline, "_stage_outputs", tamper)
    with pytest.raises(ValueError, match="cache|changed"):
        process(pdf, out, converter, force_reconvert=True)
    assert snapshot(out) == before


@pytest.mark.parametrize("mutation", ["pair", "raw", "meta", "delete-raw", "delete-meta"])
def test_reused_cache_changes_after_parse_cannot_rebind_output(tmp_path, monkeypatch, pdf_factory,
                                                              converter, pipeline_state, process,
                                                              mutation):
    from backend.bintanong_tools.prospectus_extractor import pipeline
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    raw_path, meta_path = out / "a_docling.json", out / "a_docling.meta.json"
    raw_bytes, meta_bytes = raw_path.read_bytes(), meta_path.read_bytes()
    changed_raw = json.dumps({"texts": [], "tables": [], "marker": "never parsed"}).encode()
    changed_meta = json.loads(meta_bytes)
    changed_meta["raw_json_sha256"] = hashlib.sha256(changed_raw).hexdigest()
    real = pipeline.build_payload
    def tamper(*args, **kwargs):
        payload = real(*args, **kwargs)
        if mutation in ("pair", "raw"):
            raw_path.write_bytes(changed_raw)
        if mutation in ("pair", "meta"):
            meta_path.write_bytes(json.dumps(changed_meta).encode())
        if mutation == "delete-raw":
            raw_path.unlink()
        if mutation == "delete-meta":
            meta_path.unlink()
        return payload
    monkeypatch.setattr(pipeline, "build_payload", tamper)
    result = process(pdf, out, converter)
    assert result["run_identity"]["cache"] == "reused"
    assert raw_path.read_bytes() == raw_bytes
    assert meta_path.read_bytes() == meta_bytes
    assert result["run_identity"]["cache_files"]["a_docling.json"] == hashlib.sha256(raw_bytes).hexdigest()
    assert publish.verify_published(out, publish.read_manifest(out / "a_publish.json"))[0]
    assert len(converter.calls) == 1


PUBLICATION_ORDER = ["a_essentials.json", "a_prospectus.pl", "a_rag.jsonl", "a_review.csv",
                     "a_prospectus.md", "a_prospectus.json", "a_docling.json",
                     "a_docling.meta.json", "a_publish.json"]


@pytest.mark.parametrize("step", PUBLICATION_ORDER)
@pytest.mark.parametrize("after", [False, True], ids=["before", "after"])
@pytest.mark.parametrize("stable", [False, True], ids=["changed-companions", "identical-companions"])
@pytest.mark.parametrize("change", ["new-pdf", "settings", "reconversion", "settings-identical-raw",
                                     "new-pdf-identical-raw"])
def test_interruptions_only_verify_a_coherent_generation(tmp_path, monkeypatch, pdf_factory,
                                                         converter, pipeline_state, process,
                                                         snapshot, step, after, stable, change):
    from backend.bintanong_tools.prospectus_extractor import pipeline
    monkeypatch.setattr(pipeline, "render_prospectus_markup",
                        lambda document, payload, *, pdf_sha256=None: "twin " + str(payload["nonce"]))
    if change.endswith("identical-raw"):
        from conftest import FakeDoc
        from types import SimpleNamespace
        monkeypatch.setattr(converter, "convert", lambda stream: SimpleNamespace(
            errors=[], document=FakeDoc({"texts": [], "tables": [], "marker": "constant"})))
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, export_md=True)
    before = snapshot(out)
    old = publish.read_manifest(out / "a_publish.json")
    assert publish.verify_published(out, old)[0]
    if stable:
        stage_real = pipeline._stage_outputs
        def identical_companions(stage, *args, **kwargs):
            outputs = stage_real(stage, *args, **kwargs)
            for name in outputs[:-1]:
                (stage / name).write_bytes(before[name])
            return outputs
        monkeypatch.setattr(pipeline, "_stage_outputs", identical_companions)
    if change.startswith("new-pdf"):
        pdf.write_bytes(b"%PDF-two")
    elif change.startswith("settings"):
        monkeypatch.setenv("PALSU_DOCLING_CELL_MATCHING", "false")
    elif change == "reconversion":
        real_convert = converter.convert
        def reconvert(stream):
            result = real_convert(stream)
            result.document.raw["marker"] = "new conversion of same PDF"
            return result
        monkeypatch.setattr(converter, "convert", reconvert)
    seen = []
    real = publish.replace_file
    def interrupt(source, target, *args, **kwargs):
        seen.append(target.name)
        if target.name == step and not after:
            raise OSError("injected interruption")
        real(source, target, *args, **kwargs)
        if target.name == step and after:
            raise OSError("injected interruption")
    monkeypatch.setattr(publish, "replace_file", interrupt)
    with pytest.raises(OSError, match="injected interruption"):
        process(pdf, out, converter, export_md=True, force_reconvert=True)
    assert seen == PUBLICATION_ORDER[:PUBLICATION_ORDER.index(step) + 1]
    current = publish.read_manifest(out / "a_publish.json")
    valid, _ = publish.verify_published(out, current)
    if step == "a_publish.json" and after:
        assert valid
        assert current["run_identity"] != old["run_identity"]
    elif valid:
        assert snapshot(out) == before  # every published byte belongs to the old coherent set
    main_replaced = PUBLICATION_ORDER.index(step) > 5 or (step == "a_prospectus.json" and after)
    if main_replaced and not (step == "a_publish.json" and after):
        assert not valid  # main binds even byte-identical raw/companion writes to this generation



def rebind_cache_for_verification(out, manifest, name, data):
    """Give tampering honest hashes, so identity checks (not hash mismatches) catch it."""
    (out / name).write_bytes(data)
    manifest["cache_files"][name] = hashlib.sha256(data).hexdigest()
    manifest["run_identity"]["cache_files"] = dict(manifest["cache_files"])
    main_path = out / "a_prospectus.json"
    main = json.loads(main_path.read_bytes())
    main["run_identity"] = manifest["run_identity"]
    main_bytes = json.dumps(main).encode()
    main_path.write_bytes(main_bytes)
    manifest["files"][main_path.name] = hashlib.sha256(main_bytes).hexdigest()


@pytest.mark.parametrize("field,value", [
    ("pdf_sha256", "f" * 64), ("conversion_identity", "f" * 64),
    ("conversion_settings", {}), ("raw_json_sha256", "f" * 64), ("identity_version", 0),
])
def test_matching_hashes_do_not_hide_metadata_identity_mismatch(tmp_path, pdf_factory, converter,
                                                               pipeline_state, process, field, value):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    manifest = publish.read_manifest(out / "a_publish.json")
    meta = json.loads((out / "a_docling.meta.json").read_bytes())
    meta[field] = value
    rebind_cache_for_verification(out, manifest, "a_docling.meta.json", json.dumps(meta).encode())
    assert publish.verify_published(out, manifest) == (
        False, "cache metadata does not match the main run identity")


@pytest.mark.parametrize("name", ["a_docling.json", "a_docling.meta.json"])
@pytest.mark.parametrize("data", [b"{", b"\xff", b"[]", b"null"])
def test_hash_matching_malformed_cache_fails_closed(tmp_path, pdf_factory, converter,
                                                  pipeline_state, process, name, data):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    manifest = publish.read_manifest(out / "a_publish.json")
    rebind_cache_for_verification(out, manifest, name, data)
    assert publish.verify_published(out, manifest)[0] is False


def test_other_valid_cache_generation_cannot_rebind_the_parsed_main(tmp_path, pdf_factory, converter,
                                                                 pipeline_state, process):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    manifest = publish.read_manifest(out / "a_publish.json")
    raw = json.dumps({"texts": [], "tables": [], "marker": "different generation"}).encode()
    meta = json.loads((out / "a_docling.meta.json").read_bytes())
    meta["raw_json_sha256"] = hashlib.sha256(raw).hexdigest()
    for name, data in [("a_docling.json", raw), ("a_docling.meta.json", json.dumps(meta).encode())]:
        (out / name).write_bytes(data)
        manifest["cache_files"][name] = hashlib.sha256(data).hexdigest()
    manifest["run_identity"]["cache_files"] = dict(manifest["cache_files"])
    assert publish.verify_published(out, manifest) == (
        False, "main run identity does not match the manifest")


@pytest.mark.parametrize("part", ["raw_json_bytes", "meta_bytes", "raw_json_sha256", "meta_sha256"])
def test_incomplete_loaded_snapshot_refuses_without_changing_published_files(tmp_path, monkeypatch,
                                                                           pdf_factory, converter,
                                                                           pipeline_state, process,
                                                                           snapshot, part):
    from dataclasses import replace
    from backend.bintanong_tools.prospectus_extractor import pipeline
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    before = snapshot(out)
    real = pipeline.load_document_result
    monkeypatch.setattr(pipeline, "load_document_result",
                        lambda *args, **kwargs: replace(real(*args, **kwargs), **{part: None}))
    with pytest.raises(ValueError, match="complete captured cache pair"):
        process(pdf, out, converter)
    assert snapshot(out) == before


def test_verification_hashes_and_parses_each_files_same_read(tmp_path, monkeypatch, pdf_factory,
                                                          converter, pipeline_state, process):
    from pathlib import Path
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    manifest = publish.read_manifest(out / "a_publish.json")
    reads = {}
    real = Path.read_bytes
    def read_then_replace(path):
        data = real(path)
        reads[path.name] = reads.get(path.name, 0) + 1
        if path.name in ("a_prospectus.json", "a_docling.json", "a_docling.meta.json"):
            path.write_bytes(b"null")
        return data
    monkeypatch.setattr(Path, "read_bytes", read_then_replace)
    assert publish.verify_published(out, manifest) == (True, "all files match")
    assert reads == {name: 1 for name in {*manifest["files"], *manifest["cache_files"]}}
    assert publish.verify_published(out, manifest)[0] is False


@pytest.mark.parametrize("cache_map", [{}, {"a_docling.json": "a" * 64},
    {"a_docling.json": "a" * 64, "b_docling.meta.json": "b" * 64},
    {"a_docling.json": "a" * 64, "a_docling.meta.json": "b" * 64, "extra": "c" * 64}])
def test_pdf_manifest_requires_its_complete_matching_cache_pair(tmp_path, pdf_factory, converter,
                                                              pipeline_state, process, cache_map):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    manifest = publish.read_manifest(out / "a_publish.json")
    manifest["cache_files"] = cache_map
    manifest["run_identity"]["cache_files"] = cache_map
    path = out / "a_publish.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert publish.read_manifest(path) is None
    assert publish.verify_published(out, manifest)[0] is False
