# Exact task brief from plans\2026-10-03-prospectus-phase-f-tools-cli.md

Read approved_execution.md and preflight-ledger.md first. They supersede obsolete base/merge/dev/version/path snippets in this preserved historical plan. Do not edit the original plan. Preserve original task requirements below unless an approved ruling supersedes them.

### Task 1: Start check, branch, baseline

**Files:** read only, plus the progress file.

- [ ] **Step 1: Branch and baseline**

```
git switch dev
git status --short
git switch -c feature/prospectus-tools-boundary
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test
```

Expected: the status shows only `.gitignore` and the CODEX handoff file (leave both alone). Record the observed pass count and `80/80`. If anything fails, stop and report.

- [ ] **Step 2: Conditional deletion of the Phase A gate**

If `tests/test_prospectus_split_equivalence.py` still exists, Phase B was skipped or not merged: stop and report instead of continuing. (This phase runs after B-E; the file should already be gone.)

- [ ] **Step 3: Re-read and pin names.** Open each file and write the observed facts into the progress file; edit later snippets in this plan if they differ.

  1. `backend/bintanong_tools/ingest.py`: `parse_cmd` was lines 61-73; `app` lines 8-12. Confirm there is still exactly one `@app.command`.
  2. `backend/bintanong_tools/prospectus_extractor/pipeline.py`: `build_essentials` (was 129) and `process_prospectus` (was 174-186). Confirm: the keyword list of `process_prospectus` (this plan appends `source_root` after `quiet`); that it still accepts `output_path`, `export_csv`, `device`, `semantic_doc_path`, `force_reconvert`, `quiet`; that it calls `load_document(input_path, device=..., force_reconvert=..., converter=..., raw_json_path=...)` by keyword (the `fake_conversion` fixture mirrors that signature).
  3. The payload status keys after Phase C. Run: `uv run --project backend --extra tools --extra dev python -c "from backend.bintanong_tools.prospectus_extractor import pipeline as p; from backend.bintanong_tools.prospectus_extractor.selftest import *; d=p.build_payload(fixture_document(cs_fixture_grid(), CS_TEXT_ITEMS), __import__('pathlib').Path('x.pdf'), None); print({k: (type(d[k]).__name__, d[k] if isinstance(d[k], str) else list(d[k])[:4]) for k in ('audit','extraction_audit','content_review','source_verification') if k in d})"`. Note whether `extraction_audit` is a string or a dict, and the exact key holding its status. `_status_fields` in Task 4 handles `str` and `{"status": ...}`; if the key is different, change that one helper and its test.
  4. The essentials keys (`build_essentials` return). Task 4's `candidate_facts` drops only `source_pdf`; if Phase C renamed `extraction_status`, nothing else changes.
  5. Output file names written by `process_prospectus` for a PDF (`<stem>_docling.json`, `<stem>_docling.meta.json`, `<stem>_prospectus.json`, `<stem>_essentials.json`, `<stem>_review.csv`, Phase B `<stem>_prospectus.md`). Task 4's `_ARTIFACT_ROLES` lists the suffixes; add any new one.
  6. `docker/ingest.Dockerfile:6-8` and `compose.yaml` `ingest` service (was lines 92-104) unchanged. `.dockerignore` content unchanged.

- [ ] **Step 4: Commit the progress note only**

```
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: record Phase F start check" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---



### Task 2: Provisional source records (D1)

**Files:**
- Modify: `backend/bintanong_tools/prospectus.py`
- Modify: `tests/test_prospectus_sources.py` (append; keep the existing class untouched)

- [ ] **Step 1: Write the failing tests** (append to `tests/test_prospectus_sources.py`; add `import json`, `import pytest` and the extra names to the import block at the top)

Change the import line to:

```python
from backend.bintanong_tools.prospectus import (
    ProvisionalSource,
    SourceRecordError,
    load_provisional_sources,
    locator_for,
    source_for_pdf,
)
```

Add `import json` and `import pytest` beside the existing imports, then append:

```python
HASH = "a" * 64


def test_provisional_source_id_is_keyed_by_the_pdf_hash():
    source = ProvisionalSource(HASH, "Tiniguiban - Main/CS/a.pdf")
    assert source.provisional_source_id == f"provisional:sha256:{HASH}"


def test_loads_inventory_csv_with_windows_locators(tmp_path):
    inventory = tmp_path / "inventory.csv"
    inventory.write_text(
        '"pdf_sha256","source_locator","source_verification"\n'
        f'"{HASH}","Tiniguiban - Main\\CS\\a.pdf","pending"\n',
        encoding="utf-8",
    )
    records = load_provisional_sources(inventory)
    assert list(records) == ["Tiniguiban - Main/CS/a.pdf"]
    assert records["Tiniguiban - Main/CS/a.pdf"].pdf_sha256 == HASH


def test_loads_json_object_and_list(tmp_path):
    one = tmp_path / "one.json"
    one.write_text(json.dumps({"pdf_sha256": HASH.upper(), "source_locator": "x/a.pdf"}), encoding="utf-8")
    assert load_provisional_sources(one)["x/a.pdf"].pdf_sha256 == HASH
    many = tmp_path / "many.json"
    many.write_text(
        json.dumps([{"pdf_sha256": HASH, "source_locator": "x/a.pdf"},
                    {"pdf_sha256": "b" * 64, "source_locator": "x/b.pdf"}]),
        encoding="utf-8",
    )
    assert sorted(load_provisional_sources(many)) == ["x/a.pdf", "x/b.pdf"]


@pytest.mark.parametrize(
    "row, message",
    [
        ({"pdf_sha256": HASH, "source_locator": "x/a.pdf", "source_verification": "approved"}, "pending"),
        ({"pdf_sha256": "xyz", "source_locator": "x/a.pdf"}, "64"),
        ({"pdf_sha256": HASH, "source_locator": "/etc/a.pdf"}, "relative"),
        ({"pdf_sha256": HASH, "source_locator": "x/../a.pdf"}, "relative"),
        ({"pdf_sha256": HASH, "source_locator": "C:\\a.pdf"}, "relative"),
    ],
)
def test_refuses_records_that_claim_more_than_pending_or_are_malformed(tmp_path, row, message):
    record = tmp_path / "record.json"
    record.write_text(json.dumps(row), encoding="utf-8")
    with pytest.raises(SourceRecordError, match=message):
        load_provisional_sources(record)


def test_refuses_conflicting_hashes_for_one_locator(tmp_path):
    record = tmp_path / "record.json"
    record.write_text(
        json.dumps([{"pdf_sha256": HASH, "source_locator": "x/a.pdf"},
                    {"pdf_sha256": "b" * 64, "source_locator": "x\\a.pdf"}]),
        encoding="utf-8",
    )
    with pytest.raises(SourceRecordError, match="conflicting"):
        load_provisional_sources(record)


def test_refuses_missing_and_unknown_record_files(tmp_path):
    with pytest.raises(SourceRecordError, match="not found"):
        load_provisional_sources(tmp_path / "absent.csv")
    other = tmp_path / "record.txt"
    other.write_text("x", encoding="utf-8")
    with pytest.raises(SourceRecordError, match=r"\.csv or \.json"):
        load_provisional_sources(other)


def test_source_for_pdf_needs_a_record_inside_the_source_root(tmp_path):
    root = tmp_path / "root"
    pdf = root / "Tiniguiban - Main" / "a.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-1.4")
    assert locator_for(pdf, root) == "Tiniguiban - Main/a.pdf"
    records = {"Tiniguiban - Main/a.pdf": ProvisionalSource(HASH, "Tiniguiban - Main/a.pdf")}
    assert source_for_pdf(records, pdf, root) is records["Tiniguiban - Main/a.pdf"]
    with pytest.raises(SourceRecordError, match="No provisional source record"):
        source_for_pdf({}, pdf, root)
    outside = tmp_path / "elsewhere.pdf"
    outside.write_bytes(b"%PDF-1.4")
    with pytest.raises(SourceRecordError, match="not under"):
        locator_for(outside, root)
```

- [ ] **Step 2: Run and confirm they fail**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_sources.py`
Expected: collection error `ImportError: cannot import name 'SourceRecordError'`.

- [ ] **Step 3: Implement.** Replace the whole content of `backend/bintanong_tools/prospectus.py` with the following (the original `ProvisionalSource` and `verify_pdf` are kept verbatim; the adapter is added in Task 4):

