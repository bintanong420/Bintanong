"""Pending byte identities, validated before candidate conversion (Task 5 prerequisite)."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ...bintanong_contracts.base import VOCAB
from ...bintanong_contracts.governance import SourceDocumentVersion, check_register
from ..prospectus_extractor.identity import InputSnapshot, bytes_sha256


def mint_pending_register(manifest: Sequence[Mapping[str, Any]], *, synthetic: bool = False
                          ) -> tuple[SourceDocumentVersion, ...]:
    """Mint from hash-manifest entries with explicit logical acquisition locators.

    Each entry has exactly filename, sha256 and acquisition_locator. Inspection paths must
    be mapped by the caller to logical locators; neither filenames nor local paths confer scope.
    """
    by_hash: dict[str, SourceDocumentVersion] = {}
    for entry in manifest:
        if not isinstance(entry, Mapping) or set(entry) != {"filename", "sha256", "acquisition_locator"}:
            raise ValueError("manifest entry needs filename, sha256 and acquisition_locator only")
        digest = entry["sha256"]
        scope = {"value": None, "state": "pending", "evidence_ref": None, "basis": None}
        data = {
            "schema_version": SourceDocumentVersion.SCHEMA_VERSION, "namespace": "institutional",
            "synthetic": synthetic, "document_id": f"doc-{digest}", "version_id": f"ver-{digest}",
            "edition_id": f"edition-{digest}", "filename": entry["filename"], "byte_sha256": digest,
            "acquisition_locators": [entry["acquisition_locator"]], "document_category": "source_document",
            **{name: scope for name in VOCAB["scope_fields"]},
            "supersession": {"relation": "none", "target_version_id": None,
                             "state": "pending", "evidence_ref": None, "basis": None},
            **{name: {"state": VOCAB["initial_states"][name], "evidence_ref": None}
               for name in ("acquisition_state", "verification_state", "approval_state", "content_review_state")},
            "approval_id": None, "evidence": [],
        }
        record = SourceDocumentVersion.parse(data)
        if digest in by_hash:
            prior = by_hash[digest]
            locators = tuple(sorted(set(prior.acquisition_locators + record.acquisition_locators)))
            # Duplicate bytes are one version; the filename is a deterministic display label only.
            record = prior.model_copy(update={"acquisition_locators": locators,
                                              "filename": min(prior.filename, record.filename)})
        by_hash[digest] = record
    records = tuple(by_hash[k] for k in sorted(by_hash))
    check_register(records)
    return records


def pending_version(snapshot: InputSnapshot, locator: str, *, synthetic: bool = False) -> SourceDocumentVersion:
    if not isinstance(snapshot, InputSnapshot) or bytes_sha256(snapshot.data) != snapshot.sha256:
        raise ValueError("invalid input snapshot")
    snapshot.verify_unchanged()
    return mint_pending_register([{"filename": snapshot.path.name, "sha256": snapshot.sha256,
                                   "acquisition_locator": locator}], synthetic=synthetic)[0]


def load_pending_register(records: Sequence[SourceDocumentVersion | Mapping[str, Any]]
                          ) -> tuple[SourceDocumentVersion, ...]:
    """Reparse existing contracts, then refuse promotion and non-byte-derived identities."""
    parsed = tuple(SourceDocumentVersion.parse(r.model_dump(mode="json")
                   if isinstance(r, SourceDocumentVersion) else r) for r in records)
    check_register(parsed)
    for record in parsed:
        digest = record.byte_sha256
        if (record.document_id, record.version_id, record.edition_id) != (
                f"doc-{digest}", f"ver-{digest}", f"edition-{digest}"):
            raise ValueError("register ids must derive from the byte SHA-256")
        if record.document_category != "source_document" or record.evidence or record.approval_id is not None:
            raise ValueError("candidate preflight accepts only pending source_document records")
        for field in VOCAB["scope_fields"] + ["supersession"]:
            if getattr(record, field).state != "pending":
                raise ValueError("candidate preflight cannot promote scope or supersession")
        for field in ("acquisition_state", "verification_state", "approval_state", "content_review_state"):
            if getattr(record, field).state != VOCAB["initial_states"][field]:
                raise ValueError("candidate preflight cannot promote source states")
    return parsed


def version_for_snapshot(snapshot: InputSnapshot,
                         records: Sequence[SourceDocumentVersion | Mapping[str, Any]]) -> SourceDocumentVersion:
    parsed = load_pending_register(records)
    if not isinstance(snapshot, InputSnapshot) or bytes_sha256(snapshot.data) != snapshot.sha256:
        raise ValueError("invalid input snapshot")
    snapshot.verify_unchanged()
    for record in parsed:
        if record.byte_sha256 == snapshot.sha256:
            return record
    raise ValueError("snapshot bytes have no matching pending register version")
