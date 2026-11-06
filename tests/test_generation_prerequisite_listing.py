"""Audit A01: requirement descriptions never calculate a student's eligibility."""
import asyncio
import copy
import json

import pytest

from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
from backend.bintanong_orchestration.adapters import SymbolicAdapter
from backend.bintanong_orchestration.contracts import ReleasePin
from backend.bintanong_orchestration.orchestrator import Orchestrator
from backend.bintanong_orchestration.ports import ReleaseResources, SyntheticReleaseProvider
from backend.bintanong_generation.generator import Generator
from backend.bintanong_private_context.memory import pending_from
from backend.bintanong_routing.contracts import CatalogEntry, RequestContext
from backend.bintanong_symbolic.runtime import CurriculumRuntime
from test_generation_research import NoModel
from test_symbolic_authoring import fixture
from test_symbolic_compiler import rereview
from test_symbolic_runtime import request
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, style_proposal


@pytest.fixture(params=['synthetic', 'unfamiliar'])
def described(request):
    data=fixture()
    key='curriculum-'+request.param
    data[0]['curriculum_id']=key
    for course in data[2]: course['curriculum_id']=key
    return data, key


def run_listing(data, key, language='en', *, facts=()):
    runtime=CurriculumRuntime(rereview(data))
    source=data[1][0]
    catalog=tuple(CatalogEntry(kind='course',entity_id=c['course_id'],program_id=data[0]['program_id'],
        curriculum_id=key,aliases=(c['facts']['course_code']['value'],),reviewed=True,
        source_ref=source.version_id,review_ref='review-1') for c in data[2])
    code=data[2][1]['facts']['course_code']['value']
    text={'en':f'What are the prerequisites of {code}?', 'fil':f'Ano ang kailangan bago kunin ang {code}?',
          'taglish':f'Ano ang prerequisites ng {code}?'}[language]
    start=text.index(code)
    value=proposal(text=text,language=language,mentions=[dict(kind='course',text=code,start=start,end=start+len(code))],
        operations=[dict(name='list_course_prerequisites',target=0)])
    registry=CapabilityRegistry({'list_course_prerequisites':Capability('synthetic_prerequisite_description',
        ('curriculum_id','course_id'))})
    pin=ReleasePin.parse(dict(release_id=runtime.release_id,synthetic=True,rule_bundle_version=runtime.rule_bundle_version,
        sources=[dict(version_id=source.version_id,byte_sha256=source.byte_sha256)]))
    resources=ReleaseResources(pin,catalog,registry,symbolic=SymbolicAdapter(runtime),
        course_labels=tuple((c.entity_id,c.aliases[0]) for c in catalog))
    context=RequestContext(session_id='sess-a',request_id='req-a',program_id=data[0]['program_id'],
        curriculum_id=key,facts=facts)
    style=style_proposal('en',english=['What']) if language=='en' else style_proposal('fil',english=[],filipino=['Ano'])
    async def run():
        routed=[]
        integration=await Orchestrator(FakeTransport(json.dumps(value),style_outputs=[json.dumps(style)]),
            releases=SyntheticReleaseProvider(resources)).run(text,context,routed_sink=routed.append)
        answer=await Generator(NoModel()).generate(text,integration)
        return answer,routed[0],integration
    return asyncio.run(run())


@pytest.mark.parametrize('language',['en','fil','taglish'])
def test_listing_has_no_eligibility_decision_and_needs_no_student_results(described,language):
    data,key=described
    answer,routed,integration=run_listing(data,key,language)
    assert routed.decision.predicate_request.predicate=='list_course_prerequisites'
    assert answer.status=='answered' and answer.decision is None
    assert answer.structured_context.operation=='list_course_prerequisites'
    assert 'SYN101' in answer.text and answer.citations
    assert '?' not in answer.text and 'Conditions:' not in answer.text
    assert 'eligibility check' not in answer.text and 'eligibility mo' not in answer.text
    assert pending_from(routed,answer,dict(integration.course_labels)) is None


