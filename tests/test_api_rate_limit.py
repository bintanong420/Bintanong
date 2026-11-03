"""Per-person question limit (owner, 3 Nov 2026): guests are counted per browser, not per chat session."""
from fastapi.testclient import TestClient

from backend.bintanong_api.app import ApiServices, ApiSettings, create_app
from backend.bintanong_api.rate_limit import CLIENT_COOKIE, QuestionRateLimit
from backend.bintanong_private_context.sessions import SessionStore
from test_api_auth import Auth
from test_api_stream import body
from test_api_uploads import CURRICULA, LABELS, ORIGIN, Recording, extract


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_limit_allows_the_window_quota_then_reports_the_wait_until_the_oldest_question_leaves():
    clock = Clock()
    limit = QuestionRateLimit(limit=2, window_seconds=300, clock=clock)
    assert limit.admit('guest:a') is None
    clock.now += 100
    assert limit.admit('guest:a') is None
    clock.now += 50
    assert limit.admit('guest:a') == 150  # the first question leaves the window at +300
    assert limit.admit('guest:b') is None, 'other people keep their own quota'
    clock.now += 150
    assert limit.admit('guest:a') is None


def test_a_refused_attempt_is_not_counted():
    clock = Clock()
    limit = QuestionRateLimit(limit=1, window_seconds=60, clock=clock)
    assert limit.admit('guest:a') is None
    for _ in range(5):
        assert limit.admit('guest:a') == 60
    clock.now += 60
    assert limit.admit('guest:a') is None


def app_with(limit=2):
    app = create_app(ApiServices(sessions=SessionStore(), auth=Auth(), curricula=CURRICULA,
        pipeline=Recording(), extract_rows=extract, course_labels=LABELS),
        ApiSettings(allowed_origins=(ORIGIN,), require_auth=True, allow_guests=True,
                    max_questions_per_window=limit, question_window_seconds=300))
    return app


def guest(app):
    return TestClient(app, base_url='https://testserver', headers={'Origin': ORIGIN})


def test_guest_over_the_limit_gets_429_with_a_wait_and_new_chat_does_not_reset_it():
    app = app_with(limit=2)
    with guest(app) as client:
        for n in range(2):
            assert client.post('/chat', json=body('Question', message_id=f'msg-{n}')).status_code == 200
        client_id = client.cookies.get(CLIENT_COOKIE)
        assert client_id
        limited = client.post('/chat', json=body('Question', message_id='msg-2'))
        assert limited.status_code == 429
        assert limited.json()['error'] == 'rate_limited'
        assert 0 < limited.json()['retryAfter'] <= 300
        assert limited.headers['Retry-After'] == str(limited.json()['retryAfter'])
        assert client.delete('/session').status_code == 204  # New chat
        again = client.post('/chat', json=body('Question', message_id='msg-3'))
        assert again.status_code == 429, 'a new chat session is still the same browser'
        assert client.cookies.get(CLIENT_COOKIE) == client_id
    with guest(app) as other:
        assert other.post('/chat', json=body('Question', message_id='msg-9')).status_code == 200


def test_browser_id_cookie_is_private_and_long_lived():
    app = app_with()
    with guest(app) as client:
        response = client.post('/chat', json=body('Question'))
        cookie = next(c for c in response.headers.get_list('set-cookie') if c.startswith(CLIENT_COOKIE + '='))
        lowered = cookie.lower()
        assert 'httponly' in lowered and 'secure' in lowered and 'samesite=strict' in lowered and 'max-age=' in lowered


def test_a_busy_refusal_does_not_use_the_quota():
    app = app_with(limit=1)
    held = [app.state.admission.reserve(account_id=f'other:{n}') for n in range(5)]  # 1 running + 4 waiting
    try:
        with guest(app) as client:
            busy = client.post('/chat', json=body('Question', message_id='msg-0'))
            assert busy.status_code == 503 and busy.json() == {'error': 'answers_busy'}
            for reservation in held:
                reservation.release()
            held = []
            assert client.post('/chat', json=body('Question', message_id='msg-1')).status_code == 200
    finally:
        for reservation in held:
            reservation.release()
