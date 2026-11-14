"""Phase 11 uploads over HTTP (master 15.1, 16.1): raw body -> capped read -> validated type -> extraction ->
pending rows -> the student's confirmation -> session facts. Synthetic courses and grades only."""
import json

import pytest
from fastapi.testclient import TestClient

from backend.bintanong_api.app import ApiServices, ApiSettings, create_app
from backend.bintanong_api.chat import CurriculumOption
from backend.bintanong_private_context.grades import extract_grade_rows
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_private_context.uploads import UploadRejected, validate_upload
from test_api_presentation import answer_for
from test_private_context_grades import CATALOG, grade_pdf

ORIGIN = 'https://bintanong.example'
CURRICULA = (CurriculumOption('bscs', 'bscs-2018', 'BS Computer Science', 'BSCS 2018'),)
LABELS = {'cc-105': 'CC 5/L', 'gec-1': 'GEC 1'}
SCOPE = {'programId': 'bscs', 'curriculumId': 'bscs-2018'}
PDF = grade_pdf([('CC 5/L', 'Information Management', '1.75', 'Passed'), ('GEC 1', 'Understanding Self', '2.00', '')])


def extract(data, program_id, curriculum_id):
    return extract_grade_rows(validate_upload(data), CATALOG, program_id=program_id, curriculum_id=curriculum_id)


class Recording:
    def __init__(self):
        self.contexts = []

    async def run(self, text, ctx, *, routed_sink, progress):
        self.contexts.append(ctx)
        return answer_for_rag


answer_for_rag = answer_for('RAG')


def build(store=None, extractor=extract, max_upload_bytes=None, pipeline=None):
    store = SessionStore() if store is None else store
    settings = ApiSettings(allowed_origins=(ORIGIN,)) if max_upload_bytes is None else \
        ApiSettings(allowed_origins=(ORIGIN,), max_upload_bytes=max_upload_bytes)
    services = ApiServices(sessions=store, curricula=CURRICULA, pipeline=pipeline, extract_rows=extractor,
                           course_labels=LABELS)
    return create_app(services, settings), store


def client(app):
    return TestClient(app, base_url='https://testserver', headers={'Origin': ORIGIN})


def upload(c, data=PDF.data, **scope):
    return c.post('/uploads', params=scope or SCOPE, content=data,
                  headers={'Content-Type': 'application/octet-stream'})


def confirm(c, upload_id, *decisions):
    return c.post(f'/uploads/{upload_id}/confirm',
                  json={'decisions': [dict(rowId=r, courseId=k, state=s) for r, k, s in decisions]})


def test_upload_returns_pending_rows_with_printed_labels_and_marks():
    app, store = build()
    response = upload(client(app))
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['uploadId'].startswith('upl-')
    assert [(r['printedCode'], [c['label'] for c in r['courses']], r['marks']) for r in data['rows']] == [
        ('CC 5/L', ['CC 5/L'], ['1.75']), ('GEC 1', ['GEC 1'], ['2.00'])]
    assert all(r['rowId'] for r in data['rows'])


def test_confirmed_rows_become_facts_in_the_next_chat_turn():
    pipeline = Recording()
    app, _ = build(pipeline=pipeline)
    c = client(app)
    data = upload(c).json()
    row = data['rows'][0]
    response = confirm(c, data['uploadId'], (row['rowId'], 'cc-105', 'passed'))
    assert response.status_code == 200
    assert response.json() == {'facts': [{'courseId': 'cc-105', 'label': 'CC 5/L', 'state': 'passed'}]}
    c.post('/chat', json=dict(id='chat', trigger='submit-message', **SCOPE,
                              messages=[dict(id='m1', role='user', parts=[dict(type='text', text='Can I take X?')])]))
    assert [(f.course_id, f.state) for f in pipeline.contexts[0].facts] == [('cc-105', 'passed')]


@pytest.mark.parametrize('scope, code', [({'programId': 'bscs'}, 'incomplete_scope'),
                                         ({'programId': 'bscs', 'curriculumId': 'other'}, 'unknown_curriculum')])
def test_upload_needs_a_listed_curriculum(scope, code):
    app, _ = build()
    response = upload(client(app), **scope)
    assert (response.status_code, response.json()) == (422, {'error': code})


def test_upload_without_scope_is_refused():
    app, _ = build()
    response = client(app).post('/uploads', content=PDF.data)
    assert (response.status_code, response.json()) == (422, {'error': 'incomplete_scope'})


def test_unsupported_bytes_are_refused_by_type_sniffing():
    app, store = build()
    response = upload(client(app), data=b'GIF89a not allowed')
    assert (response.status_code, response.json()) == (422, {'error': 'unsupported_type'})


