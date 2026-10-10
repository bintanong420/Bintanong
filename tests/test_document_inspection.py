"""Task 2 (Phase 2 draft): read-only inspection of an originals tree, synthetic fixtures only."""

from __future__ import annotations

import hashlib
import io
import json
import os
import stat
import sys
import zipfile
from pathlib import Path

import pytest
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from backend.bintanong_tools.document_ingest import inspection

REPORT = "inspection_report.json"
MANIFEST = "manifest.json"


# ---------- fixture builders ----------
def native_pdf(pages: int = 1) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    for i in range(pages):
        c.drawString(50, 700, f"Synthetic native page {i} " + "word " * 40)
        c.showPage()
    c.save()
    return buf.getvalue()


def image_pdf(pages: int = 1, blank_after: int = 0) -> bytes:
    img = io.BytesIO()
    Image.new("RGB", (40, 40), "white").save(img, "PNG")
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    for _ in range(pages):
        img.seek(0)
        c.drawImage(ImageReader(img), 50, 50, 100, 100)
        c.showPage()
    for _ in range(blank_after):
        c.showPage()
    c.save()
    return buf.getvalue()


def mixed_pdf() -> bytes:
    """One native page then one image-only page, merged by pdfium."""
    import pypdfium2 as pdfium

    out = pdfium.PdfDocument(native_pdf(1))
    out.import_pages(pdfium.PdfDocument(image_pdf(1)))
    buf = io.BytesIO()
    out.save(buf)
    return buf.getvalue()


def zero_page_pdf() -> bytes:
    objs = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[]/Count 0>>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for n, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj" % n + body + b"endobj\n"
    xref = len(out)
    out += b"xref\n0 3\n0000000000 65535 f \n"
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer<</Root 1 0 R/Size 3>>\nstartxref\n%d\n%%%%EOF\n" % xref
    return out


def encrypted_pdf() -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, encrypt="pw")
    c.drawString(50, 700, "secret")
    c.save()
    return buf.getvalue()


def png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), "red").save(buf, "PNG")
    return buf.getvalue()


def jpg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), "red").save(buf, "JPEG")
    return buf.getvalue()


