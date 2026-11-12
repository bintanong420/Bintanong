"""Read-only browsing of knowledge chunks: built upload packages, local Supabase and the hosted project.

Nothing here writes. Hosted access is GET-only with the anon key read from an explicitly passed env file, so hosted
shows exactly what the public runtime sees under RLS (only the active release). Local reads go to the exact local
target through local_release.local_client. Source PDFs are served only from known roots after a fresh sha256 check.
"""
from __future__ import annotations

import os
import re
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from .files import digest, read_json
from .intake import Refusal, _workspace, list_uploads

SOURCE_ID = re.compile(r'(?:package:[0-9a-f]{16}|(?:local|hosted):[A-Za-z0-9._-]{1,100})')
SHA256 = re.compile(r'[0-9a-f]{64}')
MAX_QUERY = 200
MAX_DOCUMENT = 300
DOCUMENT_BATCH = 1000          # rows per request; PostgREST commonly caps a response near this
MAX_DOCUMENT_CHUNKS = 5000     # most chunks one listing reads before it reports truncated
CHUNK_COLUMNS = ('chunk_id,text,section_path,byte_sha256,reading_id:type_fields->>reading_id,'
                 'token_count:token_count->count,documents(title),source_spans(page),release_chunks!inner(release_id)')
MESSAGES = {
    'local_unavailable': "Local Supabase isn't running. Start the local stack, then reload.",
    'local_error': 'Local Supabase refused the read (HTTP {status}). Check that the local stack is current, then reload.',
    'hosted_not_configured': 'No hosted settings file was given when the tool started. '
                             'Restart it with --hosted-env <path> to browse hosted.',
    'hosted_settings': 'The hosted settings file needs an https SUPABASE_URL and a SUPABASE_ANON_KEY. '
                       'Add both, then restart the tool.',
    'hosted_unavailable': "The hosted project can't be reached. Check your connection, then reload.",
    'hosted_rejected': 'The hosted project rejected the public key. Check SUPABASE_ANON_KEY, then restart the tool.',
    'hosted_redirect': 'The hosted address points somewhere other than your project. '
                       'Check SUPABASE_URL in the settings file, then restart.',
    'hosted_bad_url': "SUPABASE_URL in the hosted settings file isn't a usable address. Fix it, then restart the tool.",
    'hosted_error': 'The hosted project refused the read (HTTP {status}). Reload, or try again later.',
    'hosted_empty': 'Hosted shows no active release. Only an active release is visible here.',
}


def unavailable(code: str, **values) -> Refusal:
    return Refusal(MESSAGES[code].format(**values), code, 503)


@dataclass(frozen=True)
class HostedSettings:
    url: str
    anon_key: str = field(repr=False)


def hosted_settings(path) -> HostedSettings:
    """Only SUPABASE_URL and SUPABASE_ANON_KEY are kept; every other line (service keys included) is ignored."""
    if path is None:
        raise unavailable('hosted_not_configured')
    wanted = {}
    try:
        lines = Path(path).read_text(encoding='utf-8-sig').splitlines()
    except OSError:
        raise unavailable('hosted_settings') from None
    for line in lines:
        name, sep, value = line.strip().removeprefix('export ').partition('=')
        if sep and name.strip() in ('SUPABASE_URL', 'SUPABASE_ANON_KEY'):
            wanted[name.strip()] = value.strip().strip('"\'')
    try:
        url = urlsplit(wanted.get('SUPABASE_URL', ''))
        url.port  # raises ValueError for a malformed port
    except ValueError:
        raise unavailable('hosted_bad_url') from None
    if (url.scheme != 'https' or not url.hostname or url.username or url.query or url.fragment
            or url.path not in ('', '/') or not wanted.get('SUPABASE_ANON_KEY')):
        raise unavailable('hosted_settings')
    return HostedSettings('https://' + url.netloc, wanted['SUPABASE_ANON_KEY'])


class Rest:
    """GET-only PostgREST reader. Errors carry plain reasons and never the key or transport details."""

    def __init__(self, kind: str, base: str, key: str, http: httpx.Client):
        self.kind, self.base, self._key, self._http = kind, base.rstrip('/') + '/rest/v1', key, http

    def get(self, table: str, params: dict, *, count: bool = False) -> tuple[list, int | None]:
        headers = {'apikey': self._key, 'Authorization': 'Bearer ' + self._key, 'Accept': 'application/json'}
        if count:
            headers['Prefer'] = 'count=exact'
        try:
            response = self._http.get(f'{self.base}/{table}', params=params, headers=headers)
        except httpx.InvalidURL:
            raise unavailable('hosted_bad_url' if self.kind == 'hosted' else 'local_unavailable') from None
        except (httpx.HTTPError, httpx.StreamError):  # HTTPError covers every RequestError (timeouts, protocol, proxy)
            raise unavailable(self.kind + '_unavailable') from None
        status = response.status_code
        if self.kind == 'hosted' and 300 <= status < 400:
            raise unavailable('hosted_redirect')
        if self.kind == 'hosted' and status in (401, 403):
            raise unavailable('hosted_rejected')
        if not 200 <= status < 300:
            raise unavailable(self.kind + '_error', status=status)
        try:
            rows = response.json()
        except ValueError:
            raise unavailable(self.kind + '_error', status=status) from None
        total = response.headers.get('content-range', '').rpartition('/')[2]
        return rows, int(total) if total.isdigit() else None

    def close(self):
        self._http.close()


