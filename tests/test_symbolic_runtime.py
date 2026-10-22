"""Synthetic runtime acceptance through actual Janus; no institutional execution."""
from __future__ import annotations

import copy
import importlib
import subprocess
from concurrent.futures import ThreadPoolExecutor

import pytest

from backend.bintanong_contracts.runtime import PredicateRequest
from backend.bintanong_contracts.symbolic import EMPTY_REGISTRY, as_policy_result
from test_symbolic_authoring import fixture, run
from test_symbolic_compiler import rereview


def api():
    return importlib.import_module('backend.bintanong_symbolic.runtime')


def request(course='course-2', curriculum='curriculum-synthetic-1', predicate='check_prerequisite_eligibility'):
    return PredicateRequest.parse({'predicate':predicate,'inputs':[
        {'name':'course_id','value':course,'fact_ref':None},
        {'name':'curriculum_id','value':curriculum,'fact_ref':None}]})


def runtime(ledger=None, **kw):
    return api().CurriculumRuntime(run(fixture()) if ledger is None else ledger, **kw)


def facts(**kw):
    return api().StudentFacts.parse(kw)


@pytest.mark.parametrize('passed,failed,outcome', [
    (('course-1',),(), 'eligible'), ((),('course-1',),'ineligible'), ((),(),'unknown'),
    (('course-1',),('course-1',),'unknown'),
])
def test_actual_janus_distinguishes_completion_missing_and_conflict(passed,failed,outcome):
    result=runtime().check(request(),facts(passed=passed,failed=failed))
    assert result.decision.outcome==outcome and result.decision.synthetic is True
    assert result.decision.predicate_supported
    if outcome in ('eligible','ineligible'):
        assert result.rule_ids and result.rule_spans and result.decision.evidence_refs
        assert result.scope.edition_ids==('edition-'+'a'*64,)
    if passed and failed: assert result.decision.unresolved_conflicts
    if not passed and not failed: assert result.decision.missing_facts


def test_explicit_none_is_distinct_from_unknown_rule_and_draft_reference():
    assert runtime().check(request('course-1')).decision.outcome=='eligible'
    data=fixture();c=data[2][0]
    c['prerequisites']={'kind':'unresolved','reason':'Fictional blank cell',
                        'source_spans':c['prerequisites']['source_spans']}
    ledger=rereview(data)
    assert runtime(ledger).check(request('course-1')).decision.outcome=='unknown'
    data=fixture();data[2][0]['review_state']='draft';data[2][0]['review_refs']=[]
    result=runtime(run(data)).check(request(),facts(passed=('course-1',)))
    assert result.decision.outcome=='unknown' and result.decision.rule_coverage=='partial'


@pytest.mark.parametrize('course,curriculum', [('missing','curriculum-synthetic-1'),('course-2','other')])
def test_missing_course_and_wrong_curriculum_are_unknown(course,curriculum):
    result=runtime().check(request(course,curriculum),facts(passed=('course-1',)))
    assert result.decision.outcome=='unknown' and result.decision.rule_coverage=='absent'


def expression_ledger(kind):
    data=fixture()
    extra=copy.deepcopy(data[2][0]);extra['course_id']='course-3'
    extra['facts']['course_code']['value']='SYN301'
    for s in extra['facts']['course_code']['source_spans']: s['text']='SYN301'
    data[2].append(extra)
    leaf=copy.deepcopy(data[2][1]['prerequisites'])
    second=copy.deepcopy(leaf);second['course_id']='course-3'
    data[2][1]['prerequisites']={'kind':kind,'items':[leaf,second],'source_spans':leaf['source_spans']}
    return rereview(data)


