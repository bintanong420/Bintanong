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
        # one run per upload: an orphan from a closed server may still be writing packet/, so a retry is a new upload
        if (folder / 'job.json').exists() or (folder / 'packet').exists():
            raise ValueError('prepare already ran for this upload; a retry or different audit choice needs a new upload')
        argv = [str(python), '-m', 'backend.bintanong_tools.knowledge_update', 'prepare',
                str(folder / 'manifest.json'), '--out', str(folder / 'packet')]
        if assist:
            argv += ['--assist-mode', 'flagged']
        with (folder / 'prepare.log').open('wb') as log:
            _jobs[upload_id] = runner(argv, cwd=REPO, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        write_json(folder / 'job.json', {'state': 'running', 'assist': assist})
    return prepare_status(workspace, upload_id)


def _polled(key: str, job: dict) -> dict:
    """A running job's state from its in-memory process: interrupted when this server never started it."""
    if job['state'] != 'running':
        return job
    with _jobs_lock:
        process = _jobs.get(key)
    code = None if process is None else process.poll()
    if process is None:
        return {**job, 'state': 'interrupted'}
    if code is not None:
        return {**job, 'state': 'done' if code == 0 else 'failed', 'exit_code': code}
    return job


def _tail(path: Path) -> list[str]:
    return path.read_text(encoding='utf-8', errors='replace').splitlines()[-20:] if path.is_file() else []


def prepare_status(workspace: Path, upload_id) -> dict:
    folder = _upload(workspace, upload_id)
    job = read_json(folder / 'job.json') if (folder / 'job.json').is_file() else {'state': 'not_started'}
    if job['state'] == 'running':
        job = _polled(upload_id, job)
        if job['state'] != 'running':
            code = job.get('exit_code')
            if code == 0:
                try:
                    items = read_json(folder / 'packet/packet.json')['items']
                    job['gemma_unavailable_fields'] = sum(f.get('assistance', {}).get('outcome') == 'failed'
                                                          for row in items for f in row['fields'])
                except (ValueError, KeyError, TypeError, AttributeError):
                    job = {**job, 'state': 'failed', 'error': 'prepare exited cleanly but its packet is unreadable'}
        if job['state'] != 'running':
            write_json(folder / 'job.json', job)
    return {**job, 'upload_id': upload_id, 'log_tail': _tail(folder / 'prepare.log')}


class Refusal(ValueError):
    """A plain-language refusal with a stable code the researcher UI can branch on."""

    def __init__(self, message: str, code: str, status: int = 422):
        super().__init__(message)
        self.code, self.status = code, status


def _package_summary(folder: Path) -> dict:
    manifest = read_json(folder / 'package/package.json')
    lines = (folder / 'package/chunks.jsonl').read_bytes().splitlines()
    return {'package_id': manifest['package_id'], 'chunk_count': sum(1 for line in lines if line.strip())}


def start_build(workspace: Path, upload_id, *, python, model_dir, runner=subprocess.Popen) -> dict:
    """Run the existing `knowledge_update build` for one reviewed upload, writing <upload>/package."""
    folder = _upload(workspace, upload_id)
    if model_dir is None or not Path(model_dir).is_dir():
        raise Refusal('No model folder was given when the tool started. Restart it with --model-dir <path>.',
                      'model_dir_missing')
    if python is None or not Path(python).is_file():
        raise Refusal('The Docling interpreter set at start-up was not found. Restart with a valid --prepare-python.',
                      'interpreter_missing')
    if prepare_status(workspace, upload_id)['state'] != 'done':
        raise Refusal('Prepare has not finished for this upload. Wait for it to finish, then build.', 'not_prepared')
    metadata = folder / 'packet/review/build-metadata.json'
    if not metadata.is_file():
        raise Refusal('Save the build form for this upload first, then build.', 'metadata_missing')
    key = 'build:' + upload_id
    with _jobs_lock:
        running = _jobs.get(key)
        if running is not None and running.poll() is None:
            raise Refusal('A build is already running for this upload. Wait for it to finish.', 'build_running', 409)
        # a failed or interrupted build may run again only while no package folder exists (it may be partial)
        if (folder / 'package').exists():
            raise Refusal('This upload already has a package folder. Make a new upload to build again.',
                          'package_exists', 409)
        argv = [str(python), '-m', 'backend.bintanong_tools.knowledge_update', 'build', str(folder / 'packet'),
                '--out', str(folder / 'package'), '--metadata', str(metadata), '--model-dir', str(model_dir)]
        with (folder / 'build.log').open('wb') as log:
            _jobs[key] = runner(argv, cwd=REPO, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        write_json(folder / 'build-job.json', {'state': 'running'})
    return build_status(workspace, upload_id)


def build_status(workspace: Path, upload_id) -> dict:
    folder = _upload(workspace, upload_id)
    path = folder / 'build-job.json'
    job = read_json(path) if path.is_file() else {'state': 'not_started'}
    if job['state'] == 'running':
        job = _polled('build:' + upload_id, job)
        if job['state'] == 'failed':
            job['error'] = f'The build stopped (exit code {job["exit_code"]}). Read the log below for the cause.'
        elif job['state'] == 'interrupted':
            job['error'] = 'The tool restarted while this build ran. Build again if no package folder exists.'
        if job['state'] != 'running':
            write_json(path, job)
    if job['state'] == 'done':
        try:
            job = {**job, 'package': _package_summary(folder)}
        except (ValueError, KeyError, TypeError, OSError):
            job = {**job, 'state': 'failed', 'error': 'The build finished but its package is unreadable. '
                   'Make a new upload to build again.'}
            write_json(path, job)
    return {**job, 'upload_id': upload_id, 'log_tail': _tail(folder / 'build.log')}


def packet_items(workspace: Path, upload_id) -> dict:
    """What prepare extracted, read-only and without the review lock, for a side-by-side check against the page."""
    from .prepare import load_packet
    folder = _upload(workspace, upload_id)
    if prepare_status(workspace, upload_id)['state'] != 'done':
        raise Refusal('Prepare has not finished for this upload. Wait for it to finish, then reload.', 'not_prepared')
    packet = load_packet(folder / 'packet')
    return {'upload_id': upload_id, 'packet_id': packet['packet_id'],
            'documents': [{'id': d['id'], 'title': d['title'], 'sha256': d['sha256']} for d in packet['documents']],
            'items': [{'id': row['id'], 'document_id': row['document_id'], 'title': row.get('title', ''),
                       'findings': row.get('findings', []), 'fields': [
                {'name': f['name'], 'original_value': f['original_value'],
                 'locator': {'physical_pages': f.get('locator', {}).get('physical_pages', [])}}
                for f in row['fields']]} for row in packet['items']]}


class SessionSlot:
    """Stands in for one ReviewSession so a single review tool can open any finished upload's packet.

    Opening another upload closes the previous session first, releasing its ledger lock. Until something is open,
    every review call says so instead of guessing a packet.
    """

    def __init__(self, workspace: Path, reviewer: str):
        self.workspace, self.reviewer = _workspace(workspace), reviewer.strip()
        self.current, self.upload_id = None, None
        self._lock = threading.RLock()

    def open(self, upload_id) -> dict:
        from .review import ReviewSession
        with self._lock:
            folder = _upload(self.workspace, upload_id)
            if upload_id == self.upload_id:
                return self.current.state()  # already open; a second session would hit our own ledger lock
            if prepare_status(self.workspace, upload_id)['state'] != 'done':
                raise ValueError('only an upload whose prepare finished can be opened for review')
            opened = ReviewSession(folder / 'packet', self.reviewer)  # a failure here keeps the current packet
            if self.current is not None:
                self.current.close()
            self.current, self.upload_id = opened, upload_id
            return opened.state()

    def close(self) -> None:
        with self._lock:
            if self.current is not None:
                self.current.close()
            self.current, self.upload_id = None, None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def __getattr__(self, name):
        # only reached for ReviewSession attributes this slot does not define itself
        current = self.__dict__.get('current')
        if name.startswith('_'):  # copy/hasattr/getattr-default probes need a plain missing attribute
            raise AttributeError(name)
        if current is None:
            raise ValueError('Open an upload for review first.')
        return getattr(current, name)


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
