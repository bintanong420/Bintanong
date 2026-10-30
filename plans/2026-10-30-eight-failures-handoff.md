---
title: Handoff - common-query readiness for the student sessions (new developer machine)
date: 2026-10-30
worktree: p12
branch: p12-evaluation-harness
head_commit: see `git log -1` (handoff commit follows 2fc829a)
status: open
---

# Handoff: common-query readiness for the student sessions

Owner (30 Oct 2026): student evaluation next week by screen share (not deployed), about two students per program,
mainly College of Sciences (CoS: prior questionnaire evidence of the guidance problem) plus a few other colleges.
Priority: answer the common queries. RAGAS is planned later, not now. A new developer (32 GB RAM, any coding agent)
takes over the test runs. Last full snapshot of this file (eight-failures handoff): `1fd0319`.

Read first, in order: repository `AGENTS.md` (binding rules for every agent), `.agents/skills/bintanong-handoff-reminder`
and `bintanong-phase-handoff`, [current progress](plan_current_progress/current_progress.md), the
[owner-decisions ledger](owner-decisions-ledger.md) (30 Oct entries). Never re-ask a decision recorded there.

## State at handoff (all local commits, verified on the owner's machine)

- 50-case benchmark: 49/50 on `ac867c6` (development data; frozen Phase 12 score stays 38/50; single runs, +/-1).
- New 97-case common-query set: 77/97 on `41dfd00` (general 20/33, CoS 43/48, other colleges 14/16). Fixed since
  and checked in live subsets only: Charter host-reply crash (`1468505`), CoS Taglish term listings (`754ee9a`),
  Taglish discipline words (`48ff8d6`). The full 97 and 50 have NOT been rerun on HEAD (owner machine ran out of RAM).
- Fix commits today, each test-first with an offline dry run on recorded calls: `f08712d` printed-exception repair,
  `12b35d1` named sanctions row, `ac867c6` heading-based topic switch, `41dfd00` verbatim printed sentence in
  Taglish, `1468505` held malformed records never host-answered, `754ee9a` ambiguous selection keeps structured
  checks, `48ff8d6` reviewed Filipino penalty words (owner list, `docs/evaluation/accepted-input-forms.md`).
- Default `pytest tests/` now skips the offline ingestion-tool tests (prospectus/review GUI/OCR, 1,796 cases);
  `--include-ingestion` runs them. Related suites passed (1,714); the full default suite has not run on HEAD.
- Benchmark checker fix: hosted/gate/common runners strip `[ev-...]` IDs before phrase matching (hex digits had
  matched number expectations). The local frozen runner is unchanged on purpose.

## New machine setup (keep the exact folder layout: `C:\Coding-projects\bintanong_workspace\...`)

The config/pin hold absolute paths and are hash-checked; editing them changes their hashes and startup refuses.

1. Code: clone/checkout `p12-evaluation-harness` into `worktrees\Bintanong\p12` (owner pushes the local commits first).
2. Copy these ignored files to the same paths (startup verifies each):
   - `audit-evidence\p12-hosted-560-activation-20261030\`: `hosted-research-api-config.json`,
     `hosted-research-pin.json`, `start_hosted_research_api.py`
   - `audit-evidence\p11-local-documents-20261029\runtime-package\`: all 8 files (`runtime-seal.json`,
     `draft-chunks.json`, `draft-embedding-records.jsonl`, `draft-embedding-manifest.json`,
     `draft-source-versions.json`, `draft-source-review-register.json`, `draft-subject-catalogue.json`,
     `subject-context-budgets.json`)
   - `audit-evidence\p05-document-evidence-calibration-20261016\encoder-verification.json`
   - Runners and cases: `audit-evidence\p12-common-queries-20261030\` (`run_common.py`, `cases.json`,
     `build_common_cases.py`, `all-curricula.json`, `dryrun_*.py`), `audit-evidence\p12-hosted-regression-20261030\`
     (`run_hosted_regression.py`, `cases.json`), `audit-evidence\p11-simple-gate-20261028\cases.json`.
     Recorded `run-*` folders are optional (only for offline dry runs).
3. Env (owner sends privately; never commit): `p12\.env` with `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `MODELS_DIR`
   only (no service-role key or DB password); `p12\frontend\.env.local` as the owner has it.
4. Models at `C:\Coding-projects\bintanong_workspace\MODELS` (`GEMMA_4_E4B\gemma-4-E4B-it-UD-Q4_K_XL.gguf`,
   `SEA-LION-E5-Embedding-600M`); encoder bytes must match `encoder-verification.json`, else copy the owner's folder.
   Never download or duplicate weights inside Git.
