"""Internal candidate evidence, separate from institutional answer contracts."""
import json
from typing import Annotated, Literal

from pydantic import Field, model_serializer, model_validator

from ..bintanong_contracts.base import Contract, Record, Route
from ..bintanong_contracts.governance import ID_VER, SHA256
from ..bintanong_contracts.source import SpanLocator
from ..bintanong_contracts.symbolic import SymbolicResult
from ..bintanong_symbolic.course_facts import CourseFactsResult
from .term_assessment import TermAssessmentResult
from .earliest_term import EarliestTermAssessment
from ..bintanong_symbolic.runtime import DependencyResult, ResearchDependencyResult, ResearchSymbolicResult
from ..bintanong_contracts.runtime import PredicateRequest
from ..bintanong_routing.contracts import RequestPart, Operation
from ..bintanong_planning.contracts import RecoveryResult, PlanCheckResult, RecoveryRoutes
from .reasons import ReasonCode

Text = Annotated[str, Field(min_length=1)]
ReleaseID = Annotated[str, Field(pattern=r'^release-[a-z0-9-]+$', max_length=128)]
Status = Literal['ready', 'unknown', 'unsupported', 'error', 'timeout', 'conflict',
    'release_mismatch', 'no_evidence', 'uncalibrated', 'clarify']
Scope = Literal['none', 'document_explanation', 'scoped_prerequisite_check',
    'dependency_listing', 'combined_explanation', 'course_facts_listing', 'term_prerequisite_listing', 'study_plan_check', 'earliest_term_assessment']
DocumentStatus = Literal['ok', 'insufficient_evidence', 'needs_scope', 'conflicting_sources',
    'uncalibrated', 'release_changed', 'configuration_mismatch', 'encoder_unavailable',
    'invalid_query', 'storage_error', 'policy_binding_error', 'needs_subject',
    'needs_claims', 'unassessed']


class SourceBinding(Record):
    version_id: str = Field(pattern=ID_VER)
    byte_sha256: str = Field(pattern=SHA256)


class DocumentMember(SourceBinding):
    chunk_id: str = Field(pattern=SHA256)
    passage_sha256: str | None = Field(default=None, pattern=SHA256, exclude_if=lambda value: value is None)


class CurriculumMember(Record):
    """One curriculum's own runtime identity inside a multi-curriculum research release."""
    curriculum_id: Text
    release_id: ReleaseID
    rule_bundle_version: Text


class ReleasePin(Record):
    """Trusted snapshot: synthetic, or owner-authorized research (never institutional use)."""
    release_id: ReleaseID
    synthetic: bool
    rule_bundle_version: Text | None
    plan_routes_sha256: str | None = Field(default=None, pattern=SHA256, exclude_if=lambda value: value is None)
    sources: tuple[SourceBinding, ...]
    documents: tuple[DocumentMember, ...] = ()
    research_ref: str | None = Field(default=None, pattern=r'^research-[A-Za-z0-9_-]+$', max_length=128)
    curricula: tuple[CurriculumMember, ...] = ()  # several reviewed curricula in one research release

    @model_validator(mode='after')
    def _membership(self):
        if self.synthetic != (self.research_ref is None):
            raise ValueError('research_pin_requires_reference_only')
        sources = {s.version_id:s.byte_sha256 for s in self.sources}
        if len(sources) != len(self.sources):
            raise ValueError('duplicate_source_version')
        if len({d.chunk_id for d in self.documents}) != len(self.documents):
            raise ValueError('duplicate_document_member')
        if any(sources.get(d.version_id) != d.byte_sha256 for d in self.documents):
            raise ValueError('document_source_not_in_pin')
        if len({c.curriculum_id for c in self.curricula}) != len(self.curricula):
            raise ValueError('duplicate_curriculum_member')
        if self.curricula and self.synthetic:
            raise ValueError('curriculum_members_are_research_only')
        return self


