# Exact task brief from plans\2026-10-03-prospectus-phase-e-rag-provenance.md

Read approved_execution.md and preflight-ledger.md first. They supersede obsolete base/merge/dev/version/path snippets in this preserved historical plan. Do not edit the original plan. Preserve original task requirements below unless an approved ruling supersedes them.

### Task 5: Layout chunks get IDs, pages and a token check

**Files:**
- Modify: `tests/test_prospectus_chunks.py` (append)

`build_hierarchical_rag_chunks` was already rewritten in Task 3. This task proves it. Decision: layout chunks over the cap are rejected, not split, because they are Docling's own units and the curriculum facts are already covered by course and term chunks; the real data has one 1,980-word table chunk.

- [ ] **Step 1: Append the tests**

```python
def _layout_document(text_items=(), docling_document=None):
    return ProspectusEvidence(
        text_items=list(text_items), docling_document=docling_document, source_kind="docling-json")


def test_fallback_layout_chunks_are_hash_bound_and_capped():
    document = _layout_document([
        {"item_id": "text-0", "label": "title", "text": "BS TEST CURRICULUM", "page": 1, "bbox": None},
        {"item_id": "text-1", "label": "text", "text": "word " * 700, "page": 1, "bbox": None},
    ])
    rejected = []
    chunks = rag.build_hierarchical_rag_chunks(document, "t.pdf", pdf_sha256=PDF_A, rejected=rejected)
    assert [c["chunk_type"] for c in chunks] == ["hierarchical_layout_fallback"]
    assert chunks[0]["pdf_sha256"] == PDF_A and chunks[0]["content_review"] == "pending"
    assert chunks[0]["source_text"] == "BS TEST CURRICULUM"
    again = rag.build_hierarchical_rag_chunks(document, "t.pdf", pdf_sha256=PDF_B)
    assert again[0]["chunk_id"] != chunks[0]["chunk_id"]
    assert [(r["label"], r["reason"]) for r in rejected] == [("layout_fallback:1", "over_token_cap")]


def test_docling_layout_chunks_carry_their_pages(monkeypatch):
    meta = SimpleNamespace(model_dump=lambda mode="json": {
        "headings": ["FIRST YEAR"],
        "doc_items": [{"self_ref": "#/texts/2", "prov": [{"page_no": 2}]}],
    })
    chunk = SimpleNamespace(text="Effective SY 2018-2019", meta=meta)
    fake = SimpleNamespace(chunk=lambda doc: [chunk])
    monkeypatch.setattr(rag, "load_docling", lambda: {"HierarchicalChunker": lambda: fake})
    chunks = rag.build_hierarchical_rag_chunks(_layout_document(docling_document=object()), "t.pdf", pdf_sha256=PDF_A)
    assert [c["chunk_type"] for c in chunks] == ["hierarchical_layout"]
    assert chunks[0]["pages"] == [2] and chunks[0]["section_path"] == ["FIRST YEAR"]
    assert chunks[0]["source_spans"][0]["locator"] == {"kind": "docling_ref", "ref": "#/texts/2"}


def test_all_oversized_docling_chunks_do_not_fall_back_to_the_text_path(monkeypatch):
    huge = SimpleNamespace(text="word " * 700, meta=None)
    fake = SimpleNamespace(chunk=lambda doc: [huge])
    monkeypatch.setattr(rag, "load_docling", lambda: {"HierarchicalChunker": lambda: fake})
    rejected = []
    chunks = rag.build_hierarchical_rag_chunks(
        _layout_document([{"item_id": "t", "label": "text", "text": "kept?", "page": 1, "bbox": None}],
                         docling_document=object()),
        "t.pdf", pdf_sha256=PDF_A, rejected=rejected)
    assert chunks == [] and rejected[0]["reason"] == "over_token_cap"
```

- [ ] **Step 2: Run**

Expected: all three pass at once, because the code exists. To make sure they can fail, temporarily change `TOKEN_HARD_CAP` to `10_000` in `chunking.py`, rerun, and confirm `test_fallback_layout_chunks_are_hash_bound_and_capped` and the last test fail; then revert the edit.

