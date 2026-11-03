"""Owner GUI 3 Nov 2026 ("memory system.. to talaga"): a follow-up that changes one thing re-asks the previous
question. Session memory keeps the previous operation, year and semester as ids and fixed values, never text."""
import importlib

import pytest

from backend.bintanong_private_context.conversation import capture
from backend.bintanong_routing.contracts import ConversationContext, Interpretation, RequestContext
from backend.bintanong_routing.prompt import build_messages, previous_turn
from test_routing_contracts import context
from test_routing_course_facts import registry, term_proposal
from test_routing_validation import catalog


def validate(text, value, conversation=None):
    ctx = context(conversation=conversation) if conversation else context()
    return importlib.import_module('backend.bintanong_routing.validation').validate_interpretation(
        text, RequestContext.parse(ctx), Interpretation.parse(value), catalog=catalog(),
        registry=registry(), documents_available=True, synthetic=True)


def inputs(result):
    return {i.name: i.value for i in result.decision.predicate_request.inputs}


def test_a_term_listing_is_remembered_with_its_operation_year_and_semester():
    remembered = capture(validate('Subjects in first year second sem?', term_proposal()))
    assert (remembered.operation, remembered.year_level, remembered.semester) == ('list_term_courses', 1, 'second_semester')


def test_the_router_sees_the_previous_question_structure():
    remembered = dict(program_id='program-a', curriculum_id='curriculum-a', operation='list_term_courses',
                      year_level=1, semester='first_semester')
    shown = previous_turn(RequestContext.parse(context(conversation=remembered)), catalog())
    assert shown['operation'] == 'list_term_courses' and shown['term'] == dict(year_level=1, semester='first_semester')
    messages = build_messages('e yung 2nd sem?', RequestContext.parse(context(conversation=remembered)), catalog(),
                              registry())
    assert 'previous_turn.operation' in messages[0]['content']


def test_a_semester_only_follow_up_takes_the_year_from_the_previous_question():
    remembered = dict(program_id='program-a', curriculum_id='curriculum-a', operation='list_term_courses',
                      year_level=1, semester='first_semester')
    result = validate('e yung 2nd sem?', term_proposal('e yung 2nd sem?', '2nd sem'), remembered)
    assert result.diagnostic == 'validated'
    assert inputs(result) == {'curriculum_id': 'curriculum-a', 'year_level': '1', 'semester': 'second_semester'}


def test_without_a_previous_term_a_semester_alone_still_asks_for_the_year():
    result = validate('e yung 2nd sem?', term_proposal('e yung 2nd sem?', '2nd sem'))
    assert result.diagnostic != 'validated'


def test_memory_holds_no_text():
    assert set(ConversationContext.model_fields) <= {'program_id', 'curriculum_id', 'course_id', 'subject_id', 'pending',
                                                     'detail', 'operation', 'year_level', 'semester'}

@pytest.mark.parametrize('fact_part_operations', [[], [0]])  # live: the fact part repeated the check
def test_a_fact_only_part_is_folded_into_the_check_it_qualifies(fact_part_operations):
    # Owner GUI 3 Nov 2026 (image 18): "Pwede ko bang i-take ang BU-3/L next sem? Hindi pa ako passed sa BU-2/L."
    # was split into a check part and a fact-only part, and the fact-only part made the reply an empty clarify.
    from test_routing_contracts import proposal
    from test_routing_validation import validate as plain
    text = 'Can I take B1? Not passed A1.'
    value = proposal(text=text, mentions=[dict(kind='course', text='B1', start=11, end=13),
                                          dict(kind='course', text='A1', start=26, end=28)],
                     claims=[dict(entity=1, state='failed', mode='asserted', text='Not passed A1.', start=15, end=29)],
                     operations=[dict(name='check_prerequisite_eligibility', target=0)],
                     parts=[dict(part_id='r1', text='Can I take B1?', start=0, end=14, evidence_need='structured',
                                 operation_indices=[0]),
                            dict(part_id='r2', text='Not passed A1.', start=15, end=29, evidence_need='structured',
                                 operation_indices=fact_part_operations)])
    result = plain(text, value)
    assert result.diagnostic == 'validated' and result.decision.predicate_request.predicate == 'check_prerequisite_eligibility'
    assert [(c.course_id, c.state) for c in result.claims] == [('course-a', 'not_passed')]  # owner plan state

