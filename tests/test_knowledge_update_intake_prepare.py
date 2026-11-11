"""GUI intake step 3: run the existing prepare command for one upload in the background; fake process only."""
import importlib
import json
import sys

import pytest

PDF = b'%PDF-1.7 synthetic upload'


def intake():
    return importlib.import_module('backend.bintanong_tools.knowledge_update.intake')


class FakeProcess:
    def __init__(self, argv, **kwargs):
        self.argv, self.kwargs, self.code = argv, kwargs, None
        kwargs['stdout'].write(b'line one\nline two\n')
        FakeProcess.last = self

    def poll(self):
        return self.code


@pytest.fixture
def upload(tmp_path):
    made = intake().create_upload(tmp_path, PDF, kind='handbook', title='Synthetic code', edition='2026')
    yield tmp_path, made['upload_id']
    intake()._jobs.clear()


def start(workspace, upload_id, **extra):
    return intake().start_prepare(workspace, upload_id, python=sys.executable, runner=FakeProcess, **extra)


def test_prepare_runs_the_existing_command_as_an_argument_list(upload):
    workspace, upload_id = upload
    assert start(workspace, upload_id)['state'] == 'running'
    argv, kwargs = FakeProcess.last.argv, FakeProcess.last.kwargs
    folder = workspace / upload_id
    assert argv == [sys.executable, '-m', 'backend.bintanong_tools.knowledge_update', 'prepare',
                    str(folder / 'manifest.json'), '--out', str(folder / 'packet')]
    assert 'shell' not in kwargs and kwargs['cwd'].joinpath('backend').is_dir()
    assert intake().prepare_status(workspace, upload_id)['state'] == 'running'


def test_gemma_audit_adds_flagged_assist_mode_and_needs_its_settings(upload, monkeypatch):
    workspace, upload_id = upload
    monkeypatch.delenv('BINTANONG_ASSIST_URL', raising=False)
    with pytest.raises(ValueError, match='Gemma'):
        start(workspace, upload_id, assist=True)
    monkeypatch.setenv('BINTANONG_ASSIST_URL', 'http://127.0.0.1:18089/v1')
    monkeypatch.setenv('BINTANONG_ASSIST_MODEL', 'synthetic-vision')
    start(workspace, upload_id, assist=True)
    assert FakeProcess.last.argv[-2:] == ['--assist-mode', 'flagged']


def test_status_reports_done_failed_and_the_log_tail(upload):
    workspace, upload_id = upload
    start(workspace, upload_id)
    FakeProcess.last.code = 1
    status = intake().prepare_status(workspace, upload_id)
    assert status['state'] == 'failed' and status['exit_code'] == 1
    assert status['log_tail'][-2:] == ['line one', 'line two']
    saved = json.loads((workspace / upload_id / 'job.json').read_text(encoding='utf-8'))
    assert saved['state'] == 'failed'


def test_done_counts_fields_where_gemma_was_unavailable(upload):
    workspace, upload_id = upload
    start(workspace, upload_id)
    packet = workspace / upload_id / 'packet'
    packet.mkdir()
    failed = {'outcome': 'failed', 'rationale': 'AI assistance unavailable. Review the original manually.'}
    (packet / 'packet.json').write_text(json.dumps({'items': [
        {'fields': [{'assistance': failed}, {'assistance': {'outcome': 'proposal'}}, {}]}]}), encoding='utf-8')
    FakeProcess.last.code = 0
    status = intake().prepare_status(workspace, upload_id)
    assert status['state'] == 'done' and status['gemma_unavailable_fields'] == 1


def test_one_job_per_upload_and_no_rerun_over_an_existing_packet(upload):
    workspace, upload_id = upload
    start(workspace, upload_id)
    with pytest.raises(ValueError, match='already'):
        start(workspace, upload_id)
    FakeProcess.last.code = 0
    (workspace / upload_id / 'packet').mkdir()
    with pytest.raises(ValueError, match='new upload'):
        start(workspace, upload_id)


