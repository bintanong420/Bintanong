"""EvidenceBundle and AnswerEnvelope.

The bundle gathers what an answer may rest on for one request: retrieved institutional passages, a
symbolic result, private session-only facts, source conflicts and the claims those permit. Private
facts stay in their own namespace and are never institutional evidence. The envelope is the answer
as sent; its status must follow the structured decision, and unknown, unsupported and error never
become an approval or a denial.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, model_validator

from .base import Contract, ContractError, Record, foreign_ids
from .governance import SHA256, ID_VER, SessionFact, SourceConflict
from .runtime import RetrievalResult
from .symbolic import DecisionOutcome, SymbolicResult

REQUEST_ID = r"^req-[a-z0-9-]+$"
# Claim names. Each decision claim must match the symbolic outcome; none is an enrollment approval.
CLAIMS = ("policy_passage", "decision_eligible", "decision_ineligible", "unknown_explanation",
          "abstention", "error_report")
_ALLOWED_BY_OUTCOME = {
    "eligible": {"decision_eligible", "policy_passage"},
    "ineligible": {"decision_ineligible", "policy_passage"},
    "unknown": {"unknown_explanation", "abstention"},
    "unsupported": {"abstention"},
    "error": {"error_report"},
}
_Text = Annotated[str, Field(min_length=1)]


class EvidenceBundle(Contract):
    SCHEMA_VERSION = "bintanong-evidence-bundle-v1"
    request_id: str = Field(pattern=REQUEST_ID)
    route: Literal["RAG", "Hybrid", "Symbolic"]
    knowledge_release_id: str = Field(pattern=r"^release-[a-z0-9-]+$")
    retrieval: RetrievalResult | None
    symbolic: SymbolicResult | None
    session_facts: tuple[SessionFact, ...]
    conflicts: tuple[SourceConflict, ...]
    permitted_claims: tuple[str, ...]

    @model_validator(mode="after")
    def _rules(self):
        errs: list[str] = []
        sym, ret, claims = self.symbolic, self.retrieval, self.permitted_claims
        if self.route == "RAG" and (ret is None or sym is not None):
            errs.append("a RAG bundle needs retrieval and carries no symbolic result")
        if self.route == "Symbolic" and sym is None:
            errs.append("a Symbolic bundle needs a symbolic result")
        if self.route == "Hybrid" and (ret is None or sym is None):
            errs.append("a Hybrid bundle needs both retrieval and a symbolic result; a partial bundle is refused")
        if ret is not None and ret.knowledge_release_id != self.knowledge_release_id:
            errs.append("retrieval comes from a different knowledge release (stale or mixed)")
        bad = [c for c in claims if c not in CLAIMS]
        if bad:
            errs.append(f"unknown claim(s) {bad}")
        if len(set(claims)) != len(claims):
            errs.append("duplicate claims")
        facts = {f.fact_id: f for f in self.session_facts}
        if len(facts) != len(self.session_facts):
            errs.append("duplicate session fact ids")

        if sym is not None:
            errs += self._symbolic_rules(sym, facts)
        elif set(claims) - {"policy_passage", "abstention"}:
            errs.append("without a symbolic result only policy_passage and abstention may be claimed")
        if "policy_passage" in claims and (ret is None or not ret.items):
            errs.append("policy_passage needs retrieved passages")
        if "abstention" in claims and len(claims) > 1 and sym is None:
            errs.append("abstention cannot be combined with other claims")

        institutional = {"retrieval": ret.model_dump(mode="json") if ret else None,
                         "conflicts": [c.model_dump(mode="json") for c in self.conflicts],
                         "symbolic": None if sym is None else {
                             "decision": sym.decision.model_dump(mode="json"), "rule_ids": list(sym.rule_ids),
                             "capability": sym.capability, "rule_bundle_version": sym.rule_bundle_version}}
        leaked = foreign_ids(institutional, "institutional")
        if leaked:
            errs.append(f"private id(s) {sorted(set(leaked))} appear in institutional evidence")
        if errs:
            raise ValueError("; ".join(errs))
        return self

    def _symbolic_rules(self, sym: SymbolicResult, facts: dict[str, SessionFact]) -> list[str]:
        errs = []
        d, claims = sym.decision, set(self.permitted_claims)
        outcome = d.outcome
        extra = claims - _ALLOWED_BY_OUTCOME[outcome]
        if extra:
            errs.append(f"claims {sorted(extra)} are not permitted for a {outcome} symbolic outcome")
        if outcome == "error" and len(claims) > 1:
            errs.append("an error outcome permits only an error report")
        if d.synthetic and claims - {"abstention", "error_report"}:
            errs.append("a synthetic decision establishes no claim")
        for i in sym.inputs:
            if i.fact_ref is None:
                continue
            fact = facts.get(i.fact_ref)
            if fact is None:
                errs.append(f"input {i.name} cites session fact {i.fact_ref} that is not in the bundle")
            elif fact.confirmation_state == "user_rejected":
                errs.append(f"input {i.name} rests on a fact the student rejected")
            elif outcome in ("eligible", "ineligible") and fact.confirmation_state != "user_confirmed":
                errs.append(f"a {outcome} decision cannot rest on the unconfirmed fact {i.fact_ref}")
        by_id = {c.conflict_id: c for c in self.conflicts}
        errs += [f"decision cites conflict {c} that is not in the bundle" for c in d.unresolved_conflicts
                 if c not in by_id]
        blocking = {c.conflict_id for c in self.conflicts
                    if c.resolution_state != "resolved" and c.affected_scope.capability == sym.capability}
        if blocking and outcome in ("eligible", "ineligible"):
            errs.append(f"an unresolved conflict blocks capability {sym.capability!r}; a {outcome} decision is refused")
        if blocking and outcome == "unknown" and not blocking <= set(d.unresolved_conflicts):
            errs.append("an unknown outcome must list the blocking conflict(s)")
        return errs


# --------------------------------------------------------------------------------------------
# AnswerEnvelope
# --------------------------------------------------------------------------------------------
class Citation(Record):
    chunk_id: str = Field(pattern=SHA256)
    byte_sha256: str = Field(pattern=SHA256)
    version_id: str = Field(pattern=ID_VER)
    page: int = Field(ge=1)
    locator_ref: _Text


class ValidationResult(Record):
    passed: bool
    checks: tuple[_Text, ...]
    failures: tuple[_Text, ...]

    @model_validator(mode="after")
    def _consistent(self):
        if self.passed == bool(self.failures):
            raise ValueError("validation passed exactly when it lists no failure")
        return self


_STATUS_OUTCOMES = {
    "answered": {"eligible", "ineligible"},
    "clarification_needed": {"unknown"},
    "abstained": {"unknown", "unsupported"},
    "error": {"error"},
}
_STATUS_CLAIMS = {"clarification_needed": {"unknown_explanation", "abstention"},
                  "abstained": {"abstention", "unknown_explanation"}, "error": {"error_report"}}


class AnswerEnvelope(Contract):
    SCHEMA_VERSION = "bintanong-answer-envelope-v1"
    request_id: str = Field(pattern=REQUEST_ID)
    status: Literal["answered", "abstained", "clarification_needed", "error"]
    language: Literal["en", "tl", "taglish"]
    text: _Text
    route: Literal["RAG", "Hybrid", "Symbolic"] | None
    decision: DecisionOutcome | None
    citations: tuple[Citation, ...]
    validation: ValidationResult

    @model_validator(mode="after")
    def _rules(self):
        errs = []
        d = self.decision
        if d is not None and d.outcome not in _STATUS_OUTCOMES[self.status]:
            errs.append(f"status {self.status!r} cannot carry a {d.outcome!r} decision")
        if d is not None and self.route not in ("Symbolic", "Hybrid"):
            errs.append("a structured decision needs a Symbolic or Hybrid route")
        if self.route == "RAG" and d is not None:
            errs.append("a RAG answer carries no structured decision")
        keys = [(c.chunk_id, c.locator_ref) for c in self.citations]
        if len(set(keys)) != len(keys):
            errs.append("duplicate citation")
        if self.status == "answered":
            if not self.validation.passed:
                errs.append("an answer needs a passed validation")
            if self.route is None:
                errs.append("an answer needs a route")
            if self.route in ("Symbolic", "Hybrid") and d is None:
                errs.append(f"a {self.route} answer needs its symbolic decision; passages alone cannot stand in")
            if self.route == "RAG" and not self.citations:
                errs.append("a RAG answer needs at least one citation")
        if self.status == "error":
            if self.citations:
                errs.append("an error cites nothing")
            if self.validation.passed:
                errs.append("an error cannot carry a passed validation")
        leaked = foreign_ids([c.model_dump(mode="json") for c in self.citations], "institutional")
        if leaked:
            errs.append(f"private id(s) {sorted(set(leaked))} appear in citations")
        if errs:
            raise ValueError("; ".join(errs))
        return self


def check_envelope_against_bundle(envelope: AnswerEnvelope, bundle: EvidenceBundle) -> None:
    errs = []
    if envelope.request_id != bundle.request_id:
        errs.append("request id differs from the bundle")
    if envelope.route is not None and envelope.route != bundle.route:
        errs.append(f"route {envelope.route} differs from the bundle route {bundle.route}")
    sym = bundle.symbolic
    if envelope.decision is not None and (sym is None or envelope.decision != sym.decision):
        errs.append("decision differs from the bundle's symbolic decision")
    if envelope.status == "answered" and sym is not None and envelope.decision is None:
        errs.append("an answer must carry the bundle's symbolic decision")
    claims = set(bundle.permitted_claims)
    retrieved = {}
    for item in (bundle.retrieval.items if bundle.retrieval else ()):
        c = item.chunk
        retrieved[c.chunk_id] = c
    for cite in envelope.citations:
        chunk = retrieved.get(cite.chunk_id)
        if chunk is None:
            errs.append(f"citation {cite.chunk_id[:8]} was not retrieved")
            continue
        ids = {i for s in chunk.spans for i in (*s.locator.cell_ids, *s.locator.item_ids, s.locator.ref or "")}
        if (cite.byte_sha256, cite.version_id) != (chunk.byte_sha256, chunk.version_id):
            errs.append(f"citation {cite.chunk_id[:8]} names other bytes or version than the chunk")
        elif cite.page not in {s.page for s in chunk.spans} or cite.locator_ref not in ids:
            errs.append(f"citation {cite.chunk_id[:8]} names a page or locator the chunk does not have")
    if envelope.status == "answered":
        if envelope.decision is not None and f"decision_{envelope.decision.outcome}" not in claims:
            errs.append(f"permitted claims do not include decision_{envelope.decision.outcome}")
        if envelope.citations and "policy_passage" not in claims:
            errs.append("permitted claims do not include policy_passage")
    elif not claims & _STATUS_CLAIMS[envelope.status]:
        errs.append(f"permitted claims do not allow status {envelope.status!r}")
    if errs:
        raise ContractError("; ".join(errs))
