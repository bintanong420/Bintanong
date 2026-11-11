"""GUI intake step 4: one review tool, any finished upload opened into it; synthetic packets only."""
import importlib

import pytest
from fastapi.testclient import TestClient

from backend.bintanong_tools.knowledge_update.files import write_json
from backend.bintanong_tools.knowledge_update.prepare import prepare
from backend.bintanong_tools.knowledge_update.review import ReviewSession
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
from test_knowledge_update_intake import ORIGIN, PDF, TOKEN
from test_policy_chunks import item, raw_document
from test_prospectus_ingestion import synthetic_converter

GOOD = {'x-review-token': TOKEN, 'origin': ORIGIN}


def intake():
    return importlib.import_module('backend.bintanong_tools.knowledge_update.intake')


def finished(workspace, monkeypatch, text='Submit the form.'):
    upload_id = intake().create_upload(workspace, PDF, kind='handbook', title='Synthetic code', edition='2026')['upload_id']
    folder = workspace / upload_id
    prepare(folder / 'manifest.json', folder / 'packet', converter=synthetic_converter(
        monkeypatch, InputSnapshot(folder / 'original/source.pdf'), raw_document([item(text)], pages=1)))
    write_json(folder / 'job.json', {'state': 'done', 'assist': False, 'exit_code': 0})
    return upload_id


@pytest.fixture
def slot(tmp_path):
    value = intake().SessionSlot(tmp_path, 'Synthetic researcher')
    yield value
    value.close()


def test_nothing_is_open_until_an_upload_is_chosen(slot):
    assert slot.upload_id is None
    with pytest.raises(ValueError, match='Open an upload'):
        slot.state()
    with pytest.raises(ValueError, match='Open an upload'):
        slot.root


def test_opening_a_finished_upload_serves_its_packet(slot, tmp_path, monkeypatch):
    upload_id = finished(tmp_path, monkeypatch)
    slot.open(upload_id)
    assert slot.upload_id == upload_id and slot.root == (tmp_path / upload_id / 'packet').resolve()
    assert slot.state()['items'][0]['fields'][0]['original_value'] == 'Submit the form.'
    assert slot.reviewer == 'Synthetic researcher'


def test_switching_releases_the_previous_review_lock(slot, tmp_path, monkeypatch):
    first, second = finished(tmp_path, monkeypatch), finished(tmp_path, monkeypatch, 'Second rule.')
    slot.open(first)
    slot.open(second)
    assert slot.state()['items'][0]['fields'][0]['original_value'] == 'Second rule.'
    with ReviewSession(tmp_path / first / 'packet', 'Another researcher'):
        pass  # would raise if the first packet were still locked


@pytest.mark.parametrize('state', ['running', 'failed', 'interrupted'])
def test_only_finished_uploads_open(slot, tmp_path, monkeypatch, state):
    upload_id = finished(tmp_path, monkeypatch)
    write_json(tmp_path / upload_id / 'job.json', {'state': state, 'assist': False})
    with pytest.raises(ValueError, match='finished'):
        slot.open(upload_id)
    assert slot.upload_id is None


def test_a_failed_open_keeps_the_current_packet(slot, tmp_path, monkeypatch):
    good = finished(tmp_path, monkeypatch)
    slot.open(good)
    with pytest.raises(ValueError):
        slot.open('0' * 16)
    assert slot.upload_id == good and slot.state()['items']


def test_open_route_then_review_routes_work(tmp_path, monkeypatch):
    upload_id = finished(tmp_path, monkeypatch)
    app = importlib.import_module('backend.bintanong_tools.knowledge_update.app')
    slot = intake().SessionSlot(tmp_path, 'Synthetic researcher')
    try:
        web = TestClient(app.create_app(slot, TOKEN, port=8765, ui_origin=ORIGIN, workspace=tmp_path),
                         base_url='http://127.0.0.1:8765')
        assert web.get('/api/state', headers=GOOD).status_code == 422
        assert web.get('/api/intake/current', headers=GOOD).json() == {'upload_id': None}
        assert web.post('/api/intake/open', json={'upload_id': upload_id}, headers={'origin': ORIGIN}).status_code == 403
        opened = web.post('/api/intake/open', json={'upload_id': upload_id}, headers=GOOD)
        assert opened.status_code == 200, opened.text
        assert web.get('/api/state', headers=GOOD).json()['packet_id'] == opened.json()['packet_id']
        assert web.get('/api/intake/current', headers=GOOD).json() == {'upload_id': upload_id}
        assert web.post('/api/intake/open', json={'upload_id': upload_id, 'x': 1}, headers=GOOD).status_code == 422
    finally:
        slot.close()


def test_intake_command_is_registered():
    cli = importlib.import_module('backend.bintanong_tools.knowledge_update.__main__')
    with pytest.raises(SystemExit) as stop:
        cli.main(['intake', '--help'])
    assert stop.value.code == 0


def test_reopening_the_current_upload_is_harmless(slot, tmp_path, monkeypatch):
    upload_id = finished(tmp_path, monkeypatch)
    slot.open(upload_id)
    assert slot.open(upload_id)['items'] and slot.upload_id == upload_id


def test_a_locked_packet_cannot_replace_the_current_one(slot, tmp_path, monkeypatch):
    good, busy = finished(tmp_path, monkeypatch), finished(tmp_path, monkeypatch, 'Busy rule.')
    slot.open(good)
    with ReviewSession(tmp_path / busy / 'packet', 'Another researcher'):
        with pytest.raises(ValueError):
            slot.open(busy)
    assert slot.upload_id == good and slot.state()['items'][0]['fields'][0]['original_value'] == 'Submit the form.'
    with pytest.raises(ValueError):  # still ours: another reviewer cannot take the current packet's lock
        ReviewSession(tmp_path / good / 'packet', 'Another researcher')


def test_probing_an_empty_slot_behaves_like_a_missing_attribute(slot):
    import copy
    assert not hasattr(slot, '_private_probe')
    assert copy.copy(slot).upload_id is None


def test_open_routes_are_absent_for_a_single_packet_tool(tmp_path, monkeypatch):
    upload_id = finished(tmp_path, monkeypatch)
    app = importlib.import_module('backend.bintanong_tools.knowledge_update.app')
    with ReviewSession(tmp_path / upload_id / 'packet', 'Synthetic researcher') as review:
        web = TestClient(app.create_app(review, TOKEN, port=8765, ui_origin=ORIGIN, workspace=tmp_path),
                         base_url='http://127.0.0.1:8765')
        assert web.post('/api/intake/open', json={'upload_id': upload_id}, headers=GOOD).status_code == 404
        assert web.get('/api/intake/current', headers=GOOD).status_code == 404