import copy
import importlib
import json
from types import SimpleNamespace

import pytest

from backend.bintanong_contracts.embedding import EmbeddingRecord
from backend.bintanong_contracts.source import TokenCount
from backend.bintanong_embedding.adapter import EmbeddingConfig
from backend.bintanong_tools.knowledge_update.prepare import prepare
from backend.bintanong_tools.knowledge_update.review import ReviewSession
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
from test_knowledge_update_prepare import manifest
from test_knowledge_update_review import answer
from test_policy_chunks import item, raw_document
from test_prospectus_ingestion import synthetic_converter


class SyntheticEncoder:
    def __init__(self):
        self.config = EmbeddingConfig(model_id='synthetic-sealion', model_revision='1' * 40)
        self.calls = 0

    def count_tokens(self, text, is_query=False):
        return TokenCount(count=len(text.split()) + 2, method='tokenizer:synthetic-sealion@' + '1' * 40,
                          exact=True, includes_prefix_and_special_tokens=True)

    def encode_documents(self, chunks):
        self.calls += len(chunks)
        return [EmbeddingRecord(schema_version=EmbeddingRecord.SCHEMA_VERSION, chunk_id=c.chunk_id,
            chunk_content_hash=c.content_hash, model_id=self.config.model_id,
            model_revision=self.config.model_revision, dimension=1024, normalization='l2',
            tokenizer_fingerprint=self.config.tokenizer_fingerprint,
            preprocessing_fingerprint=self.config.preprocessing_fingerprint,
            prompt_fingerprint=self.config.prompt_fingerprint,
            token_count=self.count_tokens(c.text), vector=(1.0,) + (0.0,) * 1023) for c in chunks]


@pytest.fixture
def reviewed(tmp_path, monkeypatch):
    path, source, spec = manifest(tmp_path)
    spec['build'] = {'reading_ids': ['handbook:text-0'],
        'assignments': [{'reading_id': 'handbook:text-0', 'subject_id': 'forms', 'basis_ref': 'synthetic-authoring'}],
        'claim_reviews': [{'subject_id': 'forms', 'claim': 'instruction', 'finding': 'visible_fields',
            'field_refs': [{'reading_id': 'handbook:text-0', 'field_name': 'body'}],
            'basis_ref': 'synthetic-authoring', 'basis_reading_id': 'handbook:text-0'}]}
    path.write_text(json.dumps(spec), encoding='utf-8')
    root = tmp_path / 'packet'
    packet = prepare(path, root, converter=synthetic_converter(monkeypatch, InputSnapshot(source),
        raw_document([item('Submit the form.'), item('Unreviewed item stays held.')], pages=1)))
    with ReviewSession(root, 'Synthetic researcher') as review:
        review.save(answer(packet))
    return root, packet


def build_api():
    return importlib.import_module('backend.bintanong_tools.knowledge_update.build')


def test_build_reuses_reviewed_builders_and_runtime_storage_contract(reviewed, tmp_path):
    root, packet = reviewed
    encoder = SyntheticEncoder()
    result = build_api().build(root, tmp_path / 'package', encoder=encoder)
    assert encoder.calls == 1
    assert result['candidate_only'] is True
    assert result['coverage']['selected_readings'] == ['handbook:text-0']
    assert result['coverage']['unselected_readings'] == ['handbook:text-1']
    package = build_api().load_package(tmp_path / 'package')
    assert len(package['chunks']) == 1
    assert package['catalogue']['assignments'][0]['subject_id'] == 'forms'
    assert package['claim_reviews']['reviews'][0]['finding'] == 'visible_fields'
    from backend.bintanong_runtime.package_storage import PackageStorage
    storage = PackageStorage(release_id='synthetic-draft', manifest=package['embedding_manifest'],
        chunks=package['chunks'], versions={v['version_id']: v for v in package['sources']},
        vectors={r['chunk_id']: r['vector'] for r in package['embeddings']})
    assert storage.embedding_set_id == package['embedding_manifest']['embedding_set_id']


