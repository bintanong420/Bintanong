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
