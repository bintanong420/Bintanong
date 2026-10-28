"""Guest access is explicit; temporary course facts remain scoped to an opaque session."""
import pytest
from fastapi.testclient import TestClient

from backend.bintanong_api.app import ApiServices, ApiSettings, create_app
from backend.bintanong_api.session import ApiError, SESSION_COOKIE
from backend.bintanong_private_context.sessions import SessionStore
from test_api_auth import Auth
from test_api_stream import body
from test_api_uploads import CURRICULA, LABELS, ORIGIN, SCOPE, Recording, confirm, extract, upload


def guest_app(store=None):
    store = SessionStore() if store is None else store
    pipeline = Recording()
    app = create_app(ApiServices(sessions=store, auth=Auth(), curricula=CURRICULA,
        pipeline=pipeline, extract_rows=extract, course_labels=LABELS),
        ApiSettings(allowed_origins=(ORIGIN,), require_auth=True, allow_guests=True))
    return app, store, pipeline


def browser(app, token=None):
    headers = {'Origin': ORIGIN}
    if token is not None:
        headers['Authorization'] = token
    return TestClient(app, base_url='https://testserver', headers=headers)


def passed_course(client):
    pending = upload(client)
    assert pending.status_code == 200, pending.text
    pending = pending.json()
    row = pending['rows'][0]
    result = confirm(client, pending['uploadId'], (row['rowId'], 'cc-105', 'passed'))
    assert result.status_code == 200, result.text
    return pending['uploadId']


def test_guest_can_use_curricula_confirmed_pdf_chat_sources_and_clear_without_an_account():
    app, store, pipeline = guest_app()
    with browser(app) as client:
        assert client.get('/curricula').status_code == 200
        upload_id = passed_course(client)
        credential = client.cookies.get(SESSION_COOKIE)
        reply = client.post('/chat', json=body('A synthetic question', **SCOPE))
        assert reply.status_code == 200 and 'data: [DONE]' in reply.text
        assert [(f.course_id, f.state) for f in pipeline.contexts[-1].facts] == [('cc-105', 'passed')]
        # Sources are the validated answer's citations, never arbitrary private uploads.
        from test_api_uploads import answer_for_rag
        for card in answer_for_rag.citations:
            assert client.get('/sources/' + card.evidence_id).status_code == 200
        assert client.delete('/uploads/' + upload_id).status_code == 204
        assert store.resolve(credential).facts == ()
        assert client.delete('/session').status_code == 204
        assert store.resolve(credential) is None


def test_two_guest_sessions_cannot_share_confirmations_or_course_facts():
    app, store, pipeline = guest_app()
    with browser(app) as first, browser(app) as second:
        first_upload = passed_course(first)
        second_pending = upload(second).json()
        first_cookie = first.cookies.get(SESSION_COOKIE)
        second_cookie = second.cookies.get(SESSION_COOKIE)
        assert first_cookie != second_cookie
        assert second.delete('/uploads/' + first_upload).status_code == 404
        assert second.post('/chat', json=body('A synthetic question', **SCOPE)).status_code == 200
        assert pipeline.contexts[-1].facts == ()
        assert len(store.resolve(first_cookie).facts) == 1
        assert store.resolve(second_cookie).pending_upload_id == second_pending['uploadId']


@pytest.mark.parametrize('original,new', [(None, 'Bearer account-a'), ('Bearer account-a', None),
                                         ('Bearer account-a', 'Bearer account-b')])
def test_switching_guest_or_account_never_adopts_previous_private_facts(original, new):
    app, store, pipeline = guest_app()
    with browser(app, original) as first:
        passed_course(first)
        credential = first.cookies.get(SESSION_COOKIE)
    with browser(app, new) as second:
        second.cookies.update(first.cookies)
        assert second.post('/chat', json=body('A synthetic question', **SCOPE)).status_code == 200
        assert pipeline.contexts[-1].facts == ()
        assert second.cookies.get(SESSION_COOKIE) != credential
    identity = None if original is None else original.removeprefix('Bearer ')
    assert len(store.resolve(credential, account_id=identity).facts) == 1


