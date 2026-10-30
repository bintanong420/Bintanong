"""Deterministic boundaries and complete (but semantically fallible) prose verdicts."""
from ..bintanong_contracts.base import foreign_ids
from .service_cutoff import cutoff_errors
from .malformed_condition import malformed_errors


def validate_draft(draft,pack):
    errors=[]
    if draft.release_id!=pack.release_id: errors.append('wrong_release')
    if draft.language!=pack.language: errors.append('wrong_language')
    expected=pack.decision.outcome if pack.decision else None
    if draft.decision_outcome!=expected: errors.append('wrong_outcome')
    document_ids={c.evidence_id for c in pack.cards if c.kind=='document'}
    if pack.route in ('RAG','Hybrid') and not any(document_ids.intersection(c.evidence_ids)
                                               for c in draft.claims):
        errors.append('missing_document_claim')
    allowed={c.evidence_id for c in pack.cards}
    if any(not set(c.evidence_ids)<=allowed for c in draft.claims): errors.append('unknown_evidence')
    if any(not c.text.strip() for c in draft.claims): errors.append('empty_claim')
    if foreign_ids([c.text for c in draft.claims],'institutional'): errors.append('private_reference')
    return tuple(errors)+cutoff_errors(pack,draft.claims)+malformed_errors(pack,draft.claims)


def validate_support(report,draft):
    expected={c.claim_id for c in draft.claims}
    given=[v.claim_id for v in report.verdicts]
    errors=[]
    if set(given)!=expected or len(given)!=len(expected): errors.append('incomplete_support_verdicts')
    if any(v.verdict!='supported' for v in report.verdicts): errors.append('unsupported_claim')
    if not report.language_appropriate: errors.append('language_unsupported')
    if not report.within_scope: errors.append('scope_unsupported')
    return tuple(errors)


def validate_final(answer,pack,claims):
    from .render import render_text,selected_cards
    from .understanding import validate_ledger
    if (answer.request_id!=pack.request_id or answer.release_id!=pack.release_id
            or answer.language!=pack.language or answer.decision!=pack.decision
            or answer.dependencies!=pack.dependencies or answer.structured_context!=pack.structured_context):
        raise ValueError('final_identity_or_decision_mismatch')
    if answer.research_ref!=pack.research_ref:
        raise ValueError('final_research_reference_mismatch')
    if answer.missing_facts!=pack.missing_facts:
        raise ValueError('final_missing_facts_mismatch')
    if answer.decision_guard is not None and (pack.route!='RAG' or pack.status!='ready'):
        raise ValueError('guard_requires_ready_rag')
    if answer.question_coverage is not None and (pack.route!='RAG' or pack.status!='ready'):
        raise ValueError('coverage_requires_ready_rag')
    if answer.text!=render_text(pack,claims,answer.status,decision_withheld=answer.validation=='decision_withheld',
                               question_uncovered=answer.validation in ('question_uncovered','parts_unresolved'),
                               ledger=answer.part_ledger,thanked=answer.validation=='thanks'):
        raise ValueError('final_render_mismatch')
    if answer.citations!=selected_cards(pack,claims):
        raise ValueError('final_citation_mismatch')
    if answer.claims!=tuple(claims):
        raise ValueError('final_claim_mapping_mismatch')
    if answer.claims and pack.status!='ready':
        from .deadline_conflict import unresolved_deadline_context
        expected=unresolved_deadline_context(pack)
        actual=tuple(dict(text=c.text,evidence_ids=list(c.evidence_ids)) for c in claims)
        if (answer.status!='source_conflict' or answer.validation!='control_fallback'
                or not expected or actual!=expected):
            raise ValueError('final_source_conflict_context_mismatch')
    if cutoff_errors(pack,claims):
        raise ValueError('final_service_cutoff_fidelity')
    if malformed_errors(pack,claims):
        raise ValueError('final_malformed_source_fidelity')
    validate_ledger(pack,claims,answer.part_ledger,answered=answer.status=='answered')
    if answer.status=='answered' and answer.part_ledger is not None:
        from .part_answers import record_coverage_errors
        slots={e.part_id:(e.status,e.claim_ids) for e in answer.part_ledger.entries}
        if record_coverage_errors(pack,claims,slots):
            raise ValueError('final_record_coverage_mismatch')
    if foreign_ids(answer.text,'institutional'):
        raise ValueError('private_final_reference')
