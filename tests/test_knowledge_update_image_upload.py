"""Synthetic image uploads retain their bytes and use a separately derived PDF for review."""
import hashlib
from io import BytesIO
import json

from PIL import Image
import pymupdf
import pytest

from backend.bintanong_tools.knowledge_update import intake
from backend.bintanong_tools.knowledge_update.manifest import load_manifest
from backend.bintanong_tools.knowledge_update.prepare import prepare, load_packet
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot
from test_knowledge_update_intake import client, headers, meta
from test_knowledge_update_review import packet, session  # noqa: F401
from test_policy_chunks import item, raw_document
from test_prospectus_ingestion import synthetic_converter


def image_bytes(kind='PNG', *, exif=None):
    out = BytesIO()
    with Image.new('RGB', (80, 40), 'white') as image:
        image.putpixel((10, 10), (255, 0, 0))
        image.save(out, format=kind, **({'exif': exif} if exif else {}))
    return out.getvalue()


@pytest.mark.parametrize('kind, media_type, extension', [('PNG', 'image/png', 'png'),
    ('JPEG', 'image/jpeg', 'jpg'), ('WEBP', 'image/webp', 'webp')])
def test_images_keep_original_bytes_and_have_a_separate_single_page_pdf(tmp_path, kind, media_type, extension):
    original = image_bytes(kind)
    made = intake.create_upload(tmp_path, original, media_type=media_type, **meta())
    folder = tmp_path / made['upload_id']
    assert (folder / f'original/source.{extension}').read_bytes() == original
    doc = load_manifest(folder / 'manifest.json')['documents'][0]
    assert doc['source'] == str(folder / 'derived/source.pdf')
    assert doc['original_image']['sha256'] == hashlib.sha256(original).hexdigest()
    assert doc['original_image']['media_type'] == media_type
    note = json.loads((folder / 'upload.json').read_text())
    assert note['original_sha256'] == hashlib.sha256(original).hexdigest()
    assert note['media_type'] == media_type and note['candidate_only'] is True
    with pymupdf.open(doc['source']) as pdf:
        assert len(pdf) == 1
        assert tuple(pdf[0].rect)[2:] == (80, 40)


def test_image_orientation_and_alpha_survive_as_visible_review_content(tmp_path):
    exif = Image.Exif()
    exif[274] = 6
    made = intake.create_upload(tmp_path, image_bytes('JPEG', exif=exif), media_type='image/jpeg', **meta())
    with pymupdf.open(tmp_path / made['upload_id'] / 'derived/source.pdf') as pdf:
        assert (pdf[0].rect.width, pdf[0].rect.height) == (40, 80)
    stream = BytesIO()
    with Image.new('RGBA', (10, 10), (0, 0, 0, 0)) as image:
        image.save(stream, format='PNG')
    made = intake.create_upload(tmp_path, stream.getvalue(), media_type='image/png', **meta())
    with pymupdf.open(tmp_path / made['upload_id'] / 'derived/source.pdf') as pdf:
        assert tuple(pdf[0].get_pixmap().samples[:3]) == (255, 255, 255)


@pytest.mark.parametrize('data, media_type', [(b'not an image', 'image/png'),
    (image_bytes('PNG'), 'image/jpeg'), (image_bytes('JPEG')[:50], 'image/jpeg'),
    (b'%PDF-synthetic', 'image/webp')])
def test_invalid_or_mislabeled_images_are_refused_before_writing(tmp_path, data, media_type):
    with pytest.raises(ValueError):
        intake.create_upload(tmp_path, data, media_type=media_type, **meta())
    assert list(tmp_path.iterdir()) == []


def test_animated_and_oversized_images_are_refused(tmp_path, monkeypatch):
    stream = BytesIO()
    with Image.new('RGB', (10, 10), 'white') as first, Image.new('RGB', (10, 10), 'black') as second:
        first.save(stream, format='WEBP', save_all=True, append_images=[second], duration=100)
    with pytest.raises(ValueError, match='single|animated'):
        intake.create_upload(tmp_path, stream.getvalue(), media_type='image/webp', **meta())
    monkeypatch.setattr(intake, 'MAX_IMAGE_PIXELS', 100)
    with pytest.raises(ValueError, match='pixel'):
        intake.create_upload(tmp_path, image_bytes(), media_type='image/png', **meta())
    assert list(tmp_path.iterdir()) == []


def test_upload_route_accepts_image_bytes_but_refuses_mime_spoofing(packet, tmp_path):
    root, _ = packet
    with session(root) as review, client(review, tmp_path / 'uploads') as web:
        response = web.post('/api/intake/upload', params=meta(), content=image_bytes(),
            headers=headers(**{'content-type': 'image/png'}))
        assert response.status_code == 200, response.text
        spoof = web.post('/api/intake/upload', params=meta(), content=image_bytes(),
            headers=headers(**{'content-type': 'image/jpeg'}))
        assert spoof.status_code == 422


def test_prepare_keeps_verified_original_image_in_packet_and_detects_tampering(tmp_path, monkeypatch):
    original = image_bytes()
    made = intake.create_upload(tmp_path / 'uploads', original, media_type='image/png', **meta())
    folder = tmp_path / 'uploads' / made['upload_id']
    source = folder / 'derived/source.pdf'
    out = tmp_path / 'packet'
    prepared = prepare(folder / 'manifest.json', out,
        converter=synthetic_converter(monkeypatch, InputSnapshot(source), raw_document([item('Synthetic instruction.')], pages=1)))
    doc = prepared['documents'][0]
    assert (out / doc['original_image']['path']).read_bytes() == original
    assert all(field['decision'] == 'pending' for row in prepared['items'] for field in row['fields'])
    assert load_packet(out) == prepared
    (out / doc['original_image']['path']).write_bytes(b'tampered')
    with pytest.raises(ValueError, match='digest'):
        load_packet(out)
    (folder / 'original/source.png').write_bytes(b'tampered')
    with pytest.raises(ValueError, match='image.*identity'):
        load_manifest(folder / 'manifest.json')
