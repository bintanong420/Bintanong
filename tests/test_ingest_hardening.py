"""Task 1 (Phase 2 draft): ingest.py refuses instead of fabricating text, pages or digests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from backend.bintanong_tools import ingest
from backend.bintanong_tools.prospectus_extractor import docling_env
from backend.bintanong_tools.prospectus_extractor.identity import file_sha256

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "synthetic_academic_guide.pdf"
PDF_BYTES = FIXTURE.read_bytes()


class StubConverter:
    def __init__(self, pages=2, text="Hello", mutate=None, boom=None):
        self.pages, self.text, self.mutate, self.boom = pages, text, mutate, boom

    def convert(self, source):
        if self.boom:
            raise self.boom
        if self.mutate:
            Path(source).write_bytes(self.mutate)
        doc = SimpleNamespace(
            pages={i + 1: object() for i in range(self.pages)},
            export_to_markdown=lambda: self.text,
        )
        return SimpleNamespace(document=doc)


def _pdf(tmp_path: Path, name: str = "a.pdf", data: bytes = PDF_BYTES) -> Path:
    path = tmp_path / name
    path.write_bytes(data)
    return path


def _stub(**kw):
    return mock.patch.object(ingest, "_converter", lambda: StubConverter(**kw))


def test_docling_unavailable_raises_and_returns_nothing(tmp_path):
    with mock.patch.object(
        docling_env, "load_docling", side_effect=docling_env.DoclingUnavailable("no docling")
    ):
        with pytest.raises(docling_env.DoclingUnavailable):
            ingest.parse_document(_pdf(tmp_path))


def test_missing_path_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        ingest.parse_document(tmp_path / "nope.pdf")


@pytest.mark.parametrize("name", ["a.txt", "a.docx", "a.jpg", "noext"])
def test_unsupported_suffixes_refused(tmp_path, name):
    path = _pdf(tmp_path, name)
    with _stub():
        with pytest.raises(ingest.UnsupportedDocument):
            ingest.parse_document(path)


def test_directory_refused(tmp_path):
    folder = tmp_path / "d.pdf"
    folder.mkdir()
    with _stub():
        with pytest.raises(ingest.UnsupportedDocument):
            ingest.parse_document(folder)


def test_suffix_check_is_case_insensitive(tmp_path):
    with _stub():
        result = ingest.parse_document(_pdf(tmp_path, "UPPER.PDF"))
    assert result["title"] == "UPPER"


def test_garbage_bytes_named_pdf_refused_with_real_docling(tmp_path):
    with pytest.raises(ingest.ConversionFailed):
        ingest.parse_document(_pdf(tmp_path, "g.pdf", b"not a pdf at all"))


def test_converter_error_is_named(tmp_path):
    with _stub(boom=RuntimeError("bad")):
        with pytest.raises(ingest.ConversionFailed):
            ingest.parse_document(_pdf(tmp_path))


def test_zero_pages_refused(tmp_path):
    with _stub(pages=0):
        with pytest.raises(ingest.EmptyDocument):
            ingest.parse_document(_pdf(tmp_path))


@pytest.mark.parametrize("text", ["", "   \n\t "])
def test_empty_text_refused(tmp_path, text):
    with _stub(text=text):
        with pytest.raises(ingest.EmptyDocument):
            ingest.parse_document(_pdf(tmp_path))


def test_result_shape_digest_and_no_fabrication(tmp_path):
    path = _pdf(tmp_path, "My Doc.pdf")
    with _stub(pages=3, text="body"):
        result = ingest.parse_document(path)
    assert result["format"] == "docling_markdown"
    assert result["num_pages"] == 3
    assert result["sha256"] == file_sha256(path)
    assert len(result["conversion_identity"]) == 64
    assert result["metadata"] == {"source": "My Doc.pdf"}
    assert set(result) >= {"title", "text", "num_pages", "metadata"}
    assert "text_extracted" not in json.dumps(result)
    assert str(tmp_path) not in json.dumps(result)


def test_input_changed_midrun_raises(tmp_path):
    with _stub(mutate=PDF_BYTES + b"\n%tail"):
        with pytest.raises(ValueError, match="changed"):
            ingest.parse_document(_pdf(tmp_path))


def test_cli_stdout_is_json_only_when_conversion_prints(tmp_path, capsys):
    def noisy(path):
        print("[*] Acceleration: CPU")
        return {"title": "t", "text": "x"}

    with mock.patch.object(ingest, "parse_document", noisy):
        ingest.parse_cmd(_pdf(tmp_path), None)
    out, err = capsys.readouterr()
    assert json.loads(out) == {"title": "t", "text": "x"}
    assert "Acceleration" in err


def test_cli_refusal_exits_nonzero_with_empty_stdout(tmp_path, capsys):
    import click

    with pytest.raises(click.exceptions.Exit) as exc:
        ingest.parse_cmd(_pdf(tmp_path, "a.txt"), None)
    assert exc.value.exit_code == 1
    out, err = capsys.readouterr()
    assert out == ""
    assert "a.txt" in err


def test_real_cli_stdout_parses_as_json():
    proc = subprocess.run(
        [sys.executable, "-m", "backend.bintanong_tools.ingest", str(FIXTURE)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    assert result["format"] == "docling_markdown" and result["num_pages"] >= 1
    assert result["sha256"] == file_sha256(FIXTURE)


_BLOCKED = (
    "import sys, runpy\n"
    "for m in ('docling', 'docling_core', 'docling_parse'): sys.modules[m] = None\n"
    "sys.argv = ['ingest', '--help']\n"
    "runpy.run_module('{mod}', run_name='__main__')\n"
)


@pytest.mark.parametrize("mod", ["backend.bintanong_tools.ingest", "bintanong_tools.ingest"])
def test_help_works_with_docling_blocked_in_both_import_roots(mod):
    cwd = ROOT if mod.startswith("backend") else ROOT / "backend"
    proc = subprocess.run(
        [sys.executable, "-c", _BLOCKED.format(mod=mod)], cwd=cwd, capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr
    assert "ingest" in proc.stdout.lower()


def test_ingest_uses_relative_imports_only():
    source = (ROOT / "backend" / "bintanong_tools" / "ingest.py").read_text(encoding="utf-8")
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith(("from backend", "from bintanong_tools", "import backend")):
            pytest.fail(f"absolute package import: {stripped}")


@pytest.mark.parametrize("alias", ["identical", "normalized", "case", "hardlink", "symlink"])
def test_cli_output_alias_refused_preserves_source(tmp_path, alias):
    from typer.testing import CliRunner

    source = _pdf(tmp_path, "source.pdf")
    if alias == "identical":
        output = source
    elif alias == "normalized":
        folder = tmp_path / "folder"
        folder.mkdir()
        output = folder / ".." / source.name
    elif alias == "case":
        output = source.with_name("SOURCE.PDF")
        if not output.exists() or not output.samefile(source):
            pytest.skip("filesystem is case-sensitive")
    else:
        output = tmp_path / "alias.json"
        try:
            if alias == "hardlink":
                output.hardlink_to(source)
            else:
                output.symlink_to(source)
        except OSError as exc:
            pytest.skip(f"{alias} unavailable: {exc}")
    with _stub():
        result = CliRunner().invoke(ingest.app, [str(source), "-o", str(output)])
    assert result.exit_code != 0, result.output
    assert source.read_bytes() == PDF_BYTES
    assert output.read_bytes() == PDF_BYTES
    assert result.stdout == ""


def test_real_cli_same_output_refused_preserves_source(tmp_path):
    source = _pdf(tmp_path, "source.pdf")
    proc = subprocess.run(
        [sys.executable, "-m", "backend.bintanong_tools.ingest", str(source), "-o", str(source)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert proc.returncode != 0, proc.stderr
    assert source.read_bytes() == PDF_BYTES
    assert proc.stdout == ""


def test_cli_output_alias_refused_before_conversion(tmp_path, capsys):
    import click

    source = _pdf(tmp_path)
    with mock.patch.object(ingest, "_converter", side_effect=AssertionError("conversion must not run")):
        with pytest.raises(click.exceptions.Exit) as exc:
            ingest.parse_cmd(source, source)
    assert exc.value.exit_code == 1
    assert source.read_bytes() == PDF_BYTES
    assert capsys.readouterr().out == ""


def test_cli_separate_output_preserves_source_and_writes_json(tmp_path, capsys):
    source = _pdf(tmp_path)
    output = tmp_path / "parsed.json"
    with _stub():
        ingest.parse_cmd(source, output)
    assert source.read_bytes() == PDF_BYTES
    assert json.loads(output.read_text(encoding="utf-8"))["text"] == "Hello"
    assert capsys.readouterr().out == ""



def test_cli_output_alias_created_during_conversion_refused(tmp_path, capsys):
    import click

    source = _pdf(tmp_path)
    output = tmp_path / "parsed.json"
    converter = StubConverter()
    real = converter.convert

    def link_then_convert(path):
        output.hardlink_to(source)
        return real(path)

    converter.convert = link_then_convert
    with mock.patch.object(ingest, "_converter", return_value=converter):
        with pytest.raises(click.exceptions.Exit) as exc:
            ingest.parse_cmd(source, output)
    assert exc.value.exit_code == 1
    assert source.read_bytes() == PDF_BYTES
    assert output.read_bytes() == PDF_BYTES
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("alias", ["hardlink", "symlink"])
def test_cli_writer_boundary_alias_preserves_source(tmp_path, monkeypatch, alias):
    source = _pdf(tmp_path)
    output = tmp_path / "parsed.json"
    real = ingest._check_output_path
    checks = 0

    def alias_after_final_check(path, target):
        nonlocal checks
        real(path, target)
        checks += 1
        if checks == 2:
            if alias == "hardlink":
                output.hardlink_to(source)
            else:
                output.symlink_to(source)

    monkeypatch.setattr(ingest, "_check_output_path", alias_after_final_check)
    with _stub():
        ingest.parse_cmd(source, output)
    assert source.read_bytes() == PDF_BYTES
    assert json.loads(output.read_text(encoding="utf-8"))["text"] == "Hello"
    assert not output.samefile(source)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.pdf", "parsed.json"]


def test_cli_output_publish_failure_preserves_source_and_existing_output(tmp_path, monkeypatch):
    from backend.bintanong_tools.prospectus_extractor import publish

    source = _pdf(tmp_path)
    output = tmp_path / "parsed.json"
    output.write_text("previous output", encoding="utf-8")

    def locked(*args, **kwargs):
        raise PermissionError("output is locked")

    monkeypatch.setattr(publish, "replace_file", locked)
    with _stub(), pytest.raises(PermissionError):
        ingest.parse_cmd(source, output)
    assert source.read_bytes() == PDF_BYTES
    assert output.read_text(encoding="utf-8") == "previous output"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.pdf", "parsed.json"]
