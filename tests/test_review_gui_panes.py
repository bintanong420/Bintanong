import copy
import json
from html import unescape
from html.parser import HTMLParser

import pytest

from backend.bintanong_tools.prospectus_extractor.evidence import (
    NormalizedCell, NormalizedTable, ProspectusEvidence, SourceBBox,
)
from backend.bintanong_tools.prospectus_extractor.markup import render_prospectus_markup
from backend.bintanong_tools.prospectus_extractor.verify import own_role_cells
from backend.bintanong_tools.prospectus_review_gui.render import (
    MAX_JSON_CELLS, cells_fallback, course_json, evidence_mismatch, load_evidence, twin_fragment,
)

import fixer_fixtures as fx
import review_gui_fixtures as rf

HASH = rf.HASH


def evidence_of(payload, extra_cells=()):
    """Docling-like evidence holding every source cell of the payload's courses (one table per table index)."""
    cells = {}
    for course in payload["courses"]:
        for c in course["provenance"]["source_cells"]:
            cells.setdefault(c["cell_id"], c)
    for c in extra_cells:
        cells[c["cell_id"]] = c
    tables = {}
    for c in cells.values():
        box = SourceBBox(c["page"], *c["bbox"], origin="TOPLEFT") if c.get("bbox") else None
        tables.setdefault(c["table_index"], []).append(NormalizedCell(
            c["cell_id"], c["table_index"], c["raw_text"], c["text"], c["row_start"], c["row_end"], c["col_start"], c["col_end"], box))
    out = [NormalizedTable(t, max(c.row_end for c in cs), max(c.col_end for c in cs), cs) for t, cs in sorted(tables.items())]
    return ProspectusEvidence(tables=out, source_kind="test", page_sizes={1: (612.0, 936.0), 2: (612.0, 936.0)})


def roles(payload, course):
    audit = payload["audit"]
    evidence_ids = {i for s in audit["curriculum_sections"] for i in s["evidence_cells"]}
    return own_role_cells(course, audit["table_layout"], evidence_ids)


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.attrs = [], []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs += [(tag, name, value) for name, value in attrs]


def parse(fragment):
    parser = Tags()
    parser.feed(fragment)
    parser.close()
    return parser


def test_twin_fragment_keeps_every_data_cell_id_of_the_course():
    payload = rf.mixed()
    fragment = twin_fragment(evidence_of(payload), payload, HASH)
    ids = {value for _tag, name, value in parse(fragment).attrs if name == "data-cell"}
    for course in payload["courses"]:
        assert set(course["provenance"]["source_cell_ids"]) <= ids, course["course_code"]


def test_twin_fragment_drops_the_notice_but_nothing_else():
    payload = rf.mixed()
    evidence = evidence_of(payload)
    full = render_prospectus_markup(evidence, payload, pdf_sha256=HASH)
    fragment = twin_fragment(evidence, payload, HASH)
    assert any(line.startswith("> ") for line in full.split("\n"))
    assert fragment == "\n".join(line for line in full.split("\n") if not line.startswith("> "))
    assert fragment.count("<table") == full.count("<table") == 1
    assert "Candidate for review" not in fragment


def test_twin_fragment_carries_no_script_or_event_handler_for_hostile_cell_text():
    payload = rf.mixed()
    hostile = [fx.cell("t0-c90", "<script>alert(1)</script>", 9, 0, 1, [60.0, 400.0, 90.0, 410.0]),
               fx.cell("t0-c91", '"><img onerror=x src=y>', 9, 1, 2, [100.0, 400.0, 200.0, 410.0]),
               fx.cell("t0-c92", "> not a notice\n> second line", 9, 2, 3, [246.0, 400.0, 260.0, 410.0])]
    fragment = twin_fragment(evidence_of(payload, hostile), payload, HASH)
    found = parse(fragment)
    assert "script" not in found.tags and "img" not in found.tags
    assert not [name for _tag, name, _value in found.attrs if name.startswith("on")]
    text = unescape(fragment)
    assert "<script>alert(1)</script>" in text and '"><img onerror=x src=y>' in text   # shown as text, not markup
    assert "&gt; not a notice<br>&gt; second line" in fragment   # cell text starting with "> " is not dropped


def test_twin_missing_docling_json_returns_none_and_reason(tmp_path):
    evidence, reason = load_evidence(tmp_path / "private folder" / "x_docling.json")
    assert evidence is None and "x_docling.json" in reason and "not found" in reason
    assert "private folder" not in reason


def test_corrupt_docling_json_returns_none_and_reason(tmp_path):
    for name, body in (("broken.json", b"{not json"), ("list.json", b"[]"), ("wrong.json", b'{"tables": 7}'),
                       ("binary.json", b"\xff\xfe\x00")):
        path = tmp_path / name
        path.write_bytes(body)
        evidence, reason = load_evidence(path)
        assert evidence is None and name in reason and "cannot be read" in reason, (name, reason)
        assert str(tmp_path) not in reason


def test_load_evidence_reads_a_docling_json(tmp_path):
    from docling_core.types.doc import DoclingDocument

    path = tmp_path / "x_docling.json"
    path.write_text(json.dumps(DoclingDocument(name="x").export_to_dict()), encoding="utf-8")
    evidence, reason = load_evidence(path)
    assert reason is None and isinstance(evidence, ProspectusEvidence) and evidence.tables == []


