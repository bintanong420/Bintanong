"""Synthetic procedure/form candidates and review-only native PPTX evidence."""
import copy
import importlib
import json
import zipfile
from dataclasses import FrozenInstanceError, replace
from types import SimpleNamespace

import pytest

from backend.bintanong_tools.document_ingest import register
from backend.bintanong_tools.prospectus_extractor import loader, docling_env
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot, bytes_sha256


def module():
    try:
        return importlib.import_module("backend.bintanong_tools.document_ingest.procedure_text")
    except ModuleNotFoundError:
        pytest.fail("Task4 procedure candidate reader is not implemented")


def item(text, slide=1, label="text", **extra):
    return {"text": text, "label": label, "prov": [{"page_no": slide,
            "bbox": {"l": 20, "t": 150, "r": 450, "b": 180, "coord_origin": "TOPLEFT"}, **extra}]}


def raw_document(texts, pages=2):
    return {"texts": texts, "pages": {str(i): {"size": {"width": 600, "height": 800}}
                                      for i in range(1, pages + 1)}, "tables": []}


@pytest.fixture
def bound(tmp_path):
    root = tmp_path / "originals"
    root.mkdir()
    def capture(name="procedure.pdf", data=b"%PDF-synthetic"):
        path = root / name
        path.write_bytes(data)
        snap = InputSnapshot(path)
        version = register.pending_version(snap, "shelf:synthetic-" + name, synthetic=True)
        return snap, version
    return root, capture


def test_pdf_steps_fields_raw_fidelity_and_accounting(bound):
    _, capture = bound
    _, version = capture()
    raw = raw_document([item("2. Do not pay 25–50 pesos.²"), item("1. Submit form."),
        item("Office: Registrar"), item("Requirements: valid ID"), item("Fees: ₱25.00"),
        item("Processing time: 3 days"), item(""), item("unlabelled 50 pesos")], pages=3)
    raw["body"] = {"children": [{"cref": f"#/texts/{i}"} for i in [1, 0, 2, 3, 4, 5, 6, 7]]}
    before = copy.deepcopy(raw)
    result = module().read_procedure_items(raw, version, printed_page_labels={1: "iv"})
    assert raw == before
    assert [f.raw_text for f in result.fields if f.kind == "step"] == ["1. Submit form.", "2. Do not pay 25–50 pesos.²"]
    assert [(f.kind, f.raw_text) for f in result.fields if f.kind != "step"] == [
        ("office", "Office: Registrar"), ("requirements", "Requirements: valid ID"),
        ("fees", "Fees: ₱25.00"), ("processing_time", "Processing time: 3 days")]
    assert result.pdf.units[1].spans[0].text == "2. Do not pay 25–50 pesos.²"
    assert result.pdf.units[1].spans[0].printed_page_label == "iv"
    assert result.pdf.page_omissions == ((2, "scanned_no_text_layer"), (3, "scanned_no_text_layer"))
    result.check_invariants()
    with pytest.raises(ValueError, match="item"):
        replace(result, pdf=replace(result.pdf, units=())).check_invariants()
    with pytest.raises(FrozenInstanceError):
        result.classification = "rule"


def test_explicit_form_and_proposal_classification_never_filename_authority(bound):
    _, capture = bound
    _, version = capture("approved-charter-BOR.pdf")
    raw = raw_document([item("Name: __________")])
    assert module().read_procedure_items(raw, version).classification == "procedure_candidate"
    for classification in ("form", "curriculum_proposal_candidate", "charter_candidate"):
        result = module().read_procedure_items(raw, version, classification=classification)
        assert result.classification == classification
        assert result.version.document_category == "source_document"
        assert result.version.approval_id is None
        assert result.version.approval_state.state == "not_requested"
        assert "rule" not in result.as_dict()
    with pytest.raises(ValueError, match="classification"):
        module().read_procedure_items(raw, version, classification="approved_curriculum")


def test_no_printed_fee_means_no_fee_candidate(bound):
    _, capture = bound
    _, version = capture("fees-500.pdf")
    result = module().read_procedure_items(raw_document([item("Submit 2 copies")]), version)
    assert result.fields == ()


