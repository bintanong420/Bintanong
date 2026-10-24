"""Independent Bintu routing/style interpretations with one shared format repair."""
from __future__ import annotations

import json
import re
from dataclasses import replace

from pydantic import ValidationError

from ..bintanong_contracts.runtime import NormalizedQuery
from ..bintanong_contracts.symbolic import EMPTY_REGISTRY
from .contracts import Interpretation, RequestContext, prepare_query
from .prompt import build_messages, output_schema, previous_turn
from .style import StyleProposal, build_style_messages, floor_style, style_output_schema
from .transport import RuntimeFailure
from .validation import RoutingResult, _decision, validate_interpretation
from .wire import WireInterpretation, normalize_interpretation


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate_json_key')
        result[key] = value
    return result


def _json_proposal(raw):
    if not isinstance(raw, str) or len(raw.encode('utf-8')) > 65536:
        raise ValueError('invalid_output_size')
    return json.loads(raw, object_pairs_hook=_unique_object)


REFERENCE_HINTS = {
    'invalid_course_quote_reference': 'every operation target and claim entity must quote a course '
        'code that is also listed in mentions with kind course; if the student names no specific '
        'course code, return no operation (route RAG, or control clarify).',
    'topic_outside_menu': 'requested_claims must be facts listed under the chosen topic only.',
}


def _repair_messages(messages, raw, problem=None):
    if problem is None:
        request = ('This is a formatting repair, not a new student question. '
            'Return valid JSON matching the original schema for the ORIGINAL student request '
            'in the payload below. Correct formatting only; preserve its meaning and facts.\n')
    else:  # A reference error is a meaning error: name it and allow reinterpretation.
        request = ('This is a repair, not a new student question. The previous interpretation was '
            f'rejected ({problem}): {REFERENCE_HINTS.get(problem, "fix that invalid reference")} '
            'Return valid JSON matching the original schema for the ORIGINAL student request '
            'in the payload below. Do not invent courses, operations or facts.\n')
    return [*messages, dict(role='assistant', content=raw[:65536] if isinstance(raw, str) else ''),
        dict(role='user', content=request + messages[1]['content'])]



def check_topics(proposed, topics):
    """Host check: topic choices must come from the release menu, claims from that subject."""
    menu = {t.subject_id: {*t.claims, *t.not_stated} for t in topics}
    for part in proposed.parts:
        if part.subject_id is not None and not set(part.requested_claims) <= menu.get(part.subject_id, set()):
            raise ValueError('topic_outside_menu')


def apply_not_stated_cues(proposed, topics):
    """Host guard: a part whose own words name a cued not-stated fact also requests that fact, so the
    evidence policy withholds instead of answering from a nearby printed fact."""
    cues = {t.subject_id: t.cues for t in topics if t.cues}
    parts = []
    for part in proposed.parts:
        claims = list(part.requested_claims)
        for cue in cues.get(part.subject_id, ()):
            if cue.claim not in claims and any(
                    re.search(r'(?<![\w-])' + re.escape(p) + r'(?![\w-])', part.text, re.IGNORECASE)
                    for p in cue.phrases):
                claims.append(cue.claim)
        parts.append(part.model_copy(update=dict(requested_claims=tuple(claims))))
    if all(a.requested_claims == b.requested_claims for a, b in zip(parts, proposed.parts)):
        return proposed
    return Interpretation.parse(proposed.model_copy(update=dict(parts=tuple(parts))).model_dump(mode='json'))


class Router:
    def __init__(self, transport, *, catalog=(), registry=EMPTY_REGISTRY,
                 documents_available=False, synthetic=False, topics=()):
        self.transport = transport
        self.catalog = tuple(catalog)
        self.registry = registry
        self.documents_available = documents_available
        self.synthetic = synthetic
        self.topics = tuple(topics)

    async def route(self, text: str, context: RequestContext) -> RoutingResult:
        normalized = prepare_query(text)
        context = RequestContext.parse(context.model_dump(mode='json'))
        messages = build_messages(text, context, self.catalog, self.registry, self.topics)
        follow_up = previous_turn(context, self.catalog) is not None
        names = tuple(alias for entry in self.catalog for alias in entry.aliases)  # never style evidence
        proposed = None

        def failure(code, attempts, style_attempts=0, style=None, floored=False):
            query = NormalizedQuery(schema_version=NormalizedQuery.SCHEMA_VERSION,
                original_text=text, normalized_text=normalized, language_hints=(), intent=None,
                entities=(), ambiguities=(), negations=(), time_qualifiers=(),
                session_fact_refs=tuple(f.fact_id for f in context.facts))
            return RoutingResult(query, _decision(control='evidence_unavailable', reason=code),
                proposed, (), 'unknown' if style is None else style.language, code, attempts,
                style_attempts=style_attempts, style_evidence=style, style_floor_applied=floored)

        async def clarification_style():
            """One unrepaired style call so a clarification matches the student's style."""
            try:
                style = StyleProposal.parse(_json_proposal(await self.transport.infer(
                    build_style_messages(text), style_output_schema()))).style
                style.ground(text)
            except (RuntimeFailure, ValueError, ValidationError):
                return None, False
            return floor_style(style, text, names)

        for attempt in (1, 2):
            try:
                raw = await self.transport.infer(messages, output_schema(self.topics, follow_up=follow_up))
            except RuntimeFailure as error:
                return failure(str(error), attempt)
            problem = None
            try:
                wire = WireInterpretation.parse(_json_proposal(raw))
                try:
                    proposed = normalize_interpretation(text, wire)
                    check_topics(proposed, self.topics)
                    proposed = apply_not_stated_cues(proposed, self.topics)
                except (ValueError, ValidationError) as error:
                    problem = str(error) if str(error) in REFERENCE_HINTS else 'invalid_reference'
                    raise
            except (ValueError, ValidationError):
                if attempt == 2:
                    if problem is None:
                        return failure('invalid_model_output', attempt)
                    return failure('invalid_reference', attempt, 1, *await clarification_style())
                messages = _repair_messages(messages, raw, problem)
                continue
            style_messages = build_style_messages(text)
            style_limit = 2 if attempt == 1 else 1  # one shared repair, maximum three calls
            for style_attempt in range(1, style_limit + 1):
                try:
                    style_raw = await self.transport.infer(style_messages, style_output_schema())
                except RuntimeFailure as error:
                    return failure(str(error), attempt, style_attempt)
                try:
                    style = StyleProposal.parse(_json_proposal(style_raw)).style
                except (ValueError, ValidationError):
                    if style_attempt == style_limit:
                        return failure('invalid_style_output', attempt, style_attempt)
                    style_messages = _repair_messages(style_messages, style_raw)
                    continue
                try:
                    style.ground(text)
                    style, floored = floor_style(style, text, names)
                    effective = Interpretation.parse(dict(proposed.model_dump(mode='json'), language=style.language))
                    result = validate_interpretation(text, context, effective, catalog=self.catalog,
                        registry=self.registry, documents_available=self.documents_available,
                        synthetic=self.synthetic)
                    return replace(result, proposed=proposed, attempts=attempt,
                        style_attempts=style_attempt, style_evidence=style,
                        style_floor_applied=floored, offset_corrections=0)
                except ValueError:
                    return failure('invalid_grounding', attempt, style_attempt)
        raise AssertionError('unreachable')
