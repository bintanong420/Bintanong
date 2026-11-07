"""Owner, 24 Oct 2026 (step 2e): a message whose parts choose different document topics (live: "INC meaning + until
when can I complete it", grading_scale + grade_completion) retrieved only the first topic, so the answer was a
referral. Every chosen topic is retrieved; the message is answered only when every topic has evidence.
Synthetic fixtures only."""
import asyncio
import json
import pytest

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


def test_shifting_follow_up_retrieval_keeps_the_resolved_topic_and_companion():
    from dataclasses import replace
    from backend.bintanong_routing.contracts import ConversationContext, DocumentTopic
    from test_routing_router import FakeTransport, style_proposal
    text = 'How many units transfer?'
    menu = tuple(DocumentTopic(subject_id=s, claims=(c,)) for s,c in (
        ('handbook_shifting', 'printed shifting fields'),
        ('handbook_drop_shift_faq', 'printed FAQ 8 shifting steps')))
    value = proposal(text=text, route='RAG', mentions=[], operations=[], language='en', parts=[
        dict(part_id='r1', text=text, start=0, end=len(text), evidence_need='document', operation_indices=[],
             subject_id=menu[0].subject_id, requested_claims=list(menu[0].claims))])
    docs = PerTopicDocuments()
    base = replace(resources(doc=docs), topics=menu)
    ctx = RequestContext.parse(context(conversation=ConversationContext(subject_id=menu[0].subject_id).model_dump(mode='json')))
    model_ = FakeTransport(json.dumps(value), style_outputs=[json.dumps(style_proposal('en', english=['How']))])
    asyncio.run(Orchestrator(model_, releases=ports().SyntheticReleaseProvider(base)).run(text, ctx))
    assert {i['subject_id'] for i in docs.intents} == {t.subject_id for t in menu}
    assert all('shifting' in r.query.casefold() and text in r.query for r in docs.calls)


def test_a_single_topic_keeps_the_whole_message_as_its_query():
    docs = PerTopicDocuments()
    value = json.loads(two_topics())
    value['parts'] = value['parts'][:1]  # one topic; its words differ from the whole message
    run(model(json.dumps(value)), docs)
    assert [r.query for r in docs.calls] == [TEXT]


def test_a_topic_without_evidence_preserves_the_independent_supported_part():
    docs = PerTopicDocuments(fictional_fees=documents('insufficient_evidence', passages=[]))
    result = run(model(two_topics()), docs)
    assert result.status == 'ready'
    assert result.evidence.documents.status == 'partial'
    assert len(result.evidence.documents.passages) == 1
    outcomes = result.evidence.documents.topic_outcomes
    assert [(o.part_ids, o.subject_id, o.status) for o in outcomes] == [
        (('r1',), 'fictional_office', 'ok'), (('r2',), 'fictional_fees', 'insufficient_evidence')]


def test_all_missing_topics_remain_unavailable():
    absent = documents('insufficient_evidence', passages=[])
    result = run(model(two_topics()), PerTopicDocuments(fictional_office=absent, fictional_fees=absent))
    assert result.status == 'no_evidence'


def test_conflict_in_either_topic_still_holds_the_answer():
    result = run(model(two_topics()), PerTopicDocuments(fictional_fees=documents('conflicting_sources')))
    assert result.status == 'conflict'


def test_missing_topic_cannot_hide_a_different_release():
    other = documents('insufficient_evidence', release_id='release-other', passages=[])
    result = run(model(two_topics()), PerTopicDocuments(fictional_fees=other))
    assert result.status == 'release_mismatch'


def test_unknown_source_inside_unavailable_topic_is_still_a_hard_hold():
    raw = documents('insufficient_evidence').model_dump(mode='json')
    raw['passages'][0]['citations'][0]['byte_sha256'] = 'f' * 64
    unknown = type(documents()).parse(raw)
    result = run(model(two_topics()), PerTopicDocuments(fictional_fees=unknown))
    assert result.status == 'release_mismatch'


def test_companion_failure_cannot_leave_its_own_part_looking_supported():
    from backend.bintanong_orchestration.contracts import DocumentTopicOutcome
    first, second = documents(), documents('insufficient_evidence', passages=[])
    bound = []
    for subject, result in [('fictional_office', first), ('fictional_fees', second)]:
        observation = DocumentTopicOutcome(part_ids=('r1',), subject_id=subject, requested_claims=('detail',),
            release_id=result.release_id, status=result.status, passages=result.passages, gaps=result.gaps)
        bound.append(result.model_copy(update=dict(topic_outcomes=(observation,))))
    merged = merge_documents(bound)
    assert merged.status == 'insufficient_evidence'  # the only part depends on both topics


def test_a_partial_aggregate_cannot_forge_away_a_conflict():
    from backend.bintanong_orchestration.contracts import DocumentResult
    raw = run(model(two_topics()), PerTopicDocuments(
        fictional_fees=documents('insufficient_evidence', passages=[]))).evidence.documents.model_dump(mode='json')
    raw['topic_outcomes'][1]['status'] = 'conflicting_sources'
    with pytest.raises(ValueError, match='partial_documents_cannot_bypass_hard_hold'):
        DocumentResult.parse(raw)


def test_a_partial_aggregate_cannot_be_relabelled_ok():
    from backend.bintanong_orchestration.contracts import DocumentResult
    raw = run(model(two_topics()), PerTopicDocuments(
        fictional_fees=documents('insufficient_evidence', passages=[]))).evidence.documents.model_dump(mode='json')
    raw['status'] = 'ok'
    with pytest.raises(ValueError, match='ok_documents_require_successful_topics'):
        DocumentResult.parse(raw)


def test_duplicate_chunk_with_different_body_is_rejected():
    with pytest.raises(ValueError, match='incompatible_document_chunk'):
        merge_documents((documents(), documents(passages=[dict(
            documents().passages[0].model_dump(mode='json'), text='Contradictory body under same ID.')])) )


def test_merged_results_keep_every_distinct_passage_and_gap_in_order():
    first = documents()
    second = documents(gaps=['source_gap'], passages=[dict(first.passages[0].model_dump(mode='json'),
                                                         chunk_id='0' * 63 + '2', text='Other policy.')])
    merged = merge_documents((first, second, first))
    assert [p.text for p in merged.passages] == ['Fictional policy.', 'Other policy.']
    assert merged.status == 'ok' and merged.gaps == ('source_gap',)
