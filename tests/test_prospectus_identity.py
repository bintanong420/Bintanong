"""Identity of conversions and output sets: what changes it, what must not."""

from __future__ import annotations

import ast
import hashlib

import pytest

from backend.bintanong_tools import prospectus_batch
from backend.bintanong_tools.prospectus_extractor import identity

SETTINGS_VERSIONS = {"docling": "t1", "docling-core": "t1", "docling-parse": "t1"}


@pytest.fixture(autouse=True)
def fixed_versions(monkeypatch):
    monkeypatch.setattr(identity, "installed_versions", lambda: dict(SETTINGS_VERSIONS))
    monkeypatch.delenv("PALSU_DOCLING_CELL_MATCHING", raising=False)


def test_conversion_identity_is_stable_and_changes_with_each_conversion_input(monkeypatch):
    pdf = "a" * 64
    base = identity.conversion_identity(pdf, identity.conversion_settings())
    assert base == identity.conversion_identity(pdf, identity.conversion_settings())

    assert base != identity.conversion_identity("b" * 64, identity.conversion_settings())

    monkeypatch.setenv("PALSU_DOCLING_CELL_MATCHING", "false")
    assert base != identity.conversion_identity(pdf, identity.conversion_settings())
    monkeypatch.setenv("PALSU_DOCLING_CELL_MATCHING", "1")  # same behaviour as the default "true"
    assert base == identity.conversion_identity(pdf, identity.conversion_settings())

    monkeypatch.setattr(identity, "installed_versions",
                        lambda: {**SETTINGS_VERSIONS, "docling-parse": "t2"})
    assert base != identity.conversion_identity(pdf, identity.conversion_settings())


def test_ocr_settings_are_part_of_the_conversion_identity():
    pdf = "a" * 64
    born_digital = identity.conversion_identity(pdf, identity.conversion_settings())
    ocr = identity.conversion_identity(pdf, identity.conversion_settings(do_ocr=True, ocr_languages=["en"]))
    ocr_two = identity.conversion_identity(pdf, identity.conversion_settings(do_ocr=True, ocr_languages=["en", "fil"]))
    ocr_two_reordered = identity.conversion_identity(pdf, identity.conversion_settings(do_ocr=True, ocr_languages=["fil", "en"]))
    assert len({born_digital, ocr, ocr_two}) == 3
    assert ocr_two == ocr_two_reordered
    # languages are meaningless when OCR is off and must not split the cache
    assert born_digital == identity.conversion_identity(
        pdf, identity.conversion_settings(do_ocr=False, ocr_languages=["en"]))


def test_run_identity_changes_with_every_input(tmp_path):
    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF-one")
    semantic = tmp_path / "map.md"
    semantic.write_text("map one", encoding="utf-8")
    package = "c" * 64

    def key(**overrides):
        arguments = {"package_hash": package, "schema_version": "s1", **overrides}
        return identity.run_identity(arguments.pop("path", pdf), arguments.pop("semantic", semantic), **arguments)

    base = key()
    assert base["run_key"] == key()["run_key"]
    assert base["input_kind"] == "pdf"
    assert base["pdf_sha256"] == hashlib.sha256(b"%PDF-one").hexdigest()
    assert base["review_input_only"] is False

    assert key(package_hash="d" * 64)["run_key"] != base["run_key"]
    assert key(schema_version="s2")["run_key"] != base["run_key"]
    semantic.write_text("map two", encoding="utf-8")
    assert key()["run_key"] != base["run_key"]
    semantic.write_text("map one", encoding="utf-8")
    pdf.write_bytes(b"%PDF-two")
    assert key()["run_key"] != base["run_key"]


def test_docling_json_input_is_a_review_input(tmp_path):
    raw = tmp_path / "a_docling.json"
    raw.write_text("{}", encoding="utf-8")
    result = identity.run_identity(raw, None, package_hash="c" * 64, schema_version="s1")
    assert result["input_kind"] == "docling-json"
    assert result["review_input_only"] is True
    assert result["conversion_identity"] is None
    assert result["pdf_sha256"] is None
    assert result["semantic_sha256"] is None


def test_unsupported_input_type_is_refused(tmp_path):
    other = tmp_path / "a.png"
    other.write_bytes(b"x")
    with pytest.raises(ValueError, match="Unsupported input type"):
        identity.run_identity(other, None, package_hash="c" * 64, schema_version="s1")


def test_package_hash_is_shared_with_the_isolated_batch_runner():
    assert prospectus_batch.package_sha256 is identity.package_sha256
    assert prospectus_batch.PACKAGE_DIR == identity.PACKAGE_DIR


def test_package_never_imports_the_batch_runner():
    offenders = []
    for path in sorted(identity.PACKAGE_DIR.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.ImportFrom):
                names = [node.module or "", *[alias.name for alias in node.names]]
            elif isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            if any("prospectus_batch" in name for name in names):
                offenders.append(path.name)
    assert offenders == []


# One owner for the PDF hash (cross-phase rule: B2 fixer and the batch record route through identity).
def test_pdf_hash_has_one_owner(tmp_path):
    from backend.bintanong_tools.prospectus_extractor import course_checks, fixer_cli

    pdf = tmp_path / "a.pdf"
    pdf.write_bytes(b"%PDF-one")
    expected = hashlib.sha256(b"%PDF-one").hexdigest()
    assert identity.file_sha256(pdf) == expected
    assert course_checks.sha256 is identity.file_sha256
    assert fixer_cli.sha256 is identity.file_sha256


def test_fixer_reads_the_pdf_hash_phase_d_records():
    from backend.bintanong_tools.prospectus_extractor.fixer_cli import resolve_identity

    payload = {"run_identity": {"pdf_sha256": "e" * 64}}
    found = resolve_identity(payload)
    assert found["pdf_sha256"] == "e" * 64 and found["how"] == "run_identity"
    with pytest.raises(Exception, match="differs from the PDF hash the candidate recorded"):
        resolve_identity(payload, pdf_sha256="f" * 64)


from types import SimpleNamespace

from backend.bintanong_tools.prospectus_extractor import docling_env


def test_pipeline_options_follow_conversion_settings(monkeypatch):
    class Mode:
        ACCURATE = "accurate-enum"
        FAST = "fast-enum"

    class Device:
        CPU = "cpu-enum"
        CUDA = "cuda-enum"

    class Options:
        def __init__(self):
            self.table_structure_options = SimpleNamespace(mode=None, do_cell_matching=None)

    fake = {
        "PdfPipelineOptions": Options,
        "AcceleratorDevice": Device,
        "AcceleratorOptions": lambda device: SimpleNamespace(device=device),
        "TableFormerMode": Mode,
    }
    monkeypatch.setattr(docling_env, "load_docling", lambda: fake)
    monkeypatch.setattr(
        docling_env, "check_cuda_environment",
        lambda: {"cuda_available": False, "status_message": "no gpu", "cuda_device_name": None},
    )
    monkeypatch.setenv("PALSU_DOCLING_CELL_MATCHING", "off")

    options = docling_env.get_pipeline_options("cpu")
    assert options.do_ocr is False
    assert options.force_backend_text is True
    assert options.do_table_structure is True
    assert options.table_structure_options.mode == "accurate-enum"
    assert options.table_structure_options.do_cell_matching is False
    assert options.accelerator_options.device == "cpu-enum"

    ocr = docling_env.get_pipeline_options("cpu", settings=identity.conversion_settings(do_ocr=True))
    assert ocr.do_ocr is True
