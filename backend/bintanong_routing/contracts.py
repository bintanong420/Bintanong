"""Strict routing data. Model proposals never carry trusted IDs or executable goals."""
from __future__ import annotations

import unicodedata
from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Contract, Control, Record, Route

Text = Annotated[str, Field(min_length=1, max_length=240)]
Identifier = Annotated[str, Field(min_length=1, max_length=128, pattern=r'^[a-z][a-z0-9_-]*$')]
Kind = Literal['program', 'curriculum', 'course']
# A student's year/semester words ("first year, second sem"); read by the host, never a catalog entity.
MentionKind = Literal['program', 'curriculum', 'course', 'term']
TERM_OPERATIONS = ('list_term_courses',)  # operations whose target is a term mention
State = Literal['passed', 'failed', 'enrolled', 'not_enrolled']
Language = Literal['en', 'fil', 'taglish', 'unknown']


def prepare_query(text: str) -> str:
    """NFC and whitespace only; offsets elsewhere always refer to the original."""
    if not isinstance(text, str) or not text or len(text) > 8192:
        raise ValueError('invalid_query')
    if any(unicodedata.category(c) in {'Cs', 'Cf'} or
           (unicodedata.category(c) == 'Cc' and c not in '\t\r\n') for c in text):
        raise ValueError('invalid_query')
    if len(text.encode('utf-8')) > 16384:
        raise ValueError('query_too_large')
    normalized = ' '.join(unicodedata.normalize('NFC', text).split())
    if not normalized:
        raise ValueError('empty_query')
    return normalized


class ScopedFact(Record):
    """Trusted caller's scoped user assertion; not an institutional record."""
    fact_id: str = Field(pattern=r'^fact-[a-z0-9-]+$')
    session_id: str = Field(pattern=r'^sess-[a-z0-9-]+$')
    program_id: Identifier
    curriculum_id: Identifier
    course_id: Identifier
    state: State


class ConversationContext(Record):
    """Ids the previous answered turn used (master 23); session memory only, never text or grades."""
    program_id: Identifier | None = None
    curriculum_id: Identifier | None = None
    course_id: Identifier | None = None
    subject_id: str | None = Field(default=None, pattern=r'^[a-z][a-z0-9_]*$', max_length=64)


class RequestContext(Record):
    """Must come from the owning application, not directly from model output."""
    session_id: str = Field(pattern=r'^sess-[a-z0-9-]+$')
    request_id: str = Field(pattern=r'^req-[a-z0-9-]+$', max_length=128)
    program_id: Identifier | None = None
    curriculum_id: Identifier | None = None
    facts: tuple[ScopedFact, ...] = Field(default=(), max_length=256)
    conversation: ConversationContext | None = None

    @model_validator(mode='after')
    def _ownership(self):
        if len({f.fact_id for f in self.facts}) != len(self.facts):
            raise ValueError('duplicate_fact_id')
        for f in self.facts:
            if f.session_id != self.session_id:
                raise ValueError('foreign_session_fact')
            if f.program_id != self.program_id or f.curriculum_id != self.curriculum_id:
                raise ValueError('fact_scope_mismatch')
        return self


class Quote(Record):
    text: str = Field(min_length=1, max_length=4096)
    start: int = Field(ge=0, le=8192)
    end: int = Field(ge=1, le=8192)

    @model_validator(mode='after')
    def _length(self):
        if self.end - self.start != len(self.text):
            raise ValueError('invalid_quote_length')
        return self


class Mention(Quote):
    kind: MentionKind


class Claim(Quote):
    entity: int = Field(ge=0, le=31)
    state: State
    mode: Literal['asserted', 'hypothetical', 'reported']


class Operation(Record):
    name: str = Field(pattern=r'^[a-z][a-z0-9_]*$', max_length=64)
    target: int = Field(ge=0, le=31)


