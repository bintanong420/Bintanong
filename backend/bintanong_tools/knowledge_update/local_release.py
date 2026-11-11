"""Stage, activate and roll back candidate releases on the owner's local Supabase only.

Owner decision, 8 November 2026: writes target only the local stack; the hosted project
stays read-only and the hosted/local fingerprint (freeze rule) is rerun before each local
write. stage_draft never activates; activate_draft/rollback_to act only on an explicit owner
authorization reference. Local activation is research use, not institutional approval.

Staging order: target and client check -> package verification -> injected fingerprint check ->
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


def _check_client(target_url, client) -> None:
    check_target(target_url)
    if getattr(client, 'base_url', None) != LOCAL_TARGET + '/rest/v1':
        raise LocalReleaseError('refused: the storage client is not bound to the local target')


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


def _write(client, written: dict, key: str, action: str, fn, summary=_summary):
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
    raise LocalReleaseError(f'{action} failed ({reason}). {summary(written)}', written) from None


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


def _is_report(report) -> bool:
    return (isinstance(report, Mapping) and bool(report) and all(
        isinstance(v, Mapping) and isinstance(v.get('same'), bool) for v in report.values()))


def _side(row, side):
    return row.get(side + '_sha256'), row.get(side + '_rows')


def _require_consistent(report, baseline) -> None:
    """Freeze rule (owner, 11 Nov 2026): every table equal, or both sides unchanged since the
    baseline this tool wrote after its own last successful write."""
    if not _is_report(report):
        raise LocalReleaseError('fingerprint report is malformed; refusing to write')
    if all(v['same'] is True for v in report.values()):
        return
    if baseline is None:
        raise LocalReleaseError('hosted/local fingerprint does not report every table equal and no '
                                'baseline exists; refusing to write until hosted and local match')
    if set(report) != set(baseline):
        raise LocalReleaseError('fingerprint table set differs from the baseline; refusing to write')
    for side, why in (('hosted', 'hosted changed since the baseline'),
                      ('local', 'local changed since the baseline (another writer?)')):
        moved = [t for t in report if _side(report[t], side) != _side(baseline[t], side)
                 or _side(report[t], side) == (None, None)]
        if moved:
            raise LocalReleaseError(f'fingerprint: {why} in {", ".join(sorted(moved))}; refusing to write')


_POINTER = 'fingerprint-baseline.json'
_BASELINE_SCHEMA = 'bintanong-fingerprint-baseline-v1'
_RELEASE_ID = re.compile(r'[A-Za-z0-9._-]{1,100}')


def _baseline_root(baseline_dir) -> Path:
    if baseline_dir is None:
        raise LocalReleaseError('an explicit baseline directory outside Git is required')
    root = Path(baseline_dir).resolve()
    if any((p / '.git').exists() for p in (root, *root.parents)):
        raise LocalReleaseError('refused: the baseline directory is inside a Git checkout; keep it in ignored evidence')
    return root


def _load_baseline(root: Path):
    pointer = root / _POINTER
    if not pointer.exists():
        return None
    try:
        data = json.loads(pointer.read_text(encoding='utf-8'))
        rid = data['release_id']
        if (data.get('schema_version') != _BASELINE_SCHEMA or not isinstance(rid, str)
                or not _RELEASE_ID.fullmatch(rid) or data.get('report') != f'fingerprint-after-{rid}.json'):
            raise ValueError
        report = json.loads((root / data['report']).read_text(encoding='utf-8'))
    except (ValueError, TypeError, KeyError, OSError):
        raise LocalReleaseError('fingerprint baseline is malformed or foreign; refusing to write') from None
    if not _is_report(report):
        raise LocalReleaseError('fingerprint baseline report is malformed; refusing to write')
    return report


def _write_baseline(root: Path, release_id: str, report, **record) -> None:
    root.mkdir(parents=True, exist_ok=True)
    name = f'fingerprint-after-{release_id}.json'
    for path, data in ((root / name, report), (root / _POINTER, {'schema_version': _BASELINE_SCHEMA,
                        'release_id': release_id, 'report': name, **record})):
        tmp = path.with_suffix('.tmp')
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding='utf-8')
        os.replace(tmp, path)


def _run_fingerprint(fingerprint_check, written=None):
    try:
        return fingerprint_check()
    except Exception as exc:  # the check is injected; any failure means "not proven equal"
        raise LocalReleaseError(f'fingerprint check failed ({type(exc).__name__}); refusing to write'
                                if written is None else f'post-write fingerprint check failed '
                                f'({type(exc).__name__}); baseline not refreshed', written) from None


def _refresh_baseline(root, release_id, before, fingerprint_check, written, **record) -> None:
    """Capture the post-write report; hosted must not have moved while this tool wrote locally."""
    after = _run_fingerprint(fingerprint_check, written)
    if not _is_report(after) or set(after) != set(before) or any(
            _side(after[t], 'hosted') != _side(before[t], 'hosted') for t in after):
        raise LocalReleaseError('post-write fingerprint shows hosted changed or is malformed; baseline not '
                                'refreshed. Inspect before the next write.', written)
    _write_baseline(root, release_id, after, **record)


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
        raise LocalReleaseError(f'read-back mismatch: active release changed from {active_before!r} to {after!r} '
                                'during staging; this module did not request it. Inspect the local stack.', written)
    return len(members), len(vectors), len(versions)


def stage_draft(package_path, *, client, target_url, fingerprint_check, release_label: str, actor: str,
                documents: list[dict], baseline_dir, packet_root=None) -> dict:
    """Stage one package as an inactive draft. `documents` is the explicit storage metadata
    (document_id, namespace, synthetic, document_category, title) for every package source
    document; the storage category is never inferred from the package. After success the
    post-write fingerprint becomes the freeze baseline in `baseline_dir` (outside Git)."""
    _check_client(target_url, client)
    base = _baseline_root(baseline_dir)
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

    baseline = _load_baseline(base)
    before = _run_fingerprint(fingerprint_check)
    _require_consistent(before, baseline)

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
    _refresh_baseline(base, release_label, before, fingerprint_check, written, action='stage', actor=actor.strip())
    return {'staged': True, 'created': existing is None, 'release_id': release_label,
            'release_version': release_version, 'package_id': package_id, 'embedding_set_id': set_id,
            'status': 'draft', 'chunks': chunks, 'embeddings': embeddings, 'document_versions': versions,
            'registered_versions': written['registered_versions'],
            'already_registered_versions': [i for i in version_ids if i in registered],
            'loader': asdict(summary), 'active_release_id': active_before, 'target': LOCAL_TARGET,
            'actor': actor.strip(), 'candidate_only': True, 'activation_eligible': False}


CHECKS_SCHEMA = 'bintanong-draft-checks-v1'
_RESEARCH_REF = re.compile(r'research-owner-[0-9]{8}')  # the phase-9 migration's accepted format
_RELEASE_COLUMNS = ('release_id,release_version,status,embedding_set_id,published_at,review_scope_id,'
                    'release_kind,research_authorization_ref')


def _require_line(value, what: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 200 or not value.isprintable():
        raise LocalReleaseError(f'an explicit single-line {what} is required')
    return value.strip()


def _load_checks(path, package: dict) -> dict:
    """Draft-checks report (5b contract) bound to this exact package's bytes."""
    try:
        report = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        raise LocalReleaseError('checks report is missing or unreadable; refusing to activate') from None
    manifest = package['manifest']
    if not isinstance(report, dict) or report.get('schema_version') != CHECKS_SCHEMA:
        raise LocalReleaseError(f'checks report is not a {CHECKS_SCHEMA} report; refusing to activate')
    if report.get('passed') is not True:
        raise LocalReleaseError('checks report did not pass; refusing to activate')
    cases = report.get('cases')
    if (not isinstance(cases, list) or not cases
            or any(not isinstance(c, dict) or c.get('passed') is not True for c in cases)):
        raise LocalReleaseError('checks report has no cases or a failed case; refusing to activate')
    if not isinstance(report.get('created_at'), str) or not report['created_at']:
        raise LocalReleaseError('checks report has no creation time; refusing to activate')
    if report.get('package_id') != manifest['package_id']:
        raise LocalReleaseError('checks report package_id differs from the draft package; refusing to activate')
    binding = report.get('package_binding')
    if not isinstance(binding, dict):
        raise LocalReleaseError('checks report has no package_binding; refusing to activate')
    files = manifest['files']
    expected = {'package_id': manifest['package_id'], 'chunks_sha256': files['chunks.jsonl'],
                'embeddings_sha256': files['embeddings.jsonl'],
                'embedding_manifest_sha256': files['embedding_manifest.json'],
                'embedding_set_id': package['embedding_manifest']['embedding_set_id']}
    for name, value in expected.items():
        if binding.get(name) != value:
            raise LocalReleaseError(f'checks report package_binding.{name} differs from the package; '
                                    'refusing to activate')
    return report


