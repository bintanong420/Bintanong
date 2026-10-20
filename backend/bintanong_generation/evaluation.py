"""Bounded synthetic observations; semantic/style accuracy requires human review."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from ..bintanong_contracts.base import Record
from ..bintanong_orchestration.contracts import IntegrationResult
from ..bintanong_routing.contracts import prepare_query
from ..bintanong_routing.transport import LlamaTransport
from .generator import Generator
from .prompt import (PROMPT_SHA256,SUPPORT_PROMPT_SHA256,
                     SHORT_PROMPT_SHA256,SHORT_SUPPORT_PROMPT_SHA256)
from .scope import DOCUMENT_PROMPT_SHA256,DOCUMENT_SUPPORT_PROMPT_SHA256


class GenerationCase(Record):
    case_id: str=Field(pattern=r'^[a-z0-9-]+$',max_length=128)
    family_id: str=Field(pattern=r'^[a-z0-9-]+$',max_length=128)
    split: Literal['dev']
    synthetic: Literal[True]
    question: str=Field(min_length=1,max_length=8192)
    integration: IntegrationResult


def load_cases(values):
    if not isinstance(values,list) or not 1<=len(values)<=30:
        raise ValueError('bounded_synthetic_dev_cases_required')
    cases=tuple(GenerationCase.parse(value) for value in values)
    if len({c.case_id for c in cases})!=len(cases): raise ValueError('duplicate_case_id')
    for case in cases: prepare_query(case.question)
    return cases


async def observe(cases,generator,*,evaluation_kind):
    if evaluation_kind not in ('mock','real_model'): raise ValueError('explicit_evaluation_kind_required')
    if generator.explanation_profile=='scoped':
        prompt_hash,support_hash=DOCUMENT_PROMPT_SHA256,DOCUMENT_SUPPORT_PROMPT_SHA256
    elif generator.reference_profile=='short':
        prompt_hash,support_hash=SHORT_PROMPT_SHA256,SHORT_SUPPORT_PROMPT_SHA256
    else:
        prompt_hash,support_hash=PROMPT_SHA256,SUPPORT_PROMPT_SHA256
    observations=[]
    for case in cases:
        answer=await generator.generate(case.question,case.integration)
        evidence=case.integration.evidence
        expected=evidence.symbolic.decision if evidence is not None and evidence.symbolic else None
        observations.append(dict(case_id=case.case_id,family_id=case.family_id,
            requested_language=case.integration.response_style,answer=answer.model_dump(mode='json'),
            canonical_decision_preserved=answer.decision==expected,
            generation_mode=('host_only' if answer.draft_attempts==0 else
                'documentary_model' if generator.explanation_profile=='scoped' else 'legacy_model'),
            human_language_review='pending',human_claim_support_review='pending'))
    return dict(schema_version='bintanong-generation-observations-v1',candidate_only=True,
        institutional_use_allowed=False,evaluation_kind=evaluation_kind,
        actual_model_accuracy='unmeasured',prompt_sha256=prompt_hash,
        support_prompt_sha256=support_hash,explanation_profile=generator.explanation_profile,
        reference_profile=generator.reference_profile,observations=observations)


def _output_path(path,evidence_root):
    path,root=Path(path).resolve(),Path(evidence_root).resolve()
    if path==root or not path.is_relative_to(root): raise ValueError('output_outside_evidence_root')
    return path


def write_report(report,path,evidence_root):
    path=_output_path(path,evidence_root)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--url',default='http://127.0.0.1:18087')
    parser.add_argument('--timeout',type=float,default=120)
    args=parser.parse_args()
    _output_path(args.output,args.evidence_root)
    raw=args.input.read_bytes()
    cases=load_cases(json.loads(raw))
    transport=LlamaTransport(args.url,timeout_seconds=args.timeout)
    result=asyncio.run(observe(cases,Generator(transport,timeout_seconds=args.timeout),evaluation_kind='real_model'))
    result.update(input_sha256=hashlib.sha256(raw).hexdigest(),runtime_metadata=transport.metadata)
    write_report(result,args.output,args.evidence_root)


if __name__=='__main__': main()
