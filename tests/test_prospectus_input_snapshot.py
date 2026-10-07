"""One captured input supplies conversion, identity, and publication checks."""

from dataclasses import FrozenInstanceError
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.bintanong_tools import prospectus
from backend.bintanong_tools.prospectus_extractor import batch, identity, loader, pipeline
from backend.bintanong_tools.prospectus_extractor.pipeline import build_payload as real_build_payload
from conftest import FakeDoc, RAW_BASE

pytestmark = pytest.mark.usefixtures("fake_docling", "pipeline_state")


def converted(source):
    body = source.stream.read() if hasattr(source, "stream") else Path(source).read_bytes()
    return SimpleNamespace(errors=[], document=FakeDoc({**RAW_BASE, "marker": body.decode("latin-1")}))


def test_same_size_restored_mtime_change_during_conversion_preserves_publication(
    tmp_path, pdf_factory, converter, process, snapshot
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    before = snapshot(out)
    original_stat = pdf.stat()

    def mutate(source):
        result = converted(source)
        pdf.write_bytes(b"%PDF-two")
        os.utime(pdf, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
        return result

    with pytest.raises(ValueError, match="Input bytes changed"):
        process(pdf, out, SimpleNamespace(convert=mutate), force_reconvert=True)
    assert snapshot(out) == before
    assert (out / "failed" / "a" / "failure.json").is_file()


def test_standalone_loader_refuses_changed_source_before_overwriting_cache(
    tmp_path, pdf_factory, converter
):
    pdf = pdf_factory(tmp_path / "in")
    raw = tmp_path / "out" / "a_docling.json"
    loader.load_document(pdf, converter=converter, raw_json_path=raw)
    meta = loader._cache_meta_path(raw)
    before = (raw.read_bytes(), meta.read_bytes())

    def mutate(source):
        result = converted(source)
        pdf.write_bytes(b"%PDF-two")
        return result

    with pytest.raises(ValueError, match="Input bytes changed"):
        loader.load_document(pdf, converter=SimpleNamespace(convert=mutate), raw_json_path=raw)
    assert (raw.read_bytes(), meta.read_bytes()) == before


def test_conversion_uses_capture_even_when_original_changes_before_conversion(tmp_path, pdf_factory):
    pdf = pdf_factory(tmp_path)
    captured = identity.InputSnapshot(pdf)
    pdf.write_bytes(b"%PDF-two")
    loaded = loader.load_document_result(
        pdf, converter=SimpleNamespace(convert=converted), snapshot=captured, stage_dir=tmp_path / "stage",
    )
    assert loaded.document.docling_document.raw["marker"] == "%PDF-one"
    assert loaded.raw_json_sha256 == hashlib.sha256(loaded.raw_json_bytes).hexdigest()


def test_snapshot_cannot_be_reassigned_or_attached_to_another_path(tmp_path, pdf_factory):
    pdf = pdf_factory(tmp_path)
    captured = identity.InputSnapshot(pdf)
    with pytest.raises(FrozenInstanceError):
        captured.data = b"other"
    other = pdf_factory(tmp_path, name="other.pdf")
    with pytest.raises(ValueError, match="Snapshot path"):
        loader.load_document_result(other, snapshot=captured)


def test_one_input_digest_supplies_source_run_and_cache_identity(
    tmp_path, monkeypatch, pdf_factory, converter, process
):
    pdf = pdf_factory(tmp_path / "in")
    digested = []
    real_digest = identity.bytes_sha256

    def digest(body):
        if body == b"%PDF-one":
            digested.append(body)
        return real_digest(body)

    monkeypatch.setattr(identity, "bytes_sha256", digest)
    source = prospectus.ProvisionalSource(hashlib.sha256(b"%PDF-one").hexdigest(), "local/a.pdf")
    payload = process(pdf, tmp_path / "out", converter, source=source)
    assert payload["run_identity"]["pdf_sha256"] == source.pdf_sha256
    assert digested == [b"%PDF-one"]


def test_reused_cache_result_retains_exact_parsed_json_and_meta_bytes(
    tmp_path, monkeypatch, pdf_factory, converter
):
    pdf = pdf_factory(tmp_path / "in")
    raw = tmp_path / "out" / "a_docling.json"
    first = loader.load_document(pdf, converter=converter, raw_json_path=raw)
    assert len(first) == 2  # public callers still unpack document and path
    raw_bytes = raw.read_bytes()
    meta_path = loader._cache_meta_path(raw)
    meta_bytes = meta_path.read_bytes()
    real_read = Path.read_bytes

    def read(path):
        body = real_read(path)
        if path == raw:
            path.write_bytes(b'{"marker": "other"}')
        elif path == meta_path:
            path.write_bytes(b'{}')
        return body

    monkeypatch.setattr(Path, "read_bytes", read)
    loaded = loader.load_document_result(pdf, force_reconvert=False, converter=converter, raw_json_path=raw)
    assert loaded.document.docling_document.raw["marker"] == "%PDF-one"
    assert loaded.cache_status == "reused"
    assert loaded.raw_json_bytes == raw_bytes
    assert loaded.meta_bytes == meta_bytes
    assert loaded.raw_json_sha256 == hashlib.sha256(raw_bytes).hexdigest()
    assert loaded.meta_sha256 == hashlib.sha256(meta_bytes).hexdigest()
    assert len(converter.calls) == 1


def test_backend_retry_receives_a_fresh_capture_stream_with_original_filename(tmp_path, monkeypatch, pdf_factory):
    pdf = pdf_factory(tmp_path, name="original filename.pdf")
    sources = []

    def primary(source):
        sources.append(source)
        assert source.stream.read() == b"%PDF-one"
        return SimpleNamespace(errors=["std::bad_alloc"], document=None)

    def fallback(source):
        sources.append(source)
        return converted(source)

    monkeypatch.setattr(loader, "get_shared_converter", lambda **kwargs: SimpleNamespace(convert=fallback))
    document, _ = loader.load_document(pdf, converter=SimpleNamespace(convert=primary))
    assert document.docling_document.raw["marker"] == "%PDF-one"
    assert [source.name for source in sources] == [pdf.name, pdf.name]
    assert sources[0].stream is not sources[1].stream


def test_json_input_is_parsed_from_the_same_capture_used_for_identity(tmp_path):
    raw = tmp_path / "review.json"
    raw.write_bytes(json.dumps({**RAW_BASE, "marker": "original"}).encode())
    captured = identity.InputSnapshot(raw)
    raw.write_bytes(b'{}')
    loaded = loader.load_document_result(raw, snapshot=captured)
    run = identity.run_identity(raw, None, snapshot=captured)
    assert loaded.document.docling_document.raw["marker"] == "original"
    assert run["input_sha256"] == captured.sha256
    assert run["review_input_only"] is True


def test_batch_captures_one_item_at_a_time_and_reuses_skip_identity(
    tmp_path, monkeypatch, pdf_factory, converter
):
    root = tmp_path / "in"
    first = pdf_factory(root)
    second = pdf_factory(root, name="b.pdf", body=b"%PDF-two")
    out = tmp_path / "out"
    config = batch.BatchConfig(input_root=root, output_root=out, semantic_doc=None,
                               skip_existing=True, write_md=False)
    monkeypatch.setattr(loader, "get_shared_converter", lambda **kwargs: converter)
    assert batch.run_batch(config)["succeeded"] == 2
    reads = []
    real_read = Path.read_bytes

    def read(path):
        if path in (first, second):
            reads.append(path.name)
        return real_read(path)

    monkeypatch.setattr(Path, "read_bytes", read)
    (out / "a_publish.json").unlink()
    result = batch.run_batch(config)
    assert result["succeeded"] == 1 and result["skipped"] == 1
    assert reads == ["a.pdf", "a.pdf", "b.pdf"]  # capture, prepublish check, next capture


def test_batch_cache_reparse_does_not_initialize_a_converter(tmp_path, monkeypatch, pdf_factory, converter):
    root = tmp_path / "in"
    pdf_factory(root)
    out = tmp_path / "out"
    config = batch.BatchConfig(input_root=root, output_root=out, semantic_doc=None, write_md=False)
    monkeypatch.setattr(loader, "get_shared_converter", lambda **kwargs: converter)
    assert batch.run_batch(config)["succeeded"] == 1

    def unexpected(**kwargs):
        raise AssertionError("cache reparse initialized a converter")

    monkeypatch.setattr(loader, "get_shared_converter", unexpected)
    assert batch.run_batch(config)["succeeded"] == 1


def test_batch_processes_a_captured_item_when_skip_check_is_unreadable(
    tmp_path, monkeypatch, pdf_factory, converter
):
    root = tmp_path / "in"
    pdf_factory(root)
    config = batch.BatchConfig(input_root=root, output_root=tmp_path / "out",
                               semantic_doc=None, skip_existing=True, write_md=False)
    monkeypatch.setattr(loader, "get_shared_converter", lambda **kwargs: converter)

    def unreadable(*args, **kwargs):
        raise OSError("manifest temporarily unreadable")

    monkeypatch.setattr(batch, "skip_check", unreadable)
    result = batch.run_batch(config)
    assert result["succeeded"] == 1
    assert result["records"][0]["skip_check"] == "identity check failed: OSError: manifest temporarily unreadable"


SCIENCE_MAP = b"# College of Science (CS)\n- Bachelor of Science in Computer Science (BS CS)\n"
FINANCE_MAP = SCIENCE_MAP.replace(b"Science (CS)", b"Finance (CS)")


@pytest.mark.parametrize("mutation", ["same_size_restored_mtime", "deleted", "appeared"])
def test_semantic_map_changes_during_loading_preserve_prior_publication(tmp_path, monkeypatch, snapshot, mutation):
    source = tmp_path / "CS" / "review.json"
    source.parent.mkdir()
    source.write_bytes(json.dumps(RAW_BASE).encode())
    semantic = tmp_path / "map.md"
    if mutation != "appeared":
        semantic.write_bytes(SCIENCE_MAP)
    out = tmp_path / "out" / "review_prospectus.json"
    monkeypatch.setattr(pipeline, "build_payload", real_build_payload)
    pipeline.process_prospectus(source, out, semantic_doc_path=semantic, quiet=True)
    before = snapshot(out.parent)
    real_load = pipeline.load_document_result

    def mutate(*args, **kwargs):
        loaded = real_load(*args, **kwargs)
        if mutation == "deleted":
            semantic.unlink()
        elif mutation == "appeared":
            semantic.write_bytes(SCIENCE_MAP)
        else:
            original_stat = semantic.stat()
            semantic.write_bytes(FINANCE_MAP)
            os.utime(semantic, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
            assert semantic.stat().st_size == original_stat.st_size
        return loaded

    monkeypatch.setattr(pipeline, "load_document_result", mutate)
    with pytest.raises((ValueError, FileNotFoundError)):
        pipeline.process_prospectus(source, out, semantic_doc_path=semantic, quiet=True)
    assert snapshot(out.parent) == before
    assert (out.parent / "failed" / "review" / "failure.json").is_file()


def test_transient_semantic_edit_cannot_change_metadata_under_original_identity(tmp_path, monkeypatch):
    source = tmp_path / "CS" / "review.json"
    source.parent.mkdir()
    source.write_bytes(json.dumps(RAW_BASE).encode())
    semantic = tmp_path / "map.md"
    semantic.write_bytes(SCIENCE_MAP)
    real_load = pipeline.load_document_result

    def mutate(*args, **kwargs):
        loaded = real_load(*args, **kwargs)
        semantic.write_bytes(FINANCE_MAP)
        return loaded

    def restore_after_parse(*args, **kwargs):
        payload = real_build_payload(*args, **kwargs)
        semantic.write_bytes(SCIENCE_MAP)
        return payload

    monkeypatch.setattr(pipeline, "load_document_result", mutate)
    monkeypatch.setattr(pipeline, "build_payload", restore_after_parse)
    out = tmp_path / "out" / "review_prospectus.json"
    payload = pipeline.process_prospectus(source, out, semantic_doc_path=semantic, quiet=True)
    assert payload["college_name"] == "College of Science"
    assert payload["run_identity"]["semantic_sha256"] == hashlib.sha256(SCIENCE_MAP).hexdigest()


@pytest.mark.parametrize("present", [False, True])
def test_unchanged_optional_semantic_map_preserves_loader_and_identity_contract(tmp_path, monkeypatch, present):
    source = tmp_path / "CS" / "review.json"
    source.parent.mkdir()
    source.write_bytes(json.dumps(RAW_BASE).encode())
    semantic = tmp_path / "map.md"
    if present:
        semantic.write_bytes(SCIENCE_MAP)
    monkeypatch.setattr(pipeline, "build_payload", real_build_payload)
    out = tmp_path / "out" / "review_prospectus.json"
    payload = pipeline.process_prospectus(source, out, semantic_doc_path=semantic, quiet=True)
    expected_digest = hashlib.sha256(SCIENCE_MAP).hexdigest() if present else None
    assert payload["run_identity"]["semantic_sha256"] == expected_digest
    assert identity.run_identity(source, semantic)["semantic_sha256"] == expected_digest
    assert payload["college_name"] == ("College of Science" if present else None)
    assert len(loader.load_document(source)) == 2
