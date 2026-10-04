"""Regression tests for the Codex read-only review of Phase B2 (12 confirmed defects)."""

import copy
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.fixes import propose_fixes
from backend.bintanong_tools.prospectus_extractor.verify import own_role_cells, verify_candidate

import fixer_fixtures as fx
from fixer_fixtures import by_code

HASH = "a" * 64


def set_cell_text(payload, cell_id, text):
    for course in payload["courses"]:
        for c in course["provenance"]["source_cells"]:
            if c["cell_id"] == cell_id:
                c["text"] = text


def roles(course, payload):
    audit = payload["audit"]
    ids = {i for s in audit["curriculum_sections"] for i in s["evidence_cells"]}
    return own_role_cells(course, audit["table_layout"], ids)


BANNERS = {"FIRST", "SEMESTER", "YEAR"}


# --- commit 1: proposals come from the source and never strip a title word

def test_item1_a_title_that_is_only_banner_plus_one_word_in_its_own_cell_is_not_stripped():
    payload = copy.deepcopy(fx.bscs())
    course = payload["courses"][1]
    course["course_title"] = "FIRST SEMESTER PRACTICUM"
    set_cell_text(payload, "t0-c18", "FIRST SEMESTER PRACTICUM")
    pdf = "CC 1/L FIRST SEMESTER PRACTICUM 2/1"
    assert propose_fixes(course, roles(course, payload), page_text=pdf, banners=BANNERS) == []
    row = by_code(payload, verify_candidate(payload))["CC 1/L"]
    assert row.fixes == [] and row.worst() is not None       # still flagged, section not clean


def test_item1_a_strip_is_proposed_when_the_pdf_prints_the_remainder_without_the_banner():
    payload = copy.deepcopy(fx.bscs())
    course = payload["courses"][0]       # CS 1: only its title cell t0-c9 carries the banner
    course["course_title"] = "FIRST SEMESTER Discrete Structures 1"
    page = "FIRST SEMESTER CS 1 Discrete Structures 1 3 CC 1/L Introduction to Computing 2/1"
    fixes = propose_fixes(course, roles(course, payload), page_text=page, banners=BANNERS)
    assert [f.new for f in fixes] == ["Discrete Structures 1"]
    assert propose_fixes(course, roles(course, payload), banners=BANNERS) == []   # nothing to confirm it with


def test_item2_a_remainder_that_is_in_no_source_cell_or_pdf_text_is_not_proposed():
    payload = copy.deepcopy(fx.bscs())
    course = payload["courses"][1]
    course["course_title"] = "FIRST SEMESTER Galactic Mechanics"      # its cell says "Introduction to Computing"
    page = "CC 1/L Introduction to Computing 2/1"
    assert propose_fixes(course, roles(course, payload), page_text=page, banners=BANNERS) == []
    assert by_code(payload, verify_candidate(payload))["CC 1/L"].fixes == []


# --- item 12: glyphs of one printed code sit on one text line

def make_two_line_page():
    # "Mktg" at the end of a wrapped line, "2001" at the start of the next one: horizontally adjacent
    # (the second word starts 3 pt after the first ends) but on different lines.
    chars = []
    for i, ch in enumerate("Mktg"):
        chars.append((ch, 400.0 + i * 5, 700.0, 405.0 + i * 5, 710.0))
    for i, ch in enumerate("2001"):
        chars.append((ch, 423.0 + i * 5, 686.0, 428.0 + i * 5, 696.0))
    return PdfPage("Mktg 2001", chars, 800.0)


def test_item12_glyphs_on_different_lines_are_not_one_code():
    from backend.bintanong_tools.prospectus_extractor.placement import is_split_across_cells, locate_in_page
    page = make_two_line_page()
    assert locate_in_page(page, "Mktg 2001") is None
    assert is_split_across_cells(page, "Mktg 2001")


# --- commit 2: sheet controls and bulk confirm respect section flags

from backend.bintanong_tools.prospectus_extractor.sheet import (
    build_entries, candidate_sha256, check_against, parse_decision, parse_sheet, render_sheet,
)
from sheet_helpers import edit_row, set_line


def rendered(payload, v):
    return render_sheet(payload, v, {"pdf_sha256": HASH, "candidate_sha256": candidate_sha256(payload)})


def test_item3_confirm_yes_on_a_section_with_a_section_level_flag_is_refused_naming_the_flag():
    payload = copy.deepcopy(fx.bscs())
    payload["audit"]["term_unit_audit"][0]["declared_units"] = 99        # S1: printed 99, extracted 5
    v = verify_candidate(payload)
    assert [r.worst() for r in v.sections[0].rows] == [None, None] and v.sections[0].flags
    text = set_line(rendered(payload, v), "S1", "confirm", "yes")
    entries, errors = build_entries(parse_sheet(text), payload, v, reviewer="N", pdf_sha256=HASH)
    assert entries == []
    assert any("S1" in e and "unit_total" in e and "(line " in e for e in errors), errors


@pytest.mark.parametrize("key", ["confirm", "accept", "reason"])
def test_item4_a_repeated_control_line_in_one_section_is_rejected_with_its_line_number(key):
    payload = copy.deepcopy(fx.bscs())
    v = verify_candidate(payload)
    base = rendered(payload, v)
    lines = base.splitlines()
    at_line = next(i for i, l in enumerate(lines) if l.startswith(f"{key}:"))
    lines.insert(at_line + 1, f"{key}: no")
    text = "\n".join(lines) + "\n"
    errors = check_against(parse_sheet(text), parse_sheet(base))
    assert any(f"line {at_line + 2}" in e and key in e and "twice" in e for e in errors), errors


def test_item5_a_decision_that_is_only_a_reason_is_a_validation_error_not_a_crash():
    assert parse_decision(": because")[3] is not None
    payload = copy.deepcopy(fx.bscs())
    v = verify_candidate(payload)
    text = edit_row(rendered(payload, v), "S1-01", decision=": because")
    entries, errors = build_entries(parse_sheet(text), payload, v, reviewer="N", pdf_sha256=HASH)
    assert entries == [] and any("S1-01" in e and "(line " in e for e in errors)
