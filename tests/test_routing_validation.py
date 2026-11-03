"""Exact synthetic entity scopes and guardrails around model proposals."""
import importlib

import pytest

from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry, EMPTY_REGISTRY
from backend.bintanong_routing.contracts import CatalogEntry, Interpretation, RequestContext
from test_routing_contracts import context, proposal


def api():
    return importlib.import_module('backend.bintanong_routing.validation')


def entry(kind='course', entity='course-a', alias='A1', curriculum='curriculum-a'):
    return CatalogEntry.parse(dict(kind=kind, entity_id=entity, program_id='program-a',
        curriculum_id=curriculum, aliases=[alias], source_ref='ver-a', review_ref='review-a', reviewed=True))


def catalog():
    return (entry(), entry(entity='course-b', alias='B1'),
            entry(kind='program', entity='program-a', alias='Program A', curriculum=None),
            entry(kind='curriculum', entity='curriculum-a', alias='Edition A'))


def registry():
    return CapabilityRegistry({'check_prerequisite_eligibility': Capability(
        'synthetic_prerequisite_check', ('curriculum_id', 'course_id'))})


def validate(text='A1', value=None, ctx=None, **options):
    defaults = dict(catalog=catalog(), registry=registry(), documents_available=True, synthetic=True)
    defaults.update(options)
    return api().validate_interpretation(text, RequestContext.parse(context() if ctx is None else ctx),
        Interpretation.parse(proposal() if value is None else value), **defaults)


def test_supported_operation_uses_fixed_scoped_bound_inputs_and_response_style():
    result = validate()
    assert result.decision.route == 'Symbolic' and result.diagnostic == 'validated'
    assert result.response_style == 'taglish'
    assert {i.name: i.value for i in result.decision.predicate_request.inputs} == {
        'course_id': 'course-a', 'curriculum_id': 'curriculum-a'}
    assert result.query.original_text == 'A1' and result.query.entities[0].value == 'course-a'
    assert not result.claims


@pytest.mark.parametrize('options,control,diagnostic', [
    (dict(registry=EMPTY_REGISTRY), 'evidence_unavailable', 'unsupported_operation'),
    (dict(synthetic=False), 'evidence_unavailable', 'institutional_execution_held'),
    (dict(documents_available=False), 'evidence_unavailable', 'documents_unavailable')])
def test_components_never_fall_back_to_rag(options, control, diagnostic):
    text = 'A1 policy' if 'documents_available' in options else 'A1'
    value = proposal(text=text, route='Hybrid') if 'documents_available' in options else proposal()
    result = validate(text, value=value, **options)
    assert result.proposed.route in ('Symbolic', 'Hybrid')
    assert result.decision.control == control and result.decision.route is None
    assert result.diagnostic == diagnostic


def test_curriculum_is_never_inferred_from_a_course_alias():
    # Two reviewed editions of the program: the course alias alone never picks one.
    entries = (*catalog(), entry(kind='curriculum', entity='curriculum-old', alias='Edition Old', curriculum='curriculum-old'))
    result = validate(ctx=context(curriculum_id=None), catalog=entries)
    assert result.decision.control == 'clarify'
    assert result.decision.missing_facts == ('curriculum_id',)
    assert result.diagnostic == 'missing_scope'


def test_program_with_one_reviewed_curriculum_uses_it():
    # Owner decision, 24 Oct 2026: a program with exactly one reviewed curriculum uses it.
    result = validate(ctx=context(curriculum_id=None))
    assert result.decision.route == 'Symbolic' and result.curriculum_id == 'curriculum-a'
    assert {i.name: i.value for i in result.decision.predicate_request.inputs}['curriculum_id'] == 'curriculum-a'


def test_program_named_in_text_with_one_curriculum_needs_no_session_scope():
    text = 'Program A A1'
    value = proposal(text=text, mentions=[dict(kind='program', text='Program A', start=0, end=9),
        dict(kind='course', text='A1', start=10, end=12)],
        operations=[dict(name='check_prerequisite_eligibility', target=1)])
    result = validate(text, value, context(program_id=None, curriculum_id=None))
    assert result.decision.route == 'Symbolic' and (result.program_id, result.curriculum_id) == ('program-a', 'curriculum-a')