```python
"""Hash-bound source identity for review-only prospectus work."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

_SHA256 = re.compile(r"[0-9a-f]{64}")
_DRIVE_LETTER = re.compile(r"^[A-Za-z]:")


class SourceRecordError(ValueError):
    """A provisional source record is missing, malformed, or claims more than pending."""


@dataclass(frozen=True)
class ProvisionalSource:
    pdf_sha256: str
    source_locator: str
    source_verification: Literal["pending"] = field(default="pending", init=False)

    @property
    def provisional_source_id(self) -> str:
        return f"provisional:sha256:{self.pdf_sha256}"

    def verify_pdf(self, pdf_path: Path) -> None:
        with pdf_path.open("rb") as pdf:
            actual_hash = hashlib.file_digest(pdf, "sha256").hexdigest()
        if actual_hash != self.pdf_sha256:
            raise ValueError(f"PDF hash mismatch for {pdf_path}")


def normalize_locator(locator: str) -> str:
    """Posix-style relative locator; inventories written on Windows use backslashes."""
    text = str(locator).strip()
    parts = text.replace("\\", "/").split("/")
    if (
        not text
        or text[0] in "/\\"
        or _DRIVE_LETTER.match(text)
        or ".." in parts
        or not any(part not in ("", ".") for part in parts)
    ):
        raise SourceRecordError(f"Source locator must be a relative path inside the source root: {locator!r}")
    return "/".join(part for part in parts if part not in ("", "."))


def _source_from_row(row: object) -> ProvisionalSource:
    if not isinstance(row, dict):
        raise SourceRecordError(f"Source record rows must be objects, got {type(row).__name__}")
    digest = str(row.get("pdf_sha256") or "").strip().lower()
    if not _SHA256.fullmatch(digest):
        raise SourceRecordError("pdf_sha256 must be 64 hexadecimal characters")
    state = str(row.get("source_verification") or "pending").strip().lower()
    if state != "pending":
        raise SourceRecordError(
            f"Source record claims source_verification={state!r}; only 'pending' is accepted. "
            "Approval comes from a later, separate source-approval step, never from this file."
        )
    return ProvisionalSource(digest, normalize_locator(row.get("source_locator") or ""))


def load_provisional_sources(record_path: Path) -> dict[str, ProvisionalSource]:
    """Read an inventory CSV or JSON record file into {normalized locator: source}."""
    path = Path(record_path)
    if not path.is_file():
        raise SourceRecordError(f"Source record not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows: list[object] = list(csv.DictReader(handle))
    elif suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SourceRecordError(f"Source record is not valid JSON: {path}: {exc}") from exc
        rows = data if isinstance(data, list) else [data]
    else:
        raise SourceRecordError(f"Source record must be a .csv or .json file: {path}")
    if not rows:
        raise SourceRecordError(f"Source record has no rows: {path}")
    records: dict[str, ProvisionalSource] = {}
    for row in rows:
        source = _source_from_row(row)
        known = records.get(source.source_locator)
        if known is not None and known.pdf_sha256 != source.pdf_sha256:
            raise SourceRecordError(f"Source record has conflicting hashes for {source.source_locator!r}")
        records[source.source_locator] = source
    return records


def locator_for(pdf_path: Path, source_root: Path) -> str:
    try:
        relative = Path(pdf_path).resolve().relative_to(Path(source_root).resolve())
    except ValueError:
        raise SourceRecordError(f"{pdf_path} is not under source root {source_root}") from None
    return relative.as_posix()


def source_for_pdf(
    records: dict[str, ProvisionalSource], pdf_path: Path, source_root: Path
) -> ProvisionalSource:
    locator = locator_for(pdf_path, source_root)
    try:
        return records[locator]
    except KeyError:
        raise SourceRecordError(
            f"No provisional source record for {locator!r}; add it to the source record before extraction"
        ) from None
```

- [ ] **Step 4: Run and confirm they pass**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_sources.py`
Expected: all pass (the original test plus 16 parametrized and new cases).

- [ ] **Step 5: Progress note and commit**

```
git add backend/bintanong_tools/prospectus.py tests/test_prospectus_sources.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: load provisional source records for the tools boundary" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---



### Task 3: Explicit `source_root` in essentials (replaces the in-repo default on the tools path)

**Files:**
- Modify: `backend/bintanong_tools/prospectus_extractor/pipeline.py` (`build_essentials`, `process_prospectus`)
- Create: `tests/conftest.py`
- Create: `tests/test_prospectus_source_root.py`

`build_essentials` computes `source_pdf` relative to `SOURCE_PDF_ROOT` (a dataset path that does not exist in the repo) and falls back to the bare file name. With an explicit root, host and container give the same `source_pdf` (`Tiniguiban - Main/CS/x.pdf`). Default behavior stays for the legacy CLI.

- [ ] **Step 1: Write the shared fixture** `tests/conftest.py`

```python
"""Shared fixtures for prospectus tests. No institution PDF is ever read."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.bintanong_tools.prospectus_extractor import pipeline
from backend.bintanong_tools.prospectus_extractor.selftest import (
    CS_TEXT_ITEMS,
    cs_fixture_grid,
    fixture_document,
)


@pytest.fixture
def fake_conversion(monkeypatch):
    """Replace Docling with the in-memory BSCS fixture; returns the list of PDFs 'converted'."""
    converted: list[Path] = []

    def fake_load_document(input_path, device="auto", force_reconvert=True, converter=None, raw_json_path=None):
        converted.append(Path(input_path))
        raw = Path(raw_json_path)
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_text('{"fixture": true}', encoding="utf-8")
        return fixture_document(cs_fixture_grid(), CS_TEXT_ITEMS), raw

    monkeypatch.setattr(pipeline, "load_document", fake_load_document)
    return converted
```

- [ ] **Step 2: Write the failing test** `tests/test_prospectus_source_root.py`

```python
from __future__ import annotations

import json

from backend.bintanong_tools.prospectus_extractor import pipeline
from backend.bintanong_tools.prospectus_extractor.selftest import (
    CS_TEXT_ITEMS,
    cs_fixture_grid,
    fixture_document,
)


def _payload(pdf):
    return pipeline.build_payload(fixture_document(cs_fixture_grid(), CS_TEXT_ITEMS), pdf, None)


def test_essentials_source_pdf_is_relative_to_an_explicit_root(tmp_path):
    root = tmp_path / "root"
    pdf = root / "Tiniguiban - Main" / "CS" / "p.pdf"
    payload = _payload(pdf)
    assert pipeline.build_essentials(payload, source_root=root)["source_pdf"] == "Tiniguiban - Main/CS/p.pdf"
    # Legacy behavior is unchanged: outside the in-repo default root, only the name remains.
    assert pipeline.build_essentials(payload)["source_pdf"] == "p.pdf"


def test_process_prospectus_passes_the_root_through(tmp_path, fake_conversion):
    root = tmp_path / "root"
    pdf = root / "Tiniguiban - Main" / "CS" / "p.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-1.4")
    out = tmp_path / "out" / "p_prospectus.json"
    pipeline.process_prospectus(
        pdf, output_path=out, semantic_doc_path=None, quiet=True, source_root=root
    )
    essentials = json.loads((tmp_path / "out" / "p_essentials.json").read_text(encoding="utf-8"))
    assert essentials["source_pdf"] == "Tiniguiban - Main/CS/p.pdf"
```

- [ ] **Step 3: Run and confirm failure**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_source_root.py`
Expected: 2 failed with `TypeError: ... got an unexpected keyword argument 'source_root'`.

- [ ] **Step 4: Implement.** In `pipeline.py`:

Change the `build_essentials` signature and the relative-path lines (was 129-137):

```python
def build_essentials(payload: Mapping[str, Any], source_root: Path | None = None) -> dict[str, Any]:
    """Project an audited extraction into portable curriculum facts."""
    source_path = Path(payload["source_path"]).resolve()
    if source_path.suffix.lower() != ".pdf":
        raise ValueError("Essentials require a source PDF")
    root = SOURCE_PDF_ROOT if source_root is None else Path(source_root)
    try:
        source_pdf = source_path.relative_to(root.resolve()).as_posix()
    except ValueError:
        source_pdf = source_path.name
```

Add a last parameter to `process_prospectus` (after `quiet: bool = False,`):

```python
    source_root: Path | None = None,
```

and change its call `build_essentials(payload)` to `build_essentials(payload, source_root=source_root)`.

- [ ] **Step 5: Run the new tests and the whole suite**

Run: `uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests`
Expected: all pass (baseline count plus the new tests); self-test still `80/80`.

- [ ] **Step 6: Commit**

```
git add backend/bintanong_tools/prospectus_extractor/pipeline.py tests/conftest.py tests/test_prospectus_source_root.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: let essentials locate the PDF under an explicit source root" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---



### Task 4: The adapter, `run_candidate()`

**Files:**
- Modify: `backend/bintanong_tools/prospectus.py`
- Create: `tests/test_prospectus_cli.py` (adapter section first; later tasks append)

- [ ] **Step 1: Write the failing tests** `tests/test_prospectus_cli.py`

