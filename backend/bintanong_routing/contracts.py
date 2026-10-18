"""Strict routing data. Model proposals never carry trusted IDs or executable goals."""
from __future__ import annotations

import unicodedata
from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Contract, Control, Record, Route

Text = Annotated[str, Field(min_length=1, max_length=240)]
Identifier = Annotated[str, Field(min_length=1, max_length=128, pattern=r'^[a-z][a-z0-9_-]*$')]
Kind = Literal['program', 'curriculum', 'course']
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


class RequestContext(Record):
    """Must come from the owning application, not directly from model output."""
    session_id: str = Field(pattern=r'^sess-[a-z0-9-]+$')
    request_id: str = Field(pattern=r'^req-[a-z0-9-]+$', max_length=128)
    program_id: Identifier | None = None
    curriculum_id: Identifier | None = None
    facts: tuple[ScopedFact, ...] = Field(default=(), max_length=256)

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
    kind: Kind


class Claim(Quote):
    entity: int = Field(ge=0, le=31)
    state: State
    mode: Literal['asserted', 'hypothetical', 'reported']


class Operation(Record):
    name: str = Field(pattern=r'^[a-z][a-z0-9_]*$', max_length=64)
    target: int = Field(ge=0, le=31)


class Interpretation(Contract):
    SCHEMA_VERSION = 'bintanong-interpretation-v1'
    language: Language
    audience: Literal['undergraduate', 'excluded', 'unrelated', 'unknown']
    intent: Text
    mentions: tuple[Mention, ...] = Field(max_length=32)
    claims: tuple[Claim, ...] = Field(max_length=32)
    operations: tuple[Operation, ...] = Field(max_length=4)
    route: Route() | None
    control: Control() | None
    ambiguities: tuple[Text, ...] = Field(max_length=16, description=
        'Only unresolved questions needed to interpret the request. Normally empty. '
        'Never put a route explanation or a need to retrieve documents here.')
    reason: Text

    @model_validator(mode='after')
    def _structure(self):
        if (self.route is None) == (self.control is None):
            raise ValueError('exactly_one_route_or_control')
        for item in (*self.claims, *self.operations):
            idx = item.entity if isinstance(item, Claim) else item.target
            if idx >= len(self.mentions) or self.mentions[idx].kind != 'course':
                raise ValueError('invalid_course_mention_reference')
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