def test_oversized_body_is_refused_with_413():
    app, _ = build(max_upload_bytes=100)
    response = upload(client(app), data=PDF.data)
    assert (response.status_code, response.json()) == (413, {'error': 'too_large'})


def test_signed_bytes_reach_the_isolated_extractor_unparsed():
    # Security review S5: PDF/image parsers run only inside the bounded extractor job, never in the API process.
    seen = []

    def refuse(data, *_):
        seen.append(data)
        raise UploadRejected('unreadable')
    app, _ = build(extractor=refuse)
    response = upload(client(app), data=b'%PDF-1.7 truncated')
    assert (response.status_code, response.json()) == (422, {'error': 'unreadable'})
    assert seen == [b'%PDF-1.7 truncated']


def test_uploads_past_the_parallel_limit_are_refused_as_busy():
    # Security review S6: each upload starts a parser process, so their number is bounded.
    import threading
    started, release = threading.Event(), threading.Event()

    def blocking(data, program_id, curriculum_id):
        started.set()
        release.wait(10)
        return extract(data, program_id, curriculum_id)
    store = SessionStore()
    app = create_app(ApiServices(sessions=store, curricula=CURRICULA, extract_rows=blocking, course_labels=LABELS),
                     ApiSettings(allowed_origins=(ORIGIN,), max_parallel_uploads=1))
    first = []
    with client(app) as c:
        worker = threading.Thread(target=lambda: first.append(upload(c)))
        worker.start()
        assert started.wait(10)
        busy = upload(client(app))
        release.set()
        worker.join(10)
        after = upload(c)
    assert (busy.status_code, busy.json()) == (503, {'error': 'uploads_busy'})
    assert first[0].status_code == 200 and after.status_code == 200


def test_extractor_refusal_is_a_typed_error():
    def refuse(*_):
        raise UploadRejected('photo_ocr_unavailable')
    app, _ = build(extractor=refuse)
    response = upload(client(app))
    assert (response.status_code, response.json()) == (422, {'error': 'photo_ocr_unavailable'})


def test_confirming_a_course_outside_the_row_is_refused_without_echoing_grades():
    app, store = build()
    c = client(app)
    data = upload(c).json()
    response = confirm(c, data['uploadId'], (data['rows'][0]['rowId'], 'gec-1', 'passed'))
    assert (response.status_code, response.json()) == (422, {'error': 'course_not_in_row'})
    assert '1.75' not in response.text


def test_invalid_state_is_a_plain_422():
    app, _ = build()
    c = client(app)
    data = upload(c).json()
    assert confirm(c, data['uploadId'], (data['rows'][0]['rowId'], 'cc-105', 'aced')).status_code == 422


def test_unknown_upload_id_is_404():
    app, _ = build()
    c = client(app)
    upload(c)
    assert confirm(c, 'upl-0000', ('row-1-1', 'cc-105', 'passed')).json() == {'error': 'unknown_upload'}
    assert c.delete('/uploads/upl-0000').status_code == 404


def test_delete_upload_removes_its_facts():
    app, store = build()
    c = client(app)
    data = upload(c).json()
    confirm(c, data['uploadId'], (data['rows'][0]['rowId'], 'cc-105', 'passed'))
    assert c.delete(f"/uploads/{data['uploadId']}").status_code == 204
    credential = c.cookies['__Host-bintanong_session']
    assert store.resolve(credential).facts == ()


def test_session_b_cannot_confirm_or_delete_session_a_upload():
    app, store = build()
    a, b = client(app), client(app)
    data = upload(a).json()
    row = data['rows'][0]['rowId']
    assert confirm(b, data['uploadId'], (row, 'cc-105', 'passed')).status_code == 404
    assert b.delete(f"/uploads/{data['uploadId']}").status_code == 404
    assert store.resolve(a.cookies['__Host-bintanong_session']).pending is not None


def test_expired_session_loses_its_upload():
    class Clock:
        now = 0.0

        def __call__(self):
            return self.now
    clock = Clock()
    app, _ = build(SessionStore(idle_seconds=60, clock=clock))
    c = client(app)
    data = upload(c).json()
    clock.now = 61
    response = confirm(c, data['uploadId'], (data['rows'][0]['rowId'], 'cc-105', 'passed'))
    assert response.status_code == 404


def test_upload_requires_an_allowed_origin():
    app, store = build()
    response = TestClient(app, base_url='https://testserver').post('/uploads', params=SCOPE, content=PDF.data)
    assert response.status_code == 403 and len(store) == 0


def test_upload_response_holds_no_file_text_beyond_codes_and_marks():
    app, _ = build()
    response = upload(client(app))
    assert 'Information Management' not in response.text and 'Passed' not in response.text
    json.loads(response.text)
