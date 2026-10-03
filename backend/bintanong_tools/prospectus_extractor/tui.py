"""Interactive terminal UI."""

from __future__ import annotations

from pathlib import Path
import json
import re

from .common import RICH_AVAILABLE, SCHEMA_VERSION, console

if RICH_AVAILABLE:
    from .common import Confirm, Panel, Prompt, Table
from .loader import dump_grid, load_document
from .pipeline import process_prospectus
from .batch import BatchConfig, build_batch_items, run_batch, scan_inputs
from .selftest import run_self_tests


def print_line(message: str = "") -> None:
    if RICH_AVAILABLE and console:
        console.print(message)
    else:
        print(
            re.sub(
                r"\[/?(?:bold|italic|dim|underline|red|green|blue|cyan|magenta|yellow|white|black)"
                r"[^\]]*\]",
                "",
                message,
            )
        )


def ask_text(prompt: str, default: str = "") -> str:
    try:
        if RICH_AVAILABLE:
            return Prompt.ask(prompt, default=default)
        suffix = f" [{default}]" if default else ""
        return input(f"{prompt}{suffix}: ").strip() or default
    except (EOFError, KeyboardInterrupt):
        return default


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    try:
        if RICH_AVAILABLE:
            return Confirm.ask(prompt, default=default)
        answer = input(f"{prompt} ({'Y/n' if default else 'y/N'}): ").strip().lower()
        return default if not answer else answer in {"y", "yes", "1", "true"}
    except (EOFError, KeyboardInterrupt):
        return default


