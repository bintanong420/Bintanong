"""Owner, 24 Oct 2026 (step 2d): a structured fact Bintanong has no operation for (live: "How many units is CC 5?")
was shown as "temporarily unavailable, try again later". It is unavailable information instead: the E1 reply
("not in the reviewed sources yet, ask the university office"). Synthetic fixtures only."""
import asyncio
import json

from test_orchestration_pipeline import api, ports, resources, ctx
from test_routing_contracts import proposal
from test_routing_router import FakeTransport

TEXT = 'A1'


def lookup_without_operation():
    return proposal(text=TEXT, operations=[], claims=[])  # one structured part, no operation to run


def test_a_structured_lookup_without_an_operation_is_unavailable_information():
    async def scenario():
        provider = ports().SyntheticReleaseProvider(resources())
        return await api().Orchestrator(FakeTransport(json.dumps(lookup_without_operation())),
                                        releases=provider).run(TEXT, ctx())
    result = asyncio.run(scenario())
    assert result.status == 'no_evidence' and result.evidence is None
