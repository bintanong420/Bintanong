# Task 6 bounded draft evidence
Base/unchanged HEAD: c08846154c1d697887252f9fc70eb613d09d726d
No commit or staging performed. Product frozen for root acceptance: five new files in frozen_files.json. Protected-path diff empty. Formal phase is not started.

All test invocations used:
Set-Location 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_HUB_DISABLE_TELEMETRY='1'
$ev='E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\phase2_ocr_gate'
py -3.13 -B -m pytest -q 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_ocr_run.py' 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010\tests\test_ocr_gate.py' -p no:cacheprovider --basetemp "$ev\bt_NAME" *> "$ev\NAME.log"
The native Python exit was captured immediately in $testExit=$LASTEXITCODE; logs were then read; wrapper shell exit0 is not the test verdict.

Invocations:
NAME red_01, actual basetemp bt_red_01: 35 errors, native exit1, modules absent (initial discovery, not behavior RED).
NAME red_02, actual basetemp bt_red_02: 35 failed, native exit1, callable stubs raise NotImplementedError (behavior RED).
NAME green_01, actual basetemp bt_green_01: 33 passed/2 failed, 21.11s, native exit1. Native PdfPage lacks __enter__; empty-register contract refuses earlier than intended missing-version fixture. No protected edit.
NAME green_02, actual basetemp bt_green_02: 35 passed, 20.62s, native exit0. Correct installed close APIs via closing; unregistered-source fixture now valid different-byte register.

Additional exact Python commands (same worktree location):
py -3.13 -B -c "import pypdfium2; print('PdfPage.close',hasattr(pypdfium2.PdfPage,'close')); print('PdfBitmap.close',hasattr(pypdfium2.PdfBitmap,'close'))"
Exit0; both True.
py -3.13 -B -c "from pathlib import Path; from backend.bintanong_tools.document_ingest import ocr_run,ocr_gate; root=Path(r'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010'); assert all(root in Path(m.__file__).resolve().parents for m in (ocr_run,ocr_gate)); print('worktree imports verified')"
Exit0; saved imports.log.
git diff --check
Exit0; no output (new files remain untracked).
git diff --stat c08846154c1d697887252f9fc70eb613d09d726d -- backend/bintanong_contracts backend/bintanong_tools/prospectus_extractor backend/bintanong_tools/ocr_bench backend/bintanong_api backend/bintanong_embedding backend/pyproject.toml backend/uv.lock uv.lock .gitignore
Exit0; zero output.
git status --short
Exit0; exactly the five untracked Task6 files.
git rev-parse HEAD
Exit0; c08846154c1d697887252f9fc70eb613d09d726d.

Interfaces/decision: docs/decisions/phase-02-ocr-gate.md. Source hashes are synthetic_source_hashes.json; product hashes frozen_files.json. Both external, private evidence only. No institutional original was processed.

Rulings: preparation-only Task6 callable core, no gratuitous CLI; full suite/mutations/manual corpus expressly deferred. Parent instructions supersede markdown template's self-review/automatic commit/uv invocation. No self-review verdict. RapidOCR initialization is NOT RUN until local-model-only behavior can be verified. Line position matching is conservatively strict; annotation completeness, human identity and timing are trusted declarations rather than authenticated facts.
NOT RUN: actual engines/GPU/photo/corpus, institutional certification, approximately4000 broad suite, mutation campaign, Docker/API/phase exit.

## Local commit after explicit root acceptance
Root gate: 51 passed, 20.79s, native exit0 (Task6 files plus pending-register tests); root_focused.log and root_acceptance_exit.json recorded by root. Frozen product hashes rechecked unchanged. Root explicitly authorized local commit.
Exact staging: git add -- backend/bintanong_tools/document_ingest/ocr_gate.py backend/bintanong_tools/document_ingest/ocr_run.py docs/decisions/phase-02-ocr-gate.md tests/test_ocr_gate.py tests/test_ocr_run.py
Staged names match exact allowlist; git diff --cached --check exit0.
Commit: git commit -m 'feat(tools): add draft OCR runner and manual reference gate'; exit0.
SHA: 7fe26c07fc5338dfeaae874438d8a802ae4ad774
Post-commit git status --short empty; no attribution. task6_commit.json holds SHA/staged paths/status. No product edits, owner writes, push, merge or new verification batch.