- [ ] **Step 3: Full suite, progress note, commit**

```
git add tests/test_prospectus_chunks.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "test: pin layout chunk IDs, pages and token cap"
```

---



### Task 6: Wire the pipeline: hash, payload shape, jsonl, schema version

**Files:**
- Modify: `tests/test_prospectus_chunks.py` (append)
- Modify: `backend/bintanong_tools/prospectus_extractor/pipeline.py` (lines 25-126, 174-263)
- Modify: `backend/bintanong_tools/prospectus_extractor/common.py` (line 8)

- [ ] **Step 1: Append the failing end-to-end tests**

```python
import hashlib
import json
import time

from backend.bintanong_tools.prospectus_extractor import pipeline
from backend.bintanong_tools.prospectus_extractor.common import SCHEMA_VERSION
from backend.bintanong_tools.prospectus_extractor.pipeline import build_payload
from backend.bintanong_tools.prospectus_extractor.selftest import (
    CS_TEXT_ITEMS, cs_fixture_grid, fixture_document)


def _cs_payload(pdf):
    return build_payload(
        fixture_document(cs_fixture_grid(), CS_TEXT_ITEMS), Path("cs.pdf"),
        semantic_doc_path=None, pdf_sha256=pdf)


def _ids(payload):
    return [c["chunk_id"] for c in payload["rag"]["semantic_chunks"]]


def test_same_pdf_gives_same_ids_even_when_the_timestamp_differs():
    first = _cs_payload(PDF_A)
    time.sleep(1.1)  # generated_at has one-second resolution
    second = _cs_payload(PDF_A)
    assert first["generated_at"] != second["generated_at"]
    assert _ids(first) and _ids(first) == _ids(second)
    assert len(set(_ids(first))) == len(_ids(first))


def test_another_edition_shares_no_chunk_id():
    assert not set(_ids(_cs_payload(PDF_A))) & set(_ids(_cs_payload(PDF_B)))


def test_payload_rag_block_reports_chunker_and_rejections():
    payload = _cs_payload(PDF_A)
    rag_block = payload["rag"]
    assert payload["pdf_sha256"] == PDF_A
    assert rag_block["chunker_version"] == chunking.CHUNKER_VERSION
    assert rag_block["token_count_method"] == chunking.TOKEN_COUNT_METHOD
    assert rag_block["rejected_chunks"] == [], rag_block["rejected_chunks"]
    assert payload["quality_report"]["total_rejected_chunks"] == 0
    assert payload["schema_version"] == SCHEMA_VERSION
    for chunk in rag_block["semantic_chunks"] + rag_block["hierarchical_chunks"]:
        assert chunk["pdf_sha256"] == PDF_A and chunk["content_review"] == "pending"
        assert chunking.fits_cap(chunk["token_count"])
    for chunk in of_type(rag_block["semantic_chunks"], "course"):
        assert chunk["cell_ids"] and chunk["source_spans"] and chunk["source_text"]
    for chunk in of_type(rag_block["semantic_chunks"], "elective_pool"):
        assert any(s["locator"]["kind"] == "text_item" for s in chunk["source_spans"])


def test_blocked_audit_still_emits_no_chunks_and_no_rejections():
    from backend.bintanong_tools.prospectus_extractor.selftest import bsa_fixture_grid, BSA_TEXT_ITEMS
    payload = build_payload(
        fixture_document(bsa_fixture_grid(), BSA_TEXT_ITEMS), Path("bsa.pdf"),
        semantic_doc_path=None, pdf_sha256=PDF_A)
    assert payload["audit"]["status"] == "error"
    assert payload["rag"]["semantic_chunks"] == [] and payload["rag"]["rejected_chunks"] == []


def test_process_prospectus_hashes_the_pdf_and_writes_lf_jsonl(tmp_path, monkeypatch):
    pdf = tmp_path / "cs.pdf"
    pdf.write_bytes(b"%PDF-test")
    monkeypatch.setattr(
        pipeline, "load_document",
        lambda *_args, **_kwargs: (fixture_document(cs_fixture_grid(), CS_TEXT_ITEMS), None))
    pipeline.process_prospectus(
        pdf, tmp_path / "cs_prospectus.json", export_jsonl=True, semantic_doc_path=None, quiet=True)
    raw = (tmp_path / "cs_rag.jsonl").read_bytes()
    assert b"\r\n" not in raw
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
    assert rows and {r["pdf_sha256"] for r in rows} == {hashlib.sha256(b"%PDF-test").hexdigest()}
    assert all("chunk_id" in r and "id" not in r for r in rows)


def test_docling_json_input_runs_unanchored(tmp_path, monkeypatch):
    source = tmp_path / "cs_docling.json"
    source.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        pipeline, "load_document",
        lambda *_args, **_kwargs: (fixture_document(cs_fixture_grid(), CS_TEXT_ITEMS), source))
    payload = pipeline.process_prospectus(
        source, tmp_path / "cs_prospectus.json", semantic_doc_path=None, quiet=True)
    assert payload["pdf_sha256"] is None
    assert {c["source_anchored"] for c in payload["rag"]["semantic_chunks"]} == {False}
```

