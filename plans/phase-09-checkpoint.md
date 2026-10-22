---
artifact: phase-checkpoint
phase: 9
status: in_progress
sequence: 130
plan: plans/phase-09-generation-validation-plan.md
head_commit: 94c3d62
working_tree: clean
updated_at: 2026-10-22T23:30:00+08:00
---

# Phase 09 checkpoint - hosted Supabase done; program prerequisite reviews started

Last full snapshot before this replacement: `94c3d62:plans/phase-09-checkpoint.md` (use `git show`).
Owner asked for this handoff on 22 Oct so the session can be cleared; resume from here.

## Completed Tasks

- Earlier Phase 09 work (generation, per-part answers, real-data roster runs 1-6, style floor
  `e53153b`): see [roster results](2026-10-21-real-data-roster-results.md) and the
  [exit reassessment](2026-10-22-phase09-exit-reassessment.md). Prior closeout handoff
  `a31ac32:plans/phase-09-handoff.md` is history; owner reopened Phase 09 for Supabase.
- Hosted Supabase ([plan](2026-10-22-hosted-supabase-integration-plan.md)), all done 22 Oct:
  7 Phase 05 migrations + research-release migration `20261022090000` (`115d218`) on hosted
  project `jyrudbiuajahsucsorco` (14 migrations, versions = repo files, advisors clean); real
  undergraduate document selection loaded and active as research release
  `p09-research-selected-20261022` (5 sources, 19 chunks; approval stays not_requested);
  runtime reads it via `HostedReleaseStorage` (`b4616ab`, 39/39 equivalence); roster runs 7-8
  on hosted: 17/63 answered, 0 wrong after the conflict-notice fix (`f77b952`).
- Program prerequisite reviews (owner: Phase 06 only delivered BSCS; review the rest).
  BS Architecture: [review 01](2026-10-22-bsa-prerequisite-review-01.md) read from the original
  page, owner decisions 1-6 recorded, 77-course reviewed ledger authored and checked with real
  Prolog (7/9 as expected; 2 conservative unknowns explained there).

## Current Task

Program-by-program prerequisite review and loading. BS Architecture ledger is authored
(workspace `audit-evidence/p09-bsa-review-20261022/`: `ledger.json`, `author_bsa.py`,
`check_bsa.py`, `bsa-p1.png`). Not yet loaded into Supabase or wired into the runtime.

## Repository State

Branch `feat/p09-generation-validation`, HEAD `94c3d62`, clean, nothing pushed. Hosted keys in
the worktree's git-ignored `.env` (owner-run script). Model container `bintanong-p09-cuda-latency`
(127.0.0.1:18088; `docker restart` before long runs; start Docker Desktop first if `docker ps` fails).

## Verification Evidence

- Full suite at `f77b952`: 6139 passed, 6 skipped, 0 failed (1061 s); later commits docs only.
- Storage DB regression with research release: 182 passed, 916 subtests.
- Commands: test Python `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider <tests> --basetemp=<audit-evidence dir>`;
  DB tests use local Docker `supabase_db_Bintanong` (set `BINTANONG_STORAGE_EVIDENCE_DIR`).
- Roster runner: workspace `audit-evidence/p09-real-data-20261021/roster.py <outdir>` (`HOSTED=1`
  for Supabase retrieval, `ONLY=id1,id2` to filter); record a protocol before counted runs.

## Versions and Digests

BSA PDF SHA256 `72dad4a0384f82228d63c8926e4ae8a1eb14a33497c9952e0f60782083e82666`; BSA ledger
SHA256 `a5f4e2205d1aae974dbbc7a4ac23ab7c8baf2d2d9050efebdf69982578c57041`. Router v14, ctx 8192,
out 768, temp 0, seed 0 unchanged. Model weights `C:/Coding-projects/bintanong_workspace/MODELS`.

## Decisions

- Research release kind: owner authorization lives on the release; sources never marked approved.
- BS Architecture decisions 1-6 (22 Oct): comma = all_of; short codes TOA-1/AR-INT/BT-2/BT-5/
  Ar RM 1 map to full codes; Arc 1 = Ar-CC 1; MATH 19-20 = Math 19 and Math 20; D-10/L, PP-4,
  D-7 kept as printed (PP-4, D-7 = source gaps, unknown); "4th Year Standing" unknown unless the
  student gives their year (chatbot may ask). Blank cells stay unknown.
- Owner cannot open files: always show program, course code, title and printed text inline.

## Known Failures or Blockers

- Compiler withholds a whole rule if any node is unresolved (BSA Ar-RM 2, Ar-CC 2, SP-3,
  BM/AA-2 give unknown even when a known prerequisite failed). Owner decision pending.
- Only BSCS + BSA have reviewed prerequisites; about 35 programs remain (39 PDFs in
  `Bintanong/dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/`).
- Course facts/rules are not in Supabase yet (tables `programs`, `curriculum_versions`, `courses`,
  `course_aliases`, `policy_rules`, `rule_source_spans` exist, empty).

## Next Action

Ask the owner which first (one question): (a) next program review, e.g. another college's
prospectus, following the BSA method (render page with pypdfium2, read cells from the image,
compare with any developer CSV, show questions inline with program/course/title/printed text,
record decisions, author with an `author_<program>.py` like `author_bsa.py`, check with real
Prolog); (b) generic Supabase loader for reviewed course facts/rules (BSCS + BSA) with the Prolog
bundle generated from the database and checked equal to the current bundles; (c) the compiler
partial-rule decision above. The developer's CSV for BSA was
`audit-evidence/cad_review_simple(AutoRecovered).csv`; ask whether CSVs exist for other colleges.

## Do Not Repeat

Hosted migrations/load (done; hosted is not empty - the load script refuses a non-empty project),
BSA page reading and decisions, roster runs 7-8, style floor, per-part observation, task-first
trial, checker diagnosis, source/benchmark reviews, asset setup.
