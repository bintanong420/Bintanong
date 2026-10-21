"""Release topic menus reach the router, and chosen topics/facts reach retrieval."""
import asyncio

from backend.bintanong_orchestration.orchestrator import Orchestrator
from backend.bintanong_routing.contracts import RequestContext
from test_orchestration_pipeline import Documents, ports, resources
from test_routing_contracts import context
from test_routing_document_topics import MENU, TEXT, answer, model as FakeTransport


class TopicDocuments(Documents):
    def __init__(self):
        super().__init__()
        self.intents = []

    async def retrieve(self, request, **intent):
        self.intents.append(intent)
        return await super().retrieve(request)


def run(model, docs, **release):
    base = resources(doc=docs)
    data = dict(pin=base.pin, catalog=base.catalog, registry=base.registry,
                retrieval=base.retrieval, symbolic=base.symbolic) | release
    provider = ports().SyntheticReleaseProvider(ports().ReleaseResources(**data))
    return asyncio.run(Orchestrator(model, releases=provider).run(TEXT, RequestContext.parse(context())))


def test_menu_reaches_router_and_chosen_topic_reaches_retrieval():
    docs, model = TopicDocuments(), FakeTransport(answer())
    run(model, docs, topics=MENU, document_scope=('audience:undergraduate',))
    assert 'fictional_office' in model.calls[0][0][0]['content']
    assert docs.intents == [dict(subject_id='fictional_office', requested_claims=('filing office',))]
    assert 'audience:undergraduate' in docs.calls[0].scope


def test_no_menu_keeps_the_existing_retrieval_call():
    docs = TopicDocuments()
    plain = answer()
    import json
    value = json.loads(plain)
    for part in value['parts']:
        part.pop('subject_id'); part.pop('requested_claims')
    run(FakeTransport(json.dumps(value)), docs)
    assert docs.intents == [{}] and 'audience:undergraduate' not in docs.calls[0].scope


class RecordingEngine:
    def __init__(self):
        self.calls = []

    def retrieve(self, request, **intent):
        self.calls.append(intent)
        return dict(schema_version='bintanong-retrieval-debug-v1', release_id=request.release_id,
                    status='insufficient_evidence', gaps=[], evidence=[])


def test_retrieval_adapter_forwards_topic_intent_only_when_supplied():
    from backend.bintanong_orchestration.adapters import RetrievalAdapter
    from backend.bintanong_retrieval.types import RetrievalRequest
    engine = RecordingEngine()
    adapter = RetrievalAdapter(engine)
    request = RetrievalRequest('Fictional question?', 'release-synth-1')
    asyncio.run(adapter.retrieve(request))
    asyncio.run(adapter.retrieve(request, subject_id='fictional_office', requested_claims=('filing office',)))
    assert engine.calls == [{}, dict(subject_id='fictional_office', requested_claims=('filing office',))]


class StatusEngine:
    def __init__(self, status, assessment):
        self.status, self.assessment = status, assessment

    def retrieve(self, request, **intent):
        policy = dict(assessment=None if self.assessment is None else dict(status=self.assessment))
        return dict(schema_version='bintanong-retrieval-debug-v1', release_id=request.release_id,
                    status=self.status, gaps=[], evidence=[], evidence_policy=policy)


def _status(engine, **options):
    from backend.bintanong_orchestration.adapters import RetrievalAdapter
    from backend.bintanong_retrieval.types import RetrievalRequest
    request = RetrievalRequest('Fictional question?', 'release-synth-1')
    return asyncio.run(RetrievalAdapter(engine, **options).retrieve(request)).status


def test_research_mode_answers_only_reviewed_fields_available():
    assert _status(StatusEngine('uncalibrated', 'reviewed_fields_available'), research=True) == 'ok'


def test_research_mode_keeps_every_other_result_withheld():
    assert _status(StatusEngine('uncalibrated', 'insufficient_context'), research=True) == 'uncalibrated'
    assert _status(StatusEngine('uncalibrated', None), research=True) == 'uncalibrated'
    assert _status(StatusEngine('insufficient_evidence', 'insufficient_evidence'), research=True) == 'insufficient_evidence'


def test_default_mode_never_upgrades_uncalibrated():
    assert _status(StatusEngine('uncalibrated', 'reviewed_fields_available')) == 'uncalibrated'
