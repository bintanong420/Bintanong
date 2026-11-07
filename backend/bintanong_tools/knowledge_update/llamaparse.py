from __future__ import annotations

import os
import json
from pathlib import Path
import re
import time

import httpx

from ..document_ingest.inspection import check_out
from ..prospectus_extractor.ledger import LedgerLock
from ..prospectus_review_gui.render import PageRenderer
from .files import contained, digest, read_json, write_json


class LlamaParseClient:
    def __init__(self, key=None, *, transport=None, timeout=60, polls=120):
        self.key = key or os.environ.get('LLAMA_CLOUD_API_KEY')
        if not self.key:
            raise ValueError('LLAMA_CLOUD_API_KEY is required for live parsing')
        self.transport, self.timeout, self.polls = transport, timeout, polls

    def _request(self, method, path, **kwargs):
        try:
            with httpx.Client(timeout=self.timeout, transport=self.transport, trust_env=False,
                              follow_redirects=False) as client:
                response = client.request(method, 'https://api.cloud.llamaindex.ai/api/v2/parse' + path,
                    headers={'Authorization': 'Bearer ' + self.key}, **kwargs)
                response.raise_for_status()
                if len(response.content) > 32 * 1024 * 1024:
                    raise ValueError('parse result exceeds local bound')
                value = response.json()
                if not isinstance(value, dict):
                    raise ValueError('invalid parse response')
                return value
        except (httpx.HTTPError, ValueError):
            raise RuntimeError('LlamaParse request failed; check authentication, quota or connectivity and resume.') from None

    def upload(self, source, pages, config):
        config = {**config, 'page_ranges': {'target_pages': ','.join(map(str, pages))}}
        with Path(source).open('rb') as stream:
            value = self._request('POST', '/upload', files={'file': (Path(source).name, stream, 'application/pdf')},
                                  data={'configuration': json.dumps(config)})
        identity = value.get('id')
        if not isinstance(identity, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,160}', identity):
            raise RuntimeError('LlamaParse returned an invalid job identity')
        return identity

    def poll(self, job_id):
        if not isinstance(job_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,160}', job_id):
            raise ValueError('invalid parse job identity')
        for _ in range(self.polls):
            value = self._request('GET', '/' + job_id, params={'expand': 'items,usage'})
            job = value.get('job', {})
            if not isinstance(job, dict) or job.get('id') != job_id:
                raise RuntimeError('LlamaParse job identity mismatch')
            if job.get('status') == 'COMPLETED':
                if not isinstance(value.get('items'), dict):
                    raise RuntimeError('LlamaParse page results unavailable; resume or review manually')
                return value
            if job.get('status') not in ('PENDING', 'RUNNING'):
                raise RuntimeError('LlamaParse job failed or was cancelled; explicit retry is required')
            time.sleep(1)
        raise TimeoutError('LlamaParse polling timed out; resume the recorded job')


def _pages(rows, selected):
    if not isinstance(rows, list) or any(not isinstance(p, dict) for p in rows):
        raise ValueError('invalid parse pages')
    actual = [p.get('page_number') for p in rows]
    if (any(type(p) is not int or p not in selected for p in actual)
            or len(actual) != len(set(actual))
            or any(type(p.get('success')) is not bool
                   or (p['success'] and not isinstance(p.get('items'), list)) for p in rows)):
        raise ValueError('invalid parse pages')
    return {p['page_number']: p for p in rows if p['success']}


def parse(source: Path, out: Path, *, pages, batch_size=5, client=None, tier='agentic', version='latest', retry_failed=False):
    source, out = Path(source).resolve(), Path(out).absolute()
    if out.exists() and (out / 'request.json').is_file():
        if (source.parent == out.resolve() or source.parent in out.resolve().parents
                or any(p.is_symlink() or (p / '.git').exists() for p in (out, *out.parents))):
            raise ValueError('unsafe parser resume output')
    else:
        check_out(source.parent, out)
    if (not isinstance(pages, (tuple, list)) or not pages or len(pages) != len(set(pages))
            or any(type(p) is not int or p < 1 for p in pages)
            or type(batch_size) is not int or not 1 <= batch_size <= 20
            or tier not in ('fast', 'cost_effective', 'agentic', 'agentic_plus')
            or not isinstance(version, str) or not version or len(version) > 80):
        raise ValueError('explicit unique physical page selection and bounded parser configuration required')
    data = source.read_bytes()
    if len(data) > 128 * 1024 * 1024:
        raise ValueError('PDF exceeds 128 MiB')
    with PageRenderer(source) as renderer:
        if max(pages) > renderer.page_count:
            raise ValueError('page selection exceeds the original PDF')
    pages = sorted(pages)
    config = {'pages': pages, 'batch_size': batch_size, 'tier': tier, 'version': version}
    identity = {'source_sha256': digest(data), 'config': config}
    out.mkdir(parents=True, exist_ok=True)
    with LedgerLock(out / 'parse-session', 'LlamaParse candidate generation'):
        receipt = contained(out, 'request.json')
        if receipt.exists() and read_json(receipt) != identity:
            raise ValueError('parse source, page selection or configuration changed; use a new output')
        write_json(receipt, identity)
        parsed, failed, batches = [], [], []
        for offset in range(0, len(pages), batch_size):
            selected = pages[offset:offset + batch_size]
            cache = contained(out, 'batch-' + str(offset // batch_size + 1) + '.json')
            batch = read_json(cache) if cache.exists() else {**identity, 'pages': selected}
            if any(batch.get(k) != v for k, v in identity.items()) or batch['pages'] != selected:
                raise ValueError('stale parse batch')
            completed = _pages(batch.get('result', {}).get('pages', []), selected)
            missing = [p for p in selected if p not in completed]
            try:
                if missing:
                    client = client or LlamaParseClient()
                    if retry_failed and batch.get('failed'):
                        batch.pop('pending_pages', None)
                    if not batch.get('pending_pages'):
                        batch['job_id'] = client.upload(source, missing, {'tier': tier, 'version': version})
                        batch['pending_pages'] = missing
                        write_json(cache, batch)
                    response = client.poll(batch['job_id'])
                    if response.get('job', {}).get('status') != 'COMPLETED':
                        raise ValueError('incomplete parse job')
                    returned = _pages(response.get('items', {}).get('pages', []), batch['pending_pages'])
                    completed.update(returned)
                    batch['result'] = {'pages': list(completed.values()),
                                       'usage': response.get('job', {}).get('usage')}
                    batch.pop('pending_pages', None)
                    batch.pop('failed', None)
                write_json(cache, batch)
                batches.append({'pages': selected, 'job_id': batch.get('job_id'), 'outcome': 'returned'})
            except (RuntimeError, ValueError, TimeoutError, httpx.HTTPError, KeyError, TypeError):
                batch['failed'] = True
                write_json(cache, batch)
                batches.append({'pages': selected, 'job_id': batch.get('job_id'), 'outcome': 'failed'})
            parsed.extend(completed[p] for p in selected if p in completed)
            failed.extend(p for p in selected if p not in completed)
        if digest(source.read_bytes()) != identity['source_sha256']:
            raise ValueError('source changed during parsing')
        value = {'schema_version': 'bintanong-llamaparse-candidate-v1', **identity,
                 'pages': parsed, 'failed_pages': sorted(set(failed)), 'batches': batches}
        write_json(contained(out, 'result.json'), value)
        return value
