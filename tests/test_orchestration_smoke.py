"""Real Router + RetrievalEngine + Janus; scripted model and synthetic DB/vector.

This proves module integration, not actual model quality or institutional sources.
"""
import asyncio
import json

import pytest

from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
from backend.bintanong_orchestration.adapters import RetrievalAdapter, SymbolicAdapter
from backend.bintanong_orchestration.contracts import ReleasePin
from backend.bintanong_orchestration.orchestrator import Orchestrator
from backend.bintanong_orchestration.ports import ReleaseResources, SyntheticReleaseProvider
from backend.bintanong_retrieval.engine import RetrievalEngine
from backend.bintanong_retrieval.types import RetrievalSettings
from backend.bintanong_routing.contracts import CatalogEntry
from backend.bintanong_symbolic.runtime import CurriculumRuntime
from test_orchestration_adapters import context
from test_retrieval_engine import Client, Encoder
from test_routing_contracts import proposal
from test_routing_router import FakeTransport
from test_symbolic_authoring import fixture, run as ledger


@pytest.mark.parametrize('route,operation', [('RAG',None),
    ('Symbolic','check_prerequisite_eligibility'), ('Hybrid','check_prerequisite_eligibility'),
    ('Symbolic','list_missing_prerequisites'), ('Hybrid','list_missing_prerequisites'),
    ('Symbolic','list_affected_courses'), ('Hybrid','list_affected_courses')])
def test_three_route_real_module_smoke_with_fictional_sources(route,operation):
    async def scenario():
        curriculum = ledger(fixture())
        runtime = CurriculumRuntime(curriculum)
        source = curriculum['sources'][0]
        chunk_id = 'b'*64
        client = Client()
        client.payload['release_id'] = runtime.release_id
        row = client.payload['items'][0]
        row['chunk'].update(chunk_id=chunk_id, version_id=source['version_id'],
            byte_sha256=source['byte_sha256'])
        row['version'].update(version_id=source['version_id'],byte_sha256=source['byte_sha256'])
        row['spans'][0].update(version_id=source['version_id'],byte_sha256=source['byte_sha256'])
        retrieval = RetrievalAdapter(RetrievalEngine(client,Encoder(),RetrievalSettings(
            context_budget=1000,policy_id='synthetic-mechanics-only')))
        pin = ReleasePin.parse(dict(release_id=runtime.release_id, synthetic=True,
            rule_bundle_version=runtime.rule_bundle_version,
            sources=[dict(version_id=source['version_id'],byte_sha256=source['byte_sha256'])],
            documents=[dict(chunk_id=chunk_id,version_id=source['version_id'],
                byte_sha256=source['byte_sha256'])]))
        catalog = (CatalogEntry(kind='course',entity_id='course-2',program_id='program-synthetic',
            curriculum_id='curriculum-synthetic-1', aliases=('SYN201',),
            source_ref=source['version_id'],review_ref='synthetic-review',reviewed=True),)
        registry = CapabilityRegistry({name:Capability(cap,('curriculum_id','course_id'))
            for name,cap in [('check_prerequisite_eligibility','synthetic_prerequisite_check'),
                ('list_missing_prerequisites','synthetic_missing_prerequisites'),
                ('list_affected_courses','synthetic_dependency_inspection')]})
        provider = SyntheticReleaseProvider(ReleaseResources(pin,catalog,registry,retrieval,
            SymbolicAdapter(runtime)))
        value = proposal(language='en',route=route,
            mentions=[dict(kind='course',text='SYN201',start=0,end=6)],
            operations=[] if route=='RAG' else [dict(name=operation,target=0)])
        style = dict(schema_version='bintanong-response-style-v1',style=dict(
            english_fragments=['SYN201'],filipino_fragments=[],preferred_response_style='english_only'))
        model = FakeTransport(json.dumps(value),style_outputs=[json.dumps(style)])
        result = await Orchestrator(model,releases=provider).run('SYN201',context(state='passed'))
        assert result.status == 'ready' and result.evidence.pin.release_id == runtime.release_id
        assert result.evidence.route == route
        if route != 'RAG':
            if operation == 'list_affected_courses':
                assert result.evidence.symbolic is None
                assert result.evidence.dependencies.status == 'complete'
                assert result.evidence.dependencies.course_ids == ()
                assert result.evidence.permitted_scope == ('dependency_listing'
                    if route == 'Symbolic' else 'combined_explanation')
            else:
                assert result.evidence.symbolic.decision.outcome == 'eligible'
                assert result.evidence.symbolic.rule_spans
                assert result.evidence.symbolic.decision.predicate == operation
        if route != 'Symbolic':
            assert result.evidence.documents.status == 'ok'
        assert bool(client.roles) == (route != 'Symbolic')
        assert len(model.calls) == 2
    asyncio.run(scenario())
