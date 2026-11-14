"""Pending prospectus binding at the ingestion seam; synthetic bytes only."""
import copy
import importlib.util

import pytest

from backend.bintanong_contracts.chunk_adapter import locator_key, make_chunk_id
from backend.bintanong_contracts.governance import SourceDocumentVersion
from backend.bintanong_contracts.source import Chunk, check_chunk_binding, check_span_binding
from backend.bintanong_tools.document_ingest.register import mint_pending_register

MODULE = "backend.bintanong_tools.document_ingest.prospectus"
SHA = "a" * 64
PAGE = {(SHA, 1): (612.0, 792.0)}
# Known hash of canonical ["Printed course", "Printed course"].
HASH = "cac9449ee6e482d28a7615974ee06152385c1d31c0fc71441c40e0d517e7deed0"


def binder():
    assert importlib.util.find_spec(MODULE) is not None, "prospectus ingestion feature is missing"
    return importlib.import_module(MODULE).bind_prospectus_chunks


def inputs():
    version = mint_pending_register([{"sha256": SHA, "filename": "synthetic.pdf",
                                     "acquisition_locator": "shelf:synthetic"}], synthetic=True)[0]
    spans = [{"pdf_sha256": SHA, "page": 1, "printed_page_label": None,
              "locator": {"kind": "text_item", "item_ids": ["text-1"]},
              "text": "Printed course", "bbox": [1., 2., 30., 40.], "bbox_origin": "TOPLEFT",
              "extraction": {"source_kind": "docling-json", "resolution_method": "deterministic",
                             "repair_id": None, "ocr_confidence": None}}]
    from backend.bintanong_contracts.source import compute_content_hash
    digest = compute_content_hash("Printed course", "Printed course")
    chunk = {"chunk_id": make_chunk_id(SHA, locator_key(spans), digest), "chunk_type": "course",
             "chunker_version": "palsu-chunker-v1", "content_review": "pending", "pdf_sha256": SHA,
             "source_anchored": True, "text": "Printed course", "source_text": "Printed course",
             "source_spans": spans, "pages": [1], "table_indexes": [], "cell_ids": [],
             "content_hash": digest, "token_count": 3, "token_count_method": "estimate-v1",
             "source": "synthetic.pdf"}
    hierarchical = copy.deepcopy(chunk)
    hierarchical["source_spans"][0]["locator"]["item_ids"] = ["text-2"]
    hierarchical["chunk_id"] = make_chunk_id(SHA, locator_key(hierarchical["source_spans"]), digest)
    hierarchical["chunk_type"] = "hierarchical_text"
    payload = {"run_identity": {"pdf_sha256": SHA},
               "rag": {"semantic_chunks": [chunk], "hierarchical_chunks": [hierarchical]}}
    return payload, version


def test_binds_both_groups_preserving_identity_text_order_and_pending_states():
    bind = binder()
    payload, version = inputs()
    before, version_before = copy.deepcopy(payload), version.model_dump(mode="json")
    result = bind(payload, version, page_sizes=PAGE)
    assert set(result) == {"version_id", "source_sha256", "chunks", "rejections"}
    assert (result["version_id"], result["source_sha256"], result["rejections"]) == (version.version_id, SHA, [])
    original = payload["rag"]["semantic_chunks"] + payload["rag"]["hierarchical_chunks"]
    assert len(result["chunks"]) == 2
    for raw, serialized in zip(original, result["chunks"], strict=True):
        chunk = Chunk.parse(serialized)
        assert (chunk.chunk_id, chunk.content_hash, chunk.source_text, chunk.text) == (
            raw["chunk_id"], raw["content_hash"], raw["source_text"], raw["text"])
        assert (chunk.version_id, chunk.document_id, chunk.edition_id) == (
            version.version_id, version.document_id, version.edition_id)
        assert (chunk.content_review, chunk.source_verification, chunk.scope) == ("pending", "pending", ())
        check_chunk_binding(chunk, version)
        for span in chunk.spans:
            check_span_binding(span, version)
            assert span.version_id == version.version_id
    assert payload == before and version.model_dump(mode="json") == version_before


