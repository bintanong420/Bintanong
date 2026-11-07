import json

import pytest

from backend.bintanong_tools.knowledge_update.prepare import prepare
from backend.bintanong_tools.knowledge_update.review import ReviewSession
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
from test_knowledge_update_build import SyntheticEncoder, build_api, reviewed
from test_knowledge_update_prepare import manifest
from test_knowledge_update_review import answer
from test_policy_chunks import item, raw_document
from test_prospectus_ingestion import synthetic_converter


def extension(tmp_path, monkeypatch, baseline, membership):
    inputs = tmp_path / 'extension-inputs'
    inputs.mkdir()
    path, source, spec = manifest(inputs, edition='2027', kind='charter')
    spec['baseline'] = {'path': str(baseline), 'package_id': build_api().load_package(baseline)['manifest']['package_id']}
    spec['membership'] = membership
    spec['build'] = {'reading_ids': ['charter:text-0'], 'assignments': [
        {'reading_id': 'charter:text-0', 'subject_id': 'new_service', 'basis_ref': 'synthetic'}],
        'claim_reviews': [{'subject_id': 'new_service', 'claim': 'instruction', 'finding': 'visible_fields',
            'field_refs': [{'reading_id': 'charter:text-0', 'field_name': 'body'}],
            'basis_ref': 'synthetic', 'basis_reading_id': 'charter:text-0'}]}
    path.write_text(json.dumps(spec))
    root = tmp_path / 'extension'
    packet = prepare(path, root, converter=synthetic_converter(monkeypatch, InputSnapshot(source),
        raw_document([item('A newly reviewed service.')], pages=1)))
    with ReviewSession(root, 'Synthetic researcher') as review:
        review.save(answer(packet))
    return root


def test_baseline_membership_must_partition_every_old_chunk(reviewed, tmp_path, monkeypatch):
    root, _ = reviewed
    baseline = tmp_path / 'baseline'
    build_api().build(root, baseline, encoder=SyntheticEncoder())
    new = extension(tmp_path, monkeypatch, baseline, {'retained': [], 'replaced': {}, 'removed': []})
    with pytest.raises(ValueError, match='membership|partition'):
        build_api().build(new, tmp_path / 'new-package', encoder=SyntheticEncoder())


def test_retained_bytes_keep_old_reviews_and_vectors_while_new_readings_require_their_own(reviewed, tmp_path, monkeypatch):
    root, _ = reviewed
    baseline = tmp_path / 'baseline'
    build_api().build(root, baseline, encoder=SyntheticEncoder())
    old = build_api().load_package(baseline)
    old_id = old['chunks'][0]['chunk_id']
    new = extension(tmp_path, monkeypatch, baseline, {'retained': [old_id], 'replaced': {}, 'removed': []})
    encoder = SyntheticEncoder()
    out = tmp_path / 'extension-package'
    build_api().build(new, out, encoder=encoder)
    result = build_api().load_package(out)
    assert encoder.calls == 1
    assert len(result['chunks']) == 2
    assert old['chunks'][0] in result['chunks']
    assert old['embeddings'][0] in result['embeddings']
    assert {a['subject_id'] for a in result['catalogue']['assignments']} == {'forms', 'new_service'}
    assert result['recipe']['membership']['baseline_package_id'] == old['manifest']['package_id']


def test_replacement_requires_an_explicit_selected_new_reading(reviewed, tmp_path, monkeypatch):
    root, _ = reviewed
    baseline = tmp_path / 'baseline'
    build_api().build(root, baseline, encoder=SyntheticEncoder())
    old = build_api().load_package(baseline)['chunks'][0]['chunk_id']
    new = extension(tmp_path, monkeypatch, baseline, {'retained': [], 'replaced': {old: 'absent'}, 'removed': []})
    with pytest.raises(ValueError, match='replacement|selected'):
        build_api().build(new, tmp_path / 'new-package', encoder=SyntheticEncoder())
