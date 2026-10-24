"""Explicit research composition of Lawrence's API; no fictional or unauthenticated fallback."""
import asyncio
import base64
import json
import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field

from backend.bintanong_orchestration.adapters import _BoundedWorker
from backend.bintanong_orchestration.ports import ReleaseUnavailable
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_private_context.worker import extract_isolated
from backend.bintanong_retrieval.http_query import HttpQueryEncoder
from backend.bintanong_retrieval.query import configuration_identity
from backend.bintanong_routing.transport import LlamaTransport
from backend.bintanong_runtime.hosted_curricula import load_release_curricula
from backend.bintanong_runtime.hosted_storage import HostedReleaseStorage
from backend.bintanong_runtime.research import build_multi_research_resources
from backend.bintanong_storage.client import SupabaseStorageClient
from backend.bintanong_storage.config import StorageConfig
from .app import ApiServices, ApiSettings, create_app
from .auth import SupabaseAuth
from .chat import CurriculumOption
from .hosted_snapshot import bind_document_policy, load_document_snapshot
from .research_pipeline import ResearchPipeline


class ResearchConfig(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    schema_version: Literal['bintanong-student-runtime-v1']
    authorization_ref: str = Field(pattern=r'^research-[A-Za-z0-9_-]+$', max_length=128)
    hosted_release_id: str = Field(pattern=r'^[A-Za-z0-9_-]+$', max_length=128)
    document_policy: str = Field(min_length=1)
    model_url: str = 'http://127.0.0.1:18088'
    embedding_url: str = 'http://127.0.0.1:8001'
    program_names: dict[str, list[str]] = Field(default_factory=dict)
    curriculum_names: dict[str, list[str]] = Field(default_factory=dict)


def read_config(path):
    with Path(path).open('rb') as file:
        body = file.read(64 * 1024 * 1024 + 1)
    if len(body) > 64 * 1024 * 1024:
        raise ValueError('research_artifact_too_large')
    return json.loads(body)


def service_url(value):
    url = urlsplit(value)
    if url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in ('', '/'):
        raise ValueError('invalid_service_url')
    return value.rstrip('/')


def public_key(value):
    if value.startswith('sb_publishable_'):
        return value
    try:
        payload = value.split('.')[1]
        role = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))['role']
        if role == 'anon':
            return value
    except (ValueError, KeyError, IndexError, TypeError):
        pass
    raise ValueError('public_runtime_key_required')


class ResearchProvider:
    def __init__(self, client, resources, spec, chunks, ledgers):
        self.client, self.resources, self.spec, self.chunks = client, resources, spec, chunks
        self.digests = {key: value['content_sha256'] for key, value in ledgers.items()}
        self.worker = _BoundedWorker()

    async def probe_supabase(self):
        def check():
            engine = self.resources.retrieval.engine
            # A unit vector exercises the pinned pgvector RPC without model inference or student text.
            result = engine.client.rpc('retrieve_context', dict(
                p_release_id=self.resources.pin.release_id,
                p_config=configuration_identity(engine.encoder.config),
                query_embedding=[1.0] + [0.0] * (engine.encoder.config.dimension - 1),
                p_top_k=3, p_min_similarity=1.0, p_scope=list(self.resources.document_scope)), role='runtime')
            return result.get('status') == 'ok' and result.get('release_id') == self.resources.pin.release_id
        try:
            if await self.worker.run(check):
                return True, None
        except Exception:
            pass
        return False, 'hosted retrieval unavailable'

    async def pin(self):
        def check():
            try:
                HostedReleaseStorage(self.client, pin_release_id=self.resources.pin.release_id,
                    hosted_release_id=self.spec.hosted_release_id, authorization_ref=self.spec.authorization_ref, chunks=self.chunks)
                rows = self.client.select('release_curriculum_ledgers', role='runtime',
                    filters={'release_id': 'eq.' + self.spec.hosted_release_id})
                if len(rows) != len(self.digests) or {r['curriculum_id']: r['ledger_sha256'] for r in rows} != self.digests:
                    raise ValueError('curriculum_release_differs')
            except Exception:
                raise ReleaseUnavailable('research_release_unavailable') from None
            return self.resources
        return await self.worker.run(check)


def load_research_app(path=None):
    path = path or os.environ.get('BINTANONG_RESEARCH_CONFIG')
    if not path:
        raise ValueError('research_configuration_required')
    path = Path(path).resolve()
    spec = ResearchConfig.model_validate(read_config(path))
    model_url = service_url(spec.model_url)
    url, key = os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_ANON_KEY')
    if not url or not key:
        raise ValueError('research_credentials_required')
    public_key(key)
    auth = SupabaseAuth(url, key)
    client = SupabaseStorageClient(StorageConfig(api_url=url, anon_key=key, service_role_key='', db_url=''))
    encoder = None
    try:
        ledgers = load_release_curricula(client, release_id=spec.hosted_release_id, authorization_ref=spec.authorization_ref)
        if not ledgers:
            raise ValueError('reviewed_curricula_required')
        package = bind_document_policy(load_document_snapshot(client, release_id=spec.hosted_release_id,
            authorization_ref=spec.authorization_ref), read_config(path.parent / spec.document_policy))
        encoder = HttpQueryEncoder(service_url(spec.embedding_url))
        resources = build_multi_research_resources(ledgers, package, encoder=encoder,
            authorization_ref=spec.authorization_ref, hosted={'client': client, 'release_id': spec.hosted_release_id},
            program_names=spec.program_names, curriculum_names=spec.curriculum_names)
        provider = ResearchProvider(client, resources, spec, package['chunks'], ledgers)
        pipeline = ResearchPipeline(lambda: LlamaTransport(model_url, prefix_cache=True), provider)
        curricula = []
        for curriculum, ledger in sorted(ledgers.items()):
            program = ledger['scope']['program_id']
            filename = ledger['sources'][0]['filename']
            curricula.append(CurriculumOption(program, curriculum,
                next(iter(spec.program_names.get(program, ())), filename),
                next(iter(spec.curriculum_names.get(curriculum, ())), 'Reviewed research record')))
        def extract(data, program, curriculum):
            return extract_isolated(data, resources.catalog, program_id=program, curriculum_id=curriculum)
        async def ready():
            await provider.pin()
            return True
        async def close():
            try:
                await asyncio.to_thread(encoder.close)
            finally:
                await asyncio.to_thread(client.close)
        origins = tuple(value.strip() for value in os.environ.get('STUDENT_ALLOWED_ORIGINS', 'http://127.0.0.1:3215').split(',') if value.strip())
        app = create_app(ApiServices(sessions=SessionStore(), curricula=tuple(curricula), pipeline=pipeline,
            extract_rows=extract, course_labels=dict(resources.course_labels), auth=auth, ready=ready, close=close,
            supabase_probe=provider.probe_supabase),
            ApiSettings(allowed_origins=origins, require_auth=True))
        app.state.research_provider = provider
        return app
    except BaseException:
        try:
            if encoder is not None:
                encoder.close()
        finally:
            client.close()
        raise
