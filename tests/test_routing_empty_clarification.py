"""Owner, 24 Oct 2026 (E3): the model sometimes chooses `clarify` without naming anything to clarify (live: "Pwede ba
mag-shift ng course? Paano po?"), and students saw "Please clarify the missing information" with nothing to answer.
Such a clarify is missing information instead: the office-referral reply of E1. Synthetic fixtures only."""
import asyncio
import json

from test_orchestration_pipeline import api, ports, resources, ctx
from test_private_context_conversation import previous
from test_routing_contracts import context, proposal
from test_routing_router import FakeTransport
from test_routing_validation import validate

TEXT = 'A1'  # the synthetic style fixture quotes A1


def empty_clarify(**updates):
    return proposal(text=TEXT, route=None, control='clarify', mentions=[], operations=[], claims=[], **updates)


def test_a_clarify_that_names_nothing_is_unavailable_information():
    result = validate(TEXT, empty_clarify())
    assert result.diagnostic == 'empty_clarification'
    assert result.decision.control == 'evidence_unavailable' and result.decision.route is None


def test_a_clarify_about_a_back_reference_still_asks_the_student():
    value = empty_clarify(context_reference=dict(text=TEXT, start=0, end=len(TEXT)))
    result = validate(TEXT, value, context(conversation=previous().model_dump(mode='json')))
    assert result.diagnostic == 'model_control' and result.decision.control == 'clarify'


def test_a_clarify_that_keeps_a_requested_check_still_asks_the_student():
    value = proposal(text=TEXT, route=None, control='clarify')  # one mention, one eligibility operation
    assert validate(TEXT, value).decision.control == 'clarify'


def test_the_orchestrator_reports_an_empty_clarification_as_no_evidence():
    async def scenario():
        provider = ports().SyntheticReleaseProvider(resources())
        return await api().Orchestrator(FakeTransport(json.dumps(empty_clarify())),
                                        releases=provider).run(TEXT, ctx())
    result = asyncio.run(scenario())
    assert result.status == 'no_evidence' and result.evidence is None
