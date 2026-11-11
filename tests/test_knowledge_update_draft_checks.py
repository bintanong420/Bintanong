import json

import pytest

from backend.bintanong_embedding.adapter import EmbeddingConfig
from backend.bintanong_tools.knowledge_update import build as build_mod
from backend.bintanong_tools.knowledge_update import draft_checks
from test_knowledge_update_build import SyntheticEncoder, reviewed  # noqa: F401


class QueryEncoder(SyntheticEncoder):
    """Synthetic package vectors are all (1,0,...); queries matching them retrieve the chunk."""
    def __init__(self, vector=(1.0,) + (0.0,) * 1023):
        super().__init__()
        self.vector = vector

    def encode_queries(self, queries):
        return [self.vector for _ in queries]


@pytest.fixture
def package(reviewed, tmp_path):  # noqa: F811
    root, _ = reviewed
    out = tmp_path / 'package'
    build_mod.build(root, out, encoder=SyntheticEncoder())
    return out


def cases(tmp_path, rows, name='cases.json'):
    path = tmp_path / name
    path.write_text(json.dumps({'schema_version': 'bintanong-draft-check-cases-v1', 'cases': rows}), encoding='utf-8')
    return path


def row(case_id='c1', expected=('handbook:text-0',), **extra):
    return {'case_id': case_id, 'question': 'How do I submit the form?', 'expected_reading_ids': list(expected), **extra}


def run(package, tmp_path, rows, encoder=None, out=None):
    out = out or tmp_path / 'ext_out' / 'report.json'
    return draft_checks.run_checks(package, cases(tmp_path, rows), out, encoder=encoder or QueryEncoder())


def test_pass_and_report_contract(package, tmp_path):
    report = run(package, tmp_path, [row()])
    written = json.loads((tmp_path / 'ext_out' / 'report.json').read_text(encoding='utf-8'))
    assert written == report
    assert report['schema_version'] == 'bintanong-draft-checks-v1'
    assert report['passed'] is True
    assert report['package_id'] == build_mod.load_package(package)['manifest']['package_id']
    case = report['cases'][0]
    assert case['passed'] and case['retrieved'][0]['reading_id'] == 'handbook:text-0'
    assert report['encoder'] == {'model_id': 'synthetic-sealion', 'model_revision': '1' * 40}
    assert 'retrieval only' in report['scope']


def test_unselected_reading_is_an_authoring_error(package, tmp_path):
    with pytest.raises(ValueError, match='unknown expected'):
        run(package, tmp_path, [row('ok'), row('bad', expected=('handbook:text-1',))])

def test_miss_when_expected_not_in_top_k(package, tmp_path, monkeypatch):
    monkeypatch.setattr(draft_checks, '_retrieve', lambda *a, **k: [])
    report = run(package, tmp_path, [row()])
    assert report['passed'] is False and report['cases'][0]['passed'] is False
    assert json.loads((tmp_path / 'ext_out' / 'report.json').read_text(encoding='utf-8'))['passed'] is False


def test_one_failure_fails_whole_report(package, tmp_path, monkeypatch):
    real = draft_checks._retrieve
    monkeypatch.setattr(draft_checks, '_retrieve', lambda storage, vector, top_k, *, q=[0]: real(storage, vector, top_k) if not q.append(1) and len(q) == 2 else [])
    report = run(package, tmp_path, [row('a'), row('b')])
    assert [c['passed'] for c in report['cases']] == [True, False] and report['passed'] is False


def test_mismatched_encoder_config_refused(package, tmp_path):
    encoder = QueryEncoder()
    encoder.config = EmbeddingConfig(model_id='synthetic-sealion', model_revision='2' * 40)
    with pytest.raises(ValueError, match='embedding configuration'):
        run(package, tmp_path, [row()], encoder=encoder)
    assert not (tmp_path / 'ext_out' / 'report.json').exists()


@pytest.mark.parametrize('rows', [
    [], [row('a'), row('a')], [row(question='  ')], [row(expected=())], [row(top_k=0)], [row(top_k=21)],
    [row(top_k=True)], [row(expected=('nope:0',))], [row(case_id='')], [{'case_id': 'x'}],
    [row(extra_field=1)], [row() for _ in range(201)]])
def test_malformed_cases_refused(package, tmp_path, rows):
    with pytest.raises(ValueError):
        run(package, tmp_path, rows)


