from __future__ import annotations

import copy
import shutil
from pathlib import Path

from ..document_ingest.bundle import load_candidate_bundle
from ..document_ingest.inspection import check_out
from ..document_ingest.register import pending_version
from ..prospectus_extractor.identity import InputSnapshot
from .files import contained, digest, encoded, read_json, write_json
from .manifest import KINDS, load_manifest
from .templates import template_items


def _items(root: Path, doc: dict, checked: dict) -> list[dict]:
    identity = doc['id']
    if doc['kind'] == 'prospectus':
        payload = checked['domain_payload']
        return [{'id': identity + ':prospectus', 'document_id': identity,
                 'title': doc['title'], 'audience': 'unresolved', 'companions': [],
                 'findings': ['prospectus_review_required'], 'fields': [],
                 'prospectus_candidate': payload}]
    candidate = read_json(root / 'conversion/procedure_candidates.json')
    units = (candidate.get('pdf') or {}).get('units', [])
    tables = candidate.get('tables', [])
    result = []
    for unit in [*units, *tables]:
        item_id = unit.get('item_id', unit.get('table_id'))
        text = unit.get('source_text', unit.get('raw_table_json', ''))
        spans = unit.get('spans', [])
        result.append({'id': identity + ':' + item_id, 'document_id': identity,
            'title': ' / '.join(unit.get('heading_path', [])) or unit.get('label', item_id),
            'audience': 'unresolved', 'companions': [],
            'findings': [unit['rejection_reason']] if unit.get('rejection_reason') else [],
            'fields': [{'name': 'body', 'original_value': text, 'reviewed_value': text,
                        'decision': 'pending', 'source_blank': not text,
                        'locator': {'physical_pages': sorted({s['page'] for s in spans}) or unit.get('pages', []),
                                    'field': 'body'}, 'spans': spans}]})
    for omission in (candidate.get('pdf') or {}).get('item_omissions', []):
        result.append({'id': identity + ':' + omission['item_id'], 'document_id': identity,
            'title': 'Extraction omission', 'audience': 'unresolved', 'companions': [],
            'findings': [omission['reason']], 'fields': [{'name': 'body',
                'original_value': omission['raw_text'], 'reviewed_value': omission['raw_text'],
                'decision': 'pending', 'source_blank': not omission['raw_text'], 'spans': [],
                'locator': {'physical_pages': omission['pages'], 'field': 'body'}}]})
    for omission in (candidate.get('pdf') or {}).get('page_omissions', []):
        result.append({'id': identity + ':page-' + str(omission['page']), 'document_id': identity,
            'title': 'Page requires extraction review', 'audience': 'unresolved', 'companions': [],
            'findings': [omission['reason']], 'fields': [{'name': 'body', 'original_value': '',
                'reviewed_value': '', 'decision': 'pending', 'source_blank': False, 'spans': [],
                'locator': {'physical_pages': [omission['page']], 'field': 'body'}}]})
    return result


def _checked_bundle(root: Path, doc: dict) -> dict:
    checked = load_candidate_bundle(root)
    if (checked['document_kind'] != KINDS[doc['kind']]
            or doc['sha256'] not in {v.byte_sha256 for v in checked['source_register']}):
        raise ValueError('candidate bundle does not match document source/kind')
    return checked


