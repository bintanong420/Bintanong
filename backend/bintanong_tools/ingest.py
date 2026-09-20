from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
import typer

app = typer.Typer(
    name="ingest",
    help="Bintanong document ingestion and parsing tool suite using Docling.",
    no_args_is_help=True,
)


def parse_document(file_path: Path | str) -> Dict[str, Any]:
    """Parse a document (PDF or Markdown) and return structured text and metadata."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    # If Docling is available, use DocumentConverter
    try:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        conv_result = converter.convert(str(path))
        doc = conv_result.document
        markdown_text = doc.export_to_markdown()
        return {
            "title": path.stem,
            "format": "docling_markdown",
            "text": markdown_text,
            "num_pages": len(getattr(doc, "pages", [])) or 1,
            "metadata": {"source": str(path)},
        }
    except ImportError:
        pass

    # Fallback PDF text extraction using basic parser
    content_bytes = path.read_bytes()
    text_parts: list[str] = []
    # Extract string literals from PDF stream
    import re
    strings = re.findall(rb"\((.*?)\)\s*Tj", content_bytes)
    for s in strings:
        try:
            text_parts.append(s.decode("latin1"))
        except Exception:
            continue

    raw_text = "\n".join(text_parts) if text_parts else path.read_text(encoding="utf-8", errors="ignore")
    return {
        "title": path.stem,
        "format": "text_extracted",
        "text": raw_text,
        "num_pages": 1,
        "metadata": {"source": str(path)},
    }


@app.command("parse")
def parse_cmd(
    path: Path = typer.Argument(..., help="Path to document to parse"),
    output: Path = typer.Option(None, "--output", "-o", help="Path to write JSON output"),
) -> None:
    """Parse a document with Docling and output structured content."""
    res = parse_document(path)
    rendered = json.dumps(res, indent=2)
    if output:
        output.write_text(rendered, encoding="utf-8")
        typer.echo(f"Output saved to {output}")
    else:
        typer.echo(rendered)


if __name__ == "__main__":
    app()
