"""Exact reviewed-alias resolution and effective decisions, without tool execution."""
from __future__ import annotations

import hashlib
import re
from copy import deepcopy
from dataclasses import dataclass

from ..bintanong_contracts.runtime import BoundInput, NormalizedQuery, PredicateRequest, ResolvedEntity, RoutingDecision, negation_tokens, time_phrases
from ..bintanong_contracts.symbolic import CapabilityRegistry, EMPTY_REGISTRY, UnsupportedRequest
from .claim_evidence import enrollment_period, inside_if_clause, stated_result
from .contracts import (TERM_OPERATIONS, CatalogEntry, Interpretation, RequestContext, ScopedFact, fact_dimension,
                        prepare_query)
from .style import StyleEvidence
from .languages import unsupported_language
from .terms import parse_term

OPERATIONS = ('check_prerequisite_eligibility', 'list_missing_prerequisites', 'list_affected_courses',
              'course_facts', 'list_term_courses', 'assess_term_prerequisites')


class GroundedClaim(ScopedFact):
    mode: str
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class RoutingResult:
    query: NormalizedQuery
    decision: RoutingDecision
    proposed: Interpretation | None
    claims: tuple[GroundedClaim, ...]
    response_style: str
    diagnostic: str
    attempts: int = 1
    program_id: str | None = None
    curriculum_id: str | None = None
    offset_corrections: int = 0
    style_attempts: int = 0
    style_evidence: StyleEvidence | None = None
    style_floor_applied: bool = False
    selection_attempts: int = 0

    @property
    def inference_calls(self):
        return self.attempts + self.style_attempts + self.selection_attempts

    @property
    def repair_attempts(self):
        return max(self.attempts - 1, 0) + max(self.style_attempts - 1, 0)


def anchor_unique_quotes(data, text):
    """Anchor literal quotes deterministically; never choose between repeated text.

    Model offsets are suggestions, not evidence. Keep correctly positioned repeated
    quotes; correct bad integer offsets only when the complete quote occurs once.
    Schema/type errors, invented quotes and ambiguous occurrences remain invalid.
    """
    if not isinstance(data, dict):
        return data, 0
    anchored = deepcopy(data)
    corrections = 0
    for name in ('mentions', 'claims', 'parts'):
        items = anchored.get(name)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            quote, start, end = item.get('text'), item.get('start'), item.get('end')
            if not isinstance(quote, str) or not quote or type(start) is not int or type(end) is not int:
                continue
            if 0 <= start < end <= len(text) and text[start:end] == quote:
                continue
            first = text.find(quote)
            if first >= 0 and text.find(quote, first + 1) == -1:
                item['start'], item['end'] = first, first + len(quote)
                corrections += 1
    return anchored, corrections


def _key(text):
    return prepare_query(text).casefold()


def _matches(mention, catalog, program=None, curriculum=None):
    scoped = tuple(c for c in catalog if c.kind == mention.kind
                   and (program is None or c.program_id == program)
                   and (curriculum is None or c.curriculum_id == curriculum))
    exact = tuple(c for c in scoped if _key(mention.text) in {_key(a) for a in c.aliases})
    if exact or mention.kind == 'course':
        return exact
    # A program/curriculum phrase ("Nursing student ako") resolves when it contains an approved
    # name as whole words (owner decision, 24 Oct 2026); the longest names win, and a phrase naming
    # several entities matches all of them (the caller then asks which is meant).
    found = {}
    for c in scoped:
        for a in c.aliases:
            short = len(a) <= 4 and a.isupper()  # abbreviations such as "IT" match only as written
            pattern = r'(?<![\w-])' + re.escape(a) + r'(?![\w-])'
            for m in re.finditer(pattern, mention.text, 0 if short else re.IGNORECASE):
                found.setdefault(c.entity_id, []).append((m.start(), m.end(), c))
    spans = [s for hits in found.values() for s in hits]
    keep = {c.entity_id for s, e, c in spans
            if not any(s2 <= s and e <= e2 and (e2 - s2) > (e - s) for s2, e2, _ in spans)}
    return tuple(c for c in scoped if c.entity_id in keep)


def _split_code(text, mention, catalog, program, curriculum):
    """Live 31 Oct 2026: the model split the printed code "HPC 8 / FL 2" into two mentions. A printed code that
    starts at the mention and continues in the text names that one course (spacing may differ)."""
    found = {}
    for c in catalog:
        if c.kind != 'course' or (c.program_id, c.curriculum_id) != (program, curriculum):
            continue
        for a in c.aliases:
            m = re.compile(r'\s*'.join(map(re.escape, a.replace(' ', ''))), re.IGNORECASE).match(text, mention.start)
            if m and m.end() > mention.end and not text[m.end():m.end() + 1].isalnum():
                found[c.entity_id] = (c, m.end())
    return next(iter(found.values())) if len(found) == 1 else None