TopicClaim = Annotated[str, Field(min_length=1, max_length=256)]
MAX_TOPIC_FIELDS = 64


class NotStatedCue(Record):
    """Owner-approved phrases (23 Oct 2026) showing a part asks for a fact the source does not state."""
    claim: TopicClaim
    phrases: tuple[Annotated[str, Field(min_length=2, max_length=64)], ...] = Field(min_length=1, max_length=32)


class DocumentTopic(Record):
    """One release-supplied retrieval subject and its reviewed claim strings."""
    subject_id: str = Field(pattern=r'^[a-z][a-z0-9_]*$', max_length=64)
    claims: tuple[TopicClaim, ...] = Field(min_length=1, max_length=64)
    # Exact names of fields already bound to each reviewed claim; routing context only.
    claim_fields: dict[TopicClaim, tuple[Annotated[str, Field(min_length=1, max_length=256)], ...]] = Field(
        default_factory=dict, max_length=64)
    # Reviewed labels/clauses: routing context, never a new answerable claim.
    source_context: tuple[Annotated[str, Field(min_length=1, max_length=1024)], ...] = Field(default=(), max_length=4)
    # Candidate-only, source-bound routing labels/columns; absent metadata preserves old serialization.
    source_labels: tuple[Annotated[str, Field(min_length=1, max_length=1024)], ...] = Field(
        default=(), max_length=4, exclude_if=lambda value: not value)
    claim_context: dict[TopicClaim, dict[Annotated[str, Field(min_length=1, max_length=256)],
        Annotated[str, Field(min_length=1, max_length=1024)]]] = Field(
            default_factory=dict, max_length=64, exclude_if=lambda value: not value)
    # Verbatim opening of a reviewed body field: routing context only, never an answerable claim.
    source_opening: Annotated[str, Field(min_length=1, max_length=256)] | None = Field(
        default=None, exclude_if=lambda value: value is None)
    # Verbatim printed row names (e.g. a penalty table's causes): selector routing context only.
    source_items: tuple[Annotated[str, Field(min_length=1, max_length=64)], ...] = Field(
        default=(), max_length=48, exclude_if=lambda value: not value)
    # Owner-approved topic family (28 Oct 2026): selecting one member offers all of them.
    family: str | None = Field(default=None, pattern=r'^[a-z][a-z0-9_]*$', max_length=64,
        exclude_if=lambda value: value is None)
    # Recorded source limits: facts the source does not state (selecting one withholds).
    not_stated: tuple[TopicClaim, ...] = Field(default=(), max_length=16)
    # Host-only (never shown to the model): phrases in a part that add a not-stated fact to it.
    cues: tuple[NotStatedCue, ...] = Field(default=(), max_length=16)

    @model_validator(mode='after')
    def _cues(self):
        if any(claim not in self.claims or not fields or len(fields)>MAX_TOPIC_FIELDS or len(set(fields))!=len(fields)
               for claim,fields in self.claim_fields.items()):
            raise ValueError('context_requires_selectable_claim')
        if any(claim not in self.claims or not values or len(values)>8
               or not set(values) <= set(self.claim_fields.get(claim, ()))
               for claim,values in self.claim_context.items()):
            raise ValueError('context_requires_bound_fields')
        if any(c.claim not in self.not_stated for c in self.cues):
            raise ValueError('cue_requires_not_stated_claim')
        return self