def _shared_program_name():
    other = CatalogEntry.parse(dict(kind='program', entity_id='program-b', program_id='program-b', curriculum_id=None,
        aliases=['Program A'], source_ref='ver-a', review_ref='review-a', reviewed=True))
    text = 'Program A A1'
    value = proposal(text=text, mentions=[dict(kind='program', text='Program A', start=0, end=9),
        dict(kind='course', text='A1', start=10, end=12)],
        operations=[dict(name='check_prerequisite_eligibility', target=1)])
    return text, value, (*catalog(), other)


def test_shared_program_name_asks_which_program():
    text, value, entries = _shared_program_name()
    result = validate(text, value, context(program_id=None, curriculum_id=None), catalog=entries)
    assert result.decision.control == 'clarify' and result.decision.route is None
    assert result.decision.missing_facts == ('program_choice:program-a', 'program_choice:program-b')


def test_selected_program_settles_a_name_shared_with_another_program():
    # Live 31 Oct 2026: "Hospitality Management" with the Hotel track selected also matched Culinary.
    text, value, entries = _shared_program_name()
    result = validate(text, value, context(), catalog=entries)
    assert result.decision.route == 'Symbolic' and result.program_id == 'program-a'


@pytest.mark.parametrize('text', ['A8 / B2', 'A8/B2'])
def test_a_printed_code_split_into_two_mentions_names_one_course(text):
    # Live 31 Oct 2026: the model split "HPC 8 / FL 2" into "HPC 8" and "FL 2", so neither matched a course.
    second = text.index('B2')
    value = proposal(text=text, mentions=[dict(kind='course', text='A8', start=0, end=2),
        dict(kind='course', text='B2', start=second, end=second + 2)])
    result = validate(text, value, catalog=(*catalog(), entry(entity='course-joined', alias='A8 / B2')))
    assert result.decision.route == 'Symbolic' and result.diagnostic == 'validated'
    assert result.decision.predicate_request.inputs[-1].value == 'course-joined'


def test_reused_course_alias_resolves_only_in_explicit_edition():
    entries = (*catalog(), entry(entity='course-old', curriculum='curriculum-old'))
    assert validate(catalog=entries).decision.predicate_request.inputs[-1].value == 'course-a'
    result = validate(catalog=entries, ctx=context(curriculum_id='curriculum-old'))
    assert result.decision.predicate_request.inputs[-1].value == 'course-old'
    assert validate(catalog=(*entries, entry(entity='course-duplicate'))).diagnostic == 'unresolved_entity'


def test_exact_program_and_curriculum_mentions_can_supply_explicit_scope():
    text = 'Program A Edition A A1'
    value = proposal(mentions=[dict(kind='program', text='Program A', start=0, end=9),
        dict(kind='curriculum', text='Edition A', start=10, end=19),
        dict(kind='course', text='A1', start=20, end=22)],
        operations=[dict(name='check_prerequisite_eligibility', target=2)])
    assert validate(text, value, context(program_id=None, curriculum_id=None)).decision.route == 'Symbolic'
    assert validate(text, value, context(curriculum_id='curriculum-other')).diagnostic == 'scope_conflict'


@pytest.mark.parametrize('value,diagnostic', [
    (proposal(operations=[dict(name='arbitrary_prolog', target=0)]), 'unsupported_operation'),
    (proposal(operations=[dict(name='check_prerequisite_eligibility', target=0)] * 2), 'compound_request'),
    (proposal(ambiguities=['Which course?']), 'model_ambiguity'),
    (proposal(audience='excluded'), 'unsupported_scope'),
    (proposal(audience='unknown'), 'audience_unknown'),
    (proposal(route='RAG'), 'inconsistent_proposal')])
def test_model_semantics_do_not_override_structural_guards(value, diagnostic):
    result = validate(value=value)
    assert not result.decision.dispatchable and result.diagnostic == diagnostic


def test_rag_does_not_need_student_curriculum_but_needs_document_availability():
    value = proposal(text='Where do I ask?', route='RAG', operations=[], mentions=[], intent='procedure')
    assert validate('Where do I ask?', value, context(program_id=None, curriculum_id=None)).decision.route == 'RAG'
    assert validate('Where do I ask?', value, documents_available=False).decision.control == 'evidence_unavailable'


def test_false_quote_is_rejected_even_if_the_mention_is_a_known_course():
    with pytest.raises(ValueError, match='ungrounded_mention'):
        validate('B1')