class DocumentCitation(SourceBinding):
    page: int = Field(ge=1)
    locator: SpanLocator
    span_id: Text | None = None
    printed_page_label: Text | None = None
    document_id: Text | None = None
    edition_id: Text | None = None
    filename: Text | None = None
    acquisition_locators: tuple[Text, ...] = ()


class DocumentPassage(Record):
    chunk_id: str = Field(pattern=SHA256)
    version_id: str = Field(pattern=ID_VER)
    text: Text
    citations: tuple[DocumentCitation, ...] = Field(min_length=1)

    @model_validator(mode='after')
    def _citations(self):
        if any(c.version_id != self.version_id for c in self.citations):
            raise ValueError('passage_citation_version_mismatch')
        return self


class DocumentFieldQuote(Record):
    """An exact reviewed field and the original spans available in its passage."""
    chunk_id: str = Field(pattern=SHA256)
    field_name: str = Field(min_length=1, max_length=2048)
    text: str = Field(min_length=1, max_length=2048)
    span_ids: tuple[Annotated[str, Field(min_length=1, max_length=128)], ...] = Field(min_length=1, max_length=32)

    @model_validator(mode='after')
    def _spans(self):
        if (not self.text.strip() or not self.field_name.strip()
                or len(set(self.span_ids)) != len(self.span_ids)
                or any(not i.startswith(self.chunk_id+':') for i in self.span_ids)):
            raise ValueError('invalid_quoted_field_spans')
        return self


class DocumentRecordCoverage(Record):
    """Reviewed service records required by one exact subject/claim, not answer truth."""
    subject_id: str = Field(pattern=r'^[a-z][a-z0-9_]*$', max_length=64)
    claim: str = Field(min_length=1, max_length=256)
    chunk_ids: tuple[Annotated[str, Field(pattern=SHA256)], ...] = Field(min_length=1, max_length=32)
    source_ordered: bool = False  # only an explicit source review can establish sequence
    sequence_chunk_ids: tuple[Annotated[str, Field(pattern=SHA256)], ...] = Field(default=(), max_length=32)
    quoted_field: DocumentFieldQuote | None = None

    @model_validator(mode='after')
    def _unique(self):
        if len(set(self.chunk_ids)) != len(self.chunk_ids):
            raise ValueError('duplicate_coverage_record')
        if self.quoted_field is not None and (self.source_ordered or self.quoted_field.chunk_id not in self.chunk_ids):
            raise ValueError('invalid_quoted_field_coverage')
        if self.source_ordered and len(self.chunk_ids) < 2:
            raise ValueError('source_order_requires_multiple_records')
        if self.sequence_chunk_ids and (not self.source_ordered or len(self.sequence_chunk_ids)<2
                or len(set(self.sequence_chunk_ids))!=len(self.sequence_chunk_ids)
                or not set(self.sequence_chunk_ids)<=set(self.chunk_ids)):
            raise ValueError('invalid_source_sequence_subset')
        return self

    @model_serializer(mode='wrap')
    def _omit_unordered(self, handler):
        value = handler(self)
        if not self.source_ordered:
            value.pop('source_ordered', None)
        if not self.sequence_chunk_ids:
            value.pop('sequence_chunk_ids', None)
        if self.quoted_field is None:
            value.pop('quoted_field', None)
        return value


class DocumentResult(Record):
    release_id: ReleaseID
    status: DocumentStatus
    passages: tuple[DocumentPassage, ...]
    gaps: tuple[Text, ...]
    record_coverage: tuple[DocumentRecordCoverage, ...] = Field(default=(), max_length=64)

    @model_validator(mode='after')
    def _coverage(self):
        keys = [(c.subject_id, c.claim) for c in self.record_coverage]
        if len(set(keys)) != len(keys):
            raise ValueError('duplicate_record_coverage_claim')
        available = {p.chunk_id for p in self.passages}
        if any(not set(c.chunk_ids) <= available for c in self.record_coverage):
            raise ValueError('coverage_record_not_in_context')
        for coverage in self.record_coverage:
            quote = coverage.quoted_field
            if quote is None:
                continue
            passage = next(p for p in self.passages if p.chunk_id == quote.chunk_id)
            try:
                record = json.loads(passage.text)
                fields = [f for f in record['fields'] if isinstance(f, dict) and f.get('name') == quote.field_name]
                matches = (len(fields) == 1 and fields[0].get('source_blank') is False
                    and fields[0].get('value') == quote.text)
            except (ValueError, TypeError, KeyError):
                matches = False
            if not matches or not set(quote.span_ids) <= {c.span_id for c in passage.citations}:
                raise ValueError('quoted_field_not_in_emitted_source')
        return self

    @model_serializer(mode='wrap')
    def _omit_absent_coverage(self, handler):
        value = handler(self)
        if not self.record_coverage:
            value.pop('record_coverage', None)  # keep earlier serialized evidence/digests unchanged
        return value


