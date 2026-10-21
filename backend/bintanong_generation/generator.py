"""One bounded answer repair; nothing is returned before final host validation."""
import asyncio
import json
import math

from ..bintanong_orchestration.contracts import IntegrationResult
from ..bintanong_routing.contracts import RequestContext,prepare_query
from ..bintanong_routing.transport import RuntimeFailure
from .contracts import AnswerDraft,CandidateAnswer,GuardObservation,CoverageObservation
from .evidence import prepare
from .references import EvidenceReferences,ShortAnswerDraft
from .prompt import draft_messages,draft_schema
from .render import fallback_status,render_text,selected_cards
from .validation import validate_draft,validate_support,validate_final
from .scope import (DocumentExplanation,canonical_draft,document_messages,document_schema,
                    )
from .guard import RetrievalAssessment,guard_messages,guard_schema
from .coverage import CoverageReview,coverage_messages,coverage_schema
from .requirements import RequirementReview
from .understanding import check_question, assess, review_messages, review_schema
from .part_answers import (PartConfirmation,PartExplanation,assess_slots,confirm_messages,
                           confirm_schema,part_messages,part_schema,to_draft)


def _seconds(value):
    if type(value) not in (int,float) or not math.isfinite(value) or not 0<value<=600:
        raise ValueError('deadline_must_be_finite_positive_at_most_600')
    return float(value)


def _unique(pairs):
    data={}
    for key,value in pairs:
        if key in data: raise ValueError('duplicate_json_key')
        data[key]=value
    return data


def _parse(raw,contract):
    if not isinstance(raw,str) or len(raw.encode('utf-8'))>65536:
        raise ValueError('invalid_output_size')
    return contract.parse(json.loads(raw,object_pairs_hook=_unique))


def _answer(pack,status,*,claims=(),reason='control_fallback',attempts=0,checks=0,guard=None,coverage=None,ledger=None):
    answer=CandidateAnswer(schema_version=CandidateAnswer.SCHEMA_VERSION,
        request_id=pack.request_id,release_id=pack.release_id,language=pack.language,status=status,
        text=render_text(pack,claims,status,decision_withheld=reason=='decision_withheld',
            question_uncovered=reason in ('question_uncovered','parts_unresolved')),
        decision=pack.decision,dependencies=pack.dependencies,
        structured_context=pack.structured_context,missing_facts=pack.missing_facts,claims=tuple(claims),
        citations=selected_cards(pack,claims),validation=reason,draft_attempts=attempts,
        check_attempts=checks,answer_repairs=max(attempts-1,0),decision_guard=guard,question_coverage=coverage,
        part_ledger=ledger)
    validate_final(answer,pack,claims)
    return answer