def effective_facts(context_facts, claims):
    """The facts one check uses. A what-if premise replaces the record for its course and dimension in this check
    only; a newer self-report replaces an older one. A confirmed upload is never replaced by a chat statement,
    so a disagreement with it stays a conflict (memory/eligibility plan, Task 2)."""
    def key(f):
        return f.course_id, fact_dimension(f.state)
    hypothetical = {key(c) for c in claims if c.mode == 'hypothetical'}
    stated = {key(c) for c in claims if c.mode == 'asserted'}
    kept = tuple(f for f in context_facts if key(f) not in hypothetical
                 and not (key(f) in stated and getattr(f, 'source', None) == 'user_statement'))
    return kept + tuple(claims)


def facts_for_term(facts, question: str):
    """An enrollment statement counts only for the term it covers: "taking it this term" cannot satisfy a
    co-requisite of a course asked about for next term (memory/eligibility plan, Task 2). Completion facts and
    upload facts (no period) are unaffected."""
    asked = enrollment_period(question)
    return tuple(f for f in facts if fact_dimension(f.state) != 'enrollment' or f.period in (None, asked))


def conflicting(context_facts, claims) -> tuple[str, ...]:
    """Courses with two different results the check would use (e.g. a statement against a confirmed upload)."""
    states = {}
    for f in effective_facts(context_facts, claims):
        if f.state != 'taken_unknown':
            states.setdefault((f.course_id, fact_dimension(f.state)), set()).add(f.state)
    return tuple(sorted({course for (course, _), s in states.items() if len(s) > 1}))


def _decision(*, route=None, control=None, request=None, missing=(), reason):
    return RoutingDecision(schema_version=RoutingDecision.SCHEMA_VERSION, route=route,
        control=control, confidence=None, predicate_request=request,
        required_facts=tuple(missing), missing_facts=tuple(missing), reason=reason)


