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


def test_shared_program_name_asks_which_program():
    other = CatalogEntry.parse(dict(kind='program', entity_id='program-b', program_id='program-b', curriculum_id=None,
        aliases=['Program A'], source_ref='ver-a', review_ref='review-a', reviewed=True))
    entries = (*catalog(), other)
    text = 'Program A A1'
    value = proposal(text=text, mentions=[dict(kind='program', text='Program A', start=0, end=9),
        dict(kind='course', text='A1', start=10, end=12)],
        operations=[dict(name='check_prerequisite_eligibility', target=1)])
    result = validate(text, value, context(program_id=None, curriculum_id=None), catalog=entries)
    assert result.decision.control == 'clarify' and result.decision.route is None


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


@pytest.mark.parametrize('mode,expected', [('asserted','validated'),
                                         ('hypothetical','nonasserted_facts'),
                                         ('reported','nonasserted_facts')])
def test_claims_remain_grounded_and_request_local(mode, expected):
    value = proposal(claims=[dict(entity=0, state='failed', mode=mode,
                                 text='A1 failed', start=0, end=9)])
    result = validate('A1 failed', value)
    assert result.diagnostic == expected
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
