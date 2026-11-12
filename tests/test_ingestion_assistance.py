import copy

import pytest

from backend.bintanong_tools.knowledge_update import advisory


class FakeProvider:
    provider = 'synthetic'
    model = 'vision-fixture'

    def __init__(self, result=None):
        self.result = result or {'outcome': 'proposal', 'proposed_value': '15 working days',
                                 'rationale': 'Compare the printed number.'}
        self.calls = []

    def inspect(self, request):
        self.calls.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return copy.deepcopy(self.result)


def inputs():
    doc = {'id': 'handbook', 'sha256': 'a' * 64}
    row = {'id': 'rule-1', 'document_id': doc['id'], 'findings': ['ocr_warning'],
           'fields': [{'name': 'body', 'original_value': '5 working days',
                       'reviewed_value': '5 working days', 'decision': 'pending',
                       'locator': {'physical_pages': [1], 'field': 'body'}, 'spans': [],
                       'source_blank': False}]}
    return [row], [doc]


def test_proposal_is_bound_and_never_changes_a_decision():
    rows, docs = inputs()
    before = copy.deepcopy(rows)
    provider = FakeProvider()
    result = advisory.assist(rows, docs, provider, lambda doc, page: b'original page', mode='all')
    assert rows == before
    field = result[0]['fields'][0]
    assert field['proposed_value'] == '15 working days'
    assert field['reviewed_value'] == '5 working days'
    assert field['decision'] == 'pending'
    assert provider.calls[0]['images'] == [{'page': 1, 'png': b'original page'}]
    advisory.validate(result, docs)
    for damage in ['source', 'page', 'item', 'candidate']:
        bad = copy.deepcopy(result)
        if damage == 'source':
            bad[0]['fields'][0]['assistance']['binding']['source_sha256'] = 'b' * 64
        elif damage == 'page':
            bad[0]['fields'][0]['locator']['physical_pages'] = [2]
        elif damage == 'item':
            bad[0]['id'] = 'another'
        else:
            bad[0]['fields'][0]['original_value'] = 'different candidate'
        with pytest.raises(ValueError, match='stale'):
            advisory.validate(bad, docs)


@pytest.mark.parametrize('result', [TimeoutError('secret-token'), RuntimeError('secret-token'),
    {'outcome': 'proposal', 'proposed_value': 15, 'rationale': 'wrong type'},
    {'outcome': 'proposal', 'proposed_value': '15', 'approved': True},
    {'outcome': 'accepted'}, 'not JSON'])
def test_failures_and_privileged_metadata_leave_manual_review(result):
    rows, docs = inputs()
    out = advisory.assist(rows, docs, FakeProvider(result), lambda d, p: b'image', mode='all')
    field = out[0]['fields'][0]
    assert field['decision'] == 'pending'
    assert field['reviewed_value'] == '5 working days'
    assert field['assistance']['outcome'] == 'failed'
    assert 'secret-token' not in str(out)
    assert 'proposed_value' not in field


@pytest.mark.parametrize('outcome', ['no_change', 'uncertain'])
def test_nonproposal_is_not_acceptance(outcome):
    rows, docs = inputs()
    field = advisory.assist(rows, docs, FakeProvider({'outcome': outcome, 'rationale': 'Manual check'}),
                           lambda d, p: b'image', mode='all')[0]['fields'][0]
    assert field['decision'] == 'pending' and 'proposed_value' not in field


@pytest.mark.parametrize('mode,pages,count', [('none', [], 0), ('all', [], 1),
    ('flagged', [], 1), ('selected', [1], 1), ('selected', [2], 0)])
def test_selection(mode, pages, count):
    rows, docs = inputs()
    provider = FakeProvider()
    advisory.assist(rows, docs, provider, lambda d, p: b'image', mode=mode, pages=pages)
    assert len(provider.calls) == count


def test_rendering_failure_and_literal_blank_do_not_create_content():
    rows, docs = inputs()
    def broken(d, p):
        raise ValueError('page unavailable')
    provider = FakeProvider()
    field = advisory.assist(rows, docs, provider, broken, mode='all')[0]['fields'][0]
    assert not provider.calls and field['assistance']['outcome'] == 'failed'
    rows[0]['fields'][0].update(original_value='', reviewed_value='', source_blank=True)
    field = advisory.assist(rows, docs, provider, lambda d, p: b'image', mode='all')[0]['fields'][0]
    assert field['decision'] == 'pending' and 'proposed_value' not in field


