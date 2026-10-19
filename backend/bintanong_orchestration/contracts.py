"""Internal candidate evidence, separate from institutional answer contracts."""
from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Contract, Record, Route
from ..bintanong_contracts.governance import ID_VER, SHA256
from ..bintanong_contracts.source import SpanLocator
from ..bintanong_contracts.symbolic import SymbolicResult
from ..bintanong_symbolic.runtime import DependencyResult

Text = Annotated[str, Field(min_length=1)]
ReleaseID = Annotated[str, Field(pattern=r'^release-[a-z0-9-]+$', max_length=128)]
Status = Literal['ready', 'unknown', 'unsupported', 'error', 'timeout', 'conflict',
    'release_mismatch', 'no_evidence', 'uncalibrated', 'clarify']
Scope = Literal['none', 'document_explanation', 'scoped_prerequisite_check',
    'dependency_listing', 'combined_explanation']
DocumentStatus = Literal['ok', 'insufficient_evidence', 'needs_scope', 'conflicting_sources',
    'uncalibrated', 'release_changed', 'configuration_mismatch', 'encoder_unavailable',
    'invalid_query', 'storage_error', 'policy_binding_error', 'needs_subject',
    'needs_claims', 'unassessed']


class SourceBinding(Record):
    version_id: str = Field(pattern=ID_VER)
    byte_sha256: str = Field(pattern=SHA256)


class DocumentMember(SourceBinding):
    chunk_id: str = Field(pattern=SHA256)


class ReleasePin(Record):
    """Trusted synthetic snapshot; labels never authorize institutional execution."""
    release_id: ReleaseID
    synthetic: Literal[True]
    rule_bundle_version: Text | None
    sources: tuple[SourceBinding, ...]
    documents: tuple[DocumentMember, ...] = ()

    @model_validator(mode='after')
    def _membership(self):
        sources = {s.version_id:s.byte_sha256 for s in self.sources}
        if len(sources) != len(self.sources):
            raise ValueError('duplicate_source_version')
        if len({d.chunk_id for d in self.documents}) != len(self.documents):
            raise ValueError('duplicate_document_member')
        if any(sources.get(d.version_id) != d.byte_sha256 for d in self.documents):
            raise ValueError('document_source_not_in_pin')
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


class DocumentResult(Record):
    release_id: ReleaseID
    status: DocumentStatus
    passages: tuple[DocumentPassage, ...]
    gaps: tuple[Text, ...]


class CandidateEvidence(Contract):
    SCHEMA_VERSION = 'bintanong-candidate-evidence-v1'
    candidate_only: Literal[True] = True
    institutional_use_allowed: Literal[False] = False
    activation_allowed: Literal[False] = False
    pin: ReleasePin
    route: Route()
    documents: DocumentResult | None
    symbolic: SymbolicResult | None
    dependencies: DependencyResult | None
    status: Status
    permitted_scope: Scope
    missing_facts: tuple[Text, ...] = ()
    conflicts: tuple[Text, ...] = ()

    @model_validator(mode='after')
    def _shape(self):
        has_symbolic = (self.symbolic is not None) + (self.dependencies is not None)
        if self.route == 'RAG' and (self.documents is None or has_symbolic):
            raise ValueError('RAG_requires_documents_only')
        if self.route == 'Symbolic' and (self.documents is not None or has_symbolic != 1):
            raise ValueError('Symbolic_requires_one_symbolic_component')
        if self.route == 'Hybrid' and (self.documents is None or has_symbolic != 1):
            raise ValueError('Hybrid_requires_both_components')
        if self.symbolic is not None and (type(self.symbolic) is not SymbolicResult
                or not self.symbolic.decision.synthetic):
            raise ValueError('synthetic_results_only')
        if self.dependencies is not None and (type(self.dependencies) is not DependencyResult
                or not self.dependencies.synthetic):
            raise ValueError('synthetic_dependencies_only')
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
    evidence_ids: tuple[Annotated[str, Field(pattern=r'^(?:[0-9a-f]{64}|rule-[a-z0-9-]+)$',
                                            max_length=128)], ...] = ()


class IntegrationResult(Contract):
    SCHEMA_VERSION = 'bintanong-candidate-integration-v1'
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
    missing_facts: tuple[Text, ...] = ()
    events: tuple[StageEvent, ...]

    @model_validator(mode='after')
    def _result(self):
        if self.evidence is not None and (self.route != self.evidence.route
                or self.status != self.evidence.status):
            raise ValueError('integration_evidence_mismatch')
        if self.status == 'ready' and self.evidence is None:
            raise ValueError('ready_requires_evidence')
        return self
