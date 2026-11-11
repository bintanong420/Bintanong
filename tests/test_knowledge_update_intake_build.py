"""GUI intake step 2: the build form's inputs become build's --metadata file; synthetic packet only."""
import importlib
import json

import pytest
from fastapi.testclient import TestClient

from backend.bintanong_tools.knowledge_update.prepare import prepare
from backend.bintanong_tools.knowledge_update.review import ReviewSession
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
from test_knowledge_update_build import SyntheticEncoder
from test_knowledge_update_prepare import manifest
from test_knowledge_update_review import answer
from test_policy_chunks import item, raw_document
from test_prospectus_ingestion import synthetic_converter

TOKEN = 'test-local-review-token'
ORIGIN = 'http://127.0.0.1:3001'


@pytest.fixture
def reviewed(tmp_path, monkeypatch):
    path, source, _ = manifest(tmp_path)
    root = tmp_path / 'packet'
    packet = prepare(path, root, converter=synthetic_converter(monkeypatch, InputSnapshot(source),
        raw_document([item('Submit the form.'), item('Unreviewed item stays held.')], pages=1)))
    with ReviewSession(root, 'Synthetic researcher') as review:
        review.save(answer(packet))
    return root, packet


def intake():
    return importlib.import_module('backend.bintanong_tools.knowledge_update.intake')


def form(**extra):
    return {'reading_ids': ['handbook:text-0'],
            'assignments': [{'reading_id': 'handbook:text-0', 'subject_id': 'forms'}],
            'claim_reviews': [{'subject_id': 'forms', 'claim': 'instruction', 'finding': 'visible_fields',
                               'field_refs': [{'reading_id': 'handbook:text-0', 'field_name': 'body'}],
                               'basis_reading_id': 'handbook:text-0'}], **extra}


def test_build_plan_shows_ready_and_pending_readings(reviewed):
    root, packet = reviewed
    with ReviewSession(root, 'Synthetic researcher') as review:
        plan = intake().build_plan(review)
    assert plan['packet_id'] == packet['packet_id']
    by_id = {r['reading_id']: r for r in plan['readings']}
    assert by_id['handbook:text-0']['ready'] is True
    assert by_id['handbook:text-1']['ready'] is False and by_id['handbook:text-1']['pending_fields'] == ['body']
    assert plan['withheld_items'] == []


def test_saved_metadata_is_what_build_accepts(reviewed, tmp_path):
    root, _ = reviewed
    with ReviewSession(root, 'Synthetic researcher') as review:
        saved = intake().save_build_metadata(review, form())
    path = root / saved['path']
    value = json.loads(path.read_text(encoding='utf-8'))
    assert set(value) == {'packet_id', 'revision', 'build'}
    assert all(a['basis_ref'] == 'researcher-review:Synthetic researcher' for a in value['build']['assignments'])
    build = importlib.import_module('backend.bintanong_tools.knowledge_update.build')
    result = build.build(root, tmp_path / 'package', encoder=SyntheticEncoder(), metadata=path)
    assert result['coverage']['selected_readings'] == ['handbook:text-0']


def test_metadata_refuses_pending_or_unknown_readings(reviewed):
    root, _ = reviewed
    with ReviewSession(root, 'Synthetic researcher') as review:
        with pytest.raises(ValueError, match='handbook:text-1'):
            intake().save_build_metadata(review, form(reading_ids=['handbook:text-0', 'handbook:text-1']))
        with pytest.raises(ValueError, match='not in this review'):
            intake().save_build_metadata(review, form(reading_ids=['handbook:nope']))
    assert not (root / 'review/build-metadata.json').exists()


@pytest.mark.parametrize('bad', [{'reading_ids': 'handbook:text-0'}, {'assignments': [{'reading_id': 'handbook:text-0'}]},
                                 {'claim_reviews': []}, {'extra': 1},
                                 {'assignments': [{'reading_id': 'handbook:text-0', 'subject_id': 'forms',
                                                   'basis_ref': 'forged'}]},
                                 {'claim_reviews': [{**form()['claim_reviews'][0], 'basis_ref': 'forged'}]}])
def test_metadata_refuses_malformed_forms(reviewed, bad):
    root, _ = reviewed
    with ReviewSession(root, 'Synthetic researcher') as review:
        with pytest.raises(ValueError):
            intake().save_build_metadata(review, form(**bad))


def test_metadata_goes_stale_after_another_review_save(reviewed, tmp_path):
    root, packet = reviewed
    with ReviewSession(root, 'Synthetic researcher') as review:
        path = root / intake().save_build_metadata(review, form())['path']
        review.save(answer(packet, revision=review.state()['revision'], operation='save-2'))
    build = importlib.import_module('backend.bintanong_tools.knowledge_update.build')
    with pytest.raises(ValueError, match='stale'):
        build.build(root, tmp_path / 'package', encoder=SyntheticEncoder(), metadata=path)


def test_build_routes_need_the_token_and_save(reviewed):
    root, _ = reviewed
    module = importlib.import_module('backend.bintanong_tools.knowledge_update.app')
    with ReviewSession(root, 'Synthetic researcher') as review, TestClient(
            module.create_app(review, TOKEN, port=8765, ui_origin=ORIGIN), base_url='http://127.0.0.1:8765') as web:
        assert web.get('/api/intake/build-plan', headers={'origin': ORIGIN}).status_code == 403
        good = {'x-review-token': TOKEN, 'origin': ORIGIN}
        assert web.get('/api/intake/build-plan', headers=good).json()['readings']
        response = web.post('/api/intake/build-metadata', json=form(), headers=good)
        assert response.status_code == 200, response.text
        assert web.post('/api/intake/build-metadata', json=form(reading_ids=['handbook:nope']),
                        headers=good).status_code == 422