5. Model server (NVIDIA GPU, ~6 GB VRAM), same image/arguments as the owner's container:
   ```powershell
   docker run -d --name bintanong-model --gpus all -p 127.0.0.1:18088:8080 -v C:/Coding-projects/bintanong_workspace/MODELS:/models ghcr.io/ggml-org/llama.cpp@sha256:f66a5229a3e0586339d16155e9fe09c37834d7a7f4134bbdee7360b5a1f2546d --model /models/GEMMA_4_E4B/gemma-4-E4B-it-UD-Q4_K_XL.gguf --host 0.0.0.0 --port 8080 --ctx-size 8192 --parallel 1 --threads 8 --n-predict 768 --n-gpu-layers auto --fit-target 512 --log-verbosity 4 --no-webui --jinja
   ```
   Ready when `http://127.0.0.1:18088/health` returns `{"status":"ok"}`.
6. Python 3.13 environment from `backend/pyproject.toml` + `backend/uv.lock` (`api` and `embedding` extras, pytest,
   pytest-asyncio). Do not change the lock or dependencies; the owner authorizes the environment build on this
   machine. Below, `$PY` is that interpreter. Frontend: `npm ci` in `p12\frontend` (lockfile unchanged).
7. Local Supabase (`supabase start` from p12, container `supabase_db_Bintanong`) only for the DB test files.

## Runs to do, in order (record commands and results; never claim a check that did not run)

All runners: from `p12`, `$env:PYTHONUTF8=1`, `$PY -X utf8 <runner>`; `GATE_SUFFIX` must be new per run; they refuse a
dirty `backend/`. Outputs land in `run-<commit><suffix>\` (per-case call-N request/result, `results.jsonl`).

1. Startup: run the backend (`start_hosted_research_api.py`, prints `app constructed` in ~80-110 s) and frontend
   (`node_modules\.bin\next dev -p 3216`); ask one question in the browser at http://127.0.0.1:3216. Stop both after.
2. Full default suite, local DB up: `$PY -X utf8 -m pytest -p no:cacheprovider --basetemp=<ignored dir> tests/`
   (expect about 5,576 collected, 1,796 deselected). Then once with `--include-ingestion`.
3. Common set (97): `$PY -X utf8 ..\..\..\audit-evidence\p12-common-queries-20261030\run_common.py`, suffix `-full1`.
   Baseline to beat: 77/97 on `41dfd00` (`run-41dfd00-first`). Report by group (general/CoS/other).
4. 50-case hosted regression: `run_hosted_regression.py`, suffix `-full1`. Baseline 49/50 (`run-ac867c6-claude-full`).
5. 91-case gate on hosted: `run_common.py` with `$env:CASES_FILE` = `...\p11-simple-gate-20261028\cases.json`.
   Last scored 77/91 on the older local package (28 Oct); treat this run as the new baseline.
6. Repeat 3-4 once more (second run) to separate nondeterminism (seen: the router's raw choice differs run to run).

## Open failures (from the 77/97 run; recheck after step 3)

| Case | Got | First check |
| --- | --- | --- |
| g-absent-casual-taglish "umabsent ako kahapon..." | sickness topic, no excuse slip | topic choice vs handbook absence clause |
| g-goodmoral-req-casual-en | FAQ topic, missing Student ID / Official Receipt | Charter good-moral service vs FAQ |
| g-honors-casual-en "latin honors" | honors topic, missing two years / 75% | which honors claim was drafted |
| g-section-casual-taglish | answered, missing "misadvising" | whole-procedure coverage |
| g-gradres-casual-taglish "ilang taon... maka graduate" | routed structured, clarified | document vs structured split |
| fee-certification-taglish / g-certgrades-fee-casual-en | insufficient_evidence after `1468505` | held record quote vs fee part; may need an owner choice |
| g-transfer-fee-casual-taglish | clarification_needed | owner F4 rule (leaving vs transferring in) may make this correct |
| bshm-hotel-term-1-1-en, bshm-hotel-prereq-taglish | clarification_needed, structured | "Hospitality Management" names two BSHM curricula |

## Rules for any change

Test-first with synthetic fixtures (no institutional data in tracked tests); RED for the expected reason before
production code. Prefer narrow deterministic host guards; prompt-only wording regressed other cases here (1 gain,
3 losses) and was reverted. Dry-run every guard offline over recorded `call-N-request/result.json` (menus and cards
are inside) before a live run; the `dryrun_*.py` scripts show the pattern. Never weaken accuracy, source-gap, scope,
privacy or unknown-versus-unmet guards to pass a keyword. Source-content and wording choices go to the owner (show
the exact printed text). Small Conventional Commits, no AI attribution trailers, no push or merge unless the owner
asks. Update current progress after material work; keep this file a compact snapshot.

## Next action

Set up the machine (steps 1-7), then run steps 1-6 above and report scores per group with the failing cases;
then fix the open failures in the order CoS > general common topics > other colleges.
