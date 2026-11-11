"""Targeted question checks against a candidate knowledge package (retrieval only).

For each authored question this checks that the package's own stored vectors return a chunk
from an expected reviewed reading within top-k. It does NOT check answer correctness,
institutional approval or currentness. The report ({package_id, passed}) is consumed by the
activation step; passed is True only when at least one case ran and every case passed.

package_binding repeats the digests load_package already verified (package_id, which covers the
manifest and every file digest, plus the chunk/embedding/embedding-manifest file digests and the
embedding_set_id). The report is unsigned and trusted only as a local-operator artifact: binding
proves which package bytes it was produced for, not who produced it.

Limits: ranking is raw cosine rank within the package; answer-time scope, entity hints and
evidence-policy filters are not applied. Pass build.LocalEncoder: a bare SeaLionEmbeddingAdapter
without its model library silently falls back to mock vectors.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ...bintanong_runtime.package_storage import PackageStorage
from ...bintanong_storage.loader import CONFIG_FIELDS
from .build import load_package
from .files import read_json, write_json

CASES_SCHEMA = 'bintanong-draft-check-cases-v1'
REPORT_SCHEMA = 'bintanong-draft-checks-v1'
SCOPE = 'retrieval only: does an expected reviewed source come back in top-k; not answer correctness or approval'
_CASE_KEYS = {'case_id', 'question', 'expected_reading_ids', 'top_k'}


def _text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _cases(path: Path, reading_ids: set) -> list:
    data = read_json(Path(path))
    if not isinstance(data, dict) or data.get('schema_version') != CASES_SCHEMA or set(data) != {'schema_version', 'cases'}:
        raise ValueError('cases file has the wrong schema')
    rows = data['cases']
    if not isinstance(rows, list) or not 1 <= len(rows) <= 200:
        raise ValueError('1 to 200 cases required')
    seen, result = set(), []
    for row in rows:
        if (not isinstance(row, dict) or not {'case_id', 'question', 'expected_reading_ids'} <= set(row)
                or set(row) - _CASE_KEYS):
            raise ValueError('malformed case')
        top_k = row.get('top_k', 5)
        expected = row['expected_reading_ids']
        if (not _text(row['case_id']) or row['case_id'] in seen or not _text(row['question'])
                or type(top_k) is not int or not 1 <= top_k <= 20
                or not isinstance(expected, list) or not expected or not all(_text(i) for i in expected)):
            raise ValueError('malformed case ' + repr(row.get('case_id')))
        if any(i not in reading_ids for i in expected):
            raise ValueError('unknown expected reading id in case ' + row['case_id'])
        seen.add(row['case_id'])
        result.append({'case_id': row['case_id'], 'question': row['question'],
                       'expected_reading_ids': list(expected), 'top_k': top_k})
    return result


def _retrieve(storage: PackageStorage, vector, top_k: int) -> list:
    reply = storage.rpc('retrieve_context', dict(p_release_id=storage.release_id, p_scope=[], p_top_k=top_k,
                                                 p_min_similarity=-1.0, query_embedding=list(vector)), role='runtime')
    return [(i['chunk'], i['similarity']) for i in reply['items']]


def run_checks(package_path, cases_path, out_path, *, encoder) -> dict:
    package = load_package(Path(package_path))
    manifest = package['embedding_manifest']
    if any(getattr(encoder.config, k) != manifest[k] for k in CONFIG_FIELDS):
        raise ValueError('encoder embedding configuration differs from the package vectors')
    out = Path(out_path).resolve()
    for parent in (out, *out.parents):
        if (parent / '.git').exists():
            raise ValueError('output is inside a git repository')
    reading_ids = {c['type_fields']['reading_id'] for c in package['chunks']}
    cases = _cases(Path(cases_path), reading_ids)
    storage = PackageStorage(release_id='draft-check', manifest=manifest, chunks=package['chunks'],
        versions={v['version_id']: v for v in package['sources']},
        vectors={r['chunk_id']: r['vector'] for r in package['embeddings']})
    files = package['manifest']['files']
    results = []
    for case in cases:
        # the runtime query encoder refuses over-length queries; the adapter would silently truncate
        if encoder.count_tokens(case['question'], is_query=True).count > encoder.config.max_context_length:
            raise ValueError(f"case {case['case_id']}: question too long for the embedding model context")
        vector = encoder.encode_queries([case['question']])[0]
        hits = _retrieve(storage, vector, case['top_k'])
        retrieved = [{'chunk_id': c['chunk_id'], 'reading_id': c['type_fields']['reading_id'], 'score': s}
                     for c, s in hits]
        results.append({'case_id': case['case_id'], 'expected_reading_ids': case['expected_reading_ids'],
            'passed': any(r['reading_id'] in case['expected_reading_ids'] for r in retrieved),
            'retrieved': retrieved})
    report = {'schema_version': REPORT_SCHEMA, 'package_id': package['manifest']['package_id'],
        'package_binding': {'package_id': package['manifest']['package_id'],
            'chunks_sha256': files['chunks.jsonl'], 'embeddings_sha256': files['embeddings.jsonl'],
            'embedding_manifest_sha256': files['embedding_manifest.json'],
            'embedding_set_id': manifest['embedding_set_id']},
        'passed': bool(results) and all(r['passed'] for r in results), 'scope': SCOPE, 'cases': results,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'encoder': {'model_id': encoder.config.model_id, 'model_revision': encoder.config.model_revision}}
    write_json(out, report)
    return report
