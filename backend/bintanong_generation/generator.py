"""One bounded answer repair; nothing is returned before final host validation."""
import asyncio
import re
import json
import math

from ..bintanong_orchestration.contracts import IntegrationResult
from ..bintanong_routing.contracts import RequestContext,prepare_query
from ..bintanong_routing.transport import RuntimeFailure
from ..bintanong_routing.shorthand import expand_shorthand
from .contracts import AnswerDraft,CandidateAnswer,GuardObservation,CoverageObservation,ProseClaim
from .deadline_conflict import unresolved_deadline_context
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
from .part_answers import (PartConfirmationOutput,PartExplanation,ShortPartExplanation,decode_part_explanation,
                           answered_slots,assess_slots,bind_confirmation,
                           confirm_messages,confirm_schema,conjunction_errors,disjunction_errors,host_only,omitted_exception_errors,part_messages,part_schema,
                           record_coverage_errors,style_errors,to_draft)
from .ledger_contracts import ANSWERED_LEDGERS
from .quoted_field import quoted_field_parts

TRUNCATED_DRAFT_OUTPUT_TOKENS=1536


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
            question_uncovered=reason in ('question_uncovered','parts_unresolved'),ledger=ledger,
            thanked=reason=='thanks'),
        decision=pack.decision,dependencies=pack.dependencies,
        structured_context=pack.structured_context,missing_facts=pack.missing_facts,claims=tuple(claims),
        citations=selected_cards(pack,claims),validation=reason,draft_attempts=attempts,
        check_attempts=checks,answer_repairs=max(attempts-1,0),decision_guard=guard,question_coverage=coverage,
        part_ledger=ledger,research_ref=pack.research_ref)
    validate_final(answer,pack,claims)
    return answer


# A thank-you the router marked as a greeting gets "you're welcome", not "Hello" (owner f-list, 25 Oct 2026).
THANKS=re.compile(r'\b(?:thank you|thanks|thank u|thx|ty|tysm|salamat)\b',re.I)