```python
"""Tools boundary for prospectus candidates: adapter, command, folder mode, equivalence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from backend.bintanong_tools import prospectus as adapter
from backend.bintanong_tools.prospectus import ExtractionSettings, ProvisionalSource, run_candidate
from backend.bintanong_tools.prospectus_batch import package_sha256

REL = "Tiniguiban - Main/CS/prog.pdf"


def make_pdf(root: Path, rel: str = REL, content: bytes = b"%PDF-1.4\nfixture one") -> tuple[Path, str]:
    pdf = root.joinpath(*rel.split("/"))
    pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf.write_bytes(content)
    return pdf, hashlib.sha256(content).hexdigest()


def test_hash_mismatch_refuses_before_any_conversion_or_output(tmp_path, fake_conversion):
    pdf, _ = make_pdf(tmp_path / "src")
    wrong = ProvisionalSource("0" * 64, REL)
    run_dir = tmp_path / "out" / "run"
    with pytest.raises(ValueError, match="hash mismatch"):
        run_candidate(pdf, run_dir, wrong)
    assert fake_conversion == []
    assert not run_dir.exists()


def test_manifest_records_identity_versions_statuses_and_artifact_hashes(tmp_path, fake_conversion):
    pdf, digest = make_pdf(tmp_path / "src")
    run_dir = tmp_path / "out" / "run"
    manifest = run_candidate(pdf, run_dir, ProvisionalSource(digest, REL), source_root=tmp_path / "src")

    assert json.loads((run_dir / "candidate_run.json").read_text(encoding="utf-8")) == manifest
    assert manifest["schema_version"] == "palsu-prospectus-candidate-run-v1"
    assert manifest["provisional_source_id"] == f"provisional:sha256:{digest}"
    assert manifest["approved_source_version_id"] is None
    assert manifest["pdf_sha256"] == digest
    assert manifest["source_locator"] == REL
    assert manifest["content_review"] == "pending"
    assert manifest["source_verification"] == "pending"
    assert manifest["extraction_audit"] in {"ok", "warn", "error"}
    assert manifest["versions"]["extractor_package_sha256"] == package_sha256()
    assert manifest["versions"]["payload_schema_version"].startswith("palsu-prospectus-")
    assert len(manifest["candidate_facts_sha256"]) == 64
    roles = {artifact["role"] for artifact in manifest["artifacts"]}
    assert {"raw_docling", "candidate_payload", "essentials", "review_csv"} <= roles
    for artifact in manifest["artifacts"]:
        actual = hashlib.sha256((run_dir / artifact["path"]).read_bytes()).hexdigest()
        assert artifact["sha256"] == actual
        assert "\\" not in artifact["path"]
    assert "candidate_run.json" not in {artifact["path"] for artifact in manifest["artifacts"]}


def test_a_pdf_changed_during_conversion_is_refused(tmp_path, monkeypatch, fake_conversion):
    from backend.bintanong_tools.prospectus_extractor import pipeline

    pdf, digest = make_pdf(tmp_path / "src")
    original = pipeline.load_document

    def mutate_then_load(*args, **kwargs):
        pdf.write_bytes(b"%PDF-1.4\nchanged underneath")
        return original(*args, **kwargs)

    monkeypatch.setattr(pipeline, "load_document", mutate_then_load)
    with pytest.raises(ValueError, match="hash mismatch"):
        run_candidate(pdf, tmp_path / "out" / "run", ProvisionalSource(digest, REL))
    assert not (tmp_path / "out" / "run" / "candidate_run.json").exists()


def test_an_extractor_claiming_content_review_is_refused(tmp_path, monkeypatch, fake_conversion):
    pdf, digest = make_pdf(tmp_path / "src")
    real = adapter.extractor.process_prospectus

    def claims_reviewed(*args, **kwargs):
        payload = real(*args, **kwargs)
        payload["content_review"] = "approved"
        return payload

    monkeypatch.setattr(adapter.extractor, "process_prospectus", claims_reviewed)
    with pytest.raises(ValueError, match="content_review"):
        run_candidate(pdf, tmp_path / "out" / "run", ProvisionalSource(digest, REL))


def test_an_existing_run_is_never_overwritten(tmp_path, fake_conversion):
    pdf, digest = make_pdf(tmp_path / "src")
    run_dir = tmp_path / "out" / "run"
    source = ProvisionalSource(digest, REL)
    run_candidate(pdf, run_dir, source)
    with pytest.raises(FileExistsError):
        run_candidate(pdf, run_dir, source)


def test_a_missing_semantic_map_is_refused_before_conversion(tmp_path, fake_conversion):
    pdf, digest = make_pdf(tmp_path / "src")
    settings = ExtractionSettings(semantic_doc=tmp_path / "absent.md")
    with pytest.raises(FileNotFoundError, match="Semantic map"):
        run_candidate(pdf, tmp_path / "out" / "run", ProvisionalSource(digest, REL), settings)
    assert fake_conversion == []


def test_semantic_map_identity_is_recorded_by_name_and_hash(tmp_path, fake_conversion):
    pdf, digest = make_pdf(tmp_path / "src")
    semantic = tmp_path / "meaning.md"
    semantic.write_text("# map\n", encoding="utf-8")
    manifest = run_candidate(
        pdf, tmp_path / "out" / "run", ProvisionalSource(digest, REL), ExtractionSettings(semantic_doc=semantic)
    )
    assert manifest["settings"]["semantic_doc_name"] == "meaning.md"
    assert manifest["settings"]["semantic_doc_sha256"] == hashlib.sha256(semantic.read_bytes()).hexdigest()
    assert str(tmp_path) not in json.dumps(manifest["settings"])


@pytest.mark.parametrize(
    "payload, expected",
    [
        ({"audit": {"status": "ok"}}, ("ok", "pending")),
        ({"audit": {"status": "ok"}, "extraction_audit": "error"}, ("error", "pending")),
        ({"audit": {"status": "ok"}, "extraction_audit": {"status": "warn"}, "content_review": {"status": "pending"}},
         ("warn", "pending")),
    ],
)
def test_status_fields_read_both_the_current_and_the_phase_c_shapes(payload, expected):
    assert adapter._status_fields(payload) == expected
```

- [ ] **Step 2: Run and confirm failure**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_cli.py`
Expected: collection error `ImportError: cannot import name 'ExtractionSettings'`.

- [ ] **Step 3: Implement.** In `prospectus.py` extend the imports:

```python
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from typing import Any, Mapping

from . import prospectus_extractor as extractor
from .prospectus_batch import package_sha256
from .prospectus_extractor.docling_env import DoclingUnavailable
```

(`Path`, `Literal`, `json`, `hashlib` are already imported; keep a single `from typing import ...` line: `from typing import Any, Literal, Mapping`.) Append to the end of the file:

```python
CANDIDATE_RUN_SCHEMA = "palsu-prospectus-candidate-run-v1"
MANIFEST_NAME = "candidate_run.json"
EXPECTED_FAILURES = (OSError, ValueError, DoclingUnavailable)

# Suffix -> role. Order matters only where one suffix ends another; unknown files are "other".
_ARTIFACT_ROLES = (
    ("_docling.meta.json", "docling_runtime_fingerprint"),
    ("_docling.json", "raw_docling"),
    ("_prospectus.json", "candidate_payload"),
    ("_essentials.json", "essentials"),
    ("_review.csv", "review_csv"),
    ("_prospectus.md", "prospectus_markup"),
)


@dataclass(frozen=True)
class ExtractionSettings:
    """Settings that influence candidate facts. CPU by default so hosts and containers agree."""

    semantic_doc: Path | None = None
    device: str = "cpu"


def file_sha256(path: Path) -> str:
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _distribution_version(name: str) -> str | None:
    try:
        return package_version(name)
    except PackageNotFoundError:
        return None


def _status_fields(payload: Mapping[str, Any]) -> tuple[str, str]:
    """(extraction_audit, content_review) from either the current or the Phase C payload shape."""
    audit = payload.get("extraction_audit", payload["audit"])
    if isinstance(audit, Mapping):
        audit = audit["status"]
    review = payload.get("content_review", "pending")
    if isinstance(review, Mapping):
        review = review.get("status", "pending")
    return str(audit), str(review)


def candidate_facts(payload: Mapping[str, Any]) -> dict[str, Any]:
    """The facts a reviewer will see, without paths, timestamps or anything run-specific."""
    essentials = extractor.build_essentials(payload)
    return {key: value for key, value in essentials.items() if key != "source_pdf"}


