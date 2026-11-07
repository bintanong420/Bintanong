import copy
import hashlib
import json

import pypdfium2 as pdfium
import pytest

from backend.bintanong_tools.knowledge_update.prepare import prepare
from backend.bintanong_tools.knowledge_update.review import ReviewSession
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
from test_knowledge_update_prepare import manifest
from test_knowledge_update_review import answer
from test_knowledge_update_review_api import client, headers
from test_policy_chunks import item, raw_document
from test_prospectus_ingestion import synthetic_converter


@pytest.fixture
def feedback_packet(tmp_path, monkeypatch):
    path, source, spec = manifest(tmp_path)
    with pdfium.PdfDocument.new() as pdf:
        for _ in range(2):
            page = pdf.new_page(600, 800)
            page.close()
        pdf.save(source)
    spec['documents'][0]['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    path.write_text(json.dumps(spec), encoding='utf-8')
    root = tmp_path / 'packet'
    value = prepare(path, root, converter=synthetic_converter(monkeypatch, InputSnapshot(source),
        raw_document([item('A captured instruction.')], pages=2)))
    return root, value


def omission(revision=0, operation='report-1'):
    return {'kind': 'omission', 'revision': revision, 'operation_id': operation,
        'document_id': 'handbook', 'page': 2, 'region': [.1, .2, .8, .4],
        'stage': 'not_sure', 'visible_text': 'Synthetic visible table row.',
        'note': 'This row is visible in the source but absent from the review queue.'}


def test_missing_content_can_be_saved_without_an_existing_field_and_never_approves_it(feedback_packet):
    root, packet = feedback_packet
    before = (root / packet['documents'][0]['source']).read_bytes()
    with ReviewSession(root, 'Researcher') as review, client(review) as web:
        response = web.post('/api/decision', headers=headers(), json=omission())
        assert response.status_code == 200, response.text
        receipt = response.json()
        assert receipt['feedback']['status'] == 'pending'
        assert review.state()['items'] == packet['items']
        assert review.state()['feedback'][0]['page'] == 2
        assert review.save(omission()) == receipt
        review.save(answer(packet, revision=1))
    with ReviewSession(root, 'Researcher') as reopened:
        assert reopened.state()['revision'] == 2
        feedback = reopened.state()['feedback'][0]
        assert feedback['source_sha256'] == packet['documents'][0]['sha256']
        assert feedback['region'] == [.1, .2, .8, .4]
        assert feedback['status'] == 'pending'
        exported = reopened.export()
        assert exported['feedback'] == [feedback]
        assert len(exported['readings']) == 2
        assert exported['readings'][0]['fields'][0]['original_value'] == 'A captured instruction.'
        assert exported['readings'][1]['fields'][0]['decision'] == 'pending'
        assert exported['readings'][1]['fields'][0]['original_value'] == ''
        assert len(reopened.history()) == 2
    assert (root / packet['documents'][0]['source']).read_bytes() == before


@pytest.mark.parametrize('patch', [
    {'page': 0}, {'page': 3}, {'page': True}, {'document_id': 'not-in-packet'},
    {'region': [0, 0, 2, 1]}, {'region': [.8, .2, .1, .4]}, {'region': [True, 0, 1, 1]},
    {'region': [0, 0, 1]}, {'stage': 'approved'}, {'note': ''}, {'visible_text': ' '},
    {'status': 'approved'}, {'source_sha256': '0' * 64},
])
def test_invalid_or_promoting_feedback_is_refused_without_a_journal_entry(feedback_packet, patch):
    root, _ = feedback_packet
    command = {**omission(), **patch}
    with ReviewSession(root, 'Researcher') as review, client(review) as web:
        result = web.post('/api/decision', headers=headers(), json=command)
        assert result.status_code == 422, result.text
        assert review.history() == []


def test_feedback_retries_refuse_stale_edits_and_changed_operations(feedback_packet):
    root, packet = feedback_packet
    with ReviewSession(root, 'Researcher') as review:
        review.save(omission())
        with pytest.raises(ValueError, match='operation'):
            review.save({**omission(), 'note': 'Changed after retry.'})
        with pytest.raises(ValueError, match='stale'):
            review.save(omission(operation='report-2'))
        review.save({**omission(revision=1, operation='report-2'), 'region': None})
        assert len(review.state()['feedback']) == 2
        assert review.state()['items'] == packet['items']


def test_changed_pdf_stops_feedback_and_keeps_original_journal(feedback_packet):
    root, packet = feedback_packet
    with ReviewSession(root, 'Researcher') as review:
        review.save(omission())
        before = review.path.read_bytes()
        (root / packet['documents'][0]['source']).write_bytes(b'%PDF-altered')
        with pytest.raises(ValueError, match='digest|identity'):
            review.save(omission(revision=1, operation='report-2'))
        assert review.path.read_bytes() == before
