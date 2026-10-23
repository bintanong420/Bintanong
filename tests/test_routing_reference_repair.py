"""Reference errors get a specific repair; persistent ones become a clarification, not an outage."""
import asyncio
import json

from backend.bintanong_routing.contracts import RequestContext
from routing_wire_fixtures import wire_fixture
from test_routing_contracts import context, proposal
from test_routing_router import FakeTransport, run

TEXT = 'A1 policy'


def wire(valid=True):
    value = wire_fixture(proposal(text=TEXT), TEXT)
    if not valid:  # operation aimed at a phrase listed as a non-course mention
        value['mentions'].append(dict(kind='program', quote=dict(text='policy', occurrence=0)))
        value['operations'][0]['target'] = dict(text='policy', occurrence=0)
    return json.dumps(value)


def test_reference_error_repair_names_the_problem_and_allows_reinterpretation():
    model = FakeTransport(wire(valid=False), wire())
    result = run(model, text=TEXT)
    assert result.diagnostic == 'validated'
    repair = model.calls[1][0][-1]['content']
    assert 'invalid_course_quote_reference' in repair and 'course' in repair
    assert 'Correct formatting only' not in repair


def test_persistent_reference_errors_are_reported_as_invalid_reference():
    result = run(FakeTransport(wire(valid=False), wire(valid=False)), text=TEXT)
    assert result.diagnostic == 'invalid_reference' and result.attempts == 2


def test_format_errors_keep_the_existing_diagnostic():
    assert run(FakeTransport('bad', 'still bad'), text=TEXT).diagnostic == 'invalid_model_output'


def test_orchestrator_turns_persistent_reference_errors_into_a_clarification():
    from backend.bintanong_orchestration.orchestrator import Orchestrator
    from test_orchestration_pipeline import ports, resources, ctx
    release = resources()
    result = asyncio.run(Orchestrator(FakeTransport(wire(valid=False), wire(valid=False)),
        releases=ports().SyntheticReleaseProvider(release)).run(TEXT, ctx()))
    assert result.status == 'clarify' and not release.symbolic.calls
