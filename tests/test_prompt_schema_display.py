"""Prompt size reduction must preserve schema meaning and decoder constraints."""
from copy import deepcopy
import json

import pytest
from jsonschema import Draft202012Validator

from backend.bintanong_contracts.schema_display import compact_for_prompt
from backend.bintanong_routing.prompt import output_schema as routing_schema
from backend.bintanong_routing.style import style_output_schema
from backend.bintanong_generation.contracts import AnswerDraft,SupportReport
from backend.bintanong_generation.prompt import output_schema
from test_routing_contracts import proposal


def schemas():
    return [routing_schema(),style_output_schema(),output_schema(AnswerDraft),output_schema(SupportReport)]


@pytest.mark.parametrize('full',schemas(),ids=['routing','style','draft','support'])
def test_display_keeps_acceptance_for_valid_and_invalid_candidates(full):
    short=compact_for_prompt(full)
    original=Draft202012Validator(full); compact=Draft202012Validator(short)
    Draft202012Validator.check_schema(short)
    values=[proposal(),proposal(route='RAG',operations=[]),
        proposal(audience='excluded',route=None,control='unsupported_scope',operations=[]),
        proposal(audience='unknown',route=None,control='clarify',operations=[]),
        dict(schema_version='bintanong-response-style-v1',style=dict(
            english_fragments=['hello'],filipino_fragments=[],preferred_response_style='english_only')),
        dict(schema_version='bintanong-answer-draft-v1',language='en',release_id='release-synthetic',
            decision_outcome=None,claims=[dict(claim_id='c1',text='Fictional fact',evidence_ids=['ev-'+'a'*64])]),
        dict(schema_version='bintanong-prose-support-v1',verdicts=[dict(claim_id='c1',verdict='supported')],
            language_appropriate=True,within_scope=True)]
    assert any(original.is_valid(value) for value in values)
    for value in values:
        variants=[value,None,[],dict(value,extra='forbidden')]
        variants += [{k:v for k,v in value.items() if k!=drop} for drop in value]
        for variant in variants:
            assert original.is_valid(variant)==compact.is_valid(variant)


def test_factorization_reduces_repeated_routing_schema_without_mutating_decoder():
    full=routing_schema(); before=deepcopy(full)
    short=compact_for_prompt(full)
    assert full==before
    assert len(json.dumps(short)) < len(json.dumps(full))*0.55
    # Branches must still select exactly one legal audience/route/control shape.
    old,new=Draft202012Validator(full),Draft202012Validator(short)
    for audience in ('undergraduate','excluded','unrelated','unknown'):
        for route in (None,'RAG','Symbolic','Hybrid'):
            for control in (None,'clarify','greeting','unsupported_scope','evidence_unavailable'):
                for operations in ([],[dict(name='check_prerequisite_eligibility',target=0)]):
                    value=proposal(audience=audience,route=route,control=control,operations=operations)
                    assert old.is_valid(value)==new.is_valid(value)


def test_real_property_names_and_literal_objects_are_not_schema_annotations():
    schema={'type':'object','title':'Display annotation','properties':{
        'title':{'type':'string','title':'Actual title field'},
        'constant':{'const':{'title':'literal data','oneOf':['not','a schema']}}},
        'required':['title','constant'],'additionalProperties':False}
    short=compact_for_prompt(schema)
    value={'title':'student title','constant':{'title':'literal data','oneOf':['not','a schema']}}
    assert Draft202012Validator(short).is_valid(value)
    assert short['properties']['constant']['const']==value['constant']
    assert 'title' in short['properties'] and 'title' not in short


