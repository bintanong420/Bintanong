"""Server-owned ephemeral dialogue commits, independent of model wording."""
import pytest

from backend.bintanong_private_context.sessions import SessionStore
from test_private_context_sessions import Clock, fact


def exchange(message='msg-1', user='Can I take A1?', assistant='Have you passed B1?'):
    from backend.bintanong_private_context.dialogue import DialogueExchange
    return DialogueExchange(message_id=message, user_text=user, assistant_text=assistant,
                            answer_status='clarification_needed')


def test_completed_turn_commits_dialogue_and_facts_together():
    store = SessionStore()
    issued = store.issue()
    store.begin_turn(issued.credential, 'msg-1')
    store.commit_turn_result(issued.credential, 'msg-1', expected_revision=0,
                             exchange=exchange(), facts=(fact(issued.session_id),))
    view = store.resolve(issued.credential)
    assert view.dialogue.revision == 1
    assert view.dialogue.exchanges[0].assistant_text == 'Have you passed B1?'
    assert len(view.facts) == 1
    with pytest.raises(ValueError, match='already_answered'):
        store.begin_turn(issued.credential, 'msg-1')


def test_invalid_commit_does_not_partially_change_history_facts_or_gate():
    store = SessionStore()
    a, b = store.issue(), store.issue()
    store.begin_turn(a.credential, 'msg-1')
    with pytest.raises(ValueError, match='foreign_session_fact'):
        store.commit_turn_result(a.credential, 'msg-1', expected_revision=0,
                                exchange=exchange(), facts=(fact(b.session_id),))
    view = store.resolve(a.credential)
    assert not view.facts and view.dialogue.revision == 0 and not view.dialogue.exchanges
    with pytest.raises(ValueError, match='chat_in_progress'):
        store.begin_turn(a.credential, 'msg-2')


def test_stale_revision_and_wrong_message_cannot_commit_or_unlock_another_turn():
    store = SessionStore()
    a = store.issue()
    store.begin_turn(a.credential, 'msg-1')
    with pytest.raises(ValueError, match='stale_dialogue_revision'):
        store.commit_turn_result(a.credential, 'msg-1', expected_revision=9, exchange=exchange())
    with pytest.raises(ValueError, match='turn_mismatch'):
        store.commit_turn_result(a.credential, 'msg-2', expected_revision=0, exchange=exchange('msg-2'))
    store.end_turn(a.credential, 'msg-old', completed=False)
    with pytest.raises(ValueError, match='chat_in_progress'):
        store.begin_turn(a.credential, 'msg-2')


def test_ledger_is_bounded_and_replay_of_an_evicted_message_is_refused():
    store = SessionStore()
    a = store.issue()
    for i in range(12):
        message = f'msg-{i}'
        store.begin_turn(a.credential, message)
        store.commit_turn_result(a.credential, message, expected_revision=i,
            exchange=exchange(message, user='a'*4000, assistant='b'*4000))
    dialogue = store.resolve(a.credential).dialogue
    assert 1 <= len(dialogue.exchanges) <= 8 and dialogue.revision == 12
    assert sum(len(e.user_text.encode())+len(e.assistant_text.encode()) for e in dialogue.exchanges) <= 32768
    with pytest.raises(ValueError, match='already_answered'):
        store.begin_turn(a.credential, 'msg-0')  # replay remains refused after its text was evicted


def test_ledger_ownership_expiry_delete_and_new_store_are_isolated():
    clock = Clock()
    store = SessionStore(clock=clock)
    a = store.issue(account_id='owner')
    store.begin_turn(a.credential, 'msg-1', account_id='owner')
    with pytest.raises(KeyError):
        store.commit_turn_result(a.credential, 'msg-1', expected_revision=0, exchange=exchange())
    store.commit_turn_result(a.credential, 'msg-1', expected_revision=0,
                             exchange=exchange(), account_id='owner')
    assert SessionStore().resolve(a.credential, account_id='owner') is None
    clock.now += 1801
    assert store.resolve(a.credential, account_id='owner') is None
    b = store.issue()
    store.begin_turn(b.credential, 'msg-1')
    store.delete(b.credential)
    assert store.commit_turn_result(b.credential, 'msg-1', expected_revision=0, exchange=exchange()) is False
    assert store.resolve(b.credential) is None


def test_multibyte_context_is_bounded_explicitly_and_cannot_drop_the_current_exchange():
    from backend.bintanong_private_context.dialogue import bounded_text
    original = '\u20ac' * 6000
    text, truncated = bounded_text(original)
    assert truncated and len(text.encode('utf-8')) <= 8192
    assert original.startswith(text)
    with pytest.raises(ValueError, match='dialogue_exchange_text_budget'):
        exchange(user=original)


def test_regeneration_replaces_history_and_advances_revision():
    store = SessionStore()
    a = store.issue()
    for revision, response in enumerate(('First answer', 'Revised answer')):
        store.begin_turn(a.credential, 'msg-1', regenerate=revision > 0)
        store.commit_turn_result(a.credential, 'msg-1', expected_revision=revision,
                                exchange=exchange(assistant=response))
    state = store.resolve(a.credential).dialogue
    assert state.revision == 2 and len(state.exchanges) == 1
    assert state.exchanges[0].assistant_text == 'Revised answer'
