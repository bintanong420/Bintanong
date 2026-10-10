"""Candidate policy extraction from synthetic raw Docling structures only."""
import copy
import json
from dataclasses import FrozenInstanceError, replace
from types import SimpleNamespace

import pytest

from backend.bintanong_tools.document_ingest import policy_text, register
from backend.bintanong_tools.prospectus_extractor import loader
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot, bytes_sha256


def item(text, page=1, label="text", top=150, bottom=180):
    return {"text": text, "label": label, "prov": [{"page_no": page, "bbox": {
        "l": 20, "t": top, "r": 450, "b": bottom, "coord_origin": "TOPLEFT"}}]}


def raw_document(texts, pages=3):
    return {"texts": texts, "pages": {str(i): {"size": {"width": 600, "height": 800}}
                                      for i in range(1, pages + 1)}}


@pytest.fixture
def bound(tmp_path):
    root = tmp_path / "originals"
    root.mkdir()
    source = root / "handbook.pdf"
    source.write_bytes(b"%PDF-synthetic-input")
    snapshot = InputSnapshot(source)
    version = register.pending_version(snapshot, "shelf:synthetic-handbook", synthetic=True)
    return root, snapshot, version


def test_raw_text_heading_clause_exception_scope_and_labels(bound):
    _, _, version = bound
    raw = raw_document([
        item("Scope", label="section_header"), item("USG members only."),
        item("Article 2 — Rules", label="section_header"),
        item("Shall not pay 25–50 pesos before 2026-10-10.²"), item("Except when rule 3 applies.")
    ])
    result = policy_text.read_policy_items(raw, version, printed_page_labels={1: "iv"})
    assert [u.source_text for u in result.units] == [t["text"] for t in raw["texts"]]
    rule, exception = result.units[-2:]
    assert rule.heading_path == ("Scope", "Article 2 — Rules")
    assert exception.exception_to == rule.item_id
    assert result.units[1].printed_scope == "USG members only."
    assert rule.printed_scope is None
    assert "CSG" not in json.dumps(result.as_dict())
    assert rule.spans[0].page == 1 and rule.spans[0].printed_page_label == "iv"
    assert rule.spans[0].text == rule.source_text
    assert rule.spans[0].version_id == version.version_id
    assert rule.spans[0].byte_sha256 == version.byte_sha256
    assert "heading_depth" not in result.as_dict()["units"][0]


def test_multipage_all_provenance_and_raw_item_omissions(bound):
    _, _, version = bound
    multi = item("Do not discard this exception — 12².")
    multi["prov"].append(item("ignored", page=2)["prov"][0])
    multi["prov"][0]["charspan"] = [0, 15]
    multi["prov"][1]["charspan"] = [15, len(multi["text"])]
    raw = raw_document([multi, item(" \n", page=2),
                        *[item("  Repeated   header  ", p, top=1, bottom=20) for p in (1, 2, 3)]], pages=4)
    before = copy.deepcopy(raw)
    result = policy_text.read_policy_items(raw, version)
    assert raw == before
    assert result.units[0].pages == (1, 2)
    assert [s.page for s in result.units[0].spans] == [1, 2]
    assert "".join(s.text for s in result.units[0].spans) == multi["text"]
    assert len(json.loads(result.units[0].raw_provenance_json)) == 2
    assert len(result.units) + len(result.item_omissions) == len(raw["texts"])
    assert [o.reason for o in result.item_omissions] == ["empty_text_item"] + ["repeated_header_footer"] * 3
    assert result.item_omissions[0].pages == (2,)
    assert result.item_omissions[0].raw_text == " \n"
    assert result.page_omissions == ((4, "scanned_no_text_layer"),)
    result.check_invariants()


@pytest.mark.parametrize("top,bottom", [(1, 20), (781, 798)])
def test_furniture_requires_three_distinct_pages_and_margin(bound, top, bottom):
    _, _, version = bound
    for texts, omitted in [([item("same", 1, top=top, bottom=bottom)] * 3, 0),
                            ([item("same", p, top=top, bottom=bottom) for p in (1, 2)], 0),
                            ([item("same", p) for p in (1, 2, 3)], 0),
                            ([item("same", p, top=top, bottom=bottom) for p in (1, 2, 3)], 3)]:
        assert len(policy_text.read_policy_items(raw_document(texts), version).item_omissions) == omitted


def test_bottomleft_furniture_and_unchanged_punctuation(bound):
    _, _, version = bound
    texts = [item("Same–²", p) for p in (1, 2, 3)]
    for t in texts:
        t["prov"][0]["bbox"].update(t=799, b=780, coord_origin="BOTTOMLEFT")
    result = policy_text.read_policy_items(raw_document(texts), version)
    assert [o.raw_text for o in result.item_omissions] == ["Same–²"] * 3


