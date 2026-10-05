"""Run each original prospectus PDF in its own Docling process."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from . import prospectus_extractor as extractor
from .prospectus_extractor.identity import PACKAGE_DIR, file_sha256, package_sha256


def run_isolated(
    input_root: Path, output_root: Path, semantic_doc: Path | None, device: str = "cpu"
) -> dict:
    input_root = input_root.resolve()
    output_root = output_root.resolve()
    if semantic_doc is not None and not semantic_doc.is_file():
        raise FileNotFoundError(f"Semantic map does not exist: {semantic_doc}")
    config = extractor.BatchConfig(input_root=input_root, output_root=output_root)
    items = extractor.build_batch_items(extractor.scan_inputs(input_root, patterns=["*.pdf"]), config)
    if not items:
        raise ValueError(f"No original PDFs found under {input_root}")
    if (output_root / "isolated_manifest.json").exists() or any(item.json_path.exists() for item in items):
        raise FileExistsError("Output already has a run; choose a new run directory")
    output_root.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    manifest_path = output_root / "isolated_manifest.json"
    for number, item in enumerate(items, 1):
        item.json_path.parent.mkdir(parents=True, exist_ok=True)
        log_path = output_root / f"run-{number:02d}.log"
        command = [sys.executable, str(PACKAGE_DIR), "-i", str(item.source_pdf),
                   "-o", str(item.json_path), "--force", "--device", device, "--strict"]
        if semantic_doc is not None:
            command.extend(["--semantic-doc", str(semantic_doc.resolve())])
        launch_error = None
        with log_path.open("w", encoding="utf-8") as log:
            try:
                exit_code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
            except OSError as exc:
                exit_code = None
                launch_error = f"{type(exc).__name__}: {exc}"
        record = {
            "source": str(item.source_pdf),
            "pdf_sha256": file_sha256(item.source_pdf),
            "json_path": str(item.json_path),
            "log": str(log_path),
            "strict_exit_code": exit_code,
            "status": "processing_error",
            "error": launch_error,
        }
        if launch_error is None:
            try:
                payload = json.loads(item.json_path.read_text(encoding="utf-8"))
                if Path(payload["source_path"]).resolve() != item.source_pdf.resolve():
                    raise ValueError("candidate source path differs from input PDF")
                status = payload["audit"]["status"]
                if status not in ("ok", "warn", "error") or exit_code != (1 if status == "error" else 0):
                    raise ValueError(f"child exit {exit_code} disagrees with audit {status}")
                record.update(status=status, course_count=len(payload["courses"]),
                              total_units=payload["audit"]["computed_total_units"])
            except (OSError, ValueError, KeyError, TypeError) as exc:
                record["error"] = f"{type(exc).__name__}: {exc}"
        records.append(record)
        summary = {
            "total_expected": len(items), "completed": len(records),
            "ok": sum(r["status"] == "ok" for r in records),
            "warn": sum(r["status"] == "warn" for r in records),
            "audit_error": sum(r["status"] == "error" for r in records),
            "processing_error": sum(r["status"] == "processing_error" for r in records),
        }
        manifest = {"schema_version": "isolated-original-pdf-run-v1",
                    "parser_sha256": package_sha256(),
                    "semantic_doc": str(semantic_doc.resolve()) if semantic_doc else None,
                    "summary": summary, "records": records}
        checkpoint = manifest_path.with_suffix(".tmp")
        checkpoint.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        checkpoint.replace(manifest_path)
        print(f"{number}/{len(items)} exit={exit_code} status={record['status']} "
              f"{item.source_pdf.name}", flush=True)
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("-i", "--input", required=True, type=Path, help="Original PDF folder")
    cli.add_argument("-o", "--output", required=True, type=Path, help="New output folder")
    cli.add_argument("--semantic-doc", type=Path, help="Original source metadata map")
    cli.add_argument("--device", choices=("cpu", "auto", "cuda"), default="cpu")
    args = cli.parse_args(argv)
    try:
        manifest = run_isolated(args.input, args.output, args.semantic_doc, args.device)
    except (OSError, ValueError) as exc:
        cli.error(str(exc))
    summary = manifest["summary"]
    print(f"Batch: {summary['completed']}/{summary['total_expected']} PDFs, "
          f"{summary['processing_error']} processing errors, "
          f"{summary['audit_error']} audit errors.")
    return 2 if summary["processing_error"] else (1 if summary["audit_error"] else 0)


if __name__ == "__main__":
    raise SystemExit(main())
