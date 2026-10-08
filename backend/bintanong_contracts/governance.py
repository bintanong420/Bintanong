"""Source governance contracts: SourceDocumentVersion, SourceConflict, SessionFact.

States, roles, evidence kinds and the transition table come from governance-vocabulary.json.
Acquisition, verification, approval and content review are four separate fields. A state other than
the initial one must cite evidence inside the record whose kind and recorder match a transition row,
and that row's `from` state must itself have been entered by earlier evidence of the same record.
Extraction audits, extractor labels, filenames and possession never authorize anything.
"""

from __future__ import annotations

import calendar
import re
from collections.abc import Sequence
from datetime import date
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .base import (TIMESTAMP, VOCAB, Contract, ContractError, EvidenceKind, Record, Role, State, folded, id_pattern,
                   is_logical_locator, is_plain_filename, parse_timestamp, reject_foreign_ids, strip_format)

ID_DOC = id_pattern("doc-")
ID_VER = id_pattern("ver-")
ID_EDITION = id_pattern("edition-")
ID_CONFLICT = id_pattern("conflict-")
ID_FACT = id_pattern("fact-")
ID_SESSION = id_pattern("sess-")
SHA256 = r"^[0-9a-f]{64}$"
_TOKEN = r"^\S+$"          # approval ids and authorization references: no blank, no padding, no inner space
_TRIMMED = r"^\S(?:.*\S)?$"

Basis = Annotated[str, Field(pattern="^(" + "|".join(VOCAB["field_bases"]["allowed"]) + ")$")]
STATE_FIELDS = ("acquisition_state", "verification_state", "approval_state", "content_review_state")
OBSERVED = ("observed", "verified")


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
    authorization_ref: str | None = Field(default=None, pattern=_TOKEN)

    @model_validator(mode="after")
    def _real_time(self):
        if parse_timestamp(self.recorded_at) is None:
            raise ValueError(f"evidence {self.evidence_id}: {self.recorded_at!r} is not a real timestamp")
        return self


def _row_accepts(row: dict, ev: Evidence) -> bool:
    return (ev.kind == row["evidence_kind"] and ev.recorded_by in row["recorded_by"]
            and bool(ev.authorization_ref) == bool(row.get("needs_authorization_ref")))


def evidence_authorizes(field: str, to_state: str, ev: Evidence, frm: str | None = None) -> bool:
    """True if `ev` can authorize entering `to_state` of `field` under a row of the table."""
    return any(_row_accepts(row, ev) for row in _rows(field, to_state, frm))


def entered_in_order(field: str, state: str, evidence: Sequence[Evidence], i: int) -> bool:
    """The `from` column on a record: evidence[i] enters `state` under a row whose `from` is the initial
    state, or a state that EARLIER evidence of the same record (earlier in the list and not dated later)
    entered in turn. Evidence is not bound to a field, so this proves the order of the evidence kinds, not
    who wrote what for which field."""
    for row in _rows(field, state):
        if not _row_accepts(row, evidence[i]):
            continue
        if row["from"] == VOCAB["initial_states"][field]:
            return True
        now = parse_timestamp(evidence[i].recorded_at)
        for j in range(i):
            before = parse_timestamp(evidence[j].recorded_at)
            if now and before and before <= now and entered_in_order(field, row["from"], evidence, j):
                return True
    return False


def _check_state(errs: list[str], evidence: Sequence[Evidence], label: str, vocab_field: str,
                 state: str, ref: str | None) -> None:
    if state == VOCAB["initial_states"][vocab_field]:
        if ref is not None:
            errs.append(f"{label}: initial state {state} must not cite evidence")
        return
    if ref is None:
        errs.append(f"{label}: {state} without an evidence reference")
        return
    position = next((i for i, e in enumerate(evidence) if e.evidence_id == ref), None)
    if position is None:
        errs.append(f"{label}: evidence {ref!r} not in the record")
        return
    ev = evidence[position]
    if not evidence_authorizes(vocab_field, state, ev):
        errs.append(f"{label}: evidence {ref!r} ({ev.kind} by {ev.recorded_by}) cannot authorize {state}")
    elif not entered_in_order(vocab_field, state, evidence, position):
        errs.append(f"{label}: {state} has no earlier evidence that entered the state it comes from")


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


_PARTIAL_DATE = re.compile(r"([0-9]{4})(?:-([0-9]{2})(?:-([0-9]{2}))?)?")