@pytest.mark.parametrize("attack", ["missing_digest", "wrong_digest", "foreign_version", "nonnull_version",
    "foreign_document", "foreign_edition", "foreign_span_version", "foreign_span_digest", "duplicate",
    "privileged_chunk", "privileged_span", "bad_rag", "bad_group", "bad_chunk", "missing_id"])
def test_global_refusal_checks_claims_before_any_write(attack):
    bind = binder()
    payload, version = inputs()
    chunk = payload["rag"]["hierarchical_chunks"][0]
    if attack == "missing_digest":
        payload["run_identity"].clear()
    elif attack == "wrong_digest":
        payload["run_identity"]["pdf_sha256"] = "b" * 64
    elif attack in {"foreign_version", "nonnull_version"}:
        chunk["version_id"] = "ver-other" if attack == "foreign_version" else version.version_id
    elif attack == "foreign_document":
        chunk["document_id"] = "doc-other"
    elif attack == "foreign_edition":
        chunk["edition_id"] = "edition-other"
    elif attack == "foreign_span_version":
        chunk["source_spans"][0]["version_id"] = "ver-other"
    elif attack == "foreign_span_digest":
        chunk["source_spans"][0]["pdf_sha256"] = "b" * 64
    elif attack == "duplicate":
        payload["rag"]["hierarchical_chunks"] = copy.deepcopy(payload["rag"]["semantic_chunks"])
    elif attack == "privileged_chunk":
        chunk["extra"] = {"is_approved": True}
    elif attack == "privileged_span":
        chunk["source_spans"][0]["extraction"]["verified_by"] = "forged"
    elif attack == "bad_rag":
        payload["rag"] = []
    elif attack == "bad_group":
        payload["rag"]["semantic_chunks"] = {}
    elif attack == "bad_chunk":
        payload["rag"]["hierarchical_chunks"] = [None]
    elif attack == "missing_id":
        del chunk["chunk_id"]
    before = copy.deepcopy(payload)
    with pytest.raises(ValueError):
        bind(payload, version, page_sizes=PAGE)
    assert payload == before


@pytest.mark.parametrize("failure,reason", [("geometry", "bbox_missing_page_size"),
    ("hash", "content_hash_mismatch"), ("unsupported", "incomplete_source_span")])
def test_each_unsupported_chunk_has_original_identity_and_reason(failure, reason):
    bind = binder()
    payload, version = inputs()
    chunk = payload["rag"]["hierarchical_chunks"][0]
    sizes = PAGE
    if failure == "geometry":
        sizes = {}
    elif failure == "hash":
        chunk["source_text"] = "altered raw text"
    else:
        chunk["source_text"] = None
        chunk["source_spans"][0]["text"] = None
    before = copy.deepcopy(payload)
    result = bind(payload, version, page_sizes=sizes)
    rejected = result["rejections"]
    assert any(r == {"chunk_id": chunk["chunk_id"], "reason": reason} for r in rejected)
    assert len(result["chunks"]) + len(rejected) == 2
    assert payload == before


def test_pending_loader_refuses_promoted_version_without_mutation():
    bind = binder()
    payload, version = inputs()
    data = version.model_dump()
    data["issuer"].update(state="not_stated", evidence_ref="ev-absence")
    data["evidence"] = ({"evidence_id": "ev-absence", "kind": "reviewer_absence_check",
                         "recorded_by": "reviewer", "recorded_at": "2026-01-01T00:00:00+00:00"},)
    promoted = SourceDocumentVersion.model_validate(data)
    before = promoted.model_dump(mode="json")
    with pytest.raises(ValueError):
        bind(payload, promoted, page_sizes=PAGE)
    assert promoted.model_dump(mode="json") == before


