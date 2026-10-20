"""Detached declared-part ledger. No extraction, semantic oracle, or answer release.

Nested records share their enclosing contract's version. Quotes are untrusted data;
offsets and the question digest always refer to the exact original Python string.
"""
import hashlib
import json
from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Contract, Record, foreign_ids
from ..bintanong_orchestration.contracts import ReleaseID
from ..bintanong_routing.contracts import prepare_query
from .contracts import AnswerDraft, ClaimID, SupportReport
from .evidence import prepare
from .validation import validate_draft, validate_support

PartID = Annotated[str, Field(pattern=r'^r[1-8]$')]
Digest = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]
UnavailableReason = Literal['not_in_evidence', 'source_gap', 'structured_check_not_run', 'uncertain']


class Requirement(Record):
    part_id: PartID
    start: int = Field(ge=0, lt=8192)
    end: int = Field(ge=1, le=8192)
    quote: str = Field(min_length=1, max_length=8192)
    kind: Literal['document', 'structured', 'unknown']

    @model_validator(mode='after')
    def _span(self):
        if self.end <= self.start or len(self.quote) != self.end - self.start or not self.quote.strip():
            raise ValueError('invalid_question_span')
        return self


class QuestionPlan(Contract):
    SCHEMA_VERSION = 'bintanong-question-plan-v1'
    release_id: ReleaseID
    question_sha256: Digest
    parts: tuple[Requirement, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode='after')
    def _unique(self):
        if len({p.part_id for p in self.parts}) != len(self.parts):
            raise ValueError('duplicate_part_id')
        if len({(p.start, p.end) for p in self.parts}) != len(self.parts):
            raise ValueError('duplicate_question_span')
        return self


class PartMapping(Record):
    part_id: PartID
    status: Literal['mapped', 'unavailable', 'uncertain']
    claim_ids: tuple[ClaimID, ...] = Field(default=(), max_length=8)
    reason: UnavailableReason | None = None

    @model_validator(mode='after')
    def _state(self):
        if len(set(self.claim_ids)) != len(self.claim_ids):
            raise ValueError('duplicate_mapped_claim')
        if self.status == 'mapped':
            if not self.claim_ids or self.reason is not None:
                raise ValueError('mapped_requires_claims_only')
        elif self.claim_ids or self.reason is None:
            raise ValueError('unresolved_requires_reason_only')
        return self


class ReviewIdentity(Contract):
    SCHEMA_VERSION = 'bintanong-part-review-identity-v1'
    requirements_sha256: Digest
    draft_sha256: Digest


class RequirementReview(Contract):
    SCHEMA_VERSION = 'bintanong-part-review-v1'
    requirements_sha256: Digest
    draft_sha256: Digest
    parts: tuple[PartMapping, ...] = Field(min_length=1, max_length=8)
    support: SupportReport

    @model_validator(mode='after')
    def _unique(self):
        if len({p.part_id for p in self.parts}) != len(self.parts):
            raise ValueError('duplicate_part_mapping')
        return self


class LedgerEntry(Record):
    part_id: PartID
    status: Literal['mapped', 'missing', 'unavailable', 'uncertain', 'unresolved']
    claim_ids: tuple[ClaimID, ...] = Field(default=(), max_length=8)
    reason: Literal['not_in_evidence', 'source_gap', 'structured_check_not_run', 'uncertain',
                    'missing_mapping', 'unknown_requirement_kind'] | None = None


class RequirementLedger(Contract):
    SCHEMA_VERSION = 'bintanong-requirement-ledger-v1'
    candidate_only: Literal[True] = True
    institutional_use_allowed: Literal[False] = False
    activation_allowed: Literal[False] = False
    semantic_completeness: Literal['unverified'] = 'unverified'
    status: Literal['all_declared_parts_mapped', 'unresolved']
    identity: ReviewIdentity
    entries: tuple[LedgerEntry, ...] = Field(min_length=1, max_length=8)
    errors: tuple[Literal['incomplete_support_verdicts', 'unsupported_claim', 'language_unsupported',
                          'scope_unsupported', 'unmapped_claim'], ...] = ()


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                    separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def _prepare(text, integration):
    prepare_query(text)  # Validate only; do not normalize the offsets or digest.
    if foreign_ids(text, 'institutional'):
        raise ValueError('private_question_reference')
    pack = prepare(integration)
    if pack.status != 'ready' or pack.route != 'RAG':
        raise ValueError('requirements_need_ready_rag')
    return pack


