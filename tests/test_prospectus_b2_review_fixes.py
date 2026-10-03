"""Regression tests for the two independent reviews of Phase B2 (verifier, fix proposals, ledger)."""

import copy
import os
import subprocess
import sys
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor.fixes import propose_fixes, strip_banner
from backend.bintanong_tools.prospectus_extractor.sheet import (
    build_entries, candidate_sha256, parse_sheet, render_sheet,
)
from backend.bintanong_tools.prospectus_extractor.text import leading_banner
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate

import fixer_fixtures as fx
from fixer_fixtures import by_code, kinds, section
from sheet_helpers import set_line

HASH = "a" * 64


def set_cell_text(payload, cell_id, text):
    for course in payload["courses"]:
        for c in course["provenance"]["source_cells"]:
            if c["cell_id"] == cell_id:
                c["text"] = text


# --- commit A, item 1: a move_term proposal must never leave the section clean

def test_item1_a_banner_naming_another_term_flags_the_course_and_blocks_bulk_confirm():
    payload = copy.deepcopy(fx.bscs())
    set_cell_text(payload, "t0-c9", "SECOND SEMESTER Discrete Structures 1 1")
    v = verify_candidate(payload)
    row = by_code(payload, v)["CS 1"]
    assert [f.kind for f in row.fixes and row.flags if f.kind == "term_mismatch"] == ["term_mismatch"]
    assert [fix.kind for _l, fix in row.fixes] == ["move_term"]
    assert section(v, "S1").health != "clean"
    identity = {"pdf_sha256": HASH, "candidate_sha256": candidate_sha256(payload)}
    text = set_line(render_sheet(payload, v, identity), "S1", "confirm", "yes")
    entries, errors = build_entries(parse_sheet(text), payload, v, reviewer="N", pdf_sha256=HASH)
    assert entries == [] and any("S1-01" in e and "flagged" in e for e in errors)


# --- commit A, item 2 and 3: banner units

def test_item2_an_abbreviated_semester_banner_is_stripped_with_its_full_stop():
    assert strip_banner("FIRST SEM. Ethics") == "Ethics"
    assert leading_banner("FIRST SEM. Ethics") == ("FIRST SEM.", "Ethics")


def test_item3_a_bare_ordinal_in_an_all_caps_title_is_not_swallowed():
    assert leading_banner("FIRST SEMESTER FIRST AID") == ("FIRST SEMESTER", "FIRST AID")
    assert strip_banner("FIRST SEMESTER FIRST AID") == "FIRST AID"
    assert leading_banner("FIRST AID") == ("", "FIRST AID")
    assert leading_banner("FIRST Ethics") == ("FIRST", "Ethics")     # the wrapped tail still goes


# --- commit A, item 4: strip only banners the table itself prints

@pytest.mark.parametrize("title", ["SUMMER INTERNSHIP", "SECOND YEAR PRACTICUM", "MID-YEAR PRACTICUM"])
def test_item4_an_all_caps_real_title_is_flagged_but_never_stripped(title):
    payload = copy.deepcopy(fx.bscs())          # this table prints FIRST YEAR / FIRST SEMESTER banners only
    payload["courses"][1]["course_title"] = title
    v = verify_candidate(payload)
    row = by_code(payload, v)["CC 1/L"]
    assert kinds(row) == ["banner_leak"] and row.flags[0].severity == "warn"
    assert row.fixes == []
    assert section(v, "S1").health == "review"


def test_item4_a_banner_the_table_prints_is_still_proposed_and_an_error():
    payload = copy.deepcopy(fx.bscs())
    payload["courses"][1]["course_title"] = "FIRST SEMESTER Introduction to Computing"
    row = by_code(payload, verify_candidate(payload))["CC 1/L"]
    assert row.flags[0].severity == "error"
    assert [(f.kind, f.new) for _l, f in row.fixes] == [("strip_banner", "Introduction to Computing")]


def test_item4_propose_fixes_without_a_known_banner_proposes_no_strip():
    payload = fx.bscs()
    course = payload["courses"][0]
    course["course_title"] = "FIRST SEMESTER Discrete Structures 1"
    assert propose_fixes(course, {"code": [], "title": [], "unit": [], "prereq": []}) == []


# --- commit A, item 5: section order does not depend on set order

