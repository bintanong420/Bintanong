"""GUI intake build step and packet preview: fake build process, synthetic packets, no database."""
import importlib
import json
import sys

import pytest
from fastapi.testclient import TestClient

from backend.bintanong_tools.knowledge_update.files import write_json
from test_knowledge_update_intake import ORIGIN, PDF, TOKEN
from test_knowledge_update_intake_open import finished

GOOD = {'x-review-token': TOKEN, 'origin': ORIGIN}


def intake():
    return importlib.import_module('backend.bintanong_tools.knowledge_update.intake')


class FakeProcess:
    def __init__(self, argv, **kwargs):
        self.argv, self.kwargs, self.code = argv, kwargs, None
        kwargs['stdout'].write(b'building\n')
        FakeProcess.last = self

    def poll(self):
        return self.code


@pytest.fixture
def prepared(tmp_path):
    upload_id = intake().create_upload(tmp_path, PDF, kind='handbook', title='Synthetic code', edition='2026')['upload_id']
    folder = tmp_path / upload_id
    write_json(folder / 'job.json', {'state': 'done', 'assist': False, 'exit_code': 0})
    write_json(folder / 'packet/review/build-metadata.json', {'packet_id': 'x', 'revision': 1, 'build': {}})
    model = tmp_path / 'model'
    model.mkdir()
    yield tmp_path, upload_id, model
    intake()._jobs.clear()


def start(workspace, upload_id, model, **extra):
    return intake().start_build(workspace, upload_id, python=sys.executable, model_dir=model, runner=FakeProcess, **extra)


def fake_package(folder):
    write_json(folder / 'package/package.json', {'package_id': 'a' * 64})
    (folder / 'package/chunks.jsonl').write_text('{"chunk_id": "1"}\n{"chunk_id": "2"}\n', encoding='utf-8')


def test_build_runs_the_existing_command_and_reports_the_package(prepared):
    workspace, upload_id, model = prepared
    folder = workspace / upload_id
    assert intake().build_status(workspace, upload_id)['state'] == 'not_started'
    assert start(workspace, upload_id, model)['state'] == 'running'
    assert FakeProcess.last.argv == [sys.executable, '-m', 'backend.bintanong_tools.knowledge_update', 'build',
        str(folder / 'packet'), '--out', str(folder / 'package'),
        '--metadata', str(folder / 'packet/review/build-metadata.json'), '--model-dir', str(model)]
    assert 'shell' not in FakeProcess.last.kwargs
    fake_package(folder)
    FakeProcess.last.code = 0
    status = intake().build_status(workspace, upload_id)
    assert status['state'] == 'done' and status['exit_code'] == 0
    assert status['package'] == {'package_id': 'a' * 64, 'chunk_count': 2}
    assert status['log_tail'] == ['building']


def test_build_refuses_without_model_folder_with_a_next_step(prepared):
    workspace, upload_id, _ = prepared
    with pytest.raises(ValueError) as caught:
        intake().start_build(workspace, upload_id, python=sys.executable, model_dir=None, runner=FakeProcess)
    assert caught.value.code == 'model_dir_missing'
    assert str(caught.value) == 'No model folder was given when the tool started. Restart it with --model-dir <path>.'


def test_build_needs_finished_prepare_and_saved_metadata(prepared):
    workspace, upload_id, model = prepared
    folder = workspace / upload_id
    (folder / 'packet/review/build-metadata.json').unlink()
    with pytest.raises(ValueError) as caught:
        start(workspace, upload_id, model)
    assert caught.value.code == 'metadata_missing'
    write_json(folder / 'job.json', {'state': 'failed', 'assist': False, 'exit_code': 1})
    with pytest.raises(ValueError) as caught:
        start(workspace, upload_id, model)
    assert caught.value.code == 'not_prepared'


