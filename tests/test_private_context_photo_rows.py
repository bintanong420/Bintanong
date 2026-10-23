"""Phase 11 / 24.1: rebuild text lines from OCR word boxes on tilted or perspective photos, and refuse
instead of guessing when a word could belong to two lines. Synthetic boxes only (no OCR, no real report)."""
import math

import pytest

from backend.bintanong_private_context.photo_rows import Word, RowsUncertain, group_lines

# A synthetic grade table: five rows, four cells each, the far-right cell 600 px from the first.
CELLS = [(60, 'CC 1/L'), (200, 'Introduction'), (520, '1.75'), (660, 'Passed')]
ROWS = [[f'{text}{r}' if i == 1 else text for i, (_, text) in enumerate(CELLS)] for r in range(5)]


def page_words(transform, *, row_gap=34, height=18):
    """Words of the synthetic table, each box's corners passed through `transform` (x, y) -> (x, y)."""
    words = []
    for r, texts in enumerate(ROWS):
        top = 100 + r * row_gap
        for (left, _), text in zip(CELLS, texts):
            width = 11 * len(text)
            corners = [(left, top), (left + width, top), (left + width, top + height), (left, top + height)]
            words.append(Word(text, tuple(transform(x, y) for x, y in corners), 0.99))
    return words


def rotate(degrees, cx=400, cy=200):
    a = math.radians(degrees)
    return lambda x, y: (cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a),
                         cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a))


def perspective(k=0.0006):
    """Keystone: rows fan out, so each line has its own slope (no single page angle fits)."""
    return lambda x, y: (x, y + k * (x - 400) * (y - 200))


def texts(lines):
    return [[w.text for w in line] for line in lines]


@pytest.mark.parametrize('transform', [lambda x, y: (x, y), rotate(5), rotate(-4), perspective()],
                         ids=['flat', 'tilt+5', 'tilt-4', 'keystone'])
def test_lines_follow_the_printed_rows(transform):
    assert texts(group_lines(page_words(transform))) == ROWS


def test_words_come_back_in_reading_order_whatever_the_input_order():
    words = page_words(rotate(5))
    assert texts(group_lines(list(reversed(words)))) == ROWS


def test_tilt_beyond_the_verified_envelope_is_refused_not_guessed():
    # Simulated photos verify tilts up to MAX_TILT_DEGREES; a steeper page is refused rather than trusted.
    with pytest.raises(RowsUncertain):
        group_lines(page_words(rotate(12)))


def test_a_word_sitting_between_two_rows_is_refused():
    words = page_words(lambda x, y: (x, y))
    stray = Word('2.00', ((520, 117), (564, 117), (564, 135), (520, 135)), 0.99)  # halfway between rows 0 and 1
    with pytest.raises(RowsUncertain):
        group_lines(words + [stray])


def test_no_words_means_no_lines():
    assert group_lines([]) == []


def test_a_word_just_off_the_last_row_is_refused():
    # Last row's centre is y=245; this mark sits 13 px below it (more than half a word height, less than one),
    # so it is neither on that row nor clearly a new one.
    words = page_words(lambda x, y: (x, y))
    stray = Word('3.00', ((520, 249), (564, 249), (564, 267), (520, 267)), 0.99)
    with pytest.raises(RowsUncertain):
        group_lines(words + [stray])


# --- 8b: grade rows from lines. Header mode reads only the FINAL column (rows also print units and midterm).
from backend.bintanong_private_context.photo_rows import photo_grade_rows  # noqa: E402
from test_private_context_grades import CATALOG  # noqa: E402

HEADER = [(60, 'CODE'), (200, 'TITLE'), (420, 'UNIT'), (500, 'MIDTERM'), (580, 'FINAL'), (660, 'RE-EX'),
          (740, 'REMARKS')]


def table_words(rows, transform=lambda x, y: (x, y), header=HEADER, row_gap=34):
    words, lines = [], [header] + rows
    for r, cells in enumerate(lines):
        top = 100 + r * row_gap
        for left, text in cells:
            width = 10 * len(text)
            corners = [(left, top), (left + width, top), (left + width, top + 18), (left, top + 18)]
            words.append(Word(text, tuple(transform(x, y) for x, y in corners), 0.99))
    return words


def grade_rows(words):
    result = photo_grade_rows(group_lines(words), CATALOG, program_id='bscs', curriculum_id='bscs-2018')
    return [(r.code_text, r.candidates, r.marks) for r in result.rows], result.unmatched_lines


ROW_CC5 = [(60, 'CC 5/L'), (200, 'Info'), (420, '3.0'), (500, '1.50'), (580, '1.75'), (740, 'Passed')]
ROW_GEC = [(60, 'GEC 1'), (200, 'Self'), (420, '3.0'), (580, '2.00'), (740, 'Passed')]


@pytest.mark.parametrize('transform', [lambda x, y: (x, y), rotate(5), perspective()], ids=['flat', 'tilt', 'keystone'])
def test_header_mode_reads_only_the_final_column(transform):
    rows, unmatched = grade_rows(table_words([ROW_CC5, ROW_GEC], transform))
    assert rows == [('CC 5/L', ('cc-105',), ('1.75',)), ('GEC 1', ('gec-1',), ('2.00',))]
    assert unmatched == 0


def test_empty_final_cell_shows_no_mark():
    rows, _ = grade_rows(table_words([[(60, 'CC 5/L'), (200, 'Info'), (420, '3.0'), (500, '1.50')]]))
    assert rows == [('CC 5/L', ('cc-105',), ())]


def test_a_value_on_the_edge_of_the_final_column_is_refused():
    # Header centres: MIDTERM 535, FINAL 605, so the column boundary is 570; this word's centre is 570.
    edge = [(60, 'CC 5/L'), (200, 'Info'), (550, '1.75')]
    with pytest.raises(RowsUncertain):
        grade_rows(table_words([edge]))


def test_without_a_final_header_all_marks_after_the_code_are_shown():
    plain = [[(60, 'CC 5/L'), (200, 'Info'), (520, '1.75')]]
    rows, _ = grade_rows(table_words(plain, header=[(60, 'Subject'), (520, 'Grade')]))
    assert rows == [('CC 5/L', ('cc-105',), ('1.75',))]


def test_unknown_code_lines_with_marks_are_counted_never_matched():
    rows, unmatched = grade_rows(table_words([ROW_CC5, [(60, 'XYZ 9'), (200, 'Other'), (580, '1.25')]]))
    assert [r[0] for r in rows] == ['CC 5/L'] and unmatched == 1


def test_two_values_inside_the_final_column_are_refused():
    crowded = [(60, 'CC 5/L'), (200, 'Info'), (585, '1.75'), (615, '2.0')]  # centres 605 and 630, both in FINAL
    with pytest.raises(RowsUncertain):
        grade_rows(table_words([crowded]))
