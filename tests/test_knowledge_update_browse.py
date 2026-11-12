"""Read-only knowledge browsing: packages, local and hosted Supabase (faked transports only) and source pages."""
import importlib
import logging
import os

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.bintanong_tools.knowledge_update.files import digest
from test_knowledge_update_build import SyntheticEncoder, reviewed  # noqa: F401  (fixture)
from test_knowledge_update_intake import ORIGIN, PDF, TOKEN

GOOD = {'x-review-token': TOKEN, 'origin': ORIGIN}
ANON, SERVICE = 'anon-key-synthetic-123', 'service-role-secret-must-never-leave'
RELEASE = {'release_id': 'rel-1', 'release_version': 'v2026.11', 'status': 'active'}
ROW = {'chunk_id': 'c' * 64, 'text': 'Submit the form.', 'section_path': ['Part I', 'Forms'], 'byte_sha256': 'b' * 64,
       'reading_id': 'handbook:text-0', 'token_count': 7, 'documents': {'title': 'Synthetic code'},
       'source_spans': [{'page': 3}, {'page': 2}, {'page': 3}], 'release_chunks': [{'release_id': 'rel-1'}]}


def browse():
    return importlib.import_module('backend.bintanong_tools.knowledge_update.knowledge_browse')


def intake():
    return importlib.import_module('backend.bintanong_tools.knowledge_update.intake')


class Recorder:
    """Fake PostgREST: answers by table, records every request it receives."""

    def __init__(self, tables=None, status=200, total='0-0/1'):
        self.requests, self.tables, self.status, self.total = [], tables or {}, status, total

    def __call__(self, request):
        self.requests.append(request)
        if self.status != 200:
            return httpx.Response(self.status, headers={'location': 'https://elsewhere.example'}, json={})
        table = request.url.path.rsplit('/', 1)[1]
        return httpx.Response(200, json=self.tables.get(table, []), headers={'content-range': self.total})


def env_file(tmp_path, url='https://synthetic.supabase.co'):
    path = tmp_path / 'hosted.env'
    path.write_text(f'SUPABASE_URL={url}\nSUPABASE_SERVICE_ROLE_KEY={SERVICE}\nSUPABASE_ANON_KEY="{ANON}"\n',
                    encoding='utf-8')
    return path


def local_down():
    def refuse(request):
        raise httpx.ConnectError('connection refused to 127.0.0.1:54321')
    return browse().Rest('local', 'http://127.0.0.1:54321', 'local-key', httpx.Client(transport=httpx.MockTransport(refuse)))


def browser(tmp_path, *, hosted=None, local=local_down, **extra):
    return browse().KnowledgeBrowser(tmp_path, hosted_env=extra.pop('hosted_env', None), local=local,
                                     transport=None if hosted is None else httpx.MockTransport(hosted), **extra)


def test_hosted_uses_only_the_anon_key_and_get(tmp_path, caplog):
    caplog.set_level(logging.DEBUG)
    fake = Recorder({'active_release': [{'release_id': 'rel-1'}], 'knowledge_releases': [RELEASE], 'chunks': [ROW]})
    knowledge = browser(tmp_path, hosted=fake, hosted_env=env_file(tmp_path))
    listed = knowledge.sources()
    assert {'id': 'hosted:rel-1', 'kind': 'hosted', 'label': 'v2026.11', 'status': 'active', 'active': True} in listed['sources']
    knowledge.chunks('hosted:rel-1', q='form')
    assert fake.requests and all(r.method == 'GET' for r in fake.requests)
    for request in fake.requests:
        assert request.headers['apikey'] == ANON and request.headers['authorization'] == 'Bearer ' + ANON
        assert SERVICE not in str(request.url) and SERVICE not in str(dict(request.headers))
        assert request.url.host == 'synthetic.supabase.co'
    assert SERVICE not in caplog.text and ANON not in caplog.text
    assert ANON not in repr(browse().hosted_settings(env_file(tmp_path)))


