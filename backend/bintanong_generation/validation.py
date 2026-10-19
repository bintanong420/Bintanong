"""Deterministic boundaries and complete (but semantically fallible) prose verdicts."""
from ..bintanong_contracts.base import foreign_ids


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
    return tuple(errors)


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
    if (answer.request_id!=pack.request_id or answer.release_id!=pack.release_id
            or answer.language!=pack.language or answer.decision!=pack.decision
            or answer.dependencies!=pack.dependencies or answer.structured_context!=pack.structured_context):
        raise ValueError('final_identity_or_decision_mismatch')
    if answer.text!=render_text(pack,claims,answer.status):
        raise ValueError('final_render_mismatch')
    if answer.citations!=selected_cards(pack,claims):
        raise ValueError('final_citation_mismatch')
    if answer.claims!=tuple(claims):
        raise ValueError('final_claim_mapping_mismatch')
    if foreign_ids(answer.text,'institutional'):
        raise ValueError('private_final_reference')
