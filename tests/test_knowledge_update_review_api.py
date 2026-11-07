import importlib
import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from test_knowledge_update_review import answer, packet, session
from test_knowledge_update_prepare import manifest
from test_prospectus_ingestion import synthetic_converter
from backend.bintanong_tools.knowledge_update.prepare import prepare
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot

TOKEN = 'test-local-review-token'
ORIGIN = 'http://127.0.0.1:3001'


def client(review):
    module = importlib.import_module('backend.bintanong_tools.knowledge_update.app')
    return TestClient(module.create_app(review, TOKEN, port=8765, ui_origin=ORIGIN),
                      base_url='http://127.0.0.1:8765')


def headers(**extra):
    return {'x-review-token': TOKEN, 'origin': ORIGIN, **extra}


def test_review_api_requires_token_for_read_and_write(packet):
    root, value = packet
    with session(root) as review, client(review) as web:
        assert web.get('/api/state').status_code == 403
        assert web.post('/api/decision', json=answer(value)).status_code == 403
        response = web.get('/api/state', headers=headers())
        assert response.status_code == 200
        assert response.json()['packet_id'] == value['packet_id']
        assert response.headers['cache-control'] == 'no-store'


@pytest.mark.parametrize('attack', ['host', 'origin', 'token'])
def test_review_api_refuses_foreign_requests(packet, attack):
    root, _ = packet
    h = headers()
    h[{'host': 'host', 'origin': 'origin', 'token': 'x-review-token'}[attack]] = {
        'host': 'attacker.example', 'origin': 'https://attacker.example', 'token': 'wrong'}[attack]
    with session(root) as review, client(review) as web:
        assert web.get('/api/state', headers=h).status_code == 403


def test_review_api_save_export_and_stale_conflict(packet):
    root, value = packet
    with session(root) as review, client(review) as web:
        first = web.post('/api/decision', headers=headers(), json=answer(value))
        assert first.status_code == 200
        stale = answer(value, operation='other')
        assert web.post('/api/decision', headers=headers(), json=stale).status_code == 409
        exported = web.post('/api/export', headers=headers()).json()
        assert exported['candidate_only'] is True
        assert exported['readings'][0]['fields'][0]['decision'] == 'accepted'
        assert web.get('/api/history', headers=headers()).json()[0]['reviewer'] == 'Researcher'


def test_review_api_has_no_publication_route_and_bounds_input(packet):
    root, _ = packet
    with session(root) as review, client(review) as web:
        assert web.post('/api/publish', headers=headers()).status_code == 404
        assert web.post('/api/decision', headers=headers(), content='not json').status_code == 415
        assert web.post('/api/decision', headers=headers(**{'content-type': 'application/json'}),
                        content='x' * (1024 * 1024 + 1)).status_code == 413
        assert web.post('/api/decision', headers=headers(), json={'revision': 0}).status_code == 422


def test_review_api_serves_only_packet_source_identities(packet):
    root, value = packet
    with session(root) as review, client(review) as web:
        response = web.get('/api/source/handbook', headers=headers())
        assert response.status_code == 200
        assert response.content == (root / value['documents'][0]['source']).read_bytes()
        assert web.get('/api/source/unknown', headers=headers()).status_code == 404


def test_review_api_preflight_only_accepts_declared_local_ui(packet):
    root, _ = packet
    with session(root) as review, client(review) as web:
        valid = web.options('/api/decision', headers={'origin': ORIGIN,
            'access-control-request-method': 'POST', 'access-control-request-headers': 'x-review-token,content-type'})
        assert valid.status_code == 204
        assert valid.headers['access-control-allow-origin'] == ORIGIN
        assert web.options('/api/decision', headers={'origin': 'https://attacker.example'}).status_code == 403


def test_prospectus_api_reuses_existing_questions_answers_and_candidate_export(tmp_path, monkeypatch):
    import pypdfium2 as pdfium
    path, source, spec = manifest(tmp_path, kind='prospectus')
    with pdfium.PdfDocument.new() as pdf:
        page = pdf.new_page(612, 792)
        page.close()
        pdf.save(source)
    spec['documents'][0]['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    path.write_text(json.dumps(spec), encoding='utf-8')
    root = tmp_path / 'packet'
    prepare(path, root, converter=synthetic_converter(monkeypatch, InputSnapshot(source)))
    with session(root) as review, client(review) as web:
        queue = web.get('/api/prospectus/prospectus/queue', headers=headers())
        assert queue.status_code == 200
        questions = queue.json()['questions']
        assert questions
        question = questions[0]
        view = web.get('/api/prospectus/prospectus/question', params={'qid': question['qid']}, headers=headers())
        assert view.status_code == 200
        assert view.json()['question']['qid'] == question['qid']
        result = web.post('/api/prospectus/prospectus/answer', headers=headers(), json={
            'qid': question['qid'], 'choice': 'yes', 'edits': {}, 'proposals': [],
            'reason': 'Checked the displayed synthetic evidence.', 'note': ''})
        assert result.status_code == 200
        assert result.json()['errors'] == []
        exported = web.post('/api/prospectus/prospectus/export', headers=headers())
        assert exported.status_code == 200
        assert exported.json()['candidate_only'] is True
    assert source.read_bytes().startswith(b'%PDF')