def _date_span(text: str | None) -> tuple[date, date] | None:
    """Earliest and latest day a (possibly partial ISO) date can mean, or None for any other format. The
    printed date format is an open owner decision, so only ISO dates are ever compared."""
    m = _PARTIAL_DATE.fullmatch(text or "")
    if not m:
        return None
    year, month, day = int(m.group(1)), m.group(2), m.group(3)
    try:
        first = date(year, int(month or 1), int(day or 1))
        last = date(year, int(month or 12), int(day) if day else calendar.monthrange(year, int(month or 12))[1])
    except ValueError:
        return None
    return first, last


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
    approval_id: str | None = Field(pattern=_TOKEN)
    evidence: tuple[Evidence, ...]

    @model_validator(mode="after")
    def _governance(self):
        errs: list[str] = []
        try:
            reject_foreign_ids(self, "institutional")
        except ValueError as exc:
            errs.append(str(exc))
        if not is_plain_filename(self.filename):
            errs.append(f"filename {self.filename!r} is not a plain file name (no path, drive, scheme or control character)")
        for loc in self.acquisition_locators:
            if not is_logical_locator(loc):
                errs.append(f"locator {loc!r} is a local path, file URL or padded text; "
                            "registers carry logical locators or https URLs only")
        if len(set(self.acquisition_locators)) != len(self.acquisition_locators):
            errs.append("duplicate acquisition locators in one version")
        evs = _index_evidence(errs, self.evidence)
        for name in STATE_FIELDS:
            ref = getattr(self, name)
            _check_state(errs, self.evidence, name, name, ref.state, ref.evidence_ref)
        for name in VOCAB["scope_fields"] + ["supersession"]:
            f = getattr(self, name)
            _check_state(errs, self.evidence, name, "scope_field", f.state, f.evidence_ref)
            if f.state in ("pending", "not_stated") and f.basis is not None:
                errs.append(f"{name}: {f.state} must carry no basis (nothing is inferred)")
            if name != "supersession":
                if f.state in ("pending", "not_stated") and f.value is not None:
                    errs.append(f"{name}: {f.state} must carry no value (nothing is inferred)")
                if f.state in OBSERVED and (f.value is None or f.basis is None):
                    errs.append(f"{name}: {f.state} needs a value and an allowed basis")
            elif f.state in OBSERVED and f.basis is None:
                errs.append("supersession: observed or verified needs an allowed basis")
        errs += self._supersession_errors()
        errs += self._effectivity_errors()
        if self.verification_state.state in OBSERVED and self.acquisition_state.state not in OBSERVED:
            errs.append("verification recorded against bytes that are not acquired and matching")
        errs += self._approval_errors(evs)
        if errs:
            raise ValueError("; ".join(errs))
        return self

    def _supersession_errors(self) -> list[str]:
        s, errs = self.supersession, []
        if s.relation == "none":
            if s.target_version_id is not None:
                errs.append("supersession: relation none must not name a target")
            if s.state in OBSERVED:
                errs.append("supersession: relation none cannot be observed or verified")
            return errs
        if s.target_version_id is None or s.state not in OBSERVED:
            errs.append("supersession: a relation needs a target and an observed or verified state")
        if s.target_version_id == self.version_id:
            errs.append("supersession: a version cannot supersede itself")
        return errs

    def _effectivity_errors(self) -> list[str]:
        # A pending or not-stated field carries no value (checked above), so only observed dates are compared.
        errs = []
        for name in ("effective_from", "effective_to"):
            value = getattr(self, name).value
            if _PARTIAL_DATE.fullmatch(value or "") and _date_span(value) is None:
                errs.append(f"{name}: {value!r} is not a calendar date")
        a, b = _date_span(self.effective_from.value), _date_span(self.effective_to.value)
        if a and b and b[1] < a[0]:
            errs.append("effective_to is before effective_from")
        return errs

    def _approval_errors(self, evs: dict[str, Evidence]) -> list[str]:
        errs, appr = [], self.approval_state
        if appr.state in ("approved", "revoked"):
            ev = evs.get(appr.evidence_ref)
            if not self.approval_id or ev is None or ev.authorization_ref != self.approval_id:
                errs.append("approval_id must equal the authorization_ref of the cited authorized evidence")
        elif self.approval_id is not None:
            errs.append("approval_id supplied without authorized approval evidence")
        if appr.state == "revoked" and not any(
                e.kind == "issuing_office_authorization" and e.authorization_ref == self.approval_id
                for e in self.evidence):
            errs.append("revocation must cite the authorization_ref of the approval it revokes")
        if appr.state in ("approved", "revoked"):
            # A revoked record was approved first, so every guard of approval holds for it too.
            label = appr.state
            if self.acquisition_state.state != "verified" or self.verification_state.state != "verified":
                errs.append(f"{label}: approval needs verified acquisition and verified scope")
            if self.issuer.state != "verified" or any(
                    getattr(self, f).state not in ("verified", "not_stated") for f in VOCAB["scope_fields"]):
                errs.append(f"{label}: approval needs issuer and scope/effectivity fields verified or explicitly not stated")
            if self.document_category in VOCAB["proposal_categories"]:
                errs.append(f"{label}: a proposal candidate cannot be approved as a source")
            errs += self._authorization_date_errors(evs)
        return errs

    def _authorization_date_errors(self, evs: dict[str, Evidence]) -> list[str]:
        """The authorization must not be dated before any evidence the approved or revoked state relies on:
        acquisition, verification, and the issuer and every scope field (including a 'not stated' check)."""
        granted_at = [parse_timestamp(e.recorded_at) for e in self.evidence
                      if e.kind == "issuing_office_authorization" and e.authorization_ref == self.approval_id]
        granted = min((t for t in granted_at if t), default=None)
        relied = {name: getattr(self, name).evidence_ref for name in ("acquisition_state", "verification_state")}
        relied.update({name: getattr(self, name).evidence_ref for name in VOCAB["scope_fields"]})
        errs = []
        for name, ref in relied.items():
            basis = evs.get(ref)
            basis_at = parse_timestamp(basis.recorded_at) if basis else None
            if granted and basis_at and granted < basis_at:
                errs.append(f"approval: the authorization is dated before the {name} evidence it relies on")
        return errs


