"""Router topic/fact selection from a release-supplied menu (research real-data mode).

Without a menu the wire schema and prompt are unchanged. With a menu each document
part must name one menu subject (or null) and only that subject's reviewed claims.
"""
import json

import pytest

from backend.bintanong_routing.contracts import DocumentTopic, NotStatedCue, RequestPart
from backend.bintanong_routing.prompt import build_messages, output_schema
from test_routing_contracts import proposal
from test_routing_router import FakeTransport, run, style_proposal

MENU = (DocumentTopic(subject_id='fictional_fees', claims=('printed fee amount', 'payment channel')),
        DocumentTopic(subject_id='fictional_office', claims=('filing office',)))
TEXT = 'Where do I file slip S?'


def model(*outputs):
    style = json.dumps(style_proposal('en', english=['Where do I file']))
    return FakeTransport(*outputs, style_outputs=[style] * 3)


def answer(subject='fictional_office', claims=('filing office',)):
    value = proposal(text=TEXT, route='RAG', mentions=[], operations=[], intent='Filing location', language='en')
    value['parts'][0].update(subject_id=subject, requested_claims=list(claims))
    return json.dumps(value)


def test_schema_without_topics_is_unchanged():
    part = output_schema()['$defs']['WirePart']
    assert set(part['properties']) == {'part_id', 'quote', 'evidence_need', 'operation_indices'}


def test_schema_with_topics_pairs_each_topic_with_its_own_claims():
    branches = output_schema(MENU)['$defs']['WirePart']['anyOf']
    by_subject = {b['properties']['subject_id'].get('const'): b['properties']['requested_claims']
                  for b in branches}
    assert set(by_subject) == {'fictional_fees', 'fictional_office', None}
    assert by_subject['fictional_office']['items']['enum'] == ['filing office']
    assert by_subject['fictional_office']['minItems'] == 1
    assert by_subject[None]['maxItems'] == 0
    assert all({'subject_id', 'requested_claims'} <= set(b['required']) for b in branches)


def test_prompt_lists_topics_only_when_a_menu_exists():
    from backend.bintanong_routing.contracts import RequestContext
    from test_routing_router import context
    ctx = RequestContext.parse(context())
    with_menu = build_messages(TEXT, ctx, (), _registry(), topics=MENU)[0]['content']
    without = build_messages(TEXT, ctx, (), _registry())[0]['content']
    assert 'fictional_office' in with_menu and 'filing office' in with_menu
    assert 'fictional_office' not in without and 'Document topics' not in without


def _registry():
    from test_routing_router import registry
    return registry()


def test_router_keeps_a_valid_topic_choice():
    result = run(model(answer()), text=TEXT, topics=MENU)
    assert result.diagnostic == 'validated' and result.decision.route == 'RAG'
    part = result.proposed.parts[0]
    assert part.subject_id == 'fictional_office' and part.requested_claims == ('filing office',)


def test_router_rejects_claims_outside_the_chosen_topic():
    result = run(FakeTransport(answer(claims=('printed fee amount',)), answer(claims=('printed fee amount',))),
                 text=TEXT, topics=MENU)
    assert result.diagnostic == 'invalid_reference'


def test_router_rejects_topic_choices_when_no_menu_exists():
    result = run(FakeTransport(answer(), answer()), text=TEXT)
    assert result.diagnostic == 'invalid_reference'


def test_only_document_parts_carry_topics():
    with pytest.raises(ValueError):
        RequestPart.parse(dict(part_id='r1', text='A1', start=0, end=2, evidence_need='structured',
                               operation_indices=[0], subject_id='fictional_fees', requested_claims=[]))


def test_generation_input_omits_retrieval_topic_labels():
    from backend.bintanong_generation.evidence import prepare
    from backend.bintanong_generation.scope import document_payload
    from test_request_understanding_pipeline import source
    parts = document_payload(prepare(source()))['requested_parts']
    assert parts and all('subject_id' not in p and 'requested_claims' not in p for p in parts)