def test_local_down_and_hosted_unconfigured_are_plain_unavailable_reasons(tmp_path):
    listed = browser(tmp_path).sources()
    assert listed['sources'] == []
    assert listed['unavailable'] == {
        'local': "Local Supabase isn't running. Start the local stack, then reload.",
        'hosted': 'No hosted settings file was given when the tool started. Restart it with --hosted-env <path> to browse hosted.'}
    assert all(len(reason) <= 160 for reason in listed['unavailable'].values())


@pytest.mark.parametrize('status, code', [(401, 'hosted_rejected'), (302, 'hosted_redirect'), (500, 'hosted_error')])
def test_hosted_refusals_and_redirects_are_not_followed(tmp_path, status, code):
    fake = Recorder(status=status)
    listed = browser(tmp_path, hosted=fake, hosted_env=env_file(tmp_path)).sources()
    assert listed['unavailable']['hosted'] == browse().MESSAGES[code].format(status=status)
    assert len(fake.requests) == 1 and 'elsewhere' not in str(fake.requests[0].url)


def test_hosted_with_rls_hiding_every_release_says_so(tmp_path):
    listed = browser(tmp_path, hosted=Recorder(), hosted_env=env_file(tmp_path)).sources()
    assert listed['unavailable']['hosted'] == 'Hosted shows no active release. Only an active release is visible here.'


def test_hosted_settings_need_https_and_an_anon_key(tmp_path):
    with pytest.raises(ValueError) as caught:
        browse().hosted_settings(env_file(tmp_path, url='http://synthetic.supabase.co'))
    assert caught.value.code == 'hosted_settings'


def test_a_service_key_alone_never_stands_in_for_the_anon_key(tmp_path):
    path = tmp_path / 'service-only.env'
    path.write_text(f'SUPABASE_URL=https://synthetic.supabase.co\nSUPABASE_SERVICE_ROLE_KEY={SERVICE}\n', encoding='utf-8')
    fake = Recorder({'knowledge_releases': [RELEASE]})
    listed = browser(tmp_path, hosted=fake, hosted_env=path).sources()
    assert listed['unavailable']['hosted'] == browse().MESSAGES['hosted_settings']
    assert fake.requests == []  # nothing was sent, so the service key cannot have been used


@pytest.mark.parametrize('error', [httpx.InvalidURL('bad host'), httpx.ReadTimeout('slow'), httpx.RemoteProtocolError('x')])
def test_transport_and_url_errors_become_plain_unavailable_reasons(tmp_path, error):
    def fail(request):
        raise error
    listed = browser(tmp_path, hosted=fail, hosted_env=env_file(tmp_path)).sources()
    reason = listed['unavailable']['hosted']
    assert reason in {browse().MESSAGES['hosted_unavailable'], browse().MESSAGES['hosted_bad_url']}
    assert 'bad host' not in reason and 'Error' not in reason and len(reason) <= 160


def test_redirect_message_is_actionable_without_jargon():
    assert 'redirect' not in browse().MESSAGES['hosted_redirect'].lower()
    assert 'SUPABASE_URL' in browse().MESSAGES['hosted_redirect']


def test_local_chunks_filter_by_release_escape_search_and_page(tmp_path):
    fake = Recorder({'chunks': [ROW]}, total='25-25/26')
    client = httpx.Client(transport=httpx.MockTransport(fake))
    knowledge = browser(tmp_path, local=lambda: browse().Rest('local', 'http://127.0.0.1:54321', 'k', client))
    result = knowledge.chunks('local:rel-1', q=r'50%_a*b\c', offset=25, limit=10)
    params = fake.requests[0].url.params
    assert params['release_chunks.release_id'] == 'eq.rel-1'
    assert params['text'] == r'ilike.*50\%\_a_b\\c*'
    assert (params['offset'], params['limit']) == ('25', '10')
    assert fake.requests[0].headers['prefer'] == 'count=exact'
    assert result == {'chunks': [{'chunk_id': 'c' * 64, 'text': 'Submit the form.', 'display_text': None, 'document_title': 'Synthetic code',
        'section': 'Part I > Forms', 'pages': [2, 3], 'source_sha256': 'b' * 64, 'reading_id': 'handbook:text-0',
        'token_count': 7}], 'total': 26, 'offset': 25, 'limit': 10}