def _facts_sha256(facts: Mapping[str, Any]) -> str:
    canonical = json.dumps(facts, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _artifact_records(run_dir: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted(p for p in run_dir.rglob("*") if p.is_file()):
        if path.name == MANIFEST_NAME or path.name.endswith(".tmp"):
            continue
        role = next((name for suffix, name in _ARTIFACT_ROLES if path.name.endswith(suffix)), "other")
        records.append(
            {
                "role": role,
                "path": path.relative_to(run_dir).as_posix(),
                "sha256": file_sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    return records


def _write_json_atomic(path: Path, data: Mapping[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes((json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    temporary.replace(path)


def run_dir_for(output_root: Path, source: ProvisionalSource) -> Path:
    """<output root>/<locator without .pdf>: mirrors the source tree, so stems never collide."""
    parts = source.source_locator.split("/")
    return Path(output_root).joinpath(*parts[:-1], Path(parts[-1]).stem)


def run_candidate(
    pdf_path: Path,
    output_dir: Path,
    source: ProvisionalSource,
    settings: ExtractionSettings = ExtractionSettings(),
    *,
    source_root: Path | None = None,
) -> dict[str, Any]:
    """Convert one original PDF into a review-only candidate run and return its manifest.

    Nothing is written until the PDF bytes match the provisional record. Nothing here
    approves a source, a curriculum, RAG or Prolog.
    """
    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.is_file():
        raise FileNotFoundError(f"Original PDF not found: {pdf_path}")
    source.verify_pdf(pdf_path)
    semantic = Path(settings.semantic_doc).resolve() if settings.semantic_doc is not None else None
    if semantic is not None and not semantic.is_file():
        raise FileNotFoundError(f"Semantic map does not exist: {semantic}")
    run_dir = Path(output_dir).resolve()
    if (run_dir / MANIFEST_NAME).exists():
        raise FileExistsError(f"{run_dir} already holds a candidate run; choose a new output directory")
    run_dir.mkdir(parents=True, exist_ok=True)

    payload = extractor.process_prospectus(
        pdf_path,
        output_path=run_dir / f"{pdf_path.stem}_prospectus.json",
        export_csv=True,
        device=settings.device,
        semantic_doc_path=semantic,
        force_reconvert=True,
        quiet=True,
        source_root=source_root,
    )
    source.verify_pdf(pdf_path)  # the file must not have changed while Docling was reading it
    extraction_audit, content_review = _status_fields(payload)
    if content_review != "pending":
        raise ValueError(f"extractor reported content_review={content_review!r}; candidates start pending")

    facts = candidate_facts(payload)
    manifest = {
        "schema_version": CANDIDATE_RUN_SCHEMA,
        "provisional_source_id": source.provisional_source_id,
        "approved_source_version_id": None,
        "pdf_sha256": source.pdf_sha256,
        "source_locator": source.source_locator,
        "extraction_audit": extraction_audit,
        "content_review": content_review,
        "source_verification": source.source_verification,
        "versions": {
            "extractor_package_sha256": package_sha256(),
            "payload_schema_version": payload["schema_version"],
            "essentials_schema_version": extractor.build_essentials(payload)["schema_version"],
            "docling": _distribution_version("docling"),
            "docling_parse": _distribution_version("docling-parse"),
        },
        "settings": {
            "device": settings.device,
            "semantic_doc_name": semantic.name if semantic else None,
            "semantic_doc_sha256": file_sha256(semantic) if semantic else None,
        },
        "candidate_facts_sha256": _facts_sha256(facts),
        "artifacts": _artifact_records(run_dir),
    }
    _write_json_atomic(run_dir / MANIFEST_NAME, manifest)
    return manifest
```

- [ ] **Step 4: Run and confirm pass**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_cli.py`
Expected: all pass. If `test_manifest_records...` fails on a missing role, the Task 1 step 3 item 5 list of file names is out of date; fix `_ARTIFACT_ROLES` and re-run.

- [ ] **Step 5: Mutation check (tests must be able to fail).** Temporarily delete the first `source.verify_pdf(pdf_path)` line, run `... pytest -q tests/test_prospectus_cli.py::test_hash_mismatch_refuses_before_any_conversion_or_output` and confirm FAIL; restore the line. Then temporarily delete the second `verify_pdf`, confirm `test_a_pdf_changed_during_conversion_is_refused` FAILS, and restore.

- [ ] **Step 6: Commit**

```
git add backend/bintanong_tools/prospectus.py tests/test_prospectus_cli.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: add the hash-checked candidate-run adapter" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---



### Task 5: The `prospectus` command, single PDF (D1, D2)

**Files:**
- Modify: `backend/bintanong_tools/prospectus.py` (add `run_candidates`, single-PDF branch; folder branch is Task 6)
- Modify: `backend/bintanong_tools/ingest.py`
- Modify: `tests/test_prospectus_cli.py` (append)

- [ ] **Step 1: Write the failing tests** (append to `tests/test_prospectus_cli.py`; add `from typer.testing import CliRunner` and `from backend.bintanong_tools import ingest` to the imports)

```python
runner = CliRunner()


def make_world(tmp_path: Path, content: bytes = b"%PDF-1.4\nfixture one", declared: str | None = None):
    """A source tree with one PDF and an inventory CSV written the way Windows wrote it."""
    root = tmp_path / "sources"
    pdf, digest = make_pdf(root, REL, content)
    record = root / "records.csv"
    record.write_text(
        '"pdf_sha256","source_locator","source_verification"\n'
        f'"{declared or digest}","{REL.replace("/", chr(92))}","pending"\n',
        encoding="utf-8",
    )
    return root, pdf, record, digest


def invoke(*args):
    return runner.invoke(ingest.app, [str(a) for a in args])


def prospectus_args(root, pdf, record, out, *extra):
    return ["prospectus", pdf, "--source-root", root, "--source-record", record, "--output-dir", out, *extra]


def test_parse_stays_a_subcommand_and_prospectus_is_listed(tmp_path):
    listing = invoke("--help")
    assert listing.exit_code == 0
    assert "parse" in listing.output and "prospectus" in listing.output
    missing = tmp_path / "absent.pdf"
    result = invoke("parse", missing)
    assert isinstance(result.exception, FileNotFoundError)
    assert str(missing) in str(result.exception)


def test_prospectus_help_names_the_required_options():
    result = invoke("prospectus", "--help")
    assert result.exit_code == 0
    for option in ("--source-root", "--source-record", "--output-dir", "--semantic-doc", "--strict"):
        assert option in result.output


def test_single_pdf_writes_a_pending_candidate_run(tmp_path, fake_conversion):
    root, pdf, record, digest = make_world(tmp_path)
    out = tmp_path / "out"
    result = invoke(*prospectus_args(root, pdf, record, out))
    assert result.exit_code == 0, result.output
    run_dir = out / "Tiniguiban - Main" / "CS" / "prog"
    manifest = json.loads((run_dir / "candidate_run.json").read_text(encoding="utf-8"))
    assert manifest["pdf_sha256"] == digest
    assert "content_review=pending" in result.output
    assert "source_verification=pending" in result.output
    essentials = json.loads((run_dir / "prog_essentials.json").read_text(encoding="utf-8"))
    assert essentials["source_pdf"] == REL


def test_hash_mismatch_exits_2_and_writes_nothing(tmp_path, fake_conversion):
    root, pdf, record, _ = make_world(tmp_path, declared="f" * 64)
    out = tmp_path / "out"
    result = invoke(*prospectus_args(root, pdf, record, out))
    assert result.exit_code == 2
    assert "hash mismatch" in result.output
    assert fake_conversion == [] and not out.exists()


def test_a_pdf_without_a_record_exits_2(tmp_path, fake_conversion):
    root, pdf, record, _ = make_world(tmp_path)
    other, _ = make_pdf(root, "Tiniguiban - Main/CS/other.pdf", b"%PDF-1.4\nother")
    result = invoke(*prospectus_args(root, other, record, tmp_path / "out"))
    assert result.exit_code == 2
    assert "No provisional source record" in result.output
    assert fake_conversion == []


def test_a_record_claiming_approval_exits_2(tmp_path, fake_conversion):
    root, pdf, record, digest = make_world(tmp_path)
    record.write_text(
        '"pdf_sha256","source_locator","source_verification"\n'
        f'"{digest}","{REL}","approved"\n',
        encoding="utf-8",
    )
    result = invoke(*prospectus_args(root, pdf, record, tmp_path / "out"))
    assert result.exit_code == 2
    assert "pending" in result.output
    assert fake_conversion == []


def test_json_input_is_refused_because_candidates_start_from_original_pdfs(tmp_path, fake_conversion):
    root, pdf, record, _ = make_world(tmp_path)
    cached = root / "Tiniguiban - Main" / "CS" / "prog_docling.json"
    cached.write_text("{}", encoding="utf-8")
    result = invoke(*prospectus_args(root, cached, record, tmp_path / "out"))
    assert result.exit_code == 2
    assert "original PDF" in result.output


def test_missing_docling_is_reported_with_the_fix(tmp_path, monkeypatch):
    from backend.bintanong_tools.prospectus_extractor import pipeline
    from backend.bintanong_tools.prospectus_extractor.docling_env import DoclingUnavailable

    def unavailable(*_args, **_kwargs):
        raise DoclingUnavailable("Docling is required to convert PDFs.")

    monkeypatch.setattr(pipeline, "load_document", unavailable)
    root, pdf, record, _ = make_world(tmp_path)
    result = invoke(*prospectus_args(root, pdf, record, tmp_path / "out"))
    assert result.exit_code == 2
    assert "Docling is required" in result.output
    assert "--extra tools" in result.output


def test_the_command_never_falls_back_to_in_repo_default_paths(tmp_path, monkeypatch, fake_conversion):
    seen = {}
    real = adapter.extractor.process_prospectus

    def spy(*args, **kwargs):
        seen.update(kwargs)
        return real(*args, **kwargs)

    monkeypatch.setattr(adapter.extractor, "process_prospectus", spy)
    root, pdf, record, _ = make_world(tmp_path)
    assert invoke(*prospectus_args(root, pdf, record, tmp_path / "out")).exit_code == 0
    assert seen["semantic_doc_path"] is None
    assert Path(seen["source_root"]) == root.resolve()


def test_strict_exits_1_when_the_extraction_audit_is_error(tmp_path, monkeypatch):
    def error_manifest(*_args, **_kwargs):
        return {"extraction_audit": "error", "content_review": "pending",
                "source_verification": "pending", "pdf_sha256": "a" * 64}

    monkeypatch.setattr(adapter, "run_candidate", error_manifest)
    root, pdf, record, _ = make_world(tmp_path)
    assert invoke(*prospectus_args(root, pdf, record, tmp_path / "out")).exit_code == 0
    assert invoke(*prospectus_args(root, pdf, record, tmp_path / "out2", "--strict")).exit_code == 1
```

- [ ] **Step 2: Run and confirm failure**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_cli.py -k "subcommand or prospectus_help or single_pdf or mismatch or without_a_record or claiming or json_input or docling or defaults or strict"`
Expected: all of these fail (`No such command 'prospectus'` / the collapsed-root error for `parse`).

- [ ] **Step 3: Implement `run_candidates` (single-PDF branch).** Append to `prospectus.py` (add `import subprocess` and `import sys` to its imports now; Task 6 uses them):

```python
INDEX_NAME = "candidate_runs.json"
INDEX_SCHEMA = "palsu-prospectus-candidate-runs-v1"


def _summary(source: ProvisionalSource, manifest: Mapping[str, Any], manifest_path: str | None) -> dict[str, Any]:
    return {
        "source_locator": source.source_locator,
        "pdf_sha256": source.pdf_sha256,
        "status": "candidate",
        "extraction_audit": manifest["extraction_audit"],
        "content_review": manifest["content_review"],
        "source_verification": manifest["source_verification"],
        "manifest": manifest_path,
        "error": None,
    }


def run_candidates(
    target: Path,
    source_root: Path,
    record_path: Path,
    output_root: Path,
    settings: ExtractionSettings,
    module: str = "bintanong_tools.ingest",
) -> list[dict[str, Any]]:
    """Single PDF or folder. Every PDF is checked against its record before any converts."""
    target = Path(target).resolve()
    source_root = Path(source_root).resolve()
    output_root = Path(output_root).resolve()
    if not target.exists():
        raise FileNotFoundError(f"Input not found: {target}")
    if target.is_file():
        if target.suffix.lower() != ".pdf":
            raise ValueError(f"The prospectus command takes original PDFs only, not {target.name}")
        pdfs = [target]
    else:
        pdfs = sorted(p for p in target.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf")
        if not pdfs:
            raise ValueError(f"No PDFs found under {target}")
    records = load_provisional_sources(record_path)
    plan: list[tuple[Path, ProvisionalSource, Path]] = []
    for pdf in pdfs:
        source = source_for_pdf(records, pdf, source_root)
        source.verify_pdf(pdf)
        run_dir = run_dir_for(output_root, source)
        if (run_dir / MANIFEST_NAME).exists():
            raise FileExistsError(f"{run_dir} already holds a candidate run; choose a new output directory")
        plan.append((pdf, source, run_dir))

    if target.is_file():
        pdf, source, run_dir = plan[0]
        manifest = run_candidate(pdf, run_dir, source, settings, source_root=source_root)
        return [_summary(source, manifest, (run_dir / MANIFEST_NAME).relative_to(output_root).as_posix())]
    return _run_folder(plan, source_root, record_path, output_root, settings, module)
```

and a stub-free placeholder for the folder function is **not** acceptable, so add the real one now (Task 6 only tests it):

```python
def _child_command(module, pdf, source_root, record_path, output_root, settings) -> list[str]:
    command = [
        sys.executable, "-m", module, "prospectus", str(pdf),
        "--source-root", str(source_root),
        "--source-record", str(Path(record_path).resolve()),
        "--output-dir", str(output_root),
        "--device", settings.device,
    ]
    if settings.semantic_doc is not None:
        command += ["--semantic-doc", str(Path(settings.semantic_doc).resolve())]
    return command


def _run_child(command: list[str]) -> "subprocess.CompletedProcess[str]":
    """The process boundary; tests replace this function."""
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _run_folder(plan, source_root, record_path, output_root, settings, module) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for pdf, source, run_dir in plan:
        completed = _run_child(_child_command(module, pdf, source_root, record_path, output_root, settings))
        manifest_path = run_dir / MANIFEST_NAME
        if completed.returncode == 0 and manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            summaries.append(_summary(source, manifest, manifest_path.relative_to(output_root).as_posix()))
        else:
            detail = (completed.stderr or completed.stdout or "").strip()[-2000:]
            summaries.append(
                {
                    "source_locator": source.source_locator,
                    "pdf_sha256": source.pdf_sha256,
                    "status": "processing_error",
                    "extraction_audit": None,
                    "content_review": None,
                    "source_verification": source.source_verification,
                    "manifest": None,
                    "error": f"exit {completed.returncode}: {detail}",
                }
            )
        output_root.mkdir(parents=True, exist_ok=True)
        _write_json_atomic(output_root / INDEX_NAME, {"schema_version": INDEX_SCHEMA, "runs": summaries})
    return summaries
```

- [ ] **Step 4: Implement the command.** Replace the imports block at the top of `ingest.py` and append the command before the `if __name__` guard. Imports become:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
import typer
```

(unchanged). Add this command after `parse_cmd`:

```python
@app.command("prospectus")
def prospectus_cmd(
    path: Path = typer.Argument(..., help="Original prospectus PDF, or a folder of them"),
    source_root: Path = typer.Option(
        ..., "--source-root", help="Folder the source record's locators are relative to"
    ),
    source_record: Path = typer.Option(
        ..., "--source-record", help="Provisional source record: inventory .csv or .json (hash + locator)"
    ),
    output_dir: Path = typer.Option(
        ..., "--output-dir", "-o", help="New candidate output folder (one run folder per PDF)"
    ),
    semantic_doc: Path = typer.Option(
        None, "--semantic-doc", help="College/program reference markdown (optional; no default)"
    ),
    device: str = typer.Option("cpu", "--device", help="cpu, cuda or auto"),
    strict: bool = typer.Option(False, "--strict", help="Exit 1 when an extraction audit is error"),
) -> None:
    """Convert original PDFs into review-only candidate runs. Nothing is approved or activated."""
    if device not in ("cpu", "cuda", "auto"):
        raise typer.BadParameter("must be cpu, cuda or auto", param_hint="--device")
    from . import prospectus as adapter  # lazy: keeps `parse --help` free of extractor imports

    settings = adapter.ExtractionSettings(semantic_doc=semantic_doc, device=device)
    try:
        runs = adapter.run_candidates(
            path, source_root, source_record, output_dir, settings, module=__spec__.name if __spec__ else "bintanong_tools.ingest"
        )
    except adapter.EXPECTED_FAILURES as exc:
        typer.echo(f"Refused: {exc}", err=True)
        if isinstance(exc, adapter.DoclingUnavailable):
            typer.echo("Install the tools extra: uv sync --project backend --extra tools", err=True)
        raise typer.Exit(2) from exc
    for run in runs:
        typer.echo(
            f"{run['status']}: {run['source_locator']} extraction_audit={run['extraction_audit']} "
            f"content_review={run['content_review']} source_verification={run['source_verification']}"
            + (f" manifest={run['manifest']}" if run["manifest"] else f" error={run['error']}")
        )
    if any(run["status"] == "processing_error" for run in runs):
        raise typer.Exit(2)
    if strict and any(run["extraction_audit"] == "error" for run in runs):
        raise typer.Exit(1)
```

`run_candidates` single-PDF returns `_summary(...)` built from the manifest, so the strict test's fake manifest (with only the four keys it returns) must satisfy `_summary`; it does (`extraction_audit`, `content_review`, `source_verification`) and `pdf_sha256` is unused by `_summary`. Note the strict test replaces `adapter.run_candidate`, which `run_candidates` calls by module-global name, so the fake is used; the preflight (record + hash) still runs for real.

- [ ] **Step 5: Run the new tests, then the existing contract**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_cli.py tests/test_tools_contract.py`
Expected: all pass, including `test_ingest_cli_help`, `test_evaluate_cli_help`, and the synthetic PDF parse test.

- [ ] **Step 6: Commit**

```
git add backend/bintanong_tools/prospectus.py backend/bintanong_tools/ingest.py tests/test_prospectus_cli.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: add the review-only prospectus command to the ingest tool" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---



### Task 6: Folder mode tests (D3)

**Files:** `tests/test_prospectus_cli.py` (append). The implementation went in with Task 5; this task proves it and may adjust it.

- [ ] **Step 1: Write the tests** (append; add `import subprocess` to the imports)

```python
def fake_child_via_cli(command):
    """Stand in for the child process: run the same arguments through the real command."""
    result = invoke(*command[command.index("prospectus"):])
    return subprocess.CompletedProcess(command, result.exit_code, result.output, "")


def make_folder(tmp_path: Path):
    root = tmp_path / "sources"
    first, first_hash = make_pdf(root, "Tiniguiban - Main/CS/one.pdf", b"%PDF-1.4\none")
    second, second_hash = make_pdf(root, "Tiniguiban - Main/CAD/two.pdf", b"%PDF-1.4\ntwo")
    twin, _ = make_pdf(root, "Tiniguiban - Main/CAH/one-copy.pdf", b"%PDF-1.4\none")
    record = root / "records.csv"
    rows = [
        (first_hash, "Tiniguiban - Main\\CS\\one.pdf"),
        (second_hash, "Tiniguiban - Main\\CAD\\two.pdf"),
        (first_hash, "Tiniguiban - Main\\CAH\\one-copy.pdf"),
    ]
    record.write_text(
        '"pdf_sha256","source_locator","source_verification"\n'
        + "".join(f'"{digest}","{locator}","pending"\n' for digest, locator in rows),
        encoding="utf-8",
    )
    return root, record


def test_folder_runs_one_child_per_pdf_and_indexes_the_runs(tmp_path, monkeypatch, fake_conversion):
    root, record = make_folder(tmp_path)
    commands = []

    def spy(command):
        commands.append(command)
        return fake_child_via_cli(command)

    monkeypatch.setattr(adapter, "_run_child", spy)
    out = tmp_path / "out"
    result = invoke(*prospectus_args(root, root, record, out))
    assert result.exit_code == 0, result.output
    assert len(commands) == 3 and len(fake_conversion) == 3
    for command in commands:
        assert command[1:3] == ["-m", "backend.bintanong_tools.ingest"]
        assert "--semantic-doc" not in command
    index = json.loads((out / "candidate_runs.json").read_text(encoding="utf-8"))
    assert index["schema_version"] == "palsu-prospectus-candidate-runs-v1"
    assert sorted(run["source_locator"] for run in index["runs"]) == [
        "Tiniguiban - Main/CAD/two.pdf",
        "Tiniguiban - Main/CAH/one-copy.pdf",
        "Tiniguiban - Main/CS/one.pdf",
    ]
    assert all(run["status"] == "candidate" for run in index["runs"])
    # Byte-identical PDFs share an ID but keep separate run directories.
    assert (out / "Tiniguiban - Main" / "CS" / "one" / "candidate_run.json").is_file()
    assert (out / "Tiniguiban - Main" / "CAH" / "one-copy" / "candidate_run.json").is_file()


def test_folder_preflight_blocks_everything_when_one_pdf_has_no_record(tmp_path, monkeypatch, fake_conversion):
    root, record = make_folder(tmp_path)
    make_pdf(root, "Tiniguiban - Main/CS/unrecorded.pdf", b"%PDF-1.4\nunrecorded")
    calls = []
    monkeypatch.setattr(adapter, "_run_child", lambda command: calls.append(command))
    out = tmp_path / "out"
    result = invoke(*prospectus_args(root, root, record, out))
    assert result.exit_code == 2
    assert "unrecorded.pdf" in result.output
    assert calls == [] and not out.exists()


def test_folder_preflight_blocks_everything_on_one_hash_mismatch(tmp_path, monkeypatch, fake_conversion):
    root, record = make_folder(tmp_path)
    (root / "Tiniguiban - Main" / "CAD" / "two.pdf").write_bytes(b"%PDF-1.4\nreplaced")
    calls = []
    monkeypatch.setattr(adapter, "_run_child", lambda command: calls.append(command))
    result = invoke(*prospectus_args(root, root, record, tmp_path / "out"))
    assert result.exit_code == 2
    assert "hash mismatch" in result.output
    assert calls == []


def test_a_failed_child_is_recorded_and_the_batch_exits_2(tmp_path, monkeypatch, fake_conversion):
    root, record = make_folder(tmp_path)

    def flaky(command):
        if command[command.index("prospectus") + 1].endswith("two.pdf"):
            return subprocess.CompletedProcess(command, 3, "", "std::bad_alloc")
        return fake_child_via_cli(command)

    monkeypatch.setattr(adapter, "_run_child", flaky)
    out = tmp_path / "out"
    result = invoke(*prospectus_args(root, root, record, out))
    assert result.exit_code == 2
    index = json.loads((out / "candidate_runs.json").read_text(encoding="utf-8"))
    failed = [run for run in index["runs"] if run["status"] == "processing_error"]
    assert len(failed) == 1 and "std::bad_alloc" in failed[0]["error"]
    assert sum(run["status"] == "candidate" for run in index["runs"]) == 2


def test_child_command_carries_the_semantic_map(tmp_path):
    command = adapter._child_command(
        "bintanong_tools.ingest", tmp_path / "a.pdf", tmp_path, tmp_path / "r.csv", tmp_path / "o",
        ExtractionSettings(semantic_doc=tmp_path / "m.md", device="cpu"),
    )
    assert command[command.index("--semantic-doc") + 1] == str((tmp_path / "m.md").resolve())
    assert command[command.index("--device") + 1] == "cpu"
```

- [ ] **Step 2: Run**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_cli.py`
Expected: all pass. A failure of `test_folder_runs_one_child...` on the module name means `__spec__.name` is `None` when invoked through `CliRunner`: confirm it resolves to `backend.bintanong_tools.ingest`, and if the test environment gives a different name fix the assertion, not the code.

- [ ] **Step 3: Mutation check.** In `_run_folder`, temporarily change `completed.returncode == 0` to `True`, run `test_a_failed_child_is_recorded_and_the_batch_exits_2`, confirm FAIL, restore.

- [ ] **Step 4: Commit**

```
git add backend/bintanong_tools/prospectus.py tests/test_prospectus_cli.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "test: pin folder mode, preflight refusal and child failure handling" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---



### Task 7: CLI/API equivalence

**Files:** `tests/test_prospectus_cli.py` (append).

- [ ] **Step 1: Write the tests** (append; add to imports: `from backend.bintanong_tools.prospectus import run_dir_for, source_for_pdf, load_provisional_sources`, and `from backend.bintanong_tools.prospectus_extractor import pipeline`, `from backend.bintanong_tools.prospectus_extractor.selftest import BSA_TEXT_ITEMS, bsa_fixture_grid, fixture_document`)

```python
def test_cli_and_api_produce_equal_candidate_facts(tmp_path, fake_conversion):
    root, pdf, record, digest = make_world(tmp_path)
    cli_out, api_out = tmp_path / "cli", tmp_path / "api"
    assert invoke(*prospectus_args(root, pdf, record, cli_out)).exit_code == 0

    source = source_for_pdf(load_provisional_sources(record), pdf, root)
    api_manifest = run_candidate(pdf, run_dir_for(api_out, source), source, source_root=root)

    cli_manifest = json.loads(
        (run_dir_for(cli_out, source) / "candidate_run.json").read_text(encoding="utf-8")
    )
    for key in ("provisional_source_id", "pdf_sha256", "extraction_audit", "content_review",
                "source_verification", "candidate_facts_sha256", "versions", "settings"):
        assert cli_manifest[key] == api_manifest[key], key
    cli_artifact = {a["path"]: a["sha256"] for a in cli_manifest["artifacts"] if a["role"] == "essentials"}
    api_artifact = {a["path"]: a["sha256"] for a in api_manifest["artifacts"] if a["role"] == "essentials"}
    assert cli_artifact == api_artifact and cli_artifact


def test_candidate_facts_change_when_the_extracted_content_changes(tmp_path, monkeypatch, fake_conversion):
    pdf, digest = make_pdf(tmp_path / "src")
    source = ProvisionalSource(digest, REL)
    first = run_candidate(pdf, tmp_path / "one", source)
    again = run_candidate(pdf, tmp_path / "two", source)
    assert first["candidate_facts_sha256"] == again["candidate_facts_sha256"]

    def other_document(input_path, device="auto", force_reconvert=True, converter=None, raw_json_path=None):
        Path(raw_json_path).parent.mkdir(parents=True, exist_ok=True)
        Path(raw_json_path).write_text('{"fixture": true}', encoding="utf-8")
        return fixture_document(bsa_fixture_grid(), BSA_TEXT_ITEMS), Path(raw_json_path)

    monkeypatch.setattr(pipeline, "load_document", other_document)
    different = run_candidate(pdf, tmp_path / "three", source)
    assert different["candidate_facts_sha256"] != first["candidate_facts_sha256"]
```

- [ ] **Step 2: Run**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_cli.py -k "equal_candidate_facts or extracted_content_changes"`
Expected: both pass (the implementation exists). If the first fails on `versions` or `settings`, find which key differs and fix the code, not the test.

- [ ] **Step 3: Full suite, then commit**

Run: `uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests`
Expected: all pass.

```
git add tests/test_prospectus_cli.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "test: pin CLI and API equivalence for candidate facts" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---



### Task 8: Compose, `.dockerignore`, env example (D4, D5)

**Files:**
- Modify: `compose.yaml`, `.dockerignore`, `.env.example`, `tests/test_scaffold_contract.py`
- Create: `tests/test_prospectus_compose.py`

- [ ] **Step 1: Write the failing tests** `tests/test_prospectus_compose.py`

```python
from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BASE_ENV = {
    "MODELS_DIR": str(ROOT / ".missing-models"),
    "BINTU_MODEL_RELATIVE_PATH": "GEMMA_4_E4B/model.gguf",
    "EMBEDDING_MODEL_RELATIVE_PATH": "SEA-LION-E5-Embedding-600M",
}


def compose_config(extra: dict[str, str], drop: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
    env = {key: value for key, value in os.environ.items() if key not in drop}
    env.update(BASE_ENV)
    env.update(extra)
    return subprocess.run(
        ["docker", "compose", "-f", "compose.yaml", "--profile", "tools", "config", "--format", "json"],
        cwd=ROOT, env=env, text=True, capture_output=True, check=False,
    )


@unittest.skipUnless(shutil.which("docker"), "docker CLI not installed")
class ProspectusComposeTests(unittest.TestCase):
    EXTRA = {"PROSPECTUS_PDF_DIR": str(ROOT / ".missing-pdfs"), "PROSPECTUS_OUTPUT_DIR": str(ROOT / ".missing-out")}

    def test_pdfs_are_read_only_and_outputs_are_a_separate_writable_mount(self) -> None:
        result = compose_config(self.EXTRA)
        self.assertEqual(result.returncode, 0, result.stderr)
        ingest = json.loads(result.stdout)["services"]["ingest"]
        mounts = {volume["target"]: volume for volume in ingest["volumes"]}
        self.assertTrue(mounts["/sources"]["read_only"])
        self.assertEqual(mounts["/sources"]["type"], "bind")
        self.assertFalse(mounts["/candidate-output"].get("read_only", False))
        self.assertNotEqual(mounts["/sources"]["source"], mounts["/candidate-output"]["source"])
        self.assertEqual(mounts["/cache"]["type"], "volume")
        self.assertFalse(mounts["/cache"].get("read_only", False))

    def test_weight_cache_variables_point_into_the_cache_volume(self) -> None:
        result = compose_config(self.EXTRA)
        environment = json.loads(result.stdout)["services"]["ingest"]["environment"]
        self.assertEqual(environment["HF_HOME"], "/cache/huggingface")
        self.assertEqual(environment["DOCLING_CACHE_DIR"], "/cache/docling")
        self.assertEqual(environment["HF_HUB_OFFLINE"], "0")

    def test_no_tools_service_publishes_a_port_and_no_other_service_sees_the_pdfs(self) -> None:
        services = json.loads(compose_config(self.EXTRA).stdout)["services"]
        for name in ("ingest", "evaluate"):
            self.assertNotIn("ports", services[name])
        for name, service in services.items():
            if name == "ingest":
                continue
            targets = {volume["target"] for volume in service.get("volumes", [])}
            self.assertFalse({"/sources", "/candidate-output"} & targets, name)

    def test_missing_pdf_or_output_directory_variable_is_a_clear_error(self) -> None:
        for missing, kept in (("PROSPECTUS_PDF_DIR", "PROSPECTUS_OUTPUT_DIR"), ("PROSPECTUS_OUTPUT_DIR", "PROSPECTUS_PDF_DIR")):
            result = compose_config({kept: self.EXTRA[kept]}, drop=(missing,))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(missing, result.stderr)


class DockerContextTests(unittest.TestCase):
    def test_dockerignore_keeps_institutional_pdfs_and_the_host_venv_out_of_the_image(self) -> None:
        lines = {line.strip() for line in (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()}
        for required in (
            "backend/bintanong_tools/bintanong_jsonifer_prolog/dataset",
            "**/docling_jsonified_output",
            "**/.venv",
            "**/.docling-venv",
        ):
            self.assertIn(required, lines)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run and confirm failure**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_compose.py`
Expected: 4 compose tests fail (`KeyError: '/sources'` or the variable not required) and the dockerignore test fails; if Docker CLI is missing they skip, which means this red step is not valid: use a machine with the CLI (it is installed here; no daemon is needed for `compose config`).

- [ ] **Step 3: Edit `compose.yaml`.** Replace the whole `ingest` service (was lines 92-104) with:

```yaml
  ingest:
    profiles: [tools]
    build:
      context: .
      dockerfile: docker/ingest.Dockerfile
    command: [python, -m, bintanong_tools.ingest, --help]
    environment:
      MODELS_ROOT: /models
      HF_HOME: /cache/huggingface
      DOCLING_CACHE_DIR: /cache/docling
      HF_HUB_OFFLINE: ${HF_HUB_OFFLINE:-0}
    volumes:
      - ${MODELS_DIR:?Set MODELS_DIR}:/models:ro
      - ${PROSPECTUS_PDF_DIR:?Set PROSPECTUS_PDF_DIR to the folder holding the original prospectus PDFs}:/sources:ro
      - ${PROSPECTUS_OUTPUT_DIR:?Set PROSPECTUS_OUTPUT_DIR to a writable folder for candidate runs}:/candidate-output
      - docling-cache:/cache
      - ./tests/fixtures:/workspace/tests/fixtures:ro
      - ./artifacts:/workspace/artifacts
    networks: [bintanong-local]
```

and add, between the `evaluate` service and `networks:`, a top-level block:

```yaml
volumes:
  docling-cache:
```

(There is no `ports:` on any tools service and none is added.)

- [ ] **Step 4: Edit `.dockerignore`.** Append:

```
backend/bintanong_tools/bintanong_jsonifer_prolog/dataset
**/docling_jsonified_output
**/.venv
**/.docling-venv
```

- [ ] **Step 5: Edit `.env.example`.** Append:

```
PROSPECTUS_PDF_DIR=C:/Coding-projects/prospectus-source-pdfs
PROSPECTUS_OUTPUT_DIR=C:/Coding-projects/prospectus-candidates
HF_HUB_OFFLINE=0
```

- [ ] **Step 6: Keep the existing compose test valid.** In `tests/test_scaffold_contract.py`, add two entries to the `env = os.environ | {...}` mapping in `test_compose_base_has_required_services_and_tools_profiles`:

```python
            "PROSPECTUS_PDF_DIR": str(ROOT / ".missing-pdfs"),
            "PROSPECTUS_OUTPUT_DIR": str(ROOT / ".missing-out"),
```

- [ ] **Step 7: Run and confirm pass**

Run: `uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests/test_prospectus_compose.py tests/test_scaffold_contract.py`
Expected: all pass.

- [ ] **Step 8: Commit**

```
git add compose.yaml .dockerignore .env.example tests/test_prospectus_compose.py tests/test_scaffold_contract.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: mount institutional PDFs read-only and outputs separately for the tools profile" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---



### Task 9: Docker verification and weight cache (evidence task)

**Files:** `docker/ingest.Dockerfile` only if a system library is missing; evidence goes into `docs/decisions/prospectus-tools-boundary.md` (created in Task 11) and the progress file. No claim may be written that a command did not show.

The whole task needs a running Linux-container Docker. Variables used below (PowerShell):

```
$Repo = "C:\Users\Hawksprey\source\repos\Bintanong"
$Dataset = "$Repo\backend\bintanong_tools\bintanong_jsonifer_prolog\dataset\PalSU Undergraduate Prospectus Website Dump"
$Out = "$env:TEMP\bintanong-candidates"
$env:MODELS_DIR = "C:/Coding-projects/MODELS"      # must exist or be any readable folder; compose requires it
$env:PROSPECTUS_PDF_DIR = $Dataset -replace '\\','/'
$env:PROSPECTUS_OUTPUT_DIR = $Out -replace '\\','/'
$env:BINTU_MODEL_RELATIVE_PATH = "GEMMA_4_E4B/gemma-4-E4B-it-UD-Q4_K_XL.gguf"
$env:EMBEDDING_MODEL_RELATIVE_PATH = "SEA-LION-E5-Embedding-600M"
```

- [ ] **Step 1: Check the engine**

Run: `docker version`
Expected when usable: both a `Client` and a `Server` section, with `Server: ... OS/Arch: linux/amd64`. On 3 October the server section failed with `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`.

If the server is missing, try once: `Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"`, then poll `docker info --format "{{.OSType}}"` every 15 seconds for up to 4 minutes (a loop with `Start-Sleep -Seconds 15` is acceptable here because it is a bounded poll of an external process). Expected: `linux`. If it never answers, or the path differs, or Windows containers are selected, **stop this task as skipped**: append to the progress file and to the decision doc's Evidence section exactly

```
Container gate: NOT RUN. docker version showed no reachable Linux engine (<paste the error line>). Phase F's container gate stays open; no container evidence is claimed.
```

then continue with Tasks 10 and 11. Do not report Phase F's gate as passed.

- [ ] **Step 2: Network, build (detached, it downloads Docling and torch)**

```
docker network inspect bintanong-local *> $null; if ($LASTEXITCODE -ne 0) { docker network create bintanong-local }
Start-Process pwsh -ArgumentList '-NoProfile','-Command',"cd '$Repo'; docker compose --profile tools build ingest *> '$env:TEMP\ingest-build.log'; `$LASTEXITCODE | Out-File '$env:TEMP\ingest-build.exit'" -WindowStyle Hidden
```

Poll `Get-Content $env:TEMP\ingest-build.exit` until it exists (re-check every few minutes; a build can exceed 10 minutes, so never run it in the foreground). Expected: `0`. Confirm the image holds no institutional data and no host venv: `docker compose --profile tools run --rm ingest sh -c "ls /workspace/backend/bintanong_tools/bintanong_jsonifer_prolog; cat /workspace/backend/.venv/pyvenv.cfg | head -3"`. Expected: no `dataset` entry; `pyvenv.cfg` mentions a Linux path (`/usr/local/bin` or similar), not `C:\`.

If the build or a later import fails with `libGL.so.1` or `libgthread` missing, edit `docker/ingest.Dockerfile` and insert before the `COPY backend` line:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
```

rebuild, and commit the Dockerfile with message `fix: add system libraries Docling needs in the ingest image`. Only add it if the failure actually appears.

- [ ] **Step 3: The command-shape check required by the draft**

Run: `docker compose --profile tools run --rm ingest python -m bintanong_tools.ingest prospectus --help`
Expected: exit 0 and help text listing `--source-root`, `--source-record`, `--output-dir`, `--semantic-doc`, `--strict`. Also run the same with `parse --help` and bare `--help` (expected: both commands listed). Save the three outputs' first lines into the evidence.

- [ ] **Step 4: Prepare the pilot inputs.** The semantic map is not in the local dataset copy. Copy it from the external dump into the ignored dataset folder (read from the E: dump, write only under the ignored path):

```
Copy-Item "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md" "$Dataset\Tiniguiban - Main\"
git status --short   # must still show nothing new (the folder is git-ignored)
```

Pilot PDF: `Tiniguiban - Main\CS\Computer Science\New Curriculum (2025-2026)\1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf` (its record exists in `provisional-source-inventory.csv`).

- [ ] **Step 5: First conversion in the container (online, populates the weight cache). Detached, then polled.**

```
$pilot = "/sources/Tiniguiban - Main/CS/Computer Science/New Curriculum (2025-2026)/1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf"
$cmd = "docker compose --profile tools run --rm ingest python -m bintanong_tools.ingest prospectus `"$pilot`" --source-root /sources --source-record /sources/provisional-source-inventory.csv --semantic-doc `"/sources/Tiniguiban - Main/palsu_main_undergrad_program_college_meaning.md`" --output-dir /candidate-output --device cpu *> '$env:TEMP\pilot-container.log'; `$LASTEXITCODE | Out-File '$env:TEMP\pilot-container.exit'"
Start-Process pwsh -ArgumentList '-NoProfile','-Command',"cd '$Repo'; $cmd" -WindowStyle Hidden
```

Poll the `.exit` file. Expected exit `0` or `1`-free: the command was run without `--strict`, so `0` even if the audit is `error`. Then `Get-Content "$Out\Tiniguiban - Main\CS\Computer Science\New Curriculum (2025-2026)\1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025\candidate_run.json"` and note `extraction_audit`, `content_review` (must be `pending`), `source_verification` (must be `pending`), `approved_source_version_id` (must be `null`).

Confirm the PDFs are really read-only: `docker compose --profile tools run --rm ingest sh -c "touch /sources/x 2>&1; echo exit=$?"`. Expected: `Read-only file system`, nonzero exit. Confirm writes go to the output mount (the run folder above exists on the host).

- [ ] **Step 6: Where did the weights go, and does a second run work offline (D5)**

```
docker compose --profile tools run --rm ingest sh -c "du -sh /cache/huggingface /cache/docling /root/.cache 2>&1; find /cache -maxdepth 3 -type d | head -30"
```

Record the output. Expected: the weights are under `/cache/huggingface` and/or `/cache/docling`. **If they are under `/root/.cache` instead** (that is the failure this step exists to catch: the env names are assumptions), change `compose.yaml` `environment:` to the variable Docling actually used (or mount the volume at `/root/.cache`), update the matching assertions in `tests/test_prospectus_compose.py::test_weight_cache_variables_point_into_the_cache_volume`, and re-run Step 5.

Offline proof, with a new output folder because runs are never overwritten:

```
$env:PROSPECTUS_OUTPUT_DIR = ("$env:TEMP\bintanong-candidates-offline" -replace '\\','/')
$env:HF_HUB_OFFLINE = "1"
```

then re-run Step 5's command (same detached pattern, log `pilot-container-offline.log`). Expected: it succeeds without network fetches. If it fails with a Hugging Face offline error, the cache is incomplete: record that, fall back to option (c) in D5 (pre-seed with `docling-tools models download` into a bind mount and set `DOCLING_ARTIFACTS_PATH`), and say so in the decision doc. Reset `$env:HF_HUB_OFFLINE = "0"` afterwards.

- [ ] **Step 7: Host run of the same PDF and the equivalence comparison.** Host side, same settings (detached, ~2+ minutes):

```
$hostOut = "$env:TEMP\bintanong-candidates-host"
$pilotHost = "$Dataset\Tiniguiban - Main\CS\Computer Science\New Curriculum (2025-2026)\1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025.pdf"
Start-Process pwsh -ArgumentList '-NoProfile','-Command',"cd '$Repo\backend'; uv run --extra tools python -m bintanong_tools.ingest prospectus '$pilotHost' --source-root '$Dataset' --source-record '$Dataset\provisional-source-inventory.csv' --semantic-doc '$Dataset\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md' --output-dir '$hostOut' --device cpu *> '$env:TEMP\pilot-host.log'; `$LASTEXITCODE | Out-File '$env:TEMP\pilot-host.exit'" -WindowStyle Hidden
```

Then compare:

```
$rel = "Tiniguiban - Main\CS\Computer Science\New Curriculum (2025-2026)\1_BS Computer Science_for BOR approval _rev02_v7_6 August 2025\candidate_run.json"
$h = Get-Content "$hostOut\$rel" -Raw | ConvertFrom-Json
$c = Get-Content "$Out\$rel" -Raw | ConvertFrom-Json
foreach ($k in 'provisional_source_id','pdf_sha256','extraction_audit','content_review','source_verification','candidate_facts_sha256') { "{0}: host={1} container={2} equal={3}" -f $k,$h.$k,$c.$k,($h.$k -eq $c.$k) }
"package hash equal: " + ($h.versions.extractor_package_sha256 -eq $c.versions.extractor_package_sha256)
"docling equal: " + ($h.versions.docling -eq $c.versions.docling)
```

Expected: every `equal=True`. Artifact byte hashes are expected to differ (CRLF on the Windows host, LF in the container; Finding 4) and must not be used as the test. If `candidate_facts_sha256` differs, do not weaken the check: diff the two `*_essentials.json` files field by field and report the first differing course field; that is a real host/container difference (likely Docling or table-model variance) and is the finding. If `extractor_package_sha256` differs, `.dockerignore` or a checkout line-ending issue changed the package bytes; investigate before anything else.

- [ ] **Step 8: Record the evidence** in the progress file now (the decision doc is written in Task 11 and includes it): the engine versions from `docker version`, the three exit codes, the observed `extraction_audit`, the cache listing, the offline result, the equal/not-equal lines above. Commit any Dockerfile or compose adjustment made in this task with a message naming the actual failure.

---

