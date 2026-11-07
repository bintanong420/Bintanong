"""Owner 2 Nov 2026: narrowed topic companions. #4 a good-moral question picking the Handbook FAQ also sees the
Charter CGMC checklist, and a requirements part goes to that checklist; #3 an absence question fetches the
attendance rule and the sickness certificate together. Topic ids are menu identifiers; texts are fictional."""
from types import SimpleNamespace

import pytest

from backend.bintanong_routing.contracts import DocumentTopic
from backend.bintanong_routing.topic_selection import add_companions


@pytest.mark.parametrize('text', ['May 4 ako sa subject; how do I clear it?',
                                'I got INC in a subject; how can I complete it?'])
def test_a_stated_deficient_mark_keeps_grade_completion_available_to_the_interpreter(text):
    grade = DocumentTopic(subject_id='grade_completion', claims=('reviewed completion fields',))
    drop = DocumentTopic(subject_id='handbook_dac_policy', claims=('reviewed change fields',))
    assert add_companions((drop,), (drop, grade), text) == (drop, grade)


@pytest.mark.parametrize('text', ['I have 4 units to drop.', 'Enrollment starts May 4.',
                                'May 4 classes ako next semester.', 'May 4 ako mag-eenroll.'])
def test_numbers_for_units_dates_or_classes_do_not_add_grade_completion(text):
    grade = DocumentTopic(subject_id='grade_completion', claims=('reviewed completion fields',))
    drop = DocumentTopic(subject_id='handbook_dac_policy', claims=('reviewed change fields',))
    assert add_companions((drop,), (drop, grade), text) == (drop,)


@pytest.mark.parametrize('picked', ['handbook_student_faq', 'charter_library_facilities'])
def test_general_room_request_retrieves_general_and_library_guidance_together(picked):
    from backend.bintanong_orchestration.orchestrator import _topic_intents
    part = SimpleNamespace(part_id='r1', evidence_need='document', subject_id=picked,
        requested_claims=('printed student faq fields' if picked == 'handbook_student_faq' else
                          'printed library facilities fields',), text='How do we reserve a room for our club?')
    intents = _topic_intents(SimpleNamespace(parts=(part,)))
    assert {i['subject_id'] for _, i in intents} == {'handbook_student_faq', 'charter_library_facilities'}

MENU = tuple(DocumentTopic(subject_id=s, claims=(c,)) for s, c in (
    ('handbook_student_faq', 'printed student faq fields'), ('charter_good_moral', 'printed good moral fields'),
    ('handbook_attendance', 'printed attendance fields'), ('handbook_sickness_access', 'printed sickness access fields'),
    ('charter_transfer', 'printed transfer fields'), ('handbook_transfer_credentials', 'printed transfer credentials fields'),
    ('handbook_transfer_clearance', 'printed transfer clearance fields'),
    ('handbook_shifting', 'printed shifting fields'), ('handbook_drop_shift_faq', 'printed FAQ 8 shifting steps')))
BY_ID = {t.subject_id: t for t in MENU}


def chosen(*ids):
    return tuple(BY_ID[i] for i in ids)


@pytest.mark.parametrize('text,picked,expected', [
    ('what are the requirements for a good moral certificate?', ('handbook_student_faq',),
     ['handbook_student_faq', 'charter_good_moral']),
    ('how do I get my transfer credentials?', ('handbook_student_faq',), ['handbook_student_faq']),
    ('umabsent ako kahapon, ano kailangan ko gawin?', ('handbook_sickness_access',),
     ['handbook_sickness_access', 'handbook_attendance']),
    ('I was absent yesterday', ('handbook_attendance',), ['handbook_attendance', 'handbook_sickness_access']),
    ('saan ang clinic para sa medical certificate?', ('handbook_sickness_access',), ['handbook_sickness_access']),
    ('magkano transfer fee?', ('charter_transfer',), ['charter_transfer']),
    # Live fee-transfer-en: a leaving phrase also offers the leaving topics; plain 'transfer credentials' does not.
    ('How much does it cost to get transfer credentials or honorable dismissal?', ('handbook_transfer_credentials',),
     ['handbook_transfer_credentials', 'charter_transfer', 'handbook_transfer_clearance']),
    ('magkano bayad sa transfer credentials?', ('handbook_transfer_credentials',), ['handbook_transfer_credentials']),
    # Owner 3 Nov 2026 (H8): a shifting question that picked Handbook 4.1 also sees FAQ 8's printed steps.
    ('How to shift/change curricular program?', ('handbook_shifting',), ['handbook_shifting', 'handbook_drop_shift_faq']),
    ('paano mag-shift ng program?', ('handbook_shifting',), ['handbook_shifting', 'handbook_drop_shift_faq']),
    ('Pano po lumipat ng kurso?', ('handbook_shifting',), ['handbook_shifting', 'handbook_drop_shift_faq']),
    ('Paano po lumipat ng kurso?', ('handbook_shifting',), ['handbook_shifting', 'handbook_drop_shift_faq']),
    ('what does residence mean?', ('handbook_shifting',), ['handbook_shifting']),
])
def test_companions_are_added_only_for_their_own_questions(text, picked, expected):
    assert [t.subject_id for t in add_companions(chosen(*picked), MENU, text)] == expected


