"""Page images for the review GUI. Everything is rendered into memory; nothing is written to disk."""

from __future__ import annotations

import io
import math
from collections import OrderedDict
from pathlib import Path

DEFAULT_SCALE, MAX_SCALE = 1.5, 3
CACHE_SIZE = 8


class PageError(ValueError):
    """A page cannot be shown. `code` is missing_pdf, bad_pdf, bad_page or bad_scale; messages carry file names only."""

    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code


class PageRenderer:
    """pypdfium2 behind a small interface: page_count, size(n) and rotation(n) in points and degrees, png(n, scale)."""

    def __init__(self, pdf_path: Path):
        import pypdfium2 as pdfium

        self.name = Path(pdf_path).name
        if not Path(pdf_path).is_file():
            raise PageError(f"the PDF {self.name} was not found", "missing_pdf")
        try:
            self._pdf = pdfium.PdfDocument(str(pdf_path))
        except Exception as exc:  # pypdfium2 raises PdfiumError for a damaged file
            raise PageError(f"the PDF {self.name} cannot be opened", "bad_pdf") from exc
        self.page_count = len(self._pdf)
        self.render_count = 0
        self._cache: OrderedDict[tuple[int, float], bytes] = OrderedDict()

    def __enter__(self) -> "PageRenderer":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        self._pdf.close()

    def _page(self, number):
        if type(number) is not int or not 1 <= number <= self.page_count:
            raise PageError(f"page {number!r} is not in {self.name} (1 to {self.page_count})", "bad_page")
        return self._pdf[number - 1]

    def size(self, number: int) -> tuple[float, float]:
        page = self._page(number)
        try:
            return tuple(page.get_size())
        finally:
            page.close()

    def rotation(self, number: int) -> int:
        page = self._page(number)
        try:
            return int(page.get_rotation())
        finally:
            page.close()

    def png(self, number: int, scale: float = DEFAULT_SCALE) -> bytes:
        if isinstance(scale, bool) or not isinstance(scale, (int, float)) or not math.isfinite(scale) or not 0 < scale <= MAX_SCALE:
            raise PageError(f"scale must be above 0 and at most {MAX_SCALE}", "bad_scale")
        key = (number, float(scale))
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        page = self._page(number)
        try:
            buffer = io.BytesIO()
            page.render(scale=float(scale)).to_pil().save(buffer, format="PNG")
        finally:
            page.close()
        self.render_count += 1
        self._cache[key] = buffer.getvalue()
        while len(self._cache) > CACHE_SIZE:
            self._cache.popitem(last=False)
        return self._cache[key]