# Memory/eligibility plan: a what-if premise is request-only for its check; a reported result adds no fact.
@pytest.mark.parametrize('mode', ['asserted', 'hypothetical'])
def test_claims_remain_grounded_and_request_local(mode):
    value = proposal(claims=[dict(entity=0, state='failed', mode=mode,
                                 text='A1 failed', start=0, end=9)])
    result = validate('A1 failed', value)
    assert result.diagnostic == 'validated'
    assert result.claims[0].mode == mode and result.claims[0].state == 'failed'
    assert result.claims[0].session_id == 'sess-a'
    other = validate('A1 failed', value, context(session_id='sess-b'))
    assert result.claims[0].fact_id != other.claims[0].fact_id
    assert result.query.session_fact_refs == (result.claims[0].fact_id,)


def test_conflicting_session_facts_are_not_overwritten():
    value = proposal(claims=[dict(entity=0, state='failed', mode='asserted',
                                 text='A1 failed', start=0, end=9)])
    ctx = context(facts=[dict(fact_id='fact-original', session_id='sess-a',
        program_id='program-a', curriculum_id='curriculum-a', course_id='course-a', state='passed')])
    result = validate('A1 failed', value, ctx)
    assert result.diagnostic == 'conflicting_facts' and not result.decision.dispatchable
    assert RequestContext.parse(ctx).facts[0].state == 'passed'


def test_claim_quote_cannot_be_assigned_to_an_unrelated_mention():
    value = proposal(claims=[dict(entity=0, state='failed', mode='asserted',
                                 text='failed', start=3, end=9)])
    with pytest.raises(ValueError, match='ungrounded_claim'):
        validate('A1 failed', value)


def test_document_only_request_does_not_require_resolving_irrelevant_grade_conflicts():
    ctx = context(facts=[dict(fact_id='fact-'+state, session_id='sess-a',
        program_id='program-a', curriculum_id='curriculum-a', course_id='course-a', state=state)
        for state in ['passed','failed']])
    result = validate('Where do I request a copy?',
        proposal(text='Where do I request a copy?', route='RAG', operations=[], mentions=[], intent='procedure'), ctx)
    assert result.decision.route == 'RAG'
    assert len(result.query.session_fact_refs) == 2  # preserve conflict for any later check


def test_unmatched_scope_phrase_is_ignored_on_a_document_only_question():
    # Owner, 23 Oct 2026 (run 9): "Graduating undergraduate sa last semester" quoted as a curriculum.
    text = 'Graduating student: where do I ask?'
    value = proposal(text=text, route='RAG', operations=[], intent='procedure',
        mentions=[dict(kind='curriculum', text='Graduating student', start=0, end=18)])
    assert validate(text, value, context(program_id=None, curriculum_id=None)).decision.route == 'RAG'


def test_unmatched_scope_phrase_still_clarifies_a_course_question():
    text = 'Graduating student A1'
    value = proposal(text=text, mentions=[dict(kind='curriculum', text='Graduating student', start=0, end=18),
        dict(kind='course', text='A1', start=19, end=21)], operations=[dict(name='check_prerequisite_eligibility', target=1)])
    result = validate(text, value)
    assert result.decision.control == 'clarify' and result.diagnostic == 'unresolved_entity'


def program_question(phrase, text_tail=' A1'):
    text = phrase + text_tail
    return text, proposal(text=text, mentions=[dict(kind='program', text=phrase, start=0, end=len(phrase)),
        dict(kind='course', text='A1', start=len(phrase) + 1, end=len(phrase) + 3)],
        operations=[dict(name='check_prerequisite_eligibility', target=1)])


@pytest.mark.parametrize('phrase', ['Program A student ako', 'I am a Program A student', 'program a student'])
def test_approved_program_name_inside_the_quoted_phrase_resolves(phrase):
    # Owner, 24 Oct 2026: the model quotes the student's own phrase; the host finds the approved name inside it.
    text, value = program_question(phrase)
    result = validate(text, value, context(program_id=None, curriculum_id=None))
    assert result.decision.route == 'Symbolic' and result.program_id == 'program-a'


