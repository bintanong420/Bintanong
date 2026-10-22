"""Synthetic missing-condition and potential-dependency operations."""
from __future__ import annotations

import copy

import pytest

from test_symbolic_runtime import api, expression_ledger, facts, fixture, request, rereview, runtime


@pytest.mark.parametrize('passed,failed,outcome',[((),(),'unknown'),((),('course-1',),'ineligible'),(('course-1',),(),'eligible')])
def test_missing_prerequisites_preserves_known_unmet_and_unknown(passed,failed,outcome):
    result=runtime().check(request(predicate='list_missing_prerequisites'),facts(passed=passed,failed=failed))
    assert result.decision.outcome==outcome
    assert result.decision.predicate=='list_missing_prerequisites'
    if failed: assert result.decision.violated_conditions==('not_completed:course-1',)
    if not passed and not failed: assert result.decision.missing_facts==('completion_unknown:course-1',)


def chain(first_link='course'):
    data=fixture();data[2][1]['prerequisites']['kind']=first_link;c=copy.deepcopy(data[2][0]);c['course_id']='course-3'
    c['facts']['course_code']['value']='SYN301'
    c['facts']['course_code']['source_spans'][0]['text']='SYN301'
    c['prerequisites']=copy.deepcopy(data[2][1]['prerequisites'])
    c['prerequisites']['kind']='course';c['prerequisites']['course_id']='course-2'
    data[2].append(c)
    return rereview(data)


def query(runner=None,**kw):
    runner=runtime() if runner is None else runner
    return runner.list_affected_courses(request(predicate='list_affected_courses',**kw))


def test_dependency_lookup_includes_transitive_potential_dependents_and_sources():
    result=query(runtime(chain()),course='course-1')
    assert result.status=='complete' and result.course_ids==('course-2','course-3')
    assert result.relation=='potential_prerequisite_or_corequisite_dependency'
    assert result.coverage_scope=='supplied_bundle' and result.rule_ids and result.rule_spans
    assert result.synthetic is True and result.activation_allowed is result.eligibility_executable is False


def test_any_of_dependency_is_potential():
    result=query(runtime(expression_ledger('any_of')),course='course-1')
    assert result.course_ids==('course-2',) and result.relation.startswith('potential_')


def test_corequisite_dependents_are_listed_directly_and_transitively():
    # Failing a co-requisite without taking it the same term blocks the dependent, so it is affected.
    result=query(runtime(chain('co_requisite')),course='course-1')
    assert result.status=='complete' and result.course_ids==('course-2','course-3')
    assert result.relation=='potential_prerequisite_or_corequisite_dependency'


def test_unresolved_rule_makes_listing_partial_even_when_no_dependents_found():
    data=fixture();c=data[2][1]
    c['prerequisites']={'kind':'unresolved','reason':'Fictional missing rule','source_spans':c['prerequisites']['source_spans']}
    result=query(runtime(rereview(data)),course='course-1')
    assert result.status=='partial' and not result.course_ids and result.unknown_conditions


@pytest.mark.parametrize('over',[{'course':'missing'},{'curriculum':'other'}])
def test_missing_identity_or_wrong_curriculum_has_no_borrowed_provenance(over):
    result=query(**over)
    assert result.status=='partial' and result.unknown_conditions
    assert not result.course_ids and not result.rule_spans and not result.rule_ids


def test_dependency_result_limit_and_worker_failure_do_not_become_empty_success(monkeypatch):
    result=query(runtime(chain(),max_conditions=1),course='course-1')
    assert result.status=='error' and result.error_code=='runtime_result_limit' and not result.course_ids
    def fail(*a): raise OSError('unavailable')
    monkeypatch.setattr(api(),'_invoke_worker',fail)
    result=query(course='course-1')
    assert result.status=='error' and result.error_code=='runtime_unavailable'


def test_dependency_unsupported_and_scope_errors_do_not_execute_worker(monkeypatch):
    monkeypatch.setattr(api(),'_invoke_worker',lambda *a:pytest.fail('must not execute'))
    result=runtime().list_affected_courses(request(predicate='other'))
    assert result.status=='unsupported' and not result.rule_ids


def test_dependency_source_provenance_counts_toward_result_cap():
    data=fixture();data[2][1]['prerequisites']['source_spans'][0]['text']='Fictional rule '+('x'*70_000)
    result=query(runtime(rereview(data)),course='course-1')
    assert result.status=='error' and result.error_code=='runtime_result_limit'


@pytest.mark.parametrize('field',['rule_bundle_version','scope'])
def test_complete_empty_listing_still_requires_its_bundle_and_scope(field):
    result=query(course='course-2')
    assert result.status=='complete' and not result.course_ids
    data=result.model_dump(mode='json');data[field]=None
    with pytest.raises(ValueError): api().DependencyResult.parse(data)


@pytest.mark.parametrize('change',[{'text':None},{'version_id':None}])
def test_dependency_result_cannot_cite_an_incomplete_source_span(change):
    data=query(course='course-1').model_dump(mode='json')
    data['rule_spans'][0].update(change)
    with pytest.raises(ValueError): api().DependencyResult.parse(data)


def test_dependency_public_result_rejects_duplicate_ids():
    data=query(course='course-1').model_dump(mode='json')
    data['course_ids']*=2
    with pytest.raises(ValueError): api().DependencyResult.parse(data)


@pytest.mark.parametrize('field',['rule_bundle_version','rule_ids','unknown_conditions','error_code'])
def test_dependency_public_result_rejects_empty_labels(field):
    data=query(course='course-1').model_dump(mode='json')
    if field=='unknown_conditions': data.update(status='partial',unknown_conditions=[''])
    elif field=='error_code':
        data=query(course='course-1').model_dump(mode='json')
        data.update(status='error',course_ids=[],unknown_conditions=[],rule_ids=[],rule_spans=[],
                    rule_bundle_version=None,scope=None,error_code='')
    else: data[field]=[''] if field=='rule_ids' else ''
    with pytest.raises(ValueError): api().DependencyResult.parse(data)


@pytest.mark.parametrize('over',[{'curriculum':'other'},{}])
def test_worker_cannot_claim_complete_for_unbound_or_incomplete_bundle(monkeypatch,over):
    data=fixture();data[2][1]['prerequisites']['kind']='unresolved'
    data[2][1]['prerequisites'].pop('course_id');data[2][1]['prerequisites']['reason']='Fictional unknown'
    runner=runtime(rereview(data))
    monkeypatch.setattr(api(),'_invoke_worker',lambda *a:api()._DependencyEvaluation(
        status='complete',course_ids=(),unknown_conditions=()))
    result=query(runner,**over)
    assert result.status=='error' and result.error_code=='runtime_invalid_output'


def test_dependency_query_identifiers_remain_data():
    result=query(course="course-1'),halt(9),('")
    assert result.status=='partial' and not result.course_ids
    assert query(course='course-1').course_ids==('course-2',)
