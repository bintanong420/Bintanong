"""A Taglish reply may carry a printed sentence verbatim in English (owner 30 Oct 2026: "we keep the answers that
came from the data as english as is ... the connecting as filipino").

Regression 30 Oct 2026 (probation-tagalog): three Taglish claims and one verbatim printed INC provision; the style
check rejected the quoted provision twice and the answer was withheld."""
from backend.bintanong_generation import part_answers
from test_generation_condition_connectives import draft, pack_with

PRINTED = ('Grades of "Inc" for valid reasons shall not be counted against the students; provided, that the '
           'documents are submitted to the fictional Office V before registration.')
TAGLISH = 'Ang probation ay pwedeng maalis kapag pumasa ka sa more than 50% of the units.'


def test_a_verbatim_printed_sentence_among_taglish_claims_is_in_style():
    pack = pack_with(PRINTED, language='taglish')
    quoted = ('Grades of “Inc” for valid reasons shall not be counted against the students, provided that the '
              'documents are submitted to the fictional Office V before registration.')
    assert part_answers.style_errors(draft(pack, TAGLISH, quoted), pack) == ()


def test_an_english_paraphrase_is_still_out_of_style():
    pack = pack_with(PRINTED, language='taglish')
    paraphrase = 'Valid-reason Inc grades do not count if the documents reach Office V before registration.'
    assert part_answers.style_errors(draft(pack, TAGLISH, paraphrase), pack) == ('claim_not_in_requested_style',)


def test_a_reply_made_only_of_printed_english_is_still_out_of_style():
    pack = pack_with(PRINTED, language='taglish')
    assert part_answers.style_errors(draft(pack, PRINTED), pack) == ('claim_not_in_requested_style',)


def test_only_the_claims_own_sources_count_as_printed():
    pack = pack_with('Fictional unrelated record.', PRINTED, language='taglish')
    first = pack.cards[0].evidence_id
    assert part_answers.style_errors(draft(pack, TAGLISH, PRINTED, cited=[first]), pack) == (
        'claim_not_in_requested_style',)