@pytest.mark.parametrize('query', [{'limit': 0}, {'limit': 101}, {'offset': -1}, {'q': 'x' * 201}, {'q': 'a\nb'}])
def test_chunk_pagination_and_search_bounds(tmp_path, query):
    with pytest.raises(ValueError) as caught:
        browser(tmp_path).chunks('local:rel-1', **query)
    assert caught.value.code == 'bad_request'


@pytest.mark.parametrize('source', ['local:', 'hosted:a b', 'package:XYZ', 'remote:rel', 'local:rel&x=1', 'local:' + 'a' * 101])
def test_source_ids_are_validated_strictly(tmp_path, source):
    with pytest.raises(ValueError) as caught:
        browser(tmp_path).chunks(source)
    assert caught.value.code == 'unknown_source'


def test_a_built_upload_package_is_browsable(reviewed, tmp_path):  # noqa: F811
    root, _ = reviewed
    upload_id = intake().create_upload(tmp_path, PDF, kind='handbook', title='Synthetic code', edition='2026')['upload_id']
    build = importlib.import_module('backend.bintanong_tools.knowledge_update.build')
    build.build(root, tmp_path / upload_id / 'package', encoder=SyntheticEncoder())
    knowledge = browser(tmp_path)
    assert {'id': 'package:' + upload_id, 'kind': 'package', 'label': 'Synthetic code (2026)',
            'chunk_count': 1} in knowledge.sources()['sources']
    found = knowledge.chunks('package:' + upload_id, q='SUBMIT')
    assert found['total'] == 1 and 'Submit the form.' in found['chunks'][0]['text']
    assert found['chunks'][0]['reading_id'] == 'handbook:text-0' and found['chunks'][0]['pages']
    assert knowledge.chunks('package:' + upload_id, q='absent')['total'] == 0


def web(tmp_path, knowledge):
    app = importlib.import_module('backend.bintanong_tools.knowledge_update.app')
    slot = intake().SessionSlot(tmp_path, 'Synthetic researcher')
    return TestClient(app.create_app(slot, TOKEN, port=8765, ui_origin=ORIGIN, workspace=tmp_path, knowledge=knowledge),
                      base_url='http://127.0.0.1:8765'), app


def test_knowledge_routes_need_the_token_and_return_codes(tmp_path):
    client, _ = web(tmp_path, browser(tmp_path))
    assert client.get('/api/knowledge/sources', headers={'origin': ORIGIN}).status_code == 403
    assert client.get('/api/knowledge/sources', headers=GOOD).json()['unavailable']['local'].startswith('Local Supabase')
    bad = client.get('/api/knowledge/chunks', params={'source': 'local:rel-1', 'limit': 101}, headers=GOOD)
    assert bad.status_code == 422 and bad.json()['code'] == 'bad_request'
    down = client.get('/api/knowledge/chunks', params={'source': 'local:rel-1'}, headers=GOOD)
    assert down.status_code == 503 and down.json() == {
        'error': "Local Supabase isn't running. Start the local stack, then reload.", 'code': 'local_unavailable'}


def test_page_is_served_only_for_a_verified_pdf_under_known_roots(tmp_path, monkeypatch):
    upload_id = intake().create_upload(tmp_path, PDF, kind='handbook', title='Synthetic code', edition='2026')['upload_id']
    dataset = tmp_path.parent / (tmp_path.name + '-dataset')
    (dataset / 'nested').mkdir(parents=True)
    other = b'%PDF-1.7 synthetic dataset file'
    (dataset / 'nested/prospectus.pdf').write_bytes(other)
    knowledge = browser(tmp_path, source_roots=[dataset])
    index = knowledge.sources_index
    assert index.pdf(digest(PDF)).read_bytes() == PDF  # a private copy of exactly the verified bytes
    assert (tmp_path / upload_id / 'original/source.pdf').read_bytes() == PDF
    assert index.pdf('0' * 64) is None
    (dataset / 'nested/prospectus.pdf').write_bytes(b'%PDF-1.7 swapped')  # bytes changed after indexing
    assert index.pdf(digest(other)) is None
    with pytest.raises(ValueError):
        index.pdf('NOT-A-HASH')

    client, app = web(tmp_path, knowledge)
    monkeypatch.setattr(app, 'PageRenderer', FakeRenderer)
    shown = client.get('/api/knowledge/page', params={'sha256': digest(PDF), 'page': 1}, headers=GOOD)
    assert shown.status_code == 200 and shown.headers['content-type'] == 'image/png'
    assert shown.headers['x-page-count'] == '4' and 'X-Page-Count' in shown.headers['access-control-expose-headers']
    missing = client.get('/api/knowledge/page', params={'sha256': '0' * 64, 'page': 1}, headers=GOOD)
    assert missing.status_code == 404 and missing.json()['error'] == 'source PDF not available locally'
    assert client.get('/api/knowledge/page', params={'sha256': digest(PDF), 'page': 1},
                      headers={'origin': ORIGIN}).status_code == 403


