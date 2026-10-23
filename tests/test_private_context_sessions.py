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


def pending_extraction():
    from backend.bintanong_private_context.grades import ExtractionResult, GradeRow
    rows = (GradeRow('row-1-2', 'CC 5/L', ('cc-101',), ('5.00',), 1),
            GradeRow('row-1-3', 'GEC 1', ('gec-1',), ('1.50',), 1))
    return ExtractionResult('bscs', 'bscs-2018', rows, 0)


def test_pending_extraction_is_visible_only_to_its_session_and_cleared_on_delete():
    store = SessionStore()
    a, b = store.issue(), store.issue()
    store.set_pending(a.credential, pending_extraction())
    assert store.resolve(b.credential).pending is None
    assert store.resolve(a.credential).pending.rows[0].code_text == 'CC 5/L'
    store.delete(a.credential)
    assert store.resolve(a.credential) is None


def test_confirming_turns_only_chosen_rows_into_facts_and_clears_the_pending_rows():
    store = SessionStore()
    a = store.issue()
    store.set_pending(a.credential, pending_extraction())
    facts = store.confirm_pending(a.credential, {'row-1-2': ('cc-101', 'failed')})
    view = store.resolve(a.credential)
    assert [(f.course_id, f.state, f.session_id) for f in view.facts] == [('cc-101', 'failed', a.session_id)]
    assert facts == view.facts and view.pending is None


def test_a_later_confirmation_replaces_the_earlier_statement_for_that_course():
    store = SessionStore()
    a = store.issue()
    store.set_facts(a.credential, (fact(a.session_id, course='cc-101', state='failed', fact_id='fact-old'),
                                   fact(a.session_id, course='gec-1', fact_id='fact-gec')))
    store.set_pending(a.credential, pending_extraction())
    store.confirm_pending(a.credential, {'row-1-2': ('cc-101', 'passed')})
    assert sorted((f.course_id, f.state) for f in store.resolve(a.credential).facts) == [
        ('cc-101', 'passed'), ('gec-1', 'passed')]


def test_confirming_without_pending_rows_is_refused():
    store = SessionStore()
    a = store.issue()
    with pytest.raises(ValueError, match='no_pending_extraction'):
        store.confirm_pending(a.credential, {'row-1-2': ('cc-101', 'failed')})


def test_two_uploads_with_the_same_row_position_keep_both_courses():
    from backend.bintanong_private_context.grades import ExtractionResult, GradeRow
    from backend.bintanong_routing.contracts import RequestContext
    store = SessionStore()
    a = store.issue()
    for course in ('cc-101', 'gec-1'):
        store.set_pending(a.credential, ExtractionResult(
            'bscs', 'bscs-2018', (GradeRow('row-1-2', 'X', (course,), (), 1),), 0))
        store.confirm_pending(a.credential, {'row-1-2': (course, 'passed')})
    view = store.resolve(a.credential)
    context = RequestContext(session_id=view.session_id, request_id='req-1', program_id='bscs',
                             curriculum_id='bscs-2018', facts=view.facts)
    assert sorted(f.course_id for f in context.facts) == ['cc-101', 'gec-1']


def test_confirming_more_facts_than_a_request_can_carry_is_refused_and_keeps_the_earlier_facts():
    from backend.bintanong_private_context.grades import ExtractionResult, GradeRow
    store = SessionStore()
    a = store.issue()
    rows = tuple(GradeRow(f'row-1-{i}', 'X', (f'course-{i}',), (), 1) for i in range(257))
    store.set_pending(a.credential, ExtractionResult('bscs', 'bscs-2018', rows, 0))
    with pytest.raises(ValueError, match='too_many_facts'):
        store.confirm_pending(a.credential, {r.row_id: (r.candidates[0], 'passed') for r in rows})
    assert store.resolve(a.credential).facts == ()


# Phase 11: one chat turn in flight per session; a completed message id is not answered twice.
def test_second_turn_while_one_is_in_flight_is_refused():
    store = SessionStore()
    a = store.issue()
    store.begin_turn(a.credential, 'msg-1')
    with pytest.raises(ValueError, match='chat_in_progress'):
        store.begin_turn(a.credential, 'msg-2')


def test_completed_message_is_not_answered_again_unless_regenerated():
    store = SessionStore()
    a = store.issue()
    store.begin_turn(a.credential, 'msg-1')
    store.end_turn(a.credential, 'msg-1', completed=True)
    with pytest.raises(ValueError, match='already_answered'):
        store.begin_turn(a.credential, 'msg-1')
    store.begin_turn(a.credential, 'msg-1', regenerate=True)


def test_cancelled_turn_can_be_retried_with_the_same_message():
    store = SessionStore()
    a = store.issue()
    store.begin_turn(a.credential, 'msg-1')
    store.end_turn(a.credential, 'msg-1', completed=False)
    store.begin_turn(a.credential, 'msg-1')


def test_turns_are_per_session():
    store = SessionStore()
    a, b = store.issue(), store.issue()
    store.begin_turn(a.credential, 'msg-1')
    store.begin_turn(b.credential, 'msg-1')


def test_ending_a_turn_of_a_deleted_session_does_not_resurrect_it():
    store = SessionStore()
    a = store.issue()
    store.begin_turn(a.credential, 'msg-1')
    store.delete(a.credential)
    store.end_turn(a.credential, 'msg-1', completed=True)
    assert len(store) == 0 and store.resolve(a.credential) is None


# Phase 11 uploads: the pending extraction has an id; deleting an upload removes its pending rows and the
# facts it confirmed, never a newer statement that replaced one of them.
def test_pending_extraction_gets_an_upload_id_shown_in_the_view():
    store = SessionStore()
    a = store.issue()
    upload_id = store.set_pending(a.credential, pending_extraction())
    assert upload_id.startswith('upl-') and store.resolve(a.credential).pending_upload_id == upload_id


def test_confirming_a_different_upload_id_is_refused():
    store = SessionStore()
    a = store.issue()
    store.set_pending(a.credential, pending_extraction())
    with pytest.raises(ValueError, match='unknown_upload'):
        store.confirm_pending(a.credential, {'row-1-2': ('cc-101', 'passed')}, upload_id='upl-other')


def test_deleting_a_pending_upload_clears_its_rows():
    store = SessionStore()
    a = store.issue()
    upload_id = store.set_pending(a.credential, pending_extraction())
    assert store.delete_upload(a.credential, upload_id) is True
    view = store.resolve(a.credential)
    assert view.pending is None and view.pending_upload_id is None


def test_deleting_a_confirmed_upload_removes_its_facts_but_not_newer_statements():
    store = SessionStore()
    a = store.issue()
    first = store.set_pending(a.credential, pending_extraction())
    store.confirm_pending(a.credential, {'row-1-2': ('cc-101', 'failed'), 'row-1-3': ('gec-1', 'passed')},
                          upload_id=first)
    second = store.set_pending(a.credential, pending_extraction())
    store.confirm_pending(a.credential, {'row-1-2': ('cc-101', 'passed')}, upload_id=second)
    assert store.delete_upload(a.credential, first) is True
    assert [(f.course_id, f.state) for f in store.resolve(a.credential).facts] == [('cc-101', 'passed')]


def test_deleting_an_unknown_or_foreign_upload_changes_nothing():
    store = SessionStore()
    a, b = store.issue(), store.issue()
    upload_id = store.set_pending(a.credential, pending_extraction())
    assert store.delete_upload(b.credential, upload_id) is False
    assert store.delete_upload(a.credential, 'upl-other') is False
    assert store.resolve(a.credential).pending is not None
