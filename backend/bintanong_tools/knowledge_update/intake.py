"""Researcher upload -> one checked manifest folder (owner GUI intake plan, 11 Nov 2026).

Each upload gets its own folder with sibling original/, manifest.json and upload.json, so `prepare` can later write
packet/ beside the original (check_out refuses outputs inside the originals). The server picks the id and the file
name; the client's file name is never used. Office and audience are notes only: audience stays a per-item review
decision. Nothing here approves content.
"""
from __future__ import annotations

import secrets
from pathlib import Path

from .files import digest, read_json, write_json

MAX_UPLOAD = 128 * 1024 * 1024  # same ceiling load_manifest enforces
KINDS = ('handbook', 'charter')  # prospectus needs the ledger path (U1), not this intake
TEXT_LIMIT = 300


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
