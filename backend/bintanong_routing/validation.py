"""Exact reviewed-alias resolution and effective decisions, without tool execution."""
from __future__ import annotations

import hashlib
from copy import deepcopy
from dataclasses import dataclass

from ..bintanong_contracts.runtime import BoundInput, NormalizedQuery, PredicateRequest, ResolvedEntity, RoutingDecision, negation_tokens, time_phrases
from ..bintanong_contracts.symbolic import CapabilityRegistry, EMPTY_REGISTRY, UnsupportedRequest
from .contracts import CatalogEntry, Interpretation, RequestContext, ScopedFact, prepare_query
from .style import StyleEvidence

OPERATIONS = ('check_prerequisite_eligibility', 'list_missing_prerequisites', 'list_affected_courses')


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

    @property
    def inference_calls(self):
        return self.attempts + self.style_attempts

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
    return tuple(c for c in catalog if c.kind == mention.kind
                 and (program is None or c.program_id == program)
                 and (curriculum is None or c.curriculum_id == curriculum)
                 and _key(mention.text) in {_key(a) for a in c.aliases})


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

    program, curriculum = context.program_id, context.curriculum_id
    resolved = {}
    scope_error = None
    for kind in ('program', 'curriculum'):
        for idx, mention in enumerate(p.mentions):
            if mention.kind != kind:
                continue
            matches = _matches(mention, catalog, program if kind == 'curriculum' else None)
            if len(matches) != 1:
                scope_error = 'unresolved_entity'
                continue
            entry = matches[0]
            selected = program if kind == 'program' else curriculum
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
    for idx, mention in enumerate(p.mentions):
        if mention.kind == 'course' and program is not None and curriculum is not None:
            matches = _matches(mention, catalog, program, curriculum)
            if len(matches) == 1:
                resolved[idx] = matches[0]

    claims = []
    for idx, claim in enumerate(p.claims):
        course = resolved.get(claim.entity)
        if course is None:
            continue
        identity = f'{context.session_id}:{context.request_id}:{idx}:{course.entity_id}:{claim.state}:{claim.mode}:{claim.start}:{claim.end}'
        claims.append(GroundedClaim(fact_id='fact-' + hashlib.sha256(identity.encode()).hexdigest(),
            session_id=context.session_id, program_id=course.program_id,
            curriculum_id=course.curriculum_id, course_id=course.entity_id, state=claim.state,
            mode=claim.mode, text=claim.text, start=claim.start, end=claim.end))
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

    if p.audience in ('excluded', 'unrelated'):
        return result('unsupported_scope', 'unsupported_scope')
    if p.audience == 'unknown':
        return result('audience_unknown')
    if scope_error:
        return result(scope_error)
    if p.ambiguities or p.language == 'unknown':
        return result('model_ambiguity')
    if len(p.operations) > 1:
        return result('compound_request')
    if p.control is not None:
        if p.control != 'clarify' and (p.operations or p.claims):
            return result('inconsistent_proposal', 'evidence_unavailable')
        return result('model_control', p.control)
    if p.route == 'RAG' and p.operations:
        return result('inconsistent_proposal', 'evidence_unavailable')
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
    if p.route != expected or covered_operations != set(range(len(p.operations))):
        return result('inconsistent_requirements', 'evidence_unavailable')
    if (p.route == 'RAG' and p.operations) or (p.route != 'RAG' and not p.operations):
        return result('inconsistent_proposal', 'evidence_unavailable')
    if p.operations:
        missing = tuple(k for k, v in (('program_id', program), ('curriculum_id', curriculum)) if v is None)
        if missing:
            return result('missing_scope', missing=missing)
    if len(resolved) != len(p.mentions):
        return result('unresolved_entity')
    if any(c.mode != 'asserted' for c in claims):
        return result('nonasserted_facts')
    states = {}
    for f in (*context.facts, *claims):
        states.setdefault(f.course_id, set()).add(f.state)
    if p.operations and any({'passed','failed'} <= s or {'enrolled','not_enrolled'} <= s for s in states.values()):
        return result('conflicting_facts')
    request = None
    if p.operations:
        op = p.operations[0]
        if op.name not in OPERATIONS or not registry.supports(op.name):
            return result('unsupported_operation', 'evidence_unavailable')
        if not synthetic:
            return result('institutional_execution_held', 'evidence_unavailable')
        course = resolved[op.target]
        request = PredicateRequest(predicate=op.name, inputs=(
            BoundInput(name='curriculum_id', value=curriculum, fact_ref=None),
            BoundInput(name='course_id', value=course.entity_id, fact_ref=None)))
        try:
            registry.goal(request)  # validates fixed signature; never executes the goal
        except UnsupportedRequest:
            return result('unsupported_signature', 'evidence_unavailable')
    if p.route in ('RAG', 'Hybrid') and not documents_available:
        return result('documents_unavailable', 'evidence_unavailable')
    return RoutingResult(query, _decision(route=p.route, request=request, reason=p.reason),
        p, tuple(claims), p.language, 'validated', program_id=program, curriculum_id=curriculum)