def synthetic_prospectus():
    """Small curriculum with real cell ownership and an unresolved prerequisite."""
    rows = [["Course Code", "Course Title", "Units", "Prerequisites"],
            ["FIRST YEAR", "", "", ""], ["FIRST SEMESTER", "", "", ""],
            ["CS101", "Introduction to Computing", "3", "None"],
            ["CS102", "Computer Programming", "3", "XX999"]]
    cells = []
    for row, values in enumerate(rows):
        for col, text in enumerate(values):
            if not text:
                continue
            cells.append({"text": text, "start_row_offset_idx": row, "end_row_offset_idx": row + 1,
                "start_col_offset_idx": col, "end_col_offset_idx": 4 if row in (1, 2) else col + 1,
                "bbox": {"l": 10 + col * 120, "t": 200 + row * 20,
                         "r": 120 + col * 120, "b": 215 + row * 20, "coord_origin": "TOPLEFT"}})
    return {"texts": [{"text": "Bachelor of Science in Computer Science", "label": "title",
                "prov": [{"page_no": 1, "bbox": {"l": 10, "t": 10, "r": 500, "b": 30,
                                                   "coord_origin": "TOPLEFT"}}]}],
            "tables": [{"prov": [{"page_no": 1}], "data": {
                "num_rows": 5, "num_cols": 4, "table_cells": cells}}],
            "pages": {"1": {"size": {"width": 612, "height": 792}}}}


def synthetic_converter(monkeypatch, snapshot, raw=None, *, status="success", errors=()):
    from types import SimpleNamespace
    from backend.bintanong_tools.prospectus_extractor import loader
    from conftest import FakeDoc
    raw = synthetic_prospectus() if raw is None else raw
    monkeypatch.setattr(loader, "ensure_docling_env", lambda: None)
    monkeypatch.setattr(loader, "load_docling", lambda: {"DoclingDocument": FakeDoc})
    calls = []
    def convert(stream):
        assert stream.stream.read() == snapshot.data
        calls.append(stream.name)
        return SimpleNamespace(status=status, errors=list(errors), document=FakeDoc(raw))
    return SimpleNamespace(convert=convert, calls=calls, conversion_settings={
        "backend": "synthetic", "profile": "synthetic-curriculum-v1", "versions": {"fixture": "1"}})


@pytest.fixture
def prospectus_input(tmp_path):
    import pypdfium2 as pdfium
    from backend.bintanong_tools.document_ingest.register import pending_version
    from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
    root = tmp_path / "originals"
    root.mkdir()
    source = root / "synthetic.pdf"
    with pdfium.PdfDocument.new() as pdf:
        page = pdf.new_page(612, 792)
        page.close()
        pdf.save(source)
    snap = InputSnapshot(source)
    return root, snap, pending_version(snap, "shelf:synthetic", synthetic=True)


def runner():
    mod = importlib.import_module(MODULE)
    assert hasattr(mod, "run_prospectus_ingestion"), "prospectus publication is missing"
    return mod.run_prospectus_ingestion


def test_real_curriculum_parser_audit_and_checked_pending_handoff(prospectus_input, tmp_path, monkeypatch):
    import json
    root, snap, version = prospectus_input
    out = tmp_path / "bundle"
    report = runner()(snap, [version], input_root=root, out=out,
                      converter=synthetic_converter(monkeypatch, snap))
    from backend.bintanong_tools.document_ingest.bundle import load_candidate_bundle
    checked = load_candidate_bundle(out)
    assert checked["report"] == report and checked["review_eligible"] is False
    assert checked["source_register"] == [version] and checked["chunks"]
    payload = checked["domain_payload"]
    assert [c["course_code"] for c in payload["courses"]] == ["CS101", "CS102"]
    assert payload["audit"]["status"] != "error" and payload["audit"]["unresolved_prerequisites"]
    assert payload["source_verification"] == payload["content_review"] == "pending"
    assert payload["authority"]["eligibility_executable"] is False
    assert payload["quality_report"]["production_artifacts_emitted"] is False
    assert "prolog" not in payload and not list(out.rglob("*.pl"))
    assert "rule_complete(C)" not in json.dumps(payload)
    assert checked["conversion"]["metadata"]["conversion_settings"]["backend"] == "synthetic"
    assert checked["conversion"]["raw_docling"] == synthetic_prospectus()
    assert report["counts"]["candidate_chunks"] == report["counts"]["chunks"] + report["counts"]["binding_rejections"]
    assert snap.path.read_bytes() == snap.data and list(root.iterdir()) == [snap.path]


