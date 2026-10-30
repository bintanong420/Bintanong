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
from . import topic_selection as selection
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
    'course_reference_unavailable': 'no scoped previous course is available. Do not emit a '
        'previous_course_quote or turn a document subject ID into a course. For a clear document '
        'follow-up, use the previous document subject and its reviewed claims; clarify an unclear '
        'request rather than inventing a course or operation.',
    'unreferenced_operation': 'every operation must be referenced by a question part that requests it. '
        'Interpret the original request again; document-only parts need no course operation. '
        'Do not invent a structured question or course to justify an unused operation.',
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


# Owner F4 (28 Oct 2026, provisional "b perhaps"): a transfer question that does not say whether the student is
# leaving PalSU or transferring in is asked first. Phrases that state the direction (English/Filipino/Taglish).
TRANSFER_FAMILIES = frozenset(('leaving_palsu_transfer_credentials', 'transferring_into_palsu'))
TRANSFER_DIRECTION_CUES = (
    'honorable dismissal', 'transfer out', 'transferring out', 'leave palsu', 'leaving palsu',
    'leave the university', 'leaving the university', 'to another school', 'to another university',
    'to other school', 'aalis', 'lilipat sa ibang', 'lilipat ng ibang',
    'transferee', 'from another school', 'from other school', 'from another university',
    'galing sa ibang', 'transfer to palsu', 'transferring to palsu', 'lilipat sa palsu', 'lumipat sa palsu')


# Owner, 28 Oct 2026: a question explicitly naming an excluded program gets the undergraduate-scope notice even
# when the router labels it undergraduate. Other wording stays with the router.
EXCLUDED_PROGRAM_CUES = (
    'college of law', 'school of law', 'juris doctor', 'college of medicine', 'doctor of medicine',
    'graduate school', "master's program", 'masters program', "master's degree", 'masters degree',
    'doctoral program', 'doctorate program', 'laboratory school')


def _names_any(text, phrases):
    text = text.replace('’', "'")  # a typed curly apostrophe matches master's
    return any(re.search(r'(?<![\w-])' + re.escape(c) + r'(?![\w-])', text, re.IGNORECASE) for c in phrases)


def transfer_direction_unstated(proposed, topics, text):
    families = {t.subject_id: t.family for t in topics}
    return (any(families.get(p.subject_id) in TRANSFER_FAMILIES for p in proposed.parts)
            and not _names_any(text, TRANSFER_DIRECTION_CUES))


def _printed_claims(topic, text):
    """The topic's printed claims for a whole request. A topic with more than a part may request (e.g. a 39-row
    sanctions table) narrows to the claims naming the request's words, either word possibly the short form
    ("exam" names "examinations"); none when those do not fit."""
    printed = tuple(c for c in topic.claims if c not in topic.not_stated)
    if len(printed) > 8:  # RequestPart.requested_claims bound
        asked = set(_heading_words(text))
        printed = tuple(c for c in printed if any(_same_word(w, a) or _same_word(a, w)
                                                  for w in _heading_words(c) for a in asked))
    return printed if len(printed) <= 8 else ()


def answer_settled_topic(proposed, topics, text):
    """Host guard (owner 30 Oct 2026): after the selector settled on one topic, a clarification naming no part,
    ambiguity, course or operation (e.g. "Kailan ako considered second year?") answers that topic's printed
    claims as one document part instead of leaving the student without an answer."""
    if (len(topics) != 1 or proposed.control != 'clarify' or proposed.parts or proposed.ambiguities
            or proposed.mentions or proposed.operations or proposed.claims):
        return proposed
    claims = _printed_claims(topics[0], text)
    if not claims:
        return proposed
    part = dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='document',
                operation_indices=[], subject_id=topics[0].subject_id, requested_claims=list(claims), detail='whole')
    return Interpretation.parse(dict(proposed.model_dump(mode='json'), parts=[part], route='RAG', control=None))


def prefer_printed_procedure(proposed, topics):
    """Host guard: a whole-procedure part asks for the printed procedure, so naming only facts the source
    does not state is replaced by the topic's printed claims (see _printed_claims). Cues then re-add a
    not-stated fact the part's own words name, which keeps withholding for an explicit ask. When the printed
    claims do not fit, the model's choice is kept."""
    menu = {t.subject_id: t for t in topics}
    parts = []
    for part in proposed.parts:
        topic = menu.get(part.subject_id)
        if (topic is not None and part.detail == 'whole' and part.requested_claims
                and set(part.requested_claims) <= set(topic.not_stated)):
            printed = _printed_claims(topic, part.text)
            if printed:
                part = part.model_copy(update=dict(requested_claims=printed))
        parts.append(part)
    if all(a.requested_claims == b.requested_claims for a, b in zip(parts, proposed.parts)):
        return proposed
    return Interpretation.parse(proposed.model_copy(update=dict(parts=tuple(parts))).model_dump(mode='json'))


# Words too generic to tie a part to one printed section heading.
HEADING_STOPWORDS = frozenset('the and for with from not any are all its ang mga ng sa na at ko'.split())


def _heading_words(text):
    return [w for w in re.findall(r'[^\W\d_]+', text.casefold()) if len(w) >= 3 and w not in HEADING_STOPWORDS]


def _same_word(heading, asked):
    """A short heading word (an abbreviation such as INC) starts the asked word; longer words share a stem."""
    return asked.startswith(heading) if len(heading) <= 4 else asked[:5] == heading[:5]


def _heading_score(topic, claim, asked):
    """The most of the asked words that one printed heading of the claim names."""
    return max((len({a for a in asked if any(_same_word(w, a) for w in _heading_words(h))})
                for h in topic.claim_headings.get(claim, ())), default=0)


