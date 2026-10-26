"""Prepare a detached, revalidated evidence view; never promote candidate authority."""
from dataclasses import dataclass
import hashlib
import json

from ..bintanong_contracts.base import foreign_ids
from ..bintanong_contracts.symbolic import DecisionOutcome,RequirementView
from ..bintanong_contracts.runtime import BoundInput
from ..bintanong_orchestration.contracts import DocumentCitation,IntegrationResult,RequestUnderstanding
from ..bintanong_orchestration.integration import assemble
from ..bintanong_symbolic.course_facts import CourseFactsResult
from ..bintanong_symbolic.runtime import DependencyResult
from .contracts import EvidenceCard,StructuredContext


@dataclass(frozen=True)
class PreparedEvidence:
    request_id: str
    release_id: str|None
    status: str
    language: str
    route: str|None
    cards: tuple[EvidenceCard,...]
    decision: DecisionOutcome|None
    dependencies: DependencyResult|None
    scope: str
    structured_context: StructuredContext|None
    missing_facts: tuple[str,...]
    understanding: RequestUnderstanding|None
    research_ref: str|None=None  # owner-authorized research release reference, if any
    course_labels: tuple[tuple[str,str],...]=()  # display-only printed codes
    requirement: RequirementView|None=None  # the checked course's reviewed prerequisites (display only)
    course_facts: CourseFactsResult|None=None  # printed course facts, rendered by the host
    record_coverage: tuple[tuple[str,str,tuple[str,...]],...]=()  # exact subject/claim -> evidence ids
    record_order: tuple[tuple[str,str,tuple[str,...]],...]=()  # explicit reviewed sequence only

    def model_payload(self):
        payload = dict(release_id=self.release_id,language=self.language,route=self.route,
            permitted_scope=self.scope,decision=None if self.decision is None else
            self.decision.model_dump(mode='json'),dependencies=None if self.dependencies is None else
            dict(status=self.dependencies.status,course_ids=self.dependencies.course_ids,
                 unknown_conditions=self.dependencies.unknown_conditions),
            structured_context=None if self.structured_context is None else dict(
                operation=self.structured_context.operation,
                inputs={i.name:i.value for i in self.structured_context.inputs},
                scope=None if self.structured_context.scope is None else self.structured_context.scope.model_dump(mode='json'),
                rule_bundle_version=self.structured_context.rule_bundle_version),
            requested_parts=[] if self.understanding is None else
                [p.model_dump(mode='json') for p in self.understanding.parts],
            sources=[c.model_dump(mode='json') for c in self.cards])
        if self.record_coverage:
            payload['record_coverage'] = self.record_coverage
        if self.record_order:
            payload['record_order'] = self.record_order  # bind sequence in the existing review identity
        return payload


def _card(kind,text,citations):
    data=dict(kind=kind,text=text,citations=[c.model_dump(mode='json') for c in citations])
    identity=hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=True).encode()).hexdigest()
    if foreign_ids(data,'institutional'):
        raise ValueError('private_evidence_reference')
    return EvidenceCard.parse(dict(data,evidence_id='ev-'+identity))


def prepare(result: IntegrationResult)->PreparedEvidence:
    if type(result) is not IntegrationResult:
        raise ValueError('candidate_integration_required')
    result=IntegrationResult.parse(result.model_dump(mode='json'))
    if foreign_ids(result.missing_facts,'institutional'):
        raise ValueError('private_missing_fact_reference')
    evidence=result.evidence
    if evidence is not None:
        checked=assemble(evidence.pin,evidence.route,documents=evidence.documents,
            symbolic=evidence.symbolic,dependencies=evidence.dependencies,course_facts=evidence.course_facts)
        if checked!=evidence:
            raise ValueError('integration_policy_mismatch')
    cards=[]
    if evidence is not None and evidence.documents is not None:
        cards.extend(_card('document',p.text,p.citations) for p in evidence.documents.passages)
    symbolic=evidence.symbolic if evidence else None
    dependencies=evidence.dependencies if evidence else None
    reasoning=symbolic if symbolic is not None else dependencies
    if reasoning is not None:
        for span in reasoning.rule_spans:
            citation=DocumentCitation(version_id=span.version_id,byte_sha256=span.byte_sha256,
                page=span.page,locator=span.locator,printed_page_label=span.printed_page_label)
            cards.append(_card('rule',span.text,(citation,)))
    cards=tuple({c.evidence_id:c for c in cards}.values())
    if len(cards)>32 or sum(len(c.text) for c in cards)>65536:
        raise ValueError('generation_evidence_limit')
    facts=evidence.course_facts if evidence else None
    context=StructuredContext(operation=facts.predicate,
        inputs=tuple(BoundInput(name=i.name,value=i.value,fact_ref=None) for i in facts.inputs),
        scope=facts.scope,rule_bundle_version=None) if facts is not None else None if reasoning is None else StructuredContext(
        operation=symbolic.decision.predicate if symbolic else 'list_affected_courses',
        inputs=tuple(BoundInput(name=i.name,value=i.value,fact_ref=None) for i in reasoning.inputs),
        scope=reasoning.scope,rule_bundle_version=reasoning.rule_bundle_version)
    plan=result.understanding
    if result.status=='ready' and result.route!='RAG':
        request=plan.predicate_request
        if (context is None or request.predicate!=context.operation or
                tuple(BoundInput(name=i.name,value=i.value,fact_ref=None) for i in request.inputs)
                !=context.inputs or plan.operations[0].name!=request.predicate):
            raise ValueError('understanding_operation_mismatch')
    by_chunk = {p.chunk_id:_card('document',p.text,p.citations).evidence_id
                for p in evidence.documents.passages} if evidence and evidence.documents else {}
    coverage = tuple((c.subject_id,c.claim,tuple(by_chunk[i] for i in c.chunk_ids))
                     for c in evidence.documents.record_coverage) if evidence and evidence.documents else ()
    order = tuple((c.subject_id,c.claim,tuple(by_chunk[i] for i in (c.sequence_chunk_ids or c.chunk_ids)))
                  for c in evidence.documents.record_coverage if c.source_ordered) if evidence and evidence.documents else ()
    return PreparedEvidence(result.request_id,evidence.pin.release_id if evidence else None,
        result.status,result.response_style,result.route,cards,
        symbolic.decision if symbolic else None,dependencies,
        evidence.permitted_scope if evidence else 'none',context,result.missing_facts,plan,
        evidence.pin.research_ref if evidence else None,tuple(sorted(result.course_labels.items())),
        symbolic.requirement if symbolic else None,facts,coverage,order)