def test_whole_pdf_is_served_only_for_a_verified_sha_with_the_token(tmp_path):
    intake().create_upload(tmp_path, PDF, kind='handbook', title='Synthetic code', edition='2026')
    root = tmp_path.parent / (tmp_path.name + '-pdf-roots')
    root.mkdir()
    swapped = b'%PDF-1.7 synthetic original'
    (root / 'later.pdf').write_bytes(swapped)
    knowledge = browser(tmp_path, source_roots=[root])
    assert knowledge.sources_index.locate(digest(swapped)) is not None
    (root / 'later.pdf').write_bytes(b'%PDF-1.7 synthetic changed')  # bytes no longer match the requested sha
    client, _ = web(tmp_path, knowledge)
    shown = client.get('/api/knowledge/pdf', params={'sha256': digest(PDF)}, headers=GOOD)
    assert shown.status_code == 200 and shown.content == PDF
    assert shown.headers['content-type'] == 'application/pdf'
    assert shown.headers['content-disposition'] == 'inline'
    assert shown.headers['cache-control'] == 'private, max-age=300'  # content-addressed, like page images
    unknown = client.get('/api/knowledge/pdf', params={'sha256': '0' * 64}, headers=GOOD)
    assert unknown.status_code == 404 and unknown.json()['code'] == 'source_not_local'
    assert client.get('/api/knowledge/pdf', params={'sha256': digest(swapped)}, headers=GOOD).status_code == 404
    assert client.get('/api/knowledge/pdf', params={'sha256': digest(PDF)}, headers={'origin': ORIGIN}).status_code == 403
    for hostile in ('../../original/source.pdf', '..%2F..%2Fsecret', 'C:/Windows/win.ini', digest(PDF).upper()):
        refused = client.get('/api/knowledge/pdf', params={'sha256': hostile}, headers=GOOD)
        assert refused.status_code in (404, 422) and refused.headers['content-type'].startswith('application/json')
    # only the sha256 identifier is accepted; a client path is never read
    assert client.get('/api/knowledge/pdf', params={'path': str(root / 'later.pdf')}, headers=GOOD).status_code == 422


def test_symlinked_pdfs_are_not_indexed(tmp_path):
    outside = tmp_path.parent / (tmp_path.name + '-outside.pdf')
    outside.write_bytes(b'%PDF-1.7 outside')
    root = tmp_path / 'dataset'
    root.mkdir()
    try:
        os.symlink(outside, root / 'link.pdf')
    except OSError:
        pytest.skip('symlinks need extra privileges on this machine')
    assert browser(tmp_path, source_roots=[root]).sources_index.pdf(digest(b'%PDF-1.7 outside')) is None


class FakeRenderer:
    page_count = 4
    opened = []

    def __init__(self, path):
        FakeRenderer.opened.append(path)

    def png(self, number, scale):
        return b'\x89PNG synthetic'

    def size(self, number):
        return (612, 792)

    def rotation(self, number):
        return 0