class CandidateEvidence(Contract):
    SCHEMA_VERSION = 'bintanong-candidate-evidence-v1'
    candidate_only: Literal[True] = True
    institutional_use_allowed: Literal[False] = False
    activation_allowed: Literal[False] = False
    pin: ReleasePin
    route: Route()
    documents: DocumentResult | None
    symbolic: ResearchSymbolicResult | SymbolicResult | None
    dependencies: ResearchDependencyResult | DependencyResult | None
    status: Status
    permitted_scope: Scope
    missing_facts: tuple[Text, ...] = ()
    conflicts: tuple[Text, ...] = ()
    course_facts: CourseFactsResult | None = None  # printed course facts (no rule executed)
    plan_check: PlanCheckResult | None = Field(default=None, exclude_if=lambda value: value is None)
    earliest_term: EarliestTermAssessment | None = Field(default=None, exclude_if=lambda value: value is None)
    plan_routes: RecoveryRoutes | None = Field(default=None, exclude_if=lambda value: value is None)
    plan_route_sources: DocumentResult | None = Field(default=None, exclude_if=lambda value: value is None)
    term_assessment: TermAssessmentResult | None = None  # each course of one term checked (memory plan, Task 4)

    @model_serializer(mode='wrap')
    def _omit_absent_course_facts(self, handler):
        # Evidence without course facts keeps its earlier dump, so pinned digests stay valid.
        data = handler(self)
        if self.course_facts is None:
            data.pop('course_facts', None)
        if self.term_assessment is None:
            data.pop('term_assessment', None)
        return data

    @model_validator(mode='after')
    def _shape(self):
        has_symbolic = ((self.symbolic is not None) + (self.dependencies is not None)
                        + (self.course_facts is not None) + (self.term_assessment is not None) + (self.plan_check is not None) + (self.earliest_term is not None))
        from .plan_sources import check_route_sources
        check_route_sources(self.pin, self.plan_routes, self.plan_route_sources)
        if self.earliest_term is not None and self.earliest_term.synthetic is not self.pin.synthetic:
            raise ValueError('earliest_term_must_match_pin')
        if self.plan_routes is not None and (self.plan_check is None or self.plan_routes.synthetic is not self.pin.synthetic):
            raise ValueError('plan_routes_require_their_checked_plan')
        if self.plan_check is not None and self.plan_check.synthetic is not self.pin.synthetic:
            raise ValueError('plan_check_must_match_pin')
        if self.term_assessment is not None and self.term_assessment.synthetic is not self.pin.synthetic:
            raise ValueError('term_assessment_must_match_pin')
        if self.route == 'RAG' and (self.documents is None or has_symbolic):
            raise ValueError('RAG_requires_documents_only')
        if self.route == 'Symbolic' and (self.documents is not None or has_symbolic != 1):
            raise ValueError('Symbolic_requires_one_symbolic_component')
        if self.route == 'Hybrid' and (self.documents is None or has_symbolic != 1):
            raise ValueError('Hybrid_requires_both_components')
        if self.pin.synthetic:
            if self.symbolic is not None and (type(self.symbolic) is not SymbolicResult
                    or not self.symbolic.decision.synthetic):
                raise ValueError('synthetic_results_only')
            if self.dependencies is not None and (type(self.dependencies) is not DependencyResult
                    or not self.dependencies.synthetic):
                raise ValueError('synthetic_dependencies_only')
            if self.course_facts is not None and not self.course_facts.synthetic:
                raise ValueError('synthetic_course_facts_only')
        else:  # Research pin: only research results bound to this pin's authorization.
            for result, kind in ((self.symbolic, ResearchSymbolicResult),
                                 (self.dependencies, ResearchDependencyResult)):
                if result is not None and (type(result) is not kind or
                        result.research.authorization.authorization_ref != self.pin.research_ref):
                    raise ValueError('research_results_must_match_pin')
            if self.course_facts is not None and self.course_facts.synthetic:
                raise ValueError('research_results_must_match_pin')
        if (self.status == 'ready') != (self.permitted_scope != 'none'):
            raise ValueError('only_ready_evidence_has_permitted_scope')
        return self


