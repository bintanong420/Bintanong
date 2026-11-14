import importlib
import json

import pytest

from backend.bintanong_tools.knowledge_update.__main__ import main
from test_knowledge_update_verify import package
from test_knowledge_update_build import reviewed
from test_knowledge_update_draft_checks import QueryEncoder, cases, row


@pytest.mark.parametrize('hit, expected_exit', [(True, 0), (False, 2)])
def test_check_draft_writes_bound_report_and_fails_on_retrieval_miss(package, tmp_path, monkeypatch, capsys,
                                                                  hit, expected_exit):
    from backend.bintanong_tools.knowledge_update import build, draft_checks

    monkeypatch.setattr(build, 'LocalEncoder', lambda path: QueryEncoder())
    if not hit:
        monkeypatch.setattr(draft_checks, '_retrieve', lambda *args: [])
    out = tmp_path / 'checks.json'
    assert main(['check-draft', str(package), '--cases', str(cases(tmp_path, [row()])),
                 '--out', str(out), '--model-dir', str(tmp_path / 'model')]) == expected_exit
    report = json.loads(capsys.readouterr().out)
    assert report == json.loads(out.read_text(encoding='utf-8'))
    assert report['passed'] is hit
    assert report['cases'][0]['passed'] is hit
    assert report['package_binding']['package_id'] == report['package_id']
    assert 'retrieval only' in report['scope']


def test_check_draft_refuses_invalid_cases_without_writing_report(package, tmp_path, monkeypatch, capsys):
    from backend.bintanong_tools.knowledge_update import build

    monkeypatch.setattr(build, 'LocalEncoder', lambda path: QueryEncoder())
    out = tmp_path / 'checks.json'
    assert main(['check-draft', str(package), '--cases', str(cases(tmp_path, [row(expected=('unknown',))])),
                 '--out', str(out), '--model-dir', str(tmp_path / 'model')]) == 1
    captured = capsys.readouterr()
    assert 'unknown expected reading id' in captured.err
    assert not captured.out and not out.exists()


def test_check_draft_requires_explicit_model_directory(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        main(['check-draft', 'package', '--cases', 'cases.json', '--out', str(tmp_path / 'report.json')])
    assert exc.value.code == 2
    assert '--model-dir' in capsys.readouterr().err
    assert not (tmp_path / 'report.json').exists()


def test_check_draft_refuses_missing_local_model_instead_of_using_mock_vectors(tmp_path, capsys):
    out = tmp_path / 'report.json'
    assert main(['check-draft', 'package', '--cases', 'cases.json', '--out', str(out),
                 '--model-dir', str(tmp_path / 'missing-model')]) == 1
    captured = capsys.readouterr()
    assert 'explicit existing workspace embedding model required' in captured.err
    assert not captured.out and not out.exists()


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


def test_review_command_defaults_to_the_fixed_researcher_address(monkeypatch):
    module = importlib.import_module('backend.bintanong_tools.knowledge_update.serve')
    seen = {}
    monkeypatch.setattr(module, 'serve', lambda packet, reviewer, **options: seen.update(options))
    assert main(['review', 'packet', '--reviewer', 'Researcher', '--no-open']) == 0
    assert seen == {'api_port': 8765, 'ui_port': 3050, 'open_browser': False}


def test_launch_link_trades_the_token_for_the_clean_review_address():
    module = importlib.import_module('backend.bintanong_tools.knowledge_update.serve')
    assert module.launch_link('http://127.0.0.1:3050', 'abc-DEF_123') == 'http://127.0.0.1:3050/review/launch?token=abc-DEF_123'
    env = module.frontend_environment('http://127.0.0.1:8765', ui_origin='http://127.0.0.1:3050', token='t' * 32)
    assert env['BINTANONG_REVIEW_UI_ORIGIN'] == 'http://127.0.0.1:3050'
    assert env['BINTANONG_REVIEW_TOKEN'] == 't' * 32