@pytest.mark.parametrize("source_format", ["pdf", "pptx"])
def test_explicit_numbered_markers_kept_without_rewriting_text(bound, source_format):
    _, capture = bound
    _, version = capture("source." + source_format)
    raw = raw_document([item("Do not pay.", label="list_item"), item("Submit ID.", label="list_item")])
    raw["texts"][0].update(enumerated=True, marker="2.")
    raw["texts"][1].update(enumerated=True, marker="1.")
    raw["body"] = {"children": [{"cref": "#/texts/1"}, {"cref": "#/texts/0"}]}
    result = module().read_procedure_items(raw, version, source_format=source_format)
    assert [(f.kind, f.raw_text, f.printed_marker) for f in result.fields] == [
        ("step", "Submit ID.", "1."), ("step", "Do not pay.", "2.")]


@pytest.mark.parametrize("classification", [None, [], 1])
def test_malformed_classification_refused(bound, classification):
    _, capture = bound
    _, version = capture()
    with pytest.raises(ValueError, match="classification"):
        module().read_procedure_items(raw_document([]), version, classification=classification)


def test_negative_group_reference_refused(bound):
    _, capture = bound
    _, version = capture()
    raw = raw_document([item("step")])
    raw["groups"] = [{"children": [{"cref": "#/texts/0"}]}]
    raw["body"] = {"children": [{"cref": "#/groups/-1"}]}
    with pytest.raises(ValueError, match="group"):
        module().read_procedure_items(raw, version)


@pytest.mark.parametrize("source_format", ["pdf", "pptx"])
def test_native_nested_refs_and_original_structure_retained(bound, source_format):
    _, capture = bound
    _, version = capture("source." + source_format)
    raw = raw_document([item("2. Second"), item("1. First")])
    raw["groups"] = [{"children": [{"$ref": "#/groups/1"}]},
                     {"children": [{"$ref": "#/texts/1"}, {"$ref": "#/texts/0"}]}]
    raw["body"] = {"children": [{"$ref": "#/groups/0"}]}
    before = copy.deepcopy(raw)
    result = module().read_procedure_items(raw, version, source_format=source_format)
    assert result.reading_order == ("#/texts/1", "#/texts/0")
    assert json.loads(result.raw_reading_order_json) == {"body": raw["body"], "groups": raw["groups"]}
    assert raw == before


@pytest.mark.parametrize("source_format", ["pdf", "pptx"])
def test_text_children_follow_parent_in_native_reading_order(bound, source_format):
    _, capture = bound
    _, version = capture("source." + source_format)
    raw = raw_document([item("Registration", label="section_header"), item("1. Submit ID.")])
    raw["texts"][0]["children"] = [{"cref": "#/texts/1"}]
    raw["body"] = {"children": [{"cref": "#/texts/0"}]}
    before = copy.deepcopy(raw)
    result = module().read_procedure_items(raw, version, source_format=source_format)
    assert result.reading_order == ("#/texts/0", "#/texts/1")
    assert [(f.kind, f.raw_text) for f in result.fields] == [("step", "1. Submit ID.")]
    assert raw == before


@pytest.mark.parametrize("child_ref", ["#/texts/0", "#/texts/1"])
def test_text_descendant_cycles_and_duplicate_references_refused(bound, child_ref):
    _, capture = bound
    _, version = capture()
    raw = raw_document([item("Parent"), item("Child")])
    raw["texts"][0]["children"] = [{"cref": child_ref}]
    raw["body"] = {"children": [{"cref": "#/texts/0"}, {"cref": "#/texts/1"}]}
    with pytest.raises(ValueError, match="duplicate"):
        module().read_procedure_items(raw, version)


def test_table_raw_cells_headers_provenance_and_geometry_retained(bound):
    _, capture = bound
    _, version = capture()
    raw = raw_document([item("Procedure")])
    raw["tables"] = [{"label": "table", "prov": [item("", 1)["prov"][0], item("", 2)["prov"][0]],
        "data": {"num_rows": 2, "num_cols": 1, "table_cells": [
            {"text": "Fees–²", "column_header": True, "start_row_offset_idx": 0,
             "end_row_offset_idx": 1, "start_col_offset_idx": 0, "end_col_offset_idx": 1},
            {"text": "No fee", "column_header": False, "prov": [item("", 2)["prov"][0]],
             "start_row_offset_idx": 1, "end_row_offset_idx": 2,
             "start_col_offset_idx": 0, "end_col_offset_idx": 1}]}}]
    raw["body"] = {"children": [{"cref": "#/tables/0"}, {"cref": "#/texts/0"}]}
    result = module().read_procedure_items(raw, version)
    table = result.tables[0]
    assert json.loads(table.raw_table_json) == raw["tables"][0]
    assert json.loads(table.raw_geometry_json) == raw["pages"]
    assert table.rejection_reason == "unresolved_table_span_coverage"
    assert table.spans == () and not table.anchored
    assert result.reading_order == ("#/tables/0", "#/texts/0")
    with pytest.raises(ValueError, match="table"):
        replace(result, tables=()).check_invariants()


