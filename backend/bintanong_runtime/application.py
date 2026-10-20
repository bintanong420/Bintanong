"""Actual service adapters, with synthetic fixture authorization kept explicit."""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
from dataclasses import dataclass
from time import perf_counter
from typing import Literal

from pydantic import Field

from ..bintanong_contracts.base import Record
from ..bintanong_contracts.symbolic import Capability, CapabilityRegistry
from ..bintanong_generation.contracts import CandidateAnswer
from ..bintanong_generation.generator import AnswerPipeline, Generator
from ..bintanong_orchestration.adapters import RetrievalAdapter, SymbolicAdapter
from ..bintanong_orchestration.contracts import ReleasePin, StageEvent
from ..bintanong_orchestration.orchestrator import Orchestrator
from ..bintanong_orchestration.ports import ReleaseResources, ReleaseUnavailable
from ..bintanong_retrieval.engine import RetrievalEngine
from ..bintanong_retrieval.query import QueryEncoder
from ..bintanong_retrieval.types import RetrievalSettings
from ..bintanong_routing.contracts import CatalogEntry, RequestContext
from ..bintanong_routing.transport import LlamaTransport, RuntimeFailure
from ..bintanong_storage.client import SupabaseStorageClient
from ..bintanong_symbolic.runtime import CurriculumRuntime


class RuntimeSpec(Record):
    schema_version: Literal['bintanong-runtime-spec-v1']
    synthetic: Literal[True]
    bundle: dict
    pin: ReleasePin
    catalog: tuple[CatalogEntry, ...] = Field(max_length=256)
    embedding_assets: dict[str, str]


@dataclass(frozen=True)
class RuntimeSettings:
    model_url: str = 'http://127.0.0.1:18087'
    inference_timeout: float = 120
    stage_timeout: float = 120
    generation_timeout: float = 120
    request_timeout: float = 180
    routing_profile: Literal['separate','combined'] = 'separate'
    generation_reference_profile: Literal['canonical','short'] = 'canonical'

    def __post_init__(self):
        if self.routing_profile not in ('separate','combined'):
            raise ValueError('invalid_routing_profile')
        if self.generation_reference_profile not in ('canonical','short'):
            raise ValueError('invalid_generation_reference_profile')
        for name in ('inference_timeout','stage_timeout','generation_timeout','request_timeout'):
            value=getattr(self,name)
            maximum=300 if name=='stage_timeout' else 600
            if type(value) not in (int,float) or not math.isfinite(value) or not 0<value<=maximum:
                raise ValueError('invalid_runtime_budget')


class CheckedSyntheticReleaseProvider:
    """Read-only anon/RLS verification; never publish or promote a source/release."""
    def __init__(self, client, resources):
        self.client, self.resources = client, resources

    def _check(self):
        pin=self.resources.pin
        def rows(table, filters):
            return self.client.select(table,filters=filters,role='runtime')
        release=rows('knowledge_releases',{'release_id':'eq.'+pin.release_id})
        if len(release)!=1 or release[0]['status']!='active':
            raise ReleaseUnavailable('synthetic_release_not_available')
        versions={s.version_id:s.byte_sha256 for s in pin.sources}
        members=rows('release_document_versions',{'release_id':'eq.'+pin.release_id})
        chunks=rows('release_chunks',{'release_id':'eq.'+pin.release_id})
        if ({v['version_id'] for v in members}!=set(versions) or
                {c['chunk_id'] for c in chunks}!={d.chunk_id for d in pin.documents}):
            raise ReleaseUnavailable('synthetic_release_membership_mismatch')
        for version,sha in versions.items():
            found=rows('document_versions',{'version_id':'eq.'+version})
            if len(found)!=1 or found[0]['byte_sha256']!=sha:
                raise ReleaseUnavailable('synthetic_source_mismatch')
            documents=rows('documents',{'document_id':'eq.'+found[0]['document_id']})
            if len(documents)!=1 or documents[0]['synthetic'] is not True:
                raise ReleaseUnavailable('institutional_source_held')
        return self.resources

    async def pin(self):
        return await asyncio.to_thread(self._check)


class ModelCall(Record):
    schema_sha256: str
    duration_ms: float
    outcome: Literal['ok','failed']
    diagnostic: str | None = None


