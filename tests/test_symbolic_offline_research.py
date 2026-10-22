"""Fictional records exercise the explicit real-input research path, not PalSU policy."""
import copy
from concurrent.futures import ThreadPoolExecutor

import pytest

from backend.bintanong_contracts.symbolic import EMPTY_REGISTRY, as_policy_result
from backend.bintanong_symbolic.bundle import prepare_runtime_bundle
from test_symbolic_runtime import api, facts, fixture, request, rereview, run

OPERATIONS=('check_prerequisite_eligibility','list_missing_prerequisites','list_affected_courses')


def real_fixture():
    data=fixture(); source=data[1][0].model_dump(mode='json'); source['synthetic']=False
    return run((data[0],[source],data[2],data[3]))


def authorization(bundle,operations=OPERATIONS):
    return {'purpose':'offline_curriculum_acceptance','authorization_ref':'research-fictional-test',
            'bundle_sha256':bundle['content_sha256'],'operations':list(operations)}


def research(bundle=None,operations=OPERATIONS,**kw):
    bundle=prepare_runtime_bundle(real_fixture()) if bundle is None else bundle
    return api().CurriculumRuntime.for_offline_research(bundle,
        authorization=authorization(bundle,operations),**kw)


@pytest.mark.parametrize('passed,failed,outcome',[(('course-1',),(),'eligible'),
    ((),('course-1',),'ineligible'),((),(),'unknown'),(('course-1',),('course-1',),'unknown')])
def test_explicit_research_executes_real_input_with_fictional_facts_and_truthful_labels(passed,failed,outcome):
    bundle=prepare_runtime_bundle(real_fixture()); before=copy.deepcopy(bundle)
    runner=research(bundle)
    result=runner.check(request(),facts(passed=passed,failed=failed))
    assert result.decision.outcome==outcome and result.decision.synthetic is False
    assert result.research.mode=='offline_research'
    assert result.research.institutional_use_allowed is False
    assert result.research.student_facts_synthetic is True
    assert result.research.generated_output_review=='pending'
    assert result.research.authorization.bundle_sha256==bundle['content_sha256']
    assert result.research.release_holds==tuple(bundle['release_holds'])
    assert result.scope.knowledge_release_id.startswith('release-offline-research-')
    assert bundle==before and not EMPTY_REGISTRY.supports(request().predicate)
    assert result==runner.check(request(),facts(passed=passed,failed=failed))
    with pytest.raises(ValueError,match='research'): as_policy_result(result)


def test_research_operation_allowlist_is_exact_and_never_executes_unsupported(monkeypatch):
    runner=research(operations=('list_missing_prerequisites',))
    result=runner.check(request(predicate='list_missing_prerequisites'),facts(failed=('course-1',)))
    assert result.decision.outcome=='ineligible' and result.capability.startswith('offline_research_')
    monkeypatch.setattr(api(),'_invoke_worker',lambda *a:pytest.fail('must not execute'))
    assert runner.check(request()).decision.outcome=='unsupported'
    dep=runner.list_affected_courses(request('course-1',predicate='list_affected_courses'))
    assert dep.status=='unsupported' and dep.research.mode=='offline_research'


def test_research_dependencies_remain_potential_and_keep_sources():
    dep=research().list_affected_courses(request('course-1',predicate='list_affected_courses'))
    assert dep.synthetic is False and dep.course_ids==('course-2',)
    assert dep.rule_spans and dep.scope and dep.research.institutional_use_allowed is False


def test_answer_pipeline_rejects_research_object_before_base_type_erases_its_labels():
    from backend.bintanong_contracts.answer import EvidenceBundle
    from backend.bintanong_contracts.governance import SessionFact, SourceDocumentVersion
    from backend.bintanong_contracts.runtime import PredicateRequest
    from test_contracts_answer import fact
    req=request().model_dump(mode='json')
    for item in req['inputs']: item['fact_ref']='fact-synth-0001'
    result=research().check(PredicateRequest.parse(req),facts(passed=('course-1',)))
    with pytest.raises(ValueError,match='research'):
        EvidenceBundle(schema_version=EvidenceBundle.SCHEMA_VERSION,request_id='req-research-test',
            route='Symbolic',knowledge_release_id=result.scope.knowledge_release_id,retrieval=None,
            versions=tuple(SourceDocumentVersion.parse(s) for s in real_fixture()['sources']),
            symbolic=result,session_facts=(SessionFact.parse(fact()),),conflicts=(),
            permitted_claims=('decision_eligible',))


