import pytest

from backend.bintanong_private_context.conversation import follow_up_context
from backend.bintanong_private_context.dialogue import DialogueExchange
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_routing.contracts import ConversationContext


def stored():
    store = SessionStore()
    issued = store.issue()
    store.begin_turn(issued.credential, 'question-1')
    store.commit_turn_result(issued.credential, 'question-1', expected_revision=0,
        exchange=DialogueExchange(message_id='question-1', program_id='program-a', curriculum_id='curriculum-a',
            user_text='Can I take A1?', assistant_text='Have you passed B1?', answer_status='clarification_needed'))
    return store.resolve(issued.credential)


def test_server_exchange_reaches_routing_context_as_dialogue_only():
    view = stored()
    context = follow_up_context(view, request_id='req-2', program_id='program-a', curriculum_id='curriculum-a')
    assert context.dialogue.session_id == view.session_id
    assert len(context.dialogue.turns) == 1
    assert context.dialogue.turns[0].user_text == 'Can I take A1?'
    assert context.dialogue.turns[0].assistant_text == 'Have you passed B1?'
    assert context.facts == ()


def test_curriculum_switch_excludes_other_curriculum_dialogue():
    context = follow_up_context(stored(), request_id='req-2', program_id='program-a', curriculum_id='curriculum-b')
    assert context.dialogue is None


def test_dialogue_from_another_session_is_rejected():
    context = follow_up_context(stored(), request_id='req-2', program_id='program-a', curriculum_id='curriculum-a')
    with pytest.raises(ValueError, match='foreign_dialogue'):
        context.model_copy(update={'session_id': 'sess-foreign'})


def test_router_prompt_contains_owned_history_with_explicit_trust_boundary():
    import json
    from backend.bintanong_routing.prompt import build_messages
    from test_routing_validation import catalog, registry
    context = follow_up_context(stored(), request_id='req-2', program_id='program-a', curriculum_id='curriculum-a')
    messages = build_messages('Why?', context, catalog(), registry())
    data = json.loads(messages[1]['content'])
    assert data['dialogue_context']['turns'][0]['assistant_text'] == 'Have you passed B1?'
    assert 'never institutional evidence' in messages[0]['content']