class RuntimeRun(Record):
    schema_version: Literal['bintanong-runtime-run-v1'] = 'bintanong-runtime-run-v1'
    synthetic: Literal[True] = True
    institutional_use_allowed: Literal[False] = False
    routing_profile: Literal['separate','combined'] = 'separate'
    generation_reference_profile: Literal['canonical','short'] = 'canonical'
    answer: CandidateAnswer
    events: tuple[StageEvent,...]
    model_calls: tuple[ModelCall,...]
    duration_ms: float


class _ObservedTransport:
    def __init__(self, transport):
        self.transport,self.calls=transport,[]

    async def infer(self,messages,schema):
        started=perf_counter()
        outcome,diagnostic='failed',None
        try:
            result=await self.transport.infer(messages,schema)
            outcome='ok'
            return result
        except RuntimeFailure as exc:
            allowed={'model_timeout','model_connection_error','model_http_error',
                'invalid_server_response','truncated_output','context_overflow',
                'server_response_too_large'}
            diagnostic=str(exc) if str(exc) in allowed else 'model_failure'
            raise
        finally:
            self.calls.append(ModelCall(schema_sha256=hashlib.sha256(
                json.dumps(schema,sort_keys=True).encode()).hexdigest(),
                duration_ms=(perf_counter()-started)*1000,outcome=outcome,diagnostic=diagnostic))


class RuntimeApplication:
    def __init__(self, client, encoder, releases, settings, owns_client):
        self.client,self.encoder,self.releases=client,encoder,releases
        self.settings,self.owns_client=settings,owns_client

    def close(self):
        if self.owns_client:
            self.client.close()

    async def run(self,text: str,context: RequestContext) -> RuntimeRun:
        settings=self.settings
        model=_ObservedTransport(LlamaTransport(settings.model_url,
            timeout_seconds=settings.inference_timeout))
        orchestrator=Orchestrator(model,releases=self.releases,stage_timeout=settings.stage_timeout,
            routing_profile=settings.routing_profile)
        # Capture evidence-stage telemetry in this request only. No raw text/grades.
        events=[]
        class ObservedOrchestrator:
            async def run(self,text,context):
                integration=await orchestrator.run(text,context)
                events.extend(integration.events)
                return integration
        pipeline=AnswerPipeline(ObservedOrchestrator(),Generator(model,
            timeout_seconds=settings.generation_timeout,reference_profile=settings.generation_reference_profile),
            timeout_seconds=settings.request_timeout)
        started=perf_counter()
        answer=await pipeline.run(text,context)
        return RuntimeRun(answer=answer,events=tuple(events),model_calls=tuple(model.calls),
            duration_ms=(perf_counter()-started)*1000,routing_profile=settings.routing_profile,
            generation_reference_profile=settings.generation_reference_profile)


def build_application(spec: RuntimeSpec, *, client=None, model_path=None,
                      settings: RuntimeSettings | None=None) -> RuntimeApplication:
    spec=RuntimeSpec.parse(spec.model_dump(mode='json'))
    runtime=CurriculumRuntime.from_bundle(spec.bundle)
    # from_bundle rejects institutional ledgers before a client/model is opened.
    if (runtime.release_id!=spec.pin.release_id or
            runtime.rule_bundle_version!=spec.pin.rule_bundle_version):
        raise ValueError('runtime_bundle_pin_mismatch')
    sources={s['version_id']:s['byte_sha256'] for s in spec.bundle['ledger']['sources']}
    if sources!={s.version_id:s.byte_sha256 for s in spec.pin.sources}:
        raise ValueError('runtime_bundle_source_mismatch')
    encoder=QueryEncoder(model_path=model_path,asset_digests=spec.embedding_assets)
    registry=CapabilityRegistry({name:Capability(cap,('curriculum_id','course_id'))
        for name,cap in [('check_prerequisite_eligibility','synthetic_prerequisite_check'),
            ('list_missing_prerequisites','synthetic_missing_prerequisites'),
            ('list_affected_courses','synthetic_dependency_inspection')]})
    owns_client=client is None
    client=SupabaseStorageClient() if client is None else client
    try:
        resources=ReleaseResources(spec.pin,spec.catalog,registry,
            RetrievalAdapter(RetrievalEngine(client,encoder,RetrievalSettings(
                context_budget=2048,policy_id='synthetic-mechanics-only'))),SymbolicAdapter(runtime))
        return RuntimeApplication(client,encoder,CheckedSyntheticReleaseProvider(client,resources),
            settings or RuntimeSettings(),owns_client)
    except BaseException:
        if owns_client: client.close()
        raise