def _release_row(client, release_id):
    rows = client.select('knowledge_releases', columns=_RELEASE_COLUMNS,
                         filters={'release_id': 'eq.' + release_id}, role='admin')
    return rows[0] if rows else None


def _preflight(client, target_url, authorization_ref, actor, baseline_dir):
    _check_client(target_url, client)
    ref = _require_line(authorization_ref, 'owner authorization reference')
    who = _require_line(actor, 'actor name')
    return ref, who, _baseline_root(baseline_dir)


def _frozen(base, fingerprint_check):
    baseline = _load_baseline(base)
    before = _run_fingerprint(fingerprint_check)
    _require_consistent(before, baseline)
    return before


def _activation_summary(written: dict) -> str:
    return (f"Written so far: research designation {written.get('designation', 'not_attempted')}; "
            f"activation {written.get('activation', 'not_attempted')}; "
            f"rollback {written.get('rollback', 'not_attempted')}.")


def _confirm_active(client, release_id, written, what):
    try:
        row, now = _release_row(client, release_id), _active(client)
    except (ValueError, StorageError) as exc:  # StorageError text can carry transport details; redact it
        raise LocalReleaseError(f'read-back failed after {what}: {_reason(exc, client)}. '
                                f'{_activation_summary(written)} Inspect the local stack.', written) from None
    if now != release_id or not row or row['status'] != 'active':
        raise LocalReleaseError(f'read-back mismatch after {what}: active release is {now!r}, release '
                                f'{release_id!r} status {row and row["status"]!r}. {_activation_summary(written)} '
                                'Inspect the local stack.', written)