def test_pptx_slides_shapes_reading_order_never_pdf_pages(bound):
    _, capture = bound
    _, version = capture("deck.pptx", b"PK-synthetic")
    raw = raw_document([item("First–²", 2, shape_id=7), item("Second", 1, shape_id=4), item("", 1)])
    raw["body"] = {"children": [{"cref": "#/texts/1"}, {"cref": "#/texts/0"}, {"cref": "#/texts/2"}]}
    result = module().read_procedure_items(raw, version, source_format="pptx")
    assert result.pdf is None
    assert [(u.item_id, u.slide_index, u.shape_id) for u in result.pptx_units] == [
        ("text-1", 1, 4), ("text-0", 2, 7), ("text-2", 1, None)]
    assert all(u.rejection_reason == "pending_locator_contract" and not u.anchored and not u.spans
               for u in result.pptx_units)
    assert "page" not in result.as_dict()["pptx_units"][0]
    assert result.pptx_units[1].source_text == "First–²"
    assert json.loads(result.pptx_units[1].raw_provenance_json) == raw["texts"][0]["prov"]
    assert result.pptx_units[2].provenance_gaps == ("shape_id_not_exported",)
    with pytest.raises(ValueError, match="item"):
        replace(result, pptx_units=()).check_invariants()


def test_unsupported_slide_provenance_null_and_explicit_gap(bound):
    _, capture = bound
    _, version = capture("deck.pptx", b"PK-synthetic")
    raw = raw_document([{"text": "No provenance", "label": "text", "prov": []}], pages=0)
    unit = module().read_procedure_items(raw, version, source_format="pptx").pptx_units[0]
    assert unit.slide_index is None and unit.shape_id is None
    assert unit.provenance_gaps == ("slide_index_not_exported", "shape_id_not_exported")


@pytest.mark.parametrize("damage", ["text", "page", "private", "table", "order"])
def test_malformed_and_namespace_refused(bound, damage):
    _, capture = bound
    _, version = capture()
    raw = raw_document([item("step")])
    if damage == "text":
        raw["texts"][0]["text"] = 3
    elif damage == "page":
        raw["texts"][0]["prov"][0]["page_no"] = True
    elif damage == "private":
        raw["texts"][0]["text"] = "sess-123 fact-987"
    elif damage == "table":
        raw["tables"] = [None]
    else:
        raw["body"] = {"children": [{"cref": "#/texts/0"}, {"cref": "#/tables/9"}]}
    with pytest.raises(ValueError):
        module().read_procedure_items(raw, version)


def test_duplicate_pdf_locators_and_distinct_pptx_versions(bound):
    _, capture = bound
    a, _ = capture("a.pdf")
    b, _ = capture("b.pdf")
    records = register.mint_pending_register([
        {"filename": s.path.name, "sha256": s.sha256, "acquisition_locator": loc}
        for s, loc in [(a, "shelf:a"), (b, "shelf:b")]], synthetic=True)
    result = module().read_procedure_items(raw_document([item("step")]), records[0])
    assert len(records) == 1 and result.version.acquisition_locators == ("shelf:a", "shelf:b")
    _, x = capture("one.pptx", b"PK-one")
    _, y = capture("two.pptx", b"PK-two")
    assert module().read_procedure_items(raw_document([]), x, source_format="pptx").version.version_id != \
           module().read_procedure_items(raw_document([]), y, source_format="pptx").version.version_id


def fake_converter(raw, snap, mutate=False, errors=()):
    def convert(stream):
        assert stream.stream.read() == snap.data
        if mutate:
            snap.path.write_bytes(b"changed")
        return SimpleNamespace(document=SimpleNamespace(export_to_dict=lambda: raw,
               export_to_markdown=lambda: "unused"), errors=errors)
    return SimpleNamespace(convert=convert)