def test_one_build_at_a_time_and_retry_only_without_a_package(prepared):
    workspace, upload_id, model = prepared
    folder = workspace / upload_id
    start(workspace, upload_id, model)
    with pytest.raises(ValueError) as caught:
        start(workspace, upload_id, model)
    assert caught.value.code == 'build_running'
    FakeProcess.last.code = 1
    failed = intake().build_status(workspace, upload_id)
    assert failed['state'] == 'failed' and 'exit code 1' in failed['error']
    assert start(workspace, upload_id, model)['state'] == 'running'  # failed, no package: retry allowed
    FakeProcess.last.code = 1
    intake().build_status(workspace, upload_id)
    (folder / 'package').mkdir()  # a partial package from the failed run
    with pytest.raises(ValueError) as caught:
        start(workspace, upload_id, model)
    assert caught.value.code == 'package_exists'


def test_a_restarted_server_reports_the_build_as_interrupted(prepared):
    workspace, upload_id, model = prepared
    start(workspace, upload_id, model)
    intake()._jobs.clear()
    status = intake().build_status(workspace, upload_id)
    assert status['state'] == 'interrupted' and 'restarted' in status['error']
    saved = json.loads((workspace / upload_id / 'build-job.json').read_text(encoding='utf-8'))
    assert saved['state'] == 'interrupted'


def test_clean_exit_with_unreadable_package_is_a_failure(prepared):
    workspace, upload_id, model = prepared
    start(workspace, upload_id, model)
    FakeProcess.last.code = 0
    status = intake().build_status(workspace, upload_id)
    assert status['state'] == 'failed' and 'unreadable' in status['error']


def web(workspace, model=None):
    app = importlib.import_module('backend.bintanong_tools.knowledge_update.app')
    slot = intake().SessionSlot(workspace, 'Synthetic researcher')
    return TestClient(app.create_app(slot, TOKEN, port=8765, ui_origin=ORIGIN, workspace=workspace,
                                     prepare_python=sys.executable, model_dir=model), base_url='http://127.0.0.1:8765')


def test_build_routes_need_the_token_and_return_codes(prepared, monkeypatch):
    workspace, upload_id, model = prepared
    client = web(workspace)
    assert client.post('/api/intake/build', json={'upload_id': upload_id}, headers={'origin': ORIGIN}).status_code == 403
    refused = client.post('/api/intake/build', json={'upload_id': upload_id}, headers=GOOD)
    assert refused.status_code == 422 and refused.json()['code'] == 'model_dir_missing'
    assert client.post('/api/intake/build', json={'upload_id': upload_id, 'x': 1}, headers=GOOD).json()['code'] == 'bad_request'
    monkeypatch.setitem(intake().start_build.__kwdefaults__, 'runner', FakeProcess)
    client = web(workspace, model)
    assert client.post('/api/intake/build', json={'upload_id': upload_id}, headers=GOOD).json()['state'] == 'running'
    assert client.get(f'/api/intake/build/{upload_id}', headers=GOOD).json()['state'] == 'running'


def test_packet_items_preview_without_opening_or_locking(tmp_path, monkeypatch):
    upload_id = finished(tmp_path, monkeypatch, 'Submit the form.')
    client = web(tmp_path)
    assert client.get(f'/api/intake/packet/{upload_id}/items', headers={'origin': ORIGIN}).status_code == 403
    body = client.get(f'/api/intake/packet/{upload_id}/items', headers=GOOD).json()
    field = body['items'][0]['fields'][0]
    assert field['name'] == 'body' and field['original_value'] == 'Submit the form.'
    assert field['locator'] == {'physical_pages': [1]}
    assert body['items'][0]['document_id'] == upload_id and body['documents'][0]['sha256']
    from backend.bintanong_tools.knowledge_update.review import ReviewSession
    with ReviewSession(tmp_path / upload_id / 'packet', 'Another researcher'):
        pass  # no lock was left behind
    write_json(tmp_path / upload_id / 'job.json', {'state': 'running', 'assist': False})
    pending = client.get(f'/api/intake/packet/{upload_id}/items', headers=GOOD)
    assert pending.status_code == 422 and pending.json()['code'] == 'not_prepared'
