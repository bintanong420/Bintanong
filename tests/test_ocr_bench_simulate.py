import io

import numpy as np
import pytest
from PIL import Image

from backend.bintanong_tools.ocr_bench import simulate as sim


def _page(width=300, height=460):
    """A white page with a few ruled lines of dark ink, standing in for a rendered prospectus page."""
    img = np.full((height, width, 3), 255, np.uint8)
    for y in range(40, height - 40, 22):
        img[y:y + 6, 30:width - 30] = 20
    return img


def _decode(data):
    return np.asarray(Image.open(io.BytesIO(data)).convert("RGB"))


@pytest.mark.parametrize("name", sorted(sim.CONDITIONS))
def test_same_seed_gives_byte_identical_jpeg(name):
    a = sim.simulate_image(_page(), name, seed=7, salt="doc/p1")
    b = sim.simulate_image(_page(), name, seed=7, salt="doc/p1")
    assert a == b
    assert a[:2] == b"\xff\xd8"


def test_a_different_seed_changes_the_random_conditions():
    for name in ("tilt", "perspective", "noisy", "hard"):
        assert sim.simulate_image(_page(), name, seed=1) != sim.simulate_image(_page(), name, seed=2), name


def test_the_page_id_salts_the_randomness():
    assert sim.simulate_image(_page(), "noisy", seed=1, salt="a/p1") != sim.simulate_image(_page(), "noisy", seed=1, salt="a/p2")


def test_output_keeps_the_input_size_and_does_not_touch_the_input():
    page = _page()
    before = page.copy()
    for name in sim.CONDITIONS:
        assert _decode(sim.simulate_image(page, name, seed=3)).shape == page.shape, name
    assert np.array_equal(page, before)


def test_condition_names_are_fixed():
    assert set(sim.CONDITIONS) == {"flat_good", "tilt", "perspective", "blur", "dim", "noisy", "hard"}


def test_unknown_condition_is_refused():
    with pytest.raises(ValueError, match="unknown condition"):
        sim.simulate_image(_page(), "sepia", seed=1)


def test_dim_is_darker_and_blur_is_softer_and_noisy_is_noisier_than_flat_good():
    flat = _decode(sim.simulate_image(_page(), "flat_good", seed=5)).astype(float)
    dim = _decode(sim.simulate_image(_page(), "dim", seed=5)).astype(float)
    blur = _decode(sim.simulate_image(_page(), "blur", seed=5)).astype(float)
    noisy = _decode(sim.simulate_image(_page(), "noisy", seed=5)).astype(float)
    assert dim.mean() < flat.mean() - 40
    sharp = lambda x: np.abs(np.diff(x[:, :, 0], axis=0)).max()  # steepest edge; blur lowers it
    assert sharp(blur) < sharp(flat) * 0.8
    blank = lambda x: x[2:30, 2:100, 0].std()  # a patch of plain paper
    assert blank(noisy) > blank(flat) + 3


def test_tilt_and_perspective_move_the_ink_and_show_the_desk_at_the_edges():
    flat = _decode(sim.simulate_image(_page(), "flat_good", seed=5))
    for name in ("tilt", "perspective"):
        out = _decode(sim.simulate_image(_page(), name, seed=5))
        assert np.abs(out.astype(int) - flat.astype(int)).mean() > 5, name
        assert out[:4, :4].mean() < 150, name  # the corner is desk, not paper


def test_render_and_simulate_pdf_are_repeatable(tmp_path):
    pdf = tmp_path / "doc.pdf"
    Image.fromarray(_page(612, 936)).save(pdf)
    first = sim.simulate_pdf(pdf, tmp_path / "one", ["flat_good", "tilt"], seed=11, dpi=60)
    second = sim.simulate_pdf(pdf, tmp_path / "two", ["flat_good", "tilt"], seed=11, dpi=60)
    assert [p.name for p in first] == ["doc_p01_flat_good.jpg", "doc_p01_tilt.jpg"]
    assert [p.read_bytes() for p in first] == [p.read_bytes() for p in second]
    assert sim.simulate_pdf(pdf, tmp_path / "three", ["blur"], seed=11, dpi=60, pages=[2]) == []
