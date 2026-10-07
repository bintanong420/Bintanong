"""Source governance contracts: SourceDocumentVersion, SourceConflict, SessionFact.

States, roles, evidence kinds and the transition table come from governance-vocabulary.json.
Acquisition, verification, approval and content review are four separate fields. A state other than
the initial one must cite evidence inside the record whose kind and recorder match a transition row.
Extraction audits, extractor labels, filenames and possession never authorize anything.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .base import (VOCAB, Contract, ContractError, EvidenceKind, Record, Role, State,
                   reject_foreign_ids)

ID_DOC = r"^doc-[a-z0-9-]+$"
ID_VER = r"^ver-[a-z0-9-]+$"
ID_EDITION = r"^edition-[a-z0-9-]+$"
SHA256 = r"^[0-9a-f]{64}$"
TIMESTAMP = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
_LOCAL_PATH = re.compile(r"^([A-Za-z]:[\\/]|[\\/])")

Basis = Annotated[str, Field(pattern="^(" + "|".join(VOCAB["field_bases"]["allowed"]) + ")$")]
STATE_FIELDS = ("acquisition_state", "verification_state", "approval_state", "content_review_state")


# --------------------------------------------------------------------------------------------
# Transition table
# --------------------------------------------------------------------------------------------
def _rows(field: str, to_state: str, frm: str | None = None) -> list[dict]:
    return [t for t in VOCAB["transitions"]
            if t["field"] == field and t["to"] == to_state and (frm is None or t["from"] == frm)]


class Evidence(Record):
    evidence_id: str = Field(min_length=1)
    kind: EvidenceKind()
    recorded_by: Role()
    recorded_at: str = Field(pattern=TIMESTAMP)
    authorization_ref: str | None = None


def evidence_authorizes(field: str, to_state: str, ev: Evidence, frm: str | None = None) -> bool:
    """True if `ev` can authorize entering `to_state` of `field` under a row of the table."""
    for row in _rows(field, to_state, frm):
        if ev.kind != row["evidence_kind"] or ev.recorded_by not in row["recorded_by"]:
            continue
        if bool(ev.authorization_ref) != bool(row.get("needs_authorization_ref")):
            continue
        return True
    return False


def _check_state(errs: list[str], evs: dict[str, Evidence], label: str, vocab_field: str,
                 state: str, ref: str | None) -> None:
    if state == VOCAB["initial_states"][vocab_field]:
        if ref is not None:
            errs.append(f"{label}: initial state {state} must not cite evidence")
        return
    if ref is None:
        errs.append(f"{label}: {state} without an evidence reference")
        return
    ev = evs.get(ref)
    if ev is None:
        errs.append(f"{label}: evidence {ref!r} not in the record")
    elif not evidence_authorizes(vocab_field, state, ev):
        errs.append(f"{label}: evidence {ref!r} ({ev.kind} by {ev.recorded_by}) cannot authorize {state}")


def _index_evidence(errs: list[str], evidence: Sequence[Evidence]) -> dict[str, Evidence]:
    evs: dict[str, Evidence] = {}
    needing_ref = {t["evidence_kind"] for t in VOCAB["transitions"] if t.get("needs_authorization_ref")}
    for ev in evidence:
        if ev.evidence_id in evs:
            errs.append(f"duplicate evidence id {ev.evidence_id}")
        evs[ev.evidence_id] = ev
        if (ev.kind in needing_ref) != bool(ev.authorization_ref):
            errs.append(f"evidence {ev.evidence_id}: authorization_ref "
                        f"{'required' if ev.kind in needing_ref else 'not allowed'}")
    return evs


# --------------------------------------------------------------------------------------------
# SourceDocumentVersion
# --------------------------------------------------------------------------------------------
class ScopeField(Record):
    value: str | None
    state: State("scope_field")
    evidence_ref: str | None
    basis: Basis | None


class Supersession(Record):
    relation: Annotated[str, Field(pattern="^(" + "|".join(VOCAB["supersession_relations"]) + ")$")]
    target_version_id: str | None = Field(pattern=ID_VER)
    state: State("scope_field")
    evidence_ref: str | None
    basis: Basis | None


class AcquisitionState(Record):
    state: State("acquisition_state")
    evidence_ref: str | None


class VerificationState(Record):
    state: State("verification_state")
    evidence_ref: str | None


class ApprovalState(Record):
    state: State("approval_state")
    evidence_ref: str | None


class ContentReviewState(Record):
    state: State("content_review_state")
    evidence_ref: str | None


class SourceDocumentVersion(Contract):
    """One acquired byte identity. Approval id stays null without authorized evidence."""

    SCHEMA_VERSION = "bintanong-source-register-v1"
    namespace: Literal["institutional"]
    synthetic: bool
    document_id: str = Field(pattern=ID_DOC)
    version_id: str = Field(pattern=ID_VER)
    edition_id: str = Field(pattern=ID_EDITION)
    filename: str = Field(min_length=1)
    byte_sha256: str = Field(pattern=SHA256)
    acquisition_locators: tuple[Annotated[str, Field(min_length=1)], ...] = Field(min_length=1)
    document_category: Annotated[str, Field(pattern="^(" + "|".join(VOCAB["document_categories"]) + ")$")]
    issuer: ScopeField
    campus: ScopeField
    college: ScopeField
    program: ScopeField
    cohort: ScopeField
    printed_revision: ScopeField
    effective_from: ScopeField
    effective_to: ScopeField
    supersession: Supersession
    acquisition_state: AcquisitionState
    verification_state: VerificationState
    approval_state: ApprovalState
    content_review_state: ContentReviewState
    approval_id: str | None
    evidence: tuple[Evidence, ...]

    @model_validator(mode="after")
    def _governance(self):
        errs: list[str] = []
        try:
            reject_foreign_ids(self, "institutional")
        except ValueError as exc:
            errs.append(str(exc))
        for text in (self.filename, *self.acquisition_locators):
            if _LOCAL_PATH.match(text):
                errs.append(f"{text!r} looks like a local path; registers carry fictional or logical locators only")
        if len(set(self.acquisition_locators)) != len(self.acquisition_locators):
            errs.append("duplicate acquisition locators in one version")
        evs = _index_evidence(errs, self.evidence)
        for name in STATE_FIELDS:
            ref = getattr(self, name)
            _check_state(errs, evs, name, name, ref.state, ref.evidence_ref)
        for name in VOCAB["scope_fields"] + ["supersession"]:
            f = getattr(self, name)
            _check_state(errs, evs, name, "scope_field", f.state, f.evidence_ref)
            if f.state in ("pending", "not_stated") and f.basis is not None:
                errs.append(f"{name}: {f.state} must carry no basis (nothing is inferred)")
            if name != "supersession":
                if f.state in ("pending", "not_stated") and f.value is not None:
                    errs.append(f"{name}: {f.state} must carry no value (nothing is inferred)")
                if f.state in ("observed", "verified") and (f.value is None or f.basis is None):
                    errs.append(f"{name}: {f.state} needs a value and an allowed basis")
            elif f.state in ("observed", "verified") and f.basis is None:
                errs.append("supersession: observed or verified needs an allowed basis")
        s = self.supersession
        if s.relation != "none":
            if s.target_version_id is None or s.state == "pending":
                errs.append("supersession: a relation needs a target and an evidenced state")
            if s.target_version_id == self.version_id:
                errs.append("supersession: a version cannot supersede itself")
        elif s.target_version_id is not None:
            errs.append("supersession: relation none must not name a target")
        if self.verification_state.state in ("observed", "verified") and \
                self.acquisition_state.state not in ("observed", "verified"):
            errs.append("verification recorded against bytes that are not acquired and matching")
        appr = self.approval_state
        if appr.state in ("approved", "revoked"):
            ev = evs.get(appr.evidence_ref)
            if not self.approval_id or ev is None or ev.authorization_ref != self.approval_id:
                errs.append("approval_id must equal the authorization_ref of the cited authorized evidence")
        elif self.approval_id is not None:
            errs.append("approval_id supplied without authorized approval evidence")
        if appr.state == "approved":
            if self.acquisition_state.state != "verified" or self.verification_state.state != "verified":
                errs.append("approval needs verified acquisition and verified scope")
            if self.issuer.state != "verified" or any(
                    getattr(self, f).state not in ("verified", "not_stated") for f in VOCAB["scope_fields"]):
                errs.append("approval needs issuer and scope/effectivity fields verified or explicitly not stated")
            if self.document_category in VOCAB["proposal_categories"]:
                errs.append("a proposal candidate cannot be approved as a source")
        if errs:
            raise ValueError("; ".join(errs))
        return self


def check_register(records: Sequence[SourceDocumentVersion]) -> None:
    """Cross-record rules. Raises ContractError naming every problem."""
    errs: list[str] = []
    ids = [r.version_id for r in records]
    errs += [f"duplicate version_id {v}" for v in sorted(set(ids)) if ids.count(v) > 1]
    by_hash: dict[str, list[str]] = {}
    by_edition: dict[str, set[str]] = {}
    for r in records:
        by_hash.setdefault(r.byte_sha256, []).append(r.version_id)
        by_edition.setdefault(r.edition_id, set()).add(r.byte_sha256)
    errs += [f"same bytes recorded as separate versions {v}; merge locators"
             for v in by_hash.values() if len(v) > 1]
    errs += [f"edition {e} spans different bytes (same filename is not same edition)"
             for e, h in by_edition.items() if len(h) > 1]
    for r in records:
        target = r.supersession.target_version_id
        if target is not None and target not in ids:
            errs.append(f"{r.version_id}: supersession target {target} is not in the register")
    if errs:
        raise ContractError("; ".join(errs))


# --------------------------------------------------------------------------------------------
# SourceConflict
# --------------------------------------------------------------------------------------------
class Claim(Record):
    version_id: str = Field(pattern=ID_VER)
    span_ref: str = Field(min_length=1)
    claim_text: str = Field(min_length=1)


class AffectedScope(Record):
    capability: str = Field(min_length=1)
    campus: str | None
    college: str | None
    program: str | None
    cohort: str | None


class SourceConflict(Contract):
    SCHEMA_VERSION = "bintanong-source-conflict-v1"
    namespace: Literal["institutional"]
    synthetic: bool
    conflict_id: str = Field(pattern=r"^conflict-[a-z0-9-]+$")
    claims: tuple[Claim, ...] = Field(min_length=2)
    affected_scope: AffectedScope
    resolution_state: State("conflict_resolution_state")
    resolution_evidence_ref: str | None
    resolution_basis: Annotated[str, Field(pattern="^(" + "|".join(VOCAB["conflict_resolution_bases"]) + ")$")] | None
    evidence: tuple[Evidence, ...]

    @model_validator(mode="after")
    def _rules(self):
        errs: list[str] = []
        try:
            reject_foreign_ids(self, "institutional")
        except ValueError as exc:
            errs.append(str(exc))
        evs = _index_evidence(errs, self.evidence)
        if len({(c.version_id, c.span_ref) for c in self.claims}) < 2:
            errs.append("a conflict needs two distinct claims")
        _check_state(errs, evs, "resolution", "conflict_resolution_state",
                     self.resolution_state, self.resolution_evidence_ref)
        if (self.resolution_state == "resolved") != (self.resolution_basis is not None):
            errs.append("a resolution basis is required exactly when the conflict is resolved")
        if errs:
            raise ValueError("; ".join(errs))
        return self


def check_conflict_versions(conflict: SourceConflict, version_ids: set[str] | Sequence[str]) -> None:
    unknown = [c.version_id for c in conflict.claims if c.version_id not in set(version_ids)]
    if unknown:
        raise ContractError(f"claim cites unknown version(s) {unknown}")


def blocked_capabilities(conflicts: Sequence[SourceConflict]) -> set[str]:
    """An unresolved or referred conflict blocks only its own capability."""
    return {c.affected_scope.capability for c in conflicts if c.resolution_state != "resolved"}


# --------------------------------------------------------------------------------------------
# SessionFact: private, session-only, never institutional evidence
# --------------------------------------------------------------------------------------------
class FactValue(Record):
    key: str = Field(min_length=1)
    value: str


class SessionFact(Contract):
    SCHEMA_VERSION = "bintanong-session-fact-v1"
    namespace: Literal["private_session"]
    synthetic: bool
    fact_id: str = Field(pattern=r"^fact-[a-z0-9-]+$")
    session_id: str = Field(pattern=r"^sess-[a-z0-9-]+$")
    origin: Annotated[str, Field(pattern="^(" + "|".join(VOCAB["session_origins"]) + ")$")]
    confirmation_state: State("session_confirmation_state")
    confirmation_evidence_ref: str | None
    lifecycle: Literal["session_only"]
    fact: FactValue
    evidence: tuple[Evidence, ...]

    @model_validator(mode="after")
    def _rules(self):
        errs: list[str] = []
        try:
            reject_foreign_ids(self, "private_session")
        except ValueError as exc:
            errs.append(str(exc))
        evs = _index_evidence(errs, self.evidence)
        _check_state(errs, evs, "confirmation", "session_confirmation_state",
                     self.confirmation_state, self.confirmation_evidence_ref)
        if errs:
            raise ValueError("; ".join(errs))
        return self
