"""Researcher upload -> one checked manifest folder (owner GUI intake plan, 11 Nov 2026).

Each upload gets its own folder with sibling original/, manifest.json and upload.json, so `prepare` can later write
packet/ beside the original (check_out refuses outputs inside the originals). The server picks the id and the file
name; the client's file name is never used. Office and audience are notes only: audience stays a per-item review
decision. Nothing here approves content.
"""
from __future__ import annotations

import os
import re
import secrets
import subprocess
import threading
from pathlib import Path

from .files import digest, read_json, write_json

MAX_UPLOAD = 128 * 1024 * 1024  # same ceiling load_manifest enforces
KINDS = ('handbook', 'charter')  # prospectus needs the ledger path (U1), not this intake
TEXT_LIMIT = 300
REPO = Path(__file__).resolve().parents[3]
# ponytail: process handles live in this server's memory; after a restart a running job reads as interrupted
_jobs: dict[str, subprocess.Popen] = {}
_jobs_lock = threading.Lock()


def _text(name: str, value, *, required: bool) -> str:
    if not isinstance(value, str) or len(value) > TEXT_LIMIT or (required and not value.strip()):
        raise ValueError(f'{name} must be text of at most {TEXT_LIMIT} characters')
    return value.strip()


def _workspace(workspace: Path) -> Path:
    workspace = Path(workspace).absolute()
    if any((p / '.git').exists() for p in (workspace, *workspace.parents)):
        raise ValueError('upload workspace is inside a Git checkout; use ignored workspace audit-evidence')
    if any(p.is_symlink() for p in (workspace, *workspace.parents)):
        raise ValueError('symlinked upload workspace refused')
    return workspace


def create_upload(workspace: Path, data: bytes, *, kind: str, title: str, edition: str,
                  office: str = '', audience: str = '') -> dict:
    workspace = _workspace(workspace)
    if kind not in KINDS:
        raise ValueError('kind must be handbook or charter')
    title, edition = _text('title', title, required=True), _text('edition', edition, required=True)
    office, audience = _text('office', office, required=False), _text('audience', audience, required=False)
    if len(data) > MAX_UPLOAD:
        raise ValueError('upload exceeds 128 MiB')
    if not data.startswith(b'%PDF'):
        raise ValueError('upload is not a PDF')
    upload_id, sha256 = secrets.token_hex(8), digest(data)
    folder = workspace / upload_id
    (folder / 'original').mkdir(parents=True)
    (folder / 'original/source.pdf').write_bytes(data)
    write_json(folder / 'manifest.json', {'schema_version': 'bintanong-knowledge-update-v1', 'documents': [{
        'id': upload_id, 'kind': kind, 'title': title, 'edition': edition, 'source': 'original/source.pdf',
        'sha256': sha256, 'locator': 'researcher-upload:' + upload_id}]})
    write_json(folder / 'upload.json', {'upload_id': upload_id, 'kind': kind, 'title': title, 'edition': edition,
        'office': office, 'audience_note': audience, 'sha256': sha256, 'bytes': len(data), 'candidate_only': True})
    return {'upload_id': upload_id, 'sha256': sha256}


def build_plan(session) -> dict:
    """What the build form needs: each reading's pending fields and the held-back items, before build is called."""
    export = session.export()
    readings = []
    for row in export['readings']:
        pending = [f['name'] for f in row['fields'] if f['decision'] == 'pending']
        readings.append({'reading_id': row['reading_id'], 'fields': [f['name'] for f in row['fields']],
                         'pending_fields': pending, 'ready': not pending,
                         'intended_audience': row['intended_audience']})
    return {'packet_id': export['packet_id'], 'revision': export['revision'], 'readings': readings,
            'withheld_items': export['withheld_items'], 'required_readings': export['required_readings']}


def _rows(value, keys: set, name: str) -> list:
    if not isinstance(value, list) or not value or any(not isinstance(r, dict) or set(r) != keys for r in value):
        raise ValueError(f'{name} must be a non-empty list of {sorted(keys)}')
    return value