def test_build_reuses_only_compatible_cached_vectors(reviewed, tmp_path):
    root, _ = reviewed
    first = tmp_path / 'first'
    build_api().build(root, first, encoder=SyntheticEncoder())
    second = SyntheticEncoder()
    build_api().build(root, tmp_path / 'second', encoder=second, cached_package=first)
    assert second.calls == 0
    third = SyntheticEncoder()
    third.config = EmbeddingConfig(model_id='synthetic-sealion', model_revision='2' * 40)
    with pytest.raises(ValueError, match='config|compatible'):
        build_api().build(root, tmp_path / 'third', encoder=third, cached_package=first)


@pytest.mark.parametrize('audience,decision', [('excluded', 'accepted'), ('unresolved', 'accepted'),
                                            ('undergraduate', 'unresolved')])
def test_build_refuses_selected_unreviewed_or_excluded_fields(reviewed, tmp_path, audience, decision):
    root, packet = reviewed
    with ReviewSession(root, 'Synthetic researcher') as review:
        command = answer(packet, revision=1, operation='hold')
        command['audience'] = audience
        command['fields']['body']['decision'] = decision
        review.save(command)
    with pytest.raises(ValueError, match='withheld|review'):
        build_api().build(root, tmp_path / 'package', encoder=SyntheticEncoder())


def test_build_does_not_treat_estimated_counts_as_verified(reviewed, tmp_path):
    root, _ = reviewed
    encoder = SyntheticEncoder()
    encoder.count_tokens = lambda text, is_query=False: TokenCount(count=10, method='estimate-v1',
        exact=False, includes_prefix_and_special_tokens=False)
    with pytest.raises(ValueError, match='exact|token'):
        build_api().build(root, tmp_path / 'package', encoder=encoder)


def test_package_tampering_and_stale_review_are_rejected(reviewed, tmp_path):
    root, packet = reviewed
    out = tmp_path / 'package'
    build_api().build(root, out, encoder=SyntheticEncoder())
    verifier = importlib.import_module('backend.bintanong_tools.knowledge_update.verify')
    assert verifier.verify(out, packet_root=root)['verified'] is True
    with ReviewSession(root, 'Synthetic researcher') as review:
        command = answer(packet, revision=1, operation='revised')
        command['reason'] = 'New review revision requires a new package.'
        review.save(command)
    with pytest.raises(ValueError, match='stale|revision'):
        verifier.verify(out, packet_root=root)
    (out / 'chunks.jsonl').write_text('{}\n', encoding='utf-8')
    with pytest.raises(ValueError, match='digest|identity'):
        verifier.verify(out)


def test_build_preserves_explicit_scalar_correction_and_original_evidence(reviewed, tmp_path):
    root, packet = reviewed
    with ReviewSession(root, 'Synthetic researcher') as review:
        command = answer(packet, revision=1, operation='correct')
        command['fields']['body'] = {'decision': 'corrected', 'value': 'Submit the original form.'}
        review.save(command)
    build_api().build(root, tmp_path / 'package', encoder=SyntheticEncoder())
    package = build_api().load_package(tmp_path / 'package')
    assert 'Submit the original form.' in package['chunks'][0]['text']
    assert packet['items'][0]['fields'][0]['original_value'] == 'Submit the form.'
    assert package['chunks'][0]['spans'][0]['extraction']['resolution_method'] == 'human_review'


def test_build_refuses_incomplete_topic_and_claim_authoring(reviewed, tmp_path):
    root, packet = reviewed
    metadata = tmp_path / 'metadata.json'
    metadata.write_text(json.dumps({'packet_id': packet['packet_id'], 'revision': 1,
        'build': {'reading_ids': ['handbook:text-0'], 'assignments': [], 'claim_reviews': []}}))
    with pytest.raises(ValueError, match='subject|topic|claim'):
        build_api().build(root, tmp_path / 'package', encoder=SyntheticEncoder(), metadata=metadata)
