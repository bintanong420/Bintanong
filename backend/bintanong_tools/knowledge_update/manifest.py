from __future__ import annotations

import re
from pathlib import Path

from .files import digest, read_json

KINDS = {'handbook': 'policy_candidate', 'charter': 'charter_candidate',
         'prospectus': 'prospectus_candidate'}


def load_manifest(path: Path) -> dict:
    path = Path(path).resolve()
    value = read_json(path)
    if (not isinstance(value, dict) or value.get('schema_version') != 'bintanong-knowledge-update-v1'
            or set(value) - {'schema_version', 'documents', 'baseline', 'membership', 'build', 'reviewed_snapshot'}):
        raise ValueError('invalid knowledge-update manifest')
    docs = value.get('documents')
    if not isinstance(docs, list) or not 1 <= len(docs) <= 32:
        raise ValueError('manifest needs 1..32 documents')
    seen = set()
    for doc in docs:
        required = {'id', 'kind', 'title', 'edition', 'source', 'sha256', 'locator'}
        if (not isinstance(doc, dict) or not required <= set(doc)
                or set(doc) - required - {'candidate_bundle', 'review_template'}):
            raise ValueError('invalid document manifest fields')
        identity = doc['id']
        if (not isinstance(identity, str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', identity)
                or identity in seen or not isinstance(doc['kind'], str) or doc['kind'] not in KINDS):
            raise ValueError('invalid or duplicate document identity/kind')
        seen.add(identity)
        if any(not isinstance(doc[k], str) or not doc[k].strip()
               for k in ('title', 'edition', 'source', 'locator')):
            raise ValueError('document metadata must be explicit text')
        if not isinstance(doc['sha256'], str) or not re.fullmatch('[a-f0-9]{64}', doc['sha256']):
            raise ValueError('invalid source digest')
        for key in ('source', 'candidate_bundle', 'review_template'):
            if key not in doc:
                continue
            if not isinstance(doc[key], str) or not doc[key]:
                raise ValueError('invalid input path')
            original = path.parent / doc[key]
            if any(p.is_symlink() for p in (original, *original.parents)):
                raise ValueError('symlink inputs are refused')
            doc[key] = str(original.resolve())
        source = Path(doc['source'])
        try:
            if not source.is_file() or source.stat().st_size > 128 * 1024 * 1024:
                raise ValueError('source must be a PDF no larger than 128 MiB')
            data = source.read_bytes()
        except OSError as exc:
            raise ValueError('source missing or unreadable') from exc
        if not data.startswith(b'%PDF') or digest(data) != doc['sha256']:
            raise ValueError('source PDF identity mismatch')
    if 'reviewed_snapshot' in value:
        reference = value['reviewed_snapshot']
        if (not isinstance(reference, dict) or set(reference) != {'path', 'manifest_sha256'}
                or not isinstance(reference['path'], str) or not isinstance(reference['manifest_sha256'], str)
                or not re.fullmatch('[a-f0-9]{64}', reference['manifest_sha256'])
                or any(d['kind'] == 'prospectus' or 'candidate_bundle' in d or 'review_template' in d for d in docs)
                or 'baseline' in value or 'membership' in value):
            raise ValueError('explicit standalone reviewed snapshot reference required')
        reference['path'] = str((path.parent / reference['path']).absolute())
    if 'baseline' in value:
        baseline = value['baseline']
        if (not isinstance(baseline, dict) or set(baseline) != {'path', 'package_id'}
                or not isinstance(baseline['path'], str)):
            raise ValueError('explicit baseline path and package identity required')
        from .build import load_package
        baseline['path'] = str((path.parent / baseline['path']).absolute())
        package = load_package(Path(baseline['path']))
        if package['manifest']['package_id'] != baseline['package_id']:
            raise ValueError('baseline package identity mismatch')
    elif 'membership' in value:
        raise ValueError('membership requires an explicit verified baseline')
    return value
