"""Model-facing quoted references; host-owned spans and course indices."""
from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Contract, Control, Record, Route
from .contracts import Interpretation, Kind, Language, State, Text, prepare_query


class QuoteReference(Record):
    text: str = Field(min_length=1, max_length=4096)
    occurrence: int = Field(ge=0, le=8191)


class WireMention(Record):
    kind: Kind
    quote: QuoteReference


class WireClaim(Record):
    quote: QuoteReference
    entity: QuoteReference
    state: State
    mode: Literal['asserted', 'hypothetical', 'reported']


class WireOperation(Record):
    name: str = Field(pattern=r'^[a-z][a-z0-9_]*$', max_length=64)
    target: QuoteReference


class WirePart(Record):
    part_id: str = Field(pattern=r'^r[1-8]$')
    quote: QuoteReference
    evidence_need: Literal['document', 'structured', 'unknown']
    operation_indices: tuple[Annotated[int, Field(ge=0, le=3)], ...] = Field(max_length=4)


class WireInterpretation(Contract):
    SCHEMA_VERSION = 'bintanong-interpretation-wire-v2'
    language: Language
    audience: Literal['undergraduate', 'excluded', 'unrelated', 'unknown']
    control: Control() | None
    part_count: int = Field(ge=0, le=8)
    parts: tuple[WirePart, ...] = Field(max_length=8)
    intent: Text
    mentions: tuple[WireMention, ...] = Field(max_length=32)
    claims: tuple[WireClaim, ...] = Field(max_length=32)
    operations: tuple[WireOperation, ...] = Field(max_length=4)
    route: Route() | None
    ambiguities: tuple[Text, ...] = Field(max_length=16, description=
        'Only unresolved questions needed to interpret the request. Normally empty. '
        'Never put a route explanation or a need to retrieve documents here.')
    reason: Text

    @model_validator(mode='after')
    def _part_count(self):
        if self.part_count != len(self.parts):
            raise ValueError('part_count_mismatch')
        return self


def normalize_interpretation(text: str, wire: WireInterpretation) -> Interpretation:
    """Resolve declared literal occurrences only; no semantic inference or alias guessing."""
    prepare_query(text)
    wire = WireInterpretation.parse(wire.model_dump(mode='json'))
    spans = {}

    def key(quote):
        return quote.text, quote.occurrence

    def span(quote):
        identity = key(quote)
        if identity not in spans:
            start = -1
            for _ in range(quote.occurrence + 1):
                start = text.find(quote.text, start + 1)
                if start < 0:
                    raise ValueError('quote_occurrence_not_found')
            spans[identity] = dict(text=quote.text, start=start, end=start + len(quote.text))
        return spans[identity]

    mentions = {}
    for index, mention in enumerate(wire.mentions):
        identity = key(mention.quote)
        if identity in mentions:
            raise ValueError('duplicate_mention_reference')
        mentions[identity] = index

    def course_index(quote):
        index = mentions.get(key(quote))
        if index is None or wire.mentions[index].kind != 'course':
            raise ValueError('invalid_course_quote_reference')
        return index

    data = wire.model_dump(mode='json')
    data.pop('part_count')
    data.update(schema_version=Interpretation.SCHEMA_VERSION,
        mentions=[dict(kind=m.kind, **span(m.quote)) for m in wire.mentions],
        claims=[dict(**span(c.quote), entity=course_index(c.entity), state=c.state, mode=c.mode)
                for c in wire.claims],
        operations=[dict(name=o.name, target=course_index(o.target)) for o in wire.operations],
        parts=[dict(**span(p.quote), part_id=p.part_id, evidence_need=p.evidence_need,
                    operation_indices=list(p.operation_indices)) for p in wire.parts])
    result = Interpretation.parse(data)
    for claim in result.claims:
        entity = result.mentions[claim.entity]
        if not claim.start <= entity.start < entity.end <= claim.end:
            raise ValueError('uncontained_claim_entity')
    for part in result.parts:
        for index in part.operation_indices:
            target = result.mentions[result.operations[index].target]
            if not part.start <= target.start < target.end <= part.end:
                raise ValueError('uncontained_part_target')
    return result
