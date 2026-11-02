"""Owner 2 Nov 2026: narrowed topic companions. #4 a good-moral question picking the Handbook FAQ also sees the
Charter CGMC checklist, and a requirements part goes to that checklist; #3 an absence question fetches the
attendance rule and the sickness certificate together. Topic ids are menu identifiers; texts are fictional."""
from types import SimpleNamespace

import pytest

from backend.bintanong_routing.contracts import DocumentTopic
from backend.bintanong_routing.topic_selection import add_companions

MENU = tuple(DocumentTopic(subject_id=s, claims=(c,)) for s, c in (
    ('handbook_student_faq', 'printed student faq fields'), ('charter_good_moral', 'printed good moral fields'),
    ('handbook_attendance', 'printed attendance fields'), ('handbook_sickness_access', 'printed sickness access fields'),
    ('charter_transfer', 'printed transfer fields')))
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
])
def test_companions_are_added_only_for_their_own_questions(text, picked, expected):
    assert [t.subject_id for t in add_companions(chosen(*picked), MENU, text)] == expected


def test_companions_never_exceed_the_selection_limit():
    from backend.bintanong_routing.topic_selection import MAX_TOPICS
    full = tuple(DocumentTopic(subject_id=f'other_{i}', claims=('x',)) for i in range(MAX_TOPICS - 1))
    picked = (BY_ID['handbook_sickness_access'], *full)
    assert add_companions(picked, MENU + full, 'umabsent ako') == picked


def test_a_good_moral_requirements_part_goes_to_the_charter_checklist():
    from backend.bintanong_routing.router import prefer_good_moral_checklist
    from backend.bintanong_routing.contracts import Interpretation
    from test_routing_contracts import proposal
    text = 'what are the requirements for a good moral certificate?'
    topics = (DocumentTopic(subject_id='handbook_student_faq', claims=('printed student faq fields',)),
              DocumentTopic(subject_id='charter_good_moral', claims=(
                  'printed good moral fields', 'printed good moral metadata and checklist fields')))
    value = proposal(text=text, language='en', route='RAG', mentions=[], operations=[])
    value['parts'][0].update(subject_id='handbook_student_faq', requested_claims=['printed student faq fields'],
                             detail='requirements')
    routed = prefer_good_moral_checklist(Interpretation.parse(value), topics)
    assert (routed.parts[0].subject_id, routed.parts[0].requested_claims) == (
        'charter_good_moral', ('printed good moral metadata and checklist fields',))
    value['parts'][0]['detail'] = 'whole'  # a "how do I get" question keeps the FAQ procedure
    assert prefer_good_moral_checklist(Interpretation.parse(value), topics).parts[0].subject_id == 'handbook_student_faq'


def test_an_absence_part_fetches_both_records():
    from backend.bintanong_orchestration.orchestrator import _topic_intents
    part = SimpleNamespace(evidence_need='document', subject_id='handbook_sickness_access',
                           requested_claims=('printed sickness access fields',), text='umabsent ako kahapon')
    intents = _topic_intents(SimpleNamespace(parts=(part,)))
    assert [(i['subject_id'], i['requested_claims']) for _, i in intents] == [
        ('handbook_sickness_access', ('printed sickness access fields',)),
        ('handbook_attendance', ('printed attendance fields',))]
    clinic = SimpleNamespace(evidence_need='document', subject_id='handbook_sickness_access',
                             requested_claims=('printed sickness access fields',), text='saan ang clinic?')
    assert len(_topic_intents(SimpleNamespace(parts=(clinic,)))) == 1