def activate_draft(release_id, *, client, target_url, package_path, checks_report, authorization_ref, actor,
                   fingerprint_check, baseline_dir) -> dict:
    """Activate a draft this tool staged from `package_path`, after its draft checks passed.
    `authorization_ref` is the owner's reference; it is recorded, and a draft bound to a selected
    review is designated research with it first, as validate_release requires."""
    ref, who, base = _preflight(client, target_url, authorization_ref, actor, baseline_dir)
    if not isinstance(release_id, str) or not _RELEASE_ID.fullmatch(release_id):
        raise LocalReleaseError('release id is not a valid release label')
    try:
        package = load_package(Path(package_path).resolve())
    except (ValueError, OSError) as exc:
        raise LocalReleaseError(f'package verification failed: {exc}') from None
    _load_checks(checks_report, package)
    package_id = package['manifest']['package_id']
    before = _frozen(base, fingerprint_check)
    try:
        row = _release_row(client, release_id)
        previous = _active(client)
    except StorageError as exc:
        raise LocalReleaseError(f'local read failed before any write ({_reason(exc, client)})') from None
    if row is None:
        raise LocalReleaseError(f'release {release_id!r} not found')
    if row['release_version'] != 'package-' + package_id:
        raise LocalReleaseError(f'release {release_id!r} was not staged by this tool from this package')
    if row['status'] != 'draft' or row.get('published_at') or previous == release_id:
        raise LocalReleaseError(f"release {release_id!r} is not an unpublished draft (status {row['status']!r}); "
                                'nothing to activate')
    if row['embedding_set_id'] != package['embedding_manifest']['embedding_set_id']:
        raise LocalReleaseError('the draft embedding set differs from the package embedding set')
    designate = bool(row.get('review_scope_id')) and row.get('release_kind') != 'research'
    if (designate or row.get('release_kind') == 'research') and not _RESEARCH_REF.fullmatch(ref):
        raise LocalReleaseError('a research designation needs an owner authorization reference of the form '
                                'research-owner-YYYYMMDD')
    if row.get('release_kind') == 'research' and row.get('research_authorization_ref') != ref:
        raise LocalReleaseError('the draft already carries a different research authorization reference')

    written = {'designation': 'not_needed', 'activation': 'not_attempted'}
    manager, stamp = ReleaseManager(client), f'{who} [{ref}]'
    if designate:
        written['designation'] = 'not_attempted'
        _write(client, written, 'designation', 'designating the research release',
               lambda: manager.designate_research_release(release_id, ref), _activation_summary)
        written['designation'] = 'designated'
    _write(client, written, 'activation', 'activating the draft',
           lambda: manager.activate_release(release_id, stamp), _activation_summary)
    written['activation'] = 'requested'
    _confirm_active(client, release_id, written, 'activation')
    written['activation'] = 'active'
    _refresh_baseline(base, release_id, before, fingerprint_check, written, action='activate',
                      actor=who, authorization_ref=ref, previous_active_release_id=previous)
    return {'activated': True, 'release_id': release_id, 'package_id': package_id,
            'active_release_id': release_id, 'previous_active_release_id': previous,
            'designated_research': designate, 'authorization_ref': ref, 'actor': who, 'target': LOCAL_TARGET}