@pytest.mark.parametrize("status,errors", [("partial_success", ()), ("failure", ()), ("success", ("bad_alloc",))])
def test_non_success_refuses_before_raw_export_or_any_writer(prospectus_input, tmp_path, monkeypatch, status, errors):
    from backend.bintanong_tools.prospectus_extractor import loader
    root, snap, version = prospectus_input
    out = tmp_path / "bundle"
    converter = synthetic_converter(monkeypatch, snap, status=status, errors=errors)
    writes = []
    monkeypatch.setattr(loader, "_write_bytes_atomic", lambda *args: writes.append(args))
    with pytest.raises((ValueError, RuntimeError), match="conversion"):
        runner()(snap, [version], input_root=root, out=out, converter=converter)
    assert converter.calls == ["synthetic.pdf"] and writes == []
    assert not (out / "manifest.json").exists() and snap.path.read_bytes() == snap.data


@pytest.mark.parametrize("damage", ["register", "private", "source", "json", "inside", "stale", "settings"])
def test_preflight_refuses_before_converter_and_writer(prospectus_input, tmp_path, monkeypatch, damage):
    from backend.bintanong_tools.prospectus_extractor import loader
    from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
    root, snap, version = prospectus_input
    out, records = tmp_path / "bundle", [version]
    converter = synthetic_converter(monkeypatch, snap)
    if damage in {"private", "register"}:
        record = version.model_dump(mode="json")
        record["namespace" if damage == "private" else "byte_sha256"] = "private" if damage == "private" else "b" * 64
        records = [record]
    elif damage == "source":
        snap.path.write_bytes(b"changed")
    elif damage == "json":
        source = root / "raw.json"
        source.write_text("{}")
        snap = InputSnapshot(source)
    elif damage == "inside":
        out = root / "bundle"
    elif damage == "stale":
        out.mkdir()
        (out / "keep").write_bytes(b"keep")
    else:
        del converter.conversion_settings
    before = {p.name: p.read_bytes() for p in root.iterdir()}
    writes = []
    monkeypatch.setattr(loader, "_write_bytes_atomic", lambda *args: writes.append(args))
    with pytest.raises(ValueError):
        runner()(snap, records, input_root=root, out=out, converter=converter)
    assert writes == [] and converter.calls == []
    assert before == {p.name: p.read_bytes() for p in root.iterdir()}
    if damage == "stale":
        assert (out / "keep").read_bytes() == b"keep"


def test_failed_audit_is_complete_diagnostic_candidate_with_no_ready_chunks(prospectus_input, tmp_path, monkeypatch):
    root, snap, version = prospectus_input
    raw = synthetic_prospectus()
    raw["tables"] = []
    out = tmp_path / "blocked"
    report = runner()(snap, [version], input_root=root, out=out,
                      converter=synthetic_converter(monkeypatch, snap, raw))
    from backend.bintanong_tools.document_ingest.bundle import load_candidate_bundle
    checked = load_candidate_bundle(out)
    assert report["audit_status"] == "error" and report["extraction_blocked"] is True
    assert checked["chunks"] == [] and checked["review_eligible"] is False
    assert "curriculum_audit_failed" in report["review_needs"]


