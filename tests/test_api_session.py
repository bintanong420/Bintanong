"""Phase 11 API session boundary: cookie credential, expiry, deletion, isolation and CSRF checks."""
from fastapi import Depends
from fastapi.testclient import TestClient

from backend.bintanong_api.app import ApiServices, ApiSettings, create_app, require_session
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_routing.contracts import ScopedFact

ORIGIN = 'https://bintanong.example'
COOKIE = '__Host-bintanong_session'


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def build(store=None):
    store = SessionStore() if store is None else store  # an empty store is falsy (__len__)
    app = create_app(ApiServices(sessions=store), ApiSettings(allowed_origins=(ORIGIN,)))

    @app.post('/test-only/whoami')
    def whoami(session=Depends(require_session)):
        return {'session_id': session.view.session_id, 'facts': len(session.view.facts)}

    return app, store


def client(app):
    return TestClient(app, base_url='https://testserver', headers={'Origin': ORIGIN})


def whoami(c):
    response = c.post('/test-only/whoami')
    assert response.status_code == 200, response.text
    return response.json()['session_id']


def test_first_request_issues_a_host_prefixed_httponly_strict_cookie():
    app, store = build()
    response = client(app).post('/test-only/whoami')
    cookie = response.headers['set-cookie']
    assert cookie.startswith(f'{COOKIE}=')
    lowered = cookie.lower()
    assert 'httponly' in lowered and 'secure' in lowered and 'samesite=strict' in lowered
    assert 'path=/' in lowered and 'domain' not in lowered
    assert len(store) == 1


def test_returning_cookie_resolves_the_same_session():
    app, _ = build()
    c = client(app)
    first = whoami(c)
    assert whoami(c) == first


def test_credential_never_appears_in_the_body():
    app, _ = build()
    response = client(app).post('/test-only/whoami')
    credential = response.cookies[COOKIE]
    assert credential not in response.text


def test_expired_session_is_replaced_by_a_new_one():
    clock = Clock()
    app, store = build(SessionStore(idle_seconds=60, clock=clock))
    c = client(app)
    first = whoami(c)
    clock.now += 61
    assert whoami(c) != first
    assert len(store) == 1


def test_unknown_or_tampered_cookie_gets_a_fresh_session_not_an_error():
    app, store = build()
    c = client(app)
    c.cookies.set(COOKIE, 'not-a-real-credential', domain='testserver')
    assert whoami(c).startswith('sess-')
    assert len(store) == 1


def test_session_b_never_sees_session_a():
    app, store = build()
    a, b = client(app), client(app)
    a_id = whoami(a)
    credential = a.cookies[COOKIE]
    store.set_facts(credential, (ScopedFact(fact_id='fact-1', session_id=a_id, program_id='bscs',
                                            curriculum_id='bscs-2018', course_id='cc-101', state='passed'),))
    assert whoami(b) != a_id
    assert b.post('/test-only/whoami').json()['facts'] == 0
    assert a.post('/test-only/whoami').json()['facts'] == 1


def test_delete_session_forgets_it_and_clears_the_cookie():
    app, store = build()
    c = client(app)
    first = whoami(c)
    response = c.delete('/session')
    assert response.status_code == 204
    assert len(store) == 0
    assert 'max-age=0' in response.headers['set-cookie'].lower()
    assert whoami(c) != first


def test_delete_session_without_a_session_is_still_204():
    app, _ = build()
    assert client(app).delete('/session').status_code == 204


def test_unsafe_request_without_origin_is_refused():
    app, store = build()
    response = TestClient(app, base_url='https://testserver').post('/test-only/whoami')
    assert response.status_code == 403
    assert response.json() == {'error': 'origin_not_allowed'}
    assert len(store) == 0


def test_foreign_and_null_origins_are_refused():
    app, _ = build()
    for origin in ('https://evil.example', 'null', 'https://bintanong.example.evil.example'):
        response = TestClient(app, base_url='https://testserver', headers={'Origin': origin}).post(
            '/test-only/whoami')
        assert response.status_code == 403, origin


def test_cross_site_fetch_metadata_is_refused_even_with_an_allowed_origin():
    app, _ = build()
    response = client(app).post('/test-only/whoami', headers={'Sec-Fetch-Site': 'cross-site'})
    assert response.status_code == 403


def test_delete_session_is_also_origin_checked():
    app, store = build()
    c = client(app)
    whoami(c)
    response = c.delete('/session', headers={'Origin': 'https://evil.example'})
    assert response.status_code == 403
    assert len(store) == 1


def fill_with_a_stated_session(store):
    issued = store.issue()
    store.set_facts(issued.credential, (ScopedFact(fact_id='fact-1', session_id=issued.session_id, program_id='bscs',
                                                   curriculum_id='bscs-2018', course_id='cc-101', state='passed'),))
    return issued


def test_full_store_answers_503_without_evicting_a_student_who_stated_something():
    app, store = build(SessionStore(max_sessions=1))
    stated = fill_with_a_stated_session(store)
    response = client(app).post('/test-only/whoami')
    assert response.status_code == 503
    assert response.json() == {'error': 'session_limit'}
    assert store.resolve(stated.credential) is not None


def test_cookie_less_requests_cannot_lock_a_new_student_out():
    # Security review S1 (24 Oct 2026): requests that never keep their cookie used to fill the store.
    app, store = build(SessionStore(max_sessions=3))
    stated = fill_with_a_stated_session(store)
    for _ in range(10):
        client(app).delete('/uploads/upl-unknown')
    whoami(client(app))
    assert store.resolve(stated.credential) is not None


def test_health_endpoints_still_exist_on_the_factory_app():
    app, _ = build()
    assert TestClient(app).get('/health/live').json() == {'status': 'live'}