def prepare(manifest_path: Path, out: Path, *, converter=None) -> dict:
    if any(p.is_symlink() for p in (Path(out), *Path(out).absolute().parents)):
        raise ValueError('symlink output refused')
    manifest_path, out = Path(manifest_path).resolve(), Path(out).resolve()
    manifest = load_manifest(manifest_path)
    if (out / 'packet.json').exists():
        if (any((p / '.git').exists() for p in (out, *out.parents))
                or any(Path(d['source']).parent == out or Path(d['source']).parent in out.parents
                       for d in manifest['documents'])):
            raise ValueError('unsafe packet output location')
        previous = load_packet(out)
        if previous['manifest'] != manifest:
            raise ValueError('existing packet belongs to another manifest')
        return previous
    # Validate every input before emitting any packet or invoking a converter.
    if 'reviewed_snapshot' in manifest:
        from .snapshot import load_snapshot, prepare_snapshot
        reference = manifest['reviewed_snapshot']
        snapshot = load_snapshot(Path(reference['path']), reference['manifest_sha256'])
        check_out(Path(reference['path']), out)
        for doc in manifest['documents']:
            check_out(Path(doc['source']).parent, out)
        prepare_snapshot(manifest, out, snapshot)
        return load_packet(out)
    for doc in manifest['documents']:
        check_out(Path(doc['source']).parent, out)
        if 'candidate_bundle' in doc:
            _checked_bundle(Path(doc['candidate_bundle']), doc)
        if 'review_template' in doc:
            template = read_json(Path(doc['review_template']))
            template_items(template, doc, Path(doc['source']).read_bytes())
    out.mkdir(parents=True, exist_ok=True)
    if 'baseline' in manifest:
        check_out(Path(manifest['baseline']['path']), out)
        shutil.copytree(manifest['baseline']['path'], out / 'baseline')
    documents, items = [], []
    for doc in manifest['documents']:
        snapshot = InputSnapshot(Path(doc['source']))
        if snapshot.sha256 != doc['sha256']:
            raise ValueError('source changed after manifest validation')
        target = out / 'candidates' / doc['id']
        if 'candidate_bundle' in doc:
            shutil.copytree(doc['candidate_bundle'], target)
        else:
            version = pending_version(snapshot, doc['locator'])
            if doc['kind'] == 'prospectus':
                from ..document_ingest.prospectus import run_prospectus_ingestion as run
                run(snapshot, [version], input_root=snapshot.path.parent, out=target, converter=converter)
            else:
                from ..document_ingest.pipeline import run_ingestion
                run_ingestion(snapshot, [version], input_root=snapshot.path.parent, out=target,
                              classification=KINDS[doc['kind']], converter=converter)
        checked = _checked_bundle(target, doc)
        source_name = 'sources/' + doc['id'] + '.pdf'
        source_copy = out / source_name
        source_copy.parent.mkdir(exist_ok=True)
        source_copy.write_bytes(snapshot.data)
        snapshot.verify_unchanged()
        record = {k: doc[k] for k in ('id', 'kind', 'title', 'edition', 'sha256', 'locator')}
        record.update(source=source_name, candidate_bundle='candidates/' + doc['id'],
                      source_versions=[v.model_dump(mode='json') for v in checked['source_register']])
        if 'review_template' in doc:
            name = 'templates/' + doc['id'] + '.json'
            template = read_json(Path(doc['review_template']))
            write_json(out / name, template)
            record['review_template'] = name
            items.extend(template_items(template, doc, snapshot.data))
        documents.append(record)
        items.extend(_items(target, doc, checked))
    identities = {item['id'] for item in items}
    if len(identities) != len(items) or any(ref not in identities for item in items for ref in item['companions']):
        raise ValueError('duplicate review identity or missing template companion')
    artifacts = {p.relative_to(out).as_posix(): digest(p.read_bytes())
                 for p in sorted(out.rglob('*')) if p.is_file()}
    packet = {'schema_version': 'bintanong-review-packet-v1', 'candidate_only': True,
              'manifest': manifest, 'documents': documents, 'items': items, 'artifacts': artifacts}
    packet['packet_id'] = digest(encoded(packet))
    write_json(out / 'packet.json', packet)
    return load_packet(out)


def load_packet(root: Path) -> dict:
    if any(p.is_symlink() for p in (Path(root), *Path(root).absolute().parents)):
        raise ValueError('symlink packet refused')
    root = Path(root).resolve()
    packet = read_json(root / 'packet.json')
    if (not isinstance(packet, dict) or packet.get('schema_version') != 'bintanong-review-packet-v1'
            or packet.get('candidate_only') is not True):
        raise ValueError('invalid review packet')
    core = copy.deepcopy(packet)
    identity = core.pop('packet_id', None)
    if identity != digest(encoded(core)):
        raise ValueError('review packet identity mismatch')
    artifacts = packet.get('artifacts')
    if not isinstance(artifacts, dict) or not artifacts:
        raise ValueError('packet artifacts absent')
    for name, expected in artifacts.items():
        path = contained(root, name)
        try:
            actual = digest(path.read_bytes())
        except OSError as exc:
            raise ValueError('packet artifact missing') from exc
        if actual != expected:
            raise ValueError('packet artifact digest mismatch')
    snapshot = None
    if packet.get('source_basis', {}).get('kind') == 'reviewed_snapshot':
        from .snapshot import load_snapshot
        snapshot = load_snapshot(root / 'reference_snapshot', packet['manifest']['reviewed_snapshot']['manifest_sha256'])
    for doc in packet['documents']:
        if digest(contained(root, doc['source']).read_bytes()) != doc['sha256']:
            raise ValueError('packet source identity mismatch')
        if snapshot is None:
            _checked_bundle(contained(root, doc['candidate_bundle']), doc)
    if snapshot is not None:
        from .snapshot import snapshot_items
        if packet['items'] != [r for d in packet['documents'] for r in snapshot_items(snapshot, d)]:
            raise ValueError('snapshot review projection differs from its source records')
    return packet
