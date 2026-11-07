"""Compose already validated part answers without merging their verdicts."""
import hashlib
import json

from .contracts import AnswerPart, CandidateAnswer
from .ledger_contracts import BoundRequirementLedger, LedgerEntry, ReviewIdentity


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def bind_answers(parts):
    claims, entries, canonical, citations = [], [], [], {}
    for part in parts:
        answer = part.answer
        mapped = answer.status == 'answered'
        ledger = answer.part_ledger
        if ledger is not None and tuple(e.part_id for e in ledger.entries) != (part.part_id,):
            raise ValueError('compound_child_ledger_mismatch')
        if part.evidence_need == 'document':
            if answer.decision is not None or answer.structured_context is not None or ledger and ledger.canonical_parts:
                raise ValueError('document_part_has_symbolic_witness')
        elif mapped and (answer.decision is None or answer.structured_context is None or ledger is None
                or ledger.canonical_parts != (part.part_id,) or answer.claims
                or answer.structured_context.operation != 'check_prerequisite_eligibility'):
            raise ValueError('structured_part_missing_canonical_witness')
        for card in answer.citations:
            if card.evidence_id in citations and citations[card.evidence_id] != card:
                raise ValueError('compound_citation_payload_mismatch')
            citations[card.evidence_id] = card
        refs = []
        if mapped:
            for claim in answer.claims:
                claim_id = f'c{len(claims)+1}'
                if len(claims) == 8:
                    raise ValueError('compound_claim_limit')
                claims.append(claim.model_copy(update={'claim_id': claim_id}))
                refs.append(claim_id)
            if part.evidence_need == 'structured':
                canonical.append(part.part_id)
        entries.append(LedgerEntry(part_id=part.part_id, status='mapped' if mapped else 'unavailable',
            claim_ids=tuple(refs), reason=None if mapped else 'uncertain'))
    return tuple(claims), tuple(entries), tuple(canonical), tuple(citations.values())


async def generate_compound(generator, text, integration, *, remaining_seconds=None):
    from ..bintanong_orchestration.contracts import IntegrationResult
    integration = IntegrationResult.parse(integration.model_dump(mode='json'))
    plan = integration.execution_plan
    if plan is None or integration.understanding.question_sha256 != hashlib.sha256(text.encode()).hexdigest():
        raise ValueError('compound_question_mismatch')
    import asyncio
    started = asyncio.get_running_loop().time()
    parts = []
    for step, child in zip(plan.steps, integration.execution_parts):
        remaining = None if remaining_seconds is None else max(0, remaining_seconds -
            (asyncio.get_running_loop().time() - started))
        answer = await generator.generate(text, child, remaining_seconds=remaining)
        parts.append(AnswerPart(part_id=step.part_id, evidence_need=step.evidence_need, answer=answer))
    claims, entries, canonical, citations = bind_answers(parts)
    mapped = sum(e.status == 'mapped' for e in entries)
    ledger = BoundRequirementLedger(schema_version=BoundRequirementLedger.SCHEMA_VERSION,
        status='all_declared_parts_mapped' if mapped == len(parts) else
               'some_parts_unavailable' if mapped else 'unresolved',
        identity=ReviewIdentity(schema_version=ReviewIdentity.SCHEMA_VERSION,
            requirements_sha256=_digest(integration.understanding.model_dump(mode='json')),
            draft_sha256=_digest([p.model_dump(mode='json') for p in parts])),
        entries=tuple(entries), canonical_parts=tuple(canonical))
    status = 'answered' if mapped else ('clarification_needed' if any(
        p.answer.status == 'clarification_needed' for p in parts) else parts[0].answer.status)
    language = parts[0].answer.language
    label = 'Part' if language == 'en' else 'Bahagi'
    return CandidateAnswer(schema_version=CandidateAnswer.SCHEMA_VERSION,
        request_id=integration.request_id, release_id=plan.release_id, language=language,
        status=status, text='\n\n'.join(f'{label} {n}\n{p.answer.text}' for n, p in enumerate(parts, 1)),
        decision=None, dependencies=None, claims=claims, citations=citations,
        missing_facts=tuple(dict.fromkeys(f for p in parts for f in p.answer.missing_facts)),
        validation='validated' if mapped else 'control_fallback', part_ledger=ledger,
        draft_attempts=max(p.answer.draft_attempts for p in parts),
        check_attempts=max(p.answer.check_attempts for p in parts),
        answer_repairs=max(p.answer.answer_repairs for p in parts), part_answers=tuple(parts),
        research_ref=next((p.answer.research_ref for p in parts if p.answer.research_ref), None))
