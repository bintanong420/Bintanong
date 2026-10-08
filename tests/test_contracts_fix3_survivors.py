"""Phase 1 Task 3, fix pass 3, L-f: one test per mutant the re-check found surviving, plus the vocabulary additions.

Each test below fails against the mutant it names (see the mutation log in the decision record)."""

from __future__ import annotations

import calendar
import re
from datetime import date

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import base, governance as gov, runtime
import test_source_governance_manifests as tl


# 1. governance._date_span: month end taken as 28
@pytest.mark.parametrize("year", [2023, 2024, 1900, 2000])
def test_date_span_ends_on_the_real_last_day_of_each_month(year):
    for month in range(1, 13):
        first, last = gov._date_span(f"{year}-{month:02d}")
        assert first == date(year, month, 1)
        assert last == date(year, month, calendar.monthrange(year, month)[1])
    assert gov._date_span(str(year)) == (date(year, 1, 1), date(year, 12, 31))
    assert gov._date_span(f"{year}-07-04") == (date(year, 7, 4), date(year, 7, 4))


def test_date_span_leaves_other_formats_and_impossible_dates_alone():
    assert gov._date_span("soon") is None and gov._date_span(None) is None and gov._date_span("2023-02-30") is None
    assert gov._date_span("2023-1-01") is None and gov._date_span("2023-13") is None


# 2. governance._effectivity_errors: b[1] < a[0] became b[0] < a[0]
def test_a_partial_end_date_is_judged_by_its_last_possible_day():
    def effective(a, b):
        return tl.mutated(tl.register()[1], lambda r: (
            r["evidence"].append(tl.ev("ev-d", "printed_text_span", "researcher")),
            r["effective_from"].update(value=a, state="observed", evidence_ref="ev-d", basis="printed_text"),
            r["effective_to"].update(value=b, state="observed", evidence_ref="ev-d", basis="printed_text")))

    gov.SourceDocumentVersion.parse(effective("2023-06-15", "2023-06"))          # the month still has days to come
    gov.SourceDocumentVersion.parse(effective("2023-06-15", "2023-06-15"))       # one day
    gov.SourceDocumentVersion.parse(effective("2023-06-30", "2023-06"))          # the month's last day
    gov.SourceDocumentVersion.parse(effective("2024-02-29", "2024-02"))          # leap year
    for a, b in (("2023-06-15", "2023-06-14"), ("2023-07", "2023-06"), ("2024-03-01", "2024-02")):
        with pytest.raises(ValidationError, match="effective_to is before effective_from"):
            gov.SourceDocumentVersion.parse(effective(a, b))


# 3. base.id_pattern: body '+' became '*'
@pytest.mark.parametrize("prefix", ["doc-", "ver-", "edition-", "conflict-", "fact-", "sess-"])
def test_an_id_needs_a_body_after_its_prefix(prefix):
    pattern = base.id_pattern(prefix)
    assert re.fullmatch(pattern.strip("^$"), prefix) is None
    assert re.fullmatch(pattern.strip("^$"), prefix + "x") is not None
    assert base.namespace_of(prefix) is None
    assert base.namespace_of(prefix + "x1") is not None


def test_a_register_refuses_an_id_with_no_body():
    rec = tl.mutated(tl.register()[1], lambda r: r.__setitem__("document_id", "doc-"))
    with pytest.raises(ValidationError, match="String should match pattern '\\^doc\\\\\\-\\[a\\-z0\\-9\\-\\]\\+\\$"):
        gov.SourceDocumentVersion.parse(rec)


# 4. source.span_identity ignoring the text is covered in test_contracts_fix3_chunks.py

# 5. runtime._TIME_PHRASES lookbehind removed
@pytest.mark.parametrize("text", ["thislast year", "o'last year", "last 2last year", "elast year", "9last year"])
def test_a_time_phrase_must_start_at_a_word_boundary(text):
    assert runtime.time_phrases(text) == set()


def test_a_time_phrase_is_found_between_boundaries():
    assert runtime.time_phrases("Enrolled last year, again.") == {"last year"}
    assert runtime.time_phrases("(next semester)") == {"next semester"}
    assert runtime.time_phrases("last year's grades") == set()      # a possessive is another word
    assert runtime.time_phrases("last years") == set()
    assert runtime.time_phrases("ilast year") == set()


def test_a_word_that_merely_ends_in_a_time_phrase_is_not_one():
    assert runtime.time_phrases("blast year") == set()
    assert runtime.time_phrases("forecast year") == set()
    assert runtime.time_phrases("outlast year") == set()


# 6. base._strings: mapping keys were not scanned
def test_mapping_keys_are_scanned_for_foreign_ids():
    assert base.foreign_ids({"fact-synth-0001": 1}, "institutional")
    assert base.foreign_ids({"x": {"y": {"sess-synth-0002": []}}}, "institutional")
    assert list(base._strings({"k1": ["v1"], "k2": {"k3": "v3"}})) == ["k1", "v1", "k2", "k3", "v3"]


def test_the_test_local_checker_scans_keys_too():
    assert list(tl._strings({"k1": ["v1"], "k2": {"k3": "v3"}})) == ["k1", "v1", "k2", "k3", "v3"]


# the vocabulary additions (owner-reviewable)
@pytest.mark.parametrize("text,found", [("nothing can be enrolled", {"nothing"}), ("Nobody passed", {"nobody"}),
                                        ("none of them", {"none"}), ("no, never", {"no", "never"})])
def test_the_negation_vocabulary_covers_nothing_nobody_and_none(text, found):
    assert runtime.negation_tokens(text) == found


def test_dropping_nobody_in_normalization_is_refused():
    q = {"schema_version": "bintanong-normalized-query-v1", "original_text": "Nobody enrolled last year",
         "normalized_text": "somebody enrolled last year", "language_hints": ["en"], "intent": None, "entities": [],
         "ambiguities": [], "negations": [], "time_qualifiers": [], "session_fact_refs": []}
    with pytest.raises(ValidationError, match="dropped the negation 'nobody'"):
        runtime.NormalizedQuery.parse(q)
    runtime.NormalizedQuery.parse({**q, "normalized_text": "nobody enrolled last year"})


def test_the_abbreviation_no_is_a_known_false_positive():
    # "Course No. 101" is read as a negation; a normalizer that expands it to "Number" is refused. Fail-safe,
    # reported to the owner, not special-cased here.
    assert runtime.negation_tokens("Course No. 101") == {"no"}