@pytest.mark.parametrize('token', ['', 'Basic credentials', 'Bearer invalid', 'Bearer '])
def test_present_invalid_credentials_cannot_fall_back_to_a_guest(token):
    app, store, pipeline = guest_app()
    with browser(app, token) as client:
        response = client.get('/curricula')
    assert response.status_code == 401
    assert pipeline.contexts == [] and len(store) == 0


def test_guest_write_still_requires_the_original_same_origin_guards():
    app, store, _ = guest_app()
    with browser(app) as client:
        assert upload(client).status_code == 200
        credential = client.cookies.get(SESSION_COOKIE)
        response = client.delete('/session', headers={'Origin': 'https://foreign.example'})
        assert response.status_code == 403
        assert store.resolve(credential) is not None
        assert client.delete('/session', headers={'Sec-Fetch-Site': 'cross-site'}).status_code == 403


@pytest.mark.parametrize('status,code', [(403, 'psu_account_required'), (503, 'auth_unavailable')])
def test_guest_enabled_app_does_not_hide_supplied_token_verification_failures(status, code):
    class RefusingAuth:
        async def verify(self, token):
            raise ApiError(status, code)
    app = create_app(ApiServices(sessions=SessionStore(), auth=RefusingAuth()),
        ApiSettings(allowed_origins=(ORIGIN,), require_auth=True, allow_guests=True))
    with browser(app, 'Bearer supplied-token') as client:
        response = client.get('/curricula')
    assert response.status_code == status and response.json() == {'error': code}


@pytest.mark.parametrize('required', [True, False])
def test_guest_needs_no_auth_provider_but_presented_credentials_still_cannot_pass(required):
    app = create_app(ApiServices(sessions=SessionStore()),
        ApiSettings(allowed_origins=(ORIGIN,), require_auth=required, allow_guests=True))
    with browser(app) as client:
        assert client.get('/curricula').status_code == 200
        assert client.get('/curricula', headers={'Authorization': 'Bearer supplied'}).status_code == 401


def test_guest_cannot_clear_private_state_owned_by_a_signed_in_account():
    app, store, _ = guest_app()
    with browser(app, 'Bearer account-a') as account:
        passed_course(account)
        credential = account.cookies.get(SESSION_COOKIE)
    with browser(app) as guest:
        guest.cookies.update(account.cookies)
        assert guest.delete('/session').status_code == 204
    assert len(store.resolve(credential, account_id='account-a').facts) == 1


def test_guest_private_facts_expire_with_the_existing_idle_session():
    clock = [0.0]
    app, store, pipeline = guest_app(SessionStore(clock=lambda: clock[0], idle_seconds=10))
    with browser(app) as client:
        passed_course(client)
        old_cookie = client.cookies.get(SESSION_COOKIE)
        clock[0] = 11
        assert client.post('/chat', json=body('A synthetic question', **SCOPE)).status_code == 200
        assert pipeline.contexts[-1].facts == ()
        assert client.cookies.get(SESSION_COOKIE) != old_cookie
        assert store.resolve(old_cookie) is None


def test_admission_limits_repeat_guest_requests_by_server_issued_session_identity():
    app, store, _ = guest_app()
    issued = store.issue()
    reserved = app.state.admission.reserve(account_id='guest:' + issued.session_id)
    try:
        with browser(app) as client:
            client.cookies.set(SESSION_COOKIE, issued.credential)
            response = client.post('/chat', json=body('A synthetic question'))
        assert response.status_code == 409 and response.json() == {'error': 'account_busy'}
        assert app.state.admission.admitted == 1
    finally:
        reserved.release()


def test_guest_admission_does_not_block_an_unrelated_guest_session():
    app, store, _ = guest_app()
    first, second = store.issue(), store.issue()
    reserved = app.state.admission.reserve(account_id='guest:' + first.session_id)
    try:
        with browser(app) as client:
            client.cookies.set(SESSION_COOKIE, second.credential)
            assert client.post('/chat', json=body('A synthetic question')).status_code == 200
    finally:
        reserved.release()