def pptx_bytes(language: str | None = None, slides: int = 2) -> bytes:
    ns = (
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for i in range(1, slides + 1):
            tbl = "<a:tbl/>" if i == 1 else ""
            z.writestr(f"ppt/slides/slide{i}.xml", f"<p:sld {ns}>{tbl}<p:pic/><p:pic/></p:sld>")
        lang = f"<dc:language>{language}</dc:language>" if language else ""
        z.writestr(
            "docProps/core.xml",
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            f'xmlns:dc="http://purl.org/dc/elements/1.1/">{lang}</cp:coreProperties>',
        )
    return buf.getvalue()


def put(root: Path, rel: str, data: bytes, readonly: bool = True) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    if readonly:
        p.chmod(stat.S_IREAD)
    return p


def run(root: Path, out: Path) -> tuple[int, dict]:
    code = inspection.main(["--root", str(root), "--out", str(out)])
    rep = out / REPORT
    return code, (json.loads(rep.read_text(encoding="utf-8")) if rep.exists() else {})


def by_path(report: dict) -> dict:
    return {f["path"]: f for f in report["files"]}


@pytest.fixture
def tree(tmp_path):
    root = tmp_path / "originals"
    put(root, "A/native.pdf", native_pdf(2))
    put(root, "A/scan.pdf", image_pdf(2))
    put(root, "A/blankish.pdf", image_pdf(1, blank_after=1))
    put(root, "B/photo.jpg", jpg_bytes())
    put(root, "B/deck.pptx", pptx_bytes("en-PH"))
    return root


# ---------- counts, classes, health ----------
def test_counts_by_extension_and_totals(tree, tmp_path):
    code, rep = run(tree, tmp_path / "out")
    assert code == 0
    assert rep["counts"]["total"] == 5
    assert rep["counts"]["by_extension"] == {".jpg": 1, ".pdf": 3, ".pptx": 1}


def test_native_scanned_blank_classification_and_invariant(tree, tmp_path):
    _, rep = run(tree, tmp_path / "out")
    f = by_path(rep)
    assert f["A/native.pdf"]["pdf"]["document_class"] == "native"
    assert f["A/scan.pdf"]["pdf"]["document_class"] == "scanned"
    pages = f["A/blankish.pdf"]["pdf"]["page_classes"]
    assert pages == {"native": 0, "scanned": 1, "blank": 1, "unknown": 0}
    for rec in f.values():
        if "pdf" in rec:
            pc = rec["pdf"]["page_classes"]
            assert sum(pc.values()) == rec["pdf"]["page_count"]
            assert rec["pdf"]["invariant_ok"] is True
    assert f["A/native.pdf"]["pdf"]["tables"] == "not_determined"
    assert f["A/native.pdf"]["pdf"]["printed_folio"] == "undetermined"


def test_mixed_document_class(tmp_path):
    root = tmp_path / "o"
    put(root, "m.pdf", mixed_pdf())
    _, rep = run(root, tmp_path / "out")
    assert by_path(rep)["m.pdf"]["pdf"]["document_class"] == "mixed"


def test_mixed_wins_even_with_an_unknown_page(tmp_path):
    """Found on the real run: a native + scanned document with one in-between page is mixed, not unknown."""
    import pypdfium2 as pdfium

    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(50, 700, "x" * 50)
    c.save()
    doc = pdfium.PdfDocument(mixed_pdf())
    doc.import_pages(pdfium.PdfDocument(buf.getvalue()))
    out = io.BytesIO()
    doc.save(out)
    root = tmp_path / "o"
    put(root, "m3.pdf", out.getvalue())
    _, rep = run(root, tmp_path / "out")
    pdf = by_path(rep)["m3.pdf"]["pdf"]
    assert pdf["page_classes"] == {"native": 1, "scanned": 1, "blank": 0, "unknown": 1}
    assert pdf["document_class"] == "mixed"

def test_unknown_class_for_middle_text_length(tmp_path):
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(50, 700, "x" * 50)
    c.save()
    root = tmp_path / "o"
    put(root, "u.pdf", buf.getvalue())
    _, rep = run(root, tmp_path / "out")
    pdf = by_path(rep)["u.pdf"]["pdf"]
    assert pdf["page_classes"]["unknown"] == 1 and pdf["document_class"] == "unknown"


def test_health_classes(tmp_path):
    root = tmp_path / "o"
    good = native_pdf()
    put(root, "truncated.pdf", good[: len(good) // 2])
    put(root, "zero.pdf", zero_page_pdf())
    put(root, "png_as.jpg", png_bytes())
    put(root, "corrupt.pptx", b"PK\x03\x04 not really a zip")
    put(root, "garbage.pdf", b"nothing here")
    put(root, "ok.jpg", jpg_bytes())
    put(root, "broken.jpg", b"\xff\xd8\xff" + b"\x00" * 10)
    _, rep = run(root, tmp_path / "out")
    h = {p: f["health"] for p, f in by_path(rep).items()}
    assert h["truncated.pdf"] == "unreadable"
    assert h["zero.pdf"] == "zero_pages"
    assert h["png_as.jpg"] == "extension_mismatch"
    assert h["corrupt.pptx"] == "unreadable"
    assert h["garbage.pdf"] == "extension_mismatch"
    assert h["ok.jpg"] == "ok"
    assert h["broken.jpg"] == "unreadable"


def test_encrypted_pdf_health(tmp_path):
    try:
        data = encrypted_pdf()
    except Exception:  # pragma: no cover
        pytest.skip("reportlab encryption unavailable")
    root = tmp_path / "o"
    put(root, "enc.pdf", data)
    _, rep = run(root, tmp_path / "out")
    assert by_path(rep)["enc.pdf"]["health"] == "encrypted"


def test_pptx_language_and_counts(tmp_path):
    root = tmp_path / "o"
    put(root, "with.pptx", pptx_bytes("fil-PH", slides=3))
    put(root, "without.pptx", pptx_bytes(None))
    _, rep = run(root, tmp_path / "out")
    f = by_path(rep)
    assert f["with.pptx"]["language"] == {"value": "fil-PH", "status": "observed"}
    assert f["without.pptx"]["language"] == {"value": "undetermined", "status": "undetermined"}
    assert f["with.pptx"]["pptx"] == {"slides": 3, "tables": 1, "pictures": 6}


def test_pdf_and_jpg_language_undetermined(tree, tmp_path):
    _, rep = run(tree, tmp_path / "out")
    f = by_path(rep)
    assert f["A/native.pdf"]["language"]["status"] == "undetermined"
    assert f["B/photo.jpg"]["language"]["status"] == "undetermined"


def test_duplicate_grouping_and_same_name_different_bytes(tmp_path):
    root = tmp_path / "o"
    data = native_pdf()
    put(root, "x/Charter.pdf", data)
    put(root, "y/Charter.pdf", data)
    put(root, "z/Charter.pdf", native_pdf(2))
    _, rep = run(root, tmp_path / "out")
    groups = rep["duplicates"]["byte_identical_groups"]
    assert [g["paths"] for g in groups] == [["x/Charter.pdf", "y/Charter.pdf"]]
    assert rep["counts"]["unique_byte_identities"] == 2
    assert rep["duplicates"]["same_name_different_bytes"] == [
        {"name": "Charter.pdf", "identities": 2}
    ]


def test_pilot_candidates_are_named_and_marked(tmp_path):
    root = tmp_path / "o"
    put(root, "Student Handbook and Constitutions/Handbook 2019.pdf", native_pdf(1))
    put(root, "Student Handbook and Constitutions/USG Constitution.pdf", native_pdf(2))
    put(root, "Procedures/poster.jpg", jpg_bytes())
    put(root, "Citizens Charter/deck.pptx", pptx_bytes())
    _, rep = run(root, tmp_path / "out")
    pc = rep["pilot_candidates"]
    assert pc["status"] == "candidates_for_owner_not_selected"
    assert "Student Handbook and Constitutions/Handbook 2019.pdf" in pc["handbook_editions"]
    assert pc["usg_constitution"] == ["Student Handbook and Constitutions/USG Constitution.pdf"]
    assert pc["pptx"] == ["Citizens Charter/deck.pptx"]
    assert pc["jpg_poster"] == ["Procedures/poster.jpg"]
    assert pc["largest_pdf_by_pages"][0]["path"].endswith("USG Constitution.pdf")


def test_prospectus_folder_counted_separately(tmp_path):
    root = tmp_path / "o"
    put(root, "Prospectus Dump/a.pdf", native_pdf(1))
    put(root, "Other/b.pdf", native_pdf(2))
    _, rep = run(root, tmp_path / "out")
    assert rep["counts"]["prospectus_workstream"] == 1
    assert rep["counts"]["non_prospectus"] == 1


def test_two_runs_give_byte_identical_reports(tree, tmp_path):
    run(tree, tmp_path / "o1")
    run(tree, tmp_path / "o2")
    for name in (REPORT, "source_manifest.json", MANIFEST):
        assert (tmp_path / "o1" / name).read_bytes() == (tmp_path / "o2" / name).read_bytes()


# ---------- safety ----------
def snapshot_tree(root: Path) -> dict:
    return {
        str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
        for p in sorted(root.rglob("*")) if p.is_file()
    }


def test_originals_read_only_and_unchanged(tree, tmp_path):
    before = snapshot_tree(tree)
    code, _ = run(tree, tmp_path / "out")
    assert code == 0
    assert snapshot_tree(tree) == before
    assert all(not os.access(p, os.W_OK) for p in tree.rglob("*.pdf"))


def test_changed_file_between_manifests_fails_run(tree, tmp_path, monkeypatch):
    real = inspection.inspect_file
    target = tree / "A" / "native.pdf"

    def tamper(*args, **kw):
        target.chmod(stat.S_IWRITE | stat.S_IREAD)
        target.write_bytes(target.read_bytes() + b"\n%x")
        return real(*args, **kw)

    monkeypatch.setattr(inspection, "inspect_file", tamper)
    code = inspection.main(["--root", str(tree), "--out", str(tmp_path / "out")])
    assert code != 0
    assert not (tmp_path / "out" / MANIFEST).exists()


def test_non_empty_out_refused(tree, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "keep.txt").write_text("x")
    assert inspection.main(["--root", str(tree), "--out", str(out)]) != 0
    assert [p.name for p in out.iterdir()] == ["keep.txt"]


def test_out_inside_root_refused(tree, tmp_path):
    out = tree / "reports"
    assert inspection.main(["--root", str(tree), "--out", str(out)]) != 0
    assert not out.exists()


def test_out_inside_repository_refused_including_git_file(tree, tmp_path):
    repo = tmp_path / "wt"
    repo.mkdir()
    (repo / ".git").write_text("gitdir: /elsewhere/.git/worktrees/wt\n")
    out = repo / "deep" / "out"
    assert inspection.main(["--root", str(tree), "--out", str(out)]) != 0
    assert not out.exists()
    repo2 = tmp_path / "plain"
    (repo2 / ".git").mkdir(parents=True)
    assert inspection.main(["--root", str(tree), "--out", str(repo2 / "out")]) != 0


def test_manifest_written_last(tree, tmp_path, monkeypatch):
    order = []
    real = inspection.write_text_lf
    monkeypatch.setattr(inspection, "write_text_lf", lambda p, t: (order.append(Path(p).name), real(p, t)))
    run(tree, tmp_path / "out")
    assert order[-1] == MANIFEST and order.index(REPORT) < order.index(MANIFEST)
    manifest = json.loads((tmp_path / "out" / MANIFEST).read_text())
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((tmp_path / "out" / name).read_bytes()).hexdigest() == digest


@pytest.mark.skipif(sys.platform != "win32", reason="extended-length paths are Windows only")
def test_over_260_char_path_is_unreachable_finding_and_nonzero(tmp_path):
    root = tmp_path / "o"
    deep = root
    while len(str(deep)) < 280:
        deep = deep / ("d" * 40)
    ext = Path("\\\\?\\" + str(deep))
    ext.mkdir(parents=True)
    (ext / "long.pdf").write_bytes(native_pdf())
    put(root, "short.pdf", native_pdf())
    code, rep = run(root, tmp_path / "out")
    assert code != 0
    longs = [f for f in rep["files"] if f["health"] == "path_unreachable"]
    assert len(longs) == 1
    assert rep["counts"]["longest_path_chars"] > 260
    text = (tmp_path / "out" / REPORT).read_text(encoding="utf-8")
    assert str(tmp_path) not in text and "Hawksprey" not in text and "Synthetic native" not in text
    assert (tmp_path / "out" / MANIFEST).exists()


def test_report_holds_no_absolute_path_or_source_text(tree, tmp_path):
    run(tree, tmp_path / "out")
    text = (tmp_path / "out" / REPORT).read_text(encoding="utf-8")
    assert str(tmp_path) not in text and "Synthetic native" not in text


@pytest.mark.parametrize("change", ["addition", "removal", "rename"])
def test_tree_membership_changed_during_inspection_fails_without_manifest(tmp_path, monkeypatch, change):
    root = tmp_path / "originals"
    source = put(root, "a.pdf", native_pdf(), readonly=False)
    original = source.read_bytes()
    real = inspection.inspect_file

    def change_membership(rel, data):
        result = real(rel, data)
        if change == "addition":
            put(root, "b.pdf", original, readonly=False)
        elif change == "removal":
            source.unlink()
        else:
            source.rename(root / "b.pdf")
        return result

    monkeypatch.setattr(inspection, "inspect_file", change_membership)
    out = tmp_path / "out"
    assert inspection.main(["--root", str(root), "--out", str(out)]) == 1
    assert not (out / MANIFEST).exists()
    if change == "addition":
        assert source.read_bytes() == original
        assert sorted(p.name for p in root.iterdir()) == ["a.pdf", "b.pdf"]


@pytest.mark.parametrize("denied_snapshot", ["before", "after"])
def test_denied_subtree_refused_without_manifest(tmp_path, monkeypatch, capsys, denied_snapshot):
    root = tmp_path / "originals"
    visible = put(root, "visible.txt", b"synthetic visible")
    hidden = put(root, "blocked/hidden.txt", b"synthetic hidden")
    before = snapshot_tree(root)
    real_scandir = os.scandir
    blocked_walks = 0

    def denied(path):
        nonlocal blocked_walks
        if Path(path).name == "blocked":
            blocked_walks += 1
            if denied_snapshot == "before" or blocked_walks == 2:
                raise PermissionError(13, "synthetic denied directory", os.fspath(path))
        return real_scandir(path)

    out = tmp_path / "out"
    with monkeypatch.context() as fault:
        fault.setattr(os, "scandir", denied)
        code = inspection.main(["--root", str(root), "--out", str(out)])

    assert snapshot_tree(root) == before
    assert visible.read_bytes() == b"synthetic visible"
    assert hidden.read_bytes() == b"synthetic hidden"
    assert code == 2
    assert not (out / MANIFEST).exists()
    assert "synthetic denied directory" in capsys.readouterr().err
