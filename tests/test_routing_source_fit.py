"""Source selection stays semantic: policy, checklist and workflow choices remain distinct."""
import asyncio
import json

import pytest

from backend.bintanong_routing.contracts import DocumentTopic, RequestContext
from backend.bintanong_routing.router import Router
from test_routing_contracts import context, proposal
from test_routing_router import FakeTransport, style_proposal
from test_routing_validation import catalog, registry


def test_reviewed_step_structure_reaches_both_menus_without_source_priority():
    from backend.bintanong_routing import topic_selection
    from backend.bintanong_routing.prompt import build_messages
    topic = DocumentTopic(subject_id='fictional_service', claims=('checklist', 'first step', 'second step', 'time'),
        claim_fields={'checklist': ('requirements',), 'first step': ('step1_client_step', 'step1_agency_action'),
                      'second step': ('step2_client_step',), 'time': ('whole_service_total_time',)})
    selector = topic_selection.build_messages('How do I obtain slip S?', (topic,))[0]['content']
    menu = json.loads(selector.split('Menu:', 1)[1])
    assert menu[0]['workflow_fact_count'] == 2
    messages = build_messages('How do I obtain slip S?', RequestContext.parse(context()), (), registry(), (topic,))
    system = messages[0]['content']
    assert '"workflow_fact_indices":[1,2]' in system
    assert topic_selection.workflow_fact_indices(DocumentTopic(subject_id='fictional_policy',
        claims=('policy',), claim_fields={'policy': ('body',)})) == []


def test_non_numbered_procedure_fragments_are_visible_without_inventing_workflow_steps():
    from backend.bintanong_routing import topic_selection
    topic = DocumentTopic(subject_id='fictional_memo', claims=('initial payment',),
        claim_fields={'initial payment': ('application_payment_procedure',)},
        claim_context={'initial payment': {'application_payment_procedure': 'Fictional initial payment only.'}})
    menu = json.loads(topic_selection.build_messages('How do I get slip S?', (topic,))[0]['content'].split('Menu:', 1)[1])
    assert menu[0]['procedure_context'] == [dict(claim='initial payment',
        fields={'application_payment_procedure': 'Fictional initial payment only.'})]
    assert 'workflow_fact_count' not in menu[0]


def test_full_selector_uses_one_short_procedure_example_and_keeps_client_steps_for_selected_topics():
    from backend.bintanong_routing.topic_selection import procedure_context
    topic = DocumentTopic(subject_id='fictional_service', claims=('service',),
        claim_fields={'service': ('step1_client_step', 'long_procedure', 'application_procedure')},
        claim_context={'service': {'step1_client_step': 'Obtain form at Office Z.',
            'long_procedure': 'x'*257, 'application_procedure': 'Submit form.'}})
    assert procedure_context(topic) == [dict(claim='service', fields={'application_procedure': 'Submit form.'})]


def test_named_service_can_expose_one_short_client_step_without_selecting_a_source():
    from backend.bintanong_routing.topic_selection import procedure_context
    topic = DocumentTopic(subject_id='fictional_service', claims=('service',),
        source_labels=('ISSUANCE OF FICTIONAL SLIP',),
        claim_fields={'service': ('step1_client_step',)},
        claim_context={'service': {'step1_client_step': 'Obtain fictional slip at Office Z.'}})
    assert procedure_context(topic, 'Where do I obtain fictional slip?') == [dict(claim='service',
        fields={'step1_client_step': 'Obtain fictional slip at Office Z.'})]
    assert procedure_context(topic, 'Explain grading policy.') == []


def test_common_request_word_does_not_expand_every_service_example():
    from backend.bintanong_routing.topic_selection import build_messages
    topics = tuple(DocumentTopic(subject_id=f'fictional_{n}', claims=('service',),
        source_labels=(f'Request for service {n}',), claim_fields={'service': ('step1_client_step',)},
        claim_context={'service': {'step1_client_step': f'Submit fictional form {n} to Office Z.'}})
        for n in range(12))
    menu = json.loads(build_messages('Paano mag-request?', topics)[0]['content'].split('Menu:', 1)[1])
    assert len(menu) == 12 and not any('procedure_context' in item for item in menu)


def test_optional_client_step_examples_have_a_global_menu_bound():
    from backend.bintanong_routing.topic_selection import build_messages
    topics = tuple(DocumentTopic(subject_id=f'fictional_{n}', claims=('service',),
        source_labels=(f'Fictional ServiceName{n}',), claim_fields={'service': ('step1_client_step',)},
        claim_context={'service': {'step1_client_step': f'Submit fictional form {n} to Office Z.'}})
        for n in range(12))
    question = ' '.join(f'ServiceName{n}' for n in range(12))
    menu = json.loads(build_messages(question, topics)[0]['content'].split('Menu:', 1)[1])
    assert len(menu) == 12
    assert sum('procedure_context' in item for item in menu) <= 3