def test_prompt_shows_plain_topic_fields_while_the_grammar_keeps_paired_branches():
    from backend.bintanong_routing.contracts import RequestContext
    from test_routing_router import context
    ctx = RequestContext.parse(context())
    system = build_messages(TEXT, ctx, (), _registry(), topics=MENU)[0]['content']
    shown = system.split('JSON schema:\n', 1)[1]
    assert 'subject_id' in shown and 'requested_claims' in shown
    assert 'anyOf' not in shown  # per-topic branches stay in the enforced grammar only
    assert 'anyOf' in json.dumps(output_schema(MENU))


NOT_STATED = (DocumentTopic(subject_id='fictional_fees', claims=('printed fee amount',),
                            not_stated=('individual share',)),)


def test_not_stated_facts_are_selectable_and_shown_as_not_stated():
    branch = next(b for b in output_schema(NOT_STATED)['$defs']['WirePart']['anyOf']
                  if b['properties']['subject_id'].get('const') == 'fictional_fees')
    assert branch['properties']['requested_claims']['items']['enum'] == ['printed fee amount', 'individual share']
    from backend.bintanong_routing.contracts import RequestContext
    from test_routing_router import context
    system = build_messages(TEXT, RequestContext.parse(context()), (), _registry(), topics=NOT_STATED)[0]['content']
    assert '"not_stated":["individual share"]' in system


def test_menus_without_not_stated_facts_render_as_before():
    from backend.bintanong_routing.contracts import RequestContext
    from test_routing_router import context
    system = build_messages(TEXT, RequestContext.parse(context()), (), _registry(), topics=MENU)[0]['content']
    assert 'not_stated' not in system


def test_router_accepts_a_not_stated_fact_of_the_chosen_topic():
    from backend.bintanong_routing.router import check_topics
    from backend.bintanong_routing.contracts import Interpretation
    value = json.loads(answer(subject='fictional_fees', claims=('individual share',)))
    proposed = Interpretation.parse(value)
    check_topics(proposed, NOT_STATED)


CUED = (DocumentTopic(subject_id='fictional_fees', claims=('printed fee amount',), not_stated=('individual share',),
                      cues=(NotStatedCue(claim='individual share', phrases=('each student', 'bawat isa')),)),)


def fee_question(text):
    value = proposal(text=text, route='RAG', mentions=[], operations=[], intent='Fee', language='en')
    value['parts'][0].update(subject_id='fictional_fees', requested_claims=['printed fee amount'])
    return json.dumps(value)


@pytest.mark.parametrize('text,expected', [
    ('How much does each student pay?', ('printed fee amount', 'individual share')),
    ('Magkano ang bayad ng bawat isa?', ('printed fee amount', 'individual share')),
    ('What amount does the fee example show?', ('printed fee amount',))])
def test_cue_in_the_part_adds_its_not_stated_fact(text, expected):
    # Owner, 23 Oct 2026 (run 11): a per-person amount question must reach the not-stated fact, so
    # the policy withholds instead of presenting the printed example as one student's share.
    style = json.dumps(style_proposal('en', english=[text.split()[0]]))
    transport = FakeTransport(fee_question(text), style_outputs=[style] * 3)
    result = run(transport, text=text, topics=CUED)
    assert result.decision.route == 'RAG' and result.proposed.parts[0].requested_claims == expected


def test_cue_must_name_one_of_the_topics_not_stated_facts():
    with pytest.raises(ValueError):
        DocumentTopic(subject_id='fictional_fees', claims=('printed fee amount',),
                      cues=(NotStatedCue(claim='printed fee amount', phrases=('each student',)),))


def test_menu_prompt_treats_a_named_destination_in_a_procedure_question_as_context():
    # Owner option A (28 Oct 2026): live "Gusto ko mag-shift sa ibang college, ano yung process?" got clarify
    # although the shifting topic fits. The contrast example is fictional, not the evaluation wording.
    from backend.bintanong_routing.contracts import RequestContext
    from test_routing_router import context
    system = build_messages(TEXT, RequestContext.parse(context()), (), _registry(), topics=MENU)[0]['content']
    assert 'destination is context' in system
    assert 'shift' not in system.casefold()