def prefer_heading_claims(proposed, topics):
    """Host guard (owner 30 Oct 2026): when one fact of the chosen topic has a printed section heading naming at
    least two of the part's own words (e.g. "remove an incomplete grade" and 3.4 REMOVAL OF "INC") and no chosen
    fact's heading names any, that fact replaces the choice. Adding both exceeded the topic's context budget.
    A tie or a single-word match keeps the model's choice; only facts of the same topic are considered."""
    menu = {t.subject_id: t for t in topics if t.claim_headings}
    parts = []
    for part in proposed.parts:
        topic = menu.get(part.subject_id)
        if topic is not None and part.evidence_need == 'document':
            asked = set(_heading_words(part.text))
            if not any(_heading_score(topic, claim, asked) for claim in part.requested_claims):
                scores = {claim: _heading_score(topic, claim, asked) for claim in topic.claim_headings
                          if claim in topic.claims and claim not in topic.not_stated}
                best = max(scores.values(), default=0)
                winners = [claim for claim, score in scores.items() if score == best]
                if best >= 2 and len(winners) == 1:
                    part = part.model_copy(update=dict(requested_claims=(winners[0],)))
        parts.append(part)
    if all(a.requested_claims == b.requested_claims for a, b in zip(parts, proposed.parts)):
        return proposed
    return Interpretation.parse(proposed.model_copy(update=dict(parts=tuple(parts))).model_dump(mode='json'))


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
                 documents_available=False, synthetic=False, topics=(), topic_selection=False):
        self.transport = transport
        self.catalog = tuple(catalog)
        self.registry = registry
        self.documents_available = documents_available
        self.synthetic = synthetic
        self.topics = tuple(topics)
        if type(topic_selection) is not bool:
            raise ValueError('invalid_topic_selection')
        self.topic_selection = topic_selection

    async def route(self, text: str, context: RequestContext) -> RoutingResult:
        normalized = prepare_query(text)
        context = RequestContext.parse(context.model_dump(mode='json'))
        follow_up = bool((previous_turn(context, self.catalog) or {}).get('course_available'))
        names = tuple(alias for entry in self.catalog for alias in entry.aliases)  # never style evidence
        proposed = None
        topics = self.topics
        selection_attempts = 0

        def failure(code, attempts, style_attempts=0, style=None, floored=False):
            query = NormalizedQuery(schema_version=NormalizedQuery.SCHEMA_VERSION,
                original_text=text, normalized_text=normalized, language_hints=(), intent=None,
                entities=(), ambiguities=(), negations=(), time_qualifiers=(),
                session_fact_refs=tuple(f.fact_id for f in context.facts))
            return RoutingResult(query, _decision(control='evidence_unavailable', reason=code),
                proposed, (), 'unknown' if style is None else style.language, code, attempts,
                style_attempts=style_attempts, style_evidence=style, style_floor_applied=floored,
                selection_attempts=selection_attempts)

        async def clarification_style():
            """One unrepaired style call so a clarification matches the student's style."""
            try:
                style = StyleProposal.parse(_json_proposal(await self.transport.infer(
                    build_style_messages(text), style_output_schema()))).style
                style.ground(text)
            except (RuntimeFailure, ValueError, ValidationError):
                return None, False
            return floor_style(style, text, names)

        if self.topic_selection and len(topics) > selection.MAX_TOPICS:
            selection_attempts = 1
            try:
                raw = await self.transport.infer(selection.build_messages(
                    text, topics, previous_turn(context, self.catalog)), selection.output_schema(topics))
                topics = selection.selected_topics(_json_proposal(raw), topics)
            except RuntimeFailure as error:
                return failure(str(error), 0)
            except ValueError:
                return failure('topic_selection_unavailable', 0)

        messages = build_messages(text, context, self.catalog, self.registry, topics)
        for attempt in (1, 2):
            try:
                raw = await self.transport.infer(messages, output_schema(topics, follow_up=follow_up))
            except RuntimeFailure as error:
                return failure(str(error), attempt)
            problem = None
            try:
                wire = WireInterpretation.parse(_json_proposal(raw))
                try:
                    if wire.previous_course_quote is not None and not follow_up:
                        raise ValueError('course_reference_unavailable')
                    proposed = normalize_interpretation(text, wire)
                    check_topics(proposed, topics)
                    if selection_attempts:
                        proposed = answer_settled_topic(proposed, topics, text)
                    proposed = apply_not_stated_cues(prefer_heading_claims(
                        prefer_printed_procedure(proposed, topics), topics), topics)
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
                    if selection_attempts and result.decision.dispatchable and any(
                            p.evidence_need == 'document' and p.subject_id is None for p in proposed.parts):
                        return failure('topic_selection_unavailable', attempt, style_attempt, style, floored)
                    if result.decision.dispatchable and _names_any(text, EXCLUDED_PROGRAM_CUES):
                        result = replace(result, decision=_decision(control='unsupported_scope',
                            reason='excluded program named'), diagnostic='excluded_program_named')
                    elif result.decision.dispatchable and transfer_direction_unstated(proposed, topics, text):
                        result = replace(result, decision=_decision(control='clarify',
                            missing=('transfer_direction',), reason='transfer direction unstated'),
                            diagnostic='transfer_direction_unstated')
                    return replace(result, proposed=proposed, attempts=attempt,
                        style_attempts=style_attempt, style_evidence=style,
                        style_floor_applied=floored, offset_corrections=0,
                        selection_attempts=selection_attempts)
                except ValueError:
                    return failure('invalid_grounding', attempt, style_attempt)
        raise AssertionError('unreachable')
