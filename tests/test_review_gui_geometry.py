import pytest

from backend.bintanong_tools.prospectus_extractor.course_checks import PdfPage
from backend.bintanong_tools.prospectus_extractor.placement import locate_in_page
from backend.bintanong_tools.prospectus_extractor.verify import own_role_cells
from backend.bintanong_tools.prospectus_review_gui.geometry import bbox_fraction, boxes_for_question
from backend.bintanong_tools.prospectus_review_gui.render import PageRenderer

import fixer_fixtures as fx
import review_gui_fixtures as rf

PAGE = (612.0, 792.0)


def test_bbox_fraction_top_left_frame():
    assert bbox_fraction([60, 80, 120, 160], (600, 800)) == {"left": 0.1, "top": 0.1, "width": 0.1, "height": 0.1}


def test_bbox_fraction_clamps_and_refuses_incomplete_boxes():
    assert bbox_fraction([-30, -40, 700, 900], (600, 800)) == {"left": 0.0, "top": 0.0, "width": 1.0, "height": 1.0}
    for bad in (None, [], [1, 2, 3], [1, 2, 3, None], ["a", 2, 3, 4], [5, 5, 5, 9], [5, 5, 9, 5], [9, 9, 1, 1]):
        assert bbox_fraction(bad, (600, 800)) is None, bad
    for size in (None, (0, 800), (600, 0), (-1, 5)):
        assert bbox_fraction([1, 2, 3, 4], size) is None


def make_pdf(path, *, rotate=0):
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(path), pagesize=PAGE)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(100, 600, "CS 9")   # x 100, baseline 600 above the bottom
    if rotate:
        c.setPageRotation(rotate)
    c.showPage()
    c.save()


def dark(image, fractions):
    w, h = image.size
    box = (int(fractions["left"] * w), int(fractions["top"] * h),
           int((fractions["left"] + fractions["width"]) * w), int((fractions["top"] + fractions["height"]) * h))
    return sum(image.convert("L").crop(box).histogram()[:100])


def test_unclaimed_item_box_uses_the_same_frame(tmp_path):
    from io import BytesIO

    from PIL import Image
    from backend.bintanong_tools.prospectus_extractor.course_checks import load_pdf_pages
    path = tmp_path / "one.pdf"
    make_pdf(path)
    page = load_pdf_pages(path)[1]
    bbox = locate_in_page(page, "CS 9")
    assert bbox is not None
    fractions = bbox_fraction(bbox, PAGE)
    with PageRenderer(path) as renderer:
        image = Image.open(BytesIO(renderer.png(1, 2.0)))
    assert dark(image, fractions) > 30   # the glyphs are under the box
    far = {"left": 0.1, "top": 0.8, "width": 0.3, "height": 0.1}
    assert dark(image, far) == 0         # and paper elsewhere
    mirrored = {**fractions, "top": 1 - fractions["top"] - fractions["height"]}   # a y-up mix-up would land here
    assert dark(image, mirrored) == 0


def question(kind="course"):
    return type("Q", (), {"kind": kind})()


def test_course_highlight_uses_own_role_cells_not_the_banner():
    payload = fx.architecture()
    course = payload["courses"][0]
    audit = payload["audit"]
    evidence = {i for s in audit["curriculum_sections"] for i in s["evidence_cells"]}
    roles = own_role_cells(course, audit["table_layout"], evidence)
    result = boxes_for_question(question(), course=course, role_cells=roles, page=1, page_size=PAGE)
    assert result["warning"] is None
    strong = {b["cell_id"]: b["role"] for b in result["boxes"] if b["strong"]}
    assert strong == {"t0-c11": "code", "t0-c12": "title", "t0-c13": "unit"}
    banner = [b for b in result["boxes"] if b["cell_id"] == "t0-c10"]
    assert banner and not banner[0]["strong"] and banner[0]["role"] == "context"
    union = bbox_fraction(course["provenance"]["bbox"], PAGE)
    assert all(b["fractions"] != union for b in result["boxes"])   # provenance.bbox (banner included) is never drawn
    assert all(set(b["fractions"]) == {"left", "top", "width", "height"} for b in result["boxes"])


def test_boxes_only_for_the_displayed_page():
    payload = rf.mixed()
    course = payload["courses"][-1]   # on page 2
    audit = payload["audit"]
    roles = own_role_cells(course, audit["table_layout"], set())
    assert boxes_for_question(question(), course=course, role_cells=roles, page=1, page_size=PAGE)["boxes"] == []
    assert len(boxes_for_question(question(), course=course, role_cells=roles, page=2, page_size=PAGE)["boxes"]) == 3


def test_unclaimed_question_draws_the_item_box_strong():
    item = {"code": "CS 9", "page": 3, "bbox": [64.0, 300.0, 84.0, 310.0]}
    result = boxes_for_question(question("unclaimed"), item=item, page=3, page_size=PAGE)
    assert [(b["role"], b["strong"]) for b in result["boxes"]] == [("code", True)]
    assert boxes_for_question(question("unclaimed"), item=item, page=2, page_size=PAGE)["boxes"] == []
    assert boxes_for_question(question("section_confirm"), page=1, page_size=PAGE) == {"boxes": [], "warning": None}


def test_rotated_page_gets_warning_and_no_boxes(tmp_path):
    path = tmp_path / "rot.pdf"
    make_pdf(path, rotate=90)
    with PageRenderer(path) as renderer:
        rotation = renderer.rotation(1)
        size = renderer.size(1)
    assert rotation == 90
    item = {"code": "CS 9", "page": 1, "bbox": [64.0, 300.0, 84.0, 310.0]}
    result = boxes_for_question(question("unclaimed"), item=item, page=1, page_size=size, rotation=rotation)
    assert result["boxes"] == [] and "rotated" in result["warning"]


def test_size_mismatch_with_docling_over_one_point_warns():
    item = {"code": "CS 9", "page": 1, "bbox": [64.0, 300.0, 84.0, 310.0]}
    result = boxes_for_question(question("unclaimed"), item=item, page=1, page_size=(612.0, 792.0), docling_size=(612.0, 794.0))
    assert result["boxes"] == [] and "size" in result["warning"]
    result = boxes_for_question(question("unclaimed"), item=item, page=1, page_size=(612.0, 792.0), docling_size=(595.0, 792.0))
    assert result["boxes"] == [] and result["warning"]


def test_size_within_one_point_is_accepted():
    item = {"code": "CS 9", "page": 1, "bbox": [64.0, 300.0, 84.0, 310.0]}
    result = boxes_for_question(question("unclaimed"), item=item, page=1, page_size=(612.0, 792.0), docling_size=(612.9, 791.2))
    assert result["warning"] is None and len(result["boxes"]) == 1


def test_missing_page_size_warns():
    item = {"code": "CS 9", "page": 1, "bbox": [64.0, 300.0, 84.0, 310.0]}
    result = boxes_for_question(question("unclaimed"), item=item, page=1, page_size=None)
    assert result["boxes"] == [] and result["warning"]