def test_companions_never_exceed_the_selection_limit():
    from backend.bintanong_routing.topic_selection import MAX_TOPICS
    full = tuple(DocumentTopic(subject_id=f'other_{i}', claims=('x',)) for i in range(MAX_TOPICS - 1))
    picked = (BY_ID['handbook_sickness_access'], *full)
    assert add_companions(picked, MENU + full, 'umabsent ako') == picked


def test_an_explicit_handbook_requirements_selection_is_not_forced_to_the_charter():
    from backend.bintanong_routing.router import prefer_printed_procedure
    from backend.bintanong_routing.contracts import Interpretation
    from test_routing_contracts import proposal
    text = 'According to the Student Handbook, what are the requirements for a good moral certificate?'
    topics = (DocumentTopic(subject_id='handbook_student_faq', claims=('printed student faq fields',)),
              DocumentTopic(subject_id='charter_good_moral', claims=(
                  'printed good moral fields', 'printed good moral metadata and checklist fields')))
    value = proposal(text=text, language='en', route='RAG', mentions=[], operations=[])
    value['parts'][0].update(subject_id='handbook_student_faq', requested_claims=['printed student faq fields'],
                             detail='requirements')
    routed = prefer_printed_procedure(Interpretation.parse(value), topics)
    assert (routed.parts[0].subject_id, routed.parts[0].requested_claims) == (
        'handbook_student_faq', ('printed student faq fields',))


def test_an_absence_part_is_led_by_the_attendance_rule():
    # Live 2 Nov 2026: the router chose the sickness topic, so the host required sickness coverage and withheld a good
    # excuse-slip answer. Every absence needs the excuse slip; sickness is the "if you were sick" branch.
    from backend.bintanong_routing.router import lead_absence_with_attendance
    from backend.bintanong_routing.contracts import Interpretation
    from test_routing_contracts import proposal
    text = 'umabsent ako kahapon, ano kailangan ko gawin?'
    value = proposal(text=text, language='taglish', route='RAG', mentions=[], operations=[])
    value['parts'][0].update(subject_id='handbook_sickness_access', requested_claims=['printed sickness access fields'])
    routed = lead_absence_with_attendance(Interpretation.parse(value), MENU)
    assert (routed.parts[0].subject_id, routed.parts[0].requested_claims) == (
        'handbook_attendance', ('printed attendance fields',))
    value['parts'][0]['text'] = value['parts'][0]['text']  # unchanged text; a clinic question is left alone below
    clinic = 'saan ang clinic?'
    other = proposal(text=clinic, language='taglish', route='RAG', mentions=[], operations=[])
    other['parts'][0].update(subject_id='handbook_sickness_access', requested_claims=['printed sickness access fields'])
    assert lead_absence_with_attendance(Interpretation.parse(other), MENU).parts[0].subject_id == 'handbook_sickness_access'


def test_an_absence_part_fetches_both_records():
    from backend.bintanong_orchestration.orchestrator import _topic_intents
    part = SimpleNamespace(part_id='r1', evidence_need='document', subject_id='handbook_sickness_access',
                           requested_claims=('printed sickness access fields',), text='umabsent ako kahapon')
    intents = _topic_intents(SimpleNamespace(parts=(part,)))
    assert [(i['subject_id'], i['requested_claims']) for _, i in intents] == [
        ('handbook_sickness_access', ('printed sickness access fields',)),
        ('handbook_attendance', ('printed attendance fields',))]
    clinic = SimpleNamespace(part_id='r1', evidence_need='document', subject_id='handbook_sickness_access',
                             requested_claims=('printed sickness access fields',), text='saan ang clinic?')
    assert len(_topic_intents(SimpleNamespace(parts=(clinic,)))) == 1


def test_a_shifting_question_fetches_the_rule_and_the_faq_steps_together():
    from backend.bintanong_orchestration.orchestrator import _topic_intents
    part = SimpleNamespace(part_id='r1', evidence_need='document', subject_id='handbook_shifting',
                           requested_claims=('printed shifting fields',), text='How to shift/change curricular program?')
    assert [(i['subject_id'], i['requested_claims']) for _, i in _topic_intents(SimpleNamespace(parts=(part,)))] == [
        ('handbook_shifting', ('printed shifting fields',)), ('handbook_drop_shift_faq', ('printed FAQ 8 shifting steps',))]
    drop = SimpleNamespace(part_id='r1', evidence_need='document', subject_id='handbook_drop_shift_faq',
                           requested_claims=('printed FAQ 7 dropping steps',), text='How to drop subjects?')
    assert len(_topic_intents(SimpleNamespace(parts=(drop,)))) == 1