class StageEvent(Record):
    """Allowlist for telemetry; no questions, facts, grades, exceptions or prompts."""
    stage: Literal['release', 'routing', 'retrieval', 'symbolic', 'integration']
    duration_ms: float = Field(ge=0, allow_inf_nan=False)
    route: Route() | None
    release_id: ReleaseID | None
    outcome: Status | DocumentStatus | Literal['eligible', 'ineligible', 'control', 'held',
                                              'busy', 'invalid_output', 'tool_error']
    retry_count: int = Field(default=0, ge=0, le=1)
    evidence_ids: tuple[Annotated[str, Field(pattern=r'^(?:[0-9a-f]{64}|rule-[a-z0-9_-]+)$',
                                            max_length=128)], ...] = ()


class RequestUnderstanding(Contract):
    """Host-bound pre-evidence interpretation;not a completeness or policy oracle."""
    SCHEMA_VERSION = 'bintanong-request-understanding-v1'
    request_id: str = Field(pattern=r'^req-[a-z0-9-]+$')
    release_id: ReleaseID
    question_sha256: str = Field(pattern=SHA256)
    route: Route() | None
    parts: tuple[RequestPart, ...] = Field(max_length=8)
    operations: tuple[Operation, ...] = Field(max_length=4)
    predicate_request: PredicateRequest | None

    @model_validator(mode='after')
    def _parts(self):
        if len({p.part_id for p in self.parts}) != len(self.parts):
            raise ValueError('duplicate_part_id')
        if len({(p.start,p.end) for p in self.parts}) != len(self.parts):
            raise ValueError('duplicate_part_span')
        if any(i >= len(self.operations) for p in self.parts for i in p.operation_indices):
            raise ValueError('invalid_part_operation')
        return self


