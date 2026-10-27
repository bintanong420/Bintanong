import copy
import json

import httpx
import pytest

from backend.bintanong_tools.knowledge_update import llamaparse


def pdf(tmp_path, pages=2):
    import pymupdf
    originals = tmp_path / 'originals'
    originals.mkdir(exist_ok=True)
    path = originals / 'source.pdf'
    with pymupdf.open() as doc:
        for _ in range(pages):
            doc.new_page(width=600, height=800).insert_text((30, 60), 'Submit the form.')
        doc.save(path)
    return path


class FakeParser:
    def __init__(self, fail=None):
        self.uploads, self.polls = [], []
        self.fail = fail

    def upload(self, source, pages, config):
        self.uploads.append(pages)
        return 'job-' + str(pages[0])

    def poll(self, job_id):
        self.polls.append(job_id)
        page = int(job_id.split('-')[-1])
        if page == self.fail:
            raise TimeoutError('never persist provider secret')
        return {'job': {'id': job_id, 'status': 'COMPLETED'}, 'items': {'pages': [{
            'page_number': page, 'page_width': 600, 'page_height': 800, 'success': True,
            'items': [{'type': 'text', 'value': 'Submit the form.',
                       'bbox': [{'x': 30, 'y': 40, 'w': 200, 'h': 30}]}]}]}}


def test_page_batches_resume_after_failure_without_duplicate_upload(tmp_path):
    source = pdf(tmp_path)
    parser = FakeParser(fail=2)
    root = tmp_path / 'parse'
    first = llamaparse.parse(source, root, pages=[1, 2], batch_size=1, client=parser)
    assert first['failed_pages'] == [2]
    assert parser.uploads == [[1], [2]]
    parser.fail = None
    second = llamaparse.parse(source, root, pages=[1, 2], batch_size=1, client=parser)
    assert second['failed_pages'] == []
    assert parser.uploads == [[1], [2]]
    assert parser.polls == ['job-1', 'job-2', 'job-2']
    assert 'never persist provider secret' not in str(second)
    with pytest.raises(ValueError, match='selection|source|configuration'):
        llamaparse.parse(source, root, pages=[1], batch_size=1, client=parser)


def test_llama_output_uses_same_pending_reviewer_and_build(tmp_path):
    import hashlib
    from backend.bintanong_tools.knowledge_update.prepare import prepare
    from backend.bintanong_tools.knowledge_update.review import ReviewSession
    from backend.bintanong_tools.knowledge_update.build import build
    from backend.bintanong_tools.knowledge_update.verify import verify
    from test_knowledge_update_build import SyntheticEncoder
    source = pdf(tmp_path, 1)
    result = tmp_path / 'parse'
    llamaparse.parse(source, result, pages=[1], client=FakeParser())
    data = (result / 'result.json').read_bytes()
    manifest = {'schema_version': 'bintanong-knowledge-update-v1', 'documents': [{
        'id': 'charter', 'kind': 'charter', 'title': 'Synthetic undergraduate service',
        'edition': 'synthetic', 'source': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'locator': 'synthetic:charter', 'parser_result': {'path': str(result / 'result.json'),
                                                      'sha256': hashlib.sha256(data).hexdigest()}}],
        'build': {'reading_ids': ['charter:llama-p1-i0'],
            'assignments': [{'reading_id': 'charter:llama-p1-i0', 'subject_id': 'forms', 'basis_ref': 'fixture'}],
            'claim_reviews': [{'subject_id': 'forms', 'claim': 'instruction', 'finding': 'visible_fields',
                'field_refs': [{'reading_id': 'charter:llama-p1-i0', 'field_name': 'body'}],
                'basis_ref': 'fixture', 'basis_reading_id': 'charter:llama-p1-i0'}]}}
    path = tmp_path / 'manifest.json'; path.write_text(json.dumps(manifest))
    root = tmp_path / 'packet'
    packet = prepare(path, root)
    field = packet['items'][0]['fields'][0]
    assert field['decision'] == 'pending' and field['original_value'] == 'Submit the form.'
    assert field['spans'][0]['extraction']['source_kind'] == 'llamaparse'
    with pytest.raises(ValueError):
        build(root, tmp_path / 'unreviewed', encoder=SyntheticEncoder())
    with ReviewSession(root, 'Synthetic researcher') as review:
        row = packet['items'][0]
        review.save({'revision': 0, 'operation_id': 'human-save', 'item_id': row['id'],
            'audience': 'undergraduate', 'reason': 'Compared with the printed source.',
            'companions': [], 'gaps': [], 'fields': {'body': {'decision': 'accepted', 'value': field['original_value']}}})
    build(root, tmp_path / 'package', encoder=SyntheticEncoder())
    assert verify(tmp_path / 'package', packet_root=root)['verified']


@pytest.mark.parametrize('status', [401, 403, 429, 500])
def test_api_failures_do_not_expose_credentials(status, tmp_path):
    client = llamaparse.LlamaParseClient('synthetic-secret', transport=httpx.MockTransport(
        lambda req: httpx.Response(status, text='synthetic-secret')))
    with pytest.raises(RuntimeError) as exc:
        client.upload(pdf(tmp_path), [1], {'tier': 'agentic', 'version': 'latest'})
    assert 'synthetic-secret' not in str(exc.value)