def _supersession_cycle(edges: set[tuple[str, str]]) -> list[str] | None:
    graph: dict[str, set[str]] = {}
    for newer, older in edges:
        graph.setdefault(newer, set()).add(older)
    done: set[str] = set()
    active: list[str] = []

    def visit(node: str):
        if node in active:
            return active[active.index(node):] + [node]
        if node in done:
            return None
        active.append(node)
        for nxt in sorted(graph.get(node, ())):
            found = visit(nxt)
            if found:
                return found
        active.pop()
        done.add(node)
        return None
    for start in sorted(graph):
        found = visit(start)
        if found:
            return found
    return None


def check_register(records: Sequence[SourceDocumentVersion]) -> None:
    """Cross-record rules. Raises ContractError naming every problem."""
    if not records:
        raise ContractError("empty register: nothing was recorded, so nothing can be checked")
    errs: list[str] = []
    ids = [r.version_id for r in records]
    errs += [f"duplicate version_id {v}" for v in sorted(set(ids)) if ids.count(v) > 1]
    by_hash: dict[str, list[str]] = {}
    by_edition: dict[str, set[str]] = {}
    by_ref: dict[str, set[str]] = {}
    for r in records:
        by_hash.setdefault(r.byte_sha256, []).append(r.version_id)
        by_edition.setdefault(r.edition_id, set()).add(r.byte_sha256)
        for e in r.evidence:
            if e.authorization_ref:
                by_ref.setdefault(folded(strip_format(e.authorization_ref)), set()).add(r.version_id)
    errs += [f"same bytes recorded as separate versions {v}; merge locators"
             for v in by_hash.values() if len(v) > 1]
    errs += [f"edition {e} spans different bytes (same filename is not same edition)"
             for e, h in by_edition.items() if len(h) > 1]
    errs += [f"authorization ref {ref} is shared by versions {sorted(v)}; one authorization names one version"
             for ref, v in by_ref.items() if len(v) > 1]
    by_version = {r.version_id: r for r in records}
    edges: set[tuple[str, str]] = set()
    for r in records:
        s = r.supersession
        target = s.target_version_id
        if target is None:
            continue
        other = by_version.get(target)
        if other is None:
            errs.append(f"{r.version_id}: supersession target {target} is not in the register")
            continue
        if other.document_category != r.document_category:
            errs.append(f"{r.version_id}: supersession category mismatch, {r.document_category} and "
                        f"{other.document_category}")
        if other.document_id != r.document_id:
            errs.append(f"{r.version_id}: supersession crosses different documents "
                        f"{r.document_id} and {other.document_id}")
        if other.supersession.relation == "none":
            errs.append(f"{r.version_id}: supersession target {target} does not record the reciprocal relation")
        edges.add((r.version_id, target) if s.relation == "supersedes" else (target, r.version_id))
    successors: dict[str, set[str]] = {}
    for newer, older in edges:
        successors.setdefault(older, set()).add(newer)
    errs += [f"{older} has two successors {sorted(n)}" for older, n in successors.items() if len(n) > 1]
    cycle = _supersession_cycle(edges)
    if cycle:
        errs.append("supersession cycle: " + " -> ".join(cycle))
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
    capability: str = Field(pattern=_TRIMMED)
    campus: str | None
    college: str | None
    program: str | None
    cohort: str | None


class SourceConflict(Contract):
    SCHEMA_VERSION = "bintanong-source-conflict-v1"
    namespace: Literal["institutional"]
    synthetic: bool
    conflict_id: str = Field(pattern=ID_CONFLICT)
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
        _index_evidence(errs, self.evidence)
        if len({(c.version_id, c.span_ref) for c in self.claims}) < 2:
            errs.append("a conflict needs two distinct claims")
        _check_state(errs, self.evidence, "resolution", "conflict_resolution_state",
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
    fact_id: str = Field(pattern=ID_FACT)
    session_id: str = Field(pattern=ID_SESSION)
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
        _index_evidence(errs, self.evidence)
        _check_state(errs, self.evidence, "confirmation", "session_confirmation_state",
                     self.confirmation_state, self.confirmation_evidence_ref)
        if errs:
            raise ValueError("; ".join(errs))
        return self