def test_prepare_proposal_reopen_human_correction_and_build(tmp_path, monkeypatch):
    import json
    from backend.bintanong_tools.knowledge_update.prepare import prepare, load_packet
    from backend.bintanong_tools.knowledge_update.review import ReviewSession
    from backend.bintanong_tools.knowledge_update.build import build
    from backend.bintanong_tools.knowledge_update.verify import verify
    from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
    from backend.bintanong_tools.prospectus_review_gui import render
    from test_knowledge_update_prepare import manifest
    from test_knowledge_update_review import answer
    from test_knowledge_update_build import SyntheticEncoder
    from test_policy_chunks import item, raw_document
    from test_prospectus_ingestion import synthetic_converter

    class Renderer:
        def __init__(self, path): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def png(self, page, scale): return b'original image'
    monkeypatch.setattr(render, 'PageRenderer', Renderer)
    path, source, spec = manifest(tmp_path)
    spec['build'] = {'reading_ids': ['handbook:text-0'],
        'assignments': [{'reading_id': 'handbook:text-0', 'subject_id': 'time', 'basis_ref': 'fixture'}],
        'claim_reviews': [{'subject_id': 'time', 'claim': 'time', 'finding': 'visible_fields',
            'field_refs': [{'reading_id': 'handbook:text-0', 'field_name': 'body'}],
            'basis_ref': 'fixture', 'basis_reading_id': 'handbook:text-0'}]}
    path.write_text(json.dumps(spec))
    root = tmp_path / 'packet'
    provider = FakeProvider()
    packet = prepare(path, root, assist_provider=provider, assist_mode='all',
        converter=synthetic_converter(monkeypatch, InputSnapshot(source),
            raw_document([item('5 working days')], pages=1)))
    assert packet['items'][0]['fields'][0]['decision'] == 'pending'
    assert load_packet(root) == packet
    assert prepare(path, root, assist_provider=provider, assist_mode='all') == packet
    assert len(provider.calls) == 1
    with pytest.raises(ValueError, match='assistance'):
        prepare(path, root)
    assert not (root / 'review/decisions.jsonl').exists()
    with pytest.raises(ValueError):
        build(root, tmp_path / 'premature-package', encoder=SyntheticEncoder())
    with ReviewSession(root, 'Synthetic researcher') as review:
        command = answer(packet)
        command['fields']['body'] = {'decision': 'corrected', 'value': '15 working days'}
        review.save(command)
        assert review.state()['items'][0]['fields'][0]['reviewed_value'] == '15 working days'
    build(root, tmp_path / 'package', encoder=SyntheticEncoder())
    assert verify(tmp_path / 'package', packet_root=root)['verified']


def test_vision_transport_sends_original_images_and_no_credentials_in_result():
    import json
    import httpx
    from backend.bintanong_tools.knowledge_update.vision import VisionProvider
    def handle(req):
        assert req.url.path == '/v1/chat/completions'
        value = json.loads(req.content)
        assert value['response_format']['type'] == 'json_schema'
        schema = value['response_format']['json_schema']['schema']
        assert schema['oneOf'][0]['properties']['outcome'] == {'const': 'proposal'}
        assert 'proposed_value' not in schema['oneOf'][1]['properties']
        assert value['messages'][1]['content'][2]['image_url']['url'].startswith('data:image/png;base64,')
        assert req.headers['authorization'] == 'Bearer synthetic-test-only'
        return httpx.Response(200, json={'choices': [{'message': {'content': json.dumps({
            'outcome': 'uncertain', 'rationale': 'The image is unclear.'})}}]})
    provider = VisionProvider('http://127.0.0.1:8080/v1', 'gemma-4-E4B',
        key='synthetic-test-only', transport=httpx.MockTransport(handle))
    rows, docs = inputs()
    out = advisory.assist(rows, docs, provider, lambda d, p: b'png', mode='all')
    assert out[0]['fields'][0]['assistance']['outcome'] == 'uncertain'
    assert 'synthetic-test-only' not in str(out)