def validate_interpretation(text: str, context: RequestContext, interpretation: Interpretation,
                            *, catalog=(), registry: CapabilityRegistry = EMPTY_REGISTRY,
                            documents_available=False, synthetic=False) -> RoutingResult:
    """Caller injects reviewed aliases/capabilities; defaults authorize no evidence path.

    Synthetic injection is for offline testing only. Source-bound institutional runtime
    loading remains outside this router. Validation cannot prove model semantics.
    """
    normalized = prepare_query(text)
    context = RequestContext.parse(context.model_dump(mode='json'))
    p = Interpretation.parse(interpretation.model_dump(mode='json'))
    catalog = tuple(CatalogEntry.parse(c.model_dump(mode='json')) for c in catalog)
    for m in p.mentions:
        if text[m.start:m.end] != m.text:
            raise ValueError('ungrounded_mention')
    for c in p.claims:
        m = p.mentions[c.entity]
        if text[c.start:c.end] != c.text or not c.start <= m.start < m.end <= c.end:
            raise ValueError('ungrounded_claim')
    for part in p.parts:
        if text[part.start:part.end] != part.text:
            raise ValueError('ungrounded_part')
    reference = p.context_reference
    if reference is not None and text[reference.start:reference.end] != reference.text:
        raise ValueError('ungrounded_context_reference')

    program, curriculum = context.program_id, context.curriculum_id
    resolved, ignored = {}, set()
    scope_error, program_choices = None, ()
    # Owner, 23 Oct 2026: a handbook-only question does not depend on program/curriculum, so a
    # phrase that matches no approved name (e.g. "Graduating undergraduate") is ignored there.
    document_only = not p.operations and bool(p.parts) and all(
        part.evidence_need == 'document' for part in p.parts)
    for kind in ('program', 'curriculum'):
        for idx, mention in enumerate(p.mentions):
            if mention.kind != kind:
                continue
            matches = _matches(mention, catalog, program if kind == 'curriculum' else None)
            selected = program if kind == 'program' else curriculum
            if len(matches) > 1:  # a name shared by several entries means the selected one (live: BSHM tracks)
                matches = tuple(m for m in matches if m.entity_id == selected) or matches
            if not matches and document_only:
                ignored.add(idx)
                continue
            if len(matches) != 1:
                scope_error = 'unresolved_entity'
                if kind == 'program' and matches:
                    program_choices = tuple('program_choice:' + m.entity_id for m in matches)
                continue
            entry = matches[0]
            if selected is not None and selected != entry.entity_id:
                scope_error = 'scope_conflict'
                continue
            if kind == 'program':
                program = entry.entity_id
            else:
                curriculum = entry.entity_id
                if program is None:
                    program = entry.program_id  # explicit curriculum identity establishes its program
            resolved[idx] = entry
    previous = context.conversation
    if (previous is not None and (p.operations or reference is not None) and curriculum is None
            and program in (None, previous.program_id)):
        # The previous turn's scope only fills what this message leaves unnamed; a newly named program
        # wins, and a document-only question keeps its own scope, so an unrelated new question is never
        # bound to the earlier turn (owner, 23 Oct 2026).
        program, curriculum = previous.program_id, previous.curriculum_id
    if program is not None and curriculum is None:
        # A program with exactly one reviewed curriculum uses it (owner decision, 24 Oct 2026);
        # several editions (e.g. old and proposed BSCS) still need the student's answer.
        editions = [c for c in catalog if c.kind == 'curriculum' and c.program_id == program]
        if len(editions) == 1:
            curriculum = editions[0].entity_id
    carried = context.conversation.course_id if context.conversation else None
    last = context.conversation
    prior_term = ((last.year_level, last.semester or 'any') if last is not None and last.operation in TERM_OPERATIONS
                  and last.year_level is not None else None)  # owner GUI 3 Nov 2026: follow-up memory
    # Thesis leader 4 Nov 2026: the router's program-switch follow-up names no term; the previous listing's term is it.
    switching = prior_term is not None and p.reason == 'program_switch_follow_up'

    def term_of(words):
        return parse_term(words, prior_term) or (prior_term if switching else None)

    for idx, mention in enumerate(p.mentions):
        if mention.kind == 'term':  # read by the host; a term with no stated year stays unresolved (clarify)
            # Beside a course question, time words only scope the answer and the host reads them from the text
            # (live 4 Nov 2026: "second semester" alone blocked a dependency question); only the target of a term
            # operation must name its own year, which a follow-up may take from the previous question (prior_term).
            term_target = any(o.name in TERM_OPERATIONS and o.target == idx for o in p.operations)
            if term_of(mention.text) is not None or not term_target:
                ignored.add(idx)
            continue
        names_course = program is not None and curriculum is not None and bool(
            _matches(mention, catalog, program, curriculum))
        # Words that name a course are never a back-reference (live F5: "What about CC 4?" -> CC 4).
        if mention.kind == 'course' and reference is not None and not names_course and (
                mention.start, mention.end) == (reference.start, reference.end):
            # The model only marks the words; the course comes from session context and must still be
            # in the request's curriculum, otherwise the mention stays unresolved and the host clarifies.
            entry = next((c for c in catalog if c.kind == 'course' and c.entity_id == carried
                          and c.program_id == program and c.curriculum_id == curriculum), None)
            if carried is not None and entry is not None:
                resolved[idx] = entry
            continue
        if mention.kind == 'course' and program is not None and curriculum is not None and idx not in ignored:
            matches = _matches(mention, catalog, program, curriculum)
            joined = None if matches else _split_code(text, mention, catalog, program, curriculum)
            if joined is not None:
                matches = (joined[0],)
                ignored.update(i for i, other in enumerate(p.mentions) if i != idx and other.kind == 'course'
                               and mention.end <= other.start and other.end <= joined[1])
            if len(matches) == 1:
                resolved[idx] = matches[0]

    claims = []
    course_spans = [(m.start, m.end) for m in p.mentions if m.kind == 'course']
    for idx, claim in enumerate(p.claims):
        course = resolved.get(claim.entity)
        if course is None or claim.mode == 'reported':  # another person's result is no fact about the speaker
            continue
        entity = p.mentions[claim.entity]
        # The host keeps only the result the student's own words state (memory/eligibility plan, Task 1).
        state = stated_result(text, (claim.start, claim.end), (entity.start, entity.end),
                              tuple(s for s in course_spans if s != (entity.start, entity.end)))
        if state is None:
            continue
        mode = 'hypothetical' if claim.mode == 'asserted' and inside_if_clause(text, entity.start) else claim.mode
        identity = f'{context.session_id}:{context.request_id}:{idx}:{course.entity_id}:{state}:{mode}:{claim.start}:{claim.end}'
        claims.append(GroundedClaim(fact_id='fact-' + hashlib.sha256(identity.encode()).hexdigest(),
            session_id=context.session_id, program_id=course.program_id,
            curriculum_id=course.curriculum_id, course_id=course.entity_id, state=state,
            source='user_statement', period=(enrollment_period(claim.text)
                                             if fact_dimension(state) == 'enrollment' else None),
            mode=mode, text=claim.text, start=claim.start, end=claim.end))
    query = NormalizedQuery(schema_version=NormalizedQuery.SCHEMA_VERSION, original_text=text,
        normalized_text=normalized, language_hints={'en':('en',), 'fil':('tl',),
        'taglish':('tl','en'), 'unknown':()}[p.language], intent=p.intent,
        entities=tuple(ResolvedEntity(kind=p.mentions[i].kind, value=c.entity_id,
                       source_ref=c.source_ref) for i, c in sorted(resolved.items())),
        ambiguities=p.ambiguities, negations=tuple(sorted(
            word for word in negation_tokens(text) if word in normalized.casefold())),
        time_qualifiers=tuple(sorted(time_phrases(text))),
        session_fact_refs=tuple(f.fact_id for f in context.facts) + tuple(c.fact_id for c in claims))

    def result(code, control='clarify', missing=(), request=None):
        return RoutingResult(query, _decision(control=control, request=request, missing=missing,
            reason=code.replace('_', ' ')), p, tuple(claims), p.language, code,
            program_id=program, curriculum_id=curriculum)

    if unsupported_language(text):  # English, Filipino and Taglish only (owner, 25 Oct 2026)
        return result('unsupported_language', missing=('language',))
    if p.audience in ('excluded', 'unrelated'):
        return result('unsupported_scope', 'unsupported_scope')
    if p.audience == 'unknown':
        return result('audience_unknown')
    if scope_error:
        return result(scope_error, missing=program_choices if scope_error == 'unresolved_entity' else ())
    if p.ambiguities or p.language == 'unknown':
        return result('model_ambiguity')
    if len(p.operations) > 1:
        return result('compound_request')
    named = {e.entity_id for e in resolved.values() if e.kind == 'program'}
    if (p.control in (None, 'clarify') and not p.operations and not p.claims and reference is None and len(named) == 1
            and len(resolved) == len(p.mentions) and all(m.kind == 'program' for m in p.mentions)
            and all(part.evidence_need == 'unknown' for part in p.parts)
            and not re.search(r'\w', ''.join(c for i, c in enumerate(text) if not any(
                m.start <= i < m.end for m in p.mentions)))):
        # Thesis leader, 4 Nov 2026: a message that is only a program name asks what the student wants to know
        # about it; the model has nothing to call a part ("unknown"), which read as an outage.
        return result('bare_program_name', missing=('program_topic:' + next(iter(named)),))
    if p.control is not None:
        if p.control != 'clarify' and (p.operations or p.claims):
            return result('inconsistent_proposal', 'evidence_unavailable')
        asserted = [c for c in claims if c.mode == 'asserted']
        if p.control == 'clarify' and not p.operations and p.claims and len(asserted) == len(p.claims):
            # A message that only states results (memory/eligibility plan, Task 1): acknowledge the scoped facts.
            return result('facts_noted', missing=tuple(f'noted_{c.state}:{c.course_id}' for c in asserted))
        if p.control == 'clarify' and not (p.operations or p.claims or reference):
            # Nothing named to clarify (live: "Pwede ba mag-shift ng course?"): missing information with an
            # office referral, not a bare "please clarify" (owner E3, 24 Oct 2026).
            return result('empty_clarification', 'evidence_unavailable')
        return result('model_control', p.control)
    if p.route == 'RAG' and p.operations:
        return result('inconsistent_proposal', 'evidence_unavailable')
    # Owner GUI 3 Nov 2026 (image 18): a structured part that only states a grade fact ("Hindi pa ako passed sa
    # BU-2/L.") qualifies the check beside it; it is not a second question needing its own operation.
    def holds_target(part):
        return any(part.start <= p.mentions[p.operations[i].target].start
                   and p.mentions[p.operations[i].target].end <= part.end for i in part.operation_indices)
    if any(part.evidence_need == 'structured' and holds_target(part) for part in p.parts):
        # live: the fact part may also repeat the check whose course lies in the other part
        stated = [part for part in p.parts if part.evidence_need == 'structured' and not holds_target(part)
                  and any(part.start <= c.start and c.end <= part.end for c in p.claims)]
        if stated:
            p = p.model_copy(update=dict(parts=tuple(part for part in p.parts if part not in stated)))
    for part in p.parts:
        for index in part.operation_indices:
            target = p.mentions[p.operations[index].target]
            if not part.start <= target.start < target.end <= part.end:
                return result('part_operation_target_mismatch')
    needs = {part.evidence_need for part in p.parts}
    if 'unknown' in needs:
        return result('unknown_requirement')
    if any(part.evidence_need == 'structured' and not part.operation_indices for part in p.parts):
        return result('unsupported_requirement', 'evidence_unavailable')
    expected = {frozenset({'document'}): 'RAG', frozenset({'structured'}): 'Symbolic',
                frozenset({'document', 'structured'}): 'Hybrid'}[frozenset(needs)]
    covered_operations = {i for part in p.parts for i in part.operation_indices}
    if covered_operations != set(range(len(p.operations))):
        return result('inconsistent_requirements', 'evidence_unavailable')
    # Consistent declared parts decide the route (owner, 25 Oct 2026: roster 18 slip, one structured part with
    # route Hybrid); the model's route label alone never refuses a well-formed request.
    route = expected
    if (route == 'RAG' and p.operations) or (route != 'RAG' and not p.operations):
        return result('inconsistent_proposal', 'evidence_unavailable')
    if p.operations:
        missing = tuple(k for k, v in (('program_id', program), ('curriculum_id', curriculum)) if v is None)
        if missing:
            return result('missing_scope', missing=missing)
    if (p.operations and p.operations[0].name == 'assess_term_prerequisites'
            and parse_term(p.mentions[p.operations[0].target].text) is None and not switching):
        claimed = {c.entity for c in p.claims}
        named = [i for i, m in enumerate(p.mentions) if m.kind == 'course' and i in resolved and i not in claimed]
        if len(named) == 1 and registry.supports('check_prerequisite_eligibility'):
            # Live 4 Nov 2026: with a previous course in context, "Can I take CS 17/L next semester?" was read as
            # a term check on "next semester". One named course with no stated result is the only target the
            # message has, so it is checked on that course; the term words only say when.
            ignored.add(p.operations[0].target)
            data = p.model_dump(mode='json')
            data['operations'][0] = dict(name='check_prerequisite_eligibility', target=named[0])
            p = Interpretation.parse(data)
        else:
            # "next sem" names no year level: ask only for the term (memory/eligibility plan, Task 4); the stated
            # results in this message are still kept by the host.
            return result('missing_term', missing=('term',))
    if len(resolved) + len(ignored) != len(p.mentions):
        unresolved = [m for i, m in enumerate(p.mentions) if i not in resolved and i not in ignored]
        # Owner step 2c (24 Oct 2026): a course that matches no reviewed course of the curriculum ("CS 999") asks
        # for the printed code; an ambiguous match or an unfilled back-reference keeps the plain clarification.
        not_found = curriculum is not None and all(
            m.kind == 'course' and not _matches(m, catalog, program, curriculum)
            and (reference is None or (m.start, m.end) != (reference.start, reference.end)) for m in unresolved)
        if not_found:
            return result('unresolved_entity', missing=('course_id',))
        # Owner, 29 Oct 2026 ("Ask which one"): one course mention that fits several reviewed courses of the
        # curriculum (a repeated printed code or shared title initials) lists them so the reply can name each.
        choices = (_matches(unresolved[0], catalog, program, curriculum)
                   if curriculum is not None and len(unresolved) == 1 and unresolved[0].kind == 'course' else ())
        return result('unresolved_entity', missing=tuple('course_choice:' + c.entity_id for c in choices)
                      if len(choices) > 1 else ())
    disputed = conflicting(context.facts, claims) if p.operations else ()
    if disputed:  # name each disputed course so the reply can say what to fix (memory/eligibility plan, Task 2)
        return result('conflicting_facts', missing=tuple(f'conflict:{course}' for course in disputed))
    request = None
    if p.operations:
        op = p.operations[0]
        if op.name not in OPERATIONS or not registry.supports(op.name):
            return result('unsupported_operation', 'evidence_unavailable')
        if not synthetic:
            return result('institutional_execution_held', 'evidence_unavailable')
        if op.name in TERM_OPERATIONS:
            year, semester = term_of(p.mentions[op.target].text)
            target = (('year_level', str(year)), ('semester', semester))
        else:
            target = (('course_id', resolved[op.target].entity_id),)
        request = PredicateRequest(predicate=op.name, inputs=(
            BoundInput(name='curriculum_id', value=curriculum, fact_ref=None),
            *(BoundInput(name=name, value=value, fact_ref=None) for name, value in target)))
        try:
            registry.goal(request)  # validates fixed signature; never executes the goal
        except UnsupportedRequest:
            return result('unsupported_signature', 'evidence_unavailable')
    if route in ('RAG', 'Hybrid') and not documents_available:
        return result('documents_unavailable', 'evidence_unavailable')
    return RoutingResult(query, _decision(route=route, request=request, reason=p.reason),
        p, tuple(claims), p.language, 'validated', program_id=program, curriculum_id=curriculum)