@pytest.mark.parametrize('kind,passed,failed,outcome', [
    ('all_of',('course-1','course-3'),(),'eligible'),
    ('all_of',(),('course-1',),'ineligible'),
    ('all_of',('course-1',),(),'unknown'),
    ('any_of',('course-1',),(),'eligible'),
    ('any_of',(),('course-1',),'unknown'),
    ('any_of',(),('course-1','course-3'),'ineligible'),
])
def test_generic_all_of_and_any_of_preserve_unknown_semantics(kind,passed,failed,outcome):
    result=runtime(expression_ledger(kind)).check(request(),facts(passed=passed,failed=failed))
    assert result.decision.outcome==outcome
    if outcome=='eligible':
        assert not result.decision.missing_facts and not result.decision.violated_conditions


@pytest.mark.parametrize('passed,enrolled,outcome', [((),(),'unknown'),((),('course-1',),'eligible'),(('course-1',),(),'eligible')])
def test_corequisite_uses_request_local_current_enrollment(passed,enrolled,outcome):
    data=fixture();data[2][1]['prerequisites']['kind']='co_requisite'
    assert runtime(rereview(data)).check(request(),facts(passed=passed,enrolled=enrolled)).decision.outcome==outcome


def test_unsupported_does_not_start_a_worker_or_register_globally(monkeypatch):
    monkeypatch.setattr(api(),'_invoke_worker',lambda *a:pytest.fail('must not execute'))
    result=runtime().check(request(predicate='unregistered_operation'))
    assert result.decision.outcome=='unsupported' and not result.rule_ids and not result.rule_spans
    assert not EMPTY_REGISTRY.supports('check_prerequisite_eligibility')


def test_ledger_snapshot_is_immutable_and_requests_do_not_leak():
    ledger=run(fixture());runner=runtime(ledger)
    ledger['courses'].clear()
    yes=runner.check(request(),facts(passed=('course-1',)))
    no=runner.check(request())
    again=runner.check(request(),facts(passed=('course-1',)))
    assert yes==again and no.decision.outcome=='unknown'


def test_concurrent_requests_are_isolated_and_deterministic():
    runner=runtime(timeout_seconds=15)
    def call(i): return runner.check(request(),facts(passed=('course-1',) if i%2 else ())).decision.outcome
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(call,range(4)))==['unknown','eligible','unknown','eligible']


def test_injected_values_are_bound_data_not_goals():
    result=runtime().check(request("course-2'),halt(7),('"),facts(passed=("course-1'),halt(7),('",)))
    assert result.decision.outcome=='unknown'
    assert runtime().check(request(),facts(passed=('course-1',))).decision.outcome=='eligible'


def test_refuses_real_sources_and_forged_ledger_before_execution(monkeypatch):
    monkeypatch.setattr(api(),'_invoke_worker',lambda *a:pytest.fail('must not execute'))
    data=fixture();data=(data[0],[data[1][0].model_copy(update={'synthetic':False})],data[2],data[3])
    with pytest.raises(ValueError,match='synthetic'): runtime(rereview(data))
    ledger=run(fixture());ledger['activation_allowed']=True
    with pytest.raises(ValueError): runtime(ledger)


@pytest.mark.parametrize('over', [{'passed':(1,)},{'passed':('x'*129,)},{'synthetic':False},{'passed':tuple(str(i) for i in range(257))}])
def test_fact_boundary_rejects_invalid_private_or_unbounded_inputs(over):
    with pytest.raises(ValueError): facts(**over)


@pytest.mark.parametrize('failure,code', [
    (subprocess.TimeoutExpired('worker',1),'runtime_timeout'),
    (OSError('worker unavailable'),'runtime_unavailable'),
    (ValueError('malformed child output'),'runtime_invalid_output'),
])
def test_worker_failures_are_operational_errors(monkeypatch,failure,code):
    def fail(*a): raise failure
    monkeypatch.setattr(api(),'_invoke_worker',fail)
    result=runtime().check(request(),facts(passed=('course-1',)))
    assert result.decision.outcome=='error' and result.decision.error_code==code
    with pytest.raises(ValueError): as_policy_result(result)


