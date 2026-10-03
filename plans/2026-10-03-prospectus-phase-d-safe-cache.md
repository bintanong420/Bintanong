# Prospectus Phase D: Safe Cache and Output Publication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task, with superpowers:test-driven-development inside each task. Steps use checkbox (`- [ ]`) syntax for tracking. Tasks run on the project agent `extractor-implementer` and are reviewed by `extractor-reviewer`. Append to `plans/plan_current_progress/extractor_split_progress.md` after every task.

**Goal:** A Docling conversion or an output set is reused only when its recorded identity (PDF bytes, conversion settings, parser package, schema) matches, and `process_prospectus` can no longer destroy earlier outputs: it writes into a staging directory beside the target and publishes only after conversion and audit finish.

**Architecture:** One new stdlib-only module `identity.py` computes hashes and identities (shared by the package and by `prospectus_batch.py`, so there is no import cycle). One new module `publish.py` owns staging, file-by-file publication with a hash manifest written last, stale-file removal and failure diagnostics. `loader.py` validates the raw Docling JSON cache against a conversion identity; `pipeline.py` stages and publishes; `batch.py` decides `--skip-existing` from the published manifest instead of file existence.

**Tech Stack:** Python 3.13, stdlib only (`hashlib`, `json`, `pathlib`, `shutil`, `uuid`), pytest 9, `uv`. No new dependency.

**Base:** branch `feature/prospectus-phase-d-safe-cache` from `dev` after Phase C merges. Line numbers below are as of `8d26f18`; Task 1 re-checks them.

---

## Decisions needed before execution

