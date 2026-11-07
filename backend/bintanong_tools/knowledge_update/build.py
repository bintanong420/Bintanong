from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

from ...bintanong_contracts.embedding import EmbeddingRecord, check_embedding_matches_chunk
from ...bintanong_contracts.governance import SourceDocumentVersion
from ...bintanong_contracts.source import Chunk
from ...bintanong_embedding.adapter import EmbeddingConfig, SeaLionEmbeddingAdapter
from ...bintanong_embedding.batch import BatchEmbeddingRunner
from ...bintanong_retrieval.candidate_claims import prepare_candidate_claim_reviews
from ...bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue
from ...bintanong_storage.loader import BatchKnowledgeLoader, CONFIG_FIELDS
from ..document_ingest.inspection import check_out
from ..document_ingest.reviewed_policy import build_reviewed_policy_bundle
from ..document_ingest.reviewed_policy_chunks import build_reviewed_policy_chunks
from .files import contained, digest, encoded, read_json, write_json
from .prepare import load_packet
from .review import ReviewSession
from .baseline import combine, retained_ids

BUILD_KEYS = {'reading_ids', 'assignments', 'claim_reviews', 'token_cap', 'include_source_limits',
              'compact_context', 'flowchart_bindings', 'record_bindings', 'heading_metadata_bindings',
              'source_reviews', 'selected_review', 'research_authorization_ref'}


class LocalEncoder(SeaLionEmbeddingAdapter):
    def __init__(self, model_path: Path):
        model_path = Path(model_path).resolve()
        models = Path('C:/Coding-projects/bintanong_workspace/MODELS').resolve()
        if models not in model_path.parents or not (model_path / 'config.json').is_file():
            raise ValueError('explicit existing workspace embedding model required; downloads are disabled')
        super().__init__(model_path=model_path)

    def load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(str(self.model_path), device='cpu',
                local_files_only=True, trust_remote_code=False)
        return self._model


def _reviewed_chunks(export: dict, sources: dict, versions: list, config: dict):
    if not isinstance(config, dict) or set(config) - BUILD_KEYS:
        raise ValueError('unknown build configuration fields')
    selected = config.get('reading_ids')
    rows = {r['reading_id']: r for r in export['readings']}
    if (not isinstance(selected, list) or not selected or any(not isinstance(i, str) or i not in rows for i in selected)
            or len(set(selected)) != len(selected)):
        raise ValueError('explicit distinct selected review readings required')
    dependencies = {i: refs for i, refs in export['required_readings'].items() if i in selected}
    if any(ref not in selected for refs in dependencies.values() for ref in refs):
        raise ValueError('selected review omits a required companion')
    events = {sha: text.encode('utf-8') for sha, text in export['review_events'].items()}
    preparation = build_reviewed_policy_bundle([rows[i] for i in selected], sources=sources, review_events=events)
    kwargs = {key: config[key] for key in ('flowchart_bindings', 'record_bindings', 'heading_metadata_bindings') if key in config}
    result = build_reviewed_policy_chunks(preparation, sources=sources, review_events=events,
        source_versions=versions, field_spans={i: export['field_spans'][i] for i in selected},
        required_readings=dependencies, token_cap=config.get('token_cap', 480),
        include_source_limits=config.get('include_source_limits', True),
        compact_context=config.get('compact_context', True), **kwargs)
    if result['withheld'] or not result['chunks']:
        raise ValueError('selected readings withheld by source/review checks: ' + json.dumps(result['withheld']))
    return result


def _metadata(chunks: list, config: dict, export: dict):
    catalogue = prepare_candidate_subject_catalogue(chunks, config.get('assignments'))
    if catalogue['unassigned_chunk_ids']:
        raise ValueError('complete explicit subject/topic assignments required')
    supplied = config.get('claim_reviews')
    if not isinstance(supplied, list) or not supplied:
        raise ValueError('explicit source claim review metadata required')
    by_reading = {c['type_fields']['reading_id']: c for c in chunks}
    by_subject = {a['reading_id']: a['subject_id'] for a in catalogue['assignments']}
    readings = {r['reading_id']: r for r in export['readings']}
    reviews = []
    for raw in supplied:
        row = copy.deepcopy(raw)
        basis = row.pop('basis_reading_id', None)
        if basis not in by_reading:
            raise ValueError('claim review basis must be a selected reviewed reading')
        refs = readings[basis]['fields']
        sha = refs[0]['review_event_sha256']
        if not sha or sha not in export['review_events']:
            raise ValueError('claim review basis lacks a source-bound review event')
        row['basis_sha256'] = sha
        row['reviewed_chunk_ids'] = sorted(c['chunk_id'] for i, c in by_reading.items()
                                          if by_subject[i] == row.get('subject_id'))
        reviews.append(row)
    register = prepare_candidate_claim_reviews(catalogue, chunks, reviews)
    if {r['subject_id'] for r in register['reviews']} != set(by_subject.values()):
        raise ValueError('claim review metadata must cover every selected subject')
    return catalogue, register