def test_short_uppercase_name_matches_only_as_written():
    short = CatalogEntry.parse(dict(kind='program', entity_id='program-a', program_id='program-a', curriculum_id=None,
        aliases=['IT'], source_ref='ver-a', review_ref='review-a', reviewed=True))
    entries = (*[e for e in catalog() if e.kind != 'program'], short)
    for phrase, route in (('IT student ako', 'Symbolic'), ('it student ako', None)):
        text, value = program_question(phrase)
        assert validate(text, value, context(program_id=None, curriculum_id=None), catalog=entries).decision.route == route


def test_phrase_naming_two_programs_asks_which():
    other = CatalogEntry.parse(dict(kind='program', entity_id='program-b', program_id='program-b', curriculum_id=None,
        aliases=['Program B'], source_ref='ver-a', review_ref='review-a', reviewed=True))
    text, value = program_question('Program A or Program B student')
    result = validate(text, value, context(program_id=None, curriculum_id=None), catalog=(*catalog(), other))
    assert result.decision.control == 'clarify'


# Memory/eligibility plan, Task 1: the host keeps only what the student's own words state.
def stated(text, state, mode='asserted', course='A1', **updates):
    start = text.index(course)
    mention = dict(kind='course', text=course, start=start, end=start + len(course))
    target = text.rfind('B1')
    mentions = [mention] + ([dict(kind='course', text='B1', start=target, end=target + 2)] if target > start else [])
    value = proposal(text=text, mentions=mentions,
                     claims=[dict(entity=0, state=state, mode=mode, text=text, start=0, end=len(text))],
                     operations=[dict(name='check_prerequisite_eligibility', target=len(mentions) - 1)]
                     if len(mentions) > 1 else [], **updates)
    if len(mentions) > 1:
        value['parts'] = [dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='structured',
                               operation_indices=[0])]
    return validate(text, value)


@pytest.mark.parametrize('text,proposed,kept', [
    ('Natake ko na yung A1. Can I take B1?', 'passed', 'taken_unknown'),
    ("I haven't taken A1 yet. Can I take B1?", 'failed', 'not_taken'),
    ('Hindi ko pa napapasa ang A1. Pwede na ba ang B1?', 'failed', 'not_passed'),
    ('I failed A1. Can I take B1?', 'failed', 'failed'),
    ('Pasado ako sa A1. Pwede na ba ang B1?', 'passed', 'passed'),
])
def test_host_keeps_the_result_the_student_stated_not_the_models_label(text, proposed, kept):
    result = stated(text, proposed)
    assert result.diagnostic == 'validated'
    assert [(c.course_id, c.state) for c in result.claims] == [('course-a', kept)]


@pytest.mark.parametrize('text', ['My friend passed A1. Can I take B1?', 'I got 1.75 in A1. Can I take B1?'])
def test_a_claim_the_students_words_do_not_support_supplies_no_fact(text):
    result = stated(text, 'passed')
    assert result.diagnostic == 'validated' and result.claims == ()


def test_a_what_if_premise_is_request_only_and_reported_results_add_nothing():
    hypothetical = stated('If I failed A1, can I take B1?', 'failed', mode='hypothetical')
    assert hypothetical.diagnostic == 'validated'
    assert [(c.state, c.mode) for c in hypothetical.claims] == [('failed', 'hypothetical')]
    reported = stated('My classmate said A1 was passed. Can I take B1?', 'passed', mode='reported')
    assert reported.diagnostic == 'validated' and reported.claims == ()


def test_a_message_that_only_states_a_result_is_noted():
    text = 'I passed A1'
    value = proposal(text=text, mentions=[dict(kind='course', text='A1', start=9, end=11)], operations=[],
                     claims=[dict(entity=0, state='passed', mode='asserted', text=text, start=0, end=len(text))],
                     route=None, control='clarify')
    result = validate(text, value)
    assert result.diagnostic == 'facts_noted' and result.decision.control == 'clarify'
    assert result.decision.missing_facts == ('noted_passed:course-a',)
    assert [(c.course_id, c.state) for c in result.claims] == [('course-a', 'passed')]


def test_a_stated_enrollment_records_the_term_it_covers():
    now = stated("I'm taking A1 this term. Can I take B1?", 'enrolled')
    later = stated("I'll be taking A1 next sem. Can I take B1?", 'enrolled')
    assert [(c.state, c.period, c.source) for c in now.claims] == [('enrolled', 'current', 'user_statement')]
    assert [(c.state, c.period) for c in later.claims] == [('enrolled', 'next')]