def rollback_to(release_id, *, client, target_url, authorization_ref, actor, fingerprint_check,
                baseline_dir) -> dict:
    """Point the local active release back to a previously published (superseded) release."""
    ref, who, base = _preflight(client, target_url, authorization_ref, actor, baseline_dir)
    if not isinstance(release_id, str) or not _RELEASE_ID.fullmatch(release_id):
        raise LocalReleaseError('release id is not a valid release label')
    before = _frozen(base, fingerprint_check)
    try:
        row = _release_row(client, release_id)
        previous = _active(client)
    except StorageError as exc:
        raise LocalReleaseError(f'local read failed before any write ({_reason(exc, client)})') from None
    if row is None:
        raise LocalReleaseError(f'release {release_id!r} not found')
    if previous == release_id or row['status'] == 'active':
        raise LocalReleaseError(f'release {release_id!r} is already active; nothing to roll back')
    if row['status'] != 'superseded' or not row.get('published_at'):
        raise LocalReleaseError(f"only a previously published release can be restored (status {row['status']!r})")
    written = {'rollback': 'not_attempted'}
    _write(client, written, 'rollback', 'rolling back',
           lambda: ReleaseManager(client).rollback_release(release_id, f'{who} [{ref}]'), _activation_summary)
    written['rollback'] = 'requested'
    _confirm_active(client, release_id, written, 'rollback')
    written['rollback'] = 'active'
    _refresh_baseline(base, release_id, before, fingerprint_check, written, action='rollback',
                      actor=who, authorization_ref=ref, previous_active_release_id=previous)
    return {'rolled_back': True, 'release_id': release_id, 'active_release_id': release_id,
            'previous_active_release_id': previous, 'authorization_ref': ref, 'actor': who, 'target': LOCAL_TARGET}
