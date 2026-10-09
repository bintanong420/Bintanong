"""DecisionOutcome (five-outcome vocabulary), SymbolicResult and the capability registry.

The per-outcome rules come from governance-vocabulary.json (decision.outcomes). An error is
operational and can never become a policy result. A goal is a registered predicate name with bound
inputs; no generated Prolog string is accepted anywhere.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Annotated

from pydantic import Field, model_validator

from .base import VOCAB, Contract, ContractError, Outcome, Record, reject_foreign_ids
from .governance import ID_EDITION
from .runtime import IDENT, BoundInput, PredicateRequest
from .source import SourceSpan

_D = VOCAB["decision"]
_Coverage = Annotated[str, Field(pattern="^(" + "|".join(_D["rule_coverage"]) + ")$")]
_PrereqState = Annotated[str, Field(pattern="^(" + "|".join(_D["prerequisite_rule_states"]) + ")$")]
_Text = Annotated[str, Field(min_length=1)]


class DecisionOutcome(Contract):
    """One scoped structured decision. It implies no official enrollment approval."""

    SCHEMA_VERSION = "bintanong-decision-v1"
    synthetic: bool
    outcome: Outcome()
    # A registered predicate name only: lower-case identifier, so no Prolog syntax (":-", ".", brackets,
    # spaces) can ride in it. Whether the name is registered is the capability registry's question.
    predicate: str = Field(pattern=IDENT, max_length=64)
    predicate_supported: bool
    rule_coverage: _Coverage
    prerequisite_rule_state: _PrereqState | None
    satisfied_conditions: tuple[_Text, ...]
    violated_conditions: tuple[_Text, ...]
    unknown_conditions: tuple[_Text, ...]
    missing_facts: tuple[_Text, ...]
    evidence_refs: tuple[_Text, ...]
    unresolved_conflicts: tuple[_Text, ...]
    error_code: _Text | None

    @model_validator(mode="after")
    def _outcome_rules(self):
        rule = _D["outcomes"][self.outcome]
        errs = []
        if rule["predicate_supported"] != "any" and self.predicate_supported != rule["predicate_supported"]:
            errs.append(f"{self.outcome}: predicate_supported must be {rule['predicate_supported']}")
        if self.rule_coverage not in rule["rule_coverage"]:
            errs.append(f"{self.outcome}: rule_coverage {self.rule_coverage} not permitted")
        prs = self.prerequisite_rule_state
        if rule["prerequisite_rule_state"] == "executable_or_null" and prs is not None \
                and prs not in _D["executable_prerequisite_rule_states"]:
            errs.append(f"{self.outcome}: prerequisite rule state {prs} is not executable")
        errs += [f"{self.outcome}: {k} must not be empty" for k in rule["nonempty"] if not getattr(self, k)]
        errs += [f"{self.outcome}: {k} must be empty" for k in rule["empty"] if getattr(self, k)]
        if (rule["error_code"] == "null") != (self.error_code is None):
            errs.append(f"{self.outcome}: error_code "
                        f"{'must be null' if rule['error_code'] == 'null' else 'is required'}")
        if rule["needs_unknown_reason"]:
            reason = (self.missing_facts or self.unknown_conditions or self.unresolved_conflicts
                      or self.rule_coverage != "verified"
                      or (prs is not None and prs not in _D["executable_prerequisite_rule_states"]))
            if not reason:
                errs.append("unknown: names no missing fact, unknown condition, conflict or coverage gap")
        if errs:
            raise ValueError("; ".join(errs))
        return self


class DecisionScope(Record):
    """What a decision is about: the knowledge release and the source editions its rules come from."""

    knowledge_release_id: str = Field(pattern=r"^release-[a-z0-9-]+$")
    edition_ids: tuple[Annotated[str, Field(pattern=ID_EDITION)], ...] = Field(min_length=1)
    scope_ids: tuple[_Text, ...] = ()

    @model_validator(mode="after")
    def _unique(self):
        if len(set(self.edition_ids)) != len(self.edition_ids):
            raise ValueError("duplicate edition ids in one scope")
        return self


class SymbolicResult(Contract):
    SCHEMA_VERSION = "bintanong-symbolic-result-v1"
    decision: DecisionOutcome
    capability: _Text
    inputs: tuple[BoundInput, ...]
    rule_ids: tuple[Annotated[str, Field(min_length=1)], ...]
    rule_bundle_version: str | None = Field(min_length=1)
    # Required for eligible and ineligible; an unsupported or error result has no scope or rule spans to give.
    scope: DecisionScope | None = None
    rule_spans: tuple[SourceSpan, ...] = ()

    @model_validator(mode="after")
    def _rules(self):
        errs = []
        try:
            reject_foreign_ids({"decision": self.decision.model_dump(mode="json"), "rule_ids": self.rule_ids,
                                "capability": self.capability, "rule_bundle_version": self.rule_bundle_version,
                                "scope": self.scope.model_dump(mode="json") if self.scope else None,
                                "rule_spans": [s.model_dump(mode="json") for s in self.rule_spans],
                                "inputs": [{"name": i.name, "value": i.value} for i in self.inputs]},
                               "institutional")
        except ValueError as exc:
            errs.append(str(exc))
        names = [i.name for i in self.inputs]
        if len(set(names)) != len(names):
            errs.append("duplicate input names")
        if len(set(self.rule_ids)) != len(self.rule_ids):
            errs.append("duplicate rule ids")
        outcome = self.decision.outcome
        if outcome in ("eligible", "ineligible") and not (self.rule_ids and self.rule_bundle_version):
            errs.append(f"{outcome} needs the rule ids and the rule bundle version it was derived from")
        if outcome == "unsupported" and (self.rule_ids or self.rule_bundle_version):
            errs.append("an unsupported predicate cannot cite rules")
        if outcome in ("eligible", "ineligible"):
            if self.scope is None:
                errs.append(f"{outcome} needs its scope (knowledge release and source editions)")
            if not self.rule_spans:
                errs.append(f"{outcome} needs the rule source spans it was derived from")
        if outcome in ("unsupported", "error") and self.rule_spans:
            errs.append(f"{outcome} cannot cite rule source spans")
        for i, s in enumerate(self.rule_spans):
            if not s.is_complete or s.version_id is None:
                errs.append(f"rule span {i} must be anchored, name its source version and carry printed text")
        if errs:
            raise ValueError("; ".join(errs))
        return self


def as_policy_result(result: SymbolicResult) -> str:
    """The outcome as a policy-level result. An error is operational and is never converted."""
    if result.decision.outcome == "error":
        raise ContractError("an operational error cannot be converted to a policy result")
    return result.decision.outcome


# --------------------------------------------------------------------------------------------
# Capability registry: fixed goals with bound inputs
# --------------------------------------------------------------------------------------------
class UnsupportedRequest(ContractError):
    """The request is outside the capability registry; no decision may be invented for it."""


@dataclass(frozen=True)
class Capability:
    name: str
    input_names: tuple[str, ...]


@dataclass(frozen=True)
class FixedGoal:
    predicate: str
    capability: str
    args: tuple[tuple[str, str], ...]


class CapabilityRegistry:
    def __init__(self, capabilities: Mapping[str, Capability]):
        self._capabilities = dict(capabilities)

    def supports(self, predicate: str) -> bool:
        return predicate in self._capabilities

    def goal(self, request: PredicateRequest) -> FixedGoal:
        cap = self._capabilities.get(request.predicate)
        if cap is None:
            raise UnsupportedRequest(f"predicate {request.predicate!r} is not in the capability registry")
        given = {i.name: i.value for i in request.inputs}
        if set(given) != set(cap.input_names):
            raise UnsupportedRequest(f"inputs {sorted(given)} do not match the registered {list(cap.input_names)}")
        return FixedGoal(request.predicate, cap.name, tuple((n, given[n]) for n in cap.input_names))

    def check_result(self, result: SymbolicResult) -> None:
        d = result.decision
        cap = self._capabilities.get(d.predicate)
        if d.outcome == "error":
            return
        if cap is None:
            if d.outcome != "unsupported":
                raise ContractError(f"registry does not know predicate {d.predicate!r}; the outcome must be unsupported")
            return
        if d.outcome == "unsupported":
            raise ContractError(f"registry supports predicate {d.predicate!r}; it cannot be reported unsupported")
        if result.capability != cap.name:
            raise ContractError(f"capability {result.capability!r} differs from the registered {cap.name!r}")
        if {i.name for i in result.inputs} != set(cap.input_names):
            raise ContractError(f"inputs differ from the registered {list(cap.input_names)}")


EMPTY_REGISTRY = CapabilityRegistry({})  # no authorized rules exist yet, so every request is unsupported
