"""On-demand audit is source-bound advice; it never saves a human decision."""
import copy

import pytest
from fastapi.testclient import TestClient

from backend.bintanong_tools.knowledge_update.app import create_app
from test_ingestion_assistance import FakeProvider
from test_knowledge_update_review import packet, session  # noqa: F401
from test_knowledge_update_review_api import TOKEN, ORIGIN, headers


def command(value, **extra):
    return {'packet_id': value['packet_id'], 'revision': 0, 'item_id': value['items'][0]['id'], 'field': 'body', **extra}


def test_review_audit_checks_one_field_without_saving_or_changing_the_packet(packet, monkeypatch):
    root, value = packet
    provider = FakeProvider({'outcome': 'proposal', 'proposed_value': 'Keep the original form.', 'rationale': 'Check the printed words.'})
    provider.url = 'http://127.0.0.1:18089/v1'
    monkeypatch.setattr('backend.bintanong_tools.knowledge_update.vision.VisionProvider.from_environment', lambda: provider)
    # Source rendering is separately tested; this seam verifies which source/pages are sent, without a model.
    import backend.bintanong_tools.knowledge_update.app as module
    class Renderer:
        def __init__(self, path):
            assert path == root / value['documents'][0]['source']
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def size(self, page): return (612, 792)
        def png(self, page, scale):
            assert page == 1
            return b'original physical page'
    monkeypatch.setattr(module, 'PageRenderer', Renderer)
    original = (root / 'packet.json').read_bytes()
    with session(root) as review, TestClient(create_app(review, TOKEN, port=8765, ui_origin=ORIGIN), base_url='http://127.0.0.1:8765') as web:
        before = copy.deepcopy(review.state())
        response = web.post('/api/audit', json=command(value), headers=headers())
        assert response.status_code == 200, response.text
        result = response.json()
        assert result['packet_id'] == value['packet_id'] and result['revision'] == 0
        assert result['field']['assistance']['outcome'] == 'proposal'
        assert result['field']['decision'] == 'pending'
        assert len(provider.calls) == 1
        assert provider.calls[0]['images'] == [{'page': 1, 'png': b'original physical page'}]
        assert review.state() == before
        assert not review.path.exists()
    assert (root / 'packet.json').read_bytes() == original


@pytest.mark.parametrize('changed', [{'packet_id': 'wrong'}, {'revision': 1}, {'revision': True},
                                    {'item_id': 'missing'}, {'field': 'not-a-field'}, {'approve': True}])
def test_review_audit_refuses_stale_or_manipulated_identity_before_inference(packet, changed, monkeypatch):
    root, value = packet
    provider = FakeProvider()
    monkeypatch.setattr('backend.bintanong_tools.knowledge_update.vision.VisionProvider.from_environment', lambda: provider)
    with session(root) as review, TestClient(create_app(review, TOKEN, port=8765, ui_origin=ORIGIN), base_url='http://127.0.0.1:8765') as web:
        response = web.post('/api/audit', json=command(value, **changed), headers=headers())
        assert response.status_code in (409, 422), response.text
    assert not provider.calls


def test_review_audit_requires_token_and_reports_missing_configuration(packet, monkeypatch):
    root, value = packet
    monkeypatch.delenv('BINTANONG_ASSIST_URL', raising=False)
    monkeypatch.delenv('BINTANONG_ASSIST_MODEL', raising=False)
    with session(root) as review, TestClient(create_app(review, TOKEN, port=8765, ui_origin=ORIGIN), base_url='http://127.0.0.1:8765') as web:
        assert web.post('/api/audit', json=command(value)).status_code == 403
        missing = web.post('/api/audit', json=command(value), headers=headers())
        assert missing.status_code == 503
        assert 'Gemma' in missing.json()['error']
