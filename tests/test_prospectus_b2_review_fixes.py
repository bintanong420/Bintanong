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