def test_http_v2_upload_poll_shape_and_one_based_ranges(tmp_path):
    def handle(req):
        assert req.headers['authorization'] == 'Bearer synthetic-secret'
        if req.method == 'POST':
            assert req.url.path == '/api/v2/parse/upload'
            assert b'"target_pages": "1,2"' in req.content
            return httpx.Response(200, json={'id': 'job-1', 'status': 'PENDING'})
        return httpx.Response(200, json={'job': {'id': 'job-1', 'status': 'COMPLETED'}, 'items': {'pages': []}})
    client = llamaparse.LlamaParseClient('synthetic-secret', transport=httpx.MockTransport(handle))
    assert client.upload(pdf(tmp_path), [1, 2], {'tier': 'agentic', 'version': 'latest'}) == 'job-1'
    assert client.poll('job-1')['job']['status'] == 'COMPLETED'


def test_partial_completed_batch_retries_only_missing_pages(tmp_path):
    source = pdf(tmp_path)
    parser = FakeParser()
    root = tmp_path / 'parse'
    first = llamaparse.parse(source, root, pages=[1, 2], batch_size=2, client=parser)
    assert first['failed_pages'] == [2]
    second = llamaparse.parse(source, root, pages=[1, 2], batch_size=2, client=parser)
    assert second['failed_pages'] == []
    assert parser.uploads == [[1, 2], [2]]
    assert [p['page_number'] for p in second['pages']] == [1, 2]


@pytest.mark.parametrize('damage', ['source', 'page', 'privileged'])
def test_wrong_source_page_and_approval_fields_are_refused(tmp_path, damage):
    from backend.bintanong_tools.knowledge_update.llama_items import items
    from backend.bintanong_tools.knowledge_update.files import digest
    source = pdf(tmp_path)
    result = llamaparse.parse(source, tmp_path / 'parse', pages=[1], client=FakeParser())
    doc = {'id': 'charter', 'kind': 'charter', 'source': str(source), 'sha256': digest(source.read_bytes())}
    if damage == 'source': result['source_sha256'] = '0' * 64
    if damage == 'page': result['pages'][0]['page_number'] = 2
    if damage == 'privileged': result['pages'][0]['items'][0]['approved'] = True
    with pytest.raises(ValueError):
        items(result, doc, source.read_bytes())


@pytest.mark.parametrize('damage', ['no_box', 'wrong_size', 'inverted_box'])
def test_missing_or_invalid_original_geometry_stays_manual(tmp_path, damage):
    from backend.bintanong_tools.knowledge_update.llama_items import items
    from backend.bintanong_tools.knowledge_update.files import digest
    source = pdf(tmp_path)
    result = llamaparse.parse(source, tmp_path / 'parse', pages=[1], client=FakeParser())
    page = result['pages'][0]
    if damage == 'no_box': page['items'][0]['bbox'] = None
    if damage == 'wrong_size': page['page_width'] = 999
    if damage == 'inverted_box': page['items'][0]['bbox'][0]['w'] = -20
    doc = {'id': 'charter', 'kind': 'charter', 'source': str(source), 'sha256': digest(source.read_bytes())}
    row = items(result, doc, source.read_bytes())[0]
    assert row['fields'][0]['decision'] == 'pending'
    assert row['fields'][0]['spans'] == []
    assert 'missing_original_geometry_build_withheld' in row['findings']


def test_heading_and_cross_page_table_payload_are_not_flattened(tmp_path):
    from backend.bintanong_tools.knowledge_update.llama_items import items
    from backend.bintanong_tools.knowledge_update.files import digest
    source = pdf(tmp_path)
    result = llamaparse.parse(source, tmp_path / 'parse', pages=[1, 2], batch_size=1, client=FakeParser())
    table = {'type': 'table', 'rows': [['Client', 'Agency', 'Fee', 'Time', 'Office'],
        ['Submit', 'Check', '25', '5 days', 'Registrar'], [None, 'Return', None, '10 days', 'Registrar']],
        'html': '<table><tr><td rowspan="2">Submit</td><td>Check</td></tr></table>',
        'merged_from_pages': [1, 2], 'parse_concerns': [{'type': 'header_row_in_body', 'details': 'Review continuation.'}]}
    result['pages'][0]['items'] = [
        {'type': 'heading', 'level': 1, 'value': 'Book I'},
        {'type': 'heading', 'level': 2, 'value': 'Undergraduate service'}, table]
    doc = {'id': 'charter', 'kind': 'charter', 'source': str(source), 'sha256': digest(source.read_bytes())}
    rows = items(result, doc, source.read_bytes())
    assert rows[2]['title'] == 'Book I / Undergraduate service'
    assert json.loads(rows[2]['fields'][0]['original_value']) == table
    assert rows[-1]['id'] in rows[2]['companions']
    assert all(f['decision'] == 'pending' for r in rows for f in r['fields'])


def test_failed_page_in_completed_response_does_not_discard_good_pages(tmp_path):
    class Partial(FakeParser):
        def poll(self, job_id):
            value = super().poll(job_id)
            value['items']['pages'].append({'page_number': 2, 'success': False})
            return value
    result = llamaparse.parse(pdf(tmp_path), tmp_path / 'parse', pages=[1, 2], client=Partial())
    assert result['failed_pages'] == [2]
    assert [p['page_number'] for p in result['pages']] == [1]
