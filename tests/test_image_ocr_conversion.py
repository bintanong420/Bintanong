import hashlib
import json
from types import SimpleNamespace

import pytest

from backend.bintanong_tools.knowledge_update import intake
from backend.bintanong_tools.knowledge_update.prepare import prepare
from backend.bintanong_tools.prospectus_extractor import docling_env, loader
from backend.bintanong_tools.prospectus_extractor.identity import InputSnapshot, conversion_identity
from test_knowledge_update_image_upload import image_bytes
from test_knowledge_update_prepare import manifest
from test_policy_chunks import item, raw_document
from test_prospectus_ingestion import synthetic_converter


@pytest.mark.parametrize('image', [False, True])
def test_only_image_uploads_enable_ocr_and_preserve_pending_review(tmp_path, monkeypatch, image):
    if image:
        made = intake.create_upload(tmp_path / 'uploads', image_bytes(), media_type='image/png',
            kind='handbook', title='Synthetic image', edition='2026')
        folder = tmp_path / 'uploads' / made['upload_id']
        path, source = folder / 'manifest.json', folder / 'derived/source.pdf'
    else:
        path, source, _ = manifest(tmp_path)
    converter = synthetic_converter(monkeypatch, InputSnapshot(source),
        raw_document([item('Synthetic instruction.')], pages=1), image_ocr=image)
    out = tmp_path / 'packet'
    packet = prepare(path, out, converter=converter)
    meta = json.loads(next(out.glob('candidates/*/conversion/raw_docling.meta.json')).read_text())
    settings = meta['conversion_settings']
    assert settings['do_ocr'] is image
    assert settings['force_backend_text'] is (not image)
    assert settings['ocr_languages'] == (['eng'] if image else [])
    assert ('image_ocr' in settings) is image
    assert meta['conversion_identity'] == conversion_identity(meta['pdf_sha256'], settings)
    assert packet['candidate_only'] and packet['items'][0]['fields'][0]['decision'] == 'pending'
    if image:
        assert settings['image_ocr']['eng_sha256'] == '2' * 64
        assert (out / packet['documents'][0]['original_image']['path']).read_bytes() == image_bytes()


def local_engine(tmp_path, monkeypatch):
    from backend.bintanong_tools.ocr_bench import engines
    exe = tmp_path / 'tesseract.exe'
    exe.write_bytes(b'synthetic executable')
    data = tmp_path / 'tessdata'
    data.mkdir()
    (data / 'eng.traineddata').write_bytes(b'synthetic english model')
    monkeypatch.setattr(engines, 'find_tesseract', lambda: str(exe))
    monkeypatch.setattr(docling_env.subprocess, 'run', lambda *a, **k:
        SimpleNamespace(stdout='tesseract synthetic-1\n', returncode=0))
    return exe, data


def test_ocr_identity_pins_installed_engine_model_and_bounded_scale(tmp_path, monkeypatch):
    exe, data = local_engine(tmp_path, monkeypatch)
    assert hasattr(docling_env, 'image_ocr_settings'), 'local image OCR settings are missing'
    settings = docling_env.image_ocr_settings()
    assert settings['do_ocr'] is True and settings['force_backend_text'] is False
    assert settings['ocr_languages'] == ['eng']
    engine = settings['image_ocr']
    assert engine['scale'] == 1.0 and engine['mode'] == 'full_page'
    assert engine['executable_sha256'] == hashlib.sha256(exe.read_bytes()).hexdigest()
    assert engine['eng_sha256'] == hashlib.sha256((data / 'eng.traineddata').read_bytes()).hexdigest()
    old = conversion_identity('a' * 64, settings)
    (data / 'eng.traineddata').write_bytes(b'updated synthetic model')
    assert conversion_identity('a' * 64, docling_env.image_ocr_settings()) != old


@pytest.mark.parametrize('missing', ['engine', 'model'])
def test_missing_local_ocr_assets_refuse_without_downloads(tmp_path, monkeypatch, missing):
    from backend.bintanong_tools.ocr_bench import engines
    _, data = local_engine(tmp_path, monkeypatch)
    assert hasattr(docling_env, 'image_ocr_settings'), 'local image OCR settings are missing'
    if missing == 'engine':
        monkeypatch.setattr(engines, 'find_tesseract', lambda: None)
    else:
        (data / 'eng.traineddata').unlink()
    with pytest.raises(RuntimeError, match='local.*Tesseract|eng.traineddata'):
        docling_env.image_ocr_settings()


@pytest.mark.parametrize('field,value', [('do_ocr', False), ('force_backend_text', True),
    ('scale', 3.0), ('lang', ['fil']), ('path', 'other-models')])
def test_injected_converter_cannot_misstate_ocr_settings(tmp_path, monkeypatch, field, value):
    _, source, _ = manifest(tmp_path)
    converter = synthetic_converter(monkeypatch, InputSnapshot(source),
        raw_document([item('Not produced by OCR.')], pages=1), image_ocr=True)
    options = converter.format_to_options['pdf'].pipeline_options
    setattr(options if field in ('do_ocr', 'force_backend_text') else options.ocr_options, field, value)
    with pytest.raises(ValueError, match='OCR.*settings|settings.*OCR'):
        loader.load_document_result(source, converter=converter, ocr=True,
            raw_json_path=tmp_path / 'raw.json')
    assert converter.calls == [] and not (tmp_path / 'raw.json').exists()


def test_assets_changing_during_ocr_refuse_before_cache_publication(tmp_path, monkeypatch):
    _, source, _ = manifest(tmp_path)
    converter = synthetic_converter(monkeypatch, InputSnapshot(source),
        raw_document([item('Synthetic instruction.')], pages=1), image_ocr=True)
    settings = loader.image_ocr_settings()
    answers = iter([settings, {**settings, 'image_ocr': {**settings['image_ocr'], 'eng_sha256': '3' * 64}}])
    monkeypatch.setattr(loader, 'image_ocr_settings', lambda: next(answers))
    with pytest.raises(ValueError, match='assets changed'):
        loader.load_document_result(source, converter=converter, ocr=True, raw_json_path=tmp_path / 'raw.json')
    assert len(converter.calls) == 1 and not (tmp_path / 'raw.json').exists()


def test_image_pipeline_uses_pinned_local_tesseract_and_input_resolution(tmp_path, monkeypatch):
    exe, data = local_engine(tmp_path, monkeypatch)
    assert hasattr(docling_env, 'image_ocr_settings'), 'local image OCR settings are missing'
    settings = docling_env.image_ocr_settings()
    monkeypatch.setattr(docling_env, 'load_docling', lambda: {
        'PdfPipelineOptions': lambda: SimpleNamespace(table_structure_options=SimpleNamespace()),
        'AcceleratorDevice': SimpleNamespace(CPU='cpu', CUDA='cuda'),
        'AcceleratorOptions': lambda **kw: SimpleNamespace(**kw),
        'TableFormerMode': SimpleNamespace(ACCURATE='accurate', FAST='fast'),
        'TesseractCliOcrOptions': lambda **kw: SimpleNamespace(**kw),
        'OcrMode': SimpleNamespace(FULL_PAGE='full_page')})
    monkeypatch.setattr(docling_env, 'check_cuda_environment', lambda: {'cuda_available': False, 'status_message': 'CPU'})
    options = docling_env.get_pipeline_options('cpu', settings=settings)
    assert options.do_ocr is True and options.force_backend_text is False
    ocr = options.ocr_options
    assert (ocr.tesseract_cmd, ocr.path, ocr.lang, ocr.scale, ocr.mode) == (
        str(exe), str(data), ['eng'], 1.0, 'full_page')
