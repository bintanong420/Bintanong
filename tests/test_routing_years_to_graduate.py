"""Owner 2 Nov 2026 (#2, option B): "how many years before I graduate" is answered both ways: the program length is
in the prospectus, and the Handbook's printed residence rule (1.4) is quoted exactly. Fictional wrappers only."""
import json
from types import SimpleNamespace

import pytest

from backend.bintanong_routing.contracts import DocumentTopic, Interpretation
from backend.bintanong_routing.topic_selection import YEARS_TO_GRADUATE, add_companions
from test_routing_contracts import proposal

RULE = ('No student shall be graduated from the University without completing at least one year of residence work. '
        'The residence work referred to must be done immediately prior to graduation.')


@pytest.mark.parametrize('text,asks', [
    ('ilang taon dapat ako mag aral dito bago maka graduate?', True),
    ('how many years do I need to study before I graduate?', True),
    ('how long do i need to study here to graduate with latin honors?', False),
    ('ilang units ang kailangan ko?', False)])
def test_the_question_is_recognised_without_honours(text, asks):
    assert bool(YEARS_TO_GRADUATE(text)) is asks


def test_the_graduation_topic_is_offered_for_this_question():
    menu = tuple(DocumentTopic(subject_id=s, claims=(f'printed {s} fields',))
                 for s in ('handbook_residence', 'handbook_year_levels', 'handbook_graduation'))
    picked = add_companions(menu[:2], menu, 'ilang taon dapat ako mag aral dito bago maka graduate?')
    assert [t.subject_id for t in picked] == ['handbook_residence', 'handbook_year_levels', 'handbook_graduation']


def test_the_part_is_answered_from_the_graduation_rules():
    from backend.bintanong_routing.router import answer_years_to_graduate
    text = 'ilang taon dapat ako mag aral dito bago maka graduate?'
    topics = (DocumentTopic(subject_id='handbook_year_levels', claims=('printed year levels fields',)),
              DocumentTopic(subject_id='handbook_graduation', claims=('printed graduation fields',)))
    value = proposal(text=text, language='taglish', route='RAG', mentions=[], operations=[])
    value['parts'][0].update(subject_id='handbook_year_levels', requested_claims=['printed year levels fields'])
    routed = answer_years_to_graduate(Interpretation.parse(value), topics, text)
    part, = routed.parts
    assert (part.subject_id, part.requested_claims, routed.route) == ('handbook_graduation', ('printed graduation fields',), 'RAG')


def test_an_operation_without_a_named_course_still_goes_to_the_graduation_rules():
    # Live 2 Nov 2026: the router attached a structured operation (no course named), so the guard skipped it.
    from backend.bintanong_routing.router import answer_years_to_graduate
    text = 'ilang taon dapat ako mag aral dito bago maka graduate?'
    topics = (DocumentTopic(subject_id='handbook_graduation', claims=('printed graduation fields',)),)
    value = proposal(text=text, language='taglish', route='Symbolic',
                     mentions=[dict(kind='term', text='ilang taon', start=0, end=10)],
                     operations=[dict(name='list_term_courses', target=0)])
    value['parts'][0].update(evidence_need='structured', operation_indices=[0])
    routed = answer_years_to_graduate(Interpretation.parse(value), topics, text)
    assert routed.parts[0].subject_id == 'handbook_graduation' and not routed.operations


def card(text):
    return SimpleNamespace(evidence_id='ev-g', kind='document', citations=(SimpleNamespace(filename='PSU Student Handbook.pdf'),),
                           text=json.dumps(dict(fields=[dict(name='body', source_blank=False, value=(
                               '1.3 REMOVAL OF DEFICIENCIES. Fictional. 1.4 RESIDENCE REQUIREMENTS. ' + text))])))


def test_the_reply_quotes_the_printed_rule_and_leads_with_the_program_length_pointer():
    from backend.bintanong_generation.residence_reply import POINTER, residence_reply
    part = SimpleNamespace(subject_id='handbook_graduation', text='ilang taon dapat ako mag aral dito bago maka graduate?')
    # Live 2 Nov 2026: a Taglish reply made only of the English quote failed the reply-style rule, so Taglish
    # introduces it with Filipino connecting words; English keeps the bare quote.
    claim, = residence_reply(SimpleNamespace(language='taglish', cards=(card(RULE),)), part)
    assert claim == dict(text=f'Ayon sa Student Handbook 1.4: "{RULE}"', evidence_ids=['ev-g'])
    claim, = residence_reply(SimpleNamespace(language='en', cards=(card(RULE),)), part)
    assert claim == dict(text=f'"{RULE}" (Student Handbook 1.4)', evidence_ids=['ev-g'])
    assert 'prospectus' in POINTER['taglish'] and 'prospectus' in POINTER['en']
    # Final run 2 Nov 2026: the pointer and the quote both named the Handbook; the quote alone names it now.
    assert all('Student Handbook' not in POINTER[k] for k in ('en', 'taglish'))
    other = SimpleNamespace(subject_id='handbook_graduation', text='what are the graduation requirements?')
    assert residence_reply(SimpleNamespace(language='en', cards=(card(RULE),)), other) is None
    assert residence_reply(SimpleNamespace(language='en', cards=(card('Fictional other rule.'),)), part) is None