def _config(config):
    return {name: getattr(config, name) for name in CONFIG_FIELDS}


def build(root: Path, out: Path, *, encoder=None, cached_package: Path | None = None,
          metadata: Path | None = None) -> dict:
    root, out = Path(root).resolve(), Path(out).resolve()
    packet = load_packet(root)
    with ReviewSession(root, 'Package compiler') as review:
        export = review.export()
    config = packet['manifest'].get('build', {})
    if metadata is not None:
        authoring = read_json(Path(metadata))
        if (not isinstance(authoring, dict) or set(authoring) != {'packet_id', 'revision', 'build'}
                or authoring['packet_id'] != packet['packet_id'] or authoring['revision'] != export['revision']):
            raise ValueError('build authoring metadata belongs to a stale packet/review revision')
        config = authoring['build']
    sources = {d['sha256']: contained(root, d['source']).read_bytes() for d in packet['documents']}
    versions = {v['version_id']: v for d in packet['documents'] for v in d['source_versions']}
    derived = _reviewed_chunks(export, sources, list(versions.values()), config)
    chunks = [Chunk.parse(c) for c in derived['chunks']]
    baseline = load_package(root / 'baseline') if 'baseline' in packet['manifest'] else None
    membership = packet['manifest'].get('membership')
    if baseline:
        if baseline['manifest']['package_id'] != packet['manifest']['baseline']['package_id']:
            raise ValueError('baseline package identity mismatch')
        retained_ids(baseline, membership, config['reading_ids'])
        for version in baseline['sources']:
            if version['version_id'] in versions and versions[version['version_id']] != version:
                raise ValueError('baseline source version identity has conflicting metadata')
    cached = load_package(cached_package) if cached_package is not None else None
    if encoder is None and cached is None:
        raise ValueError('provide an explicit local encoder/model or compatible verified cached package')
    expected_config = _config(encoder.config) if encoder is not None else {
        k: cached['embedding_manifest'][k] for k in CONFIG_FIELDS}
    if cached and any(cached['embedding_manifest'][k] != expected_config[k] for k in CONFIG_FIELDS):
        raise ValueError('cached embedding configuration is incompatible')
    cached_records = {r['chunk_id']: EmbeddingRecord.parse(r) for r in cached['embeddings']} if cached else {}
    records, missing = [], []
    for chunk in chunks:
        record = cached_records.get(chunk.chunk_id)
        if record is not None and record.chunk_content_hash == chunk.content_hash:
            records.append(record)
        else:
            missing.append(chunk)
    if missing and encoder is None:
        raise ValueError('cached package does not cover changed chunks; an explicit local encoder is required')
    for chunk in missing:
        count = encoder.count_tokens(chunk.text, is_query=False)
        if not count.exact or not count.includes_prefix_and_special_tokens or count.count > config.get('token_cap', 480):
            raise ValueError('selected context requires an exact prefixed tokenizer count within its token cap')
    if (out / 'package.json').exists():
        previous = load_package(out)
        if (previous['recipe']['export'] != export or previous['recipe']['build'] != config
                or any(previous['embedding_manifest'][k] != expected_config[k] for k in CONFIG_FIELDS)):
            raise ValueError('existing package is stale; use a new output directory')
        return previous['manifest']
    check_out(root, out)
    out.mkdir(parents=True, exist_ok=True)
    if missing:
        runner = BatchEmbeddingRunner(adapter=encoder, output_dir=out)
        fresh, _ = runner.embed_chunks(missing, resume=False)
        records.extend(fresh)
    by_id = {r.chunk_id: r for r in records}
    if set(by_id) != {c.chunk_id for c in chunks} or len(by_id) != len(records):
        raise ValueError('embedding output does not match selected chunks')
    for chunk in chunks:
        record = by_id[chunk.chunk_id]
        check_embedding_matches_chunk(record, chunk)
        if (any(getattr(record, key) != expected_config[key] for key in CONFIG_FIELDS)
                or record.token_count.count > config.get('token_cap', 480)):
            raise ValueError('embedding configuration/token count differs from the selected build')
    exact_chunks = [c.model_copy(update={'token_count': by_id[c.chunk_id].token_count}).model_dump(mode='json') for c in chunks]
    catalogue, claims = _metadata(exact_chunks, config, export)
    embedding_rows = [by_id[c['chunk_id']].model_dump(mode='json') for c in exact_chunks]
    if baseline:
        exact_chunks, catalogue, claims = combine(exact_chunks, catalogue, claims, baseline, membership)
        retained = retained_ids(baseline, membership, config['reading_ids'])
        if any(baseline['embedding_manifest'][k] != expected_config[k] for k in CONFIG_FIELDS):
            raise ValueError('retained baseline vectors require the same embedding configuration')
        embedding_rows.extend(r for r in baseline['embeddings'] if r['chunk_id'] in retained)
        versions.update({v['version_id']: v for v in baseline['sources'] if v['version_id'] in
                         {c['version_id'] for c in exact_chunks}})
    embedding_manifest = {**expected_config, 'schema_version': 'bintanong-embedding-manifest-v1',
        'total_input_chunks': len(exact_chunks), 'total_embedded_records': len(exact_chunks),
        'artifact_records_file': 'embeddings.jsonl'}
    embedding_manifest['embedding_set_id'] = BatchKnowledgeLoader._manifest_record(embedding_manifest, embedding_rows)['embedding_set_id']
    recipe = {'packet_id': packet['packet_id'], 'review_revision': export['revision'], 'export': export,
              'build': config, 'source_documents': packet['documents']}
    if baseline:
        recipe['membership'] = dict(membership, baseline_package_id=baseline['manifest']['package_id'])
        shutil.copytree(root / 'baseline', out / 'baseline')
    for filename, rows in [('chunks.jsonl', exact_chunks), ('embeddings.jsonl', embedding_rows)]:
        (out / filename).write_bytes(b''.join(encoded(row) for row in rows))
    for filename, value in [('embedding_manifest.json', embedding_manifest), ('source_register.json', list(versions.values())),
                            ('topics.json', catalogue), ('claims.json', claims), ('recipe.json', recipe)]:
        write_json(out / filename, value)
    for doc in packet['documents']:
        target = contained(out, doc['source'])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(sources[doc['sha256']])
    coverage = {'selected_readings': config['reading_ids'],
                'unselected_readings': [r['reading_id'] for r in export['readings'] if r['reading_id'] not in config['reading_ids']],
                'withheld_items': export['withheld_items'], 'whole_document_approval': False}
    manifest = {'schema_version': 'bintanong-knowledge-package-v1', 'candidate_only': True,
        'activation_eligible': False, 'packet_id': packet['packet_id'], 'review_revision': export['revision'],
        'coverage': coverage, 'files': {p.relative_to(out).as_posix(): digest(p.read_bytes())
                                     for p in sorted(out.rglob('*')) if p.is_file()}}
    manifest['package_id'] = digest(encoded(manifest))
    write_json(out / 'package.json', manifest)
    load_package(out)
    return manifest


