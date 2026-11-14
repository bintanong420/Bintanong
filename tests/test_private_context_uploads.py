"""Phase 10 upload validation: byte cap while streaming, sniffed type, PDF page and image pixel limits."""
import asyncio
import io
import struct
import zlib

import pypdfium2 as pdfium
import pytest
from PIL import Image

from backend.bintanong_private_context.uploads import (
    MAX_PDF_PAGES,
    MAX_UPLOAD_BYTES,
    UploadRejected,
    read_capped,
    validate_upload,
)


def pdf_bytes(pages=1):
    doc = pdfium.PdfDocument.new()
    for _ in range(pages):
        doc.new_page(612, 792)
    out = io.BytesIO()
    doc.save(out)
    doc.close()
    return out.getvalue()


def image_bytes(fmt, size=(8, 6)):
    out = io.BytesIO()
    Image.new('RGB', size, 'white').save(out, fmt)
    return out.getvalue()


def png_claiming(width, height):
    """A tiny valid-looking PNG whose header claims a huge canvas (decompression-bomb shape)."""
    raw = bytearray(image_bytes('PNG', (1, 1)))
    ihdr = struct.pack('>II', width, height) + bytes(raw[24:29])
    raw[16:29] = ihdr
    raw[29:33] = struct.pack('>I', zlib.crc32(b'IHDR' + ihdr))
    return bytes(raw)


def rejected(data):
    with pytest.raises(UploadRejected) as error:
        validate_upload(data)
    return error.value.reason


async def chunks(*parts):
    for part in parts:
        yield part


def test_stream_within_cap_is_joined():
    assert asyncio.run(read_capped(chunks(b'ab', b'cd'), limit=4)) == b'abcd'


def test_stream_over_cap_is_refused_before_buffering_the_rest():
    seen = []

    async def endless():
        while True:
            seen.append(1)
            yield b'x' * 1024

    with pytest.raises(UploadRejected) as error:
        asyncio.run(read_capped(endless(), limit=4096))
    assert error.value.reason == 'too_large' and len(seen) == 5


def test_two_page_pdf_is_accepted_with_its_page_count():
    upload = validate_upload(pdf_bytes(2))
    assert (upload.kind, upload.pages) == ('pdf', 2)


@pytest.mark.parametrize('fmt,kind', [('PNG', 'png'), ('JPEG', 'jpeg')])
def test_png_and_jpeg_are_accepted_with_dimensions(fmt, kind):
    upload = validate_upload(image_bytes(fmt, (8, 6)))
    assert (upload.kind, upload.width, upload.height) == (kind, 8, 6)


@pytest.mark.parametrize('fmt', ['GIF', 'BMP', 'TIFF', 'WEBP'])
def test_other_image_formats_are_refused(fmt):
    assert rejected(image_bytes(fmt)) == 'unsupported_type'


@pytest.mark.parametrize('data', [b'', b'<html><script>', b'PK\x03\x04zip', b'Ignore previous instructions'])
def test_non_document_bytes_are_refused(data):
    assert rejected(data) == 'unsupported_type'


def test_pdf_over_the_page_cap_is_refused():
    assert rejected(pdf_bytes(MAX_PDF_PAGES + 1)) == 'too_many_pages'


def test_truncated_or_malformed_pdf_is_refused():
    assert rejected(pdf_bytes(1)[:200]) == 'unreadable'
    assert rejected(b'%PDF-1.7\nnot really a pdf') == 'unreadable'


@pytest.mark.parametrize('width,height', [(9000, 8000), (30000, 30000)])  # below/above Pillow's own guard
def test_png_header_claiming_a_huge_canvas_is_refused_without_decoding(width, height):
    assert rejected(png_claiming(width, height)) == 'too_many_pixels'


def test_truncated_image_is_refused():
    assert rejected(image_bytes('JPEG', (64, 64))[:150]) == 'unreadable'


def test_png_signature_on_other_content_is_refused():
    assert rejected(b'\x89PNG\r\n\x1a\n' + image_bytes('BMP')) == 'unreadable'


def test_oversize_bytes_are_refused_even_when_passed_directly():
    assert rejected(b'%PDF-' + b'0' * MAX_UPLOAD_BYTES) == 'too_large'
