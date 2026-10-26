from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path, PureWindowsPath

from ...bintanong_contracts.embedding import EmbeddingRecord, check_embedding_matches_chunk
from ...bintanong_contracts.governance import SourceDocumentVersion
from ...bintanong_contracts.reviewed_policy_context import render_reviewed_policy_context
from ...bintanong_contracts.source import Chunk
from ...bintanong_retrieval.candidate_claims import prepare_candidate_claim_reviews
from ...bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue
from ...bintanong_storage.loader import BatchKnowledgeLoader
from .files import contained, digest, encoded, read_json, write_json


def load_snapshot(root: Path, expected_sha256: str) -> dict:
    try:
        return _load_snapshot(root, expected_sha256)
    except (KeyError, TypeError, AttributeError, IndexError, OSError, json.JSONDecodeError) as exc:
        raise ValueError('malformed or incomplete reviewed snapshot') from exc


def _load_snapshot(root: Path, expected_sha256: str) -> dict:
    root = Path(root).absolute()
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError('symlink snapshot refused')
    if digest((root / 'baseline-manifest.json').read_bytes()) != expected_sha256:
        raise ValueError('snapshot manifest digest mismatch')
    manifest = read_json(root / 'baseline-manifest.json')
    if manifest.get('schema') != 'p11-two-developer-comparison-baseline-v1':
        raise ValueError('unsupported reviewed snapshot')
    names = set()
    for row in manifest['files']:
        name = PureWindowsPath(row['snapshot']).name
        if name in names or digest(contained(root, name).read_bytes()) != row['sha256']:
            raise ValueError('snapshot file digest or identity mismatch')
        names.add(name)
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if actual != names | {'baseline-manifest.json'} or any(p.is_symlink() for p in root.rglob('*')):
        raise ValueError('snapshot file inventory mismatch')
    seal = read_json(contained(root, 'runtime-seal.json'))
    required = {'draft-chunks.json', 'draft-embedding-manifest.json', 'draft-embedding-records.jsonl',
                'draft-source-versions.json', 'draft-subject-catalogue.json',
                'draft-source-review-register.json', 'subject-context-budgets.json'}
    if set(seal) != required or not required <= names:
        raise ValueError('complete reviewed snapshot seal required')
    if any(digest(contained(root, name).read_bytes()) != sha for name, sha in seal.items()):
        raise ValueError('snapshot runtime seal digest mismatch')
    chunks = read_json(root / 'draft-chunks.json')
    versions = read_json(root / 'draft-source-versions.json')
    catalogue = read_json(root / 'draft-subject-catalogue.json')
    claims = read_json(root / 'draft-source-review-register.json')
    records = [EmbeddingRecord.parse(json.loads(line)) for line in
               (root / 'draft-embedding-records.jsonl').read_bytes().splitlines() if line.strip()]
    by_id = {c['chunk_id']: c for c in chunks}
    vectors = {r.chunk_id: r for r in records}
    if len(by_id) != len(chunks) or len(vectors) != len(records) or set(vectors) != set(by_id) or len(chunks) != manifest['chunks']:
        raise ValueError('snapshot chunk/vector identity mismatch')
    for key, row in versions.items():
        if SourceDocumentVersion.parse(row).version_id != key:
            raise ValueError('snapshot source version identity mismatch')
    for raw in chunks:
        chunk = Chunk.parse(raw)
        check_embedding_matches_chunk(vectors[chunk.chunk_id], chunk)
        render_reviewed_policy_context(raw, raw['spans'])
        if (chunk.version_id not in versions or versions[chunk.version_id]['byte_sha256'] != chunk.byte_sha256
                or any(i not in by_id or by_id[i]['version_id'] != chunk.version_id
                       for i in chunk.type_fields.get('required_neighbor_chunk_ids', []))):
            raise ValueError('snapshot source/companion identity mismatch')
    embedding_manifest = read_json(root / 'draft-embedding-manifest.json')
    if embedding_manifest.get('total_embedded_records') != len(chunks):
        raise ValueError('snapshot embedding count mismatch')
    BatchKnowledgeLoader._embedding_records([r.model_dump(mode='json') for r in records],
        embedding_manifest['embedding_set_id'], embedding_manifest)
    if (prepare_candidate_subject_catalogue(chunks, catalogue['assignments']) != catalogue
            or prepare_candidate_claim_reviews(catalogue, chunks, claims['reviews']) != claims):
        raise ValueError('snapshot topic/claim metadata mismatch')
    return {'chunks': chunks, 'versions': versions, 'catalogue': catalogue}


