from __future__ import annotations

import contextlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

import typer

app = typer.Typer(
    name="ingest",
    help="Bintanong document ingestion and parsing tool suite using Docling.",
    no_args_is_help=True,
)


class UnsupportedDocument(ValueError):
    """The input is not a regular file with a .pdf suffix."""


class ConversionFailed(RuntimeError):
    """Docling could not convert the input (corrupt or unreadable PDF)."""


class EmptyDocument(ValueError):
    """Docling returned no pages or no text; nothing is fabricated in its place."""


def _converter() -> Any:
    # Lazy: --help must work with Docling absent. Raises DoclingUnavailable if it is.
    from .prospectus_extractor.docling_env import get_shared_converter

    return get_shared_converter()


def parse_document(file_path: Path | str) -> Dict[str, Any]:
    """Convert one PDF with Docling; refuse rather than return invented text, pages or digests."""
    from .prospectus_extractor.identity import InputSnapshot, conversion_identity, conversion_settings

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file() or path.suffix.lower() != ".pdf":
        raise UnsupportedDocument(f"Unsupported document (a .pdf file is required): {path.name}")

    snapshot = InputSnapshot(path)
    converter = _converter()
    try:
        doc = converter.convert(str(path)).document
    except Exception as exc:
        raise ConversionFailed(f"Docling could not convert {path.name}: {exc}") from exc
    snapshot.verify_unchanged()

    num_pages = len(getattr(doc, "pages", None) or [])
    text = doc.export_to_markdown()
    if num_pages == 0:
        raise EmptyDocument(f"Docling returned zero pages for {path.name}")
    if not text.strip():
        raise EmptyDocument(f"Docling returned no text for {path.name}")
    return {
        "title": path.stem,
        "format": "docling_markdown",
        "text": text,
        "num_pages": num_pages,
        "sha256": snapshot.sha256,
        "conversion_identity": conversion_identity(snapshot.sha256, conversion_settings()),
        "metadata": {"source": path.name},
    }


def _check_output_path(path: Path, output: Path | None) -> None:
    if output and (output.resolve() == path.resolve() or (output.exists() and path.samefile(output))):
        raise ValueError("Output must not overwrite the input PDF")


@app.command("parse")
def parse_cmd(
    path: Path = typer.Argument(..., help="Path to a PDF to parse"),
    output: Path = typer.Option(None, "--output", "-o", help="Path to write JSON output"),
) -> None:
    """Parse a PDF with Docling and output structured content as JSON on stdout."""
    try:
        _check_output_path(path, output)
        # Conversion code prints progress to stdout; keep stdout JSON only.
        with contextlib.redirect_stdout(sys.stderr):
            res = parse_document(path)
        rendered = json.dumps(res, indent=2)
        _check_output_path(path, output)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        typer.echo(f"{type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(1)
    if output:
        from .prospectus_extractor.publish import replace_file

        # Replace the directory entry so a late file alias cannot truncate the input.
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent, delete_on_close=False) as staged:
            staged.write(rendered)
            staged.close()
            replace_file(Path(staged.name), output)
        typer.echo(f"Output saved to {output}", err=True)
    else:
        typer.echo(rendered)


if __name__ == "__main__":
    app()
