"""GUI intake (owner plan 11 Nov 2026): a researcher upload becomes a checked manifest; synthetic bytes only."""
import hashlib
import importlib
import json

import pytest
from fastapi.testclient import TestClient

from backend.bintanong_tools.knowledge_update.manifest import load_manifest
from test_knowledge_update_review import packet, session  # noqa: F401  (packet is a fixture)

PDF = b'%PDF-1.7 synthetic upload'
TOKEN = 'test-local-review-token'
ORIGIN = 'http://127.0.0.1:3001'


def intake():
    return importlib.import_module('backend.bintanong_tools.knowledge_update.intake')


def meta(**extra):
    return {'kind': 'handbook', 'title': 'Synthetic student code', 'edition': '2026', **extra}


def test_upload_writes_a_manifest_that_load_manifest_accepts(tmp_path):
    result = intake().create_upload(tmp_path, PDF, **meta(office='Synthetic Office', audience='undergraduate students'))
    folder = tmp_path / result['upload_id']
    assert sorted(p.name for p in folder.iterdir()) == ['manifest.json', 'original', 'upload.json']
    assert (folder / 'original/source.pdf').read_bytes() == PDF
    manifest = load_manifest(folder / 'manifest.json')
    doc = manifest['documents'][0]
    assert doc['id'] == result['upload_id'] and doc['kind'] == 'handbook'
    assert doc['sha256'] == hashlib.sha256(PDF).hexdigest() == result['sha256']
    note = json.loads((folder / 'upload.json').read_text(encoding='utf-8'))
    assert note['office'] == 'Synthetic Office' and note['audience_note'] == 'undergraduate students'
    assert note['candidate_only'] is True


def test_upload_ids_come_from_the_server_and_differ(tmp_path):
    first = intake().create_upload(tmp_path, PDF, **meta())['upload_id']
    second = intake().create_upload(tmp_path, PDF, **meta())['upload_id']
    assert first != second and all(c in '0123456789abcdef' for c in first)


@pytest.mark.parametrize('data, error', [(b'not a pdf', 'PDF'), (b'', 'PDF')])
def test_upload_refuses_non_pdf(tmp_path, data, error):
    with pytest.raises(ValueError, match=error):
        intake().create_upload(tmp_path, data, **meta())
    assert list(tmp_path.iterdir()) == []


def test_upload_refuses_oversize(tmp_path, monkeypatch):
    monkeypatch.setattr(intake(), 'MAX_UPLOAD', len(PDF) - 1)
    with pytest.raises(ValueError, match='128 MiB'):
        intake().create_upload(tmp_path, PDF, **meta())


@pytest.mark.parametrize('field, value', [('kind', 'prospectus'), ('kind', 'memo'), ('title', '  '),
                                          ('edition', ''), ('title', 'x' * 301)])
def test_upload_refuses_bad_metadata(tmp_path, field, value):
    with pytest.raises(ValueError):
        intake().create_upload(tmp_path, PDF, **{**meta(), field: value})
    assert list(tmp_path.iterdir()) == []


def test_upload_refuses_a_workspace_inside_git(tmp_path):
    (tmp_path / '.git').mkdir()
    with pytest.raises(ValueError, match='Git'):
        intake().create_upload(tmp_path / 'uploads', PDF, **meta())


def test_list_uploads_reads_back_metadata_only(tmp_path):
    made = intake().create_upload(tmp_path, PDF, **meta())
    (tmp_path / 'stray-folder').mkdir()
    rows = intake().list_uploads(tmp_path)
    assert [r['upload_id'] for r in rows] == [made['upload_id']]
    assert rows[0]['title'] == 'Synthetic student code' and 'source' not in rows[0]


def client(review, workspace):
    module = importlib.import_module('backend.bintanong_tools.knowledge_update.app')
    return TestClient(module.create_app(review, TOKEN, port=8765, ui_origin=ORIGIN, workspace=workspace),
                      base_url='http://127.0.0.1:8765')


def headers(**extra):
    return {'x-review-token': TOKEN, 'origin': ORIGIN, **extra}


def test_upload_route_needs_the_review_token(packet, tmp_path):
    root, _ = packet
    with session(root) as review, client(review, tmp_path / 'uploads') as web:
        response = web.post('/api/intake/upload', params=meta(), content=PDF,
                            headers={'origin': ORIGIN, 'content-type': 'application/pdf'})
        assert response.status_code == 403
        assert not (tmp_path / 'uploads').exists()


def test_upload_route_saves_and_lists(packet, tmp_path):
    root, _ = packet
    with session(root) as review, client(review, tmp_path / 'uploads') as web:
        response = web.post('/api/intake/upload', params=meta(title='Konstitusyon ng USG'), content=PDF,
                            headers=headers(**{'content-type': 'application/pdf'}))
        assert response.status_code == 200, response.text
        listed = web.get('/api/intake/uploads', headers=headers()).json()['uploads']
        assert [r['upload_id'] for r in listed] == [response.json()['upload_id']]
        assert listed[0]['title'] == 'Konstitusyon ng USG'


def test_upload_route_refuses_wrong_type_and_oversize(packet, tmp_path, monkeypatch):
    root, _ = packet
    monkeypatch.setattr(intake(), 'MAX_UPLOAD', len(PDF) - 1)
    with session(root) as review, client(review, tmp_path / 'uploads') as web:
        wrong = web.post('/api/intake/upload', params=meta(), content=PDF,
                         headers=headers(**{'content-type': 'application/json'}))
        big = web.post('/api/intake/upload', params=meta(), content=PDF,
                       headers=headers(**{'content-type': 'application/pdf'}))
        assert (wrong.status_code, big.status_code) == (415, 413)


def test_intake_routes_are_absent_without_a_workspace(packet):
    root, _ = packet
    module = importlib.import_module('backend.bintanong_tools.knowledge_update.app')
    with session(root) as review, TestClient(module.create_app(review, TOKEN, port=8765, ui_origin=ORIGIN),
                                             base_url='http://127.0.0.1:8765') as web:
        assert web.get('/api/intake/uploads', headers=headers()).status_code == 404