class IntegrationResult(Contract):
    SCHEMA_VERSION = 'bintanong-candidate-integration-v2'
    candidate_only: Literal[True] = True
    institutional_use_allowed: Literal[False] = False
    activation_allowed: Literal[False] = False
    request_id: str = Field(pattern=r'^req-[a-z0-9-]+$')
    route: Route() | None
    response_style: Literal['en', 'fil', 'taglish', 'unknown']
    status: Literal['ready', 'unknown', 'unsupported', 'error', 'conflict', 'release_mismatch',
        'no_evidence', 'uncalibrated', 'clarify', 'greeting', 'unsupported_scope',
        'evidence_unavailable', 'held', 'timeout', 'busy', 'invalid_output', 'tool_error']
    evidence: CandidateEvidence | None
    understanding: RequestUnderstanding | None
    missing_facts: tuple[Text, ...] = ()
    events: tuple[StageEvent, ...]
    # Display-only printed course codes keyed by internal course identity.
    course_labels: dict[str, Text] = Field(default_factory=dict, max_length=256)
    # Memory/eligibility plan: what-if premises ('<state>:<course id>') this check assumed; request-only, never saved.
    assumed_facts: tuple[Text, ...] = Field(default=(), max_length=32, exclude_if=lambda value: not value)
    # Ask mode (owner 4 Nov 2026): recovery routes and drafts for the failed course of a dependency listing.
    recovery: RecoveryResult | None = Field(default=None, exclude_if=lambda value: value is None)
    plan_check: PlanCheckResult | None = Field(default=None, exclude_if=lambda value: value is None)
    # Owner GUI 4 Nov 2026: the words of document parts with no reviewed topic, named as unavailable in the reply.
    unavailable_parts: tuple[Text, ...] = Field(default=(), max_length=8, exclude_if=lambda value: not value)
    # Audit A03 (4 Nov 2026): which boundary stopped an unanswered turn (reasons.py); None when ready.
    reason: ReasonCode | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode='after')
    def _result(self):
        if self.evidence is not None and (self.route != self.evidence.route
                or self.status != self.evidence.status):
            raise ValueError('integration_evidence_mismatch')
        if self.status == 'ready' and self.evidence is None:
            raise ValueError('ready_requires_evidence')
        plan = self.understanding
        if plan is not None:
            if plan.request_id != self.request_id or plan.route != self.route:
                raise ValueError('understanding_request_or_route_mismatch')
            if self.evidence is not None and plan.release_id != self.evidence.pin.release_id:
                raise ValueError('understanding_release_mismatch')
        if self.status == 'ready':
            if plan is None or not plan.parts:
                raise ValueError('ready_requires_understanding')
            needs = {p.evidence_need for p in plan.parts}
            expected = {'RAG': {'document'}, 'Symbolic': {'structured'},
                        'Hybrid': {'document','structured'}}[self.route]
            if needs != expected:
                raise ValueError('understanding_route_mismatch')
            indices = {i for p in plan.parts for i in p.operation_indices}
            if self.route == 'RAG':
                if plan.operations or plan.predicate_request is not None:
                    raise ValueError('document_understanding_has_operation')
            elif (len(plan.operations) != 1 or plan.predicate_request is None or indices != {0}
                  or any(p.evidence_need == 'structured' and not p.operation_indices for p in plan.parts)):
                raise ValueError('structured_understanding_needs_one_operation')
        if self.evidence is not None and self.evidence.earliest_term is not None:
            earliest = self.evidence.earliest_term
            if (plan is None or plan.predicate_request is None
                    or plan.predicate_request.predicate != earliest.predicate
                    or plan.predicate_request.inputs != earliest.inputs):
                raise ValueError('earliest_understanding_mismatch')
        if self.plan_check != (None if self.evidence is None else self.evidence.plan_check):
            raise ValueError('plan_check_evidence_mismatch')
        if self.plan_check is not None:
            checked = self.plan_check
            pin = None if self.evidence is None else self.evidence.pin
            inputs = ({} if plan is None or plan.predicate_request is None else
                      {i.name:i.value for i in plan.predicate_request.inputs})
            if (self.status != 'ready' or pin is None or checked.synthetic is not pin.synthetic
                    or plan.predicate_request.predicate != 'check_study_plan'
                    or inputs.get('curriculum_id') != checked.curriculum_id or checked.scope is None):
                raise ValueError('plan_check_requires_ready_pinned_evidence')
            member = next((m for m in pin.curricula if m.curriculum_id == checked.curriculum_id), None)
            release = pin.release_id if not pin.curricula else None if member is None else member.release_id
            sources = {s.version_id:s.byte_sha256 for s in pin.sources}
            if (checked.scope.knowledge_release_id != release
                    or any(sources.get(s.version_id) != s.byte_sha256 for s in checked.rule_spans)):
                raise ValueError('plan_check_release_mismatch')
        if self.recovery is not None:
            dependencies = None if self.evidence is None else self.evidence.dependencies
            inputs = {} if dependencies is None else {i.name: i.value for i in dependencies.inputs}
            if (self.status != 'ready' or self.recovery.synthetic is not self.evidence.pin.synthetic
                    or (inputs.get('curriculum_id'), inputs.get('course_id'))
                    != (self.recovery.curriculum_id, self.recovery.failed_course_id)):
                raise ValueError('recovery_requires_its_ready_dependency_listing')
        return self