def save_build_metadata(session, form) -> dict:
    """Write build's --metadata for the current review revision; build itself re-checks every binding."""
    if not isinstance(form, dict) or set(form) != {'reading_ids', 'assignments', 'claim_reviews'}:
        raise ValueError('build form needs reading_ids, assignments and claim_reviews only')
    plan = build_plan(session)
    known = {r['reading_id']: r for r in plan['readings']}
    selected = form['reading_ids']
    if not isinstance(selected, list) or not selected or any(not isinstance(i, str) for i in selected):
        raise ValueError('reading_ids must be a non-empty list of text')
    if unknown := [i for i in selected if i not in known]:
        raise ValueError('readings not in this review: ' + ', '.join(unknown))
    if pending := [i for i in selected if not known[i]['ready']]:
        raise ValueError('readings still have pending fields: ' + ', '.join(pending))
    # basis_ref is set here, from the reviewer running this session, never from the form
    basis = 'researcher-review:' + session.reviewer
    assignments = [{**r, 'basis_ref': basis} for r in _rows(form['assignments'], {'reading_id', 'subject_id'}, 'assignments')]
    reviews = [{**r, 'basis_ref': basis} for r in _rows(form['claim_reviews'],
               {'subject_id', 'claim', 'finding', 'field_refs', 'basis_reading_id'}, 'claim_reviews')]
    path = session.root / 'review/build-metadata.json'
    write_json(path, {'packet_id': plan['packet_id'], 'revision': plan['revision'],
                      'build': {'reading_ids': selected, 'assignments': assignments, 'claim_reviews': reviews}})
    return {'path': 'review/build-metadata.json', 'revision': plan['revision']}


def _upload(workspace: Path, upload_id) -> Path:
    if not isinstance(upload_id, str) or not re.fullmatch(r'[0-9a-f]{16}', upload_id):
        raise ValueError('invalid upload id')
    folder = _workspace(workspace) / upload_id
    if not (folder / 'upload.json').is_file():
        raise ValueError('unknown upload')
    return folder


def start_prepare(workspace: Path, upload_id, *, python: str, assist: bool = False, runner=subprocess.Popen) -> dict:
    """Run the existing `knowledge_update prepare` for one upload; Docling needs the p12 venv's interpreter."""
    folder = _upload(workspace, upload_id)
    if not Path(python).is_file():
        raise ValueError('configured Docling interpreter not found: ' + str(python))
    if assist and not (os.environ.get('BINTANONG_ASSIST_URL') and os.environ.get('BINTANONG_ASSIST_MODEL')):
        raise ValueError('Gemma audit needs BINTANONG_ASSIST_URL and BINTANONG_ASSIST_MODEL for a running local '
                         'vision server; upload without the audit or start it first')
    with _jobs_lock:
        running = _jobs.get(upload_id)
        if running is not None and running.poll() is None:
            raise ValueError('prepare is already running for this upload')
        if (folder / 'packet').exists():
            raise ValueError('this upload already has a packet; a different audit choice needs a new upload')
        argv = [str(python), '-m', 'backend.bintanong_tools.knowledge_update', 'prepare',
                str(folder / 'manifest.json'), '--out', str(folder / 'packet')]
        if assist:
            argv += ['--assist-mode', 'flagged']
        with (folder / 'prepare.log').open('wb') as log:
            _jobs[upload_id] = runner(argv, cwd=REPO, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        write_json(folder / 'job.json', {'state': 'running', 'assist': assist})
    return prepare_status(workspace, upload_id)


def prepare_status(workspace: Path, upload_id) -> dict:
    folder = _upload(workspace, upload_id)
    job = read_json(folder / 'job.json') if (folder / 'job.json').is_file() else {'state': 'not_started'}
    if job['state'] == 'running':
        with _jobs_lock:
            process = _jobs.get(upload_id)
        code = None if process is None else process.poll()
        if process is None:
            job = {**job, 'state': 'interrupted'}
        elif code is not None:
            job = {**job, 'state': 'done' if code == 0 else 'failed', 'exit_code': code}
            if code == 0 and (folder / 'packet/packet.json').is_file():
                items = read_json(folder / 'packet/packet.json')['items']
                job['gemma_unavailable_fields'] = sum(f.get('assistance', {}).get('outcome') == 'failed'
                                                      for row in items for f in row['fields'])
        if job['state'] != 'running':
            write_json(folder / 'job.json', job)
    log = folder / 'prepare.log'
    tail = log.read_text(encoding='utf-8', errors='replace').splitlines()[-20:] if log.is_file() else []
    return {**job, 'upload_id': upload_id, 'log_tail': tail}


def list_uploads(workspace: Path) -> list[dict]:
    workspace = _workspace(workspace)
    if not workspace.is_dir():
        return []
    rows = []
    for note in sorted(workspace.glob('*/upload.json')):
        try:
            rows.append(read_json(note))
        except ValueError:
            continue  # a half-written or foreign folder is not an upload
    return rows
