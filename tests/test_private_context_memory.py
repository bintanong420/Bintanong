"""Memory/eligibility plan, Task 2: scoped facts and one pending check carried across turns of one chat.
Synthetic course ids and codes only."""
from types import SimpleNamespace

import pytest

from backend.bintanong_private_context import memory
from backend.bintanong_private_context.sessions import SessionStore
from backend.bintanong_routing.contracts import ScopedFact


def fact(state, course='course-a', source='user_statement', curriculum='curriculum-a', **extra):
    return ScopedFact(fact_id=f'fact-{course}-{curriculum}-{state}-{source}'.replace('_', '-').lower(), session_id='sess-a', program_id='program-a',
                      curriculum_id=curriculum, course_id=course, state=state,
                      **({'source': source} if source else {}), **extra)


def pending(dimension='completion', **updates):
    value = dict(program_id='program-a', curriculum_id='curriculum-a', operation='check_prerequisite_eligibility',
                 target_course_id='course-b', target_code='B 1', course_id='course-a', course_code='A 1',
                 dimension=dimension)
    value.update(updates)
    return memory.PendingCheck(**value)


def test_a_newer_self_report_replaces_the_older_one_for_that_course():
    merged = memory.merge_facts((fact('taken_unknown'),), (fact('passed'),))
    assert [f.state for f in merged] == ['passed']
    corrected = memory.merge_facts(merged, (fact('failed'),))
    assert [f.state for f in corrected] == ['failed']


def test_took_it_never_erases_a_known_result():
    assert [f.state for f in memory.merge_facts((fact('passed'),), (fact('taken_unknown'),))] == ['passed']


def test_a_confirmed_upload_is_kept_beside_a_disagreeing_statement_so_it_stays_a_conflict():
    merged = memory.merge_facts((fact('passed', source='private_upload'),), (fact('failed'),))
    assert sorted(f.state for f in merged) == ['failed', 'passed']


def test_completion_and_enrollment_are_separate_and_scopes_never_mix():
    merged = memory.merge_facts((fact('not_passed'),), (fact('enrolled', period='current'),
                                                         fact('passed', curriculum='curriculum-z')))
    assert sorted((f.curriculum_id, f.state) for f in merged) == [
        ('curriculum-a', 'enrolled'), ('curriculum-a', 'not_passed'), ('curriculum-z', 'passed')]


@pytest.mark.parametrize('reply,state,composed', [
    ('Oo, pasado.', 'passed', 'Pwede ko na bang i-take ang B 1?'),
    ('opo', 'passed', 'Pwede ko na bang i-take ang B 1?'),
    ('Yes, I passed it', 'passed', 'Can I take B 1?'),
    ('Hindi ko pa napasa.', 'not_passed', 'Pwede ko na bang i-take ang B 1?'),
    ('not yet', 'not_passed', 'Can I take B 1?'),
    ('Bumagsak ako', 'failed', 'Pwede ko na bang i-take ang B 1?'),
    ('Oo, pasado ako sa A 1', 'passed', 'Pwede ko na bang i-take ang B 1?'),
])
def test_a_bare_reply_answers_the_pending_completion_question(reply, state, composed):
    bound = memory.bind_reply(reply, pending(), ('program-a', 'curriculum-a'), session_id='sess-a')
    assert bound is not None
    assert (bound.fact.course_id, bound.fact.state, bound.fact.source) == ('course-a', state, 'user_statement')
    assert bound.text == composed


def test_a_bare_yes_to_an_enrollment_question_is_enrollment_this_term():
    bound = memory.bind_reply('yes', pending('enrollment'), ('program-a', 'curriculum-a'), session_id='sess-a')
    assert (bound.fact.state, bound.fact.period) == ('enrolled', 'current')


@pytest.mark.parametrize('reply,scope,check', [
    ('Oo, pasado.', ('program-a', 'curriculum-z'), pending()),        # curriculum switched: nothing carries
    ('Oo, pasado.', ('program-a', 'curriculum-a'), None),             # no question is waiting
    ('Oo. Can I take C1 next sem?', ('program-a', 'curriculum-a'), pending()),  # a new question, not a reply
    ("I don't know", ('program-a', 'curriculum-a'), pending()),       # no result supplied
    ('Oo, pasado ako sa C 2', ('program-a', 'curriculum-a'), pending()),  # names another course
])
def test_a_reply_binds_only_to_a_waiting_question_in_the_same_scope(reply, scope, check):
    assert memory.bind_reply(reply, check, scope, session_id='sess-a') is None


def answer(outcome='unknown', missing=(), unknown=()):
    return SimpleNamespace(decision=SimpleNamespace(outcome=outcome, missing_facts=missing, unknown_conditions=unknown))


def routed(operation='check_prerequisite_eligibility'):
    inputs = (SimpleNamespace(name='curriculum_id', value='curriculum-a'), SimpleNamespace(name='course_id', value='course-b'))
    return SimpleNamespace(diagnostic='validated', program_id='program-a', curriculum_id='curriculum-a',
                           decision=SimpleNamespace(predicate_request=SimpleNamespace(predicate=operation, inputs=inputs)))


def test_one_missing_result_becomes_the_pending_question():
    check = memory.pending_from(routed(), answer(missing=('completion_unknown:course-a',)),
                                {'course-a': 'A 1', 'course-b': 'B 1'})
    assert check == pending()


@pytest.mark.parametrize('result', [
    answer(missing=('completion_unknown:course-a', 'completion_unknown:course-c')),  # two courses: ask which
    answer(outcome='eligible'),
    answer(missing=('rule_unresolved',)),
])
def test_no_pending_question_without_exactly_one_missing_student_result(result):
    assert memory.pending_from(routed(), result, {'course-a': 'A 1', 'course-b': 'B 1'}) is None


def test_turn_completion_commits_facts_and_pending_together_and_a_failed_turn_commits_nothing():
    store = SessionStore()
    issued = store.issue()
    store.begin_turn(issued.credential, 'msg-1')
    store.end_turn(issued.credential, 'msg-1', completed=False, facts=(fact('passed', source=None),),
                   pending_check=pending())
    view = store.resolve(issued.credential)
    assert view.facts == () and view.pending_check is None
    session_fact = fact('passed').model_copy(update=dict(session_id=view.session_id))
    store.begin_turn(issued.credential, 'msg-2')
    store.end_turn(issued.credential, 'msg-2', completed=True, facts=(session_fact,), pending_check=pending())
    view = store.resolve(issued.credential)
    assert [f.state for f in view.facts] == ['passed'] and view.pending_check == pending()
    store.begin_turn(issued.credential, 'msg-3')
    store.end_turn(issued.credential, 'msg-3', completed=True)  # any other answered turn retires the question
    assert store.resolve(issued.credential).pending_check is None
    assert [f.state for f in store.resolve(issued.credential).facts] == ['passed']