def _check_plan(text, pack, plan):
    plan = QuestionPlan.parse(plan.model_dump(mode='json'))
    if plan.release_id != pack.release_id or plan.question_sha256 != hashlib.sha256(text.encode('utf-8')).hexdigest():
        raise ValueError('question_plan_identity_mismatch')
    if any(p.end > len(text) or text[p.start:p.end] != p.quote for p in plan.parts):
        raise ValueError('question_quote_mismatch')
    return plan


def create_plan(text, integration, parts):
    """Bind supplied requirements, without extracting or certifying their completeness."""
    pack = _prepare(text, integration)
    values = [p.model_dump(mode='json') if isinstance(p, Requirement) else p for p in parts]
    plan = QuestionPlan.parse(dict(schema_version=QuestionPlan.SCHEMA_VERSION,
        release_id=pack.release_id, question_sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(), parts=values))
    return _check_plan(text, pack, plan)


def _checked(text, integration, plan, draft):
    pack = _prepare(text, integration)
    plan = _check_plan(text, pack, plan)
    draft = AnswerDraft.parse(draft.model_dump(mode='json'))
    errors = validate_draft(draft, pack)
    document_ids = {c.evidence_id for c in pack.cards if c.kind == 'document'}
    if errors or any(not set(c.evidence_ids) <= document_ids for c in draft.claims):
        raise ValueError('invalid_requirements_draft')
    return pack, plan, draft


def _identity(text, pack, plan, draft):
    return ReviewIdentity(schema_version=ReviewIdentity.SCHEMA_VERSION,
        requirements_sha256=_digest(dict(request_id=pack.request_id, release_id=pack.release_id,
            question=text, language=pack.language, plan=plan.model_dump(mode='json'),
            sources=[c.model_dump(mode='json') for c in pack.cards])),
        draft_sha256=_digest(draft.model_dump(mode='json')))


def review_identity(text, integration, plan, draft):
    """Bind the exact request/plan/cards and draft. Hashes do not prove semantic truth."""
    pack, plan, draft = _checked(text, integration, plan, draft)
    return _identity(text, pack, plan, draft)


def assess_parts(text, integration, plan, draft, review):
    """Return host bookkeeping for an untrusted review; never an answer or release."""
    pack, plan, draft = _checked(text, integration, plan, draft)
    review = RequirementReview.parse(review.model_dump(mode='json'))
    identity = _identity(text, pack, plan, draft)
    if (review.requirements_sha256 != identity.requirements_sha256 or
            review.draft_sha256 != identity.draft_sha256):
        raise ValueError('part_review_identity_mismatch')
    part_ids = {p.part_id for p in plan.parts}
    claim_ids = {c.claim_id for c in draft.claims}
    if any(p.part_id not in part_ids or not set(p.claim_ids) <= claim_ids for p in review.parts):
        raise ValueError('unknown_part_or_claim_mapping')
    mapped = {p.part_id: p for p in review.parts}
    errors = list(validate_support(review.support, draft))
    if claim_ids != {c for p in review.parts for c in p.claim_ids}:
        errors.append('unmapped_claim')
    entries = []
    for part in plan.parts:
        mapping = mapped.get(part.part_id)
        if mapping is None:
            entry = LedgerEntry(part_id=part.part_id, status='missing', reason='missing_mapping')
        elif part.kind != 'document':
            reason = 'structured_check_not_run' if part.kind == 'structured' else 'unknown_requirement_kind'
            entry = LedgerEntry(part_id=part.part_id, status='unresolved', reason=reason,
                                claim_ids=mapping.claim_ids)
        else:
            entry = LedgerEntry(**mapping.model_dump())
        entries.append(entry)
    complete = not errors and all(e.status == 'mapped' for e in entries)
    return RequirementLedger(schema_version=RequirementLedger.SCHEMA_VERSION,
        status='all_declared_parts_mapped' if complete else 'unresolved', identity=identity,
        entries=tuple(entries), errors=tuple(errors))