@pytest.mark.parametrize('update',[{'bundle_sha256':'0'*64},{'purpose':'institutional_use'},
    {'operations':[]},{'operations':['other']},{'operations':['list_affected_courses']*2},
    {'approval_id':'invented'},{'authorization_ref':''}])
def test_wrong_or_expanded_authorization_rejected_before_worker(update,monkeypatch):
    bundle=prepare_runtime_bundle(real_fixture()); auth=authorization(bundle);auth.update(update)
    monkeypatch.setattr(api(),'_invoke_worker',lambda *a:pytest.fail('must not execute'))
    with pytest.raises(ValueError):
        api().CurriculumRuntime.for_offline_research(bundle,authorization=auth)


def test_standard_constructor_stays_closed_and_facts_cannot_be_real_student_data():
    bundle=prepare_runtime_bundle(real_fixture())
    with pytest.raises(ValueError): api().CurriculumRuntime(bundle['ledger'])
    with pytest.raises(ValueError): api().CurriculumRuntime.from_bundle(bundle)
    with pytest.raises(ValueError): api().StudentFacts.parse({'synthetic':False,'passed':['course-1']})
    with pytest.raises(TypeError): api().CurriculumRuntime.for_offline_research(bundle)


def test_worker_rechecks_research_payload_and_context(monkeypatch):
    original=api()._invoke_worker; captured=[]
    def invoke(payload,timeout):
        captured.append(copy.deepcopy(payload)); return original(payload,timeout)
    monkeypatch.setattr(api(),'_invoke_worker',invoke)
    assert research().check(request(),facts(passed=('course-1',))).decision.outcome=='eligible'
    for field in ('research','bundle','operation'):
        changed=copy.deepcopy(captured[0])
        if field=='research': changed[field]=None
        elif field=='bundle': changed[field]['courses']=[]
        else: changed[field]='dependencies'
        with pytest.raises(RuntimeError): original(changed,5)


def test_large_research_context_rejects_before_it_can_break_response_bounds():
    from backend.bintanong_tools.document_ingest.register import mint_pending_register
    data=fixture(); source=data[1][0].model_dump(mode='json'); source['synthetic']=False
    extra=mint_pending_register([{'filename':f'fictional-{i}.pdf','sha256':f'{i:064x}',
                                 'acquisition_locator':f'shelf:fictional-{i}'} for i in range(1,100)],synthetic=False)
    bundle=prepare_runtime_bundle(run((data[0],[source,*extra],data[2],data[3])))
    with pytest.raises(ValueError,match='research.*limit'): research(bundle)


def test_research_unknown_scope_and_draft_rules_are_not_approved():
    runner=research()
    assert runner.check(request(curriculum='other')).decision.outcome=='unknown'
    data=fixture(); data[2][0]['review_state']='draft';data[2][0]['review_refs']=[]
    source=data[1][0].model_dump(mode='json');source['synthetic']=False
    bundle=prepare_runtime_bundle(run((data[0],[source],data[2],data[3])))
    result=research(bundle).check(request(),facts(passed=('course-1',)))
    assert result.decision.outcome=='unknown' and result.decision.rule_coverage=='partial'


def test_research_timeouts_and_concurrent_requests_preserve_isolation():
    runner=research(timeout_seconds=15)
    def check(passed):
        return runner.check(request(),facts(passed=('course-1',) if passed else ())).decision.outcome
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(check,[True,False,True,False]))==['eligible','unknown','eligible','unknown']
    result=research(timeout_seconds=.001).check(request())
    assert result.decision.outcome=='error' and result.decision.error_code=='runtime_timeout'
    assert check(True)=='eligible'