def test_a_same_size_same_mtime_content_swap_is_refused(tmp_path, monkeypatch):
    root = tmp_path / 'dataset'
    root.mkdir()
    original = b'%PDF-1.7 synthetic AAAA'
    target = root / 'a.pdf'
    target.write_bytes(original)
    knowledge = browser(tmp_path, source_roots=[root])
    assert knowledge.sources_index.locate(digest(original)) is not None  # indexed, not yet rendered
    stamp = target.stat()
    target.write_bytes(b'%PDF-1.7 synthetic BBBB')  # same size
    os.utime(target, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))  # same mtime: the stat cache cannot notice
    assert target.stat().st_size == stamp.st_size and target.stat().st_mtime_ns == stamp.st_mtime_ns
    client, app = web(tmp_path, knowledge)
    monkeypatch.setattr(app, 'PageRenderer', FakeRenderer)
    refused = client.get('/api/knowledge/page', params={'sha256': digest(original), 'page': 1}, headers=GOOD)
    assert refused.status_code == 404 and refused.json()['code'] == 'source_not_local'


def test_repeat_page_requests_do_not_rehash_or_rescan(tmp_path, monkeypatch):
    root = tmp_path / 'dataset'
    root.mkdir()
    data = b'%PDF-1.7 synthetic repeat'
    (root / 'r.pdf').write_bytes(data)
    knowledge = browser(tmp_path, source_roots=[root])
    client, app = web(tmp_path, knowledge)
    monkeypatch.setattr(app, 'PageRenderer', FakeRenderer)
    FakeRenderer.opened = []
    params = {'sha256': digest(data), 'page': 1}
    assert client.get('/api/knowledge/page', params=params, headers=GOOD).status_code == 200
    calls = {'digest': 0, 'scan': 0}
    real_digest, real_scan = browse().digest, knowledge.sources_index._scan
    monkeypatch.setattr(browse(), 'digest', lambda b: calls.__setitem__('digest', calls['digest'] + 1) or real_digest(b))
    monkeypatch.setattr(knowledge.sources_index, '_scan',
                        lambda: calls.__setitem__('scan', calls['scan'] + 1) or real_scan())
    for page in (2, 3):
        assert client.get('/api/knowledge/page', params={**params, 'page': page}, headers=GOOD).status_code == 200
    assert calls == {'digest': 0, 'scan': 0} and len(FakeRenderer.opened) == 1
    # a sha256 not yet indexed triggers a rescan, and a newly added file is found
    added = b'%PDF-1.7 synthetic added later'
    (root / 'later.pdf').write_bytes(added)
    assert knowledge.sources_index.pdf(digest(added)).read_bytes() == added and calls['scan'] >= 1


def paged(rows, total=None):
    """Fake PostgREST that honours offset/limit like the real thing and records each request."""
    seen = []

    def handler(request):
        seen.append(request)
        params = request.url.params
        start, size = int(params.get('offset', 0)), int(params.get('limit', len(rows)))
        return httpx.Response(200, json=rows[start:start + size],
                              headers={'content-range': f'{start}-{start + size - 1}/{len(rows) if total is None else total}'})
    handler.requests = seen
    return handler


def doc_row(n, sha, title, pages):
    return {'chunk_id': f'{n:064x}', 'byte_sha256': sha, 'documents': {'title': title} if title else None,
            'source_spans': [{'page': p} for p in pages], 'release_chunks': [{'release_id': 'rel-1'}]}


def test_documents_group_chunks_by_source_hash_then_title(tmp_path):
    upload_id = intake().create_upload(tmp_path, PDF, kind='handbook', title='Synthetic code', edition='2026')['upload_id']
    have = digest(PDF)
    rows = [doc_row(1, have, 'Handbook', [4, 2]), doc_row(2, have, 'Handbook', [9]), doc_row(3, 'a' * 64, 'Missing PDF', []),
            doc_row(4, None, 'Title only', [1]), doc_row(5, None, 'Title only', [3]), doc_row(6, None, None, [1])]
    fake = paged(rows)
    knowledge = browser(tmp_path, local=lambda: browse().Rest('local', 'http://127.0.0.1:54321', 'k',
                                                               httpx.Client(transport=httpx.MockTransport(fake))))
    result = knowledge.documents('local:rel-1')
    assert result['source'] == 'local:rel-1' and result['truncated'] is False
    assert result['documents'] == [
        {'document_key': have, 'title': 'Handbook', 'source_sha256': have, 'chunk_count': 2, 'pages': [2, 9], 'pdf_available': True},
        {'document_key': 'a' * 64, 'title': 'Missing PDF', 'source_sha256': 'a' * 64, 'chunk_count': 1, 'pages': [], 'pdf_available': False},
        {'document_key': 'Title only', 'title': 'Title only', 'chunk_count': 2, 'pages': [1, 3], 'pdf_available': False}]
    assert upload_id and 'text' not in fake.requests[0].url.params['select'].split(',')  # no chunk text is fetched