def test_body_reading_order_drives_headings(bound):
    _, _, version = bound
    raw = raw_document([item("clause"), item("First", label="section_header")], pages=1)
    raw["body"] = {"children": [{"cref": "#/texts/1"}, {"cref": "#/texts/0"}]}
    result = policy_text.read_policy_items(raw, version)
    assert [u.item_id for u in result.units] == ["text-1", "text-0"]
    assert result.units[1].heading_path == ("First",)


@pytest.mark.parametrize("damage", ["missing", "outside", "inverted", "origin", "size"])
def test_unlocatable_or_bad_geometry_explicitly_rejected(bound, damage):
    _, _, version = bound
    raw = raw_document([item("rule")], pages=1)
    prov = raw["texts"][0]["prov"][0]
    if damage == "missing":
        raw["texts"][0]["prov"] = []
    elif damage == "outside":
        prov["bbox"]["r"] = 900
    elif damage == "inverted":
        prov["bbox"]["r"] = 0
    elif damage == "origin":
        del prov["bbox"]["coord_origin"]
    else:
        del raw["pages"]["1"]["size"]
    result = policy_text.read_policy_items(raw, version)
    unit = result.units[0]
    assert not unit.anchored and not unit.spans and unit.rejection_reason
    assert unit.source_text == "rule" and result.raw_item_count == 1


@pytest.mark.parametrize("damage", ["bad_text", "bad_item", "bad_page", "out_of_range", "private"])
def test_malformed_or_private_raw_refused(bound, damage):
    _, _, version = bound
    raw = raw_document([item("rule")], pages=1)
    if damage == "bad_text":
        raw["texts"][0]["text"] = 3
    elif damage == "bad_item":
        raw["texts"][0] = None
    elif damage == "bad_page":
        raw["texts"][0]["prov"][0]["page_no"] = True
    elif damage == "out_of_range":
        raw["texts"][0]["prov"][0]["page_no"] = 2
    else:
        raw["texts"][0]["text"] = "student sess-123 fact-987"
    with pytest.raises(ValueError):
        policy_text.read_policy_items(raw, version)


def test_empty_pages_are_findings_and_zero_page_refused(bound):
    _, _, version = bound
    result = policy_text.read_policy_items(raw_document([], pages=2), version)
    assert result.page_omissions == ((1, "scanned_no_text_layer"), (2, "scanned_no_text_layer"))
    with pytest.raises(ValueError):
        policy_text.read_policy_items(raw_document([], pages=0), version)


def test_immutable_result_and_exact_accounting(bound):
    _, _, version = bound
    result = policy_text.read_policy_items(raw_document([item("a"), item("")]), version)
    with pytest.raises(FrozenInstanceError):
        result.units[0].source_text = "edited"
    with pytest.raises(ValueError, match="item"):
        replace(result, units=result.units + result.units).check_invariants()
    with pytest.raises(ValueError, match="item"):
        replace(result, item_omissions=()).check_invariants()
    with pytest.raises(ValueError, match="page"):
        replace(result, page_omissions=()).check_invariants()


def stub_load(monkeypatch, raw, mutate=None):
    calls = []
    def load(path, **kw):
        calls.append((path, kw))
        assert kw["snapshot"].path == path
        if mutate:
            path.write_bytes(mutate)
        payload = json.dumps(raw, ensure_ascii=False).encode()
        meta = {"pdf_sha256": kw["snapshot"].sha256, "raw_json_sha256": bytes_sha256(payload)}
        return SimpleNamespace(raw_json_bytes=payload, raw_json_sha256=bytes_sha256(payload),
                               meta_bytes=json.dumps(meta).encode(), cache_status="converted")
    monkeypatch.setattr(loader, "load_document_result", load)
    monkeypatch.setattr(loader, "load_docling", lambda: {})
    return calls


def test_explicit_scratch_paths_snapshot_and_no_source_writes(bound, tmp_path, monkeypatch):
    root, snap, version = bound
    calls = stub_load(monkeypatch, raw_document([item("not 20–30²")], pages=1))
    out = tmp_path / "out"
    result = policy_text.extract_policy(snap, [version], input_root=root, out=out)
    _, kw = calls[0]
    assert kw["raw_json_path"].parent == out.resolve()
    assert out.resolve() in kw["stage_dir"].parents
    assert kw["snapshot"] is snap
    assert sorted(p.name for p in root.iterdir()) == ["handbook.pdf"]
    assert snap.path.read_bytes() == snap.data
    assert (out / "manifest.json").exists()
    assert json.loads((out / "policy_candidates.json").read_text(encoding="utf-8")) == result.as_dict()


def test_changed_source_prevents_publication(bound, tmp_path, monkeypatch):
    root, snap, version = bound
    stub_load(monkeypatch, raw_document([item("rule")]), mutate=b"changed")
    out = tmp_path / "out"
    with pytest.raises(ValueError, match="changed"):
        policy_text.extract_policy(snap, [version], input_root=root, out=out)
    assert not (out / "manifest.json").exists()
    assert not (out / "policy_candidates.json").exists()


