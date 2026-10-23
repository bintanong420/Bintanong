"""Text lines from OCR word boxes on photos (24.1): follow each printed row's own slope, refuse when unsure.

The Phase 10 probe grouped words by vertical centre, which silently attached grades to the wrong course on
tilted and perspective photos. Here each line is chained left to right along its fitted baseline, so a
keystone page (every row with its own slope) still lines up. A word that sits near two lines, or near a line
without being on it, refuses the whole page: a refused photo is safe; a wrong row is not.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass

MAX_TILT_DEGREES = 8.0   # the envelope verified on simulated photos
ON_LINE = 0.5            # a word belongs to a line within half a word height of its fitted baseline
NEAR_LINE = 1.0          # ... and must be clearly away (one word height) from every other line


class RowsUncertain(ValueError):
    """The page cannot be split into rows without guessing."""


@dataclass(frozen=True)
class Word:
    text: str
    box: tuple[tuple[float, float], ...]  # top-left, top-right, bottom-right, bottom-left
    score: float

    @property
    def center(self) -> tuple[float, float]:
        return (sum(p[0] for p in self.box) / 4, sum(p[1] for p in self.box) / 4)

    @property
    def height(self) -> float:
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = self.box
        return (math.dist((x0, y0), (x3, y3)) + math.dist((x1, y1), (x2, y2))) / 2

    @property
    def slope(self) -> float:
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = self.box
        dx = (x1 - x0) + (x2 - x3)
        return ((y1 - y0) + (y2 - y3)) / dx if dx else 0.0


class _Line:
    def __init__(self, word: Word):
        self.words = [word]

    def predict(self, x: float) -> float:
        points = [w.center for w in self.words]
        if len(points) == 1:
            (cx, cy), slope = points[0], self.words[0].slope
        else:
            mx = statistics.fmean(p[0] for p in points)
            my = statistics.fmean(p[1] for p in points)
            spread = sum((p[0] - mx) ** 2 for p in points)
            slope = sum((p[0] - mx) * (p[1] - my) for p in points) / spread if spread else self.words[0].slope
            cx, cy = mx, my
        return cy + slope * (x - cx)


def group_lines(words: list[Word]) -> list[list[Word]]:
    """Lines in reading order (top to bottom), each left to right; raises RowsUncertain instead of guessing."""
    if not words:
        return []
    tilt = math.degrees(math.atan(statistics.median(w.slope for w in words)))
    if abs(tilt) > MAX_TILT_DEGREES:
        raise RowsUncertain('tilt_beyond_envelope')
    height = statistics.median(w.height for w in words)
    lines: list[_Line] = []
    for word in sorted(words, key=lambda w: w.center[0]):
        x, y = word.center
        residuals = sorted((abs(line.predict(x) - y), i) for i, line in enumerate(lines))
        if not residuals or residuals[0][0] > NEAR_LINE * height:
            lines.append(_Line(word))  # clearly on no existing line: a new row starts here
            continue
        best, index = residuals[0]
        if best > ON_LINE * height:
            raise RowsUncertain('word_between_lines')
        if len(residuals) > 1 and residuals[1][0] <= NEAR_LINE * height:
            raise RowsUncertain('word_near_two_lines')
        lines[index].words.append(word)
    middle = statistics.median(w.center[0] for w in words)
    return [sorted(line.words, key=lambda w: w.center[0])
            for line in sorted(lines, key=lambda line: line.predict(middle))]
