"""24.1 grade-row scorer: the Q11 strict gates adapted to private grade photos (no missing or invented row, exact
marks, zero silent errors). A refused photo is safe but counts as not supported."""
from backend.bintanong_private_context.grades import ExtractionResult, GradeRow
from backend.bintanong_tools.ocr_bench.grade_rows import score_document, verdict

TRUTH = (('CC 5/L', '1.75'), ('GEC 1', '2.00'), ('NSTP 1', None))


def result(*rows, unmatched=0):
    return ExtractionResult('bscs', 'bscs-2018', tuple(
        GradeRow(f'row-1-{i}', code, (code.lower(),), marks, 1) for i, (code, marks) in enumerate(rows, 1)), unmatched)


def test_exact_document():
    report = score_document(TRUTH, result(('CC 5/L', ('1.75',)), ('GEC 1', ('2.00',)), ('NSTP 1', ())))
    assert report == dict(refused=None, exact=3, wrong_mark=0, invented=0, missing=0, unmatched_lines=0)


def test_wrong_mark_is_a_silent_error():
    report = score_document(TRUTH, result(('CC 5/L', ('2.00',)), ('GEC 1', ('2.00',)), ('NSTP 1', ())))
    assert report['wrong_mark'] == 1 and report['exact'] == 2


def test_extra_mark_shown_beside_the_right_one_is_still_wrong():
    report = score_document(TRUTH, result(('CC 5/L', ('3.0', '1.75')), ('GEC 1', ('2.00',)), ('NSTP 1', ())))
    assert report['wrong_mark'] == 1


def test_row_for_a_course_not_on_the_page_is_invented():
    report = score_document(TRUTH, result(('CC 5/L', ('1.75',)), ('GEC 1', ('2.00',)), ('NSTP 1', ()),
                                          ('PE 1', ('1.00',))))
    assert report['invented'] == 1


def test_duplicate_row_for_one_course_counts_as_invented():
    report = score_document(TRUTH, result(('CC 5/L', ('1.75',)), ('CC 5/L', ('1.75',)), ('GEC 1', ('2.00',)),
                                          ('NSTP 1', ())))
    assert report['invented'] == 1 and report['exact'] == 3


def test_missing_rows_are_counted():
    report = score_document(TRUTH, result(('CC 5/L', ('1.75',)), unmatched=2))
    assert report['missing'] == 2 and report['unmatched_lines'] == 2


def test_refused_document_has_every_row_missing_but_no_silent_error():
    report = score_document(TRUTH, 'word_between_lines')
    assert report == dict(refused='word_between_lines', exact=0, wrong_mark=0, invented=0, missing=3,
                          unmatched_lines=0)


def test_verdict_needs_every_document_exact():
    exact = score_document(TRUTH, result(('CC 5/L', ('1.75',)), ('GEC 1', ('2.00',)), ('NSTP 1', ())))
    refused = score_document(TRUTH, 'word_between_lines')
    wrong = score_document(TRUTH, result(('CC 5/L', ('2.00',)), ('GEC 1', ('2.00',)), ('NSTP 1', ())))
    assert verdict([exact, exact]) == dict(documents=2, refused=0, silent_errors=0, missing=0, supported=True)
    assert verdict([exact, refused]) == dict(documents=2, refused=1, silent_errors=0, missing=3, supported=False)
    assert verdict([exact, wrong])['silent_errors'] == 1 and verdict([exact, wrong])['supported'] is False
