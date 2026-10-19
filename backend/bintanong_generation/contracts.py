"""Model proposals are untrusted; only host code constructs candidate answers."""
from typing import Annotated,Literal

from pydantic import Field,model_validator

from ..bintanong_contracts.base import Contract,Record
from ..bintanong_contracts.symbolic import DecisionOutcome,DecisionScope
from ..bintanong_contracts.runtime import BoundInput
from ..bintanong_orchestration.contracts import DocumentCitation,ReleaseID
from ..bintanong_symbolic.runtime import DependencyResult

Language=Literal['en','fil','taglish','unknown']
Outcome=Literal['eligible','ineligible','unknown','unsupported','error']
EvidenceID=Annotated[str,Field(pattern=r'^ev-[0-9a-f]{64}$')]
ClaimID=Annotated[str,Field(pattern=r'^c[1-8]$')]


class EvidenceCard(Record):
    evidence_id: EvidenceID
    kind: Literal['document','rule']
    text: str=Field(min_length=1,max_length=32768)
    citations: tuple[DocumentCitation,...]=Field(min_length=1)


class ProseClaim(Record):
    claim_id: ClaimID
    text: str=Field(min_length=1,max_length=1200)
    evidence_ids: tuple[EvidenceID,...]=Field(min_length=1,max_length=8)

    @model_validator(mode='after')
    def _refs(self):
        if len(set(self.evidence_ids))!=len(self.evidence_ids):
            raise ValueError('duplicate_evidence_reference')
        return self


class AnswerDraft(Contract):
    SCHEMA_VERSION='bintanong-answer-draft-v1'
    language: Language
    release_id: ReleaseID
    decision_outcome: Outcome|None
    claims: tuple[ProseClaim,...]=Field(max_length=8)

    @model_validator(mode='after')
    def _unique(self):
        if len({c.claim_id for c in self.claims})!=len(self.claims):
            raise ValueError('duplicate_claim_id')
        return self


class ClaimVerdict(Record):
    claim_id: ClaimID
    verdict: Literal['supported','unsupported','contradiction','unknown']


class SupportReport(Contract):
    SCHEMA_VERSION='bintanong-prose-support-v1'
    verdicts: tuple[ClaimVerdict,...]=Field(max_length=8)
    language_appropriate: bool
    within_scope: bool


class StructuredContext(Record):
    operation: str=Field(min_length=1,max_length=128)
    inputs: tuple[BoundInput,...]
    scope: DecisionScope|None
    rule_bundle_version: str|None

    @model_validator(mode='after')
    def _no_private_refs(self):
        if any(i.fact_ref is not None for i in self.inputs):
            raise ValueError('private_fact_refs_not_permitted')
        return self


class CandidateAnswer(Contract):
    SCHEMA_VERSION='bintanong-candidate-answer-v1'
    candidate_only: Literal[True]=True
    institutional_use_allowed: Literal[False]=False
    activation_allowed: Literal[False]=False
    request_id: str=Field(pattern=r'^req-[a-z0-9-]+$')
    release_id: ReleaseID|None
    language: Language
    status: Literal['answered','clarification_needed','source_conflict','insufficient_evidence',
        'out_of_scope','temporarily_unavailable','greeting','abstained']
    text: str=Field(min_length=1,max_length=65536)
    decision: DecisionOutcome|None
    dependencies: DependencyResult|None
    structured_context: StructuredContext|None=None
    missing_facts: tuple[Annotated[str,Field(min_length=1)],...]=()
    claims: tuple[ProseClaim,...]=()
    citations: tuple[EvidenceCard,...]
    validation: Literal['validated','control_fallback','repair_exhausted','timeout','tool_error']
    draft_attempts: int=Field(ge=0,le=2)
    check_attempts: int=Field(ge=0,le=2)
    answer_repairs: int=Field(ge=0,le=1)

    @model_validator(mode='after')
    def _limits(self):
        if self.answer_repairs!=max(self.draft_attempts-1,0):
            raise ValueError('repair_counter_mismatch')
        if self.check_attempts>self.draft_attempts:
            raise ValueError('checker_counter_mismatch')
        if self.status=='answered' and self.validation!='validated':
            raise ValueError('unvalidated_answer')
        if self.decision is not None and not self.decision.synthetic:
            raise ValueError('synthetic_decision_required')
        return self
