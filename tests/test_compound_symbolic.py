"""Synthetic FM-05 component tests; no claim of live student or PDF correctness."""
import asyncio

import pytest

from backend.bintanong_routing.contracts import Interpretation, RequestContext
from backend.bintanong_routing.validation import validate_interpretation
from backend.bintanong_orchestration.compound import (
    CompoundNotSupported, CompoundResearchResult,
    execute_two_eligibility_checks, plan_two_eligibility_checks,
)
from test_routing_contracts import context, proposal
from test_orchestration_pipeline import resources, Symbolic

QUESTION = 'Can I take A1? Can I take B1?'


def compound_data():
    start = QUESTION.index('Can I take B1?')
    return proposal(text=QUESTION, mentions=[
        dict(kind='course', text='A1', start=11, end=13),
        dict(kind='course', text='B1', start=start+11, end=start+13)],
        operations=[dict(name='check_prerequisite_eligibility', target=0),
                    dict(name='check_prerequisite_eligibility', target=1)],
        parts=[dict(part_id='r1', text=QUESTION[:14], start=0, end=14,
                    evidence_need='structured', operation_indices=[0]),
               dict(part_id='r2', text=QUESTION[start:], start=start, end=len(QUESTION),
                    evidence_need='structured', operation_indices=[1])])


def plan(value=None, *, ctx=None, release=None):
    release = resources() if release is None else release
    original = RequestContext.parse(context() if ctx is None else ctx)
    routed = validate_interpretation(QUESTION, original,
        Interpretation.parse(compound_data() if value is None else value),
        catalog=release.catalog, registry=release.registry, documents_available=True, synthetic=True)
    assert not routed.decision.dispatchable and routed.diagnostic == 'compound_request'
    return plan_two_eligibility_checks(QUESTION, original, routed, release), release


def test_two_named_checks_bind_to_independent_parts_and_targets():
    checked, release = plan()
    assert [p.part_id for p in checked.checks] == ['r1', 'r2']
    assert [next(i.value for i in p.predicate_request.inputs if i.name == 'course_id')
            for p in checked.checks] == ['course-a', 'course-b']
    assert checked.curriculum_id == 'curriculum-a'
    assert checked.release_id == release.pin.release_id


def test_two_results_preserve_separate_pinned_candidate_evidence():
    fact = dict(fact_id='fact-a', session_id='sess-a', program_id='program-a',
                curriculum_id='curriculum-a', course_id='course-pre', state='passed')
    checked, release = plan(ctx=context(facts=[fact]))
    result = asyncio.run(execute_two_eligibility_checks(checked, release))
    assert result.status == 'complete'
    assert [p.status for p in result.parts] == ['ready', 'ready']
    assert [p.evidence.symbolic.decision.outcome for p in result.parts] == ['eligible', 'eligible']
    assert len(release.symbolic.calls) == 2
    assert result.candidate_only and not result.institutional_use_allowed and not result.activation_allowed
    assert CompoundResearchResult.parse(result.model_dump(mode='json')) == result


def test_taken_unknown_does_not_become_passed():
    fact = dict(fact_id='fact-a', session_id='sess-a', program_id='program-a',
                curriculum_id='curriculum-a', course_id='course-pre', state='taken_unknown')
    checked, release = plan(ctx=context(facts=[fact]))
    result = asyncio.run(execute_two_eligibility_checks(checked, release))
    assert result.status == 'withheld'
    assert [p.status for p in result.parts] == ['unknown', 'unknown']


def test_first_worker_error_does_not_drop_second_or_invent_success():
    class BrokenFirst(Symbolic):
        async def execute(self, request, ctx):
            if any(i.name == 'course_id' and i.value == 'course-a' for i in request.inputs):
                self.calls.append((request, ctx))
                raise RuntimeError('PRIVATE grade value')
            return await super().execute(request, ctx)
    fact = dict(fact_id='fact-a', session_id='sess-a', program_id='program-a',
                curriculum_id='curriculum-a', course_id='course-pre', state='passed')
    release = resources(sym=BrokenFirst())
    checked, _ = plan(ctx=context(facts=[fact]), release=release)
    result = asyncio.run(execute_two_eligibility_checks(checked, release))
    assert result.status == 'partial'
    assert [p.status for p in result.parts] == ['tool_error', 'ready']
    assert result.parts[0].evidence is None and len(release.symbolic.calls) == 2
    assert 'PRIVATE grade value' not in repr(result)


def test_hybrid_with_unmatched_document_part_is_not_truncated():
    value = compound_data()
    value['route'] = 'Hybrid'
    value['parts'].append(dict(part_id='r3', text=QUESTION, start=0, end=len(QUESTION),
                               evidence_need='document', operation_indices=[]))
    with pytest.raises(CompoundNotSupported, match='compound_shape_not_supported'):
        plan(value)


def test_arbitrary_prolog_operation_remains_blocked():
    value = compound_data()
    value['operations'][1]['name'] = 'arbitrary_prolog'
    with pytest.raises(CompoundNotSupported, match='compound_shape_not_supported'):
        plan(value)


def test_missing_curriculum_remains_held():
    with pytest.raises(CompoundNotSupported, match='subcheck_failed_validation'):
        plan(ctx=context(program_id=None, curriculum_id=None))


def test_result_cannot_claim_institutional_authorization():
    checked, release = plan()
    result = asyncio.run(execute_two_eligibility_checks(checked, release))
    bad = result.model_dump(mode='json')
    bad['institutional_use_allowed'] = True
    with pytest.raises(ValueError):
        CompoundResearchResult.parse(bad)


def test_developer_entrypoint_routes_once_and_keeps_two_checked_results():
    import json
    from test_routing_router import FakeTransport
    from test_orchestration_pipeline import ports
    from backend.bintanong_orchestration.compound import run_bounded_compound
    fact = dict(fact_id='fact-a', session_id='sess-a', program_id='program-a',
                curriculum_id='curriculum-a', course_id='course-pre', state='passed')
    release = resources()
    model = FakeTransport(json.dumps(compound_data()))
    result = asyncio.run(run_bounded_compound(QUESTION, RequestContext.parse(context(facts=[fact])),
        model, ports().SyntheticReleaseProvider(release)))
    assert result.status == 'complete'
    assert [item.status for item in result.parts] == ['ready', 'ready']
    assert len(release.symbolic.calls) == 2
    assert len(model.calls) == 2
