"""Conservative release and outcome policy; no generated answer or semantic guesses."""
from .contracts import CandidateEvidence, DocumentResult, ReleasePin


def _identity_pinned(pin, result):
    release, version = pin.release_id, pin.rule_bundle_version
    if pin.curricula:  # multi-curriculum research release: the requested curriculum's own runtime
        curriculum = next((i.value for i in result.inputs if i.name == 'curriculum_id'), None)
        member = next((m for m in pin.curricula if m.curriculum_id == curriculum), None)
        if member is None:
            return False
        release, version = member.release_id, member.rule_bundle_version
    return ((result.scope is None or result.scope.knowledge_release_id == release)
            and (getattr(result, 'rule_bundle_version', None) in (None, version)))


def assemble(pin, route, *, documents=None, symbolic=None, dependencies=None, course_facts=None, term_assessment=None, plan_check=None, plan_routes=None, earliest_term=None, plan_route_sources=None):
    pin = ReleasePin.parse(pin.model_dump(mode='json'))
    if documents is not None:
        documents = DocumentResult.parse(documents.model_dump(mode='json'))
    data = dict(schema_version=CandidateEvidence.SCHEMA_VERSION, pin=pin, route=route,
        documents=documents, symbolic=symbolic, dependencies=dependencies,
        status='ready', permitted_scope='document_explanation' if route == 'RAG' else
        'combined_explanation' if route == 'Hybrid' else
        'dependency_listing' if dependencies is not None else
        'course_facts_listing' if course_facts is not None else
        'earliest_term_assessment' if earliest_term is not None else
        'study_plan_check' if plan_check is not None else
        'term_prerequisite_listing' if term_assessment is not None else 'scoped_prerequisite_check')
    if course_facts is not None:
        data['course_facts'] = course_facts
    if term_assessment is not None:
        data['term_assessment'] = term_assessment
    if plan_check is not None:
        data['plan_check'] = plan_check
    if plan_routes is not None:
        data['plan_routes'] = plan_routes
    if plan_route_sources is not None:
        data['plan_route_sources'] = plan_route_sources
    if earliest_term is not None:
        data['earliest_term'] = earliest_term
    # Validate component shape and reject offline/real-rule subtypes BEFORE copying.
    checked = CandidateEvidence(**data)
    result = next((r for r in (symbolic, dependencies, course_facts, term_assessment, earliest_term) if r is not None), None)
    status = None
    sources = {s.version_id:s.byte_sha256 for s in pin.sources}
    members = {d.chunk_id:(d.version_id,d.byte_sha256) for d in pin.documents}
    if documents is not None:
        observations = (documents, *documents.topic_outcomes)
        if any(o.release_id != pin.release_id for o in observations) or any(
                members.get(p.chunk_id) != (c.version_id,c.byte_sha256)
                for o in observations for p in o.passages for c in p.citations):
            status = 'release_mismatch'
    if result is not None:
        if (not _identity_pinned(pin, result)
                or any(sources.get(s.version_id) != s.byte_sha256 for s in getattr(result, 'rule_spans', ()))
                or any(c.version_id not in sources for c in getattr(result, 'courses', ()))):
            status = 'release_mismatch'
    if plan_check is not None:
        curriculum = plan_check.curriculum_id
        member = next((m for m in pin.curricula if m.curriculum_id == curriculum), None)
        expected = pin.release_id if not pin.curricula else None if member is None else member.release_id
        if (plan_check.scope is None or plan_check.scope.knowledge_release_id != expected
                or any(sources.get(s.version_id) != s.byte_sha256 for s in plan_check.rule_spans)):
            status = 'release_mismatch'
    if earliest_term is not None and status is None and earliest_term.status != 'found':
        status = 'no_evidence'
    missing, conflicts = (), ()
    if symbolic is not None:
        missing = symbolic.decision.missing_facts
        conflicts = symbolic.decision.unresolved_conflicts
        if status is None and symbolic.decision.outcome not in ('eligible','ineligible'):
            status = 'conflict' if conflicts else symbolic.decision.outcome
    if dependencies is not None and status is None and dependencies.status not in ('complete', 'partial'):
        # A partial list is answered with its limitation named (owner report, 4 Nov 2026), never as a bare clarify.
        status = {'unsupported':'unsupported', 'error':'error'}[dependencies.status]
    if course_facts is not None and status is None and course_facts.status != 'complete':
        # Unreviewed or unknown facts are missing information (E1 referral), never guessed.
        status = {'not_reviewed':'no_evidence', 'not_found':'no_evidence', 'unsupported':'unsupported'}[course_facts.status]
    if term_assessment is not None and status is None and term_assessment.status not in ('complete', 'partial',
                                                                                        'not_covered'):
        # A covered term is answered; a term the source does not include is answered as a coverage gap.
        status = {'not_reviewed':'no_evidence', 'not_found':'no_evidence', 'unsupported':'unsupported'}[
            term_assessment.status]
    if documents is not None:
        doc_status = {'conflicting_sources':'conflict', 'release_changed':'release_mismatch',
            'needs_scope':'clarify', 'uncalibrated':'uncalibrated',
            'insufficient_evidence':'no_evidence', 'unassessed':'no_evidence',
            # No reviewed topic matched: missing information, not something the student can clarify (owner E1).
            'needs_subject':'no_evidence', 'needs_claims':'clarify'}.get(documents.status)
        if documents.status not in ('ok', 'partial'):
            doc_status = doc_status or 'error'
        elif not documents.passages or documents.status == 'ok' and documents.gaps:
            doc_status = 'no_evidence'
        # Both observations stay in the package. Availability cannot conceal a
        # conflict or operational failure in the other required branch.
        priority = {name:rank for rank,name in enumerate((None,'uncalibrated','no_evidence',
            'clarify','unknown','unsupported','error','conflict','release_mismatch'))}
        if priority[doc_status] > priority[status]:
            status = doc_status
    return checked.model_copy(update=dict(status=status or 'ready',
        permitted_scope='none' if status else checked.permitted_scope,
        missing_facts=missing, conflicts=conflicts))
