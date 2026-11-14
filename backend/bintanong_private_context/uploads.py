"""Private upload checks before any parsing (master 15.1 step 2, pre-phase research finding 4).

The type comes from the bytes alone; a filename or Content-Type is never consulted. Images open
with only the sniffed Pillow plugin, so other loaders (and their decompression-bomb gaps) never run.
Nothing here writes to disk or logs the content.
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from typing import AsyncIterable, Literal

import pypdfium2 as pdfium
from PIL import Image

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_PDF_PAGES = 20
MAX_IMAGE_PIXELS = 60_000_000

Kind = Literal['pdf', 'png', 'jpeg']
_SIGNATURES: tuple[tuple[bytes, Kind], ...] = (
    (b'%PDF-', 'pdf'),
    (b'\x89PNG\r\n\x1a\n', 'png'),
    (b'\xff\xd8\xff', 'jpeg'),
)


class UploadRejected(ValueError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class ValidatedUpload:
    kind: Kind
    data: bytes
    pages: int | None = None
    width: int | None = None
    height: int | None = None


async def read_capped(stream: AsyncIterable[bytes], limit: int = MAX_UPLOAD_BYTES) -> bytes:
    """Join a request body, refusing as soon as it passes the cap instead of buffering all of it."""
    buffer = bytearray()
    async for chunk in stream:
        buffer += chunk
        if len(buffer) > limit:
            raise UploadRejected('too_large')
    return bytes(buffer)


def sniff_type(data: bytes) -> Kind:
    """Size and leading signature only; parses nothing, so it is safe outside the parser job."""
    if len(data) > MAX_UPLOAD_BYTES:
        raise UploadRejected('too_large')
    kind = next((k for signature, k in _SIGNATURES if data.startswith(signature)), None)
    if kind is None:
        raise UploadRejected('unsupported_type')
    return kind


def validate_upload(data: bytes) -> ValidatedUpload:
    kind = sniff_type(data)
    return _check_pdf(data) if kind == 'pdf' else _check_image(data, kind)


def _check_pdf(data: bytes) -> ValidatedUpload:
    try:
        document = pdfium.PdfDocument(data)
    except pdfium.PdfiumError:
        raise UploadRejected('unreadable') from None
    try:
        pages = len(document)
    finally:
        document.close()
    if pages == 0:
        raise UploadRejected('unreadable')
    if pages > MAX_PDF_PAGES:
        raise UploadRejected('too_many_pages')
    return ValidatedUpload('pdf', data, pages=pages)


def _check_image(data: bytes, kind: Kind) -> ValidatedUpload:
    try:
        with Image.open(io.BytesIO(data), formats=[kind.upper()]) as image:
            width, height = image.size
            if width * height > MAX_IMAGE_PIXELS:
                raise UploadRejected('too_many_pixels')
            image.load()
    except UploadRejected:
        raise
    except Image.DecompressionBombError:
        raise UploadRejected('too_many_pixels') from None
    except (OSError, SyntaxError, ValueError):
        raise UploadRejected('unreadable') from None
    return ValidatedUpload(kind, data, width=width, height=height)