def test_destination_example_does_not_fix_the_part_count():
    # Live 04e913f: the example's "one document part" made the router merge the two cross-enrollment questions.
    from backend.bintanong_routing.prompt import TOPIC_INSTRUCTION
    assert 'one document part' not in TOPIC_INSTRUCTION
    assert 'parts as requested' in TOPIC_INSTRUCTION


# Owner 28 Oct 2026: answer only the printed detail asked. The router labels each document part's detail.
DETAILS = ['whole', 'requirements', 'fees', 'processing_time', 'specific']


def test_menu_parts_declare_one_printed_detail_and_the_default_schema_has_none():
    branches = output_schema(MENU)['$defs']['WirePart']['anyOf']
    by_subject = {b['properties']['subject_id'].get('const'): b for b in branches}
    assert by_subject['fictional_fees']['properties']['detail'] == {'enum': DETAILS}
    assert by_subject[None]['properties']['detail'] == {'const': 'whole'}
    assert all('detail' in b['required'] for b in branches)
    assert 'detail' not in output_schema()['$defs']['WirePart']['properties']


def test_router_keeps_the_asked_detail_and_defaults_to_whole():
    value = json.loads(answer())
    value['parts'][0]['detail'] = 'fees'
    result = run(model(json.dumps(value)), text=TEXT, topics=MENU)
    assert result.diagnostic == 'validated' and result.proposed.parts[0].detail == 'fees'
    plain = run(model(answer()), text=TEXT, topics=MENU)
    assert plain.proposed.parts[0].detail == 'whole'


def test_menu_prompt_explains_the_detail_choice():
    from backend.bintanong_routing.prompt import TOPIC_INSTRUCTION
    assert 'detail' in TOPIC_INSTRUCTION and 'whole' in TOPIC_INSTRUCTION


def test_menu_prompt_offers_a_specific_detail_and_no_clarify_for_missing_personal_details():
    # Gate 28 Oct 2026: "When am I considered a second-year student?" was labelled whole (no option fit one printed
    # fact), and its Taglish form returned an empty clarify although the year-levels topic was selected.
    from backend.bintanong_routing.prompt import TOPIC_INSTRUCTION
    assert 'specific' in TOPIC_INSTRUCTION
    assert 'personal details' in TOPIC_INSTRUCTION


# Owner 30 Oct 2026: a fact whose printed section heading clearly names the part's words replaces a chosen fact
# whose headings name none of them (adding both exceeded the topic's context budget).
HEADED = (DocumentTopic(subject_id='fictional_completion',
    claims=('printed timing statements', 'printed mark meaning fields', 'printed approval fields', 'printed fee fields'),
    claim_headings={'printed mark meaning fields': ('3.4 REMOVAL OF “INC”',),
                    'printed approval fields': ('3.5 EXAMINATION FOR REMOVAL OR COMPLETION',),
                    'printed fee fields': ('3.9 FICTIONAL FEES',)}),
    DocumentTopic(subject_id='fictional_other', claims=('printed other fields',),
                  claim_headings={'printed other fields': ('4. REMOVAL OF OTHER INC MARKS',)}))


def headed(text, claims=('printed timing statements',)):
    style = json.dumps(style_proposal('en', english=[text.split()[0]]))
    value = proposal(text=text, route='RAG', mentions=[], operations=[], intent='Completion', language='en')
    value['parts'][0].update(subject_id='fictional_completion', requested_claims=list(claims))
    return run(FakeTransport(json.dumps(value), style_outputs=[style] * 3), text=text, topics=HEADED)


