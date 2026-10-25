"""Reference errors get a specific repair; persistent ones become a clarification, not an outage."""
import asyncio
import json
from copy import deepcopy

import pytest

from backend.bintanong_routing.contracts import RequestContext
from routing_wire_fixtures import wire_fixture
from test_routing_contracts import context, proposal
from test_routing_router import FakeTransport, run
from test_routing_validation import entry

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


def test_persistent_count_errors_keep_the_existing_format_failure_and_retry_limit():
    value = json.loads(wire())
    value['part_count'] = len(value['parts']) + 1
    result = run(FakeTransport(json.dumps(value), json.dumps(value)), text=TEXT)
    assert result.diagnostic == 'invalid_model_output' and result.attempts == 2


@pytest.mark.parametrize('count_mismatch', [False, True])
def test_grade_only_part_gets_targeted_repair_and_preserves_the_supplied_claim(count_mismatch):
    text = 'Can I take A1? I failed B2.'
    quote = lambda text: dict(text=text, occurrence=0)
    bad = dict(schema_version='bintanong-interpretation-wire-v4', language='en',
        audience='undergraduate', control=None, part_count=2, intent='prerequisite check',
        mentions=[dict(kind='course', quote=quote(code)) for code in ('A1', 'B2')],
        claims=[dict(quote=quote('I failed B2.'), entity=quote('B2'), state='failed', mode='asserted')],
        operations=[dict(name=name, target=quote('A1')) for name in
                    ('check_prerequisite_eligibility', 'list_missing_prerequisites')],
        parts=[dict(part_id='r1', quote=quote('Can I take A1?'), evidence_need='structured', operation_indices=[0]),
               dict(part_id='r2', quote=quote('I failed B2.'), evidence_need='structured', operation_indices=[1])],
        route='Symbolic', ambiguities=[])
    if count_mismatch:
        bad['part_count'] = 1
    corrected = deepcopy(bad)
    corrected.update(part_count=1, parts=bad['parts'][:1], operations=bad['operations'][:1])
    model = FakeTransport(json.dumps(bad), json.dumps(corrected))
    result = run(model, text=text, catalog=(entry(), entry(entity='course-b', alias='B2')))
    assert result.diagnostic == 'validated' and result.decision.route == 'Symbolic'
    assert [(c.course_id, c.state) for c in result.claims] == [('course-b', 'failed')]
    repair = model.calls[1][0][-1]['content']
    assert ('part_count_mismatch' if count_mismatch else 'uncontained_part_target') in repair
    assert 'supporting claims' in repair and 'genuine questions' in repair


def test_orchestrator_turns_persistent_reference_errors_into_a_clarification():
    from backend.bintanong_orchestration.orchestrator import Orchestrator
    from test_orchestration_pipeline import ports, resources, ctx
    release = resources()
    result = asyncio.run(Orchestrator(FakeTransport(wire(valid=False), wire(valid=False)),
        releases=ports().SyntheticReleaseProvider(release)).run(TEXT, ctx()))
    assert result.status == 'clarify' and not release.symbolic.calls
