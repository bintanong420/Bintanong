"""NormalizedQuery, RoutingDecision and RetrievalResult.

A routing decision has either a route (RAG, Hybrid or Symbolic) or a control outcome, never both and
never neither, and is validated before dispatch. There is no "Direct" route here; the legacy value is
handled only by routing_adapter, which refuses it until the owner decides what it means. A symbolic
goal is a registered predicate name with bound inputs, never generated Prolog text.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, model_validator

from .base import Contract, ContractError, Record, namespace_of, reject_foreign_ids
from .embedding import FLOATING_REFS
from .source import Chunk

ROUTES = ("RAG", "Hybrid", "Symbolic")
CONTROLS = ("clarify", "greeting", "unsupported_scope", "evidence_unavailable")
_Finite = Annotated[float, Field(allow_inf_nan=False)]
_Name = Annotated[str, Field(min_length=1)]
IDENT = r"^[a-z][a-z0-9_]*$"
# Bound values: letters, digits, space, underscore, slash, hyphen, and one decimal part. No quotes,
# parentheses, commas, semicolons, colons or full stops, so a value cannot carry Prolog syntax.
BOUND_VALUE = r"^[A-Za-z0-9 _/-]+(\.[0-9]+)?$"


# --------------------------------------------------------------------------------------------
# Typed goal pieces (shared with SymbolicResult)
# --------------------------------------------------------------------------------------------
class BoundInput(Record):
    name: str = Field(pattern=IDENT)
    value: str = Field(pattern=BOUND_VALUE, max_length=64)
    fact_ref: str | None = Field(pattern=r"^fact-[a-z0-9-]+$")


class PredicateRequest(Record):
    predicate: str = Field(pattern=IDENT, max_length=64)
    inputs: tuple[BoundInput, ...]

    @model_validator(mode="after")
    def _unique(self):
        names = [i.name for i in self.inputs]
        if len(set(names)) != len(names):
            raise ValueError("duplicate input names")
        return self


# --------------------------------------------------------------------------------------------
# NormalizedQuery
# --------------------------------------------------------------------------------------------
class ResolvedEntity(Record):
    kind: _Name
    value: _Name
    source_ref: str | None

    @model_validator(mode="after")
    def _institutional_only(self):
        if self.source_ref is not None and namespace_of(self.source_ref) != "institutional":
            raise ValueError("an entity may cite only an institutional source id")
        return self


class NormalizedQuery(Contract):
    """Minimal normalization. Negations and time qualifiers must survive; user assertions are not policy."""

    SCHEMA_VERSION = "bintanong-normalized-query-v1"
    original_text: _Name
    normalized_text: _Name
    language_hints: tuple[Annotated[str, Field(pattern=r"^[a-z]{2,8}$")], ...]
    intent: str | None = Field(min_length=1)
    entities: tuple[ResolvedEntity, ...]
    ambiguities: tuple[_Name, ...]
    negations: tuple[_Name, ...]
    time_qualifiers: tuple[_Name, ...]
    session_fact_refs: tuple[Annotated[str, Field(pattern=r"^fact-[a-z0-9-]+$")], ...]

    @model_validator(mode="after")
    def _rules(self):
        errs = []
        low = self.normalized_text.casefold()
        errs += [f"normalization dropped {w!r}" for w in (*self.negations, *self.time_qualifiers)
                 if w.casefold() not in low]
        if len(set(self.session_fact_refs)) != len(self.session_fact_refs):
            errs.append("duplicate session fact references")
        if errs:
            raise ValueError("; ".join(errs))
        return self


# --------------------------------------------------------------------------------------------
# RoutingDecision
# --------------------------------------------------------------------------------------------
class RoutingDecision(Contract):
    SCHEMA_VERSION = "bintanong-routing-decision-v1"
    route: Literal["RAG", "Hybrid", "Symbolic"] | None
    control: Literal["clarify", "greeting", "unsupported_scope", "evidence_unavailable"] | None
    confidence: float | None = Field(ge=0.0, le=1.0)
    predicate_request: PredicateRequest | None
    required_facts: tuple[_Name, ...]
    missing_facts: tuple[_Name, ...]
    reason: str = Field(min_length=1, max_length=240)

    @property
    def dispatchable(self) -> bool:
        return self.route is not None

    @model_validator(mode="after")
    def _rules(self):
        errs = []
        if (self.route is None) == (self.control is None):
            errs.append("exactly one of route and control must be set")
        if not set(self.missing_facts) <= set(self.required_facts):
            errs.append("missing_facts must be a subset of required_facts")
        if self.route is not None:
            if self.route == "RAG" and self.predicate_request is not None:
                errs.append("a RAG route carries no symbolic predicate request")
            if self.route in ("Symbolic", "Hybrid") and self.predicate_request is None:
                errs.append(f"a {self.route} route needs a typed predicate request")
            if self.missing_facts:
                errs.append("a route with missing facts cannot be dispatched; use control 'clarify'")
        elif self.control != "clarify":
            if self.predicate_request is not None or self.required_facts or self.missing_facts:
                errs.append(f"control {self.control!r} carries no predicate request or facts")
        if errs:
            raise ValueError("; ".join(errs))
        return self


def dispatch_route(decision: RoutingDecision) -> str:
    """The route to dispatch, or ContractError when the decision is a control outcome."""
    if decision.route is None:
        raise ContractError(f"cannot dispatch: control outcome {decision.control!r} has no route")
    return decision.route


# --------------------------------------------------------------------------------------------
# RetrievalResult
# --------------------------------------------------------------------------------------------
class RetrievalConfig(Record):
    top_k: int = Field(ge=1)
    score_metric: _Name
    min_score: _Finite | None
    embedding_model_id: _Name
    embedding_model_revision: _Name

    @model_validator(mode="after")
    def _pinned(self):
        if self.embedding_model_revision.lower() in FLOATING_REFS:
            raise ValueError("embedding_model_revision must be pinned")
        return self


class RetrievedChunk(Record):
    rank: int = Field(ge=1)
    score: _Finite
    knowledge_release_id: str = Field(pattern=r"^release-[a-z0-9-]+$")
    chunk: Chunk

    @property
    def source_locators(self) -> tuple[str, ...]:
        out = []
        for s in self.chunk.spans:
            loc = s.locator
            ids = loc.cell_ids or loc.item_ids or ((loc.ref,) if loc.ref else ())
            out.append(f"{s.byte_sha256}#p{s.page}:{loc.kind}:{','.join(ids)}")
        return tuple(out)

    @model_validator(mode="after")
    def _bound(self):
        c = self.chunk
        if not c.anchored or None in (c.version_id, c.edition_id, c.document_id):
            raise ValueError("a retrieved chunk must be anchored and bound to a source version and edition")
        return self


class RetrievalResult(Contract):
    SCHEMA_VERSION = "bintanong-retrieval-result-v1"
    knowledge_release_id: str = Field(pattern=r"^release-[a-z0-9-]+$")
    items: tuple[RetrievedChunk, ...]
    coverage_status: Literal["sufficient", "partial", "none"]
    config: RetrievalConfig

    @model_validator(mode="after")
    def _rules(self):
        errs = []
        try:
            reject_foreign_ids(self, "institutional")
        except ValueError as exc:
            errs.append(str(exc))
        items = self.items
        if (self.coverage_status == "none") != (not items):
            errs.append("coverage_status 'none' exactly when there are no chunks")
        if len(items) > self.config.top_k:
            errs.append("more chunks than top_k")
        if [i.rank for i in items] != list(range(1, len(items) + 1)):
            errs.append("ranks must be 1..n in order")
        if any(a.score < b.score for a, b in zip(items, items[1:])):
            errs.append("items must be ordered by non-increasing score")
        if self.config.min_score is not None and any(i.score < self.config.min_score for i in items):
            errs.append("an item scores below the configured minimum")
        if any(i.knowledge_release_id != self.knowledge_release_id for i in items):
            errs.append("items from a different knowledge release")
        ids = [i.chunk.chunk_id for i in items]
        if len(set(ids)) != len(ids):
            errs.append("duplicate chunk in one result")
        editions: dict[str, set[str]] = {}
        for i in items:
            editions.setdefault(i.chunk.document_id, set()).add(i.chunk.byte_sha256)
        errs += [f"document {d} appears with more than one edition" for d, h in editions.items() if len(h) > 1]
        if len({i.chunk.chunker_version for i in items}) > 1:
            errs.append("chunks from different chunker versions")
        if errs:
            raise ValueError("; ".join(errs))
        return self
