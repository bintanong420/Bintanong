"""Accepted question-word spelling repairs keep the student's exact original spans."""
import pytest

from backend.bintanong_routing.contracts import quote_matches
from backend.bintanong_routing.wire import WireInterpretation, normalize_interpretation
from test_routing_wire import packet


@pytest.mark.parametrize('original, quoted', [
    ('Pano ko kukunin ang card?', 'Paano ko kukunin ang card?'),
    ('paano ko kukunin ang card?', 'pano ko kukunin ang card?'),
    ('Pano\tko kukunin ang card?', 'Paano ko kukunin ang card?'),
])
def test_question_word_spelling_maps_to_the_original_whole_phrase(original, quoted):
    assert quote_matches(original, quoted) == [(0, len(original))]


def test_wire_repairs_unique_question_spelling_and_occurrence_without_changing_facts():
    question = 'Pano ko kukunin ang fictional card?'
    original = 'Can I take B2 after failing A1? ' + question
    value = packet()
    value['parts'][1]['quote'] = dict(text='Paano ko kukunin ang fictional card?', occurrence=1)
    result = normalize_interpretation(original, WireInterpretation.parse(value))
    part = result.parts[1]
    assert (part.text, part.start, part.end) == (question, original.index(question), len(original))
    assert [m.text for m in result.mentions] == ['A1', 'B2']
    assert result.claims[0].text == 'failing A1' and result.claims[0].state == 'failed'
    assert result.operations[0].target == 1


def test_equivalent_question_spellings_keep_all_original_occurrences():
    original = 'Pano? Paano? Pano?'
    assert quote_matches(original, 'Paano?') == [(0, 5), (6, 12), (13, 18)]


@pytest.mark.parametrize('original, quoted', [
    ('PANO101', 'PAANO101'), ('pano5', 'paano5'), ('Pano-code', 'Paano-code'),
    ('PAANO', 'PANO'), ('CC 4', 'CC 5'), ('grade 4', 'grade 5'),
    ('pano ko kukunin?', 'Paano ko kukunin?'), ('Pano ko kukunin?', 'Paano ko kuhanin?'),
])
def test_other_words_codes_grades_and_case_stay_literal(original, quoted):
    assert quote_matches(original, quoted) == []
