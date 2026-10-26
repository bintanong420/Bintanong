import json

import pytest

from backend.bintanong_tools.knowledge_update.build import build
from backend.bintanong_tools.knowledge_update.files import digest, encoded
from backend.bintanong_tools.knowledge_update.verify import verify
from test_knowledge_update_build import reviewed, SyntheticEncoder


@pytest.fixture
def package(reviewed, tmp_path):
    root, _ = reviewed
    out = tmp_path / 'package'
    build(root, out, encoder=SyntheticEncoder())
    return out


def reseal(root, changed=()):
    value = json.loads((root / 'package.json').read_bytes())
    for name in changed:
        value['files'][name] = digest((root / name).read_bytes())
    value.pop('package_id')
    value['package_id'] = digest(encoded(value))
    (root / 'package.json').write_bytes(encoded(value))


def test_verify_refuses_consumed_file_omitted_from_manifest(package):
    manifest = json.loads((package / 'package.json').read_bytes())
    manifest['files'].pop('embeddings.jsonl')
    (package / 'package.json').write_bytes(encoded(manifest))
    reseal(package)
    with pytest.raises(ValueError, match='artifact|inventory|manifest'):
        verify(package)


def test_verify_refuses_wrong_embedding_counts_even_after_rehash(package):
    path = package / 'embedding_manifest.json'
    value = json.loads(path.read_bytes())
    value['total_embedded_records'] = 999
    path.write_bytes(encoded(value))
    reseal(package, ['embedding_manifest.json'])
    with pytest.raises(ValueError, match='count|configuration|manifest'):
        verify(package)


def test_verify_refuses_extra_unaccounted_artifact(package):
    (package / 'unaccounted.json').write_text('{}')
    with pytest.raises(ValueError, match='artifact|inventory'):
        verify(package)


def test_verify_refuses_subject_changes_even_with_valid_file_hash(package):
    path = package / 'topics.json'
    value = json.loads(path.read_bytes())
    value['assignments'][0]['subject_id'] = 'different_subject'
    path.write_bytes(encoded(value))
    reseal(package, ['topics.json'])
    with pytest.raises(ValueError, match='topic|claim'):
        verify(package)