@pytest.mark.parametrize("damage", ["digest", "namespace", "id", "promote", "duplicate"])
def test_invalid_register_refused_before_conversion(bound, tmp_path, monkeypatch, damage):
    root, snap, version = bound
    bad = version.model_dump(mode="json")
    if damage == "digest":
        bad["byte_sha256"] = "b" * 64
    elif damage == "namespace":
        bad["namespace"] = "private_session"
    elif damage == "id":
        bad["edition_id"] = "edition-other"
    elif damage == "promote":
        bad["issuer"]["state"] = "not_stated"
    versions = [bad, bad] if damage == "duplicate" else [bad]
    calls = stub_load(monkeypatch, raw_document([]))
    with pytest.raises(ValueError):
        policy_text.extract_policy(snap, versions, input_root=root, out=tmp_path / "out")
    assert calls == []


@pytest.mark.parametrize("where", ["input", "repo", "nonempty"])
def test_output_containment_before_conversion(bound, tmp_path, monkeypatch, where):
    root, snap, version = bound
    if where == "input":
        out = root / "out"
    else:
        out = tmp_path / where / "out"
        out.parent.mkdir()
        if where == "repo":
            (out.parent / ".git").write_text("gitdir: x")
        else:
            out.mkdir()
            (out / "keep").write_text("keep")
    calls = stub_load(monkeypatch, raw_document([]))
    with pytest.raises(ValueError):
        policy_text.extract_policy(snap, [version], input_root=root, out=out)
    assert calls == []


def test_missing_docling_never_relaunches(bound, tmp_path, monkeypatch):
    root, snap, version = bound
    def unavailable():
        raise RuntimeError("installed Docling unavailable")
    monkeypatch.setattr(loader, "load_docling", unavailable)
    monkeypatch.setattr(loader, "ensure_docling_env", lambda: pytest.fail("relaunch reached"))
    with pytest.raises(RuntimeError, match="unavailable"):
        policy_text.extract_policy(snap, [version], input_root=root, out=tmp_path / "out")


def test_non_pdf_and_wrong_input_root_refused(bound, tmp_path, monkeypatch):
    root, snap, version = bound
    calls = stub_load(monkeypatch, raw_document([]))
    with pytest.raises(ValueError):
        policy_text.extract_policy(snap, [version], input_root=tmp_path / "out", out=tmp_path / "scratch")
    deck = root / "deck.pptx"
    deck.write_bytes(b"PK-synthetic")
    ds = InputSnapshot(deck)
    dv = register.pending_version(ds, "shelf:deck", synthetic=True)
    with pytest.raises(ValueError, match="PDF"):
        policy_text.extract_policy(ds, [dv], input_root=root, out=tmp_path / "scratch")
    assert calls == []


@pytest.mark.parametrize("charspans", [None, [[0, 3], [5, 9]], [[0, 5], [5, 99]],
                                      [[0, 5], [5, True]]])
def test_multipage_charspan_not_invented(bound, charspans):
    _, _, version = bound
    multi = item("not 12–²!")
    multi["prov"].append(item("unused", page=2)["prov"][0])
    if charspans is not None:
        for prov, pair in zip(multi["prov"], charspans):
            prov["charspan"] = pair
    result = policy_text.read_policy_items(raw_document([multi]), version)
    assert result.units[0].pages == (1, 2)
    assert result.units[0].rejection_reason and not result.units[0].anchored


def test_real_loader_with_stub_docling_uses_stage_and_never_relaunches(bound, tmp_path, monkeypatch):
    from backend.bintanong_tools.prospectus_extractor import docling_env
    root, snap, version = bound
    raw = raw_document([item("Shall not lose 2–3².")], pages=1)
    doc = SimpleNamespace(export_to_dict=lambda: raw, export_to_markdown=lambda: "unused")
    monkeypatch.setattr(loader, "load_docling", lambda: {
        "DoclingDocument": SimpleNamespace(model_validate=lambda data: doc)})
    monkeypatch.setattr(docling_env.subprocess, "call", lambda *a, **k: pytest.fail("relaunch reached"))
    def convert(source):
        assert source.stream.read() == snap.data
        return SimpleNamespace(document=doc, errors=[])
    result = policy_text.extract_policy(snap, [version], input_root=root, out=tmp_path / "out",
                                        converter=SimpleNamespace(convert=convert))
    assert result.units[0].source_text == raw["texts"][0]["text"]
    assert sorted(p.name for p in root.iterdir()) == ["handbook.pdf"]


def test_missing_installed_import_refused_without_loader_call(bound, tmp_path, monkeypatch):
    root, snap, version = bound
    calls = stub_load(monkeypatch, raw_document([]))
    monkeypatch.setattr(policy_text.importlib, "import_module",
                        lambda *a: (_ for _ in ()).throw(ImportError("missing installed package")))
    with pytest.raises(ImportError, match="missing installed"):
        policy_text.extract_policy(snap, [version], input_root=root, out=tmp_path / "out")
    assert calls == []