def local_rest() -> Rest:
    from .local_release import LOCAL_TARGET, local_client
    client = local_client(LOCAL_TARGET)  # exact 127.0.0.1:54321, proxy-free; this module only issues GETs with it
    return Rest('local', LOCAL_TARGET, client.config.service_role_key, client._http)


def like_pattern(text: str) -> str:
    """PostgREST ilike value matching `text` as a literal substring."""
    escaped = text.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    # ponytail: PostgREST turns every * into %, so a literal * becomes the one-character wildcard _ (still matches it)
    return '*' + escaped.replace('*', '_') + '*'


def _bounded(offset, limit, q) -> str:
    if type(offset) is not int or not 0 <= offset <= 1_000_000:
        raise Refusal('offset must be a whole number from 0.', 'bad_request')
    if type(limit) is not int or not 1 <= limit <= 100:
        raise Refusal('limit must be from 1 to 100.', 'bad_request')
    q = q or ''
    if len(q) > MAX_QUERY or any(ord(c) < 32 for c in q):
        raise Refusal(f'Search text must be one line of at most {MAX_QUERY} characters.', 'bad_request')
    return q.strip()


def _document(document) -> str:
    document = document or ''
    if len(document) > MAX_DOCUMENT or any(ord(c) < 32 for c in document):
        raise Refusal(f'Document must be one line of at most {MAX_DOCUMENT} characters.', 'bad_request')
    return document


def _document_filter(params: dict, document: str) -> None:
    """Exact match on the source hash, or on the document title through an inner join on documents."""
    if SHA256.fullmatch(document):
        params['byte_sha256'] = 'eq.' + document
    else:
        params['select'] = params['select'].replace('documents(title)', 'documents!inner(title)')
        params['documents.title'] = 'eq.' + document


def _pages(spans) -> list[int]:
    return sorted({s['page'] for s in spans or [] if isinstance(s, dict) and isinstance(s.get('page'), int)})