def test_bad_schema_version_refused(package, tmp_path):
    path = tmp_path / 'c.json'
    path.write_text(json.dumps({'schema_version': 'x', 'cases': [row()]}), encoding='utf-8')
    with pytest.raises(ValueError, match='schema'):
        draft_checks.run_checks(package, path, tmp_path / 'o' / 'r.json', encoder=QueryEncoder())


def test_unverifiable_package_refused(package, tmp_path):
    (package / 'chunks.jsonl').write_bytes(b'tampered\n')
    with pytest.raises(ValueError):
        run(package, tmp_path, [row()])


def test_output_inside_git_refused(package, tmp_path):
    inside = tmp_path / 'repo'
    (inside / '.git').mkdir(parents=True)
    with pytest.raises(ValueError, match='git'):
        run(package, tmp_path, [row()], out=inside / 'report.json')


def synthetic_ranked_package():
    """Three chunks with distinct vectors; query (1,0,0) scores r1=0.9 > r2=0.6 > r3=0.3."""
    import math
    def vec(score):
        return [score, math.sqrt(1 - score * score)] + [0.0] * 1022
    names = ['r1', 'r2', 'r3']
    chunks = [{'chunk_id': 'c-' + n, 'version_id': 'v', 'scope': [], 'spans': [],
               'type_fields': {'reading_id': n}} for n in names]
    config = {k: 'x' for k in ('model_id', 'model_revision', 'dimension', 'normalization',
              'prompt_fingerprint', 'preprocessing_fingerprint', 'tokenizer_fingerprint')}
    config.update(model_id='synthetic-sealion', model_revision='1' * 40, embedding_set_id='set-1')
    return {'manifest': {'package_id': 'pkg-1', 'files': {'chunks.jsonl': 'a', 'embeddings.jsonl': 'b',
                                                          'embedding_manifest.json': 'c'}},
            'embedding_manifest': config, 'chunks': chunks, 'sources': [{'version_id': 'v'}],
            'embeddings': [{'chunk_id': 'c-' + n, 'vector': vec(s)} for n, s in zip(names, (0.9, 0.6, 0.3))]}


@pytest.fixture
def ranked(monkeypatch):
    monkeypatch.setattr(draft_checks, 'load_package', lambda path: synthetic_ranked_package())
    monkeypatch.setattr(draft_checks, 'CONFIG_FIELDS', ('model_id', 'model_revision'))


def ranked_run(tmp_path, top_k, expected='r3'):
    encoder = QueryEncoder(vector=(1.0,) + (0.0,) * 1023)
    return run(tmp_path, tmp_path, [row(expected=(expected,), top_k=top_k)], encoder=encoder)


def test_rank_three_fails_top_two_passes_top_three(ranked, tmp_path):
    assert ranked_run(tmp_path, 2)['passed'] is False
    report = ranked_run(tmp_path, 3)
    assert report['passed'] is True
    assert [r['reading_id'] for r in report['cases'][0]['retrieved']] == ['r1', 'r2', 'r3']


def test_scores_sorted_descending_and_top_k_limits(ranked, tmp_path):
    report = ranked_run(tmp_path, 2, expected='r1')
    scores = [r['score'] for r in report['cases'][0]['retrieved']]
    assert len(scores) == 2 and scores == sorted(scores, reverse=True)
    assert scores[0] == pytest.approx(0.9) and scores[1] == pytest.approx(0.6)


def test_package_binding_comes_from_package_digests(package, tmp_path):
    report = run(package, tmp_path, [row()])
    loaded = build_mod.load_package(package)
    files = loaded['manifest']['files']
    assert report['package_binding'] == {'package_id': loaded['manifest']['package_id'],
        'chunks_sha256': files['chunks.jsonl'], 'embeddings_sha256': files['embeddings.jsonl'],
        'embedding_manifest_sha256': files['embedding_manifest.json'],
        'embedding_set_id': loaded['embedding_manifest']['embedding_set_id']}

def test_question_longer_than_the_model_context_is_refused(package, tmp_path):
    long = ' '.join(['word'] * 600)  # synthetic counter: words + 2 tokens, over the 512-token context
    with pytest.raises(ValueError, match='too long'):
        run(package, tmp_path, [row(question=long)])