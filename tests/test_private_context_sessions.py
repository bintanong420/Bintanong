"""Phase 10 session store: server-issued credential, memory only, idle expiry, delete, isolation."""
import pytest

from backend.bintanong_private_context.sessions import SessionLimitError, SessionStore
from backend.bintanong_routing.contracts import ScopedFact


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def fact(session_id, course='cc-101', state='passed', fact_id='fact-1'):
    return ScopedFact(fact_id=fact_id, session_id=session_id, program_id='bscs',
                      curriculum_id='bscs-2018', course_id=course, state=state)


def test_issued_credential_resolves_only_to_its_own_session():
    store = SessionStore()
    a, b = store.issue(), store.issue()
    assert a.credential != b.credential and a.session_id != b.session_id
    assert store.resolve(a.credential).session_id == a.session_id
    assert store.resolve(b.credential).session_id == b.session_id


def test_session_b_cannot_read_session_a_facts():
    store = SessionStore()
    a, b = store.issue(), store.issue()
    store.set_facts(a.credential, (fact(a.session_id, state='failed'),))
    assert store.resolve(b.credential).facts == ()
    assert [f.state for f in store.resolve(a.credential).facts] == ['failed']


def test_facts_owned_by_another_session_are_rejected():
    store = SessionStore()
    a, b = store.issue(), store.issue()
    with pytest.raises(ValueError, match='foreign_session_fact'):
        store.set_facts(b.credential, (fact(a.session_id),))
    assert store.resolve(b.credential).facts == ()


@pytest.mark.parametrize('credential', [None, '', 'x', 'sess-abc', 'A' * 43 + '!', 'A' * 500, 42])
def test_unknown_or_malformed_credentials_resolve_to_nothing(credential):
    store = SessionStore()
    store.issue()
    assert store.resolve(credential) is None


def test_session_id_alone_is_not_a_credential():
    store = SessionStore()
    a = store.issue()
    assert store.resolve(a.session_id) is None


def test_idle_session_expires_and_its_facts_are_gone():
    clock = Clock()
    store = SessionStore(idle_seconds=1800, clock=clock)
    a = store.issue()
    store.set_facts(a.credential, (fact(a.session_id),))
    clock.now += 1801
    assert store.resolve(a.credential) is None
    assert len(store) == 0


def test_activity_extends_the_idle_lifetime():
    clock = Clock()
    store = SessionStore(idle_seconds=1800, clock=clock)
    a = store.issue()
    clock.now += 1700
    assert store.resolve(a.credential) is not None
    clock.now += 1700
    assert store.resolve(a.credential) is not None


def test_deleted_session_cannot_be_resolved_or_written():
    store = SessionStore()
    a, b = store.issue(), store.issue()
    store.set_facts(a.credential, (fact(a.session_id),))
    assert store.delete(a.credential) is True
    assert store.resolve(a.credential) is None
    assert store.delete(a.credential) is False
    with pytest.raises(KeyError):
        store.set_facts(a.credential, ())
    assert store.resolve(b.credential) is not None


def test_wipe_and_a_new_process_store_know_no_earlier_session():
    store = SessionStore()
    a = store.issue()
    store.set_facts(a.credential, (fact(a.session_id),))
    assert SessionStore().resolve(a.credential) is None  # restart: memory only
    store.wipe()
    assert store.resolve(a.credential) is None and len(store) == 0


def test_store_refuses_new_sessions_past_its_bound_after_purging_expired():
    clock = Clock()
    store = SessionStore(idle_seconds=10, clock=clock, max_sessions=2)
    store.issue()
    store.issue()
    with pytest.raises(SessionLimitError):
        store.issue()
    clock.now += 11
    store.issue()  # expired sessions are purged first
    assert len(store) == 1


def test_raw_credentials_are_not_kept_in_store_memory():
    store = SessionStore()
    a = store.issue()
    assert a.credential not in repr(vars(store))