def test_a_clearly_matching_heading_replaces_an_unmatched_choice():
    # 3.4 REMOVAL OF "INC" names "remove" and "incomplete"; 3.5 names only "remove".
    claims = headed('How do I remove an incomplete grade?').proposed.parts[0].requested_claims
    assert claims == ('printed mark meaning fields',)


@pytest.mark.parametrize('text', ['Paano tanggalin ang INC ko?', 'Is there a removal deadline?',
                                  'What is the deadline for it?'])
def test_a_single_word_match_or_a_tie_keeps_the_model_choice(text):
    assert headed(text).proposed.parts[0].requested_claims == ('printed timing statements',)


def test_a_chosen_fact_whose_heading_matches_is_kept():
    claims = headed('How do I remove an incomplete grade?', claims=('printed approval fields',)).proposed.parts[0]
    assert claims.requested_claims == ('printed approval fields',)


# Regression 30 Oct 2026: "Ano ang parusa kapag mali ang uniform ko?" chose a discourtesy row of the sanctions table;
# only "I. Improper Uniform" names the part's word. Rows have no printed section headings, so their labels decide.
TABLE = (DocumentTopic(subject_id='fictional_sanctions',
    claims=('printed I fields: I. Fictional Uniform', 'printed II.13 fields: 13. Fictional discourtesy towards officials',
            'printed II.20 fields: 20. Fictional smoking inside rooms', 'printed II.21 fields: 21. Fictional smoking near gates',
            'the content of a fictional missing item'),
    not_stated=('the content of a fictional missing item',)),)


def tabled(text, claims, detail='whole'):
    style = json.dumps(style_proposal('taglish', filipino=[text.split()[0]]))
    value = proposal(text=text, route='RAG', mentions=[], operations=[], intent='Sanction', language='fil')
    value['parts'][0].update(subject_id='fictional_sanctions', requested_claims=list(claims), detail=detail)
    return run(FakeTransport(json.dumps(value), style_outputs=[style] * 3), text=text, topics=TABLE)


def test_the_one_row_naming_the_parts_word_replaces_an_unrelated_row():
    claims = tabled('Ano ang parusa kapag mali ang uniform ko?', ('printed II.13 fields: 13. Fictional discourtesy towards officials',))
    assert claims.proposed.parts[0].requested_claims == ('printed I fields: I. Fictional Uniform',)


@pytest.mark.parametrize('text, chosen', [
    ('Ano ang parusa sa discourtesy at uniform?', 'printed II.13 fields: 13. Fictional discourtesy towards officials'),
    ('Ano ang parusa sa smoking?', 'printed II.13 fields: 13. Fictional discourtesy towards officials'),
    ('Ano ang parusa kapag nagsinungaling ako?', 'printed II.13 fields: 13. Fictional discourtesy towards officials')])
def test_a_matching_choice_two_matching_rows_or_no_match_keep_the_model_choice(text, chosen):
    assert tabled(text, (chosen,)).proposed.parts[0].requested_claims == (chosen,)


def test_a_chosen_not_stated_fact_is_left_to_the_withholding_guards():
    claims = tabled('Magkano ang multa sa uniform?', ('the content of a fictional missing item',), detail='specific')
    assert claims.proposed.parts[0].requested_claims == ('the content of a fictional missing item',)


# Regression 30 Oct 2026: "Ano ang residence requirement para maka-graduate?" chose the maximum-residence topic
# ("1. RESIDENCE" names one word) although the graduation topic prints "1.4 RESIDENCE REQUIREMENTS" (two words).
TWO_TOPICS = (DocumentTopic(subject_id='fictional_graduation', claims=('printed graduation fields',),
                            claim_headings={'printed graduation fields': ('1. REQUIREMENTS', '1.4 RESIDENCE REQUIREMENTS')}),
              DocumentTopic(subject_id='fictional_residence', claims=('printed residence fields',),
                            claim_headings={'printed residence fields': ('1. RESIDENCE', '2. MAXIMUM RESIDENCE RULE')}))