@pytest.mark.parametrize("suffix", ["pdf", "pptx"])
def test_external_publication_byte_snapshot_and_manifest(bound, tmp_path, monkeypatch, suffix):
    root, capture = bound
    snap, version = capture("source." + suffix)
    raw = raw_document([item("1. Do not pay 3–4².")])
    doc = SimpleNamespace(export_to_dict=lambda: raw, export_to_markdown=lambda: "unused")
    if suffix == "pdf":
        monkeypatch.setattr(loader, "load_docling", lambda: {
            "DoclingDocument": SimpleNamespace(model_validate=lambda data: doc)})
    monkeypatch.setattr(docling_env.subprocess, "call", lambda *a, **k: pytest.fail("relaunch reached"))
    out = tmp_path / "out"
    result = module().extract_procedure(snap, [version], input_root=root, out=out,
                                       converter=fake_converter(raw, snap))
    assert sorted(p.name for p in root.iterdir()) == ["source." + suffix]
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["complete"] and manifest["source_unchanged"]
    assert manifest["source_sha256"] == snap.sha256
    for name, digest in manifest["files"].items():
        assert bytes_sha256((out / name).read_bytes()) == digest
    assert json.loads((out / "procedure_candidates.json").read_text(encoding="utf-8")) == result.as_dict()


@pytest.mark.parametrize("suffix", ["pdf", "pptx"])
def test_source_mutation_prevents_completion(bound, tmp_path, monkeypatch, suffix):
    root, capture = bound
    snap, version = capture("source." + suffix)
    raw = raw_document([item("step")])
    monkeypatch.setattr(loader, "load_docling", lambda: {"DoclingDocument":
                        SimpleNamespace(model_validate=lambda data: SimpleNamespace(export_to_markdown=lambda: ""))})
    out = tmp_path / "out"
    with pytest.raises(ValueError, match="changed"):
        module().extract_procedure(snap, [version], input_root=root, out=out,
                                  converter=fake_converter(raw, snap, mutate=True))
    assert not (out / "manifest.json").exists()
    assert not (out / "procedure_candidates.json").exists()
    assert not (out / "raw_docling.json").exists()
    assert not (out / "raw_docling.meta.json").exists()


@pytest.mark.parametrize("suffix", ["pdf", "pptx"])
def test_reader_refusal_retains_byte_bound_raw_conversion(bound, tmp_path, monkeypatch, suffix):
    root, capture = bound
    snap, version = capture("source." + suffix)
    raw = raw_document([item("Parent"), item("Unreferenced child")])
    raw["body"] = {"children": [{"cref": "#/texts/0"}]}
    monkeypatch.setattr(loader, "load_docling", lambda: {"DoclingDocument":
                        SimpleNamespace(model_validate=lambda data: SimpleNamespace(export_to_markdown=lambda: ""))})
    out = tmp_path / "refused"
    with pytest.raises(ValueError, match="reading order"):
        module().extract_procedure(snap, [version], input_root=root, out=out,
                                  converter=fake_converter(raw, snap))
    assert json.loads((out / "raw_docling.json").read_text(encoding="utf-8")) == raw
    metadata = json.loads((out / "raw_docling.meta.json").read_text(encoding="utf-8"))
    source_key = "pdf_sha256" if suffix == "pdf" else "source_sha256"
    assert metadata[source_key] == snap.sha256
    assert metadata["raw_json_sha256"] == bytes_sha256((out / "raw_docling.json").read_bytes())
    assert snap.path.read_bytes() == snap.data
    assert not (out / "manifest.json").exists()
    assert not (out / "procedure_candidates.json").exists()


@pytest.mark.parametrize("damage", ["digest", "namespace", "promoted", "input_out", "git_out", "nonempty", "root"])
def test_preflight_refused_before_conversion(bound, tmp_path, damage):
    root, capture = bound
    snap, version = capture("deck.pptx", b"PK-synthetic")
    record = version.model_dump(mode="json")
    out = tmp_path / "out"
    if damage == "digest":
        record["byte_sha256"] = "bad"
    elif damage == "namespace":
        record["namespace"] = "private_session"
    elif damage == "promoted":
        record["approval_id"] = "approval-invalid"
    elif damage == "input_out":
        out = root / "out"
    elif damage == "git_out":
        out.parent.joinpath(".git").write_text("gitdir: x")
    elif damage == "nonempty":
        out.mkdir()
        (out / "keep").write_text("keep")
    else:
        root = tmp_path / "elsewhere"
    with pytest.raises(ValueError):
        module().extract_procedure(snap, [record], input_root=root, out=out,
            converter=SimpleNamespace(convert=lambda *a: pytest.fail("conversion reached")))
    assert not (out / "manifest.json").exists()


