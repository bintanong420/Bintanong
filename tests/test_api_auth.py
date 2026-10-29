"""PSU identity is verified by the host, never by a browser hint or model claim."""
import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.bintanong_api.admission import AnswerAdmission
from backend.bintanong_api.app import ApiServices, ApiSettings, create_app
from backend.bintanong_api.session import ApiError, SESSION_COOKIE
from backend.bintanong_private_context.sessions import SessionStore

ORIGIN = 'https://bintanong.example'
ACCOUNT = '00000000-0000-4000-8000-000000000001'


def user(**changes):
    return dict(id=ACCOUNT, email='synthetic@psu.palawan.edu.ph', email_confirmed_at='2026-10-24T00:00:00Z',
                identities=[dict(provider='google', identity_data=dict(
                    email='synthetic@psu.palawan.edu.ph', email_verified=True))], **changes)


def verify(data, status=200):
    from backend.bintanong_api.auth import SupabaseAuth
    async def run():
        def respond(request):
            assert str(request.url) == 'https://synthetic.supabase.co/auth/v1/user'
            assert request.headers['authorization'] == 'Bearer abc.def.ghi'
            return httpx.Response(status, json=data)
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            return await SupabaseAuth('https://synthetic.supabase.co', 'synthetic-key', client=client).verify('abc.def.ghi')
    return asyncio.run(run())


def test_verified_google_psu_account_returns_only_opaque_identity():
    assert verify(user()) == ACCOUNT


@pytest.mark.parametrize('change', [
    {'email': 'synthetic@psu.palawan.edu.ph.attacker.example'},
    {'email_confirmed_at': None}, {'identities': []}, {'id': 'not-a-user-id'},
    {'identities': [{'provider': 'email', 'identity_data': {'email_verified': True}}]},
    {'identities': [{'provider': 'google', 'identity_data': {
        'email': 'synthetic@psu.palawan.edu.ph', 'email_verified': False}}]},
    {'identities': [{'provider': 'google', 'identity_data': {
        'email': 'different@psu.palawan.edu.ph', 'email_verified': True}}]},
])
def test_unverified_or_wrong_identity_is_refused(change):
    data = user()
    data.update(change)
    with pytest.raises(ApiError) as refused:
        verify(data)
    assert refused.value.code == 'psu_account_required'


def test_user_metadata_cannot_spoof_psu_membership():
    data = user()
    data.update(email='synthetic@example.com', user_metadata={'email': 'synthetic@psu.palawan.edu.ph'})
    with pytest.raises(ApiError):
        verify(data)


@pytest.mark.parametrize('status,code', [(401, 'sign_in_required'), (503, 'auth_unavailable')])
def test_auth_errors_are_fixed_codes(status, code):
    with pytest.raises(ApiError) as refused:
        verify({'message': 'private upstream detail'}, status)
    assert refused.value.code == code


class Auth:
    async def verify(self, token):
        if token not in ('account-a', 'account-b'):
            raise ApiError(401, 'sign_in_required')
        return token


def protected():
    store = SessionStore()
    app = create_app(ApiServices(sessions=store, auth=Auth()),
                     ApiSettings(allowed_origins=(ORIGIN,), require_auth=True))
    return app, store


def test_protected_reads_and_writes_require_server_verified_auth():
    app, store = protected()
    with TestClient(app, base_url='https://testserver', headers={'Origin': ORIGIN}) as client:
        assert client.get('/curricula').status_code == 401
        assert client.delete('/session').status_code == 401
        assert client.get('/health/live').status_code == 200
    assert len(store) == 0


def test_switching_account_cannot_resolve_or_delete_the_other_session():
    app, store = protected()
    issued = store.issue(account_id='account-a')
    assert store.resolve(issued.credential, account_id='account-b') is None
    with TestClient(app, base_url='https://testserver', headers={
            'Origin': ORIGIN, 'Authorization': 'Bearer account-b'}) as client:
        client.cookies.set(SESSION_COOKIE, issued.credential)
        assert client.delete('/session').status_code == 204
    assert store.resolve(issued.credential, account_id='account-a') is not None


def test_one_account_cannot_occupy_multiple_answer_slots_and_release_recovers():
    admission = AnswerAdmission(running=1, waiting=4)
    first = admission.reserve(account_id=ACCOUNT)
    with pytest.raises(ApiError) as refused:
        admission.reserve(account_id=ACCOUNT)
    assert refused.value.code == 'account_busy'
    assert admission.admitted == 1
    first.release()
    first.release()
    again = admission.reserve(account_id=ACCOUNT)
    again.release()
    assert admission.admitted == 0


def test_authenticated_upload_chat_and_cleanup_keep_account_ownership_through_every_api_call():
    from test_api_uploads import CURRICULA, LABELS, SCOPE, Recording, confirm, extract, upload
    from test_api_stream import body
    store, pipeline = SessionStore(), Recording()
    app = create_app(ApiServices(sessions=store, auth=Auth(), curricula=CURRICULA,
        pipeline=pipeline, extract_rows=extract, course_labels=LABELS),
        ApiSettings(allowed_origins=(ORIGIN,), require_auth=True))
    with TestClient(app, base_url='https://testserver', headers={
            'Origin': ORIGIN, 'Authorization': 'Bearer account-a'}) as client:
        pending = upload(client).json()
        credential = client.cookies.get(SESSION_COOKIE)
        assert store.resolve(credential, account_id='account-a').pending is not None
        row = pending['rows'][0]
        reviewed = confirm(client, pending['uploadId'], (row['rowId'], 'cc-105', 'passed'))
        assert reviewed.status_code == 200
        answer = client.post('/chat', json=body('A synthetic question', **SCOPE))
        assert answer.status_code == 200 and 'text-delta' in answer.text
        assert [(f.course_id, f.state) for f in pipeline.contexts[0].facts] == [('cc-105', 'passed')]
        assert client.delete('/uploads/' + pending['uploadId']).status_code == 204
        assert store.resolve(credential, account_id='account-a').facts == ()
        assert client.delete('/session').status_code == 204
        assert store.resolve(credential, account_id='account-a') is None


def test_foreign_cookie_creates_a_fresh_account_session_without_carrying_private_facts():
    from test_api_stream import body
    from test_api_uploads import CURRICULA, LABELS, SCOPE, Recording, confirm, extract, upload
    store, pipeline = SessionStore(), Recording()
    app = create_app(ApiServices(sessions=store, auth=Auth(), curricula=CURRICULA,
        pipeline=pipeline, extract_rows=extract, course_labels=LABELS),
        ApiSettings(allowed_origins=(ORIGIN,), require_auth=True))
    with TestClient(app, base_url='https://testserver', headers={
            'Origin': ORIGIN, 'Authorization': 'Bearer account-a'}) as first:
        pending = upload(first).json()
        row = pending['rows'][0]
        assert confirm(first, pending['uploadId'], (row['rowId'], 'cc-105', 'passed')).status_code == 200
        credential = first.cookies.get(SESSION_COOKIE)
    with TestClient(app, base_url='https://testserver', headers={
            'Origin': ORIGIN, 'Authorization': 'Bearer account-b'}) as second:
        second.cookies.set(SESSION_COOKIE, credential)
        answer = second.post('/chat', json=body('A synthetic question', **SCOPE))
        assert answer.status_code == 200
        assert pipeline.contexts[-1].facts == ()
    assert len(store.resolve(credential, account_id='account-a').facts) == 1