def two_topics(text, subject='fictional_residence', claims=('printed residence fields',)):
    style = json.dumps(style_proposal('taglish', filipino=[text.split()[0]]))
    value = proposal(text=text, route='RAG', mentions=[], operations=[], intent='Residence', language='fil')
    value['parts'][0].update(subject_id=subject, requested_claims=list(claims))
    return run(FakeTransport(json.dumps(value), style_outputs=[style] * 3), text=text, topics=TWO_TOPICS).proposed.parts[0]


def test_a_selected_topic_whose_heading_names_more_of_the_parts_words_replaces_the_choice():
    part = two_topics('Ano ang residence requirement para maka-graduate?')
    assert (part.subject_id, part.requested_claims) == ('fictional_graduation', ('printed graduation fields',))


@pytest.mark.parametrize('text', ['Ano ang maximum residence rule?', 'Gaano katagal ang residence ko?',
                                  'Ano ang requirements?'])
def test_an_equal_better_or_single_word_match_keeps_the_chosen_topic(text):
    assert two_topics(text).subject_id == 'fictional_residence'


# Owner 30 Oct 2026: reviewed Filipino words name the English printed penalty rows (backend/bintanong_routing/
# filipino_terms.py). Common-query run: "nangongopya sa pagsusulit", "nagyosi" and "nambubully" chose the
# not-stated item and were withheld; the rows print "cheating in examinations", "Smoking" and "Bullying".
FILLER = tuple(f'printed II.{n} fields: {n}. Fictional offense {name}' for n, name in
               ((1, 'alpha'), (2, 'beta'), (3, 'gamma'), (4, 'delta'), (5, 'epsilon')))
SANCTIONS = (DocumentTopic(subject_id='fictional_misconduct',
    claims=('printed II.7a fields: a. Any form of cheating in examinations',
            'printed II.7e fields: e. Unauthorized reproduction of examination',
            'printed II.20 fields: 20. Smoking inside the classroom', 'printed II.25 fields: 25. Bullying is defined',
            'printed II.26 fields: 26. Cyber bullying is the willful harm', *FILLER, 'the content of missing item 22'),
    not_stated=('the content of missing item 22',)),)


def sanctioned(text, claims=('the content of missing item 22',)):
    style = json.dumps(style_proposal('taglish', filipino=[text.split()[0]]))
    value = proposal(text=text, route='RAG', mentions=[], operations=[], intent='Sanction', language='fil')
    value['parts'][0].update(subject_id='fictional_misconduct', requested_claims=list(claims))
    return run(FakeTransport(json.dumps(value), style_outputs=[style] * 3), text=text,
               topics=SANCTIONS).proposed.parts[0].requested_claims


@pytest.mark.parametrize('text, expected', [
    ('Ano ang parusa kapag nahuling nangongopya sa pagsusulit?',
     ('printed II.7a fields: a. Any form of cheating in examinations',)),
    ('Ano parusa pag kumopya ako?', ('printed II.7a fields: a. Any form of cheating in examinations',)),
    ('ano penalty pag nagyosi sa campus?', ('printed II.20 fields: 20. Smoking inside the classroom',)),
    ('ano parusa sa nambubully?', ('printed II.25 fields: 25. Bullying is defined',
                                   'printed II.26 fields: 26. Cyber bullying is the willful harm'))])
def test_reviewed_filipino_words_name_the_printed_row(text, expected):
    assert sanctioned(text) == expected


def test_a_reviewed_form_inside_a_longer_word_names_nothing():
    # "malaking" contains "alak" (drinking); only whole reviewed words count.
    assert sanctioned('Ano ang malaking parusa?') == ('the content of missing item 22',)


def test_reviewed_filipino_terms_are_whole_words_mapped_to_printed_english_terms():
    from backend.bintanong_routing.filipino_terms import printed_terms
    assert printed_terms('kumukopya') == ('cheating',) and printed_terms('pagsusulit') == ('examination',)
    assert printed_terms('uniporme') == () and printed_terms('malaking') == ()
