---
artifact: phase-checkpoint
phase: 9
status: in_progress
sequence: 146
plan: plans/phase-09-generation-validation-plan.md
head_commit: 6dad1af
working_tree: clean
updated_at: 2026-10-23T12:00:00+08:00
---

# Phase 09 checkpoint - hosted Supabase done; program prerequisite reviews (BSA, BS Criminology)

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
- BS Criminology: [review 01](2026-10-22-crim-prerequisite-review-01.md) read from the original
  page; owner decisions 1-3 (co-requisite = passed or same term; "All major courses from 1st to 3rd
  year" kept as printed, unknown; Forensic 5 / PATH Fit-DEFTAC 2 mapped); 65-course ledger authored,
  real Prolog 12/12 as expected.
- Engine fix (owner: fix for accuracy): affected-course listing now follows co-requisite links
  (`781c9a2`, [record](2026-10-23-corequisite-dependency-fix.md)); relation label
  `potential_prerequisite_or_corequisite_dependency`. CDI 4 -> CDI 5..CDI 11.
- Partial-rule decision (owner approved 23 Oct; `e4bd8bd`, [record](2026-10-23-partial-rule-decision.md)):
  reviewed rules export known parts with unknown leaves; all_of known failure -> ineligible,
  any_of satisfied alternative -> eligible. BSA real checks now 9/9; Criminology 12/12.
- BS Information Technology: [review 01](2026-10-23-bsit-prerequisite-review-01.md) read from the
  original page (no developer CSV); owner decisions 1-2 (IT 1/L -> IT 1; same rules as BSA/Crim);
  53-course ledger authored, real Prolog 12/12.
- Program reviews scaled (owner standing approval 23 Oct for repeated scenarios, recorded in
  `plans/owner-decisions-ledger.md`): shared scripts in workspace `audit-evidence/p09-program-reviews/`
  (`draft_program.py` draft from drawn table rules; `author_program.py <spec.json>` authors + real Prolog
  checks; `record.py` writes the dated review). College of Sciences complete: BSIT, BS Environmental
  Science, BS Biology (Med Bio), BS Marine Biology (2022-2023), full old and proposed BSCS (Phase 06
  readings reproduced exactly). New owner rules: visible printed text only (clipped native text ignored),
  semicolon = comma, obvious one-character typos map to the single match.
- 23 Oct: AB Communication reviewed (shorthand/range/duplicate-code owner rules); authoring keeps
  repeated printed codes told apart by title/units (`e6a3e0c`); affected-course listings cite one
  span per course (`6e9ce80`, COMM BC 11 no longer errors); full suite 6150 passed.
- Hosted curriculum ledgers ([record](2026-10-23-hosted-curriculum-ledgers-load.md), `23882db`):
  migration 20261023090000 applied to hosted; 9 curricula / 502 courses loaded into the research
  release and verified by runtime read-back. Chatbot wired (`fb2866b`, `6f03016`): one research release
  serves all hosted curricula; hosted wiring check correct for BSCS old/proposed and BSIT.
- College of Arts and Humanities complete (AB Comm, AB PhilStud, AB PolSci, BS Psych Clinical + IO,
  BS Social Work); repeated printed codes cataloged for clarification (`8f024d7`, `dc58a4d`).
  Hosted now holds 14 curricula. Loader picks up any `p09-program-reviews/<name>` ledger.
- CBA complete (9 programs incl. BS Accountancy from PDF page 3, BSBA-HRM page 1). Owner rules added:
  self-reference = source gap; printed "None" = verified no prerequisite. Hosted: 23 curricula.
- CHTM complete (BSHM Culinary, BSHM Hotel/Resort/Club, BSTM). Owner rule: "All <prefix> subjects" =
  every course with that prefix. Author script: `pre_side` for spanning summer rows; colon variants.
  Hosted: 26 curricula.
- CNHS complete: BS Midwifery (prospectus lists years 3-4 only; earlier courses are gaps), BS Nursing
  (2 pages via `part_only` + `assemble_program.py`; merged cells, A/B pairs, loop 117B<->112 B marked
  as gaps). Hosted: 28 curricula.
- CoE complete (BSCE, BSEE, BSME, BSPE; owner rules: "Graduating"/"passed all Math courses"/OJT 85% note
  = status conditions; co-requisite marks apply to their course). CTE complete (BEEd + 6 BSEd majors).
  ALL 39 PROSPECTUS CURRICULA REVIEWED AND LOADED to hosted research release (39 curricula).
- /doctor 23 Oct: AGENTS.md history moved to `plans/owner-decisions-ledger.md`; Claude
  attribution trailers removed from unpushed commits (owner: never add them).

## Current Task

Program-by-program prerequisite review and loading. BSA, BS Criminology and BSIT ledgers are authored
(workspace `audit-evidence/p09-bsa-review-20261022/` and `p09-crim-review-20261022/`, `p09-bsit-review-20261023/`: `ledger.json`,
`author_*.py`, `check_*.py`, page PNGs). Not yet loaded into Supabase or wired into the runtime.

## Repository State

Branch `feat/p09-generation-validation`, HEAD `e4bd8bd` + this checkpoint commit, clean, nothing pushed. Hosted keys in
the worktree's git-ignored `.env` (owner-run script). Model container `bintanong-p09-cuda-latency`
(127.0.0.1:18088; `docker restart` before long runs; start Docker Desktop first if `docker ps` fails).

## Verification Evidence

- Full suite at the partial-rule fix (`e4bd8bd`): 6145 passed, 6 skipped, 0 failed (1061 s).
- Storage DB regression with research release: 182 passed, 916 subtests.
- Commands: test Python `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider <tests> --basetemp=<audit-evidence dir>`;
  DB tests use local Docker `supabase_db_Bintanong` (set `BINTANONG_STORAGE_EVIDENCE_DIR`).
- Roster runner: workspace `audit-evidence/p09-real-data-20261021/roster.py <outdir>` (`HOSTED=1`
  for Supabase retrieval, `ONLY=id1,id2` to filter); record a protocol before counted runs.

## Versions and Digests

BSA PDF SHA256 `72dad4a0384f82228d63c8926e4ae8a1eb14a33497c9952e0f60782083e82666`; BSA ledger
SHA256 `a5f4e2205d1aae974dbbc7a4ac23ab7c8baf2d2d9050efebdf69982578c57041`. BSIT PDF SHA256
`70f7893959244addd897e77a57ac69736c55c1f6262292faf6e278fb0df26ac5`, ledger file
`30c238cd1fce663ca353bfbc488aa2e85f56aa75e7c82f8c2e0c746fd349245e`. BS Criminology PDF SHA256
`b3b43dece33b171af81fdc738da45864f204188b068d66a180b670270f36a2d3`; ledger file SHA256
`405eecb78d3a1df251e822a0e956685ba0a33b8d77af8624772b0cfc0797bd60`. Router v14, ctx 8192,
out 768, temp 0, seed 0 unchanged. Model weights `C:/Coding-projects/bintanong_workspace/MODELS`.

## Decisions

- Research release kind: owner authorization lives on the release; sources never marked approved.
- BS Architecture decisions 1-6 (22 Oct): comma = all_of; short codes TOA-1/AR-INT/BT-2/BT-5/
  Ar RM 1 map to full codes; Arc 1 = Ar-CC 1; MATH 19-20 = Math 19 and Math 20; D-10/L, PP-4,
  D-7 kept as printed (PP-4, D-7 = source gaps, unknown); "4th Year Standing" unknown unless the
  student gives their year (chatbot may ask). Blank cells stay unknown.
- Owner cannot open files: always show program, course code, title and printed text inline.

## Known Failures or Blockers

- All 39 prospectus curricula reviewed and loaded (9 colleges). No program review remains.; multi-page Accountancy, BSBA-HRM, Nursing need an owner question (new layout) (39 PDFs in
  `Bintanong/dataset/PalSU Undergraduate Prospectus Website Dump/Tiniguiban - Main/`).
- Course facts/rules are not in Supabase yet (tables `programs`, `curriculum_versions`, `courses`,
  `course_aliases`, `policy_rules`, `rule_source_spans` exist, empty).

## Next Action

23 Oct resume (Claude): full suite at `e832b9a` 6183 passed, 6 skipped. Run 9 protocol fixed
(`b3d8a15`); first attempt quarantined (all 39 prospectus versions sent as retrieval version ids,
limit 32 -> every document question `invalid_output`); fixed in `b26de19` (document versions only,
TDD regression in `tests/test_orchestration_pipeline.py`). Counted run 9 restarted at `6dad1af`
(workspace `audit-evidence/p09-real-data-20261021/roster9/`); that attempt was stopped by Claude Code
after 2 cases (both answered) because the machine ran low on memory - not a code failure. Next: with
the owner's go-ahead and free memory, restart run 9 from case 1 into a fresh folder, then read run 9 against run 8, record
results in the roster results file, then rerun the full suite. Context consulted this resume: thesis
physical 17-18 and the routing PNG; no discrepancy.

## Do Not Repeat

Hosted migrations/load (done; hosted is not empty - the load script refuses a non-empty project),
BSA, BS Criminology and BSIT page reading, decisions and authoring, co-requisite and partial-rule fixes, hosted curriculum migration and 9-curricula load, roster runs 7-8, style floor, per-part observation, task-first
trial, checker diagnosis, source/benchmark reviews, asset setup.