def test_documents_page_through_chunks_and_report_truncation(tmp_path, monkeypatch):
    rows = [doc_row(n, 'c' * 64, 'Big', [n]) for n in range(1, 8)]
    fake = paged(rows)
    monkeypatch.setattr(browse(), 'DOCUMENT_BATCH', 2)
    monkeypatch.setattr(browse(), 'MAX_DOCUMENT_CHUNKS', 4)
    knowledge = browser(tmp_path, local=lambda: browse().Rest('local', 'http://127.0.0.1:54321', 'k',
                                                               httpx.Client(transport=httpx.MockTransport(fake))))
    result = knowledge.documents('local:rel-1')
    assert result['truncated'] is True and result['documents'][0]['chunk_count'] == 4
    assert [r.url.params['offset'] for r in fake.requests] == ['0', '2']
    monkeypatch.setattr(browse(), 'MAX_DOCUMENT_CHUNKS', 50)
    assert knowledge.documents('local:rel-1')['truncated'] is False


def test_hosted_documents_stay_anon_and_get_only(tmp_path):
    fake = paged([doc_row(1, 'd' * 64, 'Online', [1])])
    knowledge = browser(tmp_path, hosted=fake, hosted_env=env_file(tmp_path))
    result = knowledge.documents('hosted:rel-1')
    assert result['documents'][0]['title'] == 'Online'
    assert fake.requests and all(r.method == 'GET' for r in fake.requests)
    for request in fake.requests:
        assert request.headers['apikey'] == ANON and SERVICE not in str(dict(request.headers)) + str(request.url)
        assert request.url.host == 'synthetic.supabase.co' and request.url.params['release_chunks.release_id'] == 'eq.rel-1'


def test_document_filter_on_chunks_matches_exactly_by_hash_or_title(tmp_path):
    fake = Recorder({'chunks': [ROW]})
    knowledge = browser(tmp_path, local=lambda: browse().Rest('local', 'http://127.0.0.1:54321', 'k',
                                                               httpx.Client(transport=httpx.MockTransport(fake))))
    knowledge.chunks('local:rel-1', document='b' * 64)
    assert fake.requests[0].url.params['byte_sha256'] == 'eq.' + 'b' * 64
    knowledge.chunks('local:rel-1', document='Code, (2026)*')
    params = fake.requests[1].url.params
    assert params['documents.title'] == 'eq.Code, (2026)*' and 'documents!inner' in params['select']
    for bad in ('x' * 301, 'a\nb'):
        with pytest.raises(ValueError) as caught:
            knowledge.chunks('local:rel-1', document=bad)
        assert caught.value.code == 'bad_request'


def test_package_documents_and_document_filter(reviewed, tmp_path):  # noqa: F811
    root, _ = reviewed
    upload_id = intake().create_upload(tmp_path, PDF, kind='handbook', title='Synthetic code', edition='2026')['upload_id']
    build = importlib.import_module('backend.bintanong_tools.knowledge_update.build')
    build.build(root, tmp_path / upload_id / 'package', encoder=SyntheticEncoder())
    knowledge = browser(tmp_path)
    listed = knowledge.documents('package:' + upload_id)['documents']
    assert len(listed) == 1 and listed[0]['chunk_count'] == 1 and isinstance(listed[0]['pdf_available'], bool)
    assert knowledge.chunks('package:' + upload_id, document=listed[0]['document_key'])['total'] == 1
    assert knowledge.chunks('package:' + upload_id, document='no such document')['total'] == 0


