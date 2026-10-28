"""Explicit, authenticated composition of the current sealed research package.

Configuration is a trusted local file, never a student request. Loading performs runtime reads only;
it does not activate a package, download models, or fall back to synthetic institutional answers.
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field

from backend.bintanong_generation.generator import Generator
from backend.bintanong_orchestration.adapters import _BoundedWorker
from backend.bintanong_orchestration.ports import ReleaseUnavailable
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_private_context.worker import extract_isolated
from backend.bintanong_retrieval.query import QueryEncoder
from backend.bintanong_routing.transport import LlamaTransport
from backend.bintanong_runtime.hosted_curricula import load_release_curricula
from backend.bintanong_runtime.hosted_storage import HostedReleaseStorage
from backend.bintanong_runtime.research import build_multi_research_resources
from backend.bintanong_storage.client import SupabaseStorageClient
from backend.bintanong_storage.config import StorageConfig
from .app import ApiServices, ApiSettings, create_app
from .auth import SupabaseAuth
from .chat import CurriculumOption
from .probes import probe_http_service, probe_janus
from .research_pipeline import ResearchPipeline

RELEASE = 'p11-research-corrected-20261026'
AUTHORIZATION = 'research-owner-20261021'
FILES = ('draft-chunks.json', 'draft-source-versions.json', 'draft-embedding-manifest.json',
         'draft-subject-catalogue.json', 'draft-source-review-register.json',
         'draft-embedding-records.jsonl', 'subject-context-budgets.json')


class ResearchApiConfig(BaseModel):
    model_config = ConfigDict(extra='forbid')
    schema_version: Literal['bintanong-research-api-v1']
    pin_path: Path
    pin_sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    seal_sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    encoder_assets_path: Path
    encoder_model_path: Path
    allowed_origins: tuple[str, ...] = Field(min_length=1)
    model_url: str = 'http://127.0.0.1:18088'
    program_names: dict[str, list[str]] = Field(default_factory=dict)
    curriculum_names: dict[str, list[str]] = Field(default_factory=dict)


def _read(path, digest=None):
    body = Path(path).read_bytes()
    if digest is not None and hashlib.sha256(body).hexdigest() != digest:
        raise ValueError('research_artifact_changed')
    return body


def _public_key(value):
    if isinstance(value, str) and value.startswith('sb_publishable_'):
        return value
    try:
        payload = value.split('.')[1]
        if json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))['role'] == 'anon':
            return value
    except (AttributeError, ValueError, KeyError, IndexError, TypeError):
        pass
    raise ValueError('public_runtime_key_required')


def _package(config):
    pin = json.loads(_read(config.pin_path, config.pin_sha256))
    if (pin.get('schema_version') != 'bintanong-research-runtime-pin-v1'
            or pin.get('release_id') != RELEASE or pin.get('research_only') is not True
            or pin.get('institutional_activation_allowed') is not False):
        raise ValueError('current_research_pin_required')
    root = Path(pin['package'])
    seal = json.loads(_read(root / 'runtime-seal.json', config.seal_sha256))
    if set(seal) != set(FILES):
        raise ValueError('research_seal_members_differ')
    raw = {name: _read(root / name, seal[name]) for name in FILES}
    records = [json.loads(line) for line in raw['draft-embedding-records.jsonl'].splitlines() if line]
    vectors = {record['chunk_id']: record['vector'] for record in records}
    package = {key: json.loads(raw[name]) for key, name in (
        ('chunks', FILES[0]), ('versions', FILES[1]), ('manifest', FILES[2]),
        ('catalogue', FILES[3]), ('register', FILES[4]), ('subject_context_budgets', FILES[6]))}
    package['vectors'] = vectors
    if (len(package['chunks']) != 78 or len(records) != len(vectors) or
            set(vectors) != {chunk['chunk_id'] for chunk in package['chunks']}
            or package['manifest']['embedding_set_id'] != pin.get('embedding_set_id')):
        raise ValueError('current_research_package_required')
    return pin, package


class ResearchProvider:
    def __init__(self, client, resources, package, ledgers):
        self.client, self.resources, self.package = client, resources, package
        self.digests = {key: ledger['content_sha256'] for key, ledger in ledgers.items()}
        self.worker = _BoundedWorker()

    async def pin(self):
        def check():
            try:
                HostedReleaseStorage(self.client, pin_release_id=self.resources.pin.release_id,
                    hosted_release_id=RELEASE, authorization_ref=AUTHORIZATION, chunks=self.package['chunks'])
                links = self.client.select('release_curriculum_ledgers', role='runtime',
                                          filters={'release_id': 'eq.' + RELEASE})
                if (len(links) != len(self.digests) or
                        {row['curriculum_id']: row['ledger_sha256'] for row in links} != self.digests):
                    raise ValueError('curriculum_release_differs')
            except Exception:
                raise ReleaseUnavailable('research_release_unavailable') from None
            return self.resources
        return await self.worker.run(check)


def load_research_app(path=None):
    """Uvicorn factory; requires explicit configuration and public runtime credentials."""
    path = path or os.environ.get('BINTANONG_RESEARCH_CONFIG')
    if not path:
        raise ValueError('research_configuration_required')
    config = ResearchApiConfig.model_validate_json(_read(path))
    pin, package = _package(config)
    url, key = os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_ANON_KEY')
    if not url or not key:
        raise ValueError('research_credentials_required')
    auth = SupabaseAuth(url, _public_key(key))
    model_url = urlsplit(config.model_url)
    if (model_url.scheme not in ('http', 'https') or not model_url.hostname or model_url.username
            or model_url.password or model_url.query or model_url.fragment or model_url.path not in ('', '/')):
        raise ValueError('invalid_model_url')
    client = SupabaseStorageClient(StorageConfig(api_url=url, anon_key=key, service_role_key='', db_url=''))
    try:
        ledgers = load_release_curricula(client, release_id=RELEASE, authorization_ref=AUTHORIZATION)
        if not ledgers:
            raise ValueError('reviewed_curricula_required')
        assets = json.loads(_read(config.encoder_assets_path))['verified_assets']
        encoder = QueryEncoder(model_path=str(config.encoder_model_path), asset_digests=assets)
        resources = build_multi_research_resources(ledgers, package, encoder=encoder,
            authorization_ref=AUTHORIZATION, hosted={'client': client, 'release_id': RELEASE},
            program_names=config.program_names, curriculum_names=config.curriculum_names)
        provider = ResearchProvider(client, resources, package, ledgers)
        pipeline = ResearchPipeline(lambda: LlamaTransport(config.model_url, prefix_cache=True), provider,
            generator_factory=lambda model: Generator(model,
                reference_profile=pin.get('generation_reference_profile', 'canonical')))
        curricula = tuple(CurriculumOption(ledger['scope']['program_id'], curriculum,
            next(iter(config.program_names.get(ledger['scope']['program_id'], ())), ledger['sources'][0]['filename']),
            next(iter(config.curriculum_names.get(curriculum, ())), ledger['sources'][0]['filename']))
            for curriculum, ledger in sorted(ledgers.items()))
        async def close():
            await asyncio.to_thread(client.close)
        async def ready():
            await provider.pin()
            await asyncio.to_thread(encoder.load_model)
            model_ok, _ = await probe_http_service(config.model_url, '/health')
            janus_ok, _ = probe_janus()
            return model_ok and janus_ok
        services = ApiServices(sessions=SessionStore(), curricula=curricula, pipeline=pipeline,
            course_labels=dict(resources.course_labels), auth=auth, close=close, ready=ready,
            extract_rows=lambda raw, program, curriculum: extract_isolated(raw, resources.catalog,
                program_id=program, curriculum_id=curriculum))
        return create_app(services, ApiSettings(allowed_origins=config.allowed_origins, require_auth=True))
    except BaseException:
        client.close()
        raise