def test_cells_fallback_lists_only_the_courses_own_cells_with_their_ids():
    payload = fx.architecture()
    course = payload["courses"][0]   # AD-1/L, its provenance also carries the wide banner t0-c10
    rows = cells_fallback(course, roles(payload, course))
    assert rows == [
        {"cell_id": "t0-c11", "role": "code", "row": 2, "col": 1, "text": "AD-1/L"},
        {"cell_id": "t0-c12", "role": "title", "row": 2, "col": 2, "text": "Architectural Design 1-Introduction to Design"},
        {"cell_id": "t0-c13", "role": "unit", "row": 2, "col": 3, "text": "1/1"},
    ]
    assert "t0-c10" not in [r["cell_id"] for r in rows]
    assert cells_fallback(course, {}) == []


def test_course_json_is_the_candidate_course_unmodified():
    payload = rf.mixed()
    v = rf.verified(payload)
    _section, row = rf.row_of(v, "S3-01")
    course = payload["courses"][row.course]
    before = copy.deepcopy(course)
    out = course_json(course, row, roles(payload, course))
    assert out["course"] == before and out["course"] is not course
    assert out["truncated"] == 0
    assert out["flags"] == [{"kind": f.kind, "severity": f.severity, "message": f.message, "field": f.field} for f in row.flags]
    assert "_review" not in out["course"]
    out["course"]["provenance"]["source_cells"].clear()
    assert course == before   # a copy: changing the answer never touches the candidate


def test_course_json_for_huge_provenance_is_bounded():
    payload = fx.architecture()
    course = payload["courses"][0]
    own = roles(payload, course)
    filler = [fx.cell(f"t0-x{n}", "x" * 20, 50 + n, 0, 1, [1.0, 1.0, 2.0, 2.0]) for n in range(5000)]
    course["provenance"]["source_cells"] = filler + course["provenance"]["source_cells"]
    out = course_json(course, None, own)
    cells = out["course"]["provenance"]["source_cells"]
    assert len(cells) <= MAX_JSON_CELLS + 4
    assert out["truncated"] == 5004 - len(cells)
    kept = [c["cell_id"] for c in cells]
    assert kept[:3] == ["t0-x0", "t0-x1", "t0-x2"]
    assert {"t0-c11", "t0-c12", "t0-c13"} <= set(kept)   # the course's own cells are always kept
    assert out["flags"] == [] and len(json.dumps(out)) < 50_000
    assert len(course["provenance"]["source_cells"]) == 5004   # the candidate itself is not cut


def test_twin_page_numbers_match_pdf_pages():
    payload = rf.mixed()
    fragment = twin_fragment(evidence_of(payload), payload, HASH)
    found = parse(fragment)
    for course in payload["courses"]:
        code_cell = course["provenance"]["source_cells"][0]
        tag = f'data-cell="{code_cell["cell_id"]}"'
        start = fragment.index(tag)
        opening = fragment[fragment.rindex("<", 0, start):fragment.index(">", start)]
        assert f'data-page="{course["provenance"]["page"]}"' in opening, course["course_code"]
    assert ("td", "data-page", "2") in found.attrs   # GE-ET is on page 2


# --- S1: a Docling JSON from another prospectus is refused, not drawn


def _other_prospectus():
    other = rf.many(4)   # same cell ids (t0-a0 ...) as nothing here, and other texts
    return other


def test_evidence_that_holds_the_candidates_cells_matches():
    payload = rf.mixed()
    assert evidence_mismatch(evidence_of(payload), payload, "x_docling.json") is None


def test_evidence_with_missing_or_different_cells_is_refused_by_name():
    payload = rf.mixed()
    foreign = evidence_of(_other_prospectus())
    message = evidence_mismatch(foreign, payload, "x_docling.json")
    assert message and "x_docling.json" in message and "another prospectus" in message and "private" not in message
    # the same cell ids with other text (what two real prospectuses share: t0-c12 is a cell in both)
    altered = copy.deepcopy(payload)
    altered["courses"][0]["provenance"]["source_cells"][0]["text"] = "Something else"
    assert evidence_mismatch(evidence_of(altered), payload, "x_docling.json")
    # the candidate's own provenance wins over a payload with no source cells at all
    bare = copy.deepcopy(payload)
    for course in bare["courses"]:
        course["provenance"]["source_cells"] = []
    assert evidence_mismatch(evidence_of(payload), bare, "x_docling.json") is None


def test_real_docling_json_of_another_programme_is_refused():
    from pathlib import Path
    dump = Path(r"E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump")
    candidate = dump / "review_trial_2026-10-04" / "16_BSBA-HRM" / "BSBA-HRM-for-student-new-version_prospectus.json"
    wrong = dump / "docling_jsonified_output" / "task1_baseline_2026-09-29" / "bscs" / "1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025_docling.json"
    if not (candidate.is_file() and wrong.is_file()):
        pytest.skip("the local dataset dump is not on this machine")
    payload = json.loads(candidate.read_text(encoding="utf-8"))
    right_json = Path(payload["courses"][0]["provenance"]["raw_docling_json"])
    evidence, reason = load_evidence(wrong)
    assert evidence is not None and reason is None   # it reads fine; only the cross-check can tell
    assert evidence_mismatch(evidence, payload, wrong.name)
    if right_json.is_file():
        right, _ = load_evidence(right_json)
        assert evidence_mismatch(right, payload, right_json.name) is None