class Generator:
    def __init__(self,transport,*,timeout_seconds=120,reference_profile='canonical',explanation_profile='parts',
                 review_reference_profile='canonical'):
        if reference_profile not in ('canonical','short'):
            raise ValueError('invalid_generation_reference_profile')
        if explanation_profile not in ('legacy','scoped','guarded','covered','parts'):
            raise ValueError('invalid_explanation_profile')
        if explanation_profile in ('scoped','guarded','covered') and reference_profile!='canonical':
            raise ValueError('scoped_requires_canonical_references')
        if review_reference_profile not in ('canonical','short'):
            raise ValueError('invalid_review_reference_profile')
        if review_reference_profile=='short' and explanation_profile!='parts':
            raise ValueError('short_review_requires_parts')
        self.transport=transport
        self.timeout_seconds=_seconds(timeout_seconds)
        self.reference_profile=reference_profile
        self.explanation_profile=explanation_profile
        self.review_reference_profile=review_reference_profile

    async def generate(self,text,integration,*,remaining_seconds=None):
        prepare_query(text)
        pack=prepare(integration)
        check_question(text,pack)
        try:
            quotes=quoted_field_parts(pack)
        except ValueError:
            return _answer(pack,'abstained',reason='unsupported_answer_scope')
        if quotes and self.explanation_profile!='parts':
            return _answer(pack,'abstained',reason='unsupported_answer_scope')
        references=EvidenceReferences(pack) if self.reference_profile=='short' else None
        review_references=EvidenceReferences(pack) if self.review_reference_profile=='short' else None
        if pack.status=='greeting' and THANKS.search(text):
            return _answer(pack,'greeting',reason='thanks')
        if pack.status!='ready' or pack.language=='unknown':
            context = unresolved_deadline_context(pack)
            if context:
                claims = tuple(ProseClaim(claim_id=f'c{n}', text=claim['text'],
                    evidence_ids=tuple(claim['evidence_ids'])) for n,claim in enumerate(context,1))
                return _answer(pack,'source_conflict',claims=claims)
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
        host=host_only(pack) if per_part else None
        if host is not None:  # owner "Rate + example": host wording only, no model call
            draft,ledger=host
            return _answer(pack,'answered',claims=draft.claims,reason='validated',ledger=ledger)
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
                def draft_request(previous):
                    return (part_messages(text,pack,errors=errors,previous=previous,references=references) if per_part else
                            document_messages(text,pack,errors=errors,previous=previous) if scoped else
                            draft_messages(text,pack,errors=errors,previous=previous,references=references))
                for attempt in (1,2):
                    attempts=attempt
                    coverage=None
                    schema=(part_schema(pack,references) if per_part else document_schema(pack) if scoped else
                            draft_schema(pack,references=references))
                    try:
                        try:
                            raw=await self.transport.infer(draft_request(previous),schema)
                        except RuntimeFailure as error:
                            if str(error)!='truncated_output':
                                raise
                            # Owner 30 Oct 2026: a long draft cut off at the output limit gets one larger attempt.
                            raw=await self.transport.infer(draft_request(previous),schema,
                                                           max_output_tokens=TRUNCATED_DRAFT_OUTPUT_TOKENS)
                    except RuntimeFailure as error:
                        if str(error)!='context_overflow' or not previous:
                            raise
                        # Preflight refused before inference. Drop only the model's own previous draft;
                        # complete sources, validation errors, window and margin stay unchanged.
                        raw=await self.transport.infer(draft_request(''),schema)
                    previous=raw if isinstance(raw,str) else ''
                    slots=None
                    try:
                        if per_part:
                            explanation=(_parse(raw,PartExplanation) if references is None else
                                decode_part_explanation(_parse(raw,ShortPartExplanation),references))
                            proposal,slots=to_draft(explanation,pack)
                        else:
                            proposal=(canonical_draft(_parse(raw,DocumentExplanation),pack) if scoped else
                                      _parse(raw,AnswerDraft) if references is None else
                                      references.decode(_parse(raw,ShortAnswerDraft)))
                        errors=validate_draft(proposal,pack)
                        if per_part:
                            errors=(errors+style_errors(proposal,pack,text)+disjunction_errors(proposal,pack,slots)+
                                    conjunction_errors(proposal,pack,slots)+omitted_exception_errors(proposal,pack,slots)+
                                    record_coverage_errors(pack,proposal.claims,slots))
                    except (ValueError,TypeError,RecursionError):
                        errors=('invalid_draft',)
                        slots=None
                    if slots is not None and not answered_slots(slots):
                        # Owner "Answer what's covered": a declared-unavailable part is named when the structured
                        # check answers; with nothing mapped the slot ledger stays unresolved and withholds.
                        errors=tuple(e for e in errors if e!='missing_document_claim')
                    if not errors and proposal.claims and (not per_part or answered_slots(slots)):
                        checks+=1
                        reviewed=answered_slots(slots) if per_part else None
                        messages_to_review=(confirm_messages(text,pack,proposal,reviewed,references=review_references) if per_part else
                                            coverage_messages(text,pack,proposal) if coverage_required else
                                            review_messages(text,pack,proposal))
                        review_started=loop.time()
                        # Existing support call now accounts for each requested document part.
                        # Historical guard/coverage profiles remain explicit experiments.
                        part_review=not coverage_required
                        review_raw=await self.transport.infer(messages_to_review,
                            confirm_schema(pack,proposal,reviewed) if per_part else
                            review_schema(pack,proposal) if part_review else coverage_schema(pack,proposal))
                        try:
                            review=(bind_confirmation(pack,proposal,_parse(review_raw,PartConfirmationOutput))
                                    if per_part else
                                    _parse(review_raw,RequirementReview if part_review else CoverageReview))
                            if part_review:
                                ledger=(assess_slots(pack,proposal,slots,review) if per_part else
                                        assess(pack,proposal,review))
                                errors=ledger.errors
                                settled=('mapped','unavailable') if per_part else ('mapped',)
                                if ('incomplete_support_verdicts' not in errors and
                                        any(e.status not in settled for e in ledger.entries)):
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
                            ledger=assess_slots(pack,proposal,slots) if per_part else assess(pack,proposal)
                        if ledger.status not in ANSWERED_LEDGERS:
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
        text=expand_shorthand(text)  # owner 29 Oct 2026: reviewed Filipino shorthand, understanding only
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