class RequestPart(Quote):
    part_id: str = Field(pattern=r'^r[1-8]$')
    evidence_need: Literal['document', 'structured', 'unknown']
    operation_indices: tuple[Annotated[int, Field(ge=0, le=3)], ...] = Field(max_length=4)
    # Research real-data mode only: a menu subject and its reviewed claims.
    subject_id: str | None = Field(default=None, pattern=r'^[a-z][a-z0-9_]*$', max_length=64)
    requested_claims: tuple[TopicClaim, ...] = Field(default=(), max_length=8)
    # The printed detail a document part asks for (owner 28 Oct 2026: answer only what was asked).
    detail: Literal['whole', 'requirements', 'fees', 'processing_time', 'specific'] = 'whole'

    @model_validator(mode='after')
    def _operations(self):
        if not self.text.strip() or len(set(self.operation_indices)) != len(self.operation_indices):
            raise ValueError('invalid_part')
        if self.evidence_need != 'structured' and self.operation_indices:
            raise ValueError('only_structured_parts_reference_operations')
        if self.evidence_need != 'document' and (self.subject_id or self.requested_claims or self.detail != 'whole'):
            raise ValueError('only_document_parts_carry_topics')
        if (self.subject_id is None) != (not self.requested_claims):
            raise ValueError('topic_requires_claims')
        return self


class Interpretation(Contract):
    SCHEMA_VERSION = 'bintanong-interpretation-v2'
    language: Language
    audience: Literal['undergraduate', 'excluded', 'unrelated', 'unknown']
    intent: Text
    mentions: tuple[Mention, ...] = Field(max_length=32)
    claims: tuple[Claim, ...] = Field(max_length=32)
    operations: tuple[Operation, ...] = Field(max_length=4)
    parts: tuple[RequestPart, ...] = Field(max_length=8)
    route: Route() | None
    control: Control() | None
    ambiguities: tuple[Text, ...] = Field(max_length=16, description=
        'Only unresolved questions needed to interpret the request. Normally empty. '
        'Never put a route explanation or a need to retrieve documents here.')
    reason: Text
    # Words that refer back to the previous turn's course ("its"); the host supplies the course.
    context_reference: Quote | None = None

    @model_validator(mode='after')
    def _structure(self):
        if (self.route is None) == (self.control is None):
            raise ValueError('exactly_one_route_or_control')
        if self.control in ('greeting', 'unsupported_scope') and (self.operations or self.claims):
            raise ValueError('terminal_control_has_actions')
        if self.control in ('greeting', 'unsupported_scope') and self.parts:
            raise ValueError('terminal_control_has_parts')
        if self.route is not None and not self.parts:
            raise ValueError('route_requires_parts')
        if len({p.part_id for p in self.parts}) != len(self.parts):
            raise ValueError('duplicate_part_id')
        if len({(p.start, p.end) for p in self.parts}) != len(self.parts):
            raise ValueError('duplicate_part_span')
        if any(i >= len(self.operations) for p in self.parts for i in p.operation_indices):
            raise ValueError('invalid_part_operation')
        for item in (*self.claims, *self.operations):
            idx = item.entity if isinstance(item, Claim) else item.target
            kind = 'term' if isinstance(item, Operation) and item.name in TERM_OPERATIONS else 'course'
            if idx >= len(self.mentions) or self.mentions[idx].kind != kind:
                raise ValueError(f'invalid_{kind}_mention_reference')
        return self


class CatalogEntry(Record):
    """Declared reviewed aliases injected by a trusted caller; no lifecycle promotion."""
    kind: Kind
    entity_id: Identifier
    program_id: Identifier
    curriculum_id: Identifier | None
    aliases: tuple[Text, ...] = Field(min_length=1, max_length=32)
    source_ref: str = Field(pattern=r'^ver-[a-z0-9-]+$')
    review_ref: Text
    reviewed: Literal[True]

    @model_validator(mode='after')
    def _scope(self):
        if any(not x.strip() for x in self.aliases) or not self.review_ref.strip():
            raise ValueError('empty_alias_or_review')
        if self.kind != 'program' and self.curriculum_id is None:
            raise ValueError('curriculum_required')
        if self.kind == 'program' and (self.entity_id != self.program_id or self.curriculum_id):
            raise ValueError('program_identity_mismatch')
        if self.kind == 'curriculum' and self.entity_id != self.curriculum_id:
            raise ValueError('curriculum_identity_mismatch')
        return self