def test_documents_route_needs_token_validates_source_and_reports_unavailable(tmp_path):
    client, _ = web(tmp_path, browser(tmp_path))
    assert client.get('/api/knowledge/documents', params={'source': 'local:rel-1'}, headers={'origin': ORIGIN}).status_code == 403
    unknown = client.get('/api/knowledge/documents', params={'source': 'remote:rel'}, headers=GOOD)
    assert unknown.status_code in (404, 422) and unknown.json()['code'] == 'unknown_source'
    down = client.get('/api/knowledge/documents', params={'source': 'local:rel-1'}, headers=GOOD)
    assert down.status_code == 503 and down.json()['code'] == 'local_unavailable'
    hosted = client.get('/api/knowledge/documents', params={'source': 'hosted:rel-1'}, headers=GOOD)
    assert hosted.status_code == 503 and hosted.json()['code'] == 'hosted_not_configured'
    chunks = client.get('/api/knowledge/chunks', params={'source': 'local:rel-1', 'document': 'x' * 301}, headers=GOOD)
    assert chunks.status_code == 422


def test_knowledge_pages_are_cacheable_and_renderers_are_bounded(tmp_path, monkeypatch):
    root = tmp_path / 'dataset'
    root.mkdir()
    blobs = [b'%PDF-1.7 synthetic cache ' + str(n).encode() for n in range(5)]
    for n, blob in enumerate(blobs):
        (root / f'{n}.pdf').write_bytes(blob)
    client, app = web(tmp_path, browser(tmp_path, source_roots=[root]))
    closed = []
    FakeRenderer.opened = []
    monkeypatch.setattr(FakeRenderer, 'close', lambda self: closed.append(self), raising=False)
    monkeypatch.setattr(app, 'PageRenderer', FakeRenderer)
    first = client.get('/api/knowledge/page', params={'sha256': digest(blobs[0]), 'page': 1}, headers=GOOD)
    assert first.headers['cache-control'] == 'private, max-age=300'
    client.get('/api/knowledge/page', params={'sha256': digest(blobs[0]), 'page': 2}, headers=GOOD)
    assert len(FakeRenderer.opened) == 1  # a second view of the same document reuses its renderer
    for blob in blobs[1:]:
        client.get('/api/knowledge/page', params={'sha256': digest(blob), 'page': 1}, headers=GOOD)
    assert len(FakeRenderer.opened) == 5 and len(closed) == 1  # only four stay open
    missing = client.get('/api/knowledge/page', params={'sha256': '0' * 64, 'page': 1}, headers=GOOD)
    assert 'cache-control' not in missing.headers or 'max-age' not in missing.headers['cache-control']


REVIEWED = ('{"evidence_sha256":"' + 'e' * 64 + '","fields":[{"name":"title","value":"Shifting of programs","source_blank":false},'
            '{"name":"requirements","value":["Good moral standing","Grade of 2.0 or better"],"source_blank":false},'
            '{"name":"fee","value":"","source_blank":true},'
            '{"name":"segmentation","value":[{"kind":"page_furniture","text":"p. 4"}],"source_blank":false,"field_kind":"body_partition","field_role":"extraction_metadata"},'
            '{"name":"arrows","value":[{"from":"A","label":"Submit form","to":"END"}],"source_blank":false,"field_kind":"arrows"}],'
            '"source_limits":[{"issue":"clipped_text","affected_claims":["fee amount"]}]}')


def test_reviewed_policy_json_becomes_readable_prose():
    display, section = browse().readable_chunk(REVIEWED)
    assert display.splitlines() == ['Title: Shifting of programs', 'Requirements: Good moral standing; Grade of 2.0 or better',
        'Fee: (blank in the source)', 'Arrows: A, Submit form, END',
        'Known source problem: clipped text (affects: fee amount)']
    assert section == 'Shifting of programs'
    assert 'evidence_sha256' not in display and '{' not in display


@pytest.mark.parametrize('text', ['Submit the form.', '{"not":"reviewed"}', '{"fields":"x"}', '[1,2]', '{"fields":[{"value":1}]}', '{bad'])
def test_other_chunk_text_is_left_alone(text):
    assert browse().readable_chunk(text) == (None, None)


