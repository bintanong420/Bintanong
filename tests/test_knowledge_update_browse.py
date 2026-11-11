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
    assert listed['unavailable']['hosted'].startswith('The public key sees no release on hosted.')


def test_hosted_settings_need_https_and_an_anon_key(tmp_path):
    with pytest.raises(ValueError) as caught:
        browse().hosted_settings(env_file(tmp_path, url='http://synthetic.supabase.co'))
    assert caught.value.code == 'hosted_settings'


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
    assert result == {'chunks': [{'chunk_id': 'c' * 64, 'text': 'Submit the form.', 'document_title': 'Synthetic code',
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
    assert index.find(digest(PDF)) == (tmp_path / upload_id / 'original/source.pdf').resolve()
    assert index.find(digest(other)) == (dataset / 'nested/prospectus.pdf').resolve()
    assert index.find('0' * 64) is None
    (dataset / 'nested/prospectus.pdf').write_bytes(b'%PDF-1.7 swapped')  # bytes changed after indexing
    assert index.find(digest(other)) is None
    with pytest.raises(ValueError):
        index.find('NOT-A-HASH')

    class FakeRenderer:
        page_count = 4

        def __init__(self, path):
            FakeRenderer.path = path

        def png(self, number, scale):
            return b'\x89PNG synthetic'

        def size(self, number):
            return (612, 792)

        def rotation(self, number):
            return 0

    client, app = web(tmp_path, knowledge)
    monkeypatch.setattr(app, 'PageRenderer', FakeRenderer)
    shown = client.get('/api/knowledge/page', params={'sha256': digest(PDF), 'page': 1}, headers=GOOD)
    assert shown.status_code == 200 and shown.headers['content-type'] == 'image/png'
    assert shown.headers['x-page-count'] == '4' and 'X-Page-Count' in shown.headers['access-control-expose-headers']
    missing = client.get('/api/knowledge/page', params={'sha256': '0' * 64, 'page': 1}, headers=GOOD)
    assert missing.status_code == 404 and missing.json()['error'] == 'source PDF not available locally'
    assert client.get('/api/knowledge/page', params={'sha256': digest(PDF), 'page': 1},
                      headers={'origin': ORIGIN}).status_code == 403


def test_symlinked_pdfs_are_not_indexed(tmp_path):
    outside = tmp_path.parent / (tmp_path.name + '-outside.pdf')
    outside.write_bytes(b'%PDF-1.7 outside')
    root = tmp_path / 'dataset'
    root.mkdir()
    try:
        os.symlink(outside, root / 'link.pdf')
    except OSError:
        pytest.skip('symlinks need extra privileges on this machine')
    assert browser(tmp_path, source_roots=[root]).sources_index.find(digest(b'%PDF-1.7 outside')) is None