@pytest.mark.parametrize('upload_id', ['../x', 'ABC', '', 'a' * 17, 'deadbeefdeadbeef'])
def test_unknown_or_malformed_upload_ids_are_refused(upload, upload_id):
    workspace, _ = upload
    with pytest.raises(ValueError):
        start(workspace, upload_id)
    with pytest.raises(ValueError):
        intake().prepare_status(workspace, upload_id)


def test_a_traversal_id_cannot_reach_a_real_upload(upload):
    workspace, upload_id = upload
    for sneaky in (f'../{workspace.name}/{upload_id}', f'{upload_id}/.', f'./{upload_id}'):
        with pytest.raises(ValueError, match='invalid upload id'):
            start(workspace, sneaky)
        with pytest.raises(ValueError, match='invalid upload id'):
            intake().prepare_status(workspace, sneaky)


def test_each_upload_runs_prepare_once_even_after_failure_or_restart(upload):
    workspace, upload_id = upload
    start(workspace, upload_id)
    FakeProcess.last.code = 1
    assert intake().prepare_status(workspace, upload_id)['state'] == 'failed'
    with pytest.raises(ValueError, match='new upload'):
        start(workspace, upload_id)
    intake()._jobs.clear()  # an orphan from a closed server may still be writing packet/
    with pytest.raises(ValueError, match='new upload'):
        start(workspace, upload_id)


def test_gemma_audit_needs_the_model_setting_too(upload, monkeypatch):
    workspace, upload_id = upload
    monkeypatch.setenv('BINTANONG_ASSIST_URL', 'http://127.0.0.1:18089/v1')
    monkeypatch.delenv('BINTANONG_ASSIST_MODEL', raising=False)
    with pytest.raises(ValueError, match='Gemma'):
        start(workspace, upload_id, assist=True)


def test_an_unreadable_packet_after_exit_zero_reads_as_failed(upload):
    workspace, upload_id = upload
    start(workspace, upload_id)
    (workspace / upload_id / 'packet').mkdir()
    (workspace / upload_id / 'packet/packet.json').write_text('{"items": "broken"', encoding='utf-8')
    FakeProcess.last.code = 0
    status = intake().prepare_status(workspace, upload_id)
    assert status['state'] == 'failed' and 'packet' in status['error']


def test_missing_interpreter_is_refused(upload, tmp_path):
    workspace, upload_id = upload
    with pytest.raises(ValueError, match='interpreter'):
        intake().start_prepare(workspace, upload_id, python=str(tmp_path / 'no-python.exe'), runner=FakeProcess)


def test_a_job_left_running_by_a_closed_server_reads_as_interrupted(upload):
    workspace, upload_id = upload
    start(workspace, upload_id)
    intake()._jobs.clear()  # server restarted; the process handle is gone
    assert intake().prepare_status(workspace, upload_id)['state'] == 'interrupted'


def test_prepare_routes_need_the_token_and_a_configured_interpreter(upload, monkeypatch):
    import functools
    from fastapi.testclient import TestClient
    from test_knowledge_update_intake import ORIGIN, TOKEN
    workspace, upload_id = upload
    monkeypatch.setattr(intake(), 'start_prepare', functools.partial(intake().start_prepare, runner=FakeProcess))
    app = importlib.import_module('backend.bintanong_tools.knowledge_update.app')
    good = {'x-review-token': TOKEN, 'origin': ORIGIN}
    body = {'upload_id': upload_id, 'assist': False}
    for python, expected in ((None, 422), (sys.executable, 200)):
        web = TestClient(app.create_app(_Session(), TOKEN, port=8765, ui_origin=ORIGIN, workspace=workspace,
                                        prepare_python=python), base_url='http://127.0.0.1:8765')
        assert web.post('/api/intake/prepare', json=body, headers={'origin': ORIGIN}).status_code == 403
        assert web.post('/api/intake/prepare', json=body, headers=good).status_code == expected
    assert web.post('/api/intake/prepare', json={**body, 'assist': 'yes'}, headers=good).status_code == 422
    assert web.get(f'/api/intake/prepare/{upload_id}', headers=good).json()['state'] == 'running'
    assert web.get('/api/intake/prepare/..%2Fx', headers=good).status_code in (404, 422)


class _Session:
    root, reviewer = None, 'Synthetic researcher'