class ProspectusTUI:
    """Menu-driven front end for batch and single-file extraction."""

    def __init__(self) -> None:
        self.config = BatchConfig()
        self.last_scan: list[Path] = []

    # -- helpers ----------------------------------------------------------
    def pause(self, message: str = "") -> None:
        if message:
            print_line(f"\n{message}")
        try:
            input("\nPress Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            pass

    def header(self) -> None:
        print("\n")
        title = f"PalSU Prospectus Extractor ({SCHEMA_VERSION})"
        subtitle = "Docling -> audited JSON, Prolog knowledge base and RAG corpus"
        if RICH_AVAILABLE and console:
            console.print(Panel.fit(f"[bold]{title}[/bold]\n{subtitle}", border_style="cyan"))
        else:
            print(title)
            print(subtitle)
            print("=" * len(title))

    def show_config(self) -> None:
        cfg = self.config
        rows = [
            ("Input root", str(cfg.input_root)),
            ("Output root", str(cfg.output_root)),
            ("Device", cfg.device.upper()),
            ("Recursive", str(cfg.recursive)),
            ("Preserve structure", str(cfg.preserve_structure)),
            ("Export mode", cfg.export_mode),
            ("Write CSV / PL / JSONL / MD", f"{cfg.write_csv} / {cfg.write_pl} / {cfg.write_jsonl} / {cfg.write_md}"),
            ("Skip existing", str(cfg.skip_existing)),
            ("Semantic map", str(cfg.semantic_doc) if cfg.semantic_doc else "(none)"),
            ("Files in last scan", str(len(self.last_scan))),
        ]
        if RICH_AVAILABLE and console:
            table = Table(title="Current settings")
            table.add_column("Setting", style="bold")
            table.add_column("Value")
            for key, value in rows:
                table.add_row(key, value)
            console.print(table)
        else:
            print("\nCurrent settings:")
            for key, value in rows:
                print(f"  {key}: {value}")

    # -- menu -------------------------------------------------------------
    def main_menu(self) -> None:
        while True:
            self.header()
            self.show_config()
            print_line("\n[1] Set input folder")
            print_line("[2] Set output folder")
            print_line("[3] Scan for prospectuses")
            print_line("[4] Configure device and exports")
            print_line("[5] Preview batch plan")
            print_line("[6] Run batch extraction")
            print_line("[7] Single file extraction")
            print_line("[8] Inspect an extracted prospectus JSON")
            print_line("[9] Dump table grid (layout debugging)")
            print_line("[t] Run self-test suite")
            print_line("[0] Exit")

            choice = ask_text("Choose", "0").strip().lower()
            try:
                if choice == "1":
                    self.set_folder("input")
                elif choice == "2":
                    self.set_folder("output")
                elif choice == "3":
                    self.scan()
                elif choice == "4":
                    self.configure()
                elif choice == "5":
                    self.preview()
                elif choice == "6":
                    self.run_batch_interactive()
                elif choice == "7":
                    self.single_file()
                elif choice == "8":
                    self.inspect()
                elif choice == "9":
                    self.dump_grid_interactive()
                elif choice == "t":
                    failures = run_self_tests()
                    self.pause("Self-test passed." if not failures else f"{failures} self-test failure(s).")
                elif choice == "0":
                    print_line("Exiting. Review the *_review.csv before loading into Prolog or a vector store.")
                    return
                else:
                    self.pause("Invalid choice.")
            except Exception as exc:
                self.pause(f"Error: {type(exc).__name__}: {exc}")

    def set_folder(self, which: str) -> None:
        current = self.config.input_root if which == "input" else self.config.output_root
        value = ask_text(f"{which.title()} folder path", str(current)).strip().strip('"')
        path = Path(value).expanduser()
        if which == "input":
            if not path.is_dir():
                self.pause(f"Folder not found: {path}")
                return
            self.config.input_root = path.resolve()
            self.last_scan = []
        else:
            self.config.output_root = path.resolve()
        self.pause(f"{which.title()} folder updated.")

    def scan(self) -> None:
        self.last_scan = scan_inputs(
            self.config.input_root, self.config.recursive, self.config.include_patterns
        )
        print_line(f"\nFound {len(self.last_scan)} file(s):")
        for index, path in enumerate(self.last_scan[:15], start=1):
            try:
                shown = path.relative_to(self.config.input_root)
            except ValueError:
                shown = Path(path.name)
            print_line(f"  [{index:2d}] {shown}")
        if len(self.last_scan) > 15:
            print_line(f"  ...and {len(self.last_scan) - 15} more.")
        self.pause()

    def configure(self) -> None:
        cfg = self.config
        device = ask_text("Device [auto / cuda / cpu]", cfg.device).strip().lower()
        if device in {"auto", "cuda", "cpu"}:
            cfg.device = device
        patterns = ask_text("File patterns (comma separated)", ", ".join(cfg.include_patterns))
        cfg.include_patterns = [p.strip() for p in patterns.split(",") if p.strip()] or ["*.pdf"]
        cfg.recursive = ask_yes_no("Scan subfolders recursively?", cfg.recursive)
        cfg.preserve_structure = ask_yes_no("Mirror the input folder structure?", cfg.preserve_structure)
        print_line("\n[1] side_by_side  output/<rel>/<stem>_prospectus.json")
        print_line("[2] per_pdf_folder output/<rel>/<stem>/prospectus.json")
        mode = ask_text("Export mode", "1" if cfg.export_mode == "side_by_side" else "2").strip()
        cfg.export_mode = "side_by_side" if mode == "1" else "per_pdf_folder"
        cfg.write_csv = ask_yes_no("Write review CSV?", cfg.write_csv)
        cfg.write_pl = ask_yes_no("Write Prolog knowledge base?", cfg.write_pl)
        cfg.write_jsonl = ask_yes_no("Write RAG JSONL?", cfg.write_jsonl)
        cfg.write_md = ask_yes_no("Write prospectus-style Markdown?", cfg.write_md)
        cfg.write_manifest = ask_yes_no("Write batch manifest?", cfg.write_manifest)
        cfg.skip_existing = ask_yes_no("Skip files whose output already exists?", cfg.skip_existing)
        self.pause("Settings updated.")

    def preview(self) -> None:
        if not self.last_scan:
            self.last_scan = scan_inputs(
                self.config.input_root, self.config.recursive, self.config.include_patterns
            )
        items = build_batch_items(self.last_scan, self.config)
        print_line(f"\nBatch plan ({len(items)} file(s)):")
        for item in items[:10]:
            print_line(f"  IN : {item.source_pdf.name}")
            print_line(f"  OUT: {item.json_path}")
        if len(items) > 10:
            print_line(f"  ...and {len(items) - 10} more.")
        self.pause()

    def run_batch_interactive(self) -> None:
        if not self.last_scan:
            self.last_scan = scan_inputs(
                self.config.input_root, self.config.recursive, self.config.include_patterns
            )
        if not self.last_scan:
            self.pause("Nothing to process. Check the input folder and patterns.")
            return
        if not ask_yes_no(f"Process {len(self.last_scan)} file(s)?", default=False):
            self.pause("Cancelled.")
            return
        summary = run_batch(self.config)
        print_line(
            f"\nDone: {summary['succeeded']} extracted, {summary['audit_failed']} failed audit, "
            f"{summary['skipped']} skipped, {summary['failed']} errored."
        )
        if summary.get("manifest_path"):
            print_line(f"Manifest: {summary['manifest_path']}")
        self.pause()

    def _pick_file(self) -> Path | None:
        if not self.last_scan:
            try:
                self.last_scan = scan_inputs(
                    self.config.input_root, self.config.recursive, self.config.include_patterns
                )
            except Exception:
                self.last_scan = []
        if self.last_scan:
            print_line(f"\nAvailable files ({len(self.last_scan)}):")
            for index, path in enumerate(self.last_scan[:12], start=1):
                print_line(f"  [{index:2d}] {path.name}")
            if len(self.last_scan) > 12:
                print_line(f"  ...and {len(self.last_scan) - 12} more.")
        value = ask_text("Select # or enter a full path").strip().strip('"')
        if not value:
            return None
        if value.isdigit() and self.last_scan:
            index = int(value)
            if 1 <= index <= len(self.last_scan):
                return self.last_scan[index - 1]
            return None
        candidate = Path(value).expanduser()
        if candidate.exists():
            return candidate.resolve()
        matches = [p for p in self.last_scan if value.lower() in p.name.lower()]
        return matches[0] if matches else None

    def single_file(self) -> None:
        path = self._pick_file()
        if not path:
            self.pause("File not found.")
            return
        try:
            payload = process_prospectus(
                path,
                export_pl=self.config.write_pl,
                export_jsonl=self.config.write_jsonl,
                export_csv=self.config.write_csv,
                export_md=self.config.write_md,
                device=self.config.device,
                semantic_doc_path=self.config.semantic_doc,
            )
            self.pause(
                f"Extracted {payload['audit']['total_courses']} courses "
                f"({payload['audit']['status'].upper()})."
            )
        except Exception as exc:
            self.pause(f"Extraction failed: {type(exc).__name__}: {exc}")

    def dump_grid_interactive(self) -> None:
        path = self._pick_file()
        if not path:
            self.pause("File not found.")
            return
        document, _ = load_document(path, device=self.config.device)
        text = dump_grid(document)
        out_path = path.with_name(f"{path.stem}_grid_dump.txt")
        out_path.write_text(text, encoding="utf-8")
        print_line(text[:4000])
        self.pause(f"Full dump written to {out_path}")

    def inspect(self) -> None:
        value = ask_text("Path to *_prospectus.json").strip().strip('"')
        path = Path(value).expanduser()
        if not path.exists():
            self.pause(f"File not found: {path}")
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.pause(f"Could not read JSON: {exc}")
            return
        audit = data.get("audit", {})
        print_line(f"\nProgram: {data.get('program')}  ({data.get('degree')})")
        print_line(f"College: {data.get('college')} - {data.get('college_name')}")
        print_line(f"SY:      {data.get('metadata', {}).get('effective_school_year')}")
        print_line(f"Status:  {audit.get('status', 'unknown').upper()}")
        print_line(f"Courses: {audit.get('total_courses')}  Units: {audit.get('computed_total_units')}")
        print_line(f"Years:   {audit.get('years_detected')}")
        for term in audit.get("term_unit_audit", []):
            flag = "ok " if term["matches"] else "BAD"
            print_line(
                f"  [{flag}] {term['year_level']} {term['semester']}: "
                f"{term['computed_units']} units / declared {term['declared_units']}"
            )
        for message in audit.get("errors", []):
            print_line(f"  ERROR: {message}")
        for message in audit.get("warnings", [])[:10]:
            print_line(f"  warn:  {message}")
        self.pause()