@pytest.mark.parametrize('kind',['all_of','any_of','co_requisite','verified_none','unresolved'])
def test_rule_description_preserves_reviewed_tree_and_gaps(described,kind):
    data,key=described
    leaf=data[2][1]['prerequisites']
    node=copy.deepcopy(leaf)
    if kind in ('all_of','any_of'):
        node=dict(kind=kind,items=[copy.deepcopy(leaf),dict(kind='co_requisite',course_id='course-1',
            source_spans=leaf['source_spans'])],source_spans=leaf['source_spans'])
    elif kind=='unresolved':node=dict(kind=kind,reason='Printed condition "Third year standing" is not reviewed',source_spans=leaf['source_spans'])
    elif kind=='verified_none':node=dict(kind=kind,source_spans=leaf['source_spans'])
    else:node['kind']=kind
    data[2][1]['prerequisites']=node
    answer,_,integration=run_listing(data,key)
    assert answer.status=='answered' and answer.decision is None
    result=integration.evidence.course_facts
    assert result.requirement.kind==kind and result.rule_spans
    if kind=='unresolved':assert 'Third year standing' in answer.text and "isn't verified" in answer.text and 'adviser' in answer.text
    if kind=='any_of':assert 'either' in answer.text
    if kind=='all_of':assert 'both' in answer.text
    if kind=='co_requisite':assert 'same term' in answer.text
    if kind=='verified_none':assert 'no prerequisite' in answer.text


def test_eligibility_still_uses_unknown_student_results():
    runtime=CurriculumRuntime(rereview(fixture()))
    assert runtime.check(request()).decision.outcome=='unknown'


def test_description_never_calls_eligibility_worker(monkeypatch):
    runtime=CurriculumRuntime(rereview(fixture()))
    def forbidden(*args, **kwargs):
        raise AssertionError('describing a rule must not evaluate student eligibility')
    monkeypatch.setattr(CurriculumRuntime, '_execute', forbidden)
    result=runtime.look_up(request(predicate='list_course_prerequisites'))
    assert result.status=='complete' and result.requirement.course_id=='course-1'
    assert 'decision' not in result.model_dump(mode='json')


@pytest.mark.parametrize('change,expected',[('unknown_course','not_found'),('wrong_curriculum','not_found'),('unreviewed','not_reviewed')])
def test_description_does_not_invent_unavailable_rules(change,expected):
    data=fixture()
    if change=='unreviewed':
        data[2][1]['review_state']='draft'
        data[2][1]['review_refs']=[]
    from test_symbolic_authoring import run as author
    runtime=CurriculumRuntime(author(data) if change=='unreviewed' else rereview(data))
    bound=request(course='missing' if change=='unknown_course' else 'course-2',
        curriculum='missing' if change=='wrong_curriculum' else 'curriculum-synthetic-1',
        predicate='list_course_prerequisites')
    result=runtime.look_up(bound)
    assert result.status==expected and result.requirement is None and not result.rule_spans


def test_old_lookup_serialization_omits_new_description_fields():
    from backend.bintanong_symbolic.course_facts import CourseFactsResult
    result=CourseFactsResult.parse(dict(schema_version=CourseFactsResult.SCHEMA_VERSION,synthetic=True,
        predicate='course_facts',inputs=[],status='unsupported',courses=[],scope=None))
    assert not {'requirement','rule_spans','rule_bundle_version'} & result.model_dump(mode='json').keys()


def test_nested_unreviewed_condition_keeps_its_printed_limit(described):
    data,key=described
    leaf=data[2][1]['prerequisites']
    data[2][1]['prerequisites']=dict(kind='all_of',items=[copy.deepcopy(leaf),dict(kind='unresolved',
        reason='Printed condition "Third year standing" is not reviewed',source_spans=leaf['source_spans'])],
        source_spans=leaf['source_spans'])
    answer,_,_=run_listing(data,key)
    assert 'Third year standing' in answer.text and 'adviser' in answer.text
    assert answer.decision is None