_ORDER_SCRIPT = """
import sys
sys.path.insert(0, {tests!r})
import fixer_fixtures as fx
from backend.bintanong_tools.prospectus_extractor.verify import verify_candidate
p = fx.bscs()
a, b = p["courses"][0], p["courses"][1]
for c, sem in ((a, "Summer"), (b, "Mid-Year")):
    c["year_level"], c["semester"], c["term_index"] = "1st Year", sem, 13
v = verify_candidate(p)
print([(s.sid, s.semester) for s in v.sections])
"""


def test_item5_summer_and_mid_year_sections_sort_the_same_under_any_hash_seed():
    tests = str(Path(__file__).parent)
    out = set()
    for seed in ("0", "1", "2", "3", "4", "5"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(Path(tests).parent)}
        done = subprocess.run([sys.executable, "-c", _ORDER_SCRIPT.format(tests=tests)], env=env,
                              capture_output=True, text=True, check=True)
        out.add(done.stdout.strip().splitlines()[-1])
    assert len(out) == 1, out


# --- commit B, item 6: a PDF title ends before the totals column

# Real text layer of run 39 (BSEd Filipino) page 1; no PDF is stored.
FILIPINO_TEXT = (
    "SUMMER GE-STS Science, Technology and Society 3 GE-Elect: ES Environmental Science 3 Total 6 "
    "SECOND YEAR Fil 5 Panitikan ng Rehiyon 3 Fil 10 Sanaysay at Talumpati 3"
)
TQM_TEXT = "BA 2002 TQM Total Quality Management 3 BAC 5 P2207 Marketing Management 3"


def test_item6_a_title_read_from_the_pdf_stops_before_total_and_the_units_before_it():
    from backend.bintanong_tools.prospectus_extractor.fixes import title_from_pdf
    codes = ["GE-STS", "ES", "Fil 5", "Fil 10"]
    assert title_from_pdf("ES", "6", "", FILIPINO_TEXT, codes) == "Environmental Science"


def test_item6_a_real_title_that_starts_with_total_is_kept_whole():
    from backend.bintanong_tools.prospectus_extractor.fixes import title_from_pdf
    assert title_from_pdf("TQM", "3", "TQM", TQM_TEXT, ["BA 2002", "TQM", "BAC 5", "P2207"]) == "Total Quality Management"


# --- commit B, item 7: a printed code is one run of touching glyphs

def make_page(*words, glyph=5.0, space=3.0, height=800.0):
    """PdfPage from (text, left) words on one line; every glyph is `glyph` wide."""
    from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
    chars = []
    for text, left in words:
        for i, ch in enumerate(text):
            chars.append((ch, left + i * glyph, 700.0, left + (i + 1) * glyph, 710.0))
    return PdfPage(" ".join(w for w, _ in words), chars, height)


def test_item7_a_code_whose_glyphs_sit_in_different_cells_has_no_location_and_no_row():
    from backend.bintanong_tools.prospectus_extractor.placement import locate_in_page, unclaimed_items
    touching = make_page(("Mktg", 100.0), ("2001", 128.0))          # one space apart: a real code
    split = make_page(("Business", 100.0), ("Law", 145.0), ("3", 265.0))   # "3" is the units cell, 100 pt away
    assert locate_in_page(touching, "Mktg 2001") == [100.0, 90.0, 148.0, 100.0]
    assert locate_in_page(split, "Law 3") is None
    assert [i["code"] for i in unclaimed_items({}, [], {1: touching})] == ["Mktg 2001"]
    assert unclaimed_items({}, [], {1: split}) == []


# --- commit C: the ledger stays readable, undecidable entries are refused or skipped

import json
from datetime import datetime, timezone

from backend.bintanong_tools.prospectus_extractor.ledger import (
    LedgerError, append_entries, content_review_state, course_locator, course_snapshot, make_entry, materialise,
    read_entries, write_corrected,
)

OTHER = "b" * 64
NOW = datetime(2026, 10, 4, 9, 30, tzinfo=timezone.utc)
LINE_BREAKS = "\u2028\u2029\u0085"


def led_entry(course, field="row", disposition="accepted", old=None, new=None, pdf=HASH, reason="r", reviewer="Nestor"):
    snapshot = course_snapshot(course)
    return make_entry(
        reviewer=reviewer, reason=reason, pdf_sha256=pdf, locator=course_locator(course), field=field,
        disposition=disposition, old_value=snapshot if old is None and field == "row" else old,
        new_value=snapshot if new is None and field == "row" else new, section="s", now=NOW)