@pytest.mark.parametrize("when", ["convert", "last_write"])
def test_source_changes_during_run_leave_no_root_completion(prospectus_input, tmp_path, monkeypatch, when):
    from backend.bintanong_tools.prospectus_extractor import loader
    root, snap, version = prospectus_input
    out = tmp_path / "bundle"
    converter = synthetic_converter(monkeypatch, snap)
    if when == "convert":
        convert = converter.convert
        def mutate(stream):
            result = convert(stream)
            snap.path.write_bytes(b"changed in convert")
            return result
        converter.convert = mutate
    else:
        write = loader._write_bytes_atomic
        def mutate(path, data):
            write(path, data)
            if path.name == "ingestion_report.json":
                snap.path.write_bytes(b"changed after report")
        monkeypatch.setattr(loader, "_write_bytes_atomic", mutate)
    with pytest.raises(ValueError, match="changed"):
        runner()(snap, [version], input_root=root, out=out, converter=converter)
    assert not (out / "manifest.json").exists()


def test_settings_drift_during_conversion_refuses_before_any_writer(prospectus_input, tmp_path, monkeypatch):
    from backend.bintanong_tools.prospectus_extractor import loader
    root, snap, version = prospectus_input
    converter = synthetic_converter(monkeypatch, snap)
    convert = converter.convert
    def drift(stream):
        result = convert(stream)
        converter.conversion_settings["backend"] = "changed"
        return result
    converter.convert = drift
    writes = []
    monkeypatch.setattr(loader, "_write_bytes_atomic", lambda *args: writes.append(args))
    with pytest.raises(ValueError, match="settings"):
        runner()(snap, [version], input_root=root, out=tmp_path / "bundle", converter=converter)
    assert writes == [] and converter.calls == ["synthetic.pdf"]


@pytest.mark.parametrize("damage", ["backend", "profile", "version", "actual_backend", "actual_options"])
def test_unverifiable_converter_settings_refused_before_convert(prospectus_input, tmp_path, monkeypatch, damage):
    from types import SimpleNamespace
    from docling.datamodel.base_models import InputFormat
    root, snap, version = prospectus_input
    converter = synthetic_converter(monkeypatch, snap)
    if damage in {"backend", "profile"}:
        converter.conversion_settings[damage] = ""
    elif damage == "version":
        converter.conversion_settings["versions"] = {"fixture": None}
    else:
        backend = type("DoclingParseV4DocumentBackend", (), {})
        converter.format_to_options = {InputFormat.PDF: SimpleNamespace(backend=backend, pipeline_options=None)}
        if damage == "actual_options":
            converter.conversion_settings["backend"] = "docling_parse"
    with pytest.raises(ValueError, match="settings|backend|versions"):
        runner()(snap, [version], input_root=root, out=tmp_path / "bundle", converter=converter)
    assert converter.calls == []


def test_raw_geometry_cannot_override_captured_pdf_size(prospectus_input, tmp_path, monkeypatch):
    root, snap, version = prospectus_input
    raw = synthetic_prospectus()
    raw["pages"]["1"]["size"]["width"] = 900
    out = tmp_path / "bundle"
    with pytest.raises(ValueError, match="geometry|size"):
        runner()(snap, [version], input_root=root, out=out, converter=synthetic_converter(monkeypatch, snap, raw))
    assert not (out / "manifest.json").exists()


def test_injected_docling_ocr_languages_must_match_actual_options(prospectus_input, tmp_path, monkeypatch):
    from types import SimpleNamespace
    from docling.datamodel.base_models import InputFormat
    from backend.bintanong_tools.prospectus_extractor.identity import installed_versions
    root, snap, version = prospectus_input
    converter = synthetic_converter(monkeypatch, snap)
    converter.conversion_settings.update(backend="docling_parse", do_ocr=True, ocr_languages=["eng"],
        force_backend_text=True, do_table_structure=True, cell_matching=True, table_mode="accurate",
        versions=installed_versions())
    pipeline = SimpleNamespace(do_ocr=True, force_backend_text=True, do_table_structure=True,
        table_structure_options=SimpleNamespace(do_cell_matching=True, mode=SimpleNamespace(value="accurate")),
        ocr_options=SimpleNamespace(lang=["fil"]))
    converter.format_to_options = {InputFormat.PDF: SimpleNamespace(
        backend=type("DoclingParseV4DocumentBackend", (), {}), pipeline_options=pipeline)}
    with pytest.raises(ValueError, match="languages"):
        runner()(snap, [version], input_root=root, out=tmp_path / "bundle", converter=converter)
    assert converter.calls == []
    pipeline.ocr_options.lang = ["eng"]
    report = runner()(snap, [version], input_root=root, out=tmp_path / "bundle", converter=converter)
    assert report["conversion_settings"]["ocr_languages"] == ["eng"]
    assert converter.calls == ["synthetic.pdf"]


