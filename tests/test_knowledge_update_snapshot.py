import pytest

from backend.bintanong_tools.knowledge_update.files import digest, encoded
from backend.bintanong_tools.knowledge_update.prepare import load_packet, prepare
from backend.bintanong_tools.knowledge_update.review import ReviewSession
from backend.bintanong_tools.knowledge_update.snapshot import load_snapshot, snapshot_items
from test_knowledge_update_build import SyntheticEncoder, build_api, reviewed
from test_knowledge_update_review import answer


@pytest.fixture
def snapshot(reviewed, tmp_path):
    root, packet = reviewed
    with ReviewSession(root, 'Synthetic researcher') as review:
        command = answer(packet, revision=1, operation='record-gap')
        command['gaps'] = [{'issue': 'source_cutoff', 'field_names': ['body'],
            'visible_text': 'Submit the form.', 'affected_claims': ['remaining procedure']}]
        review.save(command)
    package_root = tmp_path / 'package'
    build_api().build(root, package_root, encoder=SyntheticEncoder())
    package = build_api().load_package(package_root)
    frozen = tmp_path / 'frozen'
    frozen.mkdir()
    values = {'draft-chunks.json': package['chunks'], 'draft-embedding-manifest.json': package['embedding_manifest'],
        'draft-source-versions.json': {v['version_id']: v for v in package['sources']},
        'draft-subject-catalogue.json': package['catalogue'], 'draft-source-review-register.json': package['claim_reviews'],
        'subject-context-budgets.json': {}}
    for name, value in values.items():
        (frozen / name).write_bytes(encoded(value))
    (frozen / 'draft-embedding-records.jsonl').write_bytes(b''.join(encoded(r) for r in package['embeddings']))
    seal = {p.name: digest(p.read_bytes()) for p in frozen.iterdir()}
    (frozen / 'runtime-seal.json').write_bytes(encoded(seal))
    source = frozen / 'handbook.pdf'
    source.write_bytes((root / packet['documents'][0]['source']).read_bytes())
    manifest = {'schema': 'p11-two-developer-comparison-baseline-v1', 'chunks': 1,
        'files': [{'snapshot': str(p), 'sha256': digest(p.read_bytes())} for p in frozen.iterdir()]}
    manifest_path = frozen / 'baseline-manifest.json'
    manifest_path.write_bytes(encoded(manifest))
    spec = {'schema_version': 'bintanong-knowledge-update-v1',
        'reviewed_snapshot': {'path': str(frozen), 'manifest_sha256': digest(manifest_path.read_bytes())},
        'documents': [{'id': 'handbook', 'kind': 'handbook', 'title': 'Synthetic Handbook', 'edition': 'synthetic',
            'source': str(source), 'sha256': digest(source.read_bytes()), 'locator': 'shelf:synthetic'}]}
    path = tmp_path / 'snapshot-manifest.json'
    path.write_bytes(encoded(spec))
    return path, spec, frozen, package


def test_prepare_snapshot_preserves_source_fields_gaps_and_reference_without_new_approval(snapshot, tmp_path):
    path, spec, frozen, package = snapshot
    before = {p.name: p.read_bytes() for p in frozen.iterdir()}
    out = tmp_path / 'review'
    packet = prepare(path, out)
    assert len(packet['items']) == 1
    row = packet['items'][0]
    assert row['audience'] == 'unresolved'
    assert row['fields'][0]['decision'] == 'pending'
    assert row['fields'][0]['original_value'] == 'Submit the form.'
    assert row['fields'][0]['spans'] == package['chunks'][0]['spans']
    assert row['source_gaps'][0]['issue'] == 'source_cutoff'
    assert row['reference_chunk'] == package['chunks'][0]
    assert not row.get('reference_only')
    assert (out / packet['documents'][0]['source']).read_bytes() == (frozen / 'handbook.pdf').read_bytes()
    assert load_packet(out) == packet
    assert prepare(path, out) == packet
    assert {p.name: p.read_bytes() for p in frozen.iterdir()} == before
    with ReviewSession(out, 'Researcher') as review:
        assert review.state()['source_basis']['kind'] == 'reviewed_snapshot'
        assert review.state()['source_basis']['candidate_review'] is True
        unreviewed = review.export()
        assert unreviewed['readings'][0]['fields'][0]['decision'] == 'pending'
        assert unreviewed['review_events'] == {}
        command = answer(packet)
        command['fields']['body'] = {'decision': 'corrected', 'value': 'Submit the original form.'}
        review.save(command)
        exported = review.export()
        assert exported['readings'][0]['fields'][0]['reviewed_value'] == 'Submit the original form.'
        assert exported['readings'][0]['gaps'] == row['source_gaps']
        assert exported['readings'][0]['reference_chunk'] == package['chunks'][0]
        assert len(exported['review_events']) == 1
    with ReviewSession(out, 'Researcher') as reopened:
        assert reopened.state()['items'][0]['fields'][0]['reviewed_value'] == 'Submit the original form.'
        assert reopened.history()[0]['reason'] == command['reason']
    assert {p.name: p.read_bytes() for p in frozen.iterdir()} == before


@pytest.mark.parametrize('damage', ['manifest', 'chunk', 'source'])
def test_prepare_snapshot_refuses_altered_frozen_evidence_before_output(snapshot, tmp_path, damage):
    path, spec, frozen, _ = snapshot
    if damage == 'manifest':
        spec['reviewed_snapshot']['manifest_sha256'] = '0' * 64
        path.write_bytes(encoded(spec))
    else:
        (frozen / ('draft-chunks.json' if damage == 'chunk' else 'handbook.pdf')).write_bytes(b'changed')
    with pytest.raises(ValueError, match='digest|identity|hash'):
        prepare(path, tmp_path / 'review')
    assert not (tmp_path / 'review').exists()


def test_snapshot_copy_is_bound_to_packet_on_reopen(snapshot, tmp_path):
    path, *_ = snapshot
    out = tmp_path / 'review'
    prepare(path, out)
    (out / 'reference_snapshot/draft-chunks.json').write_bytes(b'changed')
    with pytest.raises(ValueError, match='digest|identity|hash'):
        load_packet(out)


def test_older_reference_packet_remains_read_only_on_reopen(snapshot, tmp_path):
    path, spec, frozen, _ = snapshot
    out = tmp_path / 'old-reference'
    packet = prepare(path, out)
    packet['source_basis'].pop('candidate_review')
    original = load_snapshot(frozen, spec['reviewed_snapshot']['manifest_sha256'])
    packet['items'] = [r for doc in packet['documents'] for r in snapshot_items(original, doc)]
    packet.pop('packet_id')
    packet['packet_id'] = digest(encoded(packet))
    (out / 'packet.json').write_bytes(encoded(packet))
    with ReviewSession(out, 'Researcher') as review:
        with pytest.raises(ValueError, match='read-only'):
            review.save(answer(packet))
        assert review.export()['withheld_items'][0]['reason'] == 'prior_review_reference'
