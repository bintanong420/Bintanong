"""Tracked research app composition uses explicit sealed inputs and never a fictional fallback."""
import hashlib
import asyncio
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient


def save(path, value):
    path.write_text(json.dumps(value), encoding='utf-8')
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def configured(tmp_path, monkeypatch):
    factory = importlib.import_module('backend.bintanong_api.research_app')
    package = tmp_path / 'package'
    package.mkdir()
    entries = {
        'draft-chunks.json': [{'chunk_id': f'chunk-{i}', 'content_hash': str(i)} for i in range(78)],
        'draft-source-versions.json': [], 'draft-subject-catalogue.json': {},
        'draft-source-review-register.json': {},
        'draft-embedding-manifest.json': {'embedding_set_id': 'synthetic-set'},
        'subject-context-budgets.json': {'synthetic-topic': 2048},
    }
    seal = {name: save(package / name, value) for name, value in entries.items()}
    records = package / 'draft-embedding-records.jsonl'
    records.write_text('\n'.join(json.dumps({'chunk_id': f'chunk-{i}', 'vector': [1.0]}) for i in range(78)), encoding='utf-8')
    seal[records.name] = hashlib.sha256(records.read_bytes()).hexdigest()
    seal_sha = save(package / 'runtime-seal.json', seal)
    pin_path = tmp_path / 'pin.json'
    pin_sha = save(pin_path, {'schema_version': 'bintanong-research-runtime-pin-v1',
        'release_id': 'p11-research-corrected-20261026', 'package': str(package),
        'embedding_set_id': 'synthetic-set', 'research_only': True,
        'institutional_activation_allowed': False, 'generation_reference_profile': 'short'})
    assets = tmp_path / 'assets.json'
    save(assets, {'verified_assets': {'synthetic': 'digest'}})
    config_path = tmp_path / 'config.json'
    save(config_path, {'schema_version': 'bintanong-research-api-v1', 'pin_path': str(pin_path),
        'pin_sha256': pin_sha, 'seal_sha256': seal_sha, 'encoder_assets_path': str(assets),
        'encoder_model_path': str(tmp_path / 'model'), 'allowed_origins': ['https://bintanong.example'],
        'program_names': {'program-a': ['Program A']}, 'curriculum_names': {'curriculum-a': ['Curriculum A']}})
    seen = {}
    client = SimpleNamespace(close=lambda: seen.update(closed=True))
    monkeypatch.setattr(factory, 'SupabaseStorageClient', lambda config: client)
    monkeypatch.setattr(factory, 'QueryEncoder', lambda **kw: seen.setdefault('encoder',
        SimpleNamespace(config=kw, load_model=lambda: seen.update(encoder_loaded=True))))
    async def healthy(*args):
        return True, None
    monkeypatch.setattr(factory, 'probe_http_service', healthy)
    monkeypatch.setattr(factory, 'probe_janus', lambda: (True, None))
    monkeypatch.setattr(factory, 'load_release_curricula', lambda *a, **kw: {
        'curriculum-a': {'scope': {'program_id': 'program-a'}, 'content_sha256': 'ledger-digest',
                         'sources': [{'filename': 'Synthetic curriculum'}]}})
    def build(ledgers, payload, **kwargs):
        seen.update(package=payload, build=kwargs)
        return SimpleNamespace(catalog=(), course_labels=(('course-a', 'A 1/L'),),
                               pin=SimpleNamespace(release_id='synthetic-runtime'))
    monkeypatch.setattr(factory, 'build_multi_research_resources', build)
    monkeypatch.setenv('SUPABASE_URL', 'https://synthetic.supabase.co')
    monkeypatch.setenv('SUPABASE_ANON_KEY', 'sb_publishable_synthetic')
    return factory, config_path, seen


def test_missing_config_fails_closed_without_startup(monkeypatch):
    factory = importlib.import_module('backend.bintanong_api.research_app')
    monkeypatch.delenv('BINTANONG_RESEARCH_CONFIG', raising=False)
    with pytest.raises(ValueError, match='research_configuration_required'):
        factory.load_research_app()


def test_factory_reuses_sealed_package_cpu_encoder_and_requires_server_auth(configured):
    factory, path, seen = configured
    app = factory.load_research_app(path)
    assert app.state.settings.require_auth is True
    assert app.state.services.course_labels == {'course-a': 'A 1/L'}
    assert len(seen['package']['chunks']) == len(seen['package']['vectors']) == 78
    assert seen['package']['subject_context_budgets'] == {'synthetic-topic': 2048}
    assert seen['build']['hosted']['release_id'] == 'p11-research-corrected-20261026'
    with TestClient(app) as client:
        assert client.get('/curricula').status_code == 401
        assert client.get('/health/live').status_code == 200
    assert seen['closed'] is True


@pytest.mark.parametrize('target', ['pin', 'seal', 'chunk'])
def test_changed_research_inputs_refuse_startup_before_client_or_model_creation(configured, target):
    factory, path, seen = configured
    config = json.loads(path.read_bytes())
    pin = json.loads(Path(config['pin_path']).read_bytes())
    targets = {'pin': Path(config['pin_path']), 'seal': Path(pin['package']) / 'runtime-seal.json',
               'chunk': Path(pin['package']) / 'draft-chunks.json'}
    targets[target].write_bytes(targets[target].read_bytes() + b' ')
    with pytest.raises(ValueError, match='research_artifact_changed'):
        factory.load_research_app(path)
    assert 'encoder' not in seen and 'build' not in seen


def test_factory_requires_public_runtime_credentials(configured, monkeypatch):
    factory, path, _ = configured
    monkeypatch.setenv('SUPABASE_ANON_KEY', 'service-role-or-secret')
    with pytest.raises(ValueError, match='public_runtime_key_required'):
        factory.load_research_app(path)


@pytest.mark.parametrize('available', [True, False])
def test_configured_readiness_checks_this_research_runtime_without_default_local_stack(configured, monkeypatch, available):
    factory, path, seen = configured
    async def ready(self):
        seen['readiness_checked'] = True
        if not available:
            raise RuntimeError('private upstream detail')
        return self.resources
    monkeypatch.setattr(factory.ResearchProvider, 'pin', ready)
    app = factory.load_research_app(path)
    with TestClient(app) as client:
        response = client.get('/health/ready')
    assert response.status_code == (200 if available else 503)
    assert response.json()['probes'] == {'student_runtime': available}
    assert 'private upstream detail' not in response.text
    assert seen['readiness_checked'] is True


def test_concurrent_first_readiness_and_retrieval_share_one_completed_encoder_load(configured, monkeypatch):
    import threading
    import time
    factory, path, seen = configured
    class ColdEncoder:
        def __init__(self):
            self.model = None
            self.loads = 0
            self.lock = threading.Lock()
        def load_model(self):
            if self.model is None:
                with self.lock:
                    self.loads += 1
                time.sleep(.05)  # release GIL while an actual model constructor would read/load weights
                self.model = object()
            return self.model
        def encode(self, _query):
            return self.load_model()
    encoder = ColdEncoder()
    monkeypatch.setattr(factory, 'QueryEncoder', lambda **kwargs: encoder)
    async def pin(self):
        return self.resources
    monkeypatch.setattr(factory.ResearchProvider, 'pin', pin)
    app = factory.load_research_app(path)
    async def simultaneous_first_calls():
        first, second, retrieval = await asyncio.gather(app.state.services.ready(),
            app.state.services.ready(), asyncio.to_thread(encoder.encode, 'synthetic question'))
        assert first is True and second is True and retrieval is encoder.model
    asyncio.run(simultaneous_first_calls())
    assert encoder.loads == 1