def test_how_about_another_course_keeps_the_previous_check():
    # Owner GUI 3 Nov 2026: "pano yung CS 10/L?" after a prerequisites question was answered with course units.
    from backend.bintanong_routing.router import repeat_previous_check
    from test_routing_contracts import proposal
    value = Interpretation.parse(proposal(text='pano yung A1?', mentions=[dict(kind='course', text='A1', start=10, end=12)],
                                          operations=[dict(name='course_facts', target=0)]))
    before = ConversationContext.parse(dict(operation='list_missing_prerequisites'))
    assert repeat_previous_check(value, 'pano yung A1?', before).operations[0].name == 'list_missing_prerequisites'
    assert repeat_previous_check(value, 'How many units is A1?', before) is None
    assert repeat_previous_check(value, 'pano yung A1?', ConversationContext.parse(dict(operation='list_term_courses'))) is None

def test_the_parser_folds_a_fact_part_that_repeats_the_check():
    # Live replay 3 Nov 2026: the wire parser rejected this shape as uncontained_part_target before validation ran.
    import json
    from backend.bintanong_routing.wire import WireInterpretation, normalize_interpretation
    text = 'Can I take B1 next sem?\n\nNot passed A1.'
    quote = lambda t, n=0: dict(text=t, occurrence=n)
    wire = dict(schema_version='bintanong-interpretation-wire-v4', language='en', audience='undergraduate', control=None,
                part_count=2, parts=[dict(part_id='r1', quote=quote('Can I take B1 next sem?'), evidence_need='structured',
                                          operation_indices=[0], subject_id=None, requested_claims=[], detail='whole'),
                                     dict(part_id='r2', quote=quote('Not passed A1.', 1), evidence_need='structured',
                                          operation_indices=[0], subject_id=None, requested_claims=[], detail='whole')],
                intent='eligibility check', mentions=[dict(kind='course', quote=quote('B1')), dict(kind='course', quote=quote('A1', 1))],
                claims=[dict(quote=quote('Not passed A1.', 1), entity=quote('A1', 1), state='failed', mode='asserted')],
                operations=[dict(name='check_prerequisite_eligibility', target=quote('B1'))], route='Symbolic', ambiguities=[])
    result = normalize_interpretation(text, WireInterpretation.parse(json.loads(json.dumps(wire))))
    assert [(p.part_id, p.operation_indices) for p in result.parts] == [('r1', (0,))]
    assert [c.state for c in result.claims] == ['failed']

def test_a_named_course_with_next_semester_is_an_eligibility_check():
    # Gate 4 Nov 2026 (recorded, 19 of 25): "Can I take AE8 next semester? I haven't taken AE3 yet." chose the
    # term-plan check because of "next semester" and asked for a term; it names the course it asks about.
    from backend.bintanong_routing.router import named_course_check
    from test_routing_contracts import proposal
    text = 'Can I take B1 next semester? Not taken A1.'
    mentions = [dict(kind='course', text='B1', start=11, end=13), dict(kind='course', text='A1', start=39, end=41),
                dict(kind='term', text='next semester', start=14, end=27)]
    value = Interpretation.parse(proposal(text=text, mentions=mentions,
        claims=[dict(entity=1, state='not_taken', mode='asserted', text='Not taken A1.', start=29, end=42)],
        operations=[dict(name='assess_term_prerequisites', target=2)],
        parts=[dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='structured', operation_indices=[0])]))
    fixed = named_course_check(value)
    assert (fixed.operations[0].name, fixed.operations[0].target) == ('check_prerequisite_eligibility', 0)
    plan = Interpretation.parse(proposal(text='What can I take next semester?', mentions=[dict(kind='term',
        text='next semester', start=16, end=29)], operations=[dict(name='assess_term_prerequisites', target=0)],
        parts=[dict(part_id='r1', text='What can I take next semester?', start=0, end=30, evidence_need='structured',
                    operation_indices=[0])]))
    assert named_course_check(plan) is None