def test_a_reviewed_client_step_naming_the_requested_object_remains_a_candidate():
    from backend.bintanong_routing.topic_selection import add_companions
    policy = DocumentTopic(subject_id='fictional_policy', claims=('policy',))
    service = DocumentTopic(subject_id='fictional_service', claims=('step',),
        claim_fields={'step': ('step1_client_step',)},
        claim_context={'step': {'step1_client_step': 'Obtain fictional permit at Office Z.'}})
    chosen = (policy,)
    assert add_companions(chosen, (policy, service), 'Explain the policy. Where is the fictional permit?') == (policy, service)
    assert add_companions(chosen, (policy, service), 'Explain grading policy.') == chosen


@pytest.mark.parametrize('detail,expected', [('whole', ('checklist', 'first step', 'second step')),
                                         ('requirements', ('checklist',)), ('specific', ('checklist',))])
def test_whole_selected_procedure_keeps_its_steps_without_broadening_narrow_details(detail, expected):
    from backend.bintanong_routing.contracts import Interpretation
    from backend.bintanong_routing.router import prefer_printed_procedure
    text = 'How do I obtain fictional certificate S?'
    topic = DocumentTopic(subject_id='fictional_service', claims=('checklist', 'first step', 'second step'),
        claim_fields={'checklist': ('requirements',), 'first step': ('step1_client_step',),
                      'second step': ('step2_client_step',)})
    value = proposal(text=text, language='en', intent='document_procedure', route='RAG', mentions=[], operations=[])
    value['parts'][0].update(subject_id=topic.subject_id, requested_claims=['checklist'], detail=detail)
    result = prefer_printed_procedure(Interpretation.parse(value), (topic,))
    assert result.parts[0].requested_claims == expected


def test_workflow_metadata_does_not_invent_steps_from_titles_or_not_stated_facts():
    from backend.bintanong_routing.topic_selection import workflow_fact_indices
    topic = DocumentTopic(subject_id='fictional_service', claims=('step 1', 'missing step', 'printed step'),
        not_stated=('missing step',), claim_fields={'missing step': ('step2_client_step',),
                                                 'printed step': ('step3_client_step',)})
    assert workflow_fact_indices(topic) == [2]


def test_step_expansion_never_discards_requested_claims_to_fit_the_bound():
    from backend.bintanong_routing.contracts import Interpretation
    from backend.bintanong_routing.router import prefer_printed_procedure
    topic = DocumentTopic(subject_id='fictional_service', claims=('policy', *(f'step {n}' for n in range(1, 9))),
        claim_fields={f'step {n}': (f'step{n}_client_step',) for n in range(1, 9)})
    text = 'How do I obtain fictional slip S?'
    value = proposal(text=text, language='en', intent='document_procedure', route='RAG', mentions=[], operations=[])
    value['parts'][0].update(subject_id=topic.subject_id, requested_claims=['policy'], detail='whole')
    with pytest.raises(ValueError, match='workflow_claim_capacity'):
        prefer_printed_procedure(Interpretation.parse(value), (topic,))


def test_a_whole_policy_request_does_not_gain_service_steps():
    from backend.bintanong_routing.contracts import Interpretation
    from backend.bintanong_routing.router import prefer_printed_procedure
    text = 'Explain all policies for fictional certificate S.'
    topic = DocumentTopic(subject_id='fictional_service', claims=('policy', 'first step'),
        claim_fields={'policy': ('body',), 'first step': ('step1_client_step',)})
    value = proposal(text=text, language='en', intent='policy explanation', route='RAG', mentions=[], operations=[])
    value['parts'][0].update(subject_id=topic.subject_id, requested_claims=['policy'], detail='whole')
    result = prefer_printed_procedure(Interpretation.parse(value), (topic,))
    assert result.parts[0].requested_claims == ('policy',)


@pytest.mark.parametrize('question,subject,claim,detail', [
    ('How do I obtain fictional certificate S?', 'fictional_service', 'complete service fields', 'whole'),
    ('Which rule governs fictional certificate S?', 'fictional_policy', 'certificate policy', 'specific'),
    ('What must I bring for fictional certificate S?', 'fictional_service', 'application checklist', 'requirements'),
])
def test_request_type_keeps_its_reviewed_source_and_claims(question, subject, claim, detail):
    topics = (DocumentTopic(subject_id='fictional_policy', claims=('certificate policy',),
        claim_fields={'certificate policy': ('body',)}),
        DocumentTopic(subject_id='fictional_service', claims=('complete service fields', 'application checklist'),
            claim_fields={'complete service fields': ('step1_client_step', 'step1_agency_action'),
                          'application checklist': ('requirements',)}))
    value = proposal(text=question, language='en', route='RAG', mentions=[], operations=[])
    value['parts'][0].update(subject_id=subject, requested_claims=[claim], detail=detail)
    model = FakeTransport(json.dumps(value), style_outputs=[json.dumps(
        style_proposal('en', english=[question], filipino=[]))])
    result = asyncio.run(Router(model, catalog=catalog(), registry=registry(), topics=topics,
        documents_available=True, synthetic=True).route(question, RequestContext.parse(context())))
    assert result.decision.route == 'RAG' and result.diagnostic == 'validated'
    assert result.proposed.parts[0].subject_id == subject
    assert result.proposed.parts[0].requested_claims == (claim,)
