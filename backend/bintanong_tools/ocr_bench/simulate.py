"""Deterministic phone-photo simulation of rendered PDF pages.

Every random draw comes from a numpy Generator seeded by sha256(seed | condition | salt), so one
(seed, condition, page) always yields the same JPEG bytes in the same environment. Conditions are
fixed and named; the plan cites them by name. Pipeline: geometry (tilt, perspective, on a desk
background) -> light (brightness, shadow gradient) -> blur -> sensor noise -> JPEG.
"""

from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import cv2
import numpy as np
from PIL import Image

DESK = (38, 40, 46)  # dark desk colour shown where the page does not reach the frame edge


@dataclass(frozen=True)
class Condition:
    name: str
    rotate_deg: float = 0.0     # maximum tilt; the drawn angle is 0.6-1.0 of this, either direction
    perspective: float = 0.0    # maximum corner shift as a fraction of page size
    blur_sigma: float = 0.0
    brightness: float = 1.0
    shadow: float = 0.0         # light falloff across the page, 0 none, 1 black at one edge
    noise_sigma: float = 0.0
    jpeg_quality: int = 90


CONDITIONS = {c.name: c for c in (
    Condition("flat_good", jpeg_quality=92),
    Condition("tilt", rotate_deg=5.0, jpeg_quality=90),
    Condition("perspective", perspective=0.04, jpeg_quality=90),
    Condition("blur", blur_sigma=1.6, jpeg_quality=88),
    Condition("dim", brightness=0.45, shadow=0.35, jpeg_quality=88),
    Condition("noisy", noise_sigma=14.0, jpeg_quality=75),
    Condition("hard", rotate_deg=4.0, perspective=0.03, blur_sigma=1.1, brightness=0.6, shadow=0.3,
              noise_sigma=9.0, jpeg_quality=70),
)}


def _rng(seed: int, name: str, salt: str) -> np.random.Generator:
    digest = hashlib.sha256(f"{seed}|{name}|{salt}".encode("utf-8")).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "big"))


def _geometry(img: np.ndarray, cond: Condition, rng: np.random.Generator) -> np.ndarray:
    if not (cond.rotate_deg or cond.perspective):
        return img
    h, w = img.shape[:2]
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    centre = np.float32([w / 2, h / 2])
    pts = (src - centre) * 0.88  # leave desk around the page so the tilt does not clip text
    if cond.rotate_deg:
        angle = np.radians(cond.rotate_deg * rng.uniform(0.6, 1.0) * rng.choice([-1.0, 1.0]))
        rot = np.float32([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        pts = pts @ rot.T
    if cond.perspective:
        pts = pts + rng.uniform(-1.0, 1.0, (4, 2)).astype(np.float32) * cond.perspective * np.float32([w, h])
    dst = (pts + centre).astype(np.float32)
    matrix = cv2.getPerspectiveTransform(src, dst)
    return cv2.warpPerspective(img, matrix, (w, h), flags=cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_CONSTANT, borderValue=DESK)


def simulate_array(rgb: np.ndarray, name: str, seed: int, salt: str = "") -> np.ndarray:
    """The simulated photo as an RGB uint8 array (before JPEG)."""
    if name not in CONDITIONS:
        raise ValueError(f"unknown condition {name!r}; use one of {', '.join(sorted(CONDITIONS))}")
    cond = CONDITIONS[name]
    rng = _rng(seed, name, salt)
    img = _geometry(np.ascontiguousarray(rgb, dtype=np.uint8), cond, rng)
    out = img.astype(np.float32)
    if cond.brightness != 1.0:
        out *= cond.brightness
    if cond.shadow:
        h, w = out.shape[:2]
        ramp = np.linspace(1.0, 1.0 - cond.shadow, w, dtype=np.float32)
        if rng.random() < 0.5:
            ramp = ramp[::-1]
        out *= ramp[None, :, None]
    out = np.clip(out, 0, 255).astype(np.uint8)
    if cond.blur_sigma:
        out = cv2.GaussianBlur(out, (0, 0), cond.blur_sigma)
    if cond.noise_sigma:
        noise = rng.normal(0.0, cond.noise_sigma, out.shape).astype(np.float32)
        out = np.clip(out.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return out


def simulate_image(rgb: np.ndarray, name: str, seed: int, salt: str = "") -> bytes:
    """JPEG bytes of the simulated photo. SALT (for example "doc/p3") keeps pages' randomness apart."""
    out = simulate_array(rgb, name, seed, salt)
    buffer = io.BytesIO()
    Image.fromarray(out).save(buffer, format="JPEG", quality=CONDITIONS[name].jpeg_quality, optimize=False,
                              progressive=False, subsampling=2)
    return buffer.getvalue()


def render_page(pdf_path: Path, page_index: int, dpi: int = 150) -> np.ndarray:
    """One PDF page as an RGB uint8 array (pypdfium2)."""
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        page = pdf[page_index]
        try:
            return np.asarray(page.render(scale=dpi / 72).to_pil().convert("RGB"))
        finally:
            page.close()
    finally:
        pdf.close()


def page_count(pdf_path: Path) -> int:
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        return len(pdf)
    finally:
        pdf.close()


def simulate_pdf(pdf_path: Path, out_dir: Path, conditions: Sequence[str] | Iterable[str], seed: int,
                 dpi: int = 150, pages: Sequence[int] | None = None) -> list[Path]:
    """Write `<stem>_pNN_<condition>.jpg` for each 1-based page and condition; return the paths.
    Pages outside the document are skipped."""
    pdf_path, out_dir = Path(pdf_path), Path(out_dir)
    conditions = list(conditions)
    for name in conditions:
        if name not in CONDITIONS:
            raise ValueError(f"unknown condition {name!r}; use one of {', '.join(sorted(CONDITIONS))}")
    total = page_count(pdf_path)
    wanted = [p for p in (pages if pages else range(1, total + 1)) if 1 <= p <= total]
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for number in wanted:
        base = render_page(pdf_path, number - 1, dpi)
        for name in conditions:
            target = out_dir / f"{pdf_path.stem}_p{number:02d}_{name}.jpg"
            target.write_bytes(simulate_image(base, name, seed, salt=f"{pdf_path.stem}/p{number}"))
            written.append(target)
    return written