def test_item8_unicode_line_separators_in_a_value_do_not_split_a_ledger_line(tmp_path):
    course = fx.bscs()["courses"][0]
    path = tmp_path / "ledger.jsonl"
    title = f"Discrete{LINE_BREAKS}Structures"
    group = [led_entry(course, "course_title", "corrected", course["course_title"], title,
                       reason=f"seen{LINE_BREAKS}in PDF", reviewer=f"Ne{LINE_BREAKS}stor")]
    append_entries(path, group)
    assert read_entries(path) == group
    assert LINE_BREAKS[0] in path.read_text(encoding="utf-8")        # still written readable, not \u2028 escapes


def test_item8_a_ledger_saved_with_a_bom_and_crlf_still_reads(tmp_path):
    course = fx.bscs()["courses"][0]
    one = led_entry(course)
    path = tmp_path / "ledger.jsonl"
    path.write_bytes(b"\xef\xbb\xbf" + (json.dumps(one, ensure_ascii=False, sort_keys=True) + "\r\n").encode("utf-8") * 2)
    assert read_entries(path) == [one, one]
    assert append_entries(path, [led_entry(course, "row", "unresolved", new=None, reason="x")]) == (1, 0)


def hand_append(path, entry, **changes):
    entry = {**entry, **changes}
    entry = {k: v for k, v in entry.items() if v is not ...}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def test_item9_make_entry_refuses_a_field_materialise_cannot_apply():
    course = fx.bscs()["courses"][0]
    base = dict(reviewer="N", reason="r", pdf_sha256=HASH, locator=course_locator(course), disposition="corrected",
                old_value="x", new_value="y", section="s")
    for field in ("units", "prerequisites", "semester", "bogus"):
        with pytest.raises(LedgerError, match="field"):
            make_entry(**base, field=field)
    for field, value in (("course_code", ""), ("course_title", "   "), ("course_title", None), ("course_code", 5),
                         ("term", "somewhere"), ("row", "y"), ("unclaimed", "y")):
        with pytest.raises(LedgerError):
            make_entry(**{**base, "new_value": value}, field=field)
    make_entry(**{**base, "new_value": "2nd Year / 1st Semester"}, field="term")     # still accepted


def test_item9_entries_that_cannot_be_decided_are_skipped_with_a_reason_not_a_crash(tmp_path):
    payload = fx.bscs()
    course = payload["courses"][0]
    good = led_entry(course, "course_title", "corrected", course["course_title"], "Discrete Structures One")
    path = tmp_path / "ledger.jsonl"
    hand_append(path, good, field="units")
    hand_append(path, good, locator=...)
    hand_append(path, good, pdf_sha256=...)
    hand_append(path, good, field="course_code", new_value="")
    hand_append(path, good)
    entries = read_entries(path)
    corrected, report = materialise(payload, entries, HASH)
    reasons = sorted(s["reason"].split(":")[0] for s in report["skipped"])
    assert reasons == ["invalid_entry"] * 4 and report["applied"] == 1
    assert corrected["courses"][0]["course_title"] == "Discrete Structures One"
    state = content_review_state(payload, entries, HASH)
    assert state["invalid_entries"] == 4 and state["decided"] == 0
    assert append_entries(path, [led_entry(payload["courses"][1])]) == (1, 0)    # appending is not blocked either


def test_item10_the_same_decision_on_a_new_pdf_is_not_a_duplicate(tmp_path):
    course = fx.bscs()["courses"][0]
    path = tmp_path / "ledger.jsonl"
    assert append_entries(path, [led_entry(course)]) == (1, 0)
    assert append_entries(path, [led_entry(course, pdf=OTHER)]) == (1, 0)
    assert append_entries(path, [led_entry(course, pdf=OTHER)]) == (0, 1)
    # reviewer and reason stay out of the signature: the same accept by a second reviewer is a duplicate
    assert append_entries(path, [led_entry(course, pdf=OTHER, reviewer="Other", reason="again")]) == (0, 1)


def test_write_corrected_refuses_to_overwrite_the_raw_candidate(tmp_path):
    raw = tmp_path / "candidate.json"
    raw.write_text("{}\n", encoding="utf-8")
    with pytest.raises(LedgerError, match="raw candidate"):
        write_corrected(tmp_path / "sub" / ".." / "candidate.json", {"x": 1}, raw_candidate=raw)
    assert raw.read_text(encoding="utf-8") == "{}\n"
    write_corrected(tmp_path / "corrected.json", {"x": 1}, raw_candidate=raw)
