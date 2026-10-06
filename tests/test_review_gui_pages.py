import math
import os
import struct
import tempfile
from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_review_gui.render import MAX_SCALE, PageError, PageRenderer

SYNTHETIC = Path(__file__).parent / "fixtures" / "synthetic_academic_guide.pdf"


def png_size(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])


def test_png_is_a_png_with_scaled_dimensions():
    with PageRenderer(SYNTHETIC) as renderer:
        width_pt, height_pt = renderer.size(1)
        for scale in (1.0, 1.5, 3.0):
            w, h = png_size(renderer.png(1, scale))
            assert abs(w - math.ceil(width_pt * scale)) <= 1 and abs(h - math.ceil(height_pt * scale)) <= 1
        assert png_size(renderer.png(1)) == png_size(renderer.png(1, 1.5))   # 1.5 is the default
        assert renderer.rotation(1) == 0 and renderer.page_count >= 1


def test_render_is_cached_and_writes_no_file(tmp_path, monkeypatch):
    # Only the places this code could write are watched: the working directory, a private temp directory (so other
    # processes writing to the real %TEMP% cannot fail the test) and the PDF's own folder.
    work, temp, pdf_dir = tmp_path / "cwd", tmp_path / "temp", tmp_path / "pdf"
    for folder in (work, temp, pdf_dir):
        folder.mkdir()
    pdf = pdf_dir / SYNTHETIC.name
    pdf.write_bytes(SYNTHETIC.read_bytes())
    monkeypatch.chdir(work)
    for name in ("TEMP", "TMP", "TMPDIR"):
        monkeypatch.setenv(name, str(temp))
    monkeypatch.setattr(tempfile, "tempdir", str(temp))
    with PageRenderer(pdf) as renderer:
        first = renderer.png(1, 1.5)
        count = renderer.render_count
        assert renderer.png(1, 1.5) == first and renderer.render_count == count   # served from memory
        renderer.png(1, 2.0)
        assert renderer.render_count == count + 1
    assert os.listdir(work) == [] and os.listdir(temp) == [] and os.listdir(pdf_dir) == [SYNTHETIC.name]


def test_cache_keeps_only_the_last_eight_renders():
    with PageRenderer(SYNTHETIC) as renderer:
        for scale in (1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8):
            renderer.png(1, scale)
        count = renderer.render_count
        renderer.png(1, 1.8)
        assert renderer.render_count == count
        renderer.png(1, 1.0)   # the first one was evicted
        assert renderer.render_count == count + 1


def test_missing_pdf_and_bad_page_raise_page_error(tmp_path):
    missing = tmp_path / "private folder" / "nope.pdf"
    with pytest.raises(PageError) as caught:
        PageRenderer(missing)
    assert "nope.pdf" in str(caught.value) and "private folder" not in str(caught.value)
    with PageRenderer(SYNTHETIC) as renderer:
        for bad in (0, -1, renderer.page_count + 1, 1.5, True, "1"):
            with pytest.raises(PageError):
                renderer.png(bad)
            with pytest.raises(PageError):
                renderer.size(bad)
    not_pdf = tmp_path / "x.pdf"
    not_pdf.write_bytes(b"this is not a pdf")
    with pytest.raises(PageError):
        PageRenderer(not_pdf)


@pytest.mark.parametrize("scale", [0, -1, 10, 3.01, float("nan"), float("inf"), "big", None])
def test_scale_is_limited(scale):
    with PageRenderer(SYNTHETIC) as renderer:
        with pytest.raises(PageError):
            renderer.png(1, scale)
        assert renderer.render_count == 0


def test_scale_limits_are_inclusive_at_the_maximum():
    assert MAX_SCALE == 3
    with PageRenderer(SYNTHETIC) as renderer:
        assert png_size(renderer.png(1, 3))[0] > png_size(renderer.png(1, 1.5))[0]


def test_pdf_with_spaces_and_unicode_in_its_path_opens(tmp_path):
    folder = tmp_path / "Kuwentong Pálawan ñ"
    folder.mkdir()
    path = folder / "Gabay ng Kolehiyo (2026) 1.pdf"
    path.write_bytes(SYNTHETIC.read_bytes())
    with PageRenderer(path) as renderer:
        assert png_size(renderer.png(1))[0] > 100


HAMMER = r"""
import sys, threading
from pathlib import Path
from backend.bintanong_tools.prospectus_review_gui.render import PageRenderer

errors = []
with PageRenderer(Path(sys.argv[1])) as renderer:
    def work(k):
        try:
            for i in range(60):
                renderer.size(1); renderer.rotation(1)
                renderer.png(1, 0.2 + ((k * 61 + i * 7) % 28) / 10)
        except Exception as exc:
            errors.append(repr(exc))
    threads = [threading.Thread(target=work, args=(k,)) for k in range(12)]
    [t.start() for t in threads]
    [t.join() for t in threads]
print("errors", errors)
sys.exit(1 if errors else 0)
"""


def test_concurrent_mixed_calls_do_not_crash_pdfium():
    # pdfium is not thread-safe: unserialised size/rotation/png calls from the server's worker threads corrupted the
    # heap (exit 0xC0000374). Run in a child process so a crash is a clean failure, not a dead test run.
    import subprocess
    import sys

    repo = Path(__file__).resolve().parent.parent
    done = subprocess.run([sys.executable, "-c", HAMMER, str(SYNTHETIC)], cwd=repo, capture_output=True, text=True, timeout=300)
    assert done.returncode == 0, (done.returncode, done.stdout[-500:], done.stderr[-500:])