def test_chunks_carry_display_text_beside_the_raw_text(tmp_path):
    row = {**ROW, 'text': REVIEWED, 'section_path': []}
    fake = Recorder({'chunks': [row]})
    knowledge = browser(tmp_path, local=lambda: browse().Rest('local', 'http://127.0.0.1:54321', 'k',
                                                               httpx.Client(transport=httpx.MockTransport(fake))))
    chunk = knowledge.chunks('local:rel-1')['chunks'][0]
    assert chunk['text'] == REVIEWED and chunk['display_text'].startswith('Title: Shifting of programs')
    assert chunk['section'] == 'Shifting of programs'
    plain = Recorder({'chunks': [ROW]})
    knowledge = browser(tmp_path, local=lambda: browse().Rest('local', 'http://127.0.0.1:54321', 'k',
                                                               httpx.Client(transport=httpx.MockTransport(plain))))
    chunk = knowledge.chunks('local:rel-1')['chunks'][0]
    assert chunk['display_text'] is None and chunk['section'] == 'Part I > Forms'


@pytest.mark.parametrize('text', ['{"fields":[{"name":"title","value":"x"}],"source_limits":5}',
    '{"fields":[{"name":"title","value":"x"}],"source_limits":[5,"a",null,{"issue":3}]}',
    '{"fields":[{"name":"title","value":{"a":[1,{"b":null}]},"source_blank":false}]}',
    '{"fields":[{"name":"title","value":"x","source_blank":"yes"},{"name":7}]}',
    '{"fields":[{"name":"title","value":"x"}],"source_limits":[{"issue":"gap","affected_claims":5}]}',
    pytest.param('{"a":' * 5000 + '1' + '}' * 5000, id='deep-object'), pytest.param('{' + '[' * 100000, id='deep-array')])
def test_odd_stored_chunks_never_break_the_listing(text):
    display, section = browse().readable_chunk(text)  # must not raise
    assert display is None or isinstance(display, str)
    assert section is None or isinstance(section, str)


def test_one_odd_chunk_does_not_hide_the_others(tmp_path):
    odd = {**ROW, 'chunk_id': 'd' * 64, 'text': '{"fields":[{"name":"title","value":"x"}],"source_limits":5}'}
    fake = Recorder({'chunks': [odd, ROW]})
    knowledge = browser(tmp_path, local=lambda: browse().Rest('local', 'http://127.0.0.1:54321', 'k',
                                                               httpx.Client(transport=httpx.MockTransport(fake))))
    rows = knowledge.chunks('local:rel-1')['chunks']
    assert [r['chunk_id'] for r in rows] == ['d' * 64, 'c' * 64] and rows[0]['text'] == odd['text']


def pages_of(rows, size):
    """Fake PostgREST whose server caps every response at `size` rows, whatever limit is asked."""
    seen = []

    def handler(request):
        seen.append(request)
        start = int(request.url.params.get('offset', 0))
        return httpx.Response(200, json=rows[start:start + size],
                              headers={'content-range': f'{start}-{start + size - 1}/{len(rows)}'})
    handler.requests = seen
    return handler


def test_documents_keep_paging_when_the_server_caps_responses_below_the_batch(tmp_path):
    rows = [doc_row(n, 'c' * 64, 'Big', [1]) for n in range(1, 1201)]
    fake = pages_of(rows, 500)
    knowledge = browser(tmp_path, local=lambda: browse().Rest('local', 'http://127.0.0.1:54321', 'k',
                                                               httpx.Client(transport=httpx.MockTransport(fake))))
    result = knowledge.documents('local:rel-1')
    assert result['documents'][0]['chunk_count'] == 1200 and result['truncated'] is False
    assert [r.url.params['offset'] for r in fake.requests] == ['0', '500', '1000']


def test_documents_stop_on_an_empty_page_when_no_total_is_reported(tmp_path):
    def handler(request):
        start = int(request.url.params.get('offset', 0))
        return httpx.Response(200, json=[doc_row(n, 'c' * 64, 'Big', [1]) for n in range(start, start + 3)] if start < 6 else [])
    knowledge = browser(tmp_path, local=lambda: browse().Rest('local', 'http://127.0.0.1:54321', 'k',
                                                               httpx.Client(transport=httpx.MockTransport(handler))))
    assert knowledge.documents('local:rel-1')['documents'][0]['chunk_count'] == 6
