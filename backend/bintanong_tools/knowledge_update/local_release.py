"""Stage a verified candidate package as an inactive draft release on the owner's local Supabase.

Owner decision, 8 November 2026: staging targets only the local stack; the hosted project
stays read-only and the hosted/local fingerprint is rerun before each local publish. This
module never activates, designates or rolls back a release, and a draft is not approval.

Order: target and client check -> package verification -> injected fingerprint check ->
read current state -> register pending source versions -> load chunks/vectors -> create the
draft -> read everything back. Each write RPC is one database transaction, so a rejected
call wrote nothing; a transport failure leaves its outcome unknown and is reported as such.
Repeat runs are safe: already-registered versions are skipped, the chunk/vector batch is an
idempotent upsert and an existing draft for the same package is reused, not recreated.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ...bintanong_storage.client import StorageError, SupabaseStorageClient
from ...bintanong_storage.config import (DEFAULT_LOCAL_ANON_KEY, DEFAULT_LOCAL_DB_URL,
                                          DEFAULT_LOCAL_SERVICE_ROLE_KEY, StorageConfig)
from ...bintanong_storage.loader import BatchKnowledgeLoader
from ...bintanong_storage.release import ReleaseManager
from ...bintanong_storage.source_registration import SourceRegistrationLoader
from .build import load_package
from .verify import verify

# Exact string only. "localhost" is refused because the hosts file or an IPv6 listener can
# send it elsewhere; other ports belong to the local database, the retired scratch stack or
# unrelated services.
LOCAL_TARGET = 'http://127.0.0.1:54321'
KEY_ENV = 'BINTANONG_LOCAL_SERVICE_ROLE_KEY'
ANON_ENV = 'BINTANONG_LOCAL_ANON_KEY'
_LABEL = re.compile(r'[a-z0-9][a-z0-9._-]{2,99}')
_IDENTITY = re.compile(r'[A-Za-z0-9._:/-]+')  # safe inside a PostgREST in.(...) list
_PAGE = 500


class LocalReleaseError(Exception):
    """Refusal or failure; `written` states what reached the local database."""

    def __init__(self, message: str, written: dict | None = None):
        super().__init__(message)
        self.written = dict(written or {})


def check_target(target_url) -> None:
    if target_url != LOCAL_TARGET:
        raise LocalReleaseError(f'refused target: only local Supabase {LOCAL_TARGET} may be written; '
                                'hosted stays read-only (owner, 8 Nov 2026)')


@dataclass(frozen=True)
class _LocalConfig(StorageConfig):
    anon_key: str = field(repr=False)
    service_role_key: str = field(repr=False)


def local_client(target_url) -> SupabaseStorageClient:
    """Client bound to the local stack. The key comes from BINTANONG_LOCAL_SERVICE_ROLE_KEY
    (default: the Supabase CLI local demo key), never from SUPABASE_SERVICE_ROLE_KEY, which
    may hold the hosted key."""
    check_target(target_url)
    return SupabaseStorageClient(_LocalConfig(api_url=LOCAL_TARGET,
        anon_key=os.environ.get(ANON_ENV, DEFAULT_LOCAL_ANON_KEY),
        service_role_key=os.environ.get(KEY_ENV, DEFAULT_LOCAL_SERVICE_ROLE_KEY), db_url=DEFAULT_LOCAL_DB_URL),
        trust_env=False)


def fingerprint_script_check(script: Path, report: Path, *, run=subprocess.run):
    """Adapter for the read-only hosted/local fingerprint script; returns a fresh report each call."""
    def check():
        Path(report).unlink(missing_ok=True)
        run([sys.executable, '-I', str(script), str(report)], check=True, capture_output=True, timeout=1800)
        return json.loads(Path(report).read_text(encoding='utf-8'))
    return check


def _secrets(client) -> list[str]:
    config = getattr(client, 'config', None)
    return [s for s in (getattr(config, 'service_role_key', None), getattr(config, 'anon_key', None)) if s]


def _reason(exc: Exception, client) -> str:
    text = f'{type(exc).__name__}: {exc}'
    for secret in _secrets(client):
        text = text.replace(secret, '[redacted]')
    return text


def _summary(written: dict) -> str:
    versions = written.get('registered_versions') or 'none'
    return (f"Written so far: registered versions {versions} (registration {written['registration']}); "
            f"chunk/vector batch {written['artifacts']}; draft release {written['release']}. "
            'Nothing was activated (not activated).')


def _write(client, written: dict, key: str, action: str, fn):
    try:
        return fn()
    except ValueError as exc:
        state, reason = 'not_written', _reason(exc, client)
    except StorageError as exc:
        state = 'not_written' if exc.status_code is not None else 'unknown'
        reason = _reason(exc, client)
    except Exception as exc:  # unexpected failure: the write may or may not have committed
        state, reason = 'unknown', _reason(exc, client)
    written[key] = state
    raise LocalReleaseError(f'{action} failed ({reason}). {_summary(written)}', written) from None


def _in(values) -> str:
    return 'in.(' + ','.join(f'"{v}"' for v in values) + ')'


def _paged(client, table: str, columns: str, filters: dict, order: str) -> list[dict]:
    rows, offset = [], 0
    while True:
        batch = client.select(table, columns=columns, role='admin',
                              filters={**filters, 'order': order + '.asc', 'limit': str(_PAGE), 'offset': str(offset)})
        rows += batch
        if len(batch) < _PAGE:
            return rows
        offset += _PAGE


def _active(client):
    rows = client.select('active_release', columns='release_id', role='admin')
    return rows[0]['release_id'] if rows else None


def _require_same(report) -> None:
    if (not isinstance(report, Mapping) or not report
            or any(not isinstance(v, Mapping) or v.get('same') is not True for v in report.values())):
        raise LocalReleaseError('hosted/local fingerprint does not report every table equal; '
                                'refusing to write until hosted and local match')


def _existing_release(client, label: str, release_version: str, set_id: str):
    rows = client.select('knowledge_releases', columns='release_id,release_version,status,embedding_set_id',
                         filters={'release_id': 'eq.' + label}, role='admin')
    rows += client.select('knowledge_releases', columns='release_id,release_version,status,embedding_set_id',
                          filters={'release_version': 'eq.' + release_version}, role='admin')
    found = {r['release_id']: r for r in rows}
    if not found:
        return None
    row = found.get(label)
    if len(found) > 1 or row is None or row['release_version'] != release_version or row['embedding_set_id'] != set_id:
        raise LocalReleaseError(f'release label {label!r} or this package is already used by another release')
    if row['status'] != 'draft':
        raise LocalReleaseError(f"release {label!r} already exists with status {row['status']!r}, not a draft; "
                                'staging never changes a published release')
    return row


def _read_back(client, package: dict, label: str, release_version: str, set_id: str, active_before, written: dict):
    chunk_ids = [c['chunk_id'] for c in package['chunks']]
    version_ids = [v['version_id'] for v in package['sources']]

    def fail(problem):
        raise LocalReleaseError(f'read-back mismatch: {problem}. {_summary(written)}', written)

    rows = client.select('knowledge_releases', role='admin', filters={'release_id': 'eq.' + label},
        columns='release_id,release_version,status,embedding_set_id,expected_chunk_count,'
                'expected_document_version_count,expected_rule_count')
    if len(rows) != 1:
        fail('draft release row not found')
    row = rows[0]
    if row['status'] != 'draft':
        fail(f"release is not a draft (status {row['status']!r})")
    if row['release_version'] != release_version or row['embedding_set_id'] != set_id:
        fail('release package/embedding-set identity differs')
    if (row['expected_chunk_count'], row['expected_document_version_count'], row['expected_rule_count']) != (
            len(chunk_ids), len(version_ids), 0):
        fail('release expected counts differ from the package')
    members = {r['chunk_id'] for r in _paged(client, 'release_chunks', 'chunk_id', {'release_id': 'eq.' + label}, 'chunk_id')}
    if members != set(chunk_ids):
        fail('release chunk membership differs from the package')
    versions = {r['version_id'] for r in _paged(client, 'release_document_versions', 'version_id',
                                                {'release_id': 'eq.' + label}, 'version_id')}
    if versions != set(version_ids):
        fail('release document version membership differs from the package')
    expected = {c['chunk_id']: c['content_hash'] for c in package['chunks']}
    vectors = {r['chunk_id']: r['chunk_content_hash'] for r in _paged(client, 'chunk_embeddings',
        'chunk_id,chunk_content_hash', {'embedding_set_id': 'eq.' + set_id}, 'chunk_id')}
    if vectors != expected:
        fail(f'stored embeddings ({len(vectors)}) differ from the package ({len(expected)})')
    stored = {r['chunk_id']: r['content_hash'] for r in _paged(client, 'chunks', 'chunk_id,content_hash',
                                                               {'version_id': _in(version_ids)}, 'chunk_id')}
    if any(stored.get(k) != h for k, h in expected.items()):
        fail('stored chunks differ from the package')
    after = _active(client)
    if after != active_before:
        fail(f'active release changed from {active_before!r} to {after!r}')
    return len(members), len(vectors), len(versions)


def stage_draft(package_path, *, client, target_url, fingerprint_check, release_label: str, actor: str,
                documents: list[dict], packet_root=None) -> dict:
    """Stage one package as an inactive draft. `documents` is the explicit storage metadata
    (document_id, namespace, synthetic, document_category, title) for every package source
    document; the storage category is never inferred from the package."""
    check_target(target_url)
    if getattr(client, 'base_url', None) != LOCAL_TARGET + '/rest/v1':
        raise LocalReleaseError('refused: the storage client is not bound to the local target')
    if not isinstance(release_label, str) or not _LABEL.fullmatch(release_label):
        raise LocalReleaseError('release label must be 3-100 lowercase letters, digits, ".", "_" or "-"')
    if not isinstance(actor, str) or not actor.strip() or len(actor) > 120 or not actor.isprintable():
        raise LocalReleaseError('an explicit single-line actor name is required')
    if (not isinstance(documents, list) or not documents
            or any(not isinstance(d, dict) or 'document_id' not in d for d in documents)):
        raise LocalReleaseError('explicit storage document metadata is required')

    root = Path(package_path).resolve()
    try:
        report = verify(root, packet_root=packet_root)
        package = load_package(root)
    except (ValueError, OSError) as exc:
        raise LocalReleaseError(f'package verification failed: {exc}') from exc
    if report.get('candidate_only') is not True or report.get('activation_eligible') is not False:
        raise LocalReleaseError('package verification failed: not an inactive candidate package')
    package_id = package['manifest']['package_id']
    set_id = package['embedding_manifest']['embedding_set_id']
    sources, chunk_ids = package['sources'], [c['chunk_id'] for c in package['chunks']]
    version_ids = [v['version_id'] for v in sources]
    if any(not _IDENTITY.fullmatch(i) for i in version_ids):
        raise LocalReleaseError('package source version identities are not safe to query')
    if {d['document_id'] for d in documents} != {v['document_id'] for v in sources} or len(documents) != len(
            {d['document_id'] for d in documents}):
        raise LocalReleaseError('storage document metadata must match the package source documents exactly')

    try:
        same = fingerprint_check()
    except Exception as exc:  # the check is injected; any failure means "not proven equal"
        raise LocalReleaseError(f'fingerprint check failed ({type(exc).__name__}); refusing to write') from None
    _require_same(same)

    release_version = 'package-' + package_id
    try:
        active_before = _active(client)
        existing = _existing_release(client, release_label, release_version, set_id)
        registered = {r['version_id']: r for r in _paged(client, 'document_versions',
            'version_id,document_id,byte_sha256', {'version_id': _in(version_ids)}, 'version_id')}
    except StorageError as exc:
        raise LocalReleaseError(f'local read failed before any write ({_reason(exc, client)})') from None
    for version in sources:
        prior = registered.get(version['version_id'])
        if prior and (prior['byte_sha256'], prior['document_id']) != (version['byte_sha256'], version['document_id']):
            raise LocalReleaseError(f"registered version {version['version_id']} conflicts with the package source")

    written = {'registration': 'not_attempted', 'registered_versions': [], 'artifacts': 'not_attempted',
               'release': 'not_attempted'}
    new = [v for v in sources if v['version_id'] not in registered]
    if new:
        wanted = {v['document_id'] for v in new}
        _write(client, written, 'registration', 'registering pending source versions',
               lambda: SourceRegistrationLoader(client).load_versions(new, [d for d in documents if d['document_id'] in wanted]))
        written.update(registration='registered', registered_versions=[v['version_id'] for v in new])
    else:
        written['registration'] = 'already_registered'

    summary = _write(client, written, 'artifacts', 'loading package chunks/vectors',
        lambda: BatchKnowledgeLoader(client).load_artifacts(root / 'embedding_manifest.json',
                                                            root / 'embeddings.jsonl', chunks=package['chunks']))
    written['artifacts'] = 'loaded'
    if (summary.embedding_set_id, summary.total_chunks_loaded, summary.total_embeddings_loaded) != (
            set_id, len(chunk_ids), len(chunk_ids)):
        raise LocalReleaseError(f'loader summary differs from the package. {_summary(written)}', written)

    if existing is None:
        description = (f'Local candidate draft of package {package_id}, staged by {actor.strip()}; '
                       'inactive, not institutional approval')
        _write(client, written, 'release', 'creating the draft release',
               lambda: ReleaseManager(client).create_release(release_label, release_version, description,
                                                             set_id, chunk_ids, version_ids, ()))
        written['release'] = 'created'
    else:
        written['release'] = 'already_staged'

    chunks, embeddings, versions = _read_back(client, package, release_label, release_version, set_id,
                                              active_before, written)
    return {'staged': True, 'created': existing is None, 'release_id': release_label,
            'release_version': release_version, 'package_id': package_id, 'embedding_set_id': set_id,
            'status': 'draft', 'chunks': chunks, 'embeddings': embeddings, 'document_versions': versions,
            'registered_versions': written['registered_versions'],
            'already_registered_versions': [i for i in version_ids if i in registered],
            'loader': asdict(summary), 'active_release_id': active_before, 'target': LOCAL_TARGET,
            'actor': actor.strip(), 'candidate_only': True, 'activation_eligible': False}