@pytest.mark.parametrize("package", ["docling", "docling-core", "docling-parse"])
def test_injected_docling_versions_must_match_installed_packages(prospectus_input, tmp_path, monkeypatch, package):
    from types import SimpleNamespace
    from docling.datamodel.base_models import InputFormat
    from backend.bintanong_tools.prospectus_extractor.identity import conversion_settings
    root, snap, version = prospectus_input
    converter = synthetic_converter(monkeypatch, snap)
    converter.conversion_settings = conversion_settings()
    converter.conversion_settings["versions"][package] = "forged"
    pipeline = SimpleNamespace(do_ocr=False, force_backend_text=True, do_table_structure=True,
        table_structure_options=SimpleNamespace(do_cell_matching=True, mode=SimpleNamespace(value="accurate")))
    converter.format_to_options = {InputFormat.PDF: SimpleNamespace(
        backend=type("DoclingParseV4DocumentBackend", (), {}), pipeline_options=pipeline)}
    with pytest.raises(ValueError, match="versions"):
        runner()(snap, [version], input_root=root, out=tmp_path / "bundle", converter=converter)
    assert converter.calls == []


@pytest.mark.parametrize("drift", ["before", "during", None])
def test_default_cached_converter_settings_checked_before_and_after_conversion(
        prospectus_input, tmp_path, monkeypatch, drift):
    from docling.datamodel.base_models import InputFormat
    from backend.bintanong_tools.prospectus_extractor import docling_env, loader
    from backend.bintanong_tools.prospectus_extractor.identity import conversion_settings
    from backend.bintanong_tools.document_ingest.bundle import load_candidate_bundle
    monkeypatch.setattr(docling_env, "_SHARED_CONVERTERS", {})
    monkeypatch.setattr(docling_env, "check_cuda_environment", lambda: {
        "cuda_available": False, "status_message": "synthetic CPU check"})
    declared = conversion_settings()
    active = docling_env.get_shared_converter(device="auto", backend=declared["backend"], settings=declared)
    options = active.format_to_options[InputFormat.PDF].pipeline_options
    assert options.do_ocr is False
    root, snap, version = prospectus_input
    stub = synthetic_converter(monkeypatch, snap)
    def convert(stream):
        result = stub.convert(stream)
        if drift == "during":
            options.do_ocr = True
        return result
    monkeypatch.setattr(active, "convert", convert)
    if drift == "before":
        options.do_ocr = True
    out = tmp_path / "default-bundle"
    if drift is not None:
        out.mkdir()
        writes = []
        original_write = loader._write_bytes_atomic
        def count_write(path, data):
            writes.append(path)
            return original_write(path, data)
        monkeypatch.setattr(loader, "_write_bytes_atomic", count_write)
        with pytest.raises(ValueError, match="settings"):
            runner()(snap, [version], input_root=root, out=out)
        assert writes == [] and list(out.iterdir()) == []
        assert stub.calls == ([] if drift == "before" else ["synthetic.pdf"])
    else:
        report = runner()(snap, [version], input_root=root, out=out)
        assert report["conversion_settings"] == declared and stub.calls == ["synthetic.pdf"]
        assert load_candidate_bundle(out)["report"] == report
    assert snap.path.read_bytes() == snap.data and list(root.iterdir()) == [snap.path]
