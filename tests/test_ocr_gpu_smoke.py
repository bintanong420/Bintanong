import difflib
import importlib.util

import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from backend.bintanong_tools.ocr_bench import engines


def _cuda_ready() -> bool:
    if importlib.util.find_spec("onnxruntime") is None or importlib.util.find_spec("torch") is None:
        return False
    try:
        import onnxruntime
        import torch

        return "CUDAExecutionProvider" in onnxruntime.get_available_providers() and torch.cuda.is_available()
    except Exception:  # a broken CUDA install counts as no GPU
        return False


# The skip lives here, not in tests/conftest.py (Phase D owns the single conftest and can absorb it);
# the `gpu` marker is registered in backend/pyproject.toml. Run on a GPU host with `pytest -m gpu`.
pytestmark = [pytest.mark.gpu, pytest.mark.skipif(not _cuda_ready(), reason="no CUDA device or ocr-gpu extra")]


def _page(lines=40):
    """A white page of many short lines of different widths, like a curriculum table (many recognizer batches)."""
    img = Image.new("RGB", (1000, 40 + 28 * lines), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=18)
    except TypeError:
        font = ImageFont.load_default()
    for i in range(lines):
        draw.text((20, 20 + 28 * i), f"CS {100 + i} " + "Introduction to Computing " * (1 + i % 5), fill="black", font=font)
    return np.asarray(img)


def test_rapidocr_runs_on_cuda_without_the_first_batch_failure_and_matches_cpu(tmp_path):
    path = tmp_path / "page.png"
    Image.fromarray(_page()).save(path)
    config = engines.find_config("rapidocr-en")
    gpu, gpu_providers = engines._rapidocr_engine(config, True)
    assert gpu_providers[0] == "CUDAExecutionProvider"
    on_gpu = gpu(str(path))  # a many-batch page: failed before the warm-up in _rapidocr_engine
    cpu, _ = engines._rapidocr_engine(config, False)
    on_cpu = cpu(str(path))
    assert len(on_gpu.txts) >= 30 and len(on_gpu.txts) == len(on_cpu.txts)
    # floating-point differences may change a character on an unreadable line; the text must still agree
    same = sum(difflib.SequenceMatcher(None, a, b).ratio() for a, b in zip(on_gpu.txts, on_cpu.txts)) / len(on_gpu.txts)
    assert same >= 0.98
