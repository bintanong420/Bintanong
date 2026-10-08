"""NormalizedQuery, RoutingDecision and RetrievalResult.

A routing decision has either a route (RAG, Hybrid or Symbolic) or a control outcome, never both and
never neither, and is validated before dispatch. There is no "Direct" route here; the legacy value is
handled only by routing_adapter, which refuses it until the owner decides what it means. A symbolic
goal is a registered predicate name with bound inputs, never generated Prolog text. A bound input is data;
rendering must quote it (see `prolog_quote`), because the value itself may be any printable text. A retrieval result
carries the register versions its chunks cite and checks every chunk against its version.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Annotated, Literal

from pydantic import AfterValidator, Field, model_validator

from .base import (VOCAB, Contract, ContractError, Control, Record, Route, folded, is_pinned_revision,
                   namespace_of, reject_foreign_ids)
from .governance import ID_FACT, SourceDocumentVersion, check_register
from .source import Chunk, check_chunk_binding

_Finite = Annotated[float, Field(allow_inf_nan=False)]
_Name = Annotated[str, Field(min_length=1)]
IDENT = r"^[a-z][a-z0-9_]*$"
# A bound value is DATA: any printable text of at most BOUND_VALUE_MAX characters, so real course codes
# such as "HBO", "P2101" or "GE- Elect: EM" are values, not syntax. Nothing is generated or executed here;
# rendering must quote: the fixed renderer turns a value into Prolog only through `prolog_quote`, which
# always emits one single-quoted atom. Refused: empty text, padding or repeated spaces, control characters
# (including NUL and newlines), Unicode format, separator and unassigned characters, and over-long text.
# The cap is an owner-reviewable default.
BOUND_VALUE_MAX = 128
_REFUSED_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Co", "Cn", "Zl", "Zp"})


def _unprintable(value: str) -> str | None:
    """Why `value` is not printable data, or None. A space is the only separator character allowed."""
    if not value:
        return "empty"
    for ch in value:
        cat = unicodedata.category(ch)
        if cat in _REFUSED_CATEGORIES or (cat == "Zs" and ch != " "):
            return f"control, format or separator character U+{ord(ch):04X}"
    return None


def _bound_value(value: str) -> str:
    why = _unprintable(value)
    if why:
        raise ValueError(f"a bound value must be printable text: {why}")
    if value != value.strip() or "  " in value:
        raise ValueError("a bound value carries no padding or repeated spaces")
    return value


def prolog_quote(value: str) -> str:
    """The one way a bound value may become Prolog text: a single-quoted atom, backslash and quote escaped.
    Refuses empty text and control or format characters. No Prolog is generated or run anywhere else."""
    if not isinstance(value, str):
        raise ContractError(f"cannot quote a {type(value).__name__}")
    why = _unprintable(value)
    if why:
        raise ContractError(f"cannot quote the value as a Prolog atom: {why} (printable text only)")
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


# --------------------------------------------------------------------------------------------
# Typed goal pieces (shared with SymbolicResult)
# --------------------------------------------------------------------------------------------
class BoundInput(Record):
    name: str = Field(pattern=IDENT)
    value: Annotated[str, Field(min_length=1, max_length=BOUND_VALUE_MAX), AfterValidator(_bound_value)]
    fact_ref: str | None = Field(pattern=ID_FACT)


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
_MARKERS = VOCAB["query_markers"]
_NEGATIONS = frozenset(_MARKERS["negations"])
_TIME_PHRASES = re.compile(
    r"(?<![a-z0-9'])(" + "|".join(re.escape(p) for p in sorted(_MARKERS["time_qualifiers"], key=len, reverse=True))
    + r")(?![a-z0-9'])")


def negation_tokens(text: str) -> set[str]:
    """Negation words of the vocabulary's default list found in `text`; a contraction in n't counts as 'not'."""
    found = set()
    for word in re.findall(r"'?[a-z0-9]+(?:'[a-z0-9]+)*", folded(text).replace("’", "'")):
        word = word.lstrip("'")
        if word.endswith("n't"):
            found.add("not")
        elif word in _NEGATIONS:
            found.add(word)
    return found


def time_phrases(text: str) -> set[str]:
    return set(_TIME_PHRASES.findall(folded(text).replace("’", "'")))


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
    session_fact_refs: tuple[Annotated[str, Field(pattern=ID_FACT)], ...]

    @model_validator(mode="after")
    def _rules(self):
        errs = []
        low = self.normalized_text.casefold()
        errs += [f"normalization dropped {w!r}" for w in (*self.negations, *self.time_qualifiers)
                 if w.casefold() not in low]
        # The declared lists can be empty or short, so the original text decides which markers must survive.
        for label, found in (("negation", negation_tokens), ("time qualifier", time_phrases)):
            before, after = found(self.original_text), found(self.normalized_text)
            errs += [f"normalization dropped the {label} {w!r} found in the original" for w in sorted(before - after)]
            errs += [f"normalization added the {label} {w!r} that the original does not contain" for w in sorted(after - before)]
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
    route: Route() | None
    control: Control() | None
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
        if not self.reason.strip():
            errs.append("a routing decision needs a reason, not blank text")
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
        if not is_pinned_revision(self.embedding_model_revision):
            raise ValueError("embedding_model_revision must be pinned: a full lowercase commit (40 hex) or digest (64 hex)")
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
            ids = loc.cell_ids or loc.item_ids or loc.section_path or ((loc.ref,) if loc.ref else ())
            out.append(f"{s.byte_sha256}#p{s.page}:{loc.kind}:{','.join(ids)}")
        return tuple(out)

    @model_validator(mode="after")
    def _bound(self):
        c = self.chunk
        if not c.anchored or None in (c.version_id, c.edition_id, c.document_id):
            raise ValueError("a retrieved chunk must be anchored and bound to a source version and edition")
        if c.source_text is None:
            raise ValueError("a retrieved chunk must carry printed text in complete spans; "
                             "a layout chunk without printed text is not citable evidence")
        return self


class RetrievalResult(Contract):
    SCHEMA_VERSION = "bintanong-retrieval-result-v1"
    knowledge_release_id: str = Field(pattern=r"^release-[a-z0-9-]+$")
    items: tuple[RetrievedChunk, ...]
    versions: tuple[SourceDocumentVersion, ...]
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
        errs += self._identity_errors()
        errs += self._register_errors()
        if len({i.chunk.chunker_version for i in items}) > 1:
            errs.append("chunks from different chunker versions")
        if errs:
            raise ValueError("; ".join(errs))
        return self

    def _identity_errors(self) -> list[str]:
        # The same bytes under two editions or versions, and one edition over different bytes, are refused by
        # check_register on the carried versions (every chunk must match its version). Two editions of one
        # document are legal in a register, so that case is checked here.
        by_document: dict[str, set[str]] = {}
        for i in self.items:
            c = i.chunk
            by_document.setdefault(c.document_id, set()).add(c.byte_sha256)
        return [f"document {d} appears with more than one edition" for d, h in by_document.items() if len(h) > 1]

    def _register_errors(self) -> list[str]:
        errs = []
        if self.versions:
            try:
                check_register(self.versions)
            except ContractError as exc:
                errs.append(str(exc))
        by_id = {v.version_id: v for v in self.versions}
        used = set()
        for i in self.items:
            version = by_id.get(i.chunk.version_id)
            if version is None:
                errs.append(f"chunk {i.chunk.chunk_id[:8]} cites version {i.chunk.version_id} that is not in the result's versions")
                continue
            used.add(version.version_id)
            try:
                check_chunk_binding(i.chunk, version)
            except ContractError as exc:
                errs.append(f"chunk {i.chunk.chunk_id[:8]} does not match its register version: {exc}")
        errs += [f"version {v} is carried but no chunk cites it" for v in sorted(set(by_id) - used)]
        return errs
