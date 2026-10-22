"""One bounded answer repair; nothing is returned before final host validation."""
import asyncio
import json
import math

from ..bintanong_orchestration.contracts import IntegrationResult
from ..bintanong_routing.contracts import RequestContext,prepare_query
from ..bintanong_routing.transport import RuntimeFailure
from .contracts import AnswerDraft,CandidateAnswer,SupportReport
from .evidence import prepare
from .prompt import draft_messages,draft_schema,support_messages,output_schema
from .render import fallback_status,render_text,selected_cards
from .validation import validate_draft,validate_support,validate_final


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


def _answer(pack,status,*,claims=(),reason='control_fallback',attempts=0,checks=0):
    answer=CandidateAnswer(schema_version=CandidateAnswer.SCHEMA_VERSION,
        request_id=pack.request_id,release_id=pack.release_id,language=pack.language,status=status,
        text=render_text(pack,claims,status),decision=pack.decision,dependencies=pack.dependencies,
        structured_context=pack.structured_context,claims=tuple(claims),
        citations=selected_cards(pack,claims),validation=reason,draft_attempts=attempts,
        check_attempts=checks,answer_repairs=max(attempts-1,0))
    validate_final(answer,pack,claims)
    return answer


class Generator:
    def __init__(self,transport,*,timeout_seconds=120):
        self.transport=transport
        self.timeout_seconds=_seconds(timeout_seconds)

    async def generate(self,text,integration,*,remaining_seconds=None):
        prepare_query(text)
        pack=prepare(integration)
        if pack.status!='ready' or pack.language=='unknown':
            return _answer(pack,fallback_status(pack.status))
        seconds=self.timeout_seconds
        if remaining_seconds is not None:
            if type(remaining_seconds) not in (int,float) or not math.isfinite(remaining_seconds):
                raise ValueError('invalid_remaining_deadline')
            seconds=min(seconds,remaining_seconds)
        if seconds<=0:
            return _answer(pack,'temporarily_unavailable',reason='timeout')
        attempts=checks=0
        previous=''
        errors=()
        try:
            async with asyncio.timeout(seconds):
                for attempt in (1,2):
                    attempts=attempt
                    raw=await self.transport.infer(draft_messages(text,pack,errors=errors,previous=previous),
                                                   draft_schema(pack))
                    previous=raw if isinstance(raw,str) else ''
                    try:
                        proposal=_parse(raw,AnswerDraft)
                        errors=validate_draft(proposal,pack)
                    except (ValueError,TypeError,RecursionError):
                        errors=('invalid_draft',)
                    if not errors and proposal.claims:
                        checks+=1
                        review_raw=await self.transport.infer(support_messages(text,pack,proposal),
                                                              output_schema(SupportReport))
                        try:
                            errors=validate_support(_parse(review_raw,SupportReport),proposal)
                        except (ValueError,TypeError,RecursionError):
                            errors=('invalid_support_report',)
                    if not errors:
                        return _answer(pack,'answered',claims=proposal.claims,reason='validated',
                                       attempts=attempts,checks=checks)
        except (TimeoutError,RuntimeFailure) as error:
            timeout=isinstance(error,TimeoutError) or str(error)=='model_timeout'
            return _answer(pack,'temporarily_unavailable',reason='timeout' if timeout else 'tool_error',
                           attempts=attempts,checks=checks)
        except Exception:
            return _answer(pack,'temporarily_unavailable',reason='tool_error',attempts=attempts,checks=checks)
        return _answer(pack,'abstained',reason='repair_exhausted',attempts=attempts,checks=checks)


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
                evidence=None,events=())
            return _answer(prepare(integration),'temporarily_unavailable',reason='timeout')
        if integration.request_id!=context.request_id:
            raise ValueError('request_identity_mismatch')
        return await self.generator.generate(text,integration,remaining_seconds=deadline-loop.time())
