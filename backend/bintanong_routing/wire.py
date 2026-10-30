"""Model-facing quoted references; host-owned spans and course indices."""
from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Contract, Control, Record, Route
from .terms import parse_term
from .contracts import TERM_OPERATIONS, Interpretation, Language, MentionKind, State, Text, prepare_query


class QuoteReference(Record):
    text: str = Field(min_length=1, max_length=4096)
    occurrence: int = Field(ge=0, le=8191)


class WireMention(Record):
    kind: MentionKind
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
    subject_id: str | None = None  # only present in the schema when a topic menu exists
    requested_claims: tuple[str, ...] = ()
    detail: Literal['whole', 'requirements', 'fees', 'processing_time', 'specific'] | None = None  # menu schema only


class WireInterpretation(Contract):
    SCHEMA_VERSION = 'bintanong-interpretation-wire-v4'
    language: Language
    audience: Literal['undergraduate', 'excluded', 'unrelated', 'unknown']
    control: Control() | None
    part_count: int = Field(ge=0, le=8)
    parts: tuple[WirePart, ...] = Field(max_length=8)
    intent: Text
    # Offered (and required) only when a scoped previous course is available (master 23); removed
    # from document-only/single-turn schemas. Decided before mentions for a course back-reference.
    previous_course_quote: QuoteReference | None = None
    mentions: tuple[WireMention, ...] = Field(max_length=32)
    claims: tuple[WireClaim, ...] = Field(max_length=32)
    operations: tuple[WireOperation, ...] = Field(max_length=4)
    route: Route() | None
    ambiguities: tuple[Text, ...] = Field(max_length=16, description=
        'Only unresolved questions needed to interpret the request. Normally empty. '
        'Never put a route explanation or a need to retrieve documents here.')
    # No free-text reason (owner, 23 Oct 2026): last field, nothing reads it, decoding it cost ~2 s.
    # intent stays: removing it made a 4B-model claim extraction unstable (run 14 precheck).

    @model_validator(mode='after')
    def _part_count(self):
        # A greeting or out-of-scope refusal runs no part (Interpretation rejects any it lists), so its count cannot
        # change the outcome (live 24 Oct 2026: such a refusal was shown as "temporarily unavailable").
        if self.part_count != len(self.parts) and self.control not in ('greeting', 'unsupported_scope'):
            raise ValueError('part_count_mismatch')
        return self


def _topic_parts_as_documents(wire: WireInterpretation, course_names=frozenset()) -> WireInterpretation:
    """A structured part that chose a document topic and whose operations target no listed course
    (live 24 Oct 2026: "overload" checked as a course) has nothing to check; its only executable
    reading is the chosen topic. When every operation targets a listed course (gate 28 Oct 2026: an
    eligibility check that also named the prerequisite-policy topic), the course check is the explicit
    request and the stray topic is dropped. A target exactly naming a reviewed course alias counts as a
    listed course (owner 30 Oct 2026: "Can I take CC5 ...?" quoted CC5 without listing it)."""
    courses = {(m.quote.text, m.quote.occurrence) for m in wire.mentions if m.kind in ('course', 'term')}
    def aimed(i):
        if i >= len(wire.operations):
            return False
        target = wire.operations[i].target
        return (target.text, target.occurrence) in courses or prepare_query(target.text).casefold() in course_names
    def topical(part):
        return part.evidence_need == 'structured' and part.subject_id is not None and part.operation_indices
    def slip(part):
        return topical(part) and not any(aimed(i) for i in part.operation_indices)
    if any(topical(p) and all(aimed(i) for i in p.operation_indices) for p in wire.parts):
        data = wire.model_dump(mode='json')
        for part, value in zip(wire.parts, data['parts']):
            if topical(part) and all(aimed(i) for i in part.operation_indices):
                value.update(subject_id=None, requested_claims=[], detail='whole')
        wire = WireInterpretation.parse(data)
    dropped = {i for p in wire.parts if slip(p) for i in p.operation_indices}
    if not dropped or any(i in dropped for p in wire.parts if not slip(p) for i in p.operation_indices):
        return wire
    data = wire.model_dump(mode='json')
    kept = [i for i in range(len(wire.operations)) if i not in dropped]
    data['operations'] = [data['operations'][i] for i in kept]
    for part, value in zip(wire.parts, data['parts']):
        if slip(part):
            value.update(evidence_need='document', operation_indices=[])
        else:
            # Out-of-range indices stay for the single-operation repair below.
            value['operation_indices'] = [kept.index(i) if i in kept else i for i in part.operation_indices]
    needs = frozenset(p['evidence_need'] for p in data['parts'])
    if wire.route is not None and 'unknown' not in needs:
        data['route'] = {frozenset({'document'}): 'RAG', frozenset({'structured'}): 'Symbolic'}.get(needs, 'Hybrid')
    return WireInterpretation.parse(data)


