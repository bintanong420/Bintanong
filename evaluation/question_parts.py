"""Offline agreement with frozen author labels;not a semantic oracle or runtime gate.

Exact original spans and kinds are a deliberately strict matching policy. Alternate
valid boundaries/claim sets need preserved human adjudication,not silent relabeling.
"""
from typing import Literal

from pydantic import Field, model_validator

from backend.bintanong_contracts.base import Contract, foreign_ids
from backend.bintanong_generation.contracts import Language
from backend.bintanong_generation.requirements import (
    PartID, PartMapping, QuestionPlan, RequirementReview, ReviewIdentity,
    assess_parts, review_identity,
)


class QuestionPartsReference(Contract):
    SCHEMA_VERSION = 'bintanong-question-parts-reference-v1'
    synthetic: Literal[True] = True
    split: Literal['dev'] = 'dev'
    annotation_status: Literal['author_labeled'] = 'author_labeled'
    case_id: str = Field(pattern=r'^[a-z0-9-]+$', min_length=1, max_length=128)
    plan: QuestionPlan
    identity: ReviewIdentity
    expected: tuple[PartMapping, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode='after')
    def _labels(self):
        if foreign_ids(self.case_id, 'institutional'):
            raise ValueError('private_reference_case_id')
        given = [p.part_id for p in self.expected]
        if len(set(given)) != len(given) or set(given) != {p.part_id for p in self.plan.parts}:
            raise ValueError('incomplete_or_duplicate_reference_parts')
        kinds = {p.part_id: p.kind for p in self.plan.parts}
        if any(p.status == 'mapped' and kinds[p.part_id] != 'document' for p in self.expected):
            raise ValueError('reference_requires_unresolved_structured_check')
        return self


class QuestionPartsScore(Contract):
    SCHEMA_VERSION = 'bintanong-question-parts-score-v1'
    evaluation_kind: Literal['synthetic_reference_agreement'] = 'synthetic_reference_agreement'
    candidate_only: Literal[True] = True
    institutional_use_allowed: Literal[False] = False
    activation_allowed: Literal[False] = False
    semantic_completeness: Literal['unverified'] = 'unverified'
    case_id: str
    language: Language
    identity: ReviewIdentity
    reference_identity: ReviewIdentity
    expected_count: int = Field(ge=1, le=8)
    predicted_count: int = Field(ge=1, le=8)
    matched_count: int = Field(ge=0, le=8)
    correct_mapping_count: int = Field(ge=0, le=8)
    exact_span_and_kind_precision: float = Field(ge=0, le=1, allow_inf_nan=False)
    exact_span_and_kind_recall: float = Field(ge=0, le=1, allow_inf_nan=False)
    mapping_recall: float = Field(ge=0, le=1, allow_inf_nan=False)
    missing_reference_parts: tuple[PartID, ...]
    unexpected_candidate_parts: tuple[PartID, ...]
    kind_mismatched_parts: tuple[PartID, ...]
    incorrect_mapping_parts: tuple[PartID, ...]
    ledger_status: Literal['all_declared_parts_mapped', 'unresolved']
    support_errors: tuple[str, ...]
    agrees_with_reference: bool
    false_complete_against_reference: bool


def _span(part):
    return part.start, part.end, part.quote


def _mapping(mapping):
    return mapping.status, frozenset(mapping.claim_ids), mapping.reason


def evaluate_parts(text, integration, plan, draft, review, reference):
    """Compare supplied outputs to author judgments;do not extract or judge semantics."""
    reference = QuestionPartsReference.parse(reference.model_dump(mode='json'))
    plan = QuestionPlan.parse(plan.model_dump(mode='json'))
    review = RequirementReview.parse(review.model_dump(mode='json'))
    ledger = assess_parts(text, integration, plan, draft, review)
    if review_identity(text, integration, reference.plan, draft) != reference.identity:
        raise ValueError('reference_identity_mismatch')
    claim_ids = {c.claim_id for c in draft.claims}
    if any(not set(p.claim_ids) <= claim_ids for p in reference.expected):
        raise ValueError('unknown_reference_claim')
    observed = {_span(p): p for p in plan.parts}
    expected = {p.part_id: p for p in reference.expected}
    mappings = {p.part_id: p for p in review.parts}
    ref_spans = {_span(p) for p in reference.plan.parts}
    missing, wrong_kind, wrong_mapping = [], [], []
    matched = correct = 0
    for part in reference.plan.parts:
        candidate = observed.get(_span(part))
        if candidate is None:
            missing.append(part.part_id)
        elif candidate.kind != part.kind:
            wrong_kind.append(part.part_id)
        else:
            matched += 1
            mapping = mappings.get(candidate.part_id)
            if mapping is not None and _mapping(mapping) == _mapping(expected[part.part_id]):
                correct += 1
                continue
        wrong_mapping.append(part.part_id)
    extra = tuple(p.part_id for p in plan.parts if _span(p) not in ref_spans)
    count, predicted = len(reference.plan.parts), len(plan.parts)
    agrees = matched == count == predicted and correct == count and not ledger.errors
    return QuestionPartsScore(schema_version=QuestionPartsScore.SCHEMA_VERSION,
        case_id=reference.case_id, language=draft.language, identity=ledger.identity,
        reference_identity=reference.identity, expected_count=count, predicted_count=predicted,
        matched_count=matched, correct_mapping_count=correct,
        exact_span_and_kind_precision=matched / predicted, exact_span_and_kind_recall=matched / count,
        mapping_recall=correct / count, missing_reference_parts=tuple(missing),
        unexpected_candidate_parts=extra, kind_mismatched_parts=tuple(wrong_kind),
        incorrect_mapping_parts=tuple(wrong_mapping), ledger_status=ledger.status,
        support_errors=ledger.errors, agrees_with_reference=agrees,
        false_complete_against_reference=ledger.status == 'all_declared_parts_mapped' and not agrees)
