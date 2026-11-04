"""Offline plan-entry helpers and replies; synthetic curricula only."""
import asyncio
import pytest
from test_planning_check import curriculum, CURRICULA, POLICY, regular, plan
from backend.bintanong_planning.chat import parse_plan_terms, earliest_term
from backend.bintanong_generation.plan_check_reply import plan_check_lines, earliest_term_lines
from backend.bintanong_planning.checker import check_plan
from backend.bintanong_routing.contracts import CatalogEntry, RequestContext
from backend.bintanong_orchestration.adapters import SymbolicAdapter


def catalog(key):
    return tuple(CatalogEntry(kind='course', entity_id='course-' + ''.join(x for x in code.lower() if x.isalnum()),
        program_id='program-synthetic', curriculum_id=key, aliases=(code,), source_ref='ver-synthetic',
        review_ref='review-synthetic', reviewed=True) for code in CURRICULA[key].values())


def test_parse_sequence_and_modes(curriculum):
    key, runtime, c = curriculum
    codes = CURRICULA[key]
    text = f"2nd year 2nd sem: {codes['X']} special class; summer: {codes['D1']}, {codes['D2']}; 3rd year 1st sem: {codes['T0']}"
    request = parse_plan_terms(text, catalog(key), key)
    assert [t.kind for t in request.terms] == ['regular', 'summer', 'regular']
    assert request.terms[0].courses[0].mode == 'special_class_request'
    assert request.terms[1].courses[0].mode == 'summer'
    assert request.terms[2].courses[0].course_id == c('T0')
    with pytest.raises(ValueError, match='term_required'):
        parse_plan_terms(f"2nd sem: {codes['X']}", catalog(key), key)
    with pytest.raises(ValueError, match='course_unresolved'):
        parse_plan_terms('2nd year 2nd sem: QQ 999', catalog(key), key)


def test_plan_order_is_not_silently_reordered(curriculum):
    key, _, _ = curriculum
    code = CURRICULA[key]['X']
    with pytest.raises(ValueError, match='terms_not_in_order'):
        parse_plan_terms(f'3rd year 1st sem: {code}; 2nd year 2nd sem: {code}', catalog(key), key)


@pytest.mark.parametrize('language', ['en', 'taglish'])
def test_plan_replies_block_confirm_and_warn(curriculum, language):
    key, runtime, c = curriculum
    request = plan(key, [(c('BASE'), 'passed')], regular(2, 'second_semester', (c('X'), 'special_class_request')),
        regular(3, 'first_semester', (c('D1'), 'prescribed')))
    result = check_plan(request, runtime, POLICY)
    text = '\n'.join(plan_check_lines(request, result, language, lambda x: x))
    assert ('Works, needs confirmation' if language == 'en' else 'Works, may kailangan pang i-confirm') in text
    assert 'adviser' in text and 'requested' in text or 'ni-request' in text
    blocked = plan(key, [(c('X'), 'failed')], regular(2, 'second_semester', (c('D1'), 'prescribed')))
    text = '\n'.join(plan_check_lines(blocked, check_plan(blocked, runtime, POLICY), language, lambda x: x))
    assert 'Blocked' in text and c('X') in text
    for phrase in ('Supported prerequisite check', 'conditions satisfied', 'Based on the supplied evidence'):
        assert phrase not in text


def test_earliest_regular_chain_with_explicit_failure(curriculum):
    key, runtime, c = curriculum
    result = earliest_term(runtime, key, c('Z'), [(c('X'), 'failed')], (2, 'second_semester'))
    assert result.status == 'found'
    assert result.rule_spans and result.scope is not None
    assert (result.term.year, result.term.semester) == (4, 'second_semester')
    assert c('X') in result.assumed_passes and c('D1') in result.assumed_passes
    for language in ('en', 'taglish'):
        text = '\n'.join(earliest_term_lines(result, language, lambda x: x))
        assert c('Z') in text and 'adviser' in text


def test_adapter_rejects_context_scope_and_fact_replacement(curriculum):
    key, runtime, c = curriculum
    adapter = SymbolicAdapter(runtime, recovery=(POLICY, None))
    request = plan(key, [], regular(2, 'first_semester', (c('X'), 'prescribed')))
    context = RequestContext(request_id='req-plan', session_id='sess-plan', program_id='program-synthetic', curriculum_id=key)
    result = asyncio.run(adapter.check_typed_plan(request, context))
    assert result.curriculum_id == key
    other = context.model_copy(update={'curriculum_id':'curriculum-foreign'})
    with pytest.raises(ValueError, match='request_scope_mismatch'):
        asyncio.run(adapter.check_typed_plan(request, other))


def test_parser_ambiguous_aliases_and_unsupported_trailing_text(curriculum):
    key, _, _ = curriculum
    entries = catalog(key)
    shared = tuple(e.model_copy(update={'aliases': ('SAME',)}) for e in entries[:2])
    with pytest.raises(ValueError, match='course_ambiguous'):
        parse_plan_terms('2nd year 1st sem: SAME', shared, key)
    with pytest.raises(ValueError, match='course_unresolved'):
        parse_plan_terms(f"2nd year 1st sem: {CURRICULA[key]['X']} please approve", entries, key)


