"""Master 15.1/15 deliverable: the private-file parser runs as a transient, bounded child job."""
import os
import time

import pytest

from backend.bintanong_private_context.grades import extract_grade_rows
from backend.bintanong_private_context.uploads import UploadRejected, validate_upload
from backend.bintanong_private_context.worker import extract_isolated, run_isolated
from test_private_context_grades import CATALOG
from test_private_context_isolation import pdf_with


def slow(seconds):
    time.sleep(seconds)
    return 'late'


def crash():
    os._exit(7)


def fail():
    raise UploadRejected('no_text_layer')


def test_isolated_extraction_returns_the_same_rows_as_in_process():
    data = pdf_with('Programming')
    scope = dict(program_id='bscs', curriculum_id='bscs-2018')
    expected = extract_grade_rows(validate_upload(data), CATALOG, **scope)
    assert extract_isolated(data, CATALOG, timeout=60, **scope) == expected


def test_isolated_extraction_validates_the_raw_bytes_inside_the_job():
    with pytest.raises(UploadRejected) as error:
        extract_isolated(b'%PDF-1.7 truncated', CATALOG, timeout=60, program_id='bscs', curriculum_id='bscs-2018')
    assert error.value.reason == 'unreadable'


def test_a_job_past_its_time_limit_is_killed_and_refused():
    start = time.monotonic()
    with pytest.raises(UploadRejected) as error:
        run_isolated(slow, 30, timeout=3)
    assert error.value.reason == 'parse_timeout' and time.monotonic() - start < 25


def test_a_crashing_parser_only_kills_its_child_job():
    with pytest.raises(UploadRejected) as error:
        run_isolated(crash, timeout=30)
    assert error.value.reason == 'unreadable'


def test_a_refusal_inside_the_job_keeps_its_reason():
    with pytest.raises(UploadRejected) as error:
        run_isolated(fail, timeout=30)
    assert error.value.reason == 'no_text_layer'