def test_actual_timeout_is_bounded_and_next_request_recovers():
    timed=runtime(timeout_seconds=0.001).check(request(),facts(passed=('course-1',)))
    assert timed.decision.outcome=='error' and timed.decision.error_code=='runtime_timeout'
    assert runtime().check(request(),facts(passed=('course-1',))).decision.outcome=='eligible'


def test_condition_limit_is_error_not_partial_approval():
    result=runtime(expression_ledger('all_of'),max_conditions=1).check(request(),facts(passed=('course-1','course-3')))
    assert result.decision.outcome=='error' and result.decision.error_code=='runtime_result_limit'


def test_known_unmet_conjunct_can_be_reported_with_another_draft_reference():
    ledger=expression_ledger('all_of')
    data=copy.deepcopy(ledger)
    courses=[{k:v for k,v in c.items() if k!='content_sha256'} for c in data['courses']]
    next(c for c in courses if c['course_id']=='course-3').update(review_state='draft',review_refs=[])
    from backend.bintanong_symbolic.authoring import build_curriculum_ledger
    mixed=build_curriculum_ledger(data['scope'],data['sources'],courses,reviews=data['reviews'])
    result=runtime(mixed).check(request(),facts(failed=('course-1',)))
    assert result.decision.outcome=='ineligible' and result.decision.rule_coverage=='partial'
    assert result.decision.prerequisite_rule_state=='resolved'


def test_wrong_curriculum_does_not_attach_another_curriculums_rules():
    result=runtime().check(request(curriculum='other'),facts(passed=('course-1',)))
    assert result.decision.outcome=='unknown' and not result.rule_ids and not result.rule_spans


def test_bundle_identity_pins_the_fixed_engine_bytes(tmp_path,monkeypatch):
    original=runtime()
    path=tmp_path/'engine.pl'
    bundle_api=importlib.import_module('backend.bintanong_symbolic.bundle')
    engine=bundle_api._ENGINE
    path.write_bytes(engine.read_bytes()+b'\n% Changed engine build.\n')
    monkeypatch.setattr(bundle_api,'_ENGINE',path)
    changed=runtime()
    assert original._version!=changed._version


def test_satisfied_alternative_does_not_import_an_unused_conflict():
    result=runtime(expression_ledger('any_of')).check(request(),
        facts(passed=('course-1','course-3'),failed=('course-3',)))
    assert result.decision.outcome=='eligible' and not result.decision.unresolved_conflicts


def test_admission_timeout_releases_nothing_it_does_not_own():
    api()._ADMISSION.acquire()
    try:
        result=runtime(timeout_seconds=.01).check(request())
        assert result.decision.outcome=='error' and result.decision.error_code=='runtime_timeout'
        assert api()._ADMISSION.locked()
    finally:
        api()._ADMISSION.release()
    assert runtime().check(request('course-1')).decision.outcome=='eligible'


@pytest.mark.parametrize('reply',[b'not JSON',b'{"result":{"outcome":"eligible"}}',b'{"error":"eligible"}',b'{}'])
def test_malformed_worker_output_never_becomes_a_policy_outcome(reply,monkeypatch):
    monkeypatch.setattr(api().subprocess,'run',lambda *a,**k:subprocess.CompletedProcess('worker',0,reply,b''))
    result=runtime().check(request())
    assert result.decision.outcome=='error' and result.decision.error_code=='runtime_invalid_output'


@pytest.mark.parametrize('over',[{'timeout_seconds':True},{'timeout_seconds':float('inf')},
    {'timeout_seconds':-1},{'max_conditions':True},{'max_conditions':257}])
def test_invalid_execution_limits_reject(over):
    with pytest.raises(ValueError): runtime(**over)