def load_package(root: Path) -> dict:
    try:
        return _load_package(root)
    except (KeyError, TypeError, AttributeError, IndexError, OSError, json.JSONDecodeError) as exc:
        raise ValueError('malformed or incomplete knowledge package') from exc


def _load_package(root: Path) -> dict:
    if root is None:
        raise ValueError('explicit package root required')
    original = Path(root).absolute()
    if any(p.is_symlink() for p in (original, *original.parents)):
        raise ValueError('symlink package refused')
    root = original.resolve()
    manifest = read_json(root / 'package.json')
    if (not isinstance(manifest, dict) or manifest.get('schema_version') != 'bintanong-knowledge-package-v1'
            or manifest.get('candidate_only') is not True or manifest.get('activation_eligible') is not False
            or set(manifest) != {'schema_version', 'candidate_only', 'activation_eligible', 'packet_id',
                                 'review_revision', 'coverage', 'files', 'package_id'}):
        raise ValueError('invalid candidate package')
    core = dict(manifest)
    sha = core.pop('package_id', None)
    if sha != digest(encoded(core)):
        raise ValueError('package identity mismatch')
    required = {'chunks.jsonl', 'embeddings.jsonl', 'embedding_manifest.json', 'source_register.json',
                'topics.json', 'claims.json', 'recipe.json'}
    if not isinstance(manifest['files'], dict) or not required <= set(manifest['files']):
        raise ValueError('package manifest omits a required artifact')
    actual_files = set()
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('symlink package artifact refused')
        if path.is_file() and path != root / 'package.json':
            actual_files.add(path.relative_to(root).as_posix())
    if actual_files != set(manifest['files']):
        raise ValueError('package artifact inventory differs from its manifest')
    for name, expected in manifest['files'].items():
        try:
            actual = digest(contained(root, name).read_bytes())
        except OSError as exc:
            raise ValueError('package artifact missing') from exc
        if actual != expected:
            raise ValueError('package artifact digest mismatch')
    def lines(name):
        return [json.loads(line) for line in contained(root, name).read_bytes().splitlines() if line.strip()]
    chunks, embeddings = lines('chunks.jsonl'), lines('embeddings.jsonl')
    sources = read_json(contained(root, 'source_register.json'))
    recipe = read_json(contained(root, 'recipe.json'))
    if (recipe['packet_id'] != manifest['packet_id'] or recipe['review_revision'] != manifest['review_revision']
            or recipe['export']['revision'] != recipe['review_revision']
            or manifest['coverage']['whole_document_approval'] is not False
            or manifest['coverage']['selected_readings'] != recipe['build']['reading_ids']):
        raise ValueError('package review identity/coverage differs from its derivation')
    vectors = {r['chunk_id']: EmbeddingRecord.parse(r) for r in embeddings}
    versions = {v['version_id']: SourceDocumentVersion.parse(v) for v in sources}
    if len(vectors) != len(embeddings) or set(vectors) != {c['chunk_id'] for c in chunks}:
        raise ValueError('package chunk/vector identities differ')
    source_bytes = {}
    for doc in recipe['source_documents']:
        data = contained(root, doc['source']).read_bytes()
        if digest(data) != doc['sha256']:
            raise ValueError('package original source digest mismatch')
        source_bytes[doc['sha256']] = data
    expected = _reviewed_chunks(recipe['export'], source_bytes, sources, recipe['build'])
    original_chunks = {c['chunk_id']: c for c in expected['chunks']}
    selected_chunks = [c for c in chunks if c['chunk_id'] in original_chunks]
    catalogue, claims = _metadata(selected_chunks, recipe['build'], recipe['export'])
    if 'membership' in recipe:
        baseline = load_package(root / 'baseline')
        membership = dict(recipe['membership'])
        if membership.pop('baseline_package_id', None) != baseline['manifest']['package_id']:
            raise ValueError('baseline package identity mismatch')
        retained = retained_ids(baseline, membership, recipe['build']['reading_ids'])
        _, catalogue, claims = combine(selected_chunks, catalogue, claims, baseline, membership)
        original_chunks.update({c['chunk_id']: c for c in baseline['chunks'] if c['chunk_id'] in retained})
        if any(vectors[r['chunk_id']].model_dump(mode='json') != r
               for r in baseline['embeddings'] if r['chunk_id'] in retained):
            raise ValueError('retained baseline vectors differ from their original package')
    if len(chunks) != len(original_chunks) or {c['chunk_id'] for c in chunks} != set(original_chunks):
        raise ValueError('package membership differs from reviewed/baseline derivation')
    config = read_json(contained(root, 'embedding_manifest.json'))
    if (type(config['total_embedded_records']) is not int or config['total_embedded_records'] != len(embeddings)
            or type(config['total_input_chunks']) is not int or config['total_input_chunks'] != len(chunks)):
        raise ValueError('embedding manifest counts differ from package records')
    derived_manifest = BatchKnowledgeLoader._manifest_record({k: v for k, v in config.items() if k != 'embedding_set_id'}, embeddings)
    if config['embedding_set_id'] != derived_manifest['embedding_set_id']:
        raise ValueError('embedding manifest identity differs from its records/configuration')
    for raw in chunks:
        chunk = Chunk.parse(raw)
        record = vectors[chunk.chunk_id]
        check_embedding_matches_chunk(record, chunk)
        original_chunk = copy.deepcopy(original_chunks.get(chunk.chunk_id))
        if original_chunk is None:
            raise ValueError('chunk is not derived from the selected reviewed evidence')
        original_chunk['token_count'] = record.token_count.model_dump(mode='json')
        if original_chunk != raw or any(getattr(record, key) != config[key] for key in CONFIG_FIELDS):
            raise ValueError('chunk/embedding differs from reviewed derivation or configuration')
        pending, closure = [chunk.chunk_id], set()
        while pending:
            identity = pending.pop()
            if identity in closure:
                continue
            if identity not in original_chunks:
                raise ValueError('required companion missing from package')
            closure.add(identity)
            pending.extend(original_chunks[identity]['type_fields'].get('required_neighbor_chunk_ids', []))
        if sum(vectors[i].token_count.count for i in closure) > recipe['build'].get('token_cap', 480):
            raise ValueError('complete required context exceeds the conservative exact-token budget')
    BatchKnowledgeLoader._manifest_record(config, embeddings)
    BatchKnowledgeLoader._embedding_records(embeddings, config['embedding_set_id'], config)
    if (catalogue != read_json(contained(root, 'topics.json')) or claims != read_json(contained(root, 'claims.json'))):
        raise ValueError('package topic/claim metadata differs from reviewed derivation')
    return {'manifest': manifest, 'recipe': recipe, 'chunks': chunks, 'embeddings': embeddings,
            'embedding_manifest': config, 'sources': sources, 'catalogue': catalogue, 'claim_reviews': claims}