class KnowledgeBrowser:
    def __init__(self, workspace: Path, *, hosted_env=None, source_roots=(), local=local_rest, transport=None):
        self.workspace = _workspace(workspace)
        self.hosted_env, self.local, self.transport = hosted_env, local, transport
        self.sources_index = SourceIndex(self.workspace, source_roots)
        self._packages: dict[str, tuple[int, dict]] = {}
        self._lock = threading.Lock()

    def hosted(self) -> Rest:
        settings = hosted_settings(self.hosted_env)
        http = httpx.Client(timeout=15, trust_env=False, follow_redirects=False, transport=self.transport)
        return Rest('hosted', settings.url, settings.anon_key, http)

    def _rest(self, kind: str) -> Rest:
        return self.local() if kind == 'local' else self.hosted()

    def sources(self) -> dict:
        rows, missing = [], {}
        for note in list_uploads(self.workspace):
            folder = self.workspace / str(note.get('upload_id', ''))
            if re.fullmatch(r'[0-9a-f]{16}', str(note.get('upload_id', ''))) and (folder / 'package/package.json').is_file():
                lines = (folder / 'package/chunks.jsonl').read_bytes().splitlines() if (
                    folder / 'package/chunks.jsonl').is_file() else []
                rows.append({'id': 'package:' + note['upload_id'], 'kind': 'package',
                             'label': f"{note.get('title', '')} ({note.get('edition', '')})",
                             'chunk_count': sum(1 for line in lines if line.strip())})
        for kind in ('local', 'hosted'):
            try:
                rest = self._rest(kind)
                try:
                    active, _ = rest.get('active_release', {'select': 'release_id'})
                    releases, _ = rest.get('knowledge_releases', {'select': 'release_id,release_version,status',
                                                                  'order': 'created_at.desc', 'limit': '200'})
                finally:
                    rest.close()
                if not releases and kind == 'hosted':
                    raise unavailable('hosted_empty')
                current = {row.get('release_id') for row in active}
                rows += [{'id': f"{kind}:{r['release_id']}", 'kind': kind, 'label': r['release_version'],
                          'status': r['status'], 'active': r['release_id'] in current} for r in releases]
            except Refusal as exc:
                missing[kind] = str(exc)
        return {'sources': rows, 'unavailable': missing}

    def _package(self, upload_id: str) -> dict:
        from .build import load_package
        root = self.workspace / upload_id / 'package'
        if not (root / 'package.json').is_file():
            raise Refusal('This upload has no built package yet. Build it first.', 'unknown_source', 404)
        stamp = (root / 'package.json').stat().st_mtime_ns
        with self._lock:
            cached = self._packages.get(upload_id)
            if cached is None or cached[0] != stamp:
                try:
                    cached = (stamp, load_package(root))  # full verification once per package version
                except ValueError:
                    raise Refusal('This package failed its integrity check. Rebuild it from a new upload.',
                                  'package_invalid', 409) from None
                self._packages[upload_id] = cached
            return cached[1]

    def chunks(self, source: str, q: str = '', offset: int = 0, limit: int = 25, document: str = '') -> dict:
        if not isinstance(source, str) or not SOURCE_ID.fullmatch(source):
            raise Refusal('Unknown knowledge source. Pick one from the source list.', 'unknown_source')
        q = _bounded(offset, limit, q)
        document = _document(document)
        kind, _, ident = source.partition(':')
        if kind == 'package':
            package = self._package(ident)
            titles = {d['sha256']: d.get('title') for d in package['recipe']['source_documents']}
            needle = q.casefold()
            matched = [c for c in package['chunks'] if needle in c['text'].casefold() and (
                not document or document in (c.get('byte_sha256'), titles.get(c.get('byte_sha256'))))]
            rows = [{'chunk_id': c['chunk_id'], 'text': c['text'], 'document_title': titles.get(c.get('byte_sha256')),
                     'section': ' > '.join(c.get('section_path') or []) or None, 'pages': _pages(c.get('spans')),
                     'source_sha256': c.get('byte_sha256'), 'reading_id': (c.get('type_fields') or {}).get('reading_id'),
                     'token_count': (c.get('token_count') or {}).get('count')} for c in matched[offset:offset + limit]]
            return {'chunks': rows, 'total': len(matched), 'offset': offset, 'limit': limit}
        params = {'select': CHUNK_COLUMNS, 'release_chunks.release_id': 'eq.' + ident,
                  'order': 'chunk_id.asc', 'offset': str(offset), 'limit': str(limit)}
        if q:
            params['text'] = 'ilike.' + like_pattern(q)
        if document:
            _document_filter(params, document)
        rest = self._rest(kind)
        try:
            found, total = rest.get('chunks', params, count=True)
        finally:
            rest.close()
        rows = [{'chunk_id': r['chunk_id'], 'text': r['text'], 'document_title': (r.get('documents') or {}).get('title'),
                 'section': ' > '.join(r.get('section_path') or []) or None, 'pages': _pages(r.get('source_spans')),
                 'source_sha256': r.get('byte_sha256'), 'reading_id': r.get('reading_id'),
                 'token_count': r.get('token_count')} for r in found]
        return {'chunks': rows, 'total': len(rows) + offset if total is None else total, 'offset': offset, 'limit': limit}

    def documents(self, source: str) -> dict:
        """One entry per source document: grouped by source hash (else title). Chunk text is never fetched."""
        if not isinstance(source, str) or not SOURCE_ID.fullmatch(source):
            raise Refusal('Unknown knowledge source. Pick one from the source list.', 'unknown_source')
        kind, _, ident = source.partition(':')
        truncated = False
        if kind == 'package':
            package = self._package(ident)
            titles = {d['sha256']: d.get('title') for d in package['recipe']['source_documents']}
            chunks = [(c.get('byte_sha256'), titles.get(c.get('byte_sha256')), _pages(c.get('spans')))
                      for c in package['chunks']]
        else:
            chunks = []
            params = {'select': 'chunk_id,byte_sha256,documents(title),source_spans(page),release_chunks!inner(release_id)',
                      'release_chunks.release_id': 'eq.' + ident, 'order': 'chunk_id.asc', 'limit': str(DOCUMENT_BATCH)}
            rest = self._rest(kind)
            try:
                while True:
                    rows, total = rest.get('chunks', {**params, 'offset': str(len(chunks))}, count=True)
                    room = MAX_DOCUMENT_CHUNKS - len(chunks)
                    chunks += [(r.get('byte_sha256'), (r.get('documents') or {}).get('title'), _pages(r.get('source_spans')))
                               for r in rows[:room]]
                    if len(rows) < DOCUMENT_BATCH or (total is not None and len(chunks) >= total):
                        break
                    if len(chunks) >= MAX_DOCUMENT_CHUNKS:
                        truncated = True
                        break
            finally:
                rest.close()
        groups: dict[str, dict] = {}
        for sha, title, pages in chunks:
            sha = sha if isinstance(sha, str) and SHA256.fullmatch(sha) else None
            key = sha or title
            if not key:
                continue  # no hash and no title: nothing to group or filter by
            group = groups.setdefault(key, {'document_key': key, 'title': title or '', 'chunk_count': 0, 'pages': set()})
            group['title'] = group['title'] or title or ''
            group['chunk_count'] += 1
            group['pages'].update(pages)
            if sha:
                group['source_sha256'] = sha
        documents = []
        for group in sorted(groups.values(), key=lambda g: (g['title'].casefold(), g['document_key'])):
            pages = sorted(group.pop('pages'))
            sha = group.get('source_sha256')
            documents.append({**group, 'pages': [pages[0], pages[-1]] if pages else [],
                              'pdf_available': bool(sha and self.sources_index.locate(sha))})
        return {'documents': documents, 'source': source, 'truncated': truncated}


