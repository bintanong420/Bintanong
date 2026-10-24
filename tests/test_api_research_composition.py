import json
import base64
import pytest
from backend.bintanong_api.app import ApiServices, ApiSettings, create_app
from backend.bintanong_private_context.sessions import SessionStore
from fastapi.testclient import TestClient

def test_composition_requires_explicit_configuration(monkeypatch):
    from backend.bintanong_api.research import load_research_app
    monkeypatch.delenv('BINTANONG_RESEARCH_CONFIG', raising=False)
    with pytest.raises(ValueError, match='research_configuration_required'):
        load_research_app()

def test_composition_refuses_missing_auth_without_touching_hosted_data(tmp_path, monkeypatch):
    from backend.bintanong_api.research import load_research_app
    path = tmp_path / 'config.json'
    path.write_text(json.dumps(dict(schema_version='bintanong-student-runtime-v1',
        authorization_ref='research-synthetic', hosted_release_id='synthetic-release',
        document_policy='synthetic-policy.json')))
    monkeypatch.delenv('SUPABASE_URL', raising=False)
    monkeypatch.delenv('SUPABASE_ANON_KEY', raising=False)
    with pytest.raises(ValueError, match='research_credentials_required'):
        load_research_app(path)

def test_runtime_json_is_bounded_and_unknown_options_are_refused(tmp_path):
    from backend.bintanong_api.research import read_config
    path = tmp_path / 'config.json'
    path.write_text('{}' + ' ' * (64 * 1024 * 1024))
    with pytest.raises(ValueError, match='research_artifact_too_large'):
        read_config(path)

def test_app_cleanup_runs_even_without_a_student_request():
    closed = []
    async def close(): closed.append(True)
    app = create_app(ApiServices(sessions=SessionStore(), close=close), ApiSettings(allowed_origins=('https://synthetic.example',)))
    with TestClient(app): pass
    assert closed == [True]

def test_research_composition_refuses_privileged_credentials():
    from backend.bintanong_api.research import public_key
    def token(role):
        return 'header.' + base64.urlsafe_b64encode(json.dumps({'role': role}).encode()).decode().rstrip('=') + '.signature'
    assert public_key(token('anon')) == token('anon')
    assert public_key('sb_publishable_synthetic') == 'sb_publishable_synthetic'
    for value in ('sb_secret_synthetic', token('service_role'), 'malformed'):
        with pytest.raises(ValueError, match='public_runtime_key_required'):
            public_key(value)


@pytest.mark.parametrize('outcome', ['ok', 'release_changed', 'wrong_release', 'exception'])
def test_research_storage_probe_uses_the_pinned_runtime_vector_rpc(outcome):
    import asyncio
    from types import SimpleNamespace
    from unittest.mock import Mock
    from backend.bintanong_api.research import ResearchProvider
    from backend.bintanong_embedding.adapter import EmbeddingConfig
    from backend.bintanong_retrieval.query import configuration_identity, validate_vector

    config = EmbeddingConfig()
    storage = Mock()
    storage.rpc.return_value = dict(status='release_changed' if outcome == 'release_changed' else 'ok',
                                   release_id='other' if outcome == 'wrong_release' else 'synthetic-pin')
    if outcome == 'exception':
        storage.rpc.side_effect = RuntimeError('postgresql://secret@private-host')
    engine = SimpleNamespace(client=storage, encoder=SimpleNamespace(config=config))
    resources = SimpleNamespace(pin=SimpleNamespace(release_id='synthetic-pin'),
                                retrieval=SimpleNamespace(engine=engine),
                                document_scope=('audience:undergraduate',))
    provider = ResearchProvider(None, resources, None, [], {})
    ok, detail = asyncio.run(provider.probe_supabase())
    assert ok is (outcome == 'ok')
    assert detail == (None if ok else 'hosted retrieval unavailable')
    name, params = storage.rpc.call_args.args
    assert name == 'retrieve_context'
    assert storage.rpc.call_args.kwargs == {'role': 'runtime'}
    assert params['p_release_id'] == 'synthetic-pin'
    assert params['p_config'] == configuration_identity(config)
    assert params['p_scope'] == ['audience:undergraduate']
    validate_vector(params['query_embedding'])