class Generator:
    def __init__(self,transport,*,timeout_seconds=120,reference_profile='canonical',explanation_profile='parts'):
        if reference_profile not in ('canonical','short'):
            raise ValueError('invalid_generation_reference_profile')
        if explanation_profile not in ('legacy','scoped','guarded','covered','parts'):
            raise ValueError('invalid_explanation_profile')
        if explanation_profile in ('scoped','guarded','covered','parts') and reference_profile!='canonical':
            raise ValueError('scoped_requires_canonical_references')
        self.transport=transport
        self.timeout_seconds=_seconds(timeout_seconds)
        self.reference_profile=reference_profile
        self.explanation_profile=explanation_profile

    async def generate(self,text,integration,*,remaining_seconds=None):
        prepare_query(text)
        pack=prepare(integration)
        check_question(text,pack)
        references=EvidenceReferences(pack) if self.reference_profile=='short' else None
        if pack.status!='ready' or pack.language=='unknown':
            return _answer(pack,fallback_status(pack.status))
        seconds=self.timeout_seconds
        if remaining_seconds is not None:
            if type(remaining_seconds) not in (int,float) or not math.isfinite(remaining_seconds):
                raise ValueError('invalid_remaining_deadline')
            seconds=min(seconds,remaining_seconds)
        if seconds<=0:
            return _answer(pack,'temporarily_unavailable',reason='timeout')
        per_part=self.explanation_profile=='parts'
        scoped=self.explanation_profile in ('scoped','guarded','covered')
        coverage_required=self.explanation_profile=='covered' and pack.route=='RAG'
        if pack.route=='Symbolic':
            draft=AnswerDraft(schema_version=AnswerDraft.SCHEMA_VERSION,language=pack.language,
                release_id=pack.release_id,decision_outcome=pack.decision.outcome if pack.decision else None,claims=())
            return _answer(pack,'answered',reason='validated',ledger=assess(pack,draft))
        attempts=checks=0
        guard=None
        coverage=None
        guard_started=None
        loop=asyncio.get_running_loop()
        previous=''
        errors=()
        ledger=None
        try:
            async with asyncio.timeout(seconds):
                if self.explanation_profile=='guarded' and pack.route=='RAG':
                    guard_started=loop.time()
                    raw=await self.transport.infer(guard_messages(text,pack),guard_schema(pack))
                    try:
                        assessment=_parse(raw,RetrievalAssessment)
                        result=assessment.requirement if assessment.release_id==pack.release_id else 'invalid_output'
                    except (ValueError,TypeError,RecursionError):
                        result='invalid_output'
                    guard=GuardObservation(result=result,elapsed_seconds=loop.time()-guard_started)
                    if result!='document_only':
                        return _answer(pack,'abstained',reason='decision_withheld',guard=guard)
                for attempt in (1,2):
                    attempts=attempt
                    coverage=None
                    messages=(part_messages(text,pack,errors=errors,previous=previous) if per_part else
                              document_messages(text,pack,errors=errors,previous=previous) if scoped else
                              draft_messages(text,pack,errors=errors,previous=previous,references=references))
                    schema=(part_schema(pack) if per_part else document_schema(pack) if scoped else
                            draft_schema(pack,references=references))
                    raw=await self.transport.infer(messages,schema)
                    previous=raw if isinstance(raw,str) else ''
                    slots=None
                    try:
                        if per_part:
                            proposal,slots=to_draft(_parse(raw,PartExplanation),pack)
                        else:
                            proposal=(canonical_draft(_parse(raw,DocumentExplanation),pack) if scoped else
                                      _parse(raw,AnswerDraft) if references is None else
                                      references.decode(_parse(raw,ShortAnswerDraft)))
                        errors=validate_draft(proposal,pack)
                    except (ValueError,TypeError,RecursionError):
                        errors=('invalid_draft',)
                        slots=None
                    if slots is not None and any(status!='answered' for status,_ in slots.values()):
                        # A part declared unavailable cannot be completed by review: withhold.
                        return _answer(pack,'insufficient_evidence',reason='parts_unresolved',attempts=attempts,
                            checks=checks,ledger=assess_slots(pack,proposal,slots),guard=guard,coverage=coverage)
                    if not errors and proposal.claims:
                        checks+=1
                        messages_to_review=(confirm_messages(text,pack,proposal,slots) if per_part else
                                            coverage_messages(text,pack,proposal) if coverage_required else
                                            review_messages(text,pack,proposal))
                        review_started=loop.time()
                        # Existing support call now accounts for each requested document part.
                        # Historical guard/coverage profiles remain explicit experiments.
                        part_review=not coverage_required
                        review_raw=await self.transport.infer(messages_to_review,
                            confirm_schema(pack,proposal,slots) if per_part else
                            review_schema(pack,proposal) if part_review else coverage_schema(pack,proposal))
                        try:
                            review=_parse(review_raw,PartConfirmation if per_part else
                                          RequirementReview if part_review else CoverageReview)
                            if part_review:
                                ledger=(assess_slots(pack,proposal,slots,review) if per_part else
                                        assess(pack,proposal,review))
                                errors=ledger.errors
                                if ('incomplete_support_verdicts' not in errors and
                                        any(e.status!='mapped' for e in ledger.entries)):
                                    return _answer(pack,'insufficient_evidence',reason='parts_unresolved',
                                        attempts=attempts,checks=checks,ledger=ledger,guard=guard,coverage=coverage)
                            elif coverage_required and review.release_id!=pack.release_id:
                                errors=('wrong_review_release',)
                            elif coverage_required:
                                errors=validate_support(review,proposal)
                                if coverage_required and 'incomplete_support_verdicts' not in errors:
                                    coverage=CoverageObservation(result=review.question_coverage,
                                        draft_attempt=attempt,elapsed_seconds=loop.time()-review_started)
                                    if review.question_coverage!='complete':
                                        return _answer(pack,'insufficient_evidence',reason='question_uncovered',
                                            attempts=attempts,checks=checks,coverage=coverage)
                        except (ValueError,TypeError,RecursionError):
                            errors=('invalid_support_report',)
                    if not errors:
                        if ledger is None:
                            ledger=assess(pack,proposal)
                        if ledger.status!='all_declared_parts_mapped':
                            return _answer(pack,'insufficient_evidence',reason='parts_unresolved',
                                attempts=attempts,checks=checks,ledger=ledger,guard=guard,coverage=coverage)
                        return _answer(pack,'answered',claims=proposal.claims,reason='validated',
                                       attempts=attempts,checks=checks,guard=guard,coverage=coverage,ledger=ledger)
        except (TimeoutError,RuntimeFailure) as error:
            timeout=isinstance(error,TimeoutError) or str(error)=='model_timeout'
            if guard_started is not None and guard is None:
                guard=GuardObservation(result='timeout' if timeout else 'tool_error',
                    elapsed_seconds=loop.time()-guard_started)
            return _answer(pack,'temporarily_unavailable',reason='timeout' if timeout else 'tool_error',
                           attempts=attempts,checks=checks,guard=guard,coverage=coverage)
        except Exception:
            if guard_started is not None and guard is None:
                guard=GuardObservation(result='tool_error',elapsed_seconds=loop.time()-guard_started)
            return _answer(pack,'temporarily_unavailable',reason='tool_error',attempts=attempts,checks=checks,
                           guard=guard,coverage=coverage)
        return _answer(pack,'abstained',reason='repair_exhausted',attempts=attempts,checks=checks,
                       guard=guard,coverage=coverage)


class AnswerPipeline:
    """The generation budget is reduced by time already spent in orchestration."""
    def __init__(self,orchestrator,generator,*,timeout_seconds=180):
        self.orchestrator,self.generator=orchestrator,generator
        self.timeout_seconds=_seconds(timeout_seconds)

    async def run(self,text,context):
        prepare_query(text)
        context=RequestContext.parse(context.model_dump(mode='json'))
        loop=asyncio.get_running_loop()
        deadline=loop.time()+self.timeout_seconds
        try:
            async with asyncio.timeout(self.timeout_seconds):
                integration=await self.orchestrator.run(text,context)
        except TimeoutError:
            integration=IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION,
                request_id=context.request_id,route=None,response_style='unknown',status='timeout',
                evidence=None,understanding=None,events=())
            return _answer(prepare(integration),'temporarily_unavailable',reason='timeout')
        if integration.request_id!=context.request_id:
            raise ValueError('request_identity_mismatch')
        return await self.generator.generate(text,integration,remaining_seconds=deadline-loop.time())
