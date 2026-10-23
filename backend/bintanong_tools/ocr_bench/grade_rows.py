"""Grade-row scorer for private grade photos (24.1): the Q11 strict gates adapted to rows.

Per document: every printed row found once with exactly its mark, no row invented, no silent error. A refused
photo is safe (nothing wrong reaches the student) but every row is missing, so it is never "supported".
"""
from __future__ import annotations


def score_document(truth, outcome) -> dict:
    """truth: ((course ids, marks the student should see), ...), keyed like `GradeRow.candidates` so a printed
    spacing variant of the same reviewed course still matches; outcome: an ExtractionResult or a refusal reason."""
    if isinstance(outcome, str):
        return dict(refused=outcome, exact=0, wrong_mark=0, invented=0, missing=len(truth), unmatched_lines=0)
    expected = {tuple(key): tuple(marks) for key, marks in truth}
    exact = wrong = invented = 0
    seen = set()
    for row in outcome.rows:
        if row.candidates not in expected or row.candidates in seen:
            invented += 1
            continue
        seen.add(row.candidates)
        if row.marks == expected[row.candidates]:
            exact += 1
        else:
            wrong += 1
    return dict(refused=None, exact=exact, wrong_mark=wrong, invented=invented, missing=len(expected) - len(seen),
                unmatched_lines=outcome.unmatched_lines)


def verdict(reports) -> dict:
    refused = sum(r['refused'] is not None for r in reports)
    silent = sum(r['wrong_mark'] + r['invented'] for r in reports)
    missing = sum(r['missing'] for r in reports)
    return dict(documents=len(reports), refused=refused, silent_errors=silent, missing=missing,
                supported=bool(reports) and refused == 0 and silent == 0 and missing == 0)
