"""Document context must not grant a scoped course-reference capability."""
import asyncio
import json

import pytest

from backend.bintanong_routing.contracts import DocumentTopic, RequestContext
from backend.bintanong_routing.prompt import build_messages
from backend.bintanong_routing.router import Router
from test_routing_contracts import context
from test_routing_follow_up import PREVIOUS
from test_routing_router import FakeTransport, style_proposal
from test_routing_validation import catalog, registry

TEXT = 'What is step 1?'
SUBJECT = 'fictional_service'
MENU = (DocumentTopic(subject_id=SUBJECT, claims=('printed service steps',)),
        DocumentTopic(subject_id='fictional_fee', claims=('printed fee',)))


def document_wire(text=TEXT, *, subject=SUBJECT, quote=None, ambiguity=False):
    value=dict(schema_version='bintanong-interpretation-wire-v4', language='en',
        audience='undergraduate', control='clarify' if ambiguity else None, part_count=1,
        parts=[dict(part_id='r1',quote=dict(text=text,occurrence=0),evidence_need='document',
            operation_indices=[],subject_id=subject,requested_claims=[
                'printed service steps' if subject==SUBJECT else 'printed fee'])],
        intent='procedure inquiry',mentions=[],claims=[],operations=[],
        route=None if ambiguity else 'RAG',ambiguities=['unclear antecedent'] if ambiguity else [])
    if quote is not None: value['previous_course_quote']=dict(text=quote,occurrence=0)
    return json.dumps(value)


def run(*outputs, text=TEXT, previous=None, language='en', **ctx_changes):
    previous = dict(subject_id=SUBJECT) if previous is None else previous
    transport=FakeTransport(*outputs,style_outputs=[json.dumps(style_proposal(language,
        english=['What'] if language=='en' else ['step'],
        filipino=[] if language=='en' else ['Ano']))] * 3)
    ctx=RequestContext.parse(context(conversation=previous,**ctx_changes))
    result=asyncio.run(Router(transport,catalog=catalog(),registry=registry(),
        documents_available=True,synthetic=True,topics=MENU).route(text,ctx))
    return result,transport,ctx


@pytest.mark.parametrize('previous,scope', [
    (dict(subject_id=SUBJECT), {}),
    (dict(PREVIOUS,subject_id=SUBJECT,course_id='course-absent'), {}),
    (dict(PREVIOUS,subject_id=SUBJECT), dict(curriculum_id='curriculum-b')),
])
def test_actual_document_only_decoder_never_offers_a_course_reference(previous, scope):
    result,transport,_=run(document_wire(),previous=previous,**scope)
    assert result.decision.route=='RAG' and result.proposed.context_reference is None
    schema=transport.calls[0][1]
    assert 'previous_course_quote' not in schema['properties']
    assert 'previous_course_quote' not in schema['required']
    assert result.proposed.parts[0].subject_id==SUBJECT


def test_display_schema_agrees_with_the_actual_decoder_for_document_only_context():
    _,transport,ctx=run(document_wire())
    messages=build_messages(TEXT,ctx,catalog(),registry(),MENU)
    displayed=json.loads(messages[0]['content'].split('JSON schema:\n',1)[1])
    assert 'previous_course_quote' not in displayed['properties']
    assert json.loads(messages[1]['content'])['previous_turn']==dict(subject_id=SUBJECT)
    assert 'course_available' not in json.loads(transport.calls[0][0][1]['content'])['previous_turn']


@pytest.mark.parametrize('scope', [{},dict(program_id=None,curriculum_id=None)])
def test_mixed_context_keeps_a_real_scoped_course_and_document_subject(scope):
    result,transport,_=run(document_wire(),previous=dict(PREVIOUS,subject_id=SUBJECT),**scope)
    assert result.decision.route=='RAG'
    assert 'previous_course_quote' in transport.calls[0][1]['properties']
    assert json.loads(transport.calls[0][0][1]['content'])['previous_turn']==dict(
        subject_id=SUBJECT,course_available=True)


@pytest.mark.parametrize('quote', ['step', SUBJECT])
def test_unsolicited_course_reference_is_rejected_even_if_the_transport_ignores_grammar(quote):
    bad=document_wire(quote=quote)
    result,transport,_=run(bad,bad)
    assert result.decision.route is None and result.diagnostic=='invalid_reference'
    assert result.attempts==2 and result.style_attempts==1
    assert 'course_reference_unavailable' in transport.calls[1][0][-1]['content']
    assert result.proposed is None


def test_bounded_reference_repair_can_return_the_document_request_without_adding_an_operation():
    result,transport,_=run(document_wire(quote='step'),document_wire())
    assert result.diagnostic=='validated' and result.decision.route=='RAG'
    assert result.attempts==2 and result.inference_calls==3
    assert result.proposed.parts[0].requested_claims==('printed service steps',)
    assert not result.proposed.operations and result.proposed.context_reference is None
    assert 'previous_course_quote' not in transport.calls[1][1]['properties']


def test_document_topic_switch_is_not_overwritten_by_saved_subject():
    text='What is the fee?'
    result,_,_=run(document_wire(text,subject='fictional_fee'),text=text)
    assert result.decision.route=='RAG' and result.proposed.parts[0].subject_id=='fictional_fee'


def test_semantic_ambiguity_is_preserved_without_a_course_reference_repair():
    result,transport,_=run(document_wire(ambiguity=True))
    assert result.decision.control=='clarify'
    assert result.attempts==1 and len(transport.calls)==2


def test_taglish_document_follow_up_keeps_the_new_reply_policy():
    text='Ano yung step 1?'
    result,_,_=run(document_wire(text),text=text,language='taglish')
    assert result.decision.route=='RAG' and result.response_style=='taglish'
    assert result.proposed.context_reference is None and not result.proposed.operations
