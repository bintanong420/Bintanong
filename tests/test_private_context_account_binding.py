"""Optional verified account ownership applies to every credential-based session operation."""
import pytest

from backend.bintanong_private_context.sessions import SessionStore


def test_account_binding_refuses_foreign_and_absent_identity_without_touching_expiry():
    now = [0.0]
    store = SessionStore(clock=lambda: now[0], idle_seconds=10)
    issued = store.issue(account_id='account-a')
    now[0] = 9
    assert store.resolve(issued.credential, account_id='account-b') is None
    assert store.resolve(issued.credential) is None
    now[0] = 11
    assert store.resolve(issued.credential, account_id='account-a') is None


@pytest.mark.parametrize('operation', [
    lambda store, credential, account: store.set_facts(credential, (), account_id=account),
    lambda store, credential, account: store.set_conversation(credential, None, account_id=account),
    lambda store, credential, account: store.set_pending(credential, None, account_id=account),
    lambda store, credential, account: store.confirm_pending(credential, {}, account_id=account),
    lambda store, credential, account: store.begin_turn(credential, 'msg-foreign', account_id=account),
])
@pytest.mark.parametrize('account', ['account-b', None])
def test_foreign_mutations_raise_the_same_unknown_session_as_an_unknown_cookie(operation, account):
    store = SessionStore()
    issued = store.issue(account_id='account-a')
    for credential in (issued.credential, 'unknown'):
        with pytest.raises(KeyError, match='unknown_session'):
            operation(store, credential, account)
    assert store.resolve(issued.credential, account_id='account-a') is not None


@pytest.mark.parametrize('account', ['account-b', None])
def test_foreign_cleanup_is_noop_and_cannot_unlock_or_delete_another_accounts_turn(account):
    store = SessionStore()
    issued = store.issue(account_id='account-a')
    store.begin_turn(issued.credential, 'msg-a', account_id='account-a')
    store.end_turn(issued.credential, 'msg-a', completed=True, account_id=account)
    assert store.delete_upload(issued.credential, 'upl-0123456789abcdef', account_id=account) is False
    assert store.delete(issued.credential, account_id=account) is False
    with pytest.raises(ValueError, match='chat_in_progress'):
        store.begin_turn(issued.credential, 'msg-b', account_id='account-a')
    store.end_turn(issued.credential, 'msg-a', completed=True, account_id='account-a')
    with pytest.raises(ValueError, match='already_answered'):
        store.begin_turn(issued.credential, 'msg-a', account_id='account-a')
    assert store.delete(issued.credential, account_id='account-a') is True


def test_unbound_test_mode_keeps_existing_behavior_and_does_not_accept_an_account():
    store = SessionStore()
    issued = store.issue()
    assert store.resolve(issued.credential) is not None
    assert store.resolve(issued.credential, account_id='account-a') is None
    store.set_facts(issued.credential, ())
    store.set_conversation(issued.credential, None)
    store.set_pending(issued.credential, None)
    store.begin_turn(issued.credential, 'msg-a')
    store.end_turn(issued.credential, 'msg-a', completed=False)
    assert store.delete(issued.credential) is True


def test_global_wipe_still_removes_all_bound_and_unbound_sessions():
    store = SessionStore()
    first = store.issue(account_id='account-a')
    second = store.issue()
    store.wipe()
    assert store.resolve(first.credential, account_id='account-a') is None
    assert store.resolve(second.credential) is None
