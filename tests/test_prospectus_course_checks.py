import importlib.util
from pathlib import Path

from backend.bintanong_tools.prospectus_extractor import course_checks as cc

_spec = importlib.util.spec_from_file_location(
    "prospectus_course_audit", Path(__file__).resolve().parents[1] / "scripts" / "prospectus_course_audit.py"
)
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)

SHARED = (
    "check_course_md", "check_course_pdf", "check_pdf_missed", "check_md_unclaimed", "parse_markup", "audit_file",
    "pdf_candidates", "text_in_box", "course_roles", "load_pdf_pages", "manifest_index", "resolve_pdf", "sha256",
    "normalise", "loose", "pdf_clean", "MdDoc", "PdfPage",
)


def test_the_audit_script_uses_the_package_checks_not_copies():
    for name in SHARED:
        assert getattr(script, name) is getattr(cc, name), name


def test_pdf_check_without_a_markup_twin_says_so_and_names_the_occurrence():
    course = {"course_code": "CS 101", "course_title": "Intro", "provenance": {"page": 1}}
    page = "CS 101 Intro 3 ZZ-999 Ghost Course 3 ZZ-999 Again"
    rows = cc.check_pdf_missed([course], {}, page, None, page_no=1)
    ghosts = [r for r in rows if r["json"] == "ZZ-999"]
    assert [(r["status"], r["md_location"], r["occurrence"]) for r in ghosts] == [("silent", "unknown", 1), ("silent", "unknown", 2)]
