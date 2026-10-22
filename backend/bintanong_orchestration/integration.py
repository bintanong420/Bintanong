"""Conservative release and outcome policy; no generated answer or semantic guesses."""
from .contracts import CandidateEvidence, DocumentResult, ReleasePin


def assemble(pin, route, *, documents=None, symbolic=None, dependencies=None):
    pin = ReleasePin.parse(pin.model_dump(mode='json'))
    if documents is not None:
        documents = DocumentResult.parse(documents.model_dump(mode='json'))
    data = dict(schema_version=CandidateEvidence.SCHEMA_VERSION, pin=pin, route=route,
        documents=documents, symbolic=symbolic, dependencies=dependencies,
        status='ready', permitted_scope='document_explanation' if route == 'RAG' else
        'combined_explanation' if route == 'Hybrid' else
        'dependency_listing' if dependencies is not None else 'scoped_prerequisite_check')
    # Validate component shape and reject offline/real-rule subtypes BEFORE copying.
    checked = CandidateEvidence(**data)
    result = symbolic if symbolic is not None else dependencies
    status = None
    sources = {s.version_id:s.byte_sha256 for s in pin.sources}
    members = {d.chunk_id:(d.version_id,d.byte_sha256) for d in pin.documents}
    if documents is not None:
        if documents.release_id != pin.release_id or any(
                members.get(p.chunk_id) != (c.version_id,c.byte_sha256)
                for p in documents.passages for c in p.citations):
            status = 'release_mismatch'
    if result is not None:
        if ((result.scope is not None and result.scope.knowledge_release_id != pin.release_id)
                or (result.rule_bundle_version is not None and
                    result.rule_bundle_version != pin.rule_bundle_version)
                or any(sources.get(s.version_id) != s.byte_sha256 for s in result.rule_spans)):
            status = 'release_mismatch'
    missing, conflicts = (), ()
    if symbolic is not None:
        missing = symbolic.decision.missing_facts
        conflicts = symbolic.decision.unresolved_conflicts
        if status is None and symbolic.decision.outcome not in ('eligible','ineligible'):
            status = 'conflict' if conflicts else symbolic.decision.outcome
    if dependencies is not None and status is None and dependencies.status != 'complete':
        status = {'partial':'unknown', 'unsupported':'unsupported', 'error':'error'}[dependencies.status]
    if documents is not None:
        doc_status = {'conflicting_sources':'conflict', 'release_changed':'release_mismatch',
            'needs_scope':'clarify', 'uncalibrated':'uncalibrated',
            'insufficient_evidence':'no_evidence', 'unassessed':'no_evidence',
            'needs_subject':'clarify', 'needs_claims':'clarify'}.get(documents.status)
        if documents.status != 'ok':
            doc_status = doc_status or 'error'
        elif not documents.passages or documents.gaps:
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