@pytest.mark.parametrize("suffix", ["pdf", "pptx"])
def test_missing_installed_docling_never_relaunches(bound, tmp_path, monkeypatch, suffix):
    root, capture = bound
    snap, version = capture("source." + suffix)
    mod = module()
    monkeypatch.setattr(loader, "load_docling", lambda: (_ for _ in ()).throw(RuntimeError("unavailable")))
    monkeypatch.setattr(docling_env.subprocess, "call", lambda *a, **k: pytest.fail("relaunch reached"))
    with pytest.raises(RuntimeError, match="unavailable"):
        mod.extract_procedure(snap, [version], input_root=root, out=tmp_path / "out")


def test_pptx_conversion_errors_no_completion(bound, tmp_path):
    root, capture = bound
    snap, version = capture("deck.pptx", b"PK-synthetic")
    out = tmp_path / "out"
    with pytest.raises(RuntimeError, match="conversion errors"):
        module().extract_procedure(snap, [version], input_root=root, out=out,
            converter=fake_converter(raw_document([item("partial")]), snap,
                                     errors=[SimpleNamespace(error_message="broken slide")]))
    assert not (out / "manifest.json").exists()


def test_installed_native_pptx_smoke_offline(tmp_path, monkeypatch):
    """Minimal OOXML fixture; installed native backend must preserve slide provenance."""
    root = tmp_path / "originals"
    root.mkdir()
    path = root / "native.pptx"
    ns_p = "http://schemas.openxmlformats.org/presentationml/2006/main"
    ns_a = "http://schemas.openxmlformats.org/drawingml/2006/main"
    ns_r = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ns_rel = "http://schemas.openxmlformats.org/package/2006/relationships"
    parts = {
        "[Content_Types].xml": '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
            '<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
            '<Override PartName="/ppt/slides/slide2.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/></Types>',
        "_rels/.rels": f'<Relationships xmlns="{ns_rel}"><Relationship Id="rId1" Type="{ns_r}/officeDocument" Target="ppt/presentation.xml"/></Relationships>',
        "ppt/presentation.xml": f'<p:presentation xmlns:p="{ns_p}" xmlns:r="{ns_r}"><p:sldIdLst>'
            '<p:sldId id="256" r:id="rId1"/><p:sldId id="257" r:id="rId2"/></p:sldIdLst>'
            '<p:sldSz cx="9144000" cy="6858000"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>',
        "ppt/_rels/presentation.xml.rels": f'<Relationships xmlns="{ns_rel}">'
            f'<Relationship Id="rId1" Type="{ns_r}/slide" Target="slides/slide1.xml"/>'
            f'<Relationship Id="rId2" Type="{ns_r}/slide" Target="slides/slide2.xml"/></Relationships>'}
    for slide, text in [(1, "1. Do not pay 3–4²."), (2, "Fees: no fee")]:
        parts[f"ppt/slides/slide{slide}.xml"] = f'<p:sld xmlns:p="{ns_p}" xmlns:a="{ns_a}"><p:cSld><p:spTree>' \
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>' \
            '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Text"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>' \
            '<p:spPr><a:xfrm><a:off x="1000" y="1000"/><a:ext cx="1000000" cy="1000000"/></a:xfrm></p:spPr>' \
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:txBody>' \
            '</p:sp></p:spTree></p:cSld></p:sld>'
    with zipfile.ZipFile(path, "w") as archive:
        for name, text in parts.items():
            archive.writestr(name, text)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    monkeypatch.setattr(docling_env.subprocess, "call", lambda *a, **k: pytest.fail("relaunch reached"))
    snapshot = InputSnapshot(path)
    version = register.pending_version(snapshot, "shelf:native-synthetic", synthetic=True)
    result = module().extract_procedure(snapshot, [version], input_root=root, out=tmp_path / "out")
    assert [(u.source_text, u.slide_index) for u in result.pptx_units] == [
        ("1. Do not pay 3–4².", 1), ("Fees: no fee", 2)]
    assert all(u.shape_id is None and "shape_id_not_exported" in u.provenance_gaps for u in result.pptx_units)
    assert all(not u.spans and u.rejection_reason == "pending_locator_contract" for u in result.pptx_units)
    assert snapshot.path.read_bytes() == snapshot.data
