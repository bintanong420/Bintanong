"""Owner F4 (28 Oct 2026, provisional "b perhaps"): a transfer question that does not say whether the student
is leaving PalSU or transferring in is asked first. Synthetic topics; no institutional policy is asserted."""
import asyncio

import pytest

from backend.bintanong_orchestration.contracts import IntegrationResult
from backend.bintanong_routing.contracts import DocumentTopic
from test_generation_loop import Fake, api
from test_routing_topic_selection import Transport, answer, run, selected

FILLER = tuple(DocumentTopic(subject_id=f'other_{i}', claims=(f'printed synthetic clause {i}',)) for i in range(8))
MENU = (DocumentTopic(subject_id='fictional_incoming', claims=('printed incoming fields',),
                      family='transferring_into_palsu'),
        DocumentTopic(subject_id='fictional_outgoing', claims=('printed outgoing fields',),
                      family='leaving_palsu_transfer_credentials'),
        DocumentTopic(subject_id='fictional_office', claims=('filing office',)), *FILLER)


def route(text, subject):
    transport = Transport(selected((subject,)), answer(subject, (MENU_CLAIMS[subject],), text=text), text=text)
    result, _ = run(transport, text=text, topics=MENU)
    return result


MENU_CLAIMS = {t.subject_id: t.claims[0] for t in MENU}


@pytest.mark.parametrize('subject', ['fictional_incoming', 'fictional_outgoing'])
def test_transfer_topic_without_a_stated_direction_asks_first(subject):
    result = route('What are the requirements for transfer credentials?', subject)
    assert not result.decision.dispatchable and result.decision.control == 'clarify'
    assert result.decision.missing_facts == ('transfer_direction',)
    assert result.diagnostic == 'transfer_direction_unstated'


@pytest.mark.parametrize('text,subject', [
    ('How much is the honorable dismissal?', 'fictional_outgoing'),
    ('I am leaving PalSU, what do I need for transfer credentials?', 'fictional_outgoing'),
    ('Ano ang requirements kung galing sa ibang school ako?', 'fictional_incoming'),
    ('What does a transferee need to submit?', 'fictional_incoming'),
])
def test_a_stated_direction_answers_without_asking(text, subject):
    result = route(text, subject)
    assert result.decision.dispatchable and result.decision.route == 'RAG'


def test_the_direction_question_is_remembered_for_the_next_turn():
    # Owner GUI 3 Nov 2026 (H2, #11): after "Aalis ka ba ...?" every reply was treated as a new question with no topic.
    from backend.bintanong_private_context.conversation import capture
    asked = route('What are the requirements for transfer credentials?', 'fictional_incoming')
    remembered = capture(asked)
    assert remembered is not None and remembered.pending == 'transfer_direction'


def follow_up(text, subject='fictional_office'):
    from test_routing_contracts import context
    transport = Transport(selected((subject,)), answer(subject, (MENU_CLAIMS[subject],), text=text), text=text)
    result, _ = run(transport, text=text, topics=MENU,
                    ctx=context(conversation=dict(pending='transfer_direction', detail='fees')))
    return result


@pytest.mark.parametrize('text,expected', [
    ('aalis ako', 'fictional_outgoing'), ('leaving PalSU', 'fictional_outgoing'),
    ('transferring in', 'fictional_incoming'), ('lilipat ako sa PalSU galing sa ibang school', 'fictional_incoming'),
    # Owner GUI 3 Nov 2026 (#11): typed Taglish replies, sent after the original question by the GUI.
    ('magkano bayad sa transfer credentials\n\nlipat to PalSU from ibang school', 'fictional_incoming'),
    ('magkano bayad sa transfer credentials\n\nlilipat ako to ibang school', 'fictional_outgoing')])
def test_a_reply_that_picks_a_side_is_answered_from_that_side(text, expected):
    result = follow_up(text)
    assert result.decision.dispatchable and result.decision.route == 'RAG'
    part, = result.proposed.parts
    assert (part.subject_id, part.detail) == (expected, 'fees')


def test_a_reply_that_picks_no_side_is_asked_again():
    result = follow_up('pwede both?', 'fictional_incoming')
    assert result.decision.control == 'clarify' and result.decision.missing_facts == ('transfer_direction',)


def test_topics_outside_the_transfer_families_never_ask_for_a_direction():
    result = route('Where do I file the transfer slip?', 'fictional_office')
    assert result.decision.dispatchable


QUESTION = {'en': 'Are you leaving PalSU', 'fil': 'Aalis ka ba', 'taglish': 'Aalis ka ba'}
# Owner 2 Nov 2026 (#11, B+): the question names the leaving fee so the student sees why it is asked.
FEE_FIRST = {'en': "There's a fee when you leave PalSU (transfer credentials / honorable dismissal). Are you leaving "
                   'PalSU, or transferring into PalSU from another school?',
             'taglish': 'May fee kapag aalis ka sa PalSU (transfer credentials / honorable dismissal). Aalis ka ba, '
                        'o lilipat ka sa PalSU galing sa ibang school?'}
FEE_FIRST['fil'] = FEE_FIRST['taglish']


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_transfer_direction_reply_asks_leaving_or_transferring_in(language):
    source = IntegrationResult(understanding=None, schema_version=IntegrationResult.SCHEMA_VERSION, request_id='req-a',
                               route=None, response_style=language, status='clarify', evidence=None,
                               missing_facts=('transfer_direction',), events=())
    answer_ = asyncio.run(api().Generator(Fake(), explanation_profile='legacy').generate('transfer?', source))
    assert answer_.status == 'clarification_needed'
    assert QUESTION[language] in answer_.text and 'transfer_direction' not in answer_.text
    assert FEE_FIRST[language] in answer_.text.splitlines()


@pytest.mark.parametrize('text', [
    'What are the admission requirements for the College of Law?',
    'How do I enroll in the Juris Doctor program?',
    'Paano mag-apply sa graduate school?',
    "What are the requirements for a master's program?",
    'Ano ang requirements sa laboratory school?',
])
def test_a_question_naming_an_excluded_program_gets_the_scope_notice(text):
    result = route(text, 'fictional_office')
    assert not result.decision.dispatchable and result.decision.control == 'unsupported_scope'
    assert result.diagnostic == 'excluded_program_named'


@pytest.mark.parametrize('text', ['Is there a law subject in my program?', 'Where do I file slip S for my faculty adviser?'])
def test_ordinary_undergraduate_wording_is_not_an_excluded_program(text):
    assert route(text, 'fictional_office').decision.dispatchable