The rest of this plan assumes the recommendation. Steps that would change are marked **(D#)**.

**D1. Is the parser package hash part of the raw Docling JSON cache key?** The outline says cache identity = PDF hash + conversion settings + parser package hash.
- (a) Literal: one key with all three. Any edit to any `.py` in the package forces a 2-minute reconversion of every PDF, although the raw Docling JSON does not depend on parser code at all.
- (b) **Recommended:** two identities. `conversion_identity` = PDF hash + conversion settings (guards the raw Docling JSON). `run_key` = conversion identity + package hash + schema version + semantic-doc hash (guards a finished output set and `--skip-existing`). A parser change still invalidates every output and still re-parses, but re-parses from the cached JSON in seconds instead of reconverting.
- (c) Package hash nowhere: unsafe, rejected.
Marked **(D1)** in Tasks 2, 4, 6, 7.

**D2. Is the device (`cpu`/`cuda`) part of the identity?**
- (a) Yes: a CPU run never serves a CUDA run.
- (b) **Recommended:** no. Device does not change the conversion settings that matter to the parsed table topology, and the 44 cached inputs are CPU runs; keying on device would invalidate them for no known benefit. If a CUDA/CPU table difference is ever measured, add `device` to `conversion_settings()`; that is a one-line change plus a test.
Marked **(D2)** in Task 2.

**D3. An audit of `error` on a completed run: publish or hold back?**
- (a) **Recommended:** publish. The `_prospectus.json` with `audit.status == "error"` is the diagnostic the reviewer and `prospectus_batch.run_isolated` read (it requires the JSON to exist and its exit code to agree with an `error` audit). Companions that must not look current (`.pl`, `_rag.jsonl`) are removed after publication; the publish manifest records `audit_status: "error"`, and `--skip-existing` never skips it.
- (b) Keep the previous good set and write the error run only under `failed/`. Safer for a good set that a worse parser regresses, but the isolated runner and batch summary lose their error JSON.
"Failure" in this plan means an exception (conversion, parse, build, staging, publish), which always leaves earlier outputs untouched. Marked **(D3)** in Task 6.

**D4. Do `process_prospectus`, the CLI and the batch reuse a valid raw Docling JSON cache by default?** Today the CLI and batch hard-code `force_reconvert=True` (cli.py:124, batch.py:211), so the cache is never reused outside a direct `load_document` call.
- (a) **Recommended:** reuse when the conversion identity matches; `--force` means reconvert. This is safe only because the cache is now identity-checked, and it is what makes parser-only re-runs fast.
- (b) Keep always-reconvert. Safe, slow, and the new cache identity is then used only for writing.
`prospectus_batch.run_isolated` keeps passing `--force`, so isolated runs always convert fresh. Marked **(D4)** in Tasks 4, 6, 7.

**D5. Names visible to downstream consumers.** Payload gets a top-level `run_identity` object; every output set gets `<base>_publish.json` (publish manifest); diagnostics go to `<output dir>/failed/<base>/failure.json`; the batch manifest records gain `skip_check` and `failed_dir`. **Recommended:** exactly these. Alternatives (`source_identity`, `_manifest.json`) are equally good; change them before Task 5 if you prefer.

**D6. A conversion that succeeds but whose parse or audit then raises: is the new raw Docling JSON published to the cache?**
- (a) **Recommended:** no. Nothing is published on failure, so `<stem>_docling.json` still belongs to the earlier outputs (their provenance points at it). The new JSON is copied to `failed/<base>/` so a developer can re-run on it with `-i` as a review input. Cost: the next run reconverts.
- (b) Publish the cache anyway. Faster debugging, but when the PDF changed, the old outputs' `raw_docling_json` provenance would then point at a JSON of a different PDF.
Marked **(D6)** in Task 6.

---

## What the real code does today (8d26f18)

- `loader.py:286-293` `_docling_runtime_fingerprint()` returns profile, `docling`, `docling-core`, `docling-parse` versions and the raw `PALSU_DOCLING_CELL_MATCHING` string. It has **no PDF hash**. `loader.py:296-297` `_cache_meta_path` is `<stem>.meta.json` next to `<stem>_docling.json`. `load_document` (`loader.py:300-376`) compares the meta file to the fingerprint (`:328-332`), so a PDF replaced by different bytes under the same name reuses the old JSON. The raw JSON and meta are written non-atomically (`:369-370`), and meta last.
- `docling_env.py:180-208` `get_pipeline_options` hard-codes the conversion settings (`do_ocr=False`, `force_backend_text=True`, `do_table_structure=True`, TableFormer ACCURATE, cell matching from the env var), so the fingerprint and the real options can drift apart.
- `pipeline.py:206-213` `process_prospectus` **unlinks** the main JSON, essentials, `.pl`, `_rag.jsonl` and `_review.csv` before it loads or converts anything (`for stale in (...): stale.unlink(missing_ok=True)`). A conversion failure therefore destroys the previous good set. Writes at `:227-259` go directly to the final paths with `write_text`, which on Windows turns `\n` into `\r\n`.
- `batch.py:196-200` `--skip-existing` skips on `json_path.exists()` (plus essentials for PDFs). It would skip a failed audit and a changed PDF. `batch.py:167-173` pre-warm logic uses the same existence test. `batch.py:211` and `cli.py:124` pass `force_reconvert=True`.
- `cli.py:42-43` `--skip-existing` (batch only) and `--force`.
- `prospectus_batch.py:15-24` defines `PACKAGE_DIR` and `package_sha256`, importing the package (`from . import prospectus_extractor as extractor`). The package must not import `prospectus_batch`.

## Where the shared hash helper lives (no import cycle)

`package_sha256`, `PACKAGE_DIR` and `file_sha256` move into the new `prospectus_extractor/identity.py`, which imports only the standard library and `.common`. `prospectus_batch.py` does `from .prospectus_extractor.identity import PACKAGE_DIR, package_sha256` and keeps the public names, so its existing tests and the isolated manifest keep working. A test (Task 2) parses every package module and fails if any imports `prospectus_batch`.

## Design in one page

**Identities.**
- `conversion_settings(do_ocr=False, ocr_languages=())` returns a dict: profile, `do_ocr`, `ocr_languages` (sorted, empty unless OCR), `do_table_structure`, `table_mode`, `force_backend_text`, `cell_matching` (normalised to a bool, so `1` and `true` are equal), `backend`, `backend_fallback`, and the three Docling package versions. OCR settings are inside the dict, so a born-digital conversion can never match an OCR conversion. `get_pipeline_options` reads this same dict, so identity and real options cannot drift (Task 3).
- `conversion_identity(pdf_sha256, settings)` is the SHA-256 of canonical JSON of `{identity_version, pdf_sha256, settings}`.
- `run_identity(input_path, semantic_doc, ...)` returns `{identity_version, input_kind, input_sha256, pdf_sha256, conversion_identity, conversion_settings, package_sha256, schema_version, semantic_sha256, review_input_only, run_key}`. `run_key` hashes `input_kind, input_sha256, conversion_identity, package_sha256, schema_version, semantic_sha256`. A `*_docling.json` input has `input_kind: "docling-json"`, no conversion identity, and `review_input_only: true`.

**Cache meta** (`<stem>_docling.meta.json`): `{identity_version, pdf_sha256, conversion_settings, conversion_identity, raw_json_sha256}`. A cache is reusable only when the meta parses, has the current `identity_version`, its `conversion_identity` equals the expected one, and `raw_json_sha256` equals the hash of the JSON on disk (this catches a torn raw/meta pair and a hand-edited JSON). The old bare-fingerprint format fails the version check and is ignored.

**Publication.** Staging directory: `<output dir>/.<base>.staging-<8 hex>/`, a sibling of the target, so every `Path.replace` stays on one filesystem. Everything is written there first. After the audit, files are published one at a time with `replace_file` (a `Path.replace` with a short retry on `PermissionError`, because Windows antivirus and indexers briefly lock new files). Order: cache JSON, cache meta, essentials, `.pl`, `_rag.jsonl`, `_review.csv`, **main `_prospectus.json`**, then **`<base>_publish.json` last**.

Why a manifest last, not just "main JSON last": a file-by-file publish cannot be atomic, so a crash mid-way leaves a mix. "Main JSON last" alone does not make the mix detectable (an old main JSON next to new companions looks consistent). The publish manifest records the SHA-256 of every output of the run plus the `run_key` and `audit_status`. A consumer, and `--skip-existing`, trusts a set only if the manifest exists and every listed file still hashes to its recorded value. After a mid-way crash the old manifest no longer matches the new files, so the set is reported incomplete and reprocessed. Cost: one small extra file. `Path.replace` over an existing file is atomic on POSIX and works on Windows; replacing a directory does not, which is why nothing here replaces a directory.

Stale companions: after the new manifest is published, files listed in the previous manifest but not in the new one (for example `.pl` and `_rag.jsonl` after an audit error) are deleted. The raw cache files are never in the manifest, so they are never deleted.

**Failure.** On any exception after the input is validated, the staging files are copied to `<output dir>/failed/<base>/` next to `failure.json` (error type and message, traceback, input path, identity if computed), the staging directory is removed, and the exception propagates (CLI exit nonzero; batch records `status: "error"`). Earlier published files are not touched. A later successful publish clears `failed/<base>/`.

**Skip.** `skip_check` returns `(skip, reason)`. It skips only when: `--skip-existing` and not `--force`; a valid publish manifest exists; `audit_status` is `ok` or `warn` (an `error` is never skipped); the manifest `run_key` equals the key computed now; every manifest file still hashes correctly; and every companion requested by the current flags (essentials for PDFs, csv, pl, jsonl) is in the manifest.

## File structure

All under `backend/bintanong_tools/`.

| File | Change |
| --- | --- |
| `prospectus_extractor/identity.py` | **New.** Hashes, `conversion_settings`, `conversion_identity`, `run_identity`. Stdlib and `.common` only. |
| `prospectus_extractor/publish.py` | **New.** `OutputNames`, staging, `replace_file`, `publish_staged`, manifest read/verify, failure diagnostics. |
| `prospectus_extractor/docling_env.py` | `get_pipeline_options(device, settings=None)` reads `conversion_settings()` (lines 180-208). |
| `prospectus_extractor/loader.py` | Replace `_docling_runtime_fingerprint` (286-293) and the cache logic in `load_document` (300-376); add `cache_reuse_check`, atomic writes, `stage_dir`. |
| `prospectus_extractor/pipeline.py` | `process_prospectus` (174-263) stages and publishes; adds `run_identity` to the payload. |
| `prospectus_extractor/batch.py` | `skip_check`; replace pre-warm logic (167-173) and skip test (196-200); pass `force_reconvert`; record `skip_check`/`failed_dir`; ignore `failed/` when scanning. |
| `prospectus_extractor/cli.py` | `--force` and `--skip-existing` help text; `force_reconvert=args.force` (line 124). |
| `prospectus_extractor/common.py` | `SCHEMA_VERSION` and `MANIFEST_SCHEMA_VERSION` bumped (Tasks 6, 7). |
| `prospectus_batch.py` | Import `PACKAGE_DIR` and `package_sha256` from `identity`. |
| `tests/conftest.py` | **New.** Fake Docling and pipeline fixtures. |
| `tests/test_prospectus_identity.py`, `test_prospectus_cache.py`, `test_prospectus_publish.py`, `test_prospectus_publication.py`, `test_prospectus_batch_skip.py` | **New.** One per task. |
| `scripts/prospectus_course_compare.py` | **New, temporary** (Task 8). Never committed. |
| `docs/decisions/prospectus-cache-and-publication.md` | **New** (Task 10). |

**SCHEMA_VERSION change:** the payload gains a top-level `run_identity` object, so `SCHEMA_VERSION` is bumped. The plan assumes Phase C left it at `palsu-prospectus-v3.1` and sets `palsu-prospectus-v3.2`. If the value found in Task 1 differs, use the next minor after what you find; the literal appears only in Task 6 steps 1 and 3. `MANIFEST_SCHEMA_VERSION` (batch manifest records gain `skip_check` and `failed_dir`) is bumped the same way in Task 7.

## Commands used throughout

Run from the repo root in PowerShell (Git Bash is broken on this machine).

```
# Full suite
uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests

# Self-test (80/80)
uv run --project backend --extra tools --extra dev python -m backend.bintanong_tools.prospectus_extractor --self-test
```

Commit rules: stage by explicit path, never `.gitignore` or `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`. Every commit message ends with the line `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (pass it as a second `-m`).

---

### Task 1: Start check, branch, baseline

**Files:** none changed except the progress file.

- [ ] **Step 1: Branch and confirm what the earlier phases left**

```
git switch dev
git switch -c feature/prospectus-phase-d-safe-cache
git log --oneline -5
```

Confirm Phase B and C are merged (`git log --oneline dev` shows them). If `tests/test_prospectus_split_equivalence.py` still exists, Phase B has not merged: stop and tell the controller (Phase B deletes it in its first commit).

- [ ] **Step 2: Re-read the files this phase touches and update this plan's line references**

Read `loader.py`, `pipeline.py`, `batch.py`, `cli.py`, `docling_env.py`, `common.py`, `backend/bintanong_tools/prospectus_batch.py`. For each of these, confirm the lines quoted under "What the real code does today" still say what the plan says. Record the new numbers in the progress file.

Note from the Phase B review: the skip check must include the Phase B `_prospectus.md` when write_md is on (batch `--skip-existing` today checks only JSON + essentials, so a missing .md is never regenerated).

Adapt to Phase B and C before writing code:
- Phase B added a markup companion (`<base>_prospectus.md`, flag `--export-md`). Wherever this plan lists companions (`OutputNames` in Task 5, `_stage_outputs` in Task 6, `wanted` in `skip_check` in Task 7, the order list in the Task 6 ordering test), add it **before** the main JSON in the publish order, and add the CLI flag's value to `BatchConfig` only if Phase B already did.
- Phase C may have added or renamed companions or payload keys (for example the `audit` shape). The stub payload in `tests/conftest.py` (Task 4) must keep the keys that `process_prospectus` reads after Phase C: `payload["audit"]["status"]`, `payload["prolog"]["clauses"]`, `payload["rag"]["semantic_chunks"]`, `payload["rag"]["hierarchical_chunks"]`, `payload["courses"]`. Adjust the stub if a key moved.
- Read `SCHEMA_VERSION` and `MANIFEST_SCHEMA_VERSION` in `common.py` and note them.

- [ ] **Step 3: Baseline**

Run both commands from "Commands used throughout". Record the pass counts actually observed (expected: the suite green, self-test 80/80). If anything fails, stop and report; do not continue.

- [ ] **Step 4: Append a "Phase D" section to the progress file** with the branch, the observed counts, the schema versions found and the line-number updates. Commit:

```
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: start Phase D (safe cache and publication) progress log" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Identity module (hashes, settings, run identity), no cycle

**Files:**
- Create: `backend/bintanong_tools/prospectus_extractor/identity.py`
- Modify: `backend/bintanong_tools/prospectus_batch.py:13-24`
- Test: `tests/test_prospectus_identity.py`

- [ ] **Step 1: Write the failing tests**

```python
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
```

- [ ] **Step 2: Run and confirm the failure**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_identity.py`
Expected: collection error `ImportError: cannot import name 'identity'` for the whole file. That is the red step.

- [ ] **Step 3: Write `identity.py`**

```python
"""Identity of a conversion and of an output set: what each was made from."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Any, Mapping, Sequence
import hashlib
import json
import os

from .common import SCHEMA_VERSION

PACKAGE_DIR = Path(__file__).resolve().parent
IDENTITY_VERSION = 1
CONVERSION_PROFILE = "palsu-born-digital-v3"
_TRUE_VALUES = {"1", "true", "yes", "on"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def package_sha256(package: Path = PACKAGE_DIR) -> str:
    """One hash over every module, so any parser change changes the recorded hash."""
    digest = hashlib.sha256()
    for path in sorted(package.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()


def cell_matching_enabled() -> bool:
    raw = os.environ.get("PALSU_DOCLING_CELL_MATCHING", "true").strip().lower()
    return raw in _TRUE_VALUES


def installed_versions() -> dict[str, str]:
    found: dict[str, str] = {}
    for name in ("docling", "docling-core", "docling-parse"):
        try:
            found[name] = package_version(name)
        except PackageNotFoundError:
            found[name] = "not-installed"
    return found


def conversion_settings(do_ocr: bool = False, ocr_languages: Sequence[str] = ()) -> dict[str, Any]:
    """Every setting that changes what Docling produces. Single source for the
    pipeline options (docling_env.get_pipeline_options) and for cache identity."""
    return {
        "profile": CONVERSION_PROFILE,
        "do_ocr": bool(do_ocr),
        "ocr_languages": sorted(ocr_languages) if do_ocr else [],
        "do_table_structure": True,
        "table_mode": "accurate",
        "force_backend_text": True,
        "cell_matching": cell_matching_enabled(),
        "backend": "docling_parse",
        "backend_fallback": "pypdfium2",
        "versions": installed_versions(),
    }


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def conversion_identity(pdf_sha256: str, settings: Mapping[str, Any]) -> str:
    return _canonical_sha256(
        {"identity_version": IDENTITY_VERSION, "pdf_sha256": pdf_sha256, "settings": dict(settings)}
    )


def run_identity(
    input_path: Path,
    semantic_doc: Path | None,
    *,
    schema_version: str | None = None,
    package_hash: str | None = None,
    settings: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """What one output set is made from. `run_key` is what --skip-existing compares."""
    input_path = Path(input_path)
    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        kind = "pdf"
    elif suffix == ".json":
        kind = "docling-json"
    else:
        raise ValueError(f"Unsupported input type: {input_path.suffix}")
    input_hash = file_sha256(input_path)
    conversion_id = None
    used_settings = None
    if kind == "pdf":
        used_settings = dict(settings) if settings is not None else conversion_settings()
        conversion_id = conversion_identity(input_hash, used_settings)
    semantic_hash = (
        file_sha256(Path(semantic_doc)) if semantic_doc and Path(semantic_doc).is_file() else None
    )
    core = {
        "input_kind": kind,
        "input_sha256": input_hash,
        "conversion_identity": conversion_id,
        "package_sha256": package_hash or package_sha256(),
        "schema_version": schema_version or SCHEMA_VERSION,
        "semantic_sha256": semantic_hash,
    }
    return {
        "identity_version": IDENTITY_VERSION,
        **core,
        "pdf_sha256": input_hash if kind == "pdf" else None,
        "conversion_settings": used_settings,
        "review_input_only": kind == "docling-json",
        "run_key": _canonical_sha256(core),
    }
```

- [ ] **Step 4: Point `prospectus_batch.py` at it**

In `backend/bintanong_tools/prospectus_batch.py` replace lines 13-24 (the `from . import prospectus_extractor as extractor` line through the end of `package_sha256`) with:

```python
from . import prospectus_extractor as extractor
from .prospectus_extractor.identity import PACKAGE_DIR, package_sha256
```

`hashlib` stays imported (still used at the `pdf_sha256` record). Nothing else in the file changes; `run_isolated` already calls `package_sha256()` and uses `PACKAGE_DIR`.

- [ ] **Step 5: Run the new tests and the existing batch tests**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_identity.py tests/test_prospectus_batch.py`
Expected: all pass (the 5 existing batch tests plus 7 new).

- [ ] **Step 6: Commit** (D1, D2 are implemented here: no device in the identity; package hash only in `run_identity`)

```
git add backend/bintanong_tools/prospectus_extractor/identity.py backend/bintanong_tools/prospectus_batch.py tests/test_prospectus_identity.py
git commit -m "feat: add conversion and run identity for the prospectus extractor" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 7: Append the task result to the progress file** (red message seen, counts after, commit hash).

---

### Task 3: One source for conversion settings

**Files:**
- Modify: `backend/bintanong_tools/prospectus_extractor/docling_env.py:1-12, 180-208`
- Test: `tests/test_prospectus_identity.py` (append)

- [ ] **Step 1: Append the failing test**

```python
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
```

- [ ] **Step 2: Run and confirm it fails**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_identity.py::test_pipeline_options_follow_conversion_settings`
Expected: FAIL with `TypeError: get_pipeline_options() got an unexpected keyword argument 'settings'`.

- [ ] **Step 3: Implement**

In `docling_env.py` add below the existing imports (`import sys`):

```python
from .identity import conversion_settings
```

Replace `get_pipeline_options` (lines 180-208) with:

```python
def get_pipeline_options(device: str = "auto", settings: Any = None) -> Any:
    dl = load_docling()
    settings = settings if settings is not None else conversion_settings()
    options = dl["PdfPipelineOptions"]()
    env = check_cuda_environment()
    want = (device or "auto").strip().lower()

    if want == "cpu":
        chosen = dl["AcceleratorDevice"].CPU
        print("[*] Acceleration: CPU (explicitly selected).")
    elif env["cuda_available"]:
        chosen = dl["AcceleratorDevice"].CUDA
        print(f"[+] Acceleration: CUDA ({env['cuda_device_name']}).")
    else:
        chosen = dl["AcceleratorDevice"].CPU
        print("[*] Acceleration: CPU. " + env["status_message"])

    options.accelerator_options = dl["AcceleratorOptions"](device=chosen)
    options.do_ocr = settings["do_ocr"]
    options.force_backend_text = settings["force_backend_text"]
    options.do_table_structure = settings["do_table_structure"]
    options.table_structure_options.mode = (
        dl["TableFormerMode"].ACCURATE if settings["table_mode"] == "accurate"
        else dl["TableFormerMode"].FAST
    )
    options.table_structure_options.do_cell_matching = settings["cell_matching"]

    for attr in ("generate_page_images", "generate_picture_images"):
        if hasattr(options, attr):
            setattr(options, attr, False)
    return options
```

The values are identical to the old hard-coded ones (`do_ocr=False`, backend text on, tables on, ACCURATE, cell matching from the env var with `{"1","true","yes","on"}` true).

Note for the later OCR plan: `get_shared_converter` caches converters by `(device, backend)` (line 211-218). It must also key on the settings when `do_ocr=True` profiles arrive; this phase does not change that key.

- [ ] **Step 4: Run the new test, the self-test, and the full suite**

Run the new test: expected PASS. Then both commands from "Commands used throughout". Expected: green and 80/80.

- [ ] **Step 5: Commit and log**

```
git add backend/bintanong_tools/prospectus_extractor/docling_env.py tests/test_prospectus_identity.py
git commit -m "refactor: read Docling pipeline options from the identity settings" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
Append the result to the progress file.

---

### Task 4: Identity-checked raw Docling JSON cache

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_prospectus_cache.py`
- Modify: `backend/bintanong_tools/prospectus_extractor/loader.py:1-17 (imports), 286-376`

- [ ] **Step 1: Write the shared fakes** (`tests/conftest.py`). No real Docling is ever started; the converter and the parse/audit boundary are replaced.

```python
"""Shared fakes for the prospectus run tests: no real Docling, no real parse."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.bintanong_tools.prospectus_extractor import identity, loader, pipeline

RAW_BASE = {"texts": [{"text": "BS Test Program", "label": "text"}], "tables": []}


class FakeDoc:
    def __init__(self, raw):
        self.raw = raw

    @classmethod
    def model_validate(cls, raw):
        return cls(raw)

    def export_to_dict(self):
        return self.raw

    def export_to_markdown(self):
        return "BS Test Program"


class FakeConverter:
    """Stands in for a Docling converter; the raw JSON carries the PDF bytes so tests can see which bytes were converted."""

    def __init__(self, fail: bool = False):
        self.fail = fail
        self.calls: list[str] = []

    def convert(self, path):
        self.calls.append(str(path))
        if self.fail:
            raise RuntimeError("converter exploded")
        marker = Path(path).read_bytes().decode("latin-1")
        return SimpleNamespace(errors=[], document=FakeDoc({**RAW_BASE, "marker": marker}))


@pytest.fixture
def fake_docling(monkeypatch):
    def no_real_converter(*_args, **_kwargs):
        raise AssertionError("a real Docling converter was requested in a unit test")

    monkeypatch.setattr(loader, "ensure_docling_env", lambda: None)
    monkeypatch.setattr(loader, "load_docling", lambda: {"DoclingDocument": FakeDoc})
    monkeypatch.setattr(loader, "_docling_importable", lambda: True)
    monkeypatch.setattr(loader, "get_shared_converter", no_real_converter)
    monkeypatch.setattr(
        identity, "installed_versions",
        lambda: {"docling": "t1", "docling-core": "t1", "docling-parse": "t1"},
    )
    monkeypatch.delenv("PALSU_DOCLING_CELL_MATCHING", raising=False)


@pytest.fixture
def converter():
    return FakeConverter()


@pytest.fixture
def failing_converter():
    return FakeConverter(fail=True)


@pytest.fixture
def pipeline_state(monkeypatch):
    """Replaces parse and audit. `status`, `fail` and `builds` steer and observe it."""
    state = SimpleNamespace(status="ok", fail=None, builds=0)

    def build_payload(document, input_path, semantic_doc_path=None, raw_json_path=None,
                      repair_provider=None):
        state.builds += 1
        if state.fail is not None:
            raise state.fail
        return {
            "schema_version": "stub",
            "nonce": state.builds,
            "program": "P",
            "degree": "D",
            "college": "C",
            "campus": "K",
            "source_file": Path(input_path).name,
            "source_path": str(Path(input_path).resolve()),
            "metadata": {},
            "courses": [],
            "prolog": {"clauses": [f"fact({state.builds})."]},
            "rag": {"semantic_chunks": [{"id": state.builds}], "hierarchical_chunks": []},
            "audit": {
                "status": state.status, "promotion_status": "x", "errors": [], "warnings": [],
                "total_courses": 0, "computed_total_units": 0, "years_detected": [],
            },
        }

    monkeypatch.setattr(pipeline, "build_payload", build_payload)
    monkeypatch.setattr(
        pipeline, "build_essentials",
        lambda payload: {"nonce": payload["nonce"], "status": payload["audit"]["status"]},
    )
    return state


@pytest.fixture
def pdf_factory():
    def make(folder: Path, name: str = "a.pdf", body: bytes = b"%PDF-one") -> Path:
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / name
        path.write_bytes(body)
        return path

    return make


@pytest.fixture
def process():
    def run(pdf, out_dir, active_converter, **kwargs):
        kwargs.setdefault("quiet", True)
        return pipeline.process_prospectus(
            pdf, output_path=Path(out_dir) / "a_prospectus.json",
            export_pl=True, export_jsonl=True, export_csv=True,
            converter=active_converter, semantic_doc_path=None, **kwargs,
        )

    return run


@pytest.fixture
def snapshot():
    def take(folder: Path, exclude=("batch_manifest.json",)) -> dict[str, bytes]:
        return {
            path.name: path.read_bytes()
            for path in sorted(Path(folder).iterdir())
            if path.is_file() and path.name not in exclude
        }

    return take
```

- [ ] **Step 2: Write the failing cache tests** (`tests/test_prospectus_cache.py`)

```python
"""The raw Docling JSON cache is reused only for the same PDF bytes and the same conversion settings."""

from __future__ import annotations

import json

import pytest

from backend.bintanong_tools.prospectus_extractor import identity, loader

pytestmark = pytest.mark.usefixtures("fake_docling", "pipeline_state")


def test_unchanged_pdf_reuses_the_cache(tmp_path, pdf_factory, converter, process):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    process(pdf, out, converter, force_reconvert=False)
    assert len(converter.calls) == 1


def test_same_path_with_changed_bytes_reconverts(tmp_path, pdf_factory, converter, process):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    pdf.write_bytes(b"%PDF-two")
    process(pdf, out, converter, force_reconvert=False)
    assert len(converter.calls) == 2
    raw = json.loads((out / "a_docling.json").read_text(encoding="utf-8"))
    assert raw["marker"] == "%PDF-two"


@pytest.mark.parametrize(
    "damage", ["wrong_identity", "old_format", "raw_tampered", "meta_missing", "meta_garbage"]
)
def test_cache_with_mismatching_identity_is_ignored(
    damage, tmp_path, pdf_factory, converter, process
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    raw_path = out / "a_docling.json"
    meta_path = out / "a_docling.meta.json"
    if damage == "wrong_identity":
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["conversion_identity"] = "0" * 64
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
    elif damage == "old_format":  # what the code wrote before Phase D
        meta_path.write_text(
            json.dumps({"profile": "palsu-born-digital-v3", "docling": "t1", "cell_matching": "true"}),
            encoding="utf-8",
        )
    elif damage == "raw_tampered":
        raw_path.write_text(raw_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
    elif damage == "meta_missing":
        meta_path.unlink()
    else:
        meta_path.write_text("{not json", encoding="utf-8")
    process(pdf, out, converter, force_reconvert=False)
    assert len(converter.calls) == 2


def test_changed_cell_matching_setting_invalidates_the_cache(
    tmp_path, monkeypatch, pdf_factory, converter, process
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    monkeypatch.setenv("PALSU_DOCLING_CELL_MATCHING", "false")
    process(pdf, out, converter, force_reconvert=False)
    assert len(converter.calls) == 2


def test_born_digital_cache_is_never_reused_for_an_ocr_run(
    tmp_path, monkeypatch, pdf_factory, converter, process
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    monkeypatch.setattr(loader, "conversion_settings",
                        lambda: identity.conversion_settings(do_ocr=True, ocr_languages=["en", "fil"]))
    process(pdf, out, converter, force_reconvert=False)
    assert len(converter.calls) == 2
    meta = json.loads((out / "a_docling.meta.json").read_text(encoding="utf-8"))
    assert meta["conversion_settings"]["do_ocr"] is True


def test_cache_record_names_the_pdf_and_the_json_it_guards(tmp_path, pdf_factory, converter, process):
    import hashlib

    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter, force_reconvert=False)
    meta = json.loads((out / "a_docling.meta.json").read_text(encoding="utf-8"))
    assert meta["identity_version"] == identity.IDENTITY_VERSION
    assert meta["pdf_sha256"] == hashlib.sha256(b"%PDF-one").hexdigest()
    assert meta["raw_json_sha256"] == identity.file_sha256(out / "a_docling.json")
    assert meta["conversion_identity"] == identity.conversion_identity(
        meta["pdf_sha256"], meta["conversion_settings"])
```

- [ ] **Step 3: Run and confirm they fail for the right reasons**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_cache.py`
Expected: `test_unchanged_pdf_reuses_the_cache` passes or fails (old code compares a fingerprint, which matches, so it passes). The red ones: `test_same_path_with_changed_bytes_reconverts` (calls stay 1: the old cache is wrongly reused), `wrong_identity`/`raw_tampered` cases (old code ignores those fields, calls stay 1), `test_changed_cell_matching_setting_invalidates_the_cache` passes under the old fingerprint, the OCR test fails with `AttributeError: ... loader has no attribute 'conversion_settings'`, and the record test fails with `KeyError: 'identity_version'`. At least five failures; if everything passes, the fakes are not reaching `load_document`: stop and debug.

- [ ] **Step 4: Implement in `loader.py`**

Imports: remove `from importlib.metadata import version as package_version` and `import os` (no longer used), and add after the other relative imports:

```python
from .identity import IDENTITY_VERSION, conversion_identity, conversion_settings, file_sha256
```

Replace lines 286-376 (`_docling_runtime_fingerprint`, `_cache_meta_path`, `load_document`) with the following. `_cache_meta_path` is unchanged.

```python
def _cache_meta_path(raw_json_path: Path) -> Path:
    return raw_json_path.with_name(raw_json_path.stem + ".meta.json")


def _write_bytes_atomic(path: Path, data: bytes) -> None:
    """Write beside the target, then replace: a reader never sees half a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_bytes(data)
    temp.replace(path)


def cache_reuse_check(
    raw_json_path: Path, meta_path: Path, expected_identity: str
) -> tuple[bool, str]:
    """May this cached raw Docling JSON stand in for a fresh conversion? Returns (yes, reason)."""
    if not raw_json_path.exists():
        return False, "no cached Docling JSON"
    if not meta_path.exists():
        return False, "cached Docling JSON has no identity record"
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False, "identity record is unreadable"
    if (
        not isinstance(meta, dict)
        or meta.get("identity_version") != IDENTITY_VERSION
        or "conversion_identity" not in meta
    ):
        return False, "identity record is from an older version"
    if meta["conversion_identity"] != expected_identity:
        return False, "PDF bytes or conversion settings changed"
    if meta.get("raw_json_sha256") != file_sha256(raw_json_path):
        return False, "cached JSON does not match its identity record"
    return True, "identity matches"


def load_document(
    input_path: Path,
    device: str = "auto",
    force_reconvert: bool = True,
    converter: Any = None,
    raw_json_path: Path | None = None,
    stage_dir: Path | None = None,
) -> tuple[LoadedDocument, Path | None]:
    """Load a PDF (convert or reuse an identity-matched cache) or a raw Docling JSON.

    A Docling JSON given as the input is a review input: nothing verifies which PDF
    or settings produced it. When `stage_dir` is given, a fresh conversion is written
    there and the returned path is where it will be published; the caller publishes it.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    suffix = input_path.suffix.lower()
    if suffix == ".json":
        data = json.loads(input_path.read_text(encoding="utf-8"))
        print(f"[*] Loading Docling JSON: {input_path.name} (review input; source PDF not verified)")
        return load_from_raw_json(data), input_path

    if suffix != ".pdf":
        raise ValueError(f"Unsupported input type: {input_path.suffix}")

    ensure_docling_env()
    load_docling()

    raw_json_path = Path(raw_json_path).resolve() if raw_json_path else input_path.parent / f"{input_path.stem}_docling.json"
    meta_path = _cache_meta_path(raw_json_path)
    settings = conversion_settings()
    pdf_hash = file_sha256(input_path)
    expected = conversion_identity(pdf_hash, settings)

    if not force_reconvert:
        reusable, reason = cache_reuse_check(raw_json_path, meta_path, expected)
        if reusable:
            print(f"[*] Reusing raw Docling JSON with matching identity: {raw_json_path.name}")
            data = json.loads(raw_json_path.read_text(encoding="utf-8"))
            return load_from_raw_json(data), raw_json_path
        if raw_json_path.exists():
            print(f"[*] Ignoring cached Docling JSON ({reason}); reconverting.")

    print(f"[*] Converting with Docling ({device.upper()}): {input_path.name}")
    active = converter or get_shared_converter(device=device, backend="docling_parse")
    result = active.convert(str(input_path))

    if _conversion_has_bad_alloc(result):
        print(
            "[!] Native Docling PDF backend hit std::bad_alloc; retrying through "
            "Docling's PyPdfium backend (NOT PyMuPDF)."
        )
        result = get_shared_converter(device=device, backend="pypdfium2").convert(str(input_path))

    if _conversion_has_bad_alloc(result):
        raise MemoryError(
            "Docling still reported std::bad_alloc after backend retry. Confirm "
            "docling-parse>=7.12 (Bintanong pins >=7.20) and a Windows pagefile."
        )

    remaining_errors = _conversion_errors(result)
    if remaining_errors:
        raise RuntimeError(
            "Docling returned conversion errors; refusing to build a partial institutional artifact: "
            + " | ".join(remaining_errors[:6])
        )

    doc = result.document
    raw = doc.export_to_dict() if hasattr(doc, "export_to_dict") else doc.model_dump(mode="json")
    raw_bytes = json.dumps(raw, indent=2, ensure_ascii=False).encode("utf-8")
    meta = {
        "identity_version": IDENTITY_VERSION,
        "pdf_sha256": pdf_hash,
        "conversion_settings": settings,
        "conversion_identity": expected,
        "raw_json_sha256": __import__("hashlib").sha256(raw_bytes).hexdigest(),
    }
    write_dir = Path(stage_dir) if stage_dir else raw_json_path.parent
    # raw JSON first, meta second: a crash between them leaves a pair that fails the sha check.
    _write_bytes_atomic(write_dir / raw_json_path.name, raw_bytes)
    _write_bytes_atomic(write_dir / meta_path.name, json.dumps(meta, indent=2).encode("utf-8"))
    print(f"[+] Raw Docling JSON -> {write_dir / raw_json_path.name}")

    rehydrated = load_docling()["DoclingDocument"].model_validate(raw)
    return _load_from_rehydrated_docling_document(
        rehydrated, "docling-document", raw
    ), raw_json_path
```

Replace the awkward `__import__("hashlib")` with a plain `import hashlib` at the top of `loader.py` and `hashlib.sha256(raw_bytes).hexdigest()` in the dict. (Written inline above only to keep the replacement block self-contained; do not commit the `__import__` form.)

- [ ] **Step 5: Run the cache tests, the self-test and the full suite**

Expected: `tests/test_prospectus_cache.py` 10 passed (1 + 1 + 5 + 1 + 1 + 1); full suite green; self-test 80/80. **(D4)** `process_prospectus` still defaults to `force_reconvert=True` until Task 6; the tests pass `force_reconvert=False` explicitly.

- [ ] **Step 6: Commit and log**

```
git add backend/bintanong_tools/prospectus_extractor/loader.py tests/conftest.py tests/test_prospectus_cache.py
git commit -m "fix: reuse the raw Docling JSON only when PDF bytes and settings match" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
Append to the progress file: the red/green evidence, and that **(D1)** the cache key excludes the parser hash.

---

### Task 5: The publish module

**Files:**
- Create: `backend/bintanong_tools/prospectus_extractor/publish.py`
- Test: `tests/test_prospectus_publish.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Staging, file-by-file publication, publish manifest, failure diagnostics."""

from __future__ import annotations

import json

import pytest

from backend.bintanong_tools.prospectus_extractor import publish

IDENTITY = {"run_key": "k" * 64}


def stage_files(stage, contents: dict[str, str]):
    stage.mkdir(parents=True, exist_ok=True)
    for name, text in contents.items():
        publish.write_text_lf(stage / name, text)


def test_output_names_match_the_historical_companion_names(tmp_path):
    names = publish.output_names(tmp_path / "out" / "bscs_prospectus.json")
    assert names.base == "bscs"
    assert names.essentials.name == "bscs_essentials.json"
    assert names.prolog.name == "bscs_prospectus.pl"
    assert names.rag.name == "bscs_rag.jsonl"
    assert names.csv.name == "bscs_review.csv"
    assert names.manifest.name == "bscs_publish.json"
    assert names.failed_dir == tmp_path / "out" / "failed" / "bscs"


def test_publish_replaces_existing_files_and_writes_the_manifest_last(tmp_path, monkeypatch):
    names = publish.output_names(tmp_path / "out" / "a_prospectus.json")
    names.final.parent.mkdir(parents=True)
    names.final.write_text("old main", encoding="utf-8")
    names.csv.write_text("old csv", encoding="utf-8")
    stage = tmp_path / "out" / ".a.staging-x"
    stage_files(stage, {"a_review.csv": "new csv", "a_prospectus.json": "new main"})

    order = []
    real = publish.replace_file
    monkeypatch.setattr(publish, "replace_file",
                        lambda source, target, *a, **k: (order.append(target.name), real(source, target, *a, **k)))
    publish.publish_staged(stage, names, ["a_review.csv", "a_prospectus.json"], [], IDENTITY, "ok")

    assert order == ["a_review.csv", "a_prospectus.json", "a_publish.json"]
    assert names.final.read_text(encoding="utf-8") == "new main"
    manifest = publish.read_manifest(names.manifest)
    assert manifest["run_key"] == IDENTITY["run_key"]
    assert manifest["audit_status"] == "ok"
    assert sorted(manifest["files"]) == ["a_prospectus.json", "a_review.csv"]
    assert publish.verify_published(names.final.parent, manifest) == (True, "all files match")


def test_main_json_must_be_the_last_output(tmp_path):
    names = publish.output_names(tmp_path / "out" / "a_prospectus.json")
    stage = tmp_path / "out" / ".a.staging-x"
    stage_files(stage, {"a_review.csv": "c", "a_prospectus.json": "m"})
    with pytest.raises(ValueError, match="main JSON"):
        publish.publish_staged(stage, names, ["a_prospectus.json", "a_review.csv"], [], IDENTITY, "ok")


def test_stale_companions_are_removed_but_cache_files_are_not(tmp_path):
    out = tmp_path / "out"
    names = publish.output_names(out / "a_prospectus.json")
    stage = out / ".a.staging-1"
    stage_files(stage, {"a_prospectus.pl": "pl", "a_prospectus.json": "m1"})
    publish.publish_staged(stage, names, ["a_prospectus.pl", "a_prospectus.json"], [], IDENTITY, "ok")
    (out / "a_docling.json").write_text("cache", encoding="utf-8")  # cache is not a manifest output

    stage2 = out / ".a.staging-2"
    stage_files(stage2, {"a_prospectus.json": "m2"})
    publish.publish_staged(stage2, names, ["a_prospectus.json"], [], IDENTITY, "error")

    assert not (out / "a_prospectus.pl").exists()
    assert (out / "a_docling.json").read_text(encoding="utf-8") == "cache"
    assert publish.read_manifest(names.manifest)["audit_status"] == "error"


def test_manifest_cannot_make_publish_delete_outside_the_output_folder(tmp_path):
    out = tmp_path / "out"
    names = publish.output_names(out / "a_prospectus.json")
    out.mkdir()
    victim = tmp_path / "victim.txt"
    victim.write_text("keep", encoding="utf-8")
    names.manifest.write_text(json.dumps({
        "schema": publish.PUBLISH_SCHEMA, "run_key": "x", "audit_status": "ok",
        "files": {"../victim.txt": "0" * 64},
    }), encoding="utf-8")
    stage = out / ".a.staging-1"
    stage_files(stage, {"a_prospectus.json": "m"})
    publish.publish_staged(stage, names, ["a_prospectus.json"], [], IDENTITY, "ok")
    assert victim.read_text(encoding="utf-8") == "keep"


def test_verify_detects_a_changed_or_missing_file(tmp_path):
    out = tmp_path / "out"
    names = publish.output_names(out / "a_prospectus.json")
    stage = out / ".a.staging-1"
    stage_files(stage, {"a_review.csv": "c", "a_prospectus.json": "m"})
    publish.publish_staged(stage, names, ["a_review.csv", "a_prospectus.json"], [], IDENTITY, "ok")
    manifest = publish.read_manifest(names.manifest)

    names.final.write_text("edited", encoding="utf-8")
    ok, why = publish.verify_published(out, manifest)
    assert (ok, why) == (False, "a_prospectus.json changed since it was published")

    names.csv.unlink()
    ok, why = publish.verify_published(out, manifest)
    assert (ok, why) == (False, "a_review.csv is missing")


def test_read_manifest_rejects_garbage(tmp_path):
    path = tmp_path / "a_publish.json"
    assert publish.read_manifest(path) is None
    path.write_text("{nope", encoding="utf-8")
    assert publish.read_manifest(path) is None
    path.write_text(json.dumps({"schema": "other"}), encoding="utf-8")
    assert publish.read_manifest(path) is None


def test_write_failure_keeps_staged_files_and_clears_the_previous_diagnostics(tmp_path):
    out = tmp_path / "out"
    names = publish.output_names(out / "a_prospectus.json")
    names.failed_dir.mkdir(parents=True)
    (names.failed_dir / "old_docling.json").write_text("old", encoding="utf-8")
    stage = out / ".a.staging-1"
    stage_files(stage, {"a_docling.json": "converted"})

    try:
        raise ValueError("parser blew up")
    except ValueError as error:
        directory = publish.write_failure(names, error, tmp_path / "in" / "a.pdf", {"run_key": "k"}, stage)

    assert directory == names.failed_dir
    assert not (directory / "old_docling.json").exists()
    assert (directory / "a_docling.json").read_text(encoding="utf-8") == "converted"
    record = json.loads((directory / "failure.json").read_text(encoding="utf-8"))
    assert record["error_type"] == "ValueError"
    assert record["error_message"] == "parser blew up"
    assert "Traceback" in record["traceback"]
    assert record["run_identity"] == {"run_key": "k"}

    publish.clear_failure(names)
    assert not names.failed_dir.exists()


def test_stale_staging_directories_are_removed_for_the_same_base_only(tmp_path):
    out = tmp_path / "out"
    (out / ".a.staging-dead").mkdir(parents=True)
    (out / ".b.staging-live").mkdir()
    stage = publish.new_staging_dir(out, "a")
    assert not (out / ".a.staging-dead").exists()
    assert (out / ".b.staging-live").exists()
    assert stage.parent == out and stage.name.startswith(".a.staging-") and stage.is_dir()
```

- [ ] **Step 2: Run and confirm the failure**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_publish.py`
Expected: `ImportError: cannot import name 'publish'`.

- [ ] **Step 3: Write `publish.py`**

```python
"""Staged output publication: write beside the target, publish file by file, manifest last."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence
import json
import shutil
import time
import traceback
import uuid

from .identity import file_sha256

PUBLISH_SCHEMA = "palsu-prospectus-publish-v1"
FAILED_DIR_NAME = "failed"


@dataclass(frozen=True)
class OutputNames:
    base: str
    final: Path
    essentials: Path
    prolog: Path
    rag: Path
    csv: Path
    manifest: Path

    @property
    def failed_dir(self) -> Path:
        return self.final.parent / FAILED_DIR_NAME / self.base


def output_names(final_path: Path) -> OutputNames:
    """Companion file names, derived exactly as process_prospectus always derived them."""
    final = Path(final_path)
    base = final.stem.replace("_prospectus", "")
    return OutputNames(
        base=base,
        final=final,
        essentials=final.with_name(f"{base}_essentials.json"),
        prolog=final.with_name(f"{base}_prospectus.pl"),
        rag=final.with_name(f"{base}_rag.jsonl"),
        csv=final.with_name(f"{base}_review.csv"),
        manifest=final.with_name(f"{base}_publish.json"),
    )


def write_text_lf(path: Path, text: str) -> None:
    """UTF-8 with \\n on every platform, so the same run hashes the same everywhere."""
    Path(path).write_bytes(text.encode("utf-8"))


def remove_stale_staging(parent: Path, base: str) -> None:
    """Delete staging directories a killed run left behind. One writer per output stem."""
    prefix = f".{base}.staging-"
    if not Path(parent).is_dir():
        return
    for entry in Path(parent).iterdir():
        if entry.is_dir() and entry.name.startswith(prefix):
            shutil.rmtree(entry, ignore_errors=True)


def new_staging_dir(parent: Path, base: str) -> Path:
    """A fresh directory beside the target, so every replace stays on one filesystem."""
    parent = Path(parent)
    remove_stale_staging(parent, base)
    stage = parent / f".{base}.staging-{uuid.uuid4().hex[:8]}"
    stage.mkdir(parents=True)
    return stage


def replace_file(source: Path, target: Path, attempts: int = 5, delay: float = 0.2) -> None:
    """Path.replace with a short retry: Windows scanners briefly lock freshly written files."""
    for attempt in range(attempts):
        try:
            Path(source).replace(target)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)


def read_manifest(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if (
        not isinstance(data, dict)
        or data.get("schema") != PUBLISH_SCHEMA
        or not isinstance(data.get("files"), dict)
        or not isinstance(data.get("run_key"), str)
    ):
        return None
    return data


def verify_published(directory: Path, manifest: Mapping[str, Any]) -> tuple[bool, str]:
    """Does every file the manifest lists still hash to the value recorded when it was published?"""
    for name, digest in manifest["files"].items():
        target = Path(directory) / name
        if not target.is_file():
            return False, f"{name} is missing"
        if file_sha256(target) != digest:
            return False, f"{name} changed since it was published"
    return True, "all files match"


def publish_staged(
    stage: Path,
    names: OutputNames,
    outputs: Sequence[str],
    cache_files: Sequence[str],
    run_identity: Mapping[str, Any],
    audit_status: str,
) -> Path:
    """Move a finished stage into place, one file at a time.

    `outputs` are file names inside `stage` in publish order; the main JSON must be last.
    `cache_files` (raw Docling JSON and its meta) are published first and are not part of
    the manifest: they have their own identity record. The manifest is published very last.
    A crash part-way leaves an old manifest whose hashes no longer match: verify_published
    reports the set incomplete, so nothing trusts it.
    """
    stage = Path(stage)
    if not outputs or outputs[-1] != names.final.name:
        raise ValueError("the main JSON must be the last staged output")
    target_dir = names.final.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    previous = read_manifest(names.manifest)
    previous_files = set(previous["files"]) if previous else set()

    manifest = {
        "schema": PUBLISH_SCHEMA,
        "run_key": run_identity["run_key"],
        "audit_status": audit_status,
        "published_at": datetime.now().isoformat(timespec="seconds"),
        "run_identity": dict(run_identity),
        "files": {name: file_sha256(stage / name) for name in outputs},
    }
    write_text_lf(stage / names.manifest.name, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    for name in [*cache_files, *outputs, names.manifest.name]:
        replace_file(stage / name, target_dir / name)

    for stale in previous_files - set(outputs):
        if Path(stale).name != stale:  # a tampered manifest must not reach outside this folder
            continue
        try:
            (target_dir / stale).unlink(missing_ok=True)
        except OSError:
            pass  # no longer listed in the manifest, so it cannot pass for current output
    return names.manifest


def write_failure(
    names: OutputNames,
    error: BaseException,
    input_path: Path,
    run_identity: Mapping[str, Any] | None,
    stage: Path | None,
) -> Path | None:
    """Keep what a failed run produced under failed/<base>/, never over published output."""
    directory = names.failed_dir
    try:
        directory.mkdir(parents=True, exist_ok=True)
        for old in directory.iterdir():
            if old.is_file():
                old.unlink()
        if stage is not None and Path(stage).is_dir():
            for staged in Path(stage).iterdir():
                if staged.is_file():
                    shutil.copy2(staged, directory / staged.name)
        record = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": "".join(traceback.format_exception(error)),
            "input_path": str(input_path),
            "run_identity": dict(run_identity) if run_identity else None,
            "failed_at": datetime.now().isoformat(timespec="seconds"),
        }
        write_text_lf(directory / "failure.json", json.dumps(record, indent=2, ensure_ascii=False) + "\n")
        return directory
    except OSError as exc:
        print(f"[!] Could not write failure diagnostics to {directory}: {exc}")
        return None


def clear_failure(names: OutputNames) -> None:
    """A later successful publish makes older diagnostics misleading."""
    shutil.rmtree(names.failed_dir, ignore_errors=True)
    try:
        names.failed_dir.parent.rmdir()  # only succeeds when failed/ is now empty
    except OSError:
        pass
```

- [ ] **Step 4: Run the new tests**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_publish.py`
Expected: 9 passed.

- [ ] **Step 5: Commit and log**

```
git add backend/bintanong_tools/prospectus_extractor/publish.py tests/test_prospectus_publish.py
git commit -m "feat: add staged publication with a hash manifest and failure diagnostics" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
Append to the progress file; write the justification for manifest-last into the entry (one sentence).

---

### Task 6: `process_prospectus` stages and publishes

**Files:**
- Modify: `backend/bintanong_tools/prospectus_extractor/pipeline.py:1-23, 174-263`
- Modify: `backend/bintanong_tools/prospectus_extractor/common.py` (`SCHEMA_VERSION`)
- Test: `tests/test_prospectus_publication.py`

- [ ] **Step 1: Write the failing tests**

```python
"""process_prospectus never touches earlier outputs until conversion and audit have finished."""

from __future__ import annotations

import hashlib
import json

import pytest

from backend.bintanong_tools.prospectus_extractor import common, publish

pytestmark = pytest.mark.usefixtures("fake_docling")

EXPECTED_SCHEMA = "palsu-prospectus-v3.2"  # Phase C's value plus one minor; see "SCHEMA_VERSION change"


def leftovers(folder):
    return [p.name for p in folder.iterdir() if p.name.startswith(".")]


def test_conversion_exception_after_a_good_run_leaves_earlier_files_byte_identical(
    tmp_path, pdf_factory, converter, failing_converter, pipeline_state, process, snapshot
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    before = snapshot(out)
    assert {"a_prospectus.json", "a_essentials.json", "a_prospectus.pl", "a_rag.jsonl",
            "a_review.csv", "a_docling.json", "a_docling.meta.json", "a_publish.json"} <= set(before)

    pdf.write_bytes(b"%PDF-two")
    with pytest.raises(RuntimeError, match="converter exploded"):
        process(pdf, out, failing_converter)

    assert snapshot(out) == before
    record = json.loads((out / "failed" / "a" / "failure.json").read_text(encoding="utf-8"))
    assert record["error_type"] == "RuntimeError"
    assert leftovers(out) == []


def test_failure_after_conversion_keeps_the_new_json_only_in_failed(
    tmp_path, pdf_factory, converter, pipeline_state, process, snapshot
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)  # D6: the good run's cache stays with the good run's outputs
    before = snapshot(out)

    pdf.write_bytes(b"%PDF-two")
    pipeline_state.fail = ValueError("parser blew up")
    with pytest.raises(ValueError, match="parser blew up"):
        process(pdf, out, converter)

    assert snapshot(out) == before
    kept = json.loads((out / "failed" / "a" / "a_docling.json").read_text(encoding="utf-8"))
    assert kept["marker"] == "%PDF-two"
    assert leftovers(out) == []


def test_a_good_run_clears_older_diagnostics(
    tmp_path, pdf_factory, converter, pipeline_state, process
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    pipeline_state.fail = ValueError("first attempt fails")
    with pytest.raises(ValueError):
        process(pdf, out, converter)
    assert (out / "failed" / "a" / "failure.json").is_file()
    pipeline_state.fail = None
    process(pdf, out, converter)
    assert not (out / "failed").exists()


def test_audit_error_run_is_published_and_removes_stale_companions(
    tmp_path, pdf_factory, converter, pipeline_state, process
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    assert (out / "a_prospectus.pl").is_file() and (out / "a_rag.jsonl").is_file()

    pdf.write_bytes(b"%PDF-two")
    pipeline_state.status = "error"
    payload = process(pdf, out, converter)

    assert payload["audit"]["status"] == "error"
    assert json.loads((out / "a_prospectus.json").read_text(encoding="utf-8"))["audit"]["status"] == "error"
    assert not (out / "a_prospectus.pl").exists()
    assert not (out / "a_rag.jsonl").exists()
    assert publish.read_manifest(out / "a_publish.json")["audit_status"] == "error"


def test_publication_order_puts_the_main_json_before_the_manifest(
    tmp_path, monkeypatch, pdf_factory, converter, pipeline_state, process
):
    order = []
    real = publish.replace_file
    monkeypatch.setattr(publish, "replace_file",
                        lambda source, target, *a, **k: (order.append(target.name), real(source, target, *a, **k)))
    pdf = pdf_factory(tmp_path / "in")
    process(pdf, tmp_path / "out", converter)
    assert order == ["a_docling.json", "a_docling.meta.json", "a_essentials.json", "a_prospectus.pl",
                     "a_rag.jsonl", "a_review.csv", "a_prospectus.json", "a_publish.json"]


def test_a_crash_between_replaces_is_detected_by_the_manifest(
    tmp_path, monkeypatch, pdf_factory, converter, pipeline_state, process, snapshot
):
    pdf = pdf_factory(tmp_path / "in")
    out = tmp_path / "out"
    process(pdf, out, converter)
    old_manifest = (out / "a_publish.json").read_bytes()

    real = publish.replace_file

    def dies_at_the_main_json(source, target, *a, **k):
        if target.name == "a_prospectus.json":
            raise OSError("disk pulled")
        real(source, target, *a, **k)

    monkeypatch.setattr(publish, "replace_file", dies_at_the_main_json)
    pdf.write_bytes(b"%PDF-two")
    with pytest.raises(OSError, match="disk pulled"):
        process(pdf, out, converter)

    assert (out / "a_publish.json").read_bytes() == old_manifest  # manifest is written last
    manifest = publish.read_manifest(out / "a_publish.json")
    ok, why = publish.verify_published(out, manifest)
    assert ok is False and "changed since it was published" in why
    assert leftovers(out) == []


def test_payload_records_how_it_was_made(
    tmp_path, pdf_factory, converter, pipeline_state, process
):
    pdf = pdf_factory(tmp_path / "in", body=b"%PDF-one")
    out = tmp_path / "out"
    first = process(pdf, out, converter, force_reconvert=False)
    identity_block = first["run_identity"]
    assert identity_block["input_kind"] == "pdf"
    assert identity_block["pdf_sha256"] == hashlib.sha256(b"%PDF-one").hexdigest()
    assert identity_block["cache"] == "converted"
    assert identity_block["review_input_only"] is False
    assert json.loads((out / "a_prospectus.json").read_text(encoding="utf-8"))["run_identity"] == identity_block
    assert publish.read_manifest(out / "a_publish.json")["run_key"] == identity_block["run_key"]

    second = process(pdf, out, converter, force_reconvert=False)
    assert second["run_identity"]["cache"] == "reused"
    assert second["run_identity"]["run_key"] == identity_block["run_key"]
    assert len(converter.calls) == 1


def test_docling_json_input_is_marked_as_a_review_input(
    tmp_path, pipeline_state, process, snapshot
):
    raw = tmp_path / "in" / "a_docling.json"
    raw.parent.mkdir()
    raw.write_text(json.dumps({"texts": [{"text": "BS", "label": "text"}], "tables": []}), encoding="utf-8")
    out = tmp_path / "out"
    payload = process(raw, out, None)

    block = payload["run_identity"]
    assert block["input_kind"] == "docling-json"
    assert block["review_input_only"] is True
    assert block["cache"] == "not-applicable"
    assert "review input only" in block["review_note"]
    assert "a_essentials.json" not in snapshot(out)  # essentials still require a source PDF


def test_schema_version_names_the_new_payload_shape():
    assert common.SCHEMA_VERSION == EXPECTED_SCHEMA


def test_output_inside_the_input_folder_is_still_refused(tmp_path, pdf_factory, converter, pipeline_state):
    from backend.bintanong_tools.prospectus_extractor import pipeline

    pdf = pdf_factory(tmp_path / "in")
    with pytest.raises(ValueError, match="distinct from the source"):
        pipeline.process_prospectus(pdf, output_path=pdf, converter=converter, quiet=True)
```

- [ ] **Step 2: Run and confirm failures**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_publication.py`
Expected: most fail. `test_conversion_exception...` fails on `a_publish.json` not in the snapshot and later on file bytes (the old code unlinked the outputs first); `test_publication_order...` fails with `AttributeError`/missing publish calls; the payload test fails on `KeyError: 'run_identity'`; the schema test fails (`palsu-prospectus-v3.1` or older); `test_output_inside_the_input_folder_is_still_refused` already passes and is a guard. If the conversion-exception test passes, the unlink-first behavior is not being reached: stop and re-read `pipeline.py:206-213`.

- [ ] **Step 3: Implement in `pipeline.py`**

Imports (lines 5-22): add `import shutil` with the other stdlib imports, and replace `from .loader import load_document` with:

```python
from .identity import run_identity
from .loader import _cache_meta_path, load_document
from .publish import (
    clear_failure, new_staging_dir, output_names, publish_staged, write_failure, write_text_lf,
)
```

Add near the top, after the imports:

```python
REVIEW_INPUT_NOTE = (
    "Docling JSON given without its source PDF: the PDF hash and conversion settings are "
    "not verified, so this output is a review input only."
)
```

Replace `process_prospectus` (lines 174-263; keep `print_audit_summary` after it) with:

```python
def _stage_outputs(
    stage: Path, names: Any, payload: dict[str, Any], is_pdf: bool,
    export_pl: bool, export_jsonl: bool, export_csv: bool,
) -> list[str]:
    """Write every companion into `stage`; returns file names in publish order, main JSON last."""
    produced: list[str] = []
    if is_pdf:
        write_text_lf(
            stage / names.essentials.name,
            json.dumps(build_essentials(payload), indent=2, ensure_ascii=False),
        )
        produced.append(names.essentials.name)
    if payload["audit"]["status"] != "error":
        if export_pl:
            write_text_lf(stage / names.prolog.name, "\n".join(payload["prolog"]["clauses"]) + "\n")
            produced.append(names.prolog.name)
        if export_jsonl:
            chunks = payload["rag"]["semantic_chunks"] + payload["rag"]["hierarchical_chunks"]
            write_text_lf(
                stage / names.rag.name,
                "".join(json.dumps(chunk, ensure_ascii=False) + "\n" for chunk in chunks),
            )
            produced.append(names.rag.name)
    if export_csv:
        write_review_csv(payload["courses"], stage / names.csv.name)
        produced.append(names.csv.name)
    write_text_lf(stage / names.final.name, json.dumps(payload, indent=2, ensure_ascii=False))
    produced.append(names.final.name)
    return produced


def process_prospectus(
    input_path: Path,
    output_path: Path | None = None,
    export_pl: bool = False,
    export_jsonl: bool = False,
    export_csv: bool = False,
    device: str = "auto",
    semantic_doc_path: Path | None = DEFAULT_SEMANTIC_DOC,
    force_reconvert: bool = False,
    converter: Any = None,
    repair_provider: SemanticRepairProvider | None = None,
    quiet: bool = False,
) -> dict[str, Any]:
    """Full pipeline for one prospectus: convert, parse, audit, then publish.

    Nothing already published is touched until conversion and audit have finished. On any
    exception the staged files go to <output dir>/failed/<base>/ and the exception propagates.
    """
    input_path = Path(input_path).resolve()
    stem = input_path.stem
    if stem.endswith("_docling"):
        stem = stem[: -len("_docling")]
    if output_path:
        final_path = Path(output_path)
    elif input_path.suffix.lower() == ".pdf":
        try:
            relative_parent = input_path.relative_to(SOURCE_PDF_ROOT.resolve()).parent
        except ValueError:
            relative_parent = Path()
        final_path = find_default_output_root() / relative_parent / f"{stem}_prospectus.json"
    else:
        final_path = input_path.parent / f"{stem}_prospectus.json"
    if final_path.suffix.lower() != ".json" or final_path.resolve() == input_path:
        raise ValueError("Output must be a JSON file distinct from the source")

    names = output_names(final_path)
    is_pdf = input_path.suffix.lower() == ".pdf"
    raw_cache_path = final_path.parent / f"{stem}_docling.json" if is_pdf else None
    final_path.parent.mkdir(parents=True, exist_ok=True)
    stage = new_staging_dir(final_path.parent, names.base)
    run_id: dict[str, Any] | None = None
    try:
        run_id = run_identity(input_path, semantic_doc_path)
        document, raw_json_path = load_document(
            input_path, device=device, force_reconvert=force_reconvert,
            converter=converter, raw_json_path=raw_cache_path, stage_dir=stage,
        )
        payload = build_payload(
            document,
            input_path,
            semantic_doc_path,
            raw_json_path,
            repair_provider=repair_provider,
        )

        cache_files: list[str] = []
        if raw_cache_path is not None:
            cache_files = [
                name for name in (raw_cache_path.name, _cache_meta_path(raw_cache_path).name)
                if (stage / name).exists()
            ]
        payload["run_identity"] = {
            **run_id,
            "cache": ("converted" if cache_files else "reused") if is_pdf else "not-applicable",
        }
        if run_id["review_input_only"]:
            payload["run_identity"]["review_note"] = REVIEW_INPUT_NOTE

        outputs = _stage_outputs(stage, names, payload, is_pdf, export_pl, export_jsonl, export_csv)
        publish_staged(stage, names, outputs, cache_files, payload["run_identity"], payload["audit"]["status"])
        clear_failure(names)
    except Exception as exc:
        write_failure(names, exc, input_path, run_id, stage)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)

    if not quiet:
        print(f"[+] Prospectus JSON -> {final_path}")
        if is_pdf:
            print(f"[+] Curriculum essentials -> {names.essentials}")
        if payload["run_identity"]["review_input_only"]:
            print(f"[!] {REVIEW_INPUT_NOTE}")
        if payload["audit"]["status"] == "error":
            print("[!] Audit failed with ERROR status. Blocking downstream exports (.pl, _rag.jsonl).")
        print_audit_summary(payload)
    return payload
```

**(D3)** an `error` audit publishes. **(D4)** `force_reconvert` now defaults to `False`. **(D6)** nothing is published on failure; `write_failure` copies the staged raw JSON.

- [ ] **Step 4: Bump the schema version**

In `common.py` set `SCHEMA_VERSION = "palsu-prospectus-v3.2"` (next minor after the value you recorded in Task 1; if it differs from the plan's assumption, also change `EXPECTED_SCHEMA` in the test). The payload gained `run_identity`; the shape change is: new top-level object `run_identity` with `identity_version, input_kind, input_sha256, pdf_sha256, conversion_identity, conversion_settings, package_sha256, schema_version, semantic_sha256, review_input_only, run_key, cache` and, for review inputs, `review_note`.

- [ ] **Step 5: Run the publication tests, then everything**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_publication.py tests/test_prospectus_cache.py tests/test_prospectus_publish.py tests/test_prospectus_identity.py`
Expected: all pass. Then the full suite and the self-test: green, 80/80. If `write_review_csv([], path)` raises on an empty course list, the stub in `tests/conftest.py` needs one course dict; check the first failure message before changing code.

- [ ] **Step 6: Commit and log**

```
git add backend/bintanong_tools/prospectus_extractor/pipeline.py backend/bintanong_tools/prospectus_extractor/common.py tests/test_prospectus_publication.py
git commit -m "fix: stage prospectus outputs and publish them only after the audit" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
Append to the progress file: the old unlink-first lines replaced, the schema bump and what changed in the payload, and that outputs are now written with LF line endings on Windows (they were CRLF before; no course value changes).

---

### Task 7: `--skip-existing` compares identity and audit status

**Files:**
- Modify: `backend/bintanong_tools/prospectus_extractor/batch.py:16-23, 66-69, 159-253`
- Modify: `backend/bintanong_tools/prospectus_extractor/cli.py:42-43, 124`
- Modify: `backend/bintanong_tools/prospectus_extractor/common.py` (`MANIFEST_SCHEMA_VERSION`)
- Test: `tests/test_prospectus_batch_skip.py`

- [ ] **Step 1: Write the failing tests**

```python
"""--skip-existing trusts a published set only when identity and audit status say so."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from backend.bintanong_tools.prospectus_extractor import batch
from backend.bintanong_tools.prospectus_extractor.batch import BatchConfig, run_batch

pytestmark = pytest.mark.usefixtures("fake_docling")


@pytest.fixture
def env(tmp_path, monkeypatch, pdf_factory, converter, pipeline_state, snapshot):
    source = tmp_path / "pdfs"
    out = tmp_path / "out"
    pdf = pdf_factory(source)
    monkeypatch.setattr(batch, "ensure_docling_env", lambda: None)
    monkeypatch.setattr(batch, "get_shared_converter", lambda *a, **k: converter)

    def run(**overrides):
        config = BatchConfig(input_root=source, output_root=out, semantic_doc=None,
                             skip_existing=True, **overrides)
        return run_batch(config)

    return SimpleNamespace(pdf=pdf, out=out, converter=converter, state=pipeline_state,
                           run=run, snapshot=snapshot)


def only(summary):
    return summary["records"][0]


def test_repeat_run_of_unchanged_input_skips_and_leaves_identical_files(env):
    assert only(env.run())["status"] == "ok"
    before = env.snapshot(env.out)
    mtimes = {p.name: p.stat().st_mtime_ns for p in env.out.iterdir() if p.is_file()}

    record = only(env.run())

    assert record["status"] == "skipped"
    assert "identical run identity" in record["reason"] or "unchanged" in record["reason"]
    assert env.snapshot(env.out) == before
    assert {p.name: p.stat().st_mtime_ns for p in env.out.iterdir() if p.is_file()} == mtimes
    assert len(env.converter.calls) == 1
    assert env.state.builds == 1


def test_skip_existing_never_skips_a_failed_audit(env):
    env.state.status = "error"
    assert only(env.run())["status"] == "audit_error"
    second = only(env.run())
    assert second["status"] == "audit_error"
    assert env.state.builds == 2
    assert "previous audit status was error" in second["skip_check"]

    env.state.status = "ok"
    assert only(env.run())["status"] == "ok"
    assert env.state.builds == 3


def test_changed_pdf_bytes_are_not_skipped(env):
    env.run()
    env.pdf.write_bytes(b"%PDF-two")
    record = only(env.run())
    assert record["status"] == "ok"
    assert "changed" in record["skip_check"]
    assert env.state.builds == 2
    assert len(env.converter.calls) == 2


def test_changed_parser_is_not_skipped_but_reuses_the_cached_conversion(env, monkeypatch):
    env.run()
    monkeypatch.setattr(batch, "package_sha256", lambda: "f" * 64)
    record = only(env.run())
    assert record["status"] == "ok"
    assert env.state.builds == 2
    assert len(env.converter.calls) == 1  # D1: re-parse from the identity-matched JSON, no reconversion


def test_a_companion_requested_now_but_missing_from_the_last_run_is_not_skipped(env):
    env.run(write_csv=False)
    record = only(env.run())  # write_csv defaults to True
    assert record["status"] == "ok"
    assert "requested outputs not in last run" in record["skip_check"]


def test_a_half_published_set_is_not_skipped(env):
    env.run()
    (env.out / "a_prospectus.pl").unlink()
    record = only(env.run())
    assert record["status"] == "ok"
    assert "a_prospectus.pl is missing" in record["skip_check"]


def test_a_file_without_a_manifest_is_not_skipped(env):
    env.run()
    (env.out / "a_publish.json").unlink()
    record = only(env.run())
    assert record["status"] == "ok"
    assert record["skip_check"] == "no publish manifest"


def test_force_overrides_skip_existing_and_reconverts(env):
    env.run()
    record = only(env.run(force_reconvert=True))
    assert record["status"] == "ok"
    assert len(env.converter.calls) == 2


def test_error_record_points_at_the_diagnostics_and_keeps_earlier_files(env):
    env.run()
    before = env.snapshot(env.out)
    env.pdf.write_bytes(b"%PDF-two")
    env.converter.fail = True

    record = only(env.run())

    assert record["status"] == "error"
    assert record["error_type"] == "RuntimeError"
    assert record["failed_dir"].endswith("failed" + __import__("os").sep + "a")
    assert env.snapshot(env.out) == before


def test_scan_ignores_the_failed_diagnostics_folder(tmp_path):
    root = tmp_path / "in"
    (root / "failed" / "a").mkdir(parents=True)
    (root / "keep_docling.json").write_text("{}", encoding="utf-8")
    (root / "failed" / "a" / "a_docling.json").write_text("{}", encoding="utf-8")
    found = batch.scan_inputs(root, patterns=["*.json"])
    assert [p.name for p in found] == ["keep_docling.json"]
```

- [ ] **Step 2: Run and confirm failures**

Run: `uv run --project backend --extra tools --extra dev python -m pytest -q tests/test_prospectus_batch_skip.py`
Expected: failures. The old code skips a failed audit and a changed PDF (`status == "skipped"` where the tests expect `ok`/`audit_error`), has no `skip_check` key, and `scan_inputs` returns the `failed` file. `AttributeError: module ... batch has no attribute 'package_sha256'` for the parser test. If the unchanged-repeat test passes, that is correct (old behavior skips it by existence); every other test must fail.

- [ ] **Step 3: Implement in `batch.py`**

Imports: replace the lines from `from .docling_env import ...` through `from .pipeline import process_prospectus` with:

```python
from .docling_env import ensure_docling_env, get_shared_converter
from .identity import package_sha256, run_identity
from .paths import DEFAULT_SEMANTIC_DOC, find_default_input_root, find_default_output_root
from .pipeline import process_prospectus
from .publish import output_names, read_manifest, verify_published
```

Add `"failed"` to `IGNORED_DIR_PARTS` (the set at lines 66-69), so diagnostics copies of `*_docling.json` are not rescanned as inputs.

Add above `run_batch`:

```python
def skip_check(item: BatchItem, config: BatchConfig, package_hash: str) -> tuple[bool, str]:
    """May this item be skipped? Returns (skip, reason). Never skips a failed audit."""
    if not config.skip_existing:
        return False, "skip-existing not requested"
    if config.force_reconvert:
        return False, "--force given"
    names = output_names(item.json_path)
    manifest = read_manifest(names.manifest)
    if manifest is None:
        return False, "no publish manifest"
    status = manifest.get("audit_status")
    if status not in ("ok", "warn"):
        return False, f"previous audit status was {status}"
    expected = run_identity(item.source_pdf, config.semantic_doc, package_hash=package_hash)
    if manifest["run_key"] != expected["run_key"]:
        return False, "input, settings, parser or schema changed"
    intact, why = verify_published(names.final.parent, manifest)
    if not intact:
        return False, why
    wanted = [names.final.name]
    if item.source_pdf.suffix.lower() == ".pdf":
        wanted.append(names.essentials.name)
    if config.write_csv:
        wanted.append(names.csv.name)
    if config.write_pl:
        wanted.append(names.prolog.name)
    if config.write_jsonl:
        wanted.append(names.rag.name)
    missing = [name for name in wanted if name not in manifest["files"]]
    if missing:
        return False, f"requested outputs not in last run: {missing}"
    return True, "identical run identity"
```

Replace `run_batch` (lines 159-253) with:

```python
def run_batch(config: BatchConfig) -> dict[str, Any]:
    """Extract every prospectus under config.input_root, then write a manifest."""
    sources = scan_inputs(config.input_root, config.recursive, config.include_patterns)
    items = build_batch_items(sources, config)
    records: list[dict[str, Any]] = []

    package_hash = package_sha256()
    decisions: list[tuple[bool, str]] = []
    for item in items:
        try:
            decisions.append(skip_check(item, config, package_hash))
        except Exception as exc:  # an unreadable PDF is reported by the run itself
            decisions.append((False, f"identity check failed: {type(exc).__name__}: {exc}"))

    converter = None
    needs_conversion = any(
        not skipped
        for item, (skipped, _why) in zip(items, decisions)
        if item.source_pdf.suffix.lower() == ".pdf"
    )
    if needs_conversion:
        try:
            ensure_docling_env()
            converter = get_shared_converter(device=config.device)
        except Exception as exc:
            print(f"[!] Could not pre-warm Docling: {exc}")

    work: Iterable[tuple[BatchItem, tuple[bool, str]]] = list(zip(items, decisions))
    if RICH_AVAILABLE and console and items:
        work = track(work, description="Extracting prospectuses...")

    for item, (skip, why) in work:
        names = output_names(item.json_path)
        is_pdf = item.source_pdf.suffix.lower() == ".pdf"
        record: dict[str, Any] = {
            "source": str(item.source_pdf),
            "json_path": str(item.json_path),
            "csv_path": str(item.csv_path),
            "status": "pending",
            "skip_check": why,
        }
        try:
            if skip:
                record.update({"status": "skipped", "reason": f"unchanged: {why}"})
                records.append(record)
                continue

            payload = process_prospectus(
                item.source_pdf,
                output_path=item.json_path,
                export_pl=config.write_pl,
                export_jsonl=config.write_jsonl,
                export_csv=config.write_csv,
                device=config.device,
                semantic_doc_path=config.semantic_doc,
                converter=converter,
                force_reconvert=config.force_reconvert,
                quiet=True,
            )
            audit = payload["audit"]
            record.update(
                {
                    "status": "audit_error" if audit["status"] == "error" else audit["status"],
                    "program": payload.get("program"),
                    "degree": payload.get("degree"),
                    "college": payload.get("college"),
                    "effective_school_year": payload["metadata"].get("effective_school_year"),
                    "course_count": audit["total_courses"],
                    "total_units": audit["computed_total_units"],
                    "declared_total_units": audit["declared_total_units"],
                    "years_detected": audit["years_detected"],
                    "errors": audit["errors"],
                    "warning_count": len(audit["warnings"]),
                    "essentials_path": str(names.essentials) if is_pdf else None,
                    "publish_manifest": str(names.manifest),
                }
            )
        except Exception as exc:
            record.update(
                {
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "traceback": traceback.format_exc(limit=5),
                    "failed_dir": str(names.failed_dir),
                }
            )
        records.append(record)

    manifest_path = write_manifest(records, config.output_root) if config.write_manifest else None
    summary = {
        "total": len(records),
        "succeeded": sum(1 for r in records if r["status"] in {"ok", "warn"}),
        "audit_failed": sum(1 for r in records if r["status"] == "audit_error"),
        "skipped": sum(1 for r in records if r["status"] == "skipped"),
        "failed": sum(1 for r in records if r["status"] == "error"),
        "manifest_path": str(manifest_path) if manifest_path else None,
        "records": records,
    }
    return summary
```

The test fake audit lacks `declared_total_units`; if the run fails with a `KeyError`, add `"declared_total_units": 0` to the audit dict in `tests/conftest.py` (the real audit has it).

- [ ] **Step 4: CLI text and `--force`**

In `cli.py` replace lines 42-43:

```python
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Batch: skip a PDF only when its last run has the same PDF bytes, conversion "
             "settings, parser and schema, passed its audit, and still matches its publish manifest",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Process everything even with --skip-existing, and reconvert PDFs instead of "
             "reusing a cached Docling JSON",
    )
```

and in the single-file `process_prospectus(...)` call (line 124) change `force_reconvert=True` to `force_reconvert=args.force`. Leave the `--dump-grid` call (line 80) alone. **(D4)**

- [ ] **Step 5: Bump `MANIFEST_SCHEMA_VERSION`**

In `common.py` change `MANIFEST_SCHEMA_VERSION` to the next minor of the value found in Task 1 (assumed `palsu-prospectus-batch-manifest-v3.0` becoming `...-v3.1`): records gained `skip_check`, `publish_manifest` and, for errors, `failed_dir`.

- [ ] **Step 6: Run the skip tests, then everything**

Expected: `tests/test_prospectus_batch_skip.py` 10 passed; the full suite green; self-test 80/80; `tests/test_prospectus_batch.py` still green (the isolated runner is unchanged).

- [ ] **Step 7: Commit and log**

```
git add backend/bintanong_tools/prospectus_extractor/batch.py backend/bintanong_tools/prospectus_extractor/cli.py backend/bintanong_tools/prospectus_extractor/common.py tests/test_prospectus_batch_skip.py
git commit -m "fix: skip-existing compares run identity and audit status, never a failed audit" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
Append to the progress file (also: `--skip-existing` is batch-only; there is no single-file skip).

---

### Task 8: Prove the course fields are unchanged on the 44 cached inputs

**Files:**
- Create (not committed): `scripts/prospectus_course_compare.py`

The earlier golden script was deleted in `38af9fd`'s successor; it is recoverable with `git show 2dffe3d:scripts/prospectus_golden_check.py`. This phase needs a field-level comparer instead (old code vs new, course fields only), so the script below replaces it. Phase D must not change any extracted course value.

- [ ] **Step 1: Write the comparer**

```python
#!/usr/bin/env python3
"""Phase D regression: course fields are identical between the base commit and this branch.

    python scripts/prospectus_course_compare.py run --which old --repo OLD_TREE --golden DIR --work WORK --semantic-doc MAP
    python scripts/prospectus_course_compare.py run --which new --repo NEW_TREE --golden DIR --work WORK --semantic-doc MAP
    python scripts/prospectus_course_compare.py compare --work WORK

Each *_docling.json is run through `python -m backend.bintanong_tools.prospectus_extractor`
with cwd set to the tree under test, so that tree's package is the one imported.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

COURSE_FIELDS = (
    "course_code", "course_title", "year_level", "semester", "total_units", "lecture_units",
    "lab_units", "prerequisites", "prerequisites_raw", "prerequisites_unresolved",
    "standing_requirements", "category", "is_elective", "elective_group",
)
TOP_FIELDS = ("program", "degree", "college", "campus")
NEW_ONLY_FILES = {"candidate_publish.json"}


def run(args: argparse.Namespace) -> int:
    sources = sorted(args.golden.rglob("*_docling.json"))[: args.limit]
    if not sources:
        print(f"no *_docling.json under {args.golden}")
        return 2
    args.work.mkdir(parents=True, exist_ok=True)
    (args.work / "index.json").write_text(
        json.dumps({f"{n:02d}": s.name for n, s in enumerate(sources, 1)}, indent=2), encoding="utf-8")
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONHASHSEED="0")
    for number, source in enumerate(sources, 1):
        out = args.work / args.which / f"{number:02d}"
        out.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-m", "backend.bintanong_tools.prospectus_extractor",
                   "-i", str(source), "-o", str(out / "candidate.json"), "--export-all",
                   "--device", "cpu", "--semantic-doc", str(args.semantic_doc)]
        with (out / "run.log").open("w", encoding="utf-8") as log:
            code = subprocess.run(command, cwd=args.repo, env=env, stdout=log,
                                  stderr=subprocess.STDOUT).returncode
        print(f"{args.which} {number}/{len(sources)} exit={code} {source.name}", flush=True)
    return 0


def project(payload: dict) -> dict:
    return {
        "top": {key: payload.get(key) for key in TOP_FIELDS},
        "effective_school_year": (payload.get("metadata") or {}).get("effective_school_year"),
        "audit_status": (payload.get("audit") or {}).get("status"),
        "courses": [{key: course.get(key) for key in COURSE_FIELDS} for course in payload.get("courses", [])],
    }


def compare(args: argparse.Namespace) -> int:
    index = json.loads((args.work / "index.json").read_text(encoding="utf-8"))
    failures = 0
    for number, name in index.items():
        old_dir, new_dir = args.work / "old" / number, args.work / "new" / number
        problems = []
        old_files = {p.name for p in old_dir.iterdir() if p.name not in {"run.log"}}
        new_files = {p.name for p in new_dir.iterdir() if p.name not in {"run.log"}} - NEW_ONLY_FILES
        if old_files != new_files:
            problems.append(f"file set differs: old={sorted(old_files)} new={sorted(new_files)}")
        try:
            old = project(json.loads((old_dir / "candidate.json").read_text(encoding="utf-8")))
            new = project(json.loads((new_dir / "candidate.json").read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            problems.append(f"cannot read candidate.json: {exc}")
        else:
            if old["top"] != new["top"] or old["effective_school_year"] != new["effective_school_year"]:
                problems.append("program/degree/college/campus/school year differ")
            if old["audit_status"] != new["audit_status"]:
                problems.append(f"audit status {old['audit_status']} -> {new['audit_status']}")
            if len(old["courses"]) != len(new["courses"]):
                problems.append(f"course count {len(old['courses'])} -> {len(new['courses'])}")
            else:
                for position, (a, b) in enumerate(zip(old["courses"], new["courses"])):
                    changed = [key for key in COURSE_FIELDS if a[key] != b[key]]
                    if changed:
                        problems.append(f"course #{position} {a['course_code']!r}: {changed}")
                        break
        failures += bool(problems)
        print(f"{number} {'FAIL' if problems else 'ok'} {name}")
        for problem in problems:
            print(f"    {problem}")
    total = len(index)
    print(f"{total - failures}/{total} identical")
    return 1 if failures else 0


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    sub = cli.add_subparsers(dest="command", required=True)
    runner = sub.add_parser("run")
    runner.add_argument("--which", choices=("old", "new"), required=True)
    runner.add_argument("--repo", type=Path, required=True)
    runner.add_argument("--golden", type=Path, required=True)
    runner.add_argument("--work", type=Path, required=True)
    runner.add_argument("--semantic-doc", type=Path, required=True)
    runner.add_argument("--limit", type=int)
    comparer = sub.add_parser("compare")
    comparer.add_argument("--work", type=Path, required=True)
    args = cli.parse_args()
    return run(args) if args.command == "run" else compare(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Smoke test on one input (expect about 4 minutes)**

```
$REPO = "C:\Users\Hawksprey\source\repos\Bintanong"
$BASE_SHA = git -C $REPO merge-base dev HEAD
git -C $REPO worktree add --detach "$env:TEMP\phase-d-base" $BASE_SHA
$GOLDEN = "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29"
$MAP = "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md"
$WORK = "$env:TEMP\phase-d-compare"
$PY = uv run --project backend --extra tools --extra dev python -c "import sys;print(sys.executable)"
& $PY scripts\prospectus_course_compare.py run --which old --repo "$env:TEMP\phase-d-base" --golden $GOLDEN --work $WORK --semantic-doc $MAP --limit 1
& $PY scripts\prospectus_course_compare.py run --which new --repo $REPO --golden $GOLDEN --work $WORK --semantic-doc $MAP --limit 1
& $PY scripts\prospectus_course_compare.py compare --work $WORK
```

Expected: `old 1/1 exit=0 ...`, `new 1/1 exit=0 ...`, then `01 ok ...` and `1/1 identical`. Open `$WORK\new\01` and confirm it also contains `candidate_publish.json` (new) and that `run.log` shows no traceback. If the old run fails to import, the worktree needs no environment of its own: the interpreter comes from the main checkout and only the working directory differs. If `candidate.json` is missing in either, read `run.log`.

- [ ] **Step 3: Full run, detached (about 90 minutes per side; old and new run in parallel)**

Background tool calls die after 10 minutes, so launch both detached and poll the logs:

```
Remove-Item $WORK -Recurse -Force
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"& '$PY' '$REPO\scripts\prospectus_course_compare.py' run --which old --repo '$env:TEMP\phase-d-base' --golden '$GOLDEN' --work '$WORK' --semantic-doc '$MAP' *> '$env:TEMP\phase-d-old.log'"
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"& '$PY' '$REPO\scripts\prospectus_course_compare.py' run --which new --repo '$REPO' --golden '$GOLDEN' --work '$WORK' --semantic-doc '$MAP' *> '$env:TEMP\phase-d-new.log'"
```

Poll every few minutes with `Get-Content "$env:TEMP\phase-d-old.log" -Tail 2; Get-Content "$env:TEMP\phase-d-new.log" -Tail 2` until both show `44/44`. Meanwhile proceed with Task 9 only if it does not use the same CPU heavily; otherwise wait.

- [ ] **Step 4: Compare**

```
& $PY scripts\prospectus_course_compare.py compare --work $WORK
```

Expected final line: `44/44 identical`, exit code 0. Any `FAIL` is a real difference: use superpowers:systematic-debugging, diff `old\NN\candidate.json` against `new\NN\candidate.json` on the named course, and trace the first differing field to a module. The only acceptable differences outside course fields are `run_identity`, `schema_version` (not compared) and the extra `candidate_publish.json`.

- [ ] **Step 5: Clean up and log**

```
git -C $REPO worktree remove --force "$env:TEMP\phase-d-base"
Remove-Item scripts\prospectus_course_compare.py
git status --short
```

Expected: only the two pre-existing untracked/modified items (`.gitignore`, the CODEX handoff). Append to the progress file: date, base SHA, `44/44 identical`, and a note that the comparer is recoverable from this plan (it is not committed).

---

### Task 9: One real end-to-end failure-injection run

**Files:** none (scratch folders under `$env:TEMP`).

This run uses a real PDF and a real Docling conversion, not the fakes. Docling can take several minutes per PDF, so launch the conversions detached.

- [ ] **Step 1: Pick the smallest source PDF and copy it into a scratch input folder**

```
$SRC = "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main"
$pdf = Get-ChildItem $SRC -Recurse -Filter *.pdf | Sort-Object Length | Select-Object -First 1
$E2E = Join-Path $env:TEMP "phase-d-e2e"
Remove-Item $E2E -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory "$E2E\in","$E2E\out" | Out-Null
Copy-Item $pdf.FullName "$E2E\in\target.pdf"
$CMD = @("--project","backend","--extra","tools","--extra","dev","python","-m","backend.bintanong_tools.prospectus_extractor","-i","$E2E\in","--batch","-o","$E2E\out","--skip-existing","--export-all","--device","cpu","--semantic-doc",$MAP)
```

(`$MAP` as defined in Task 8.)

- [ ] **Step 2: Run A, a real first run (detached)**

```
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"uv run $($CMD -join ' ') *> '$E2E\runA.log'"
```

Poll `Get-Content "$E2E\runA.log" -Tail 5` until the line `[*] Batch: ...` appears. Expected: `1 extracted` (or `1 failed audit`; both publish) and a manifest line. Then record hashes of everything except the batch manifest:

```
$before = Get-ChildItem "$E2E\out" -File | Where-Object Name -ne "batch_manifest.json" | Get-FileHash | Select-Object Hash,@{n='N';e={Split-Path $_.Path -Leaf}}
$before | Format-Table
```

Expected files: `target_prospectus.json`, `target_docling.json`, `target_docling.meta.json`, `target_publish.json`, `target_essentials.json`, `target_review.csv` (and `.pl`/`_rag.jsonl` when the audit is not `error`).

- [ ] **Step 3: Run B, unchanged input**

Run the same command in the foreground (it should return in seconds): `uv run @CMD`. Expected: `[*] Batch: 0 extracted, 0 failed audit, 1 skipped, 0 errored.` when run A's audit was `ok`/`warn`. If run A's audit was `error`, expected is `1 failed audit` and no skip; that proves the failed-audit rule on real data, so note it and continue to Step 4 using a PDF that passes (pick the next-smallest) if you also want the identical-files check. Re-hash and compare with `$before`: expected no differences.

- [ ] **Step 4: Run C, failure injection at conversion**

Corrupt the PDF at the same path, then run (detached, as the converter may take time before failing):

```
[IO.File]::WriteAllBytes("$E2E\in\target.pdf", [Text.Encoding]::ASCII.GetBytes("%PDF-1.4 not really a pdf"))
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"uv run $($CMD -join ' ') *> '$E2E\runC.log'; `$LASTEXITCODE | Out-File '$E2E\runC.exit'"
```

When `runC.exit` exists: expected `[*] Batch: 0 extracted, 0 failed audit, 0 skipped, 1 errored.` and exit code `1`. Re-hash `$E2E\out` (excluding `batch_manifest.json`) and compare with `$before`: **expected no differences**. Check `Get-ChildItem "$E2E\out" -Force` shows no `.target.staging-*` directory, and that `$E2E\out\failed\target\failure.json` exists with an `error_type` and a traceback. If any earlier file changed, stop and report; that is a Phase D failure.

- [ ] **Step 5: Run D, restore and confirm the skip**

```
Copy-Item $pdf.FullName "$E2E\in\target.pdf" -Force
uv run @CMD
```

Expected: `1 skipped` (identical identity). `failed\target\` is still present: diagnostics are cleared by the next successful processing, not by a skip; note this in the decision record.

- [ ] **Step 6: Log**

Append to the progress file: the PDF file name, the three observed outcome lines, `no differences` for B and C, and the `failure.json` error type. Clean up: `Remove-Item $E2E -Recurse -Force`.

---

### Task 10: Documentation, Codex gate, hand-off

**Files:**
- Create: `docs/decisions/prospectus-cache-and-publication.md`
- Modify: `plans/plan_current_progress/extractor_split_progress.md`, `plans/plan_current_progress/current_progress.md`

- [ ] **Step 1: Write the decision record**

State, in plain sentences: the base commit; the two identities and what is in each; the cache meta format; the publish order, why the manifest is written last (a file-by-file publish is not atomic; hashes make a partial publish detectable), and that `Path.replace` over a file works on Windows while replacing a directory does not, so nothing replaces a directory; what "failure" means and what `failed/<base>/` holds; D1-D6 as implemented; the `run_identity` payload object and the schema bumps; that `--skip-existing` is batch-only; that outputs are now written with LF line endings; that `failed/` is cleared by a later successful publish, not by a skip; that a Docling JSON given as input is a review input and the output says so; and the Task 8 and Task 9 evidence (`44/44 identical`, the observed outcome lines).

- [ ] **Step 2: Full verification**

Run both commands from "Commands used throughout". Expected: full suite green, self-test 80/80. Record the counts.

- [ ] **Step 3: Codex gate (read-only, detached, about 15 minutes)**

```
$prompt = "Review branch feature/prospectus-phase-d-safe-cache against dev in this repo. Claim: the raw Docling JSON cache is reused only when PDF bytes and conversion settings match; process_prospectus stages into a sibling directory and publishes file by file with a hash manifest written last, so a failed run leaves earlier outputs byte-identical; --skip-existing never skips a failed audit, a changed PDF, a changed parser, or a half-published set. Try to break it: find any path where an earlier output is deleted or modified before conversion and audit finish, any Windows-specific failure of Path.replace or rmtree, any case where the manifest passes verification for an inconsistent set, any stale .pl or _rag.jsonl that can look current, any import of prospectus_batch from the package, and any course field that the change could alter. Do not modify files. Report findings with file and line."
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"codex exec --sandbox read-only -o '$env:TEMP\codex-phase-d.md' '$prompt'"
```

Poll for `$env:TEMP\codex-phase-d.md`. If Codex is rate-limited or errors, record that in the progress file and continue. Fix each confirmed finding with a failing test first; record unconfirmed ones as skipped with the reason.

- [ ] **Step 4: Log and commit**

Append a dated summary to `extractor_split_progress.md` and a "Phase D" paragraph to `current_progress.md` (branch, commits, counts, Task 8 and 9 results, Codex findings, "next: Phase E").

```
git add docs/decisions/prospectus-cache-and-publication.md plans/plan_current_progress/extractor_split_progress.md plans/plan_current_progress/current_progress.md
git commit -m "docs: record the safe cache and output publication design and its evidence" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

Do not merge into `dev` and do not push; ask the user (superpowers:finishing-a-development-branch).

**Phase D gate:** the cache tests, publish tests, publication tests and skip tests are green; `44/44 identical` on course fields; the real failure-injection run left the earlier files byte-identical and wrote diagnostics; the repeat run of an unchanged input skipped and produced identical files; the full suite and self-test are green; the decision record is written; Codex findings are resolved or recorded.

---

## Self-review

**Spec coverage.**
- Cache identity = PDF hash + conversion-affecting settings (OCR, table mode, cell matching env var, docling/docling-core/docling-parse versions) + parser package hash: Tasks 2 and 4 (conversion identity) and Task 2 and 7 (`run_key` adds the package hash). The device question is D2; the parser-hash split is D1.
- A mismatching cached JSON is ignored and reconverted when the PDF is available: Task 4 (five damage modes, settings change, OCR). Only-JSON input is a review input and the output says so: Task 6 (`review_input_only`, `review_note`, console warning).
- `--skip-existing` compares identity and audit status, never skips a failed audit: Task 7 `skip_check` and its tests.
- `process_prospectus` writes to a temporary sibling directory and publishes only after conversion and audit: Task 6. The old unlink-before-convert code (`pipeline.py:206-213`) is gone.
- Failure leaves earlier outputs byte-identical, diagnostics in `<output dir>/failed/<stem>/`: Tasks 5 and 6 tests; real run in Task 9.
- Windows: file-by-file publication, `replace_file` retry; partial publish handled by the manifest (justified above).
- Tests first, Docling faked at the `loader`/converter boundary and `pipeline.build_payload`: `tests/conftest.py`. One real failure-injection run: Task 9.
- Shared hash helper without an import cycle: `identity.py`, with an AST test.
- OCR room: `conversion_settings(do_ocr, ocr_languages)` is inside the cache identity and tested; `get_shared_converter`'s cache key is flagged for the OCR plan.
- 44-input regression, schema bump, progress file after each task, Codex gate, start check, Phase A gate conditional: Tasks 8, 6, every task, 10, 1.

**Placeholder scan.** No "TBD"/"similar to Task N". The one literal that depends on Phase C (`palsu-prospectus-v3.2`) is declared in "SCHEMA_VERSION change" with the rule for adjusting it and appears in exactly Task 6 step 1 and step 4.

**Type and name consistency.** `file_sha256`, `package_sha256`, `PACKAGE_DIR`, `conversion_settings`, `conversion_identity`, `run_identity`, `IDENTITY_VERSION` (identity.py); `cache_reuse_check`, `_write_bytes_atomic`, `_cache_meta_path` (loader.py); `OutputNames`, `output_names`, `new_staging_dir`, `remove_stale_staging`, `replace_file`, `write_text_lf`, `publish_staged(stage, names, outputs, cache_files, run_identity, audit_status)`, `read_manifest`, `verify_published`, `write_failure`, `clear_failure`, `PUBLISH_SCHEMA` (publish.py); `skip_check(item, config, package_hash)` (batch.py). The tests call exactly these signatures. `load_document(..., stage_dir=)` and `get_pipeline_options(device, settings=)` are the only changed existing signatures; `process_prospectus`'s `force_reconvert` default changes from `True` to `False` (D4).

**Known risks.** The staged-write test stub (`pipeline_state`) bypasses the real parse; the Task 8 real-parse comparison and the Task 9 real conversion cover that gap. Publication is not atomic across files; the manifest makes the failure detectable, not impossible. Single writer per output stem is assumed (stale staging directories of the same stem are removed at the start of a run).
