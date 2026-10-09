"""Adapter from the legacy client routing shape to the RoutingDecision contract.

Read-only: it duck-types the legacy object (bintu_client.RoutingDecision: route, confidence, reason)
and imports nothing from the API. The legacy fourth route "Direct" is refused. What Direct means
(greeting? out-of-scope? both?) is an OPEN OWNER DECISION recorded in
docs/decisions/phase-01-consumer-inventory.md; this adapter does not decide it.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import ValidationError

from .base import ContractError
from .runtime import PredicateRequest, RoutingDecision

LEGACY_FIELDS = ("route", "confidence", "reason")

DIRECT_MESSAGE = ("legacy route 'Direct' is not accepted: its meaning is an unresolved OWNER decision "
                  "(see docs/decisions/phase-01-consumer-inventory.md, 'Direct routing discrepancy'). "
                  "It must not carry an institutional claim or be mapped to a control outcome until decided.")


class LegacyRoutingError(ContractError):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(DIRECT_MESSAGE if reason == "legacy_direct_unresolved_owner_decision"
                         else f"{reason}{': ' + detail if detail else ''}")
        self.reason = reason


def from_legacy_routing(legacy: Any, *, predicate_request: PredicateRequest | Mapping | None = None) -> RoutingDecision:
    if isinstance(legacy, Mapping):
        data = dict(legacy)
    elif all(hasattr(legacy, f) for f in LEGACY_FIELDS) and not isinstance(legacy, (str, bytes)):
        data = {f: getattr(legacy, f) for f in LEGACY_FIELDS}
    else:
        raise LegacyRoutingError("legacy_not_a_decision")
    route = data.get("route")
    if route == "Direct":
        raise LegacyRoutingError("legacy_direct_unresolved_owner_decision")
    for field in data:
        if field not in LEGACY_FIELDS:
            raise LegacyRoutingError(f"legacy_unknown_field:{field}")
    for field in LEGACY_FIELDS:
        if field not in data:
            raise LegacyRoutingError(f"legacy_missing_field:{field}")
    if route not in ("RAG", "Hybrid", "Symbolic"):
        raise LegacyRoutingError("legacy_unknown_route", str(route))
    if route in ("Symbolic", "Hybrid") and predicate_request is None:
        raise LegacyRoutingError("legacy_route_needs_predicate_request",
                                 "the legacy shape has no typed predicate; supply one from a validated source")
    try:
        return RoutingDecision.parse({
            "schema_version": RoutingDecision.SCHEMA_VERSION, "route": route, "control": None,
            "confidence": data["confidence"],
            "predicate_request": (predicate_request.model_dump(mode="json")
                                  if isinstance(predicate_request, PredicateRequest) else predicate_request),
            "required_facts": [], "missing_facts": [], "reason": data["reason"]})
    except (ValidationError, ContractError) as exc:
        raise LegacyRoutingError("legacy_invalid", str(exc)[:200]) from exc
