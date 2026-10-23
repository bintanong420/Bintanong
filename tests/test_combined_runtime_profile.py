"""Trusted profile selection reaches actual dispatch without changing source holds."""
import asyncio
import json
from types import SimpleNamespace

import pytest

from backend.bintanong_orchestration.orchestrator import Orchestrator
from backend.bintanong_orchestration.ports import SyntheticReleaseProvider
from backend.bintanong_runtime.application import RuntimeSettings, RuntimeSpec, build_application
from test_orchestration_pipeline import resources, ctx
from test_routing_router import FakeTransport
from test_routing_combined import packet
from test_runtime_composition import spec, Database


@pytest.mark.parametrize('route',['RAG','Symbolic','Hybrid'])
def test_combined_profile_routes_and_joins_required_evidence_with_one_inference(route):
    value=packet(text='A1 policy',route=route,operations=[] if route=='RAG' else
        [dict(name='check_prerequisite_eligibility',target=0)])
    model=FakeTransport(json.dumps(value));release=resources()
    result=asyncio.run(Orchestrator(model,releases=SyntheticReleaseProvider(release),
        routing_profile='combined').run('A1 policy',ctx()))
    assert result.status=='ready' and result.route==route
    assert len(model.calls)==1 and result.events[1].retry_count==0
    assert len(release.retrieval.calls)==(route!='Symbolic')
    assert len(release.symbolic.calls)==(route!='RAG')
    assert result.candidate_only and not result.institutional_use_allowed


def test_combined_default_provider_still_holds_before_inference():
    model=FakeTransport(json.dumps(packet()))
    result=asyncio.run(Orchestrator(model,routing_profile='combined').run('A1',ctx()))
    assert result.status=='held' and not model.calls


@pytest.mark.parametrize('invalid',['automatic','RAG',None,True])
def test_invalid_trusted_profile_is_rejected_before_services(invalid):
    with pytest.raises(ValueError,match='routing_profile'):
        RuntimeSettings(routing_profile=invalid)
    with pytest.raises(ValueError,match='routing_profile'):
        Orchestrator(None,routing_profile=invalid)


def test_application_passes_profile_and_observation_records_it(monkeypatch):
    import backend.bintanong_runtime.application as module
    original=module.Orchestrator;seen=[]
    def observe(*args,**kwargs):
        seen.append(kwargs['routing_profile'])
        return original(*args,**kwargs)
    monkeypatch.setattr(module,'Orchestrator',observe)
    class Held(Database):
        def select(self,*args,**kwargs):return []
    data=spec();app=build_application(RuntimeSpec.parse(data),client=Held(data),
        settings=RuntimeSettings(routing_profile='combined'))
    result=asyncio.run(app.run('A1',ctx()))
    assert seen==['combined'] and result.routing_profile=='combined'
    assert result.model_calls==()


@pytest.mark.parametrize('profile',['combined','separate',None])
def test_cli_profile_is_trusted_configuration_and_recorded(tmp_path,monkeypatch,profile):
    import backend.bintanong_runtime.cli as cli
    seen=[]
    class App:
        async def run(self,*args):
            return SimpleNamespace(answer=SimpleNamespace(status='answered'),
                model_dump=lambda **kwargs:dict(answer=dict(status='answered')))
        def close(self):pass
    def build(*args,**kwargs):seen.append(kwargs['settings']);return App()
    monkeypatch.setattr(cli,'build_application',build)
    spec_path=tmp_path/'spec.json';spec_path.write_text(json.dumps(spec()))
    request=tmp_path/'request.json';request.write_text(json.dumps(dict(question='A1',context=ctx().model_dump(mode='json'))))
    output=tmp_path/'raw/run.json'
    args=[str(spec_path),str(request),'--output',str(output),'--evidence-root',str(output.parent)]
    if profile is not None:args+=['--routing-profile',profile]
    cli.main(args)
    expected=profile or 'separate'
    assert seen[0].routing_profile==expected
    assert json.loads(output.read_text())['routing_profile']==expected


def test_unselected_candidate_does_not_change_runtime_or_orchestrator_default():
    assert RuntimeSettings().routing_profile=='separate'
    assert Orchestrator(None).routing_profile=='separate'
