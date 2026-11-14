"""Synthetic pending-register preflight; no source authorization is exercised."""
import copy

import pytest

from backend.bintanong_contracts.base import VOCAB
from backend.bintanong_contracts.governance import SourceDocumentVersion, check_register
from backend.bintanong_tools.document_ingest import register
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot


def entry(digest="a" * 64, filename="Handbook.pdf", locator="shelf:handbook-a"):
    return {"sha256": digest, "filename": filename, "acquisition_locator": locator}


def test_digest_identity_duplicates_and_pending_roundtrip():
    versions = register.mint_pending_register([
        entry(), entry(filename="Renamed.pdf", locator="shelf:handbook-b"), entry("b" * 64)
    ], synthetic=True)
    assert len(versions) == 2
    check_register(versions)
    first, second = versions
    assert first.document_id == "doc-" + "a" * 64
    assert first.version_id == "ver-" + "a" * 64
    assert first.edition_id == "edition-" + "a" * 64
    assert second.edition_id != first.edition_id
    assert first.acquisition_locators == ("shelf:handbook-a", "shelf:handbook-b")
    assert first == SourceDocumentVersion.parse(first.model_dump_json())
    for record in versions:
        assert record.document_category == "source_document"
        assert record.approval_id is None and not record.evidence
        for field in VOCAB["scope_fields"]:
            scope = getattr(record, field)
            assert (scope.state, scope.value, scope.basis, scope.evidence_ref) == ("pending", None, None, None)
        for field, initial in VOCAB["initial_states"].items():
            if hasattr(record, field):
                assert getattr(record, field).state == initial
        assert record.supersession.state == "pending" and record.supersession.target_version_id is None


def test_rename_does_not_change_ids():
    a = register.mint_pending_register([entry()], synthetic=True)[0]
    b = register.mint_pending_register([entry(filename="2026 USG approved.pdf")], synthetic=True)[0]
    assert (a.document_id, a.version_id, a.edition_id) == (b.document_id, b.version_id, b.edition_id)


@pytest.mark.parametrize("patch", [
    {"sha256": "A" * 64}, {"sha256": 5}, {"filename": "C:/private.pdf"},
    {"acquisition_locator": "C:/private.pdf"}, {"acquisition_locator": "sess-123"},
    {"filename": "fact-123.pdf"}, {"approved": True},
])
def test_mint_refuses_malformed_or_private_input(patch):
    with pytest.raises(ValueError):
        register.mint_pending_register([entry() | patch], synthetic=True)


def test_empty_register_refused():
    with pytest.raises(ValueError):
        register.mint_pending_register([], synthetic=True)


def test_snapshot_binding_refuses_other_bytes_and_non_digest_ids(tmp_path):
    source = tmp_path / "a.pdf"
    source.write_bytes(b"%PDF-synthetic")
    snap = InputSnapshot(source)
    record = register.pending_version(snap, "shelf:a", synthetic=True)
    assert register.version_for_snapshot(snap, [record]) == record
    for field, value in [("byte_sha256", "b" * 64), ("version_id", "ver-wrong"),
                         ("document_id", "doc-wrong"), ("edition_id", "edition-wrong"),
                         ("namespace", "private_session"), ("synthetic", "true")]:
        bad = record.model_dump(mode="json") | {field: value}
        with pytest.raises(ValueError):
            register.version_for_snapshot(snap, [bad])


@pytest.mark.parametrize("field,state", [("issuer", "not_stated"), ("approval_state", "approved"),
                                         ("verification_state", "verified"), ("content_review_state", "reviewed")])
def test_loaded_register_cannot_promote(tmp_path, field, state):
    source = tmp_path / "a.pdf"
    source.write_bytes(b"%PDF-synthetic")
    snap = InputSnapshot(source)
    record = register.pending_version(snap, "shelf:a", synthetic=True)
    bad = copy.deepcopy(record.model_dump(mode="json"))
    bad[field]["state"] = state
    with pytest.raises(ValueError):
        register.version_for_snapshot(snap, [bad])


def test_duplicate_loaded_versions_refused(tmp_path):
    source = tmp_path / "a.pdf"
    source.write_bytes(b"%PDF-synthetic")
    snap = InputSnapshot(source)
    record = register.pending_version(snap, "shelf:a", synthetic=True)
    with pytest.raises(ValueError, match="duplicate"):
        register.version_for_snapshot(snap, [record, record])