def _inside(root: Path, path: Path) -> Path | None:
    """The resolved file when it sits under root with no symlink on the way, else None."""
    try:
        relative = path.relative_to(root)
    except ValueError:
        return None
    step = root
    for part in relative.parts:
        step = step / part
        if step.is_symlink():
            return None
    resolved = path.resolve()
    return resolved if resolved.is_file() and resolved.is_relative_to(root.resolve()) else None


RESCAN_SECONDS = 30


class SourceIndex:
    """sha256 -> PDF under the upload originals and any --source-root, served from a verified private copy.

    The scan hashes a file once per (path, size, mtime_ns), which is only an index: a swap that keeps size and mtime
    slips past it. So the bytes are hashed again at the moment they are taken for rendering, and the page renderer
    (which reads its file lazily, by path) gets a private copy of exactly those bytes under <workspace>/_runtime/pages.
    Later requests for that sha256 reuse the copy without re-reading or re-hashing anything, and no later change to
    the original can alter what is served. Inode/file-id checks were not used: an in-place write keeps the id.
    """

    def __init__(self, workspace: Path, roots=(), copies: Path | None = None):
        workspace = Path(workspace).absolute()
        self.roots = [(workspace, '*/original/source.pdf')] + [(Path(r).absolute(), '**/*.pdf') for r in roots]
        self.copies = copies or workspace / '_runtime/pages'
        self._seen: dict[Path, tuple[int, int, str]] = {}
        self._index: dict[str, Path] = {}
        self._scanned_at: float | None = None
        self._verified: dict[str, Path] = {}
        self._lock = threading.Lock()

    def _scan(self) -> None:
        found, seen = {}, {}
        for root, pattern in self.roots:
            if not root.is_dir() or any(p.is_symlink() for p in (root, *root.parents)):
                continue
            for candidate in root.glob(pattern):
                path = _inside(root, candidate)
                if path is None:
                    continue
                stat = path.stat()
                known = self._seen.get(path)
                if known is None or known[:2] != (stat.st_size, stat.st_mtime_ns):
                    known = (stat.st_size, stat.st_mtime_ns, digest(path.read_bytes()))
                seen[path] = known
                found.setdefault(known[2], path)
        self._seen, self._index, self._scanned_at = seen, found, time.monotonic()

    def locate(self, sha256: str) -> Path | None:
        """Indexed path for sha256, rescanning only on a miss or when the index is older than RESCAN_SECONDS."""
        _check_sha(sha256)
        with self._lock:
            stale = self._scanned_at is None or time.monotonic() - self._scanned_at > RESCAN_SECONDS
            if stale or sha256 not in self._index:
                self._scan()
            return self._index.get(sha256)

    def pdf(self, sha256: str) -> Path | None:
        """A private copy holding exactly the bytes whose sha256 was requested, or None."""
        _check_sha(sha256)
        with self._lock:
            ready = self._verified.get(sha256)
        if ready is not None and ready.is_file():
            return ready
        path = self.locate(sha256)
        for _ in range(2):
            if path is None:
                return None
            try:
                data = path.read_bytes()
            except OSError:
                data = b''
            if digest(data) == sha256:
                return self._keep(sha256, data)
            with self._lock:  # stale entry (content swapped, maybe with the same size and mtime): forget it, rescan
                self._seen.pop(path, None)
                self._scan()
                path = self._index.get(sha256)
        return None

    def _keep(self, sha256: str, data: bytes) -> Path:
        self.copies.mkdir(parents=True, exist_ok=True)
        target = self.copies / (sha256 + '.pdf')
        temporary = self.copies / f'{sha256}.{threading.get_ident()}.tmp'
        temporary.write_bytes(data)
        os.replace(temporary, target)
        with self._lock:
            self._verified[sha256] = target
        return target


def _check_sha(sha256) -> None:
    if not isinstance(sha256, str) or not SHA256.fullmatch(sha256):
        raise Refusal('sha256 must be 64 lowercase hex characters.', 'bad_request')
