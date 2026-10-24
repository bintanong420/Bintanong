"""Owner, 25 Oct 2026 (step 2 item g, "host-written"): a grading-scale question gets one host-written reply
in every language from the owner-approved reading of the 2021 Student Handbook, physical p.46, "2.2
UNDERGRADUATE LEVEL/SCHOOL OF LAW" (every row; generalised, no college caveat). The release holds only the
1.0 row as a reviewed chunk and published releases are immutable, so the rows live here; the reply is given
only when a retrieved card cites that Handbook version and page, and that card is the citation."""
import re

SUBJECT = 'grading_scale'
TABLE_PAGE = ('ver-4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8', 46)
# (grade, percentage equivalent or None, descriptive rating), in printed order.
ROWS = (('1.0', '98-100', 'Excellent'), ('1.25', '95-97', 'Excellent'), ('1.5', '92-94', 'Highly Satisfactory'),
        ('1.75', '89-91', 'Highly Satisfactory'), ('2.0', '86-88', 'Satisfactory'), ('2.25', '83-85', 'Satisfactory'),
        ('2.5', '80-82', 'Fairly Satisfactory'), ('2.75', '77-79', 'Fairly Satisfactory'), ('3.0', '75-76', 'Passed'),
        ('4.0', None, 'Condition'), ('Inc.', None, 'Incomplete'), ('IP', None, 'In progress'), ('5.0', None, 'Failed'),
        ('NC', None, 'No credit'), ('OD', None, 'Officially Dropped'), ('UD', None, 'Unofficially Dropped'),
        ('W', None, 'Withdrawn'), ('V', None, 'Validated'))
MAX_ROWS = 4

PASSING = re.compile(r'\b(?:pass|passing|passed|pasado\w*|pumasa|papasa|makapasa)\b', re.I)
PERCENT = re.compile(r'(?<![\d.])(\d{2,3})(?![\d.])')

_TEXT = {
 'en': dict(row='{grade} is "{rating}" in the printed undergraduate grading system.',
            passing='The printed passing grade is {grade}, rated "Passed".',
            below='{condition} is "Condition" and {failed} is "Failed".',
            grades='The printed undergraduate grades are: {rows}.', marks='Other printed marks: {rows}.'),
 'fil': dict(row='Sa naka-print na undergraduate grading system, ang {grade} ay "{rating}".',
             passing='Ang naka-print na passing grade ay {grade}, na "Passed".',
             below='Ang {condition} ay "Condition" at ang {failed} ay "Failed".',
             grades='Ang mga naka-print na undergraduate grade ay: {rows}.', marks='Iba pang naka-print na marka: {rows}.'),
 'taglish': dict(row='Sa printed undergraduate grading system, ang {grade} ay "{rating}".',
                 passing='Ang printed passing grade ay {grade}, na "Passed".',
                 below='Ang {condition} ay "Condition" at ang {failed} ay "Failed".',
                 grades='Ang printed undergraduate grades ay: {rows}.', marks='Yung other printed marks: {rows}.')}


def _label(row):
    grade, percent, _ = row
    return f'{grade} ({percent})' if percent else grade


def _mentioned(row, text):
    grade = row[0]
    if re.fullmatch(r'\d\.\d+', grade):
        return re.search(r'(?<![\d.])' + re.escape(grade) + r'0*(?![\d.])', text) is not None
    if grade.endswith('.'):  # "Inc." is also typed INC / inc
        return re.search(r'\b' + re.escape(grade[:-1]) + r'\b', text, re.I) is not None
    return re.search(r'\b' + re.escape(grade) + r'\b', text) is not None  # IP, NC, W, V: as printed only


def _in_range(row, number):
    if not row[1]:
        return False
    low, high = (int(n) for n in row[1].split('-'))
    return low <= number <= high


def _rated(rating):
    return next((r for r in ROWS if r[2] == rating), None)


def _claims(text, words):
    numbers = [int(n) for n in PERCENT.findall(text)]
    named = [r for r in ROWS if _mentioned(r, text) or any(_in_range(r, n) for n in numbers)][:MAX_ROWS]
    if named:
        return tuple(words['row'].format(grade=_label(r), rating=r[2]) for r in named)
    passed, condition, failed = (_rated(r) for r in ('Passed', 'Condition', 'Failed'))
    if PASSING.search(text) and passed and condition and failed:
        return (words['passing'].format(grade=_label(passed)),
                words['below'].format(condition=condition[0], failed=failed[0]))
    listed = '; '.join(f'{_label(r)} {r[2]}' for r in ROWS if r[1])
    others = '; '.join(f'{r[0]} {r[2]}' for r in ROWS if not r[1])
    return tuple(t for t in (listed and words['grades'].format(rows=listed),
                             others and words['marks'].format(rows=others)) if t)


def _table_card(pack):
    version, page = TABLE_PAGE
    return next((c for c in pack.cards if c.kind == 'document'
                 and any((x.version_id, x.page) == (version, page) for x in c.citations)), None)


def grade_claims(pack):
    """{part_id: ((text, evidence_id), ...)} for each grading-scale document part when a retrieved card cites
    the reviewed table page; empty otherwise (the model then explains the part as before)."""
    parts = [p for p in (pack.understanding.parts if pack.understanding else ())
             if p.evidence_need == 'document' and p.subject_id == SUBJECT]
    card = _table_card(pack) if parts and pack.language in _TEXT else None
    if card is None:
        return {}
    return {p.part_id: tuple((t, card.evidence_id) for t in _claims(p.text, _TEXT[pack.language])) for p in parts}
