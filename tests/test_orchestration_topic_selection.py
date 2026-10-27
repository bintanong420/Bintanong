"""The opt-in topic selector is reachable through the orchestrator; the default stays unchanged."""
import asyncio

import pytest

from backend.bintanong_orchestration.orchestrator import Orchestrator
from backend.bintanong_routing.contracts import RequestContext
from test_orchestration_document_topics import TopicDocuments
from test_orchestration_pipeline import ports, resources
from test_routing_contracts import context
from test_routing_topic_selection import MENU, TEXT, Transport, answer, selected

SELECTOR = 'bintanong-topic-selection-v1'


def run(model, docs, **options):
    base = resources(doc=docs)
    provider = ports().SyntheticReleaseProvider(ports().ReleaseResources(pin=base.pin, catalog=base.catalog,
        registry=base.registry, retrieval=base.retrieval, symbolic=base.symbolic, topics=MENU,
        document_scope=('audience:undergraduate',)))
    return asyncio.run(Orchestrator(model, releases=provider, **options).run(TEXT, RequestContext.parse(context())))


def schemas(model):
    return [schema['properties'].get('schema_version', {}).get('const') for _, schema in model.calls]


def test_enabled_selection_narrows_a_large_menu_before_routing_and_retrieval():
    docs, model = TopicDocuments(), Transport(selected(), answer())
    run(model, docs, topic_selection=True)
    assert schemas(model)[0] == SELECTOR
    routed = model.calls[1][0][0]['content']
    assert 'fictional_office' in routed and 'other_7' not in routed
    assert docs.intents == [dict(subject_id='fictional_office', requested_claims=('filing office',))]


def test_default_keeps_the_full_menu_without_a_selection_call():
    docs, model = TopicDocuments(), Transport(selected(), answer())
    run(model, docs)
    assert SELECTOR not in schemas(model)
    assert 'other_7' in model.calls[0][0][0]['content']


@pytest.mark.parametrize('value', [None, 1, 'yes'])
def test_non_boolean_topic_selection_is_rejected(value):
    with pytest.raises(ValueError, match='invalid_topic_selection'):
        Orchestrator(Transport(selected()), topic_selection=value)