def test_earliest_unknown_rule_never_guesses(curriculum):
    key, runtime, c = curriculum
    class Unreviewed:
        def look_up(self, request):
            return runtime.look_up(request)
        def check(self, request, facts):
            from types import SimpleNamespace
            return SimpleNamespace(decision=SimpleNamespace(outcome='unknown'), requirement=None)
    result = earliest_term(Unreviewed(), key, c('X'), [], (2, 'first_semester'))
    assert result.status == 'unknown' and result.term is None


def test_request_facts_cannot_replace_session_assertions(curriculum):
    key, runtime, c = curriculum
    adapter = SymbolicAdapter(runtime, recovery=(POLICY, None))
    request = plan(key, [(c('BASE'), 'passed')], regular(2, 'first_semester', (c('X'), 'prescribed')))
    context = RequestContext(request_id='req-plan', session_id='sess-plan', program_id='program-synthetic', curriculum_id=key)
    with pytest.raises(ValueError, match='plan_facts_must_match_context'):
        asyncio.run(adapter.check_typed_plan(request, context))


def test_integration_rejects_plan_without_ready_pinned_evidence(curriculum):
    from backend.bintanong_orchestration.contracts import IntegrationResult
    key, runtime, c = curriculum
    request = plan(key, [], regular(2, 'first_semester', (c('X'), 'prescribed')))
    checked = check_plan(request, runtime, POLICY)
    with pytest.raises(ValueError, match='plan_check_requires_ready_pinned_evidence'):
        IntegrationResult(schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-plan',
            route=None, response_style='en', status='clarify', evidence=None, understanding=None, events=(),
            plan_check=checked)


def test_co_requisite_reply_does_not_turn_same_term_into_prior_completion(curriculum):
    key, runtime, c = curriculum
    request = plan(key, [(c('PAIR_B'), 'not_taken')], regular(1, 'second_semester', (c('PAIR_A'), 'prescribed')))
    result = check_plan(request, runtime, POLICY)
    text = '\n'.join(plan_check_lines(request, result, 'en', lambda x: x))
    assert result.terms[0].outcome == 'blocked'
    assert f"needs {c('PAIR_B')} first." not in text


def test_earliest_never_counts_an_uncheckable_corequisite_as_available(curriculum):
    key, runtime, c = curriculum
    class MissingPairRule:
        def look_up(self, request):
            return runtime.look_up(request)
        def check(self, request, facts):
            from types import SimpleNamespace
            target = next(i.value for i in request.inputs if i.name == 'course_id')
            if target == c('PAIR_B'):
                return SimpleNamespace(decision=SimpleNamespace(outcome='unknown'), requirement=None)
            return runtime.check(request, facts)
    result = earliest_term(MissingPairRule(), key, c('PAIR_A'), [], (1, 'second_semester'))
    assert result.status == 'unknown' and result.term is None


def test_summer_warning_and_approval_conditions_keep_policy_sources(curriculum):
    from test_planning_recovery import ROUTES
    key, runtime, c = curriculum
    request = plan(key, [(c('X'), 'passed'), (c('AUX'), 'passed')],
        {'kind':'summer', 'year_level':None, 'semester':None,
         'courses':[{'course_id':c(n), 'mode':'summer'} for n in ('D1','D2','Y','LINK')]})
    result = check_plan(request, runtime, POLICY)
    for language in ('en', 'taglish'):
        text = '\n'.join(plan_check_lines(request, result, language, lambda x:x, routes=ROUTES))
        assert 'Heads-up' in text and '12' in text and '9' in text
        assert 'Student Handbook p. 1' in text and 'Fictional summer clause.' in text
        assert ('not yet approved' if language == 'en' else 'hindi pa approved') in text


def test_integration_plan_field_is_pinned_to_the_same_release(curriculum):
    from test_generation_evidence import integrated
    key, runtime, c = curriculum
    request = plan(key, [], regular(2, 'first_semester', (c('X'), 'prescribed')))
    result = check_plan(request, runtime, POLICY)
    base = integrated('Symbolic')
    predicate = base.understanding.predicate_request
    predicate = type(predicate).parse({**predicate.model_dump(mode='json'), 'inputs': [
        *predicate.model_dump(mode='json')['inputs'], {'name':'curriculum_id', 'value':'curriculum-a', 'fact_ref':None}]})
    base = base.model_copy(update={'understanding':base.understanding.model_copy(update={'predicate_request':predicate})})
    checked = result.model_copy(update={'curriculum_id':'curriculum-a',
        'scope':base.evidence.symbolic.scope, 'rule_spans':base.evidence.symbolic.rule_spans})
    assert base.model_copy(update={'plan_check':checked}).plan_check == checked
    foreign = checked.model_copy(update={'scope':checked.scope.model_copy(update={
        'knowledge_release_id':'release-foreign'})})
    with pytest.raises(ValueError, match='plan_check_release_mismatch'):
        base.model_copy(update={'plan_check':foreign})