@pytest.mark.parametrize('passed,failed,enrolled,not_enrolled,outcome',[
    ((),('course-1',),(),(),'unknown'),
    ((),('course-1',),(),('course-1',),'ineligible'),
    ((),('course-1',),('course-1',),(),'eligible'),
    (('course-1',),(),('course-1',),('course-1',),'eligible'),
    (('course-1',),('course-1',),('course-1',),(),'eligible'),
    (('course-1',),('course-1',),('course-1',),('course-1',),'unknown'),
])
def test_corequisite_unknown_enrollment_cannot_become_a_false_denial(passed,failed,enrolled,not_enrolled,outcome):
    data=fixture();data[2][1]['prerequisites']['kind']='co_requisite'
    result=runtime(rereview(data)).check(request(),facts(passed=passed,failed=failed,enrolled=enrolled,not_enrolled=not_enrolled))
    assert result.decision.outcome==outcome


def test_failed_completion_without_enrollment_evidence_stays_unknown():
    data=fixture();data[2][1]['prerequisites']['kind']='co_requisite'
    result=runtime(rereview(data)).check(request(),facts(failed=('course-1',)))
    assert result.decision.outcome=='unknown' and result.decision.unknown_conditions


def partial_ledger(kind):
    data=fixture();leaf=copy.deepcopy(data[2][1]['prerequisites'])
    unknown={'kind':'unresolved','reason':'Fictional unknown exception','source_spans':leaf['source_spans']}
    data[2][1]['prerequisites']={'kind':kind,'items':[leaf,unknown],'source_spans':leaf['source_spans']}
    return rereview(data)


def test_known_failed_conjunct_decides_despite_unresolved_sibling():
    # Owner decision 23 Oct 2026: a clearly failed required course gives ineligible; the unknown part stays listed.
    result=runtime(partial_ledger('all_of')).check(request(),facts(failed=('course-1',)))
    assert result.decision.outcome=='ineligible' and result.decision.rule_coverage=='partial'
    assert result.decision.violated_conditions==('not_completed:course-1',)
    assert 'rule_unresolved' in result.decision.unknown_conditions
    assert result.decision.prerequisite_rule_state=='resolved' and result.rule_spans


def test_passed_conjunct_with_unresolved_sibling_stays_unknown():
    result=runtime(partial_ledger('all_of')).check(request(),facts(passed=('course-1',)))
    assert result.decision.outcome=='unknown' and not result.decision.violated_conditions
    assert result.decision.prerequisite_rule_state=='unresolved_reference'


@pytest.mark.parametrize('passed,failed,outcome',[(('course-1',),(),'eligible'),((),('course-1',),'unknown')])
def test_alternative_with_unresolved_sibling_needs_a_satisfied_known_alternative(passed,failed,outcome):
    result=runtime(partial_ledger('any_of')).check(request(),facts(passed=passed,failed=failed))
    assert result.decision.outcome==outcome and not result.decision.violated_conditions


def test_source_provenance_counts_toward_the_result_byte_limit():
    data=fixture()
    data[2][1]['prerequisites']['source_spans'][0]['text']='Fictional source rule '+('x'*70_000)
    result=runtime(rereview(data)).check(request(),facts(passed=('course-1',)))
    assert result.decision.outcome=='error' and result.decision.error_code=='runtime_result_limit'


def test_unsupported_request_cannot_bypass_input_and_response_limits(monkeypatch):
    req=PredicateRequest.parse({'predicate':'other','inputs':[
        {'name':'field_'+str(i),'value':'data','fact_ref':None} for i in range(500)]})
    monkeypatch.setattr(api(),'_invoke_worker',lambda *a:pytest.fail('must not execute'))
    with pytest.raises(ValueError,match='request.*limit'): runtime().check(req)


@pytest.mark.parametrize('predicate',['check_prerequisite_eligibility','other'])
def test_large_fact_reference_rejects_before_it_can_be_echoed(predicate,monkeypatch):
    data=request(predicate=predicate).model_dump(mode='json')
    data['inputs'][0]['fact_ref']='fact-'+('a'*70_000)
    req=PredicateRequest.parse(data)
    monkeypatch.setattr(api(),'_invoke_worker',lambda *a:pytest.fail('must not execute'))
    with pytest.raises(ValueError,match='request.*limit'): runtime().check(req)
