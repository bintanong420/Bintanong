"""Owner, 24 Oct 2026 (step 2e): a message whose parts choose different document topics (live: "INC meaning + until
when can I complete it", grading_scale + grade_completion) retrieved only the first topic, so the answer was a
referral. Every chosen topic is retrieved; the message is answered only when every topic has evidence.
Synthetic fixtures only."""
import asyncio
import json

from backend.bintanong_orchestration.orchestrator import Orchestrator, merge_documents
from backend.bintanong_routing.contracts import RequestContext
from test_orchestration_document_topics import TopicDocuments
from test_orchestration_pipeline import ports, resources
from test_orchestration_integration import documents
from test_routing_contracts import context, proposal
from test_routing_document_topics import MENU, model

TEXT = 'Where do I file slip S? What is the fee?'
OFFICE = dict(subject_id='fictional_office', requested_claims=('filing office',))
FEES = dict(subject_id='fictional_fees', requested_claims=('printed fee amount',))


def two_topics():
    value = proposal(text=TEXT, route='RAG', mentions=[], operations=[], intent='Filing and fee', language='en',
        parts=[dict(part_id='r1', text='Where do I file slip S?', start=0, end=23, evidence_need='document',
                    operation_indices=[], subject_id='fictional_office', requested_claims=['filing office']),
               dict(part_id='r2', text='What is the fee?', start=24, end=40, evidence_need='document',
                    operation_indices=[], subject_id='fictional_fees', requested_claims=['printed fee amount'])])
    return json.dumps(value)


def run(transport, docs):
    base = resources(doc=docs)
    provider = ports().SyntheticReleaseProvider(ports().ReleaseResources(pin=base.pin, catalog=base.catalog,
        registry=base.registry, retrieval=base.retrieval, symbolic=base.symbolic, topics=MENU))
    return asyncio.run(Orchestrator(transport, releases=provider).run(TEXT, RequestContext.parse(context())))


class PerTopicDocuments(TopicDocuments):
    def __init__(self, **by_subject):
        super().__init__()
        self.by_subject = by_subject

    async def retrieve(self, request, **intent):
        self.intents.append(intent)
        self.calls.append(request)
        return self.by_subject.get(intent.get('subject_id'), self.result)


def test_every_chosen_topic_is_retrieved_in_part_order():
    docs = PerTopicDocuments()
    result = run(model(two_topics()), docs)
    assert docs.intents == [OFFICE, FEES]
    assert result.status == 'ready' and len(result.evidence.documents.passages) == 1  # same chunk kept once


def test_each_topic_is_retrieved_with_its_own_part_text():
    # Live: the whole two-topic message as the query found nothing for the special-class fee topic.
    docs = PerTopicDocuments()
    run(model(two_topics()), docs)
    assert [r.query for r in docs.calls] == ['Where do I file slip S?', 'What is the fee?']


def test_a_single_topic_keeps_the_whole_message_as_its_query():
    docs = PerTopicDocuments()
    value = json.loads(two_topics())
    value['parts'] = value['parts'][:1]  # one topic; its words differ from the whole message
    run(model(json.dumps(value)), docs)
    assert [r.query for r in docs.calls] == [TEXT]


def test_a_topic_without_evidence_leaves_the_whole_message_unanswered():
    docs = PerTopicDocuments(fictional_fees=documents('insufficient_evidence', passages=[]))
    result = run(model(two_topics()), docs)
    assert result.status == 'no_evidence'


def test_merged_results_keep_every_distinct_passage_and_gap_in_order():
    first = documents()
    second = documents(gaps=['source_gap'], passages=[dict(first.passages[0].model_dump(mode='json'),
                                                         chunk_id='0' * 63 + '2', text='Other policy.')])
    merged = merge_documents((first, second, first))
    assert [p.text for p in merged.passages] == ['Fictional policy.', 'Other policy.']
    assert merged.status == 'ok' and merged.gaps == ('source_gap',)
