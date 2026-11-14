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


@pytest.mark.parametrize('transform', [lambda x, y: (x, y), rotate(4)], ids=['flat', 'tilt'])
def test_padded_boxes_taller_than_the_row_pitch_still_line_up(transform):
    # OCR pads boxes: on the simulated perspective photo boxes were 29 px tall with rows 24 px apart.
    assert texts(group_lines(page_words(transform, row_gap=16))) == ROWS


def test_words_come_back_in_reading_order_whatever_the_input_order():
    words = page_words(rotate(5))
    assert texts(group_lines(list(reversed(words)))) == ROWS


def test_tilt_beyond_the_verified_envelope_is_refused_not_guessed():
    # Simulated photos verify tilts up to MAX_TILT_DEGREES; a steeper page is refused rather than trusted.
    with pytest.raises(RowsUncertain):
        group_lines(page_words(rotate(12)))


def test_a_mark_floating_between_two_rows_is_attached_to_neither():
    # Revised 24 Oct after the simulated-photo measurement: a word clearly on no line starts its own line, so it
    # is reported as an unmatched line and never joins the wrong row; the row it left shows no mark.
    words = page_words(lambda x, y: (x, y))
    stray = Word('2.00', ((520, 117), (564, 117), (564, 135), (520, 135)), 0.99)  # halfway between rows 0 and 1
    lines = texts(group_lines(words + [stray]))
    assert ['2.00'] in lines and all('2.00' not in line for line in lines if len(line) > 1)


def test_a_word_partly_on_two_rows_is_refused():
    words = page_words(lambda x, y: (x, y), row_gap=24)
    straddle = Word('2.00', ((520, 112), (564, 112), (564, 130), (520, 130)), 0.99)  # 12 px from rows 0 and 1
    with pytest.raises(RowsUncertain):
        group_lines(words + [straddle])


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
    result = photo_grade_rows(words, CATALOG, program_id='bscs', curriculum_id='bscs-2018')
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


def test_a_word_nearer_one_row_but_almost_as_near_the_next_is_refused():
    # Rows 22 px apart, words 18 px tall: this mark is 7 px from row 0 and 15 px from row 1 (margin under 9 px).
    words = page_words(lambda x, y: (x, y), row_gap=22)
    close = Word('2.00', ((520, 107), (564, 107), (564, 125), (520, 125)), 0.99)
    with pytest.raises(RowsUncertain):
        group_lines(words + [close])


def label_between_rows(text='SEMESTER', top=125):
    """A Report-of-Grades semester label, vertically centred on its block, so it sits between two rows."""
    return Word(text, ((8, top), (48, top), (48, top + 18), (8, top + 18)), 0.99)


def test_an_ambiguous_word_that_is_not_critical_is_dropped_not_guessed():
    # Row centres 109 and 143; the label's centre is 122 (13 px and 21 px away): placeable on neither.
    words = page_words(lambda x, y: (x, y)) + [label_between_rows(top=113)]
    lines = group_lines(words, critical=lambda w: w.text != 'SEMESTER')
    assert texts(lines) == ROWS


def test_an_ambiguous_critical_word_still_refuses():
    words = page_words(lambda x, y: (x, y)) + [label_between_rows('1.75', top=113)]
    with pytest.raises(RowsUncertain):
        group_lines(words, critical=lambda w: True)


def test_semester_labels_between_rows_do_not_block_grade_rows():
    words = table_words([ROW_CC5, ROW_GEC]) + [label_between_rows('2023-2024', top=152)]
    rows, _ = grade_rows(words)
    assert rows == [('CC 5/L', ('cc-105',), ('1.75',)), ('GEC 1', ('gec-1',), ('2.00',))]


def test_a_grade_near_two_rows_still_refuses_the_photo():
    # Row centres 143 and 177; this grade's centre is 156 (13 px and 21 px away): not clearly on either.
    words = table_words([ROW_CC5, ROW_GEC]) + [Word('2.25', ((600, 147), (640, 147), (640, 165), (600, 165)), 0.99)]
    with pytest.raises(RowsUncertain):
        grade_rows(words)


def test_an_unplaceable_final_header_refuses_instead_of_showing_every_number():
    # Two-line header: FINAL sits between the header lines, so dropping it would fall back to showing units and
    # midterm as marks.
    top = [(60, 'COURSE'), (200, 'TITLE'), (420, 'UNIT'), (500, 'MIDTERM'), (660, 'RE-EX'), (740, 'REMARKS')]
    words = table_words([[(60, 'CODE')], ROW_CC5], header=top) + [
        Word('FINAL', ((580, 113), (630, 113), (630, 131), (580, 131)), 0.99)]  # 13 px and 21 px from the lines
    with pytest.raises(RowsUncertain):
        grade_rows(words)


def test_tiny_row_number_boxes_do_not_steer_their_line():
    # A row-number box is a few pixels wide, so its own slope is noise; on a tilted page it must not decide
    # where the course code 100 px to its right is expected.
    transform = rotate(5)
    words = page_words(transform)
    for r in range(len(ROWS)):
        top = 100 + r * 34
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = [transform(x, y) for x, y in
                                                  ((20, top), (28, top), (28, top + 18), (20, top + 18))]
        words.append(Word(str(r + 1), ((x0, y0), (x1, y1 - 2.5), (x2, y2 - 2.5), (x3, y3)), 0.99))  # slope noise
    lines = group_lines(words, critical=lambda w: not w.text.isdigit())
    assert [line[1:] for line in texts(lines)] == ROWS and [line[0] for line in texts(lines)] == ['1', '2', '3', '4', '5']


@pytest.mark.xfail(strict=True, reason='known 24.1 limit (24 Oct): a far-left student-panel label bends a sparse row; '
                   'the real Report of Grades screenshot is refused for this reason')
def test_a_far_left_panel_label_does_not_bend_a_sparse_row():
    # Real screenshot: a student-panel label sits at the far left, 7 px off a table row, and joins it. With only a
    # code before the long gap to the grade, a line fitted through the label and the code is tilted by noise and
    # the grade 500 px on looks off the row.
    sparse = [(60, 'CC 5/L'), (580, '1.75')]
    words = table_words([sparse], row_gap=22) + [
        Word('MAJOR STUDY:', ((-300, 129), (-200, 129), (-200, 147), (-300, 147)), 0.99)]
    rows, _ = grade_rows(words)
    assert rows == [('CC 5/L', ('cc-105',), ('1.75',))]


@pytest.mark.xfail(strict=True, reason='known 24.1 limit (24 Oct): rows tighter than their OCR boxes (real Report of '
                   'Grades screenshot: 21 px boxes, 18 px rows) make a few pixels of jitter look ambiguous; refused')
def test_rows_tighter_than_their_boxes_tolerate_small_centre_jitter():
    # Real Report of Grades screenshot: boxes 21 px tall, rows 18 px apart, box centres jitter by a few pixels.
    # Distances must be judged against the row pitch, not the (padded) box height.
    words = []
    for r, texts_ in enumerate(ROWS):
        top = 100 + r * 18
        for c, ((left, _), text) in enumerate(zip(CELLS, texts_)):
            jitter = 4 if (r + c) % 2 else -2
            box = ((left, top + jitter), (left + 11 * len(text), top + jitter),
                   (left + 11 * len(text), top + jitter + 21), (left, top + jitter + 21))
            words.append(Word(text, box, 0.99))
    assert texts(group_lines(words)) == ROWS
