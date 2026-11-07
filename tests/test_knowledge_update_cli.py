import importlib
import json

from backend.bintanong_tools.knowledge_update.__main__ import main
from test_knowledge_update_verify import package
from test_knowledge_update_build import reviewed


def test_verify_command_exposes_candidate_verification_without_database(package, capsys):
    assert main(['verify', str(package)]) == 0
    assert json.loads(capsys.readouterr().out)['verified'] is True


def test_reviewer_child_does_not_inherit_hosted_credentials(monkeypatch):
    monkeypatch.setenv('SUPABASE_URL', 'https://must-not-be-used.example')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'must-not-be-used')
    monkeypatch.setenv('NEXT_PUBLIC_SUPABASE_URL', 'https://must-not-be-used.example')
    monkeypatch.setenv('NODE_OPTIONS', '--require=untrusted-module')
    module = importlib.import_module('backend.bintanong_tools.knowledge_update.serve')
    env = module.frontend_environment('http://127.0.0.1:8765')
    assert not any('SUPABASE' in name for name in env)
    assert 'NODE_OPTIONS' not in env
    assert env['NEXT_TELEMETRY_DISABLED'] == '1'
    assert env['BINTANONG_REVIEW_API_ORIGIN'] == 'http://127.0.0.1:8765'
