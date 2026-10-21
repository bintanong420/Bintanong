"""Run one controlled candidate request through actual configured services."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path

from pydantic import Field

from ..bintanong_contracts.base import Record
from ..bintanong_routing.contracts import RequestContext, prepare_query
from .application import RuntimeSettings, RuntimeSpec, build_application


class RuntimeRequest(Record):
    question: str = Field(min_length=1,max_length=8192)
    context: RequestContext


def _input_bytes(path, limit):
    with Path(path).open('rb') as stream:
        raw=stream.read(limit+1)
    if len(raw)>limit: raise ValueError('input_too_large')
    return raw


def read_json(path, limit=4_194_304):
    return json.loads(_input_bytes(path,limit))


def load_request(path):
    return _parse_request(read_json(path,131_072))


def _parse_request(value):
    request=RuntimeRequest.parse(value)
    prepare_query(request.question)
    return request


def output_path(path,root):
    path,root=Path(path).resolve(),Path(root).resolve()
    if path==root or not path.is_relative_to(root):
        raise ValueError('output_outside_evidence_root')
    return path


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('spec',type=Path)
    parser.add_argument('request',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--url',default='http://127.0.0.1:18087')
    parser.add_argument('--model-path',type=Path)
    parser.add_argument('--routing-profile',choices=('separate','combined'),default='separate',
        help='combined is experimental and failed multilingual promotion; default: separate')
    parser.add_argument('--explanation-profile',choices=('legacy','scoped','guarded','covered','parts'),default='parts',
        help='default: scoped; covered and guarded are experiments that failed quality gates')
    parser.add_argument('--inference-timeout',type=float,default=120)
    parser.add_argument('--stage-timeout',type=float,default=120)
    parser.add_argument('--generation-timeout',type=float,default=120)
    parser.add_argument('--request-timeout',type=float,default=180)
    args=parser.parse_args(argv)
    output=output_path(args.output,args.evidence_root)
    if output.exists(): raise ValueError('refusing_to_overwrite_observation')
    spec_raw=_input_bytes(args.spec,4_194_304)
    request_raw=_input_bytes(args.request,131_072)
    spec=RuntimeSpec.parse(json.loads(spec_raw))
    request=_parse_request(json.loads(request_raw))
    settings=RuntimeSettings(args.url,args.inference_timeout,args.stage_timeout,
        args.generation_timeout,args.request_timeout,routing_profile=args.routing_profile,
        explanation_profile=args.explanation_profile)
    app=build_application(spec,model_path=args.model_path,settings=settings)
    try:
        result=asyncio.run(app.run(request.question,request.context))
    finally:
        app.close()
    report=result.model_dump(mode='json')
    report.update(spec_sha256=hashlib.sha256(spec_raw).hexdigest(),
        routing_profile=settings.routing_profile,
        explanation_profile=settings.explanation_profile,
        request_sha256=hashlib.sha256(request_raw).hexdigest(),
        budgets=dict(inference=settings.inference_timeout,stage=settings.stage_timeout,
            generation=settings.generation_timeout,request=settings.request_timeout),
        actual_model_accuracy='unmeasured',human_output_review='pending')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    # Final text remains in the explicit evidence file, not general service logs.
    print('Candidate request recorded:',result.answer.status)


if __name__=='__main__': main()