def test_enrollment_counts_only_for_the_term_the_question_asks_about():
    from backend.bintanong_routing.contracts import ScopedFact
    def fact(state, period):
        return ScopedFact(fact_id=f'fact-{state}-{period}'.replace('_', '-').lower(), session_id='sess-a',
                          program_id='program-a', curriculum_id='curriculum-a', course_id='course-a', state=state,
                          source='user_statement', period=period)
    facts = (fact('enrolled', 'current'), fact('passed', None))
    assert [f.state for f in api().facts_for_term(facts, 'Can I take B1 this term?')] == ['enrolled', 'passed']
    assert [f.state for f in api().facts_for_term(facts, 'Can I take B1 next sem?')] == ['passed']
    assert [f.state for f in api().facts_for_term((fact('enrolled', 'next'),), 'Pwede ko bang kunin ang B1 sa susunod na sem?')] == ['enrolled']


@pytest.mark.parametrize('text,mode', [
    ("So if I haven't passed A1, can I take B1?", 'hypothetical'),  # live 3 Nov shape: the model said asserted
    ('Kung bagsak ako sa A1, pwede ko pa bang kunin ang B1?', 'hypothetical'),
    ('What if I failed A1? Can I take B1?', 'hypothetical'),
    ('I failed A1. Can I take B1?', 'asserted'),
    ('I failed A1 even though I studied. Can I take B1?', 'asserted'),
])
def test_a_result_stated_inside_an_if_clause_is_request_only(text, mode):
    result = stated(text, 'failed')
    assert result.diagnostic == 'validated'
    state = 'not_passed' if "haven't passed" in text else 'failed'
    assert [(c.state, c.mode) for c in result.claims] == [(state, mode)]


def test_a_statement_that_disagrees_with_a_confirmed_upload_names_the_course():
    value = proposal(text='A1 failed', claims=[dict(entity=0, state='failed', mode='asserted', text='A1 failed', start=0, end=9)])
    ctx = context(facts=[dict(fact_id='fact-upload', session_id='sess-a', program_id='program-a',
                              curriculum_id='curriculum-a', course_id='course-a', state='passed')])
    result = validate('A1 failed', value, ctx)
    assert result.diagnostic == 'conflicting_facts' and result.decision.missing_facts == ('conflict:course-a',)


def term_slip(text, term, claimed=('A1',)):
    """The model read 'Can I take B1 next semester?' as a term check on 'next semester' (live 4 Nov 2026)."""
    mentions = [dict(kind='course', text=c, start=text.index(c), end=text.index(c) + len(c)) for c in ('B1', 'A1') if c in text]
    mentions.append(dict(kind='term', text=term, start=text.index(term), end=text.index(term) + len(term)))
    claims = [dict(entity=[m['text'] for m in mentions].index(c), state='not_taken', mode='asserted',
                   text=text[text.index("I haven't"):], start=text.index("I haven't"), end=len(text)) for c in claimed]
    value = proposal(text=text, mentions=mentions, claims=claims,
                     operations=[dict(name='assess_term_prerequisites', target=len(mentions) - 1)])
    value['parts'] = [dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='structured', operation_indices=[0])]
    reg = registry()
    from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
    reg = CapabilityRegistry({'check_prerequisite_eligibility': Capability('synthetic_prerequisite_check', ('curriculum_id', 'course_id')),
                              'assess_term_prerequisites': Capability('synthetic_term', ('curriculum_id', 'year_level', 'semester'))})
    return validate(text, value, registry=reg)


def test_a_named_course_question_read_as_a_term_check_is_checked_on_that_course():
    result = term_slip("Can I take B1 next semester? I haven't taken A1 yet.", 'next semester')
    assert result.diagnostic == 'validated'
    request = result.decision.predicate_request
    assert request.predicate == 'check_prerequisite_eligibility'
    assert {i.name: i.value for i in request.inputs}['course_id'] == 'course-b'
    assert [(c.course_id, c.state) for c in result.claims] == [('course-a', 'not_taken')]


def test_a_real_term_question_still_asks_for_the_term():
    result = term_slip("What can I take next semester? I haven't taken A1 yet.", 'next semester')
    assert result.diagnostic == 'missing_term'
