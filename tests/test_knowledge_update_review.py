import copy
import importlib
import json

import pytest

from backend.bintanong_tools.document_ingest.reviewed_policy import build_reviewed_policy_bundle
from backend.bintanong_tools.knowledge_update.prepare import prepare
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
from backend.bintanong_tools.prospectus_extractor.ledger import LedgerBusy
from test_knowledge_update_prepare import manifest
from test_policy_chunks import item, raw_document
from test_prospectus_ingestion import synthetic_converter


@pytest.fixture
def packet(tmp_path, monkeypatch):
    path, source, _ = manifest(tmp_path)
    out = tmp_path / 'packet'
    value = prepare(path, out, converter=synthetic_converter(monkeypatch, InputSnapshot(source),
        raw_document([item('Submit the form.'), item('Keep the receipt.')], pages=1)))
    return out, value


def session(root, name='Researcher'):
    return importlib.import_module('backend.bintanong_tools.knowledge_update.review').ReviewSession(root, name)


def answer(packet, revision=0, operation='save-1'):
    row = packet['items'][0]
    return {'item_id': row['id'], 'revision': revision, 'operation_id': operation,
            'audience': 'undergraduate', 'reason': 'Compared with the displayed original.',
            'companions': [], 'gaps': [], 'fields': {
                'body': {'decision': 'accepted', 'value': row['fields'][0]['original_value']}}}


def test_review_save_reopen_and_export_uses_actual_bound_decisions(packet):
    root, value = packet
    review = session(root)
    receipt = review.save(answer(value))
    assert receipt['revision'] == 1
    review.close()
    with session(root) as reopened:
        state = reopened.state()
        assert state['revision'] == 1
        assert state['items'][0]['audience'] == 'undergraduate'
        assert state['items'][1]['fields'][0]['decision'] == 'pending'
        exported = reopened.export()
    sources = {doc['sha256']: (root / doc['source']).read_bytes() for doc in value['documents']}
    events = {key: text.encode('utf-8') for key, text in exported['review_events'].items()}
    checked = build_reviewed_policy_bundle(exported['readings'], sources=sources, review_events=events)
    assert checked['selection']['undergraduate'] == [value['items'][0]['id']]
    assert checked['coverage']['field_decisions']['pending'] == 1


def test_review_refuses_concurrent_writer(packet):
    root, _ = packet
    with session(root):
        with pytest.raises(LedgerBusy):
            session(root, 'Second researcher')


def test_review_duplicate_save_is_idempotent_but_stale_edit_is_rejected(packet):
    root, value = packet
    with session(root) as review:
        command = answer(value)
        first = review.save(command)
        assert review.save(command) == first
        changed = copy.deepcopy(command)
        changed['reason'] = 'Different operation with reused identity.'
        with pytest.raises(ValueError, match='operation'):
            review.save(changed)
        changed['operation_id'] = 'save-2'
        with pytest.raises(ValueError, match='revision'):
            review.save(changed)
        assert review.state()['revision'] == 1


@pytest.mark.parametrize('damage', ['unknown_field', 'wrong_type', 'missing_reason', 'unknown_companion'])
def test_review_rejects_invalid_changes_without_appending(packet, damage):
    root, value = packet
    command = answer(value)
    if damage == 'unknown_field':
        command['fields']['not-a-source-field'] = {'decision': 'accepted', 'value': 'invented'}
    elif damage == 'wrong_type':
        command['fields']['body']['value'] = ['unexpected']
    elif damage == 'missing_reason':
        command['reason'] = ''
    else:
        command['companions'] = ['another-packet:item']
    with session(root) as review:
        with pytest.raises(ValueError):
            review.save(command)
        assert review.state()['revision'] == 0


def test_review_source_tampering_stops_save(packet):
    root, value = packet
    with session(root) as review:
        (root / value['documents'][0]['source']).write_bytes(b'changed original')
        with pytest.raises(ValueError, match='digest|identity'):
            review.save(answer(value))


def test_review_journal_tampering_refused_on_reopen(packet):
    root, value = packet
    with session(root) as review:
        review.save(answer(value))
    path = root / 'review/decisions.jsonl'
    entry = json.loads(path.read_text(encoding='utf-8'))
    entry['reason'] = 'Changed after saving'
    path.write_text(json.dumps(entry) + '\n', encoding='utf-8')
    with pytest.raises(ValueError, match='journal'):
        session(root)


def test_review_revision_retains_original_and_history(packet):
    root, value = packet
    with session(root) as review:
        review.save(answer(value))
        changed = answer(value, revision=1, operation='save-2')
        changed['fields']['body'] = {'decision': 'corrected', 'value': 'Submit the original form.'}
        changed['companions'] = [value['items'][1]['id']]
        review.save(changed)
        state = review.state()
        assert state['items'][0]['fields'][0]['original_value'] == 'Submit the form.'
        assert state['items'][0]['fields'][0]['reviewed_value'] == 'Submit the original form.'
        assert state['items'][0]['companions'] == [value['items'][1]['id']]
        assert len(review.history()) == 2