def normalize_interpretation(text: str, wire: WireInterpretation, *, course_names=frozenset()) -> Interpretation:
    """Resolve declared literal occurrences only; no semantic inference or alias guessing. course_names
    (casefolded reviewed course aliases) only tells a course check from a topic slip."""
    prepare_query(text)
    wire = _topic_parts_as_documents(WireInterpretation.parse(wire.model_dump(mode='json')), course_names)
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
                    break
            if start < 0:
                # A miscounted occurrence is corrected only when the quote occurs exactly once,
                # so nothing has to be chosen (same rule as offset correction).
                first = text.find(quote.text)
                if first < 0 or text.find(quote.text, first + 1) >= 0:
                    raise ValueError('quote_occurrence_not_found')
                start = first
            spans[identity] = dict(text=quote.text, start=start, end=start + len(quote.text))
        return spans[identity]

    mentions = {}
    for index, mention in enumerate(wire.mentions):
        identity = key(mention.quote)
        if identity in mentions:
            raise ValueError('duplicate_mention_reference')
        mentions[identity] = index
    positions = [(span(m.quote)['start'], m.quote.text) for m in wire.mentions]
    if len(set(positions)) != len(positions):  # two declared occurrences landed on one place
        raise ValueError('duplicate_mention_reference')

    # A program/curriculum quote that reads as a year level or semester (live: "second year" listed as a
    # curriculum) is a term; reviewed curricula are school years, never "<ordinal> year".
    listed = [dict(kind='term' if m.kind in ('program', 'curriculum') and parse_term(m.quote.text) else m.kind,
                   **span(m.quote)) for m in wire.mentions]
    at = {(m['start'], m['text']): index for index, m in enumerate(listed)}

    def course_index(quote, kind='course'):
        index = mentions.get(key(quote))
        if index is None:
            # A quoted course (or term) the model did not list (owner, 23 Oct 2026) becomes a mention of
            # that kind; the host still has to resolve it. A miscount reuses the mention at that place.
            found = span(quote)
            index = at.setdefault((found['start'], found['text']), len(listed))
            if index == len(listed):
                listed.append(dict(kind=kind, **found))
            mentions[key(quote)] = index
        if listed[index]['kind'] != kind and kind == 'term' and parse_term(listed[index]['text']) is not None:
            # A listing target the model labelled as another kind (live: "second year" as a curriculum) is a
            # term when it reads as a year/semester; anything else keeps the error.
            listed[index]['kind'] = 'term'
        if listed[index]['kind'] != kind:
            raise ValueError(f'invalid_{kind}_quote_reference')
        return index

    data = wire.model_dump(mode='json')
    data.pop('part_count')
    data.pop('previous_course_quote')
    if wire.previous_course_quote is not None:
        data['context_reference'] = span(wire.previous_course_quote)
    claims = [dict(**span(c.quote), entity=course_index(c.entity), state=c.state, mode=c.mode)
              for c in wire.claims]
    operations = [dict(name=o.name, target=course_index(o.target, 'term' if o.name in TERM_OPERATIONS else 'course'))
                  for o in wire.operations]
    proposal = f'route {wire.route}' if wire.route is not None else f'control {wire.control}'
    def indices(part):
        # With one operation, an out-of-range index (live slip: the position in available_operations)
        # can only mean that operation, so nothing has to be chosen (same rule as occurrence repair).
        if len(operations) == 1 and part.operation_indices and all(i >= 1 for i in part.operation_indices):
            return [0]
        return list(part.operation_indices)

    data.update(schema_version=Interpretation.SCHEMA_VERSION,
        reason=f'interpreter proposed {proposal}', mentions=listed, claims=claims,
        operations=operations, parts=[dict(**span(p.quote), part_id=p.part_id, evidence_need=p.evidence_need,
                    operation_indices=indices(p), subject_id=p.subject_id,
                    requested_claims=list(p.requested_claims), detail=p.detail or 'whole') for p in wire.parts])
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
    if result.route in ('Symbolic', 'Hybrid') and result.audience == 'undergraduate' and not result.ambiguities:
        # Reject this structural mismatch while the router can still ask the model to repair it.
        # Keep control/audience/ambiguity holds and all later semantic validation unchanged.
        referenced = {i for part in result.parts for i in part.operation_indices}
        if referenced != set(range(len(result.operations))):
            raise ValueError('unreferenced_operation')
    return result
