"""Research is a release property: research pins accept only matching research results."""
import pytest

from backend.bintanong_orchestration.contracts import ReleasePin
from backend.bintanong_orchestration.integration import assemble
from backend.bintanong_symbolic.bundle import prepare_runtime_bundle
from test_orchestration_integration import pin as synthetic_pin
from test_symbolic_offline_research import real_fixture, research
from test_symbolic_runtime import facts, request

REF = 'research-fictional-test'


def research_case(ref=REF):
    bundle = prepare_runtime_bundle(real_fixture())
    runtime = research(bundle)
    pin = ReleasePin.parse(dict(release_id=runtime.release_id, synthetic=False, research_ref=ref,
        rule_bundle_version=runtime.rule_bundle_version,
        sources=[dict(version_id=s['version_id'], byte_sha256=s['byte_sha256'])
                 for s in bundle['ledger']['sources']]))
    return pin, runtime.check(request(), facts(failed=('course-1',)))


def test_research_pin_assembles_a_labelled_research_result():
    pin, result = research_case()
    evidence = assemble(pin, 'Symbolic', symbolic=result)
    assert evidence.status == 'ready' and evidence.symbolic.research.authorization.authorization_ref == REF
    assert evidence.symbolic.decision.outcome == 'ineligible' and evidence.symbolic.decision.synthetic is False


def test_synthetic_pin_still_rejects_research_results():
    _, result = research_case()
    with pytest.raises(ValueError):
        assemble(synthetic_pin(), 'Symbolic', symbolic=result)


def test_research_pin_rejects_results_from_another_authorization():
    pin, _ = research_case()
    _, other = research_case()
    other_pin = pin.model_copy(update=dict(research_ref='research-other'))
    with pytest.raises(ValueError):
        assemble(ReleasePin.parse(other_pin.model_dump(mode='json')), 'Symbolic', symbolic=other)


@pytest.mark.parametrize('synthetic,ref', [(False, None), (True, REF)])
def test_pin_research_reference_matches_its_mode(synthetic, ref):
    data = synthetic_pin().model_dump(mode='json') | dict(synthetic=synthetic, research_ref=ref)
    with pytest.raises(ValueError):
        ReleasePin.parse(data)


def test_orchestrator_carries_a_research_result_end_to_end():
    import asyncio, json
    from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry
    from backend.bintanong_orchestration.adapters import SymbolicAdapter
    from backend.bintanong_orchestration.orchestrator import Orchestrator
    from backend.bintanong_orchestration.ports import ReleaseResources, SyntheticReleaseProvider
    from backend.bintanong_routing.contracts import RequestContext
    from backend.bintanong_symbolic.runtime import ResearchSymbolicResult
    from test_routing_contracts import context, proposal
    from test_routing_router import FakeTransport
    from test_routing_validation import entry
    bundle = prepare_runtime_bundle(real_fixture())
    runtime = research(bundle)
    pin, _ = research_case()
    course = entry(entity='course-2', alias='A1', curriculum='curriculum-synthetic-1').model_copy(
        update=dict(source_ref=pin.sources[0].version_id))
    registry = CapabilityRegistry({'check_prerequisite_eligibility': Capability(
        'offline_research_prerequisite_check', ('curriculum_id', 'course_id'))})
    resources = ReleaseResources(pin, (course,), registry, None, SymbolicAdapter(runtime, research=True))
    ctx = RequestContext.parse(context(curriculum_id='curriculum-synthetic-1'))
    integration = asyncio.run(Orchestrator(FakeTransport(json.dumps(proposal())),
        releases=SyntheticReleaseProvider(resources)).run('A1', ctx))
    assert type(integration.evidence.symbolic) is ResearchSymbolicResult
    assert integration.evidence.symbolic.research.authorization.authorization_ref == REF