def snapshot_items(snapshot: dict, doc: dict, *, candidate_review: bool = False) -> list[dict]:
    selected = [c for c in snapshot['chunks'] if c['byte_sha256'] == doc['sha256']]
    if not selected or any(c['scope'] != ['audience:undergraduate'] for c in selected):
        raise ValueError('snapshot needs explicitly undergraduate source records for this document')
    by_id = {c['chunk_id']: c['type_fields']['reading_id'] for c in selected}
    subjects = {a['reading_id']: a['subject_id'].replace('_', ' ') for a in snapshot['catalogue']['assignments']}
    result = []
    for chunk in selected:
        meta = chunk['type_fields']
        identity = meta['reading_id']
        pages = sorted({s['page'] for s in chunk['spans']})
        first = next((f['value'] for f in meta['field_associations'] if isinstance(f['value'], str) and f['value']), '')
        title = subjects.get(identity, 'Source record').capitalize()
        if first:
            title += ': ' + first[:100] + ('…' if len(first) > 100 else '')
        fields = []
        for field in meta['field_associations']:
            spans = [copy.deepcopy(chunk['spans'][i]) for i in field['span_indexes']]
            fields.append({'name': field['name'], 'original_value': copy.deepcopy(field['value']),
                'reviewed_value': copy.deepcopy(field['value']), 'decision': 'pending',
                'source_blank': field['source_blank'], 'locator': {
                    'physical_pages': sorted({s['page'] for s in spans}) or pages, 'field': field['name']}, 'spans': spans})
        result.append({'id': identity, 'document_id': doc['id'], 'title': title,
            'audience': 'unresolved', 'companions': [by_id[i] for i in meta.get('required_neighbor_chunk_ids', [])],
            'findings': [], 'fields': fields, 'source_gaps': copy.deepcopy(meta.get('source_limits', [])),
            'reference_only': not candidate_review, 'reference_chunk': copy.deepcopy(chunk)})
        if candidate_review:
            for field, association in zip(fields, meta['field_associations']):
                for key in ('field_kind', 'node_reading_ids'):
                    if key in association:
                        field[key] = copy.deepcopy(association[key])
    return result


def prepare_snapshot(manifest: dict, out: Path, snapshot: dict) -> dict:
    reference = manifest['reviewed_snapshot']
    items = [row for doc in manifest['documents'] for row in snapshot_items(snapshot, doc, candidate_review=True)]
    if len({row['id'] for row in items}) != len(items):
        raise ValueError('duplicate snapshot reading identity')
    out.mkdir(parents=True, exist_ok=True)
    shutil.copytree(reference['path'], out / 'reference_snapshot')
    documents = []
    for doc in manifest['documents']:
        name = 'sources/' + doc['id'] + '.pdf'
        path = contained(out, name)
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(Path(doc['source']).read_bytes())
        documents.append({**doc, 'source': name, 'source_versions': [v for v in snapshot['versions'].values()
            if v['byte_sha256'] == doc['sha256']]})
    artifacts = {p.relative_to(out).as_posix(): digest(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}
    packet = {'schema_version': 'bintanong-review-packet-v1', 'candidate_only': True, 'manifest': manifest,
        'documents': documents, 'items': items, 'artifacts': artifacts,
        'source_basis': {'kind': 'reviewed_snapshot', 'manifest_sha256': reference['manifest_sha256'],
                         'selected_records': len(items), 'whole_document_review': False, 'candidate_review': True}}
    packet['packet_id'] = digest(encoded(packet))
    write_json(out / 'packet.json', packet)
    return packet