- [ ] **Step 2: Run and confirm the failures**

Expected: all six fail with `TypeError: build_payload() got an unexpected keyword argument 'pdf_sha256'` or `KeyError: 'pdf_sha256'`. (If Task 1 found that Phase C or D already passes the hash into `build_payload`, rename the keyword in these tests to match before running, and skip Step 3's helper.)

- [ ] **Step 3: Edit `pipeline.py`**

Imports: add `import hashlib` next to `import json`.

`build_payload` signature, add the keyword last:

```python
    repair_provider: SemanticRepairProvider | None = None,
    pdf_sha256: str | None = None,
) -> dict[str, Any]:
```

Replace lines 52-71 (the `verified` block) with:

```python
    verified = audit["status"] != "error"
    rejected_chunks: list[dict[str, Any]] = []
    if verified:
        prolog = generate_prolog_knowledge(metadata, courses, tracks, term_units)
        prolog["status"] = "verified"
        semantic_chunks = build_semantic_rag_chunks(
            metadata, courses, tracks, term_units,
            pdf_sha256=pdf_sha256,
            source_kind=document.source_kind,
            text_items=document.text_items,
            rejected=rejected_chunks,
        )
        hierarchical_chunks = build_hierarchical_rag_chunks(
            document, Path(input_path).name, pdf_sha256=pdf_sha256, rejected=rejected_chunks
        )
    else:
        prolog = {
            "status": "blocked",
            "reason": "audit status is error; institutional facts require review",
            "clauses": [],
            "relations": {
                "courses": [],
                "prerequisites": [],
                "standing_requirements": [],
                "elective_tracks": [],
            },
        }
        semantic_chunks = []
        hierarchical_chunks = []
```

If Phase C changed this block (for example it stopped embedding blocked Prolog), keep Phase C's `else` branch and only change the two `build_*` calls and the new `rejected_chunks` list.

In the payload dict: add `"pdf_sha256": pdf_sha256,` after `"source_path"`, and replace the `"rag"` entry with:

```python
        "rag": {
            "chunker_version": CHUNKER_VERSION,
            "token_count_method": TOKEN_COUNT_METHOD,
            "semantic_chunks": semantic_chunks,
            "hierarchical_chunks": hierarchical_chunks,
            "rejected_chunks": rejected_chunks,
        },
```

and add `"total_rejected_chunks": len(rejected_chunks),` after `"total_hierarchical_chunks"` in `quality_report`. Import the two constants: `from .chunking import CHUNKER_VERSION, TOKEN_COUNT_METHOD`.

Add the helper above `process_prospectus`:

```python
def _file_sha256(path: Path) -> str:
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()
```

In `process_prospectus`, after the `raw_cache_path` line (214) add:

```python
    pdf_sha256 = _file_sha256(input_path) if input_path.suffix.lower() == ".pdf" else None
```

and pass `pdf_sha256=pdf_sha256` in the `build_payload(...)` call (219-225). In the jsonl writer (249-252) change `jsonl_path.open("w", encoding="utf-8")` to `jsonl_path.open("w", encoding="utf-8", newline="\n")`.

**(D3)** For a Docling JSON input `pdf_sha256` stays `None`. Do not try to recover it from the JSON.

- [ ] **Step 4: Bump the schema version**

In `common.py:8` change `SCHEMA_VERSION` to the next minor of whatever Task 1 recorded (from `palsu-prospectus-v3.0` that is `palsu-prospectus-v3.1`; after earlier phases bumped it, one step further). Record in the progress file: "payload shape: new top-level `pdf_sha256`; `rag.semantic_chunks` and `rag.hierarchical_chunks` entries replace `id` with `chunk_id` and gain `chunker_version`, `content_review`, `pdf_sha256`, `source_anchored`, `source_text`, `source_spans`, `pages`, `table_indexes`, `cell_ids`, `content_hash`, `token_count`, `token_count_method`, `section_path`; new `rag.chunker_version`, `rag.token_count_method`, `rag.rejected_chunks`; new `quality_report.total_rejected_chunks`; elective options gain `source_item_id`."

- [ ] **Step 5: Run Phase E tests, full suite, self-test**

Expected: all pass, self-test 80/80. If `test_payload_rag_block_reports_chunker_and_rejections` fails on `rejected_chunks == []`, print the list and look at the reason: `prerequisite_not_in_source_text` on the CS fixture means a real course whose prerequisite words are not in its cells, which is a finding to report, not a reason to weaken the rule. Run `$env:TEMP`-style one-off to list them and record in the progress file; then decide with the controller.

- [ ] **Step 6: Update the progress file and commit**

```
git add backend/bintanong_tools/prospectus_extractor/pipeline.py backend/bintanong_tools/prospectus_extractor/common.py tests/test_prospectus_chunks.py plans/plan_current_progress/extractor_split_progress.md
git commit -m "feat: carry the PDF hash through the payload and emit source-linked chunks"
```

---



### Task 7: Regression: course fields unchanged on the 44 cached inputs

**Files:** no repository change. The comparer lives in `$env:TEMP\phaseE\course_fields_check.py` and is not added to Git. (It is adapted from the Phase A golden script, `git show 2dffe3d:scripts/prospectus_golden_check.py`, which compared whole payloads with run-to-run noise. Phase E needs a field-level comparison of old against new because the payload shape changes on purpose.)

- [ ] **Step 1: Write the comparer**

Create `$env:TEMP\phaseE\course_fields_check.py`:

```python
#!/usr/bin/env python3
"""Phase E regression: course fields and audit outcome unchanged between two code trees.

    python course_fields_check.py run ROOT OUT GOLDEN MAP     # one side
    python course_fields_check.py compare OLD_OUT NEW_OUT     # field-level diff
    python course_fields_check.py stats NEW_OUT               # Phase E chunk statistics
Run it under `uv run --project <repo>/backend --extra tools` so sys.executable has Docling.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

COURSE_KEYS = (
    "course_code", "course_title", "year_level", "semester", "term_index", "units",
    "prerequisites_raw", "prerequisites", "prerequisites_unresolved", "standing_requirements",
    "category", "is_elective", "elective_group",
)


def view(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "courses": [{k: c.get(k) for k in COURSE_KEYS} for c in data["courses"]],
        "tracks": [
            {"group": t["group"], "slots": t.get("curriculum_slots"),
             "options": [{"course_code": o["course_code"], "course_title": o["course_title"]} for o in t["options"]]}
            for t in data["elective_tracks"]
        ],
        "audit": data["audit"]["status"],
        "errors": data["audit"]["errors"],
    }


def run(root: Path, out: Path, golden: Path, semantic_map: Path) -> None:
    sources = sorted(golden.rglob("*_docling.json"))
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8")
    for number, source in enumerate(sources, 1):
        target = out / f"{number:02d}"
        target.mkdir(parents=True, exist_ok=True)
        (target / "source.txt").write_text(str(source), encoding="utf-8")
        done = subprocess.run(
            [sys.executable, "-m", "backend.bintanong_tools.prospectus_extractor", "-i", str(source),
             "-o", str(target / "candidate.json"), "--export-all", "--device", "cpu",
             "--semantic-doc", str(semantic_map)],
            cwd=root, env=env, capture_output=True,
        )
        (target / "exit.txt").write_text(str(done.returncode), encoding="utf-8")
        print(f"{number}/{len(sources)} exit={done.returncode} {source.name}", flush=True)


def compare(old: Path, new: Path) -> int:
    failures = 0
    folders = sorted(p.name for p in old.iterdir() if p.is_dir())
    for name in folders:
        a, b = old / name / "candidate.json", new / name / "candidate.json"
        problems = []
        if (old / name / "exit.txt").read_text() != (new / name / "exit.txt").read_text():
            problems.append("exit code differs")
        if a.exists() != b.exists():
            problems.append(f"candidate.json exists old={a.exists()} new={b.exists()}")
        elif a.exists():
            left, right = view(a), view(b)
            for key in left:
                if left[key] != right[key]:
                    problems.append(f"{key} differs")
            for i, (x, y) in enumerate(zip(left["courses"], right["courses"])):
                if x != y:
                    problems.append(f"first course diff #{i}: {x['course_code']} -> {y['course_code']}")
                    break
        failures += bool(problems)
        print(f"{name} {'FAIL' if problems else 'ok'} {(old / name / 'source.txt').read_text()[-60:]}")
        for problem in problems:
            print(f"    {problem}")
    print(f"{len(folders) - failures}/{len(folders)} identical")
    return 1 if failures else 0


def stats(new: Path) -> None:
    kinds, reasons, tokens, anchored = Counter(), Counter(), [], Counter()
    produced = 0
    for path in sorted(new.glob("*/candidate.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rag = data["rag"]
        chunks = rag["semantic_chunks"] + rag["hierarchical_chunks"]
        produced += bool(chunks)
        for chunk in chunks:
            kinds[chunk["chunk_type"]] += 1
            tokens.append((chunk["token_count"], chunk["chunk_type"]))
            anchored[chunk["source_anchored"]] += 1
            assert chunk["cell_ids"] or chunk["chunk_type"].startswith("hierarchical") or chunk["chunk_type"] == "program_overview"
        for r in rag["rejected_chunks"]:
            reasons[(r["chunk_type"], r["reason"])] += 1
    print("inputs with chunks:", produced)
    print("chunks by type:", dict(kinds))
    print("rejected:", dict(reasons))
    print("source_anchored:", dict(anchored))
    for kind in sorted(kinds):
        values = sorted(t for t, k in tokens if k == kind)
        print(f"{kind}: n={len(values)} min={values[0]} median={values[len(values)//2]} max={values[-1]}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "run":
        run(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
    elif mode == "compare":
        raise SystemExit(compare(Path(sys.argv[2]), Path(sys.argv[3])))
    elif mode == "stats":
        stats(Path(sys.argv[2]))
```

- [ ] **Step 2: Prove the comparer can fail**

Make a one-input smoke directory and compare it with itself and with a tampered copy:

```
$t = "$env:TEMP\phaseE"; New-Item -ItemType Directory -Force $t | Out-Null
$repo = (Get-Location).Path
$golden = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task2b_standing_isolated_2026-09-29'
$map = 'E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\PalSU Undergraduate Prospectus Website Dump\Tiniguiban - Main\palsu_main_undergrad_program_college_meaning.md'
```

Run the `run` mode once with the new tree on a single-input folder (copy one `*_docling.json` into `$t\one`), then `compare` that output with itself (expect `1/1 identical`), then edit one `course_title` in a copy of `candidate.json` and compare again (expect `FAIL` with `courses differs`). Record both results.

- [ ] **Step 3: Create the old-tree worktree**

```
git worktree add "$env:TEMP\phaseE\old" <phase-start-commit>
```

`<phase-start-commit>` is the `dev` commit recorded in Task 1 step 1 (the base of this branch). The worktree has no `.venv`; use the repo's own: all runs go through `uv run --project $repo\backend`, with `cwd` set to the tree being tested, so `python -m backend.bintanong_tools.prospectus_extractor` resolves from that tree's `backend/` folder.

- [ ] **Step 4: Launch both sweeps detached**

Each sweep takes roughly 90 minutes (44 Docling-JSON runs). Tool calls die at 10 minutes, so start them with `Start-Process` and poll the log files:

```
$cmd = { param($root,$out,$log) uv run --project "$repo\backend" --extra tools --extra dev python "$t\course_fields_check.py" run $root $out $golden $map *> $log }
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"cd '$t\old'; uv run --project '$repo\backend' --extra tools --extra dev python '$t\course_fields_check.py' run '$t\old' '$t\out_old' '$golden' '$map' *> '$t\old.log'"
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"cd '$repo'; uv run --project '$repo\backend' --extra tools --extra dev python '$t\course_fields_check.py' run '$repo' '$t\out_new' '$golden' '$map' *> '$t\new.log'"
```

(Drop the unused `$cmd` line; it is shown only to name the three arguments.) Poll with `Get-Content "$t\new.log" -Tail 3` until the last line reads `44/44 exit=...`.

- [ ] **Step 5: Compare**

Run: `uv run --project backend --extra tools python "$env:TEMP\phaseE\course_fields_check.py" compare "$env:TEMP\phaseE\out_old" "$env:TEMP\phaseE\out_new"`
Expected final line: `44/44 identical`. Any `FAIL` is a real change in a course field, audit status or elective option. Use superpowers:systematic-debugging; the likely culprit is the `parse_elective_tracks` edit in Task 4, which must produce the same `options` apart from `source_item_id`. Do not continue past a FAIL.

- [ ] **Step 6: Chunk statistics**

Run: `... course_fields_check.py stats "$env:TEMP\phaseE\out_new"`
Record in the progress file: inputs with chunks (expect well under 44, because error audits emit none), chunks by type, rejected counts by reason, token min/median/max per type, anchored counts (expect `False` for all, since every input is cached Docling JSON). Pass criteria: no `course` or `term_schedule` chunk above 480 estimated tokens; rejected `course` chunks with reason `prerequisite_not_in_source_text` or `no_valid_source_cells` should be 0 on the real inputs. If not 0, list the codes and stop for the controller; do not loosen `course_rejection`. Expected `hierarchical_layout` rejections for over-cap table chunks; record their count.

- [ ] **Step 7: Clean up the worktree and commit the progress note**

```
git worktree remove --force "$env:TEMP\phaseE\old"
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: record Phase E regression and chunk statistics"
```

---



### Task 8: Gate, optional token calibration, Codex review

**Files:** `plans/plan_current_progress/extractor_split_progress.md`; scratch scripts in `$env:TEMP\phaseE`.

- [ ] **Step 1: Resolve every chunk back to cells (automatic part of the gate)**

Create `$env:TEMP\phaseE\chunk_gate.py`:

```python
"""For each chunk in one candidate run, confirm its cell IDs, text and pages exist in the evidence."""
import json
import sys
from pathlib import Path

from backend.bintanong_tools.prospectus_extractor.loader import load_document

run_dir = Path(sys.argv[1])
source = Path((run_dir / "source.txt").read_text(encoding="utf-8"))
payload = json.loads((run_dir / "candidate.json").read_text(encoding="utf-8"))
document, _ = load_document(source, device="cpu", force_reconvert=False)
cells = document.all_cells()
checked = 0
for chunk in payload["rag"]["semantic_chunks"]:
    for span in chunk["source_spans"]:
        if span["locator"]["kind"] != "table_cells":
            continue
        for cell_id in span["locator"]["cell_ids"]:
            cell = cells[cell_id]  # KeyError means the chunk points at a cell that does not exist
            assert (cell.bbox.page if cell.bbox else None) == span["page"], (chunk["chunk_id"], cell_id)
            assert cell.text in span["text"], (chunk["chunk_id"], cell_id)
        checked += 1
print("spans resolved:", checked, "chunks:", len(payload["rag"]["semantic_chunks"]))
for chunk in payload["rag"]["semantic_chunks"]:
    if chunk["chunk_type"] == "course" and ("Prerequisites**: None" not in chunk["text"]):
        print(chunk["chunk_id"][:12], chunk["course_code"], "p", chunk["pages"], chunk["cell_ids"], "|", chunk["source_text"])
```

Run it for each output folder from Task 7 whose `candidate.json` has chunks (find them with `Get-ChildItem $env:TEMP\phaseE\out_new -Recurse -Filter candidate.json | Where-Object { (Get-Content $_ -Raw | ConvertFrom-Json).rag.semantic_chunks.Count -gt 0 }`). Expected: `spans resolved: N` with no assertion error for every one.

- [ ] **Step 2: Human check against the PDF (manual part of the gate)**

The pilot PDFs are BSCS and Architecture. Their audits may be `error` after this phase (BSA was `error` on 3 October with 77 courses and no chunks by design), in which case their gate result is "no chunks emitted, blocked by audit, owned by the parser repairs"; record that and do not force it. For the non-error pilot (`ABPhilStud`, `warn`), take the printed list from step 1, pick every course that prints a prerequisite or standing condition (up to 10), open the original PDF at the printed page, and confirm the course row text equals `source_text` and the prerequisite text is in it. Record each checked chunk ID prefix, page and verdict in the progress file. Any mismatch fails the gate.

- [ ] **Step 3: Optional token calibration (Decision D1)**

Only if `$env:MODELS_DIR\SEA-LION-E5-Embedding-600M\tokenizer.json` exists on the executor's machine (it does not on the planning machine):

```
uv run --project backend --extra tools python -c "
import json,sys,os
from pathlib import Path
from tokenizers import Tokenizer
tok = Tokenizer.from_file(str(Path(os.environ['MODELS_DIR'])/'SEA-LION-E5-Embedding-600M'/'tokenizer.json'))
worst = 10.0
for p in Path(sys.argv[1]).glob('*/candidate.json'):
    for c in json.loads(p.read_text(encoding='utf-8'))['rag']['semantic_chunks']:
        exact = len(tok.encode(c['text']).ids)
        worst = min(worst, c['token_count'] / max(exact, 1))
print('smallest estimate/exact ratio:', round(worst, 2))
" "$env:TEMP\phaseE\out_new"
```

Pass: ratio at least 1.0 (the estimate never under-counts). If under 1.0, raise the multipliers in `estimate_tokens`, change `TOKEN_COUNT_METHOD` to `estimate-v2`, bump `CHUNKER_VERSION` to `palsu-chunker-v2` (split points change, so content and IDs change), update the tests that mention the old constants, and rerun Task 7 step 6. If the file does not exist, write "tokenizer not available; exact counting is Phase 3" in the progress file.

- [ ] **Step 4: Codex gate (read-only, detached, about 15 minutes)**

```
$prompt = 'Review branch feature/prospectus-phase-e-rag-provenance against dev in this repo. Claim: every chunk from backend/bintanong_tools/prospectus_extractor/rag.py carries pdf_sha256, pages, table indexes and cell IDs from the extractor evidence; chunk_id is stable for one PDF and different for another edition; no chunk is built from a course without valid source cells; summaries list all contributing pages and never a single fabricated page; the 512-token cap including a 32-token reserve is enforced; no embedding call or vector write was added; no course field changed. Try to break each claim: find a path where provenance page is None but a page is invented, where the ID depends on a timestamp or dict ordering, where a rejected course still appears in a summary, where text can exceed the cap, or where Windows line endings change an ID or hash. Do not modify files. Report findings with file and line.'
Start-Process pwsh -WindowStyle Hidden -ArgumentList '-NoProfile','-Command',"codex exec --sandbox read-only -o '$env:TEMP\phaseE\codex_e.txt' '$prompt'"
```

Poll `Get-Item "$env:TEMP\phaseE\codex_e.txt"` until it exists. Record the findings in the progress file. Fix each confirmed finding with a failing test first; note and skip unconfirmed ones. If Codex is rate-limited or errors, record that and continue.

- [ ] **Step 5: Final run and hand-off note**

Run the full suite and the self-test. Expected: all green, 80/80. Append to the progress file: test counts, the `44/44 identical` line, the stats, the gate verdicts, Codex findings, the new `SCHEMA_VERSION`, and "next: Phase F". Do not merge into `dev` and do not push; ask the user (superpowers:finishing-a-development-branch).

```
git add plans/plan_current_progress/extractor_split_progress.md
git commit -m "docs: record Phase E gate results"
```

**Phase E gate:** `tests/test_prospectus_chunks.py` green; `44/44 identical` course fields; every chunk of every non-error input resolves to existing cells with matching text and page; every checked prerequisite or standing chunk of the non-error pilot matches the PDF by eye; no `course` or `term_schedule` chunk exceeds the cap; Codex findings resolved or recorded. No embedding call and no vector write exist in the diff (check with `git diff dev --stat` and `Select-String -Path backend\bintanong_tools\prospectus_extractor\*.py -Pattern "embed|encode|vector"`, expecting nothing new).

---

## Self-review

**Spec coverage.**
- `pdf_sha256` on every chunk: `assemble_chunk` sets it; dependency and D3 explain the missing-hash case (Tasks 2, 6).
- Page, table index, cell IDs, source text separate from summary: `pages`, `table_indexes`, `cell_ids`, `source_text` vs `text` (Tasks 2, 3).
- Term and elective summaries list all spans, no fabricated page: Task 4 tests; course and summary pages come from per-cell pages, never from `provenance["page"]` (Task 3).
- Chunk ID from hash, source locator, content hash and chunker version, replacing `<code>::course`: `make_chunk_id`; `id` removed (Tasks 2, 3).
- Token cap 512 with 300 to 400 target; counter decision: D1, D5, Tasks 2 and 8.
- `content_review: pending`: every chunk (Task 2).
- Tests first: two editions, same PDF with different timestamps, multi-page summary, prerequisite without source cells, token cap: Tasks 3, 4, 6.
- No embedding or vector write: stated and checked in the gate.
- Required plan items: start check (Task 1), conditional AST-gate deletion (Task 1), schema bump with description (Task 6), regression on 44 inputs with a detached run and a recovered, adapted comparer (Task 7), progress-file updates (every task), Codex gate (Task 8), Decisions section, OCR room (`source_kind`, `ocr_confidence`), commit rules.

**Placeholder scan.** No TBD or "handle edge cases". Two places depend on facts that only exist at execution time and say how to resolve them: the next `SCHEMA_VERSION` value and whether Phase C or D already provide the hash (Task 1 step 3 records both; Task 6 branches on it).

**Type consistency.** `make_span`, `spans_from_cells`, `spans_from_text_items`, `locator_key`, `make_chunk_id`, `course_rejection`, `pack_items`, `assemble_chunk`, `fits_cap`, `estimate_tokens`, `CHUNKER_VERSION`, `TOKEN_*` are defined in Task 2 and used under the same names in Tasks 3 to 6. Rejection records have the shape `{"chunk_type", "label", "reason"}` plus `token_count` for over-cap, in code and tests. `build_semantic_rag_chunks(..., *, pdf_sha256, source_kind, text_items, rejected)` and `build_hierarchical_rag_chunks(document, source_name, *, pdf_sha256, rejected)` match the pipeline calls. The `rag.py` code uses `"aggregate"` as the resolution method for summary spans; no test depends on it.

**Known limits, stated rather than hidden.**
- The prerequisite check is word containment (every alphanumeric token of `prerequisites_raw` appears in the cells), not order. It stops a prerequisite with no matching source; it does not prove the words came from the prerequisite column.
- Course `source_cells` include the year and semester banner cell, so `source_text` and the span carry that banner text.
- Overview chunks carry `unsourced_fields` because program, college and school year come from the file name, semantic map and document text, not from table cells.
- Elective options split across parts share their slot-course spans.
- Without a PDF (cached Docling JSON) chunks are unanchored and must not be loaded as institutional chunks.
- The review-corrected projection (draft Task 6, last bullet) cannot be used yet because the review GUI does not exist; chunks are built from extractor output and labelled `content_review: pending`.
