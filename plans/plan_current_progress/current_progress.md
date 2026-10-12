# Current prospectus workstream progress — 29 September 2026

**Current numbered-phase status, 12 October 2026:** Handbook whole394page conversion finished922.075s, reader refused83native text items under picture nodes. Raw/meta retained; no repeated conversion.8syntheticRED regressions then minimal guarded picture traversal GREEN141passed/1skipped; actualreader5864refs succeeds. Exact retained-byte candidate replay running; fullsuite/review/validation pending. Original images/scope/timing findings retained; authority/content review pending. Charter427chunks/3rejections preserved. No setup/moves/replacement search, prospectus review, activation orPhase06. Current record: plans/phase-05-handbook-source-recovery.md.

This is the recoverable handoff for the approved review-only prospectus workstream. It is not a formal numbered phase checkpoint or institutional approval. Fresh Git/test evidence outranks this note.

## Completed work

- Planning commit `e31a881` approved parallel prospectus preparation and the local human correction GUI. Phase 1 source approval still gates active institutional use.
- Task 0 commit `702a38f` added and tested `ProvisionalSource(pdf_sha256, source_locator)`, with source verification fixed pending. It verifies original PDF bytes and rejects hash mismatch. Local copied PDFs match the external corpus's 39 distinct hashes / 44 paths; the ignored inventory is under `backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/PalSU Undergraduate Prospectus Website Dump/provisional-source-inventory.csv`.
- Task 0 review passed; recorded supplemental suite: 19 tests passed using `uv run --project backend --extra tools --extra dev --with fastapi==0.141.1 python -m pytest -q tests`. Full Windows `api` extra could not build `janus-swi` without MSVC. That is prior Task 0 evidence, not a Task 1 rerun.
- Task 1 completed fresh BSCS and Architecture original-PDF conversions and an initial comparison of all 132 scheduled rows. Both complete one-page originals were visually inspected. Independent source transcription and candidate comparison produced 1,320 field decisions. Eight additional BSCS option rows were checked separately.
- Task 1 created a 92-entry field discrepancy/spot-check ledger, plus a fresh 39-hash/44-path review index. Initial checks include Values Education, both Psychology tracks, Civil Engineering, BSBA Marketing, Midwifery, old ComSci and source-total conflicts. Other Engineering PDFs are indexed/rendered but not field-reviewed.

## Current evidence and limits

- Task 1 report: `.superpowers/sdd/2026-09-26-prospectus-phase2-implementation-draft/task-1-report.md` (ignored local review workspace).
- All detailed source-derived review artifacts remain outside Git: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\docling_jsonified_output\task1_baseline_2026-09-29`.
- Authoritative conversion source: original PDFs under the external `PalSU Undergraduate Prospectus Website Dump`. Generated JSON is diagnostic output, never the expected source reading.
- Fresh self-test: 80/80. Runtime Python 3.13.5, Docling 2.129.0, docling-parse 7.20.0. Repo/dataset parser text still matches after normalizing line endings.
- Fresh BSCS: 55 courses, 159 units, audit WARN, strict exit 0. Fresh Architecture: 77 courses, 230 units, audit ERROR, strict exit 1. Both audit states are extractor-only.
- All 132 scheduled codes and course units match visible source rows. Missing scheduled codes: 0/132 source rows; false scheduled codes: 0/132 emitted rows. Course identities being present does not make their fields correct.
- Nine critical field groups per row: 1,112 matches, 73 mismatches, 3 source-unresolved / 1,188 comparisons under documented whitespace/hyphen/terminal-period normalization. Physical page is measured separately. No corpus accuracy percentage is claimed.
- BSCS truncates one standing requirement and spills its last word into the next course's prerequisite. Architecture has 33 wrong titles, 13 wrong raw prerequisite fields, 11 wrong resolved prerequisite fields, and 3 unresolved source references. Explicit elective labels are not correctly reflected in `is_elective` for 12 pilot rows.
- Architecture's printed second-year second-term 23 and grand 231 conflict with visible row sums 22 and 230. Extracted individual course units agree with the source; do not change units to force its checksum.
- All discrepancy records have PDF hash/page/cell locators. Corrected cell ownership and geometry still require independent review, especially where Docling merged or misplaced text. The 37 other unique PDFs lack complete field review. This is an agent-reviewed initial baseline, not a human-approved gold set.
- The old v5 batch manifest was freshly read: 44 paths, 1 OK, 6 WARN, 37 audit failures, 0 exceptions. Its 7/44 audit-pass count is not field accuracy. The non-pilot spot checks compare original PDF views against this older v5 output and are labeled as not freshly converted.

## Repository state

- Task 1 implementation base: `dev`, HEAD `702a38f`. The next documentation commit updates this note; identify that commit from Git rather than treating the earlier planning HEAD `8e382bd` as current.
- Pre-existing dirty files remain untouched: `.gitignore`, `backend/bintanong_tools/bintanong_jsonifer_prolog/bintanong_prospectus_jsonifier.py`, and untracked `plans/CODEX_HANDOFF_prospectus_extractor_phase2_2026-09-26.md`.
- Parser SHA-256 at review: `b50ece65539252cc4c7b519dac8506497dd40ec0f3b9220c0575bab6f745c835`; its pre-existing diff is 41 insertions / 3 deletions. HEAD alone does not identify this parser snapshot.
- No Task 1 parser edits, institution PDF staging, production release companions, active RAG/Prolog activation, database writes, or formal phase advancement occurred. Local legacy full candidate JSON retains parser-embedded candidate Prolog/RAG fields; these have no approval status.
- `phase_state.py inspect` reports a valid ledger, no active numbered phase, Phase 0 complete, Phase 1 next permitted. `plans/INDEX.md` remains authoritative.

## Next action

1. Review the Task 1 report and local source-backed discrepancy ledger. Independently confirm corrected cell ownership before marking a source reference human-approved.
2. Begin Task 2 with one focused failing regression per demonstrated topology failure. Include the newly demonstrated BSCS standing spill and Architecture row spill alongside the Values Education/Psychology merged rows. Keep ambiguous source references explicitly unresolved.
3. After each shared parser change, run the self-test and original-PDF 44-path regression, compare repaired/newly broken fields, and preserve all source aliases. Complete the 39-PDF reference before any general accuracy claim.
4. Continue the approved adapter, review GUI and provenance tasks in plan order. Pending Phase 1 indexing does not block local review preparation; active institutional release still requires source/version and rule approval.

Do not repeat Task 0 or discard the pre-existing dirty parser. Do not use generated JSON as the conversion source. No numbered Phase 2 exit or Phase 3 advancement is implied.

## Parallel prospectus Task 2 recovery (29 September 2026)

- The full source-backed report is `plans/prospectus_extractor_recovery_2026-09-29.md`. New parser guards withhold fused multi-course cells and preserve page/cell evidence; original-PDF checked slash-code repairs cover old ComSci, Hospitality, and Tourism. A process-isolated command checkpoints each PDF so one Docling child crash cannot erase later results.
- Final regression used 44 original PDF paths (39 distinct hashes), with 44 detailed and 44 compact review JSON files. Processing errors: 0. Extractor audit: 1 OK, 6 WARN, 37 ERROR; strict run exit 1. These are candidate outputs, not approved curricula. Forty-five merged-code issues in 14 paths have PDF review evidence. No Prolog or RAG companions were generated in this run.
- Verification: Bintanong tests 25 passed and 13 subtests passed (5 dependency warnings); extractor self-test 80/80. The supported isolated command passed a separate two-original-PDF smoke run; the 44-path result came from an external equivalent runner. Full row-field reference remains only two PDFs, so no corpus accuracy claim is justified.
- Remaining critical parser defects include incomplete BSCS standing ownership and the Social Work `World` spill into SW 13. Architecture has many wrong titles/prerequisites. Task 2 remains partial, review-only. The formal phase ledger is unchanged; Phase 1 source approval and later human curriculum/rule review still gate active use.

### Latest standing-spill check

- A source-backed guard now withholds one-word standing continuations from the following course and raises a blocking anomaly with PDF cells. The original new BSCS PDF changed from WARN to ERROR; GE-STS no longer carries `semesters`, while CS Elect 4/L still needs its complete standing reconstructed by review.
- The supported isolated command completed all 44 original paths: 39 distinct hashes, 0 processing errors, 1 OK, 5 WARN, 38 ERROR, exit 1 due to audits. Only BSCS changed audit status. Candidate fields changed in new BSCS, Social Work, and Civil Engineering; visual checks of the original latter two PDFs confirm blank next-course prerequisites. The earlier 45 fused-course flags remain, plus 3 standing-fragment flags.
- Verification: full suite 26 passed and 13 subtests passed; extractor self-test 80/80. No corpus accuracy claim, institutional approval, or active RAG/Prolog release follows.


## Extractor package split (3 October 2026)

- Branch refactor/prospectus-extractor-package, from dev at 7591264. Not merged and not pushed. Commits (git log --oneline dev..HEAD):
  - 24b800f docs: plan the prospectus extractor package split
  - c5b0d04 chore: add extractor subagent definitions with model and effort
  - b5235de test: add failing 1:1 gate for prospectus extractor split
  - 83d5996 test: add golden-output check for extractor split
  - dcd94ff refactor: generate prospectus_extractor package from the monolith
  - f5bbca4 refactor: route the jsonifier entry points through prospectus_extractor
  - 4c450e9 fix: hash and launch the extractor package in the isolated batch
  - c7ff0c4 docs: record two more location effects found in review
  - 2dffe3d test: run the extractor self-test under pytest
  - 38af9fd docs: record the extractor package split and its equivalence evidence
- The 6,320-line extractor is now the package backend/bintanong_tools/prospectus_extractor/; the old file path is a compatibility shim.
- Tests: full suite 36 passed, 13 subtests passed, 0 failed; extractor self-test 80/80 from four entry points.
- Golden result on 44 cached Docling JSON inputs: 44/44 identical to the old file apart from run-to-run timestamps. Cached JSON was used, so PDFs were not re-converted through Docling.
- parser_sha256 in the isolated batch manifest is now a hash over every .py file in the package (line endings normalised). It is not comparable with the single-file hash 8ea75006... in earlier manifests.
- Decision record: docs/decisions/prospectus-extractor-package.md. The scaffolding scripts were removed; recover them from Git at 2dffe3d.
- Next: user decides on merge, then Phase B (markup twin that looks like the printed prospectus). Outputs remain review candidates; nothing here approves a curriculum, RAG, or Prolog release.

## Prospectus markup twin, Phase B closed (4 October 2026)

- Branch feature/prospectus-markup-twin: the pipeline now writes <name>_prospectus.md, an HTML-table rendering of the Docling evidence with cell IDs, spans, gaps and original text (--export-md). Course fields unchanged: 44/44 identical to base 69ca855. Suite 93 passed, 13 subtests. Merged into dev locally, not pushed.
- The course audit (44 paths, 39 PDFs, 2031 courses) is committed as scripts/prospectus_course_audit.py, the planned OCR scorer; scripts/prospectus_course_compare.py is the old-versus-new comparer.
- Human visual check (3-4 October): first-year rows fine, year/semester banner rows broken because Docling merges banner text into neighbouring cells; the twin is faithful and the parser inherits the defect.
- Decision record: docs/decisions/prospectus-markup-twin.md. Next: Phase B2 (year/semester verifier and fixer with a human decision ledger), then a parser banner-split repair.

## Phase D final implementation gates and documentary handoff (6 October 2026)

- Branch `feat/prospectus-phase-d-safe-cache`; approved pickup/regression base `641523d212839084da03d966ffbfca66c7e83e42`, reviewed production tip `c40a38c9f633dd085766ca11f81f0dd3890810cc`. S2/S4 independent specification and quality seats approved; final whole-range specification and quality reviews of `641523d..final-documentary-tip` remain **PENDING**, so Phase D is not yet fully complete.
- Fresh comprehensive run in the GUI-review venv (includes API and embedding tests; the main backend venv gives 984): 990 passed, 13 subtests, five upstream warnings; focused publication/publish/snapshot/skip: 394 passed including all 180 replacement interruptions; self-test 80/80. Unchanged-production-tip main subset evidence reused: 984 passed, 13 subtests, three upstream warnings, with the two previously approved API/embedding ignores. All final gate commands exited 0 except the deliberately corrupted scratch PDF, which exited 1 as required. No installs or main-venv changes.
- Fresh comparer against `641523d`: 44/44 course fields identical. B2 health mixed/warnings_only/broken/clean = 21/3/19/1; title_from_pdf 67, strip_banner 0, unclaimed_code 316, banner_leak 3. Direct prerequisite states blank_unreviewed/resolved/unresolved_reference/standing_condition/unreadable/alternative_or_exception/stated_none = 1005/689/253/59/20/3/2. Original trial 01/16/33 sheets: zero `check_against` errors each. These prove regression stability, not corpus extraction accuracy or approval.
- Fresh real PDF A published WARN; B skipped with `identical run identity`; C conversion failure preserved all nine earlier files and wrote `ConversionError` diagnostics; D restore skipped and retained diagnostics; E successful forced conversion cleared them. Same-size/restored-mtime mutation after a real cached parse refused publication; restoring bytes and a successful reused-cache publish cleared diagnostics. Original/source candidate/trial files: 101 hashes unchanged around these workflows. Evidence retained externally, including explicit timing/provenance limits.
- [Decision record](../../docs/decisions/prospectus-cache-and-publication.md) records snapshots/DocumentStream and the legacy wrapper, separate conversion/run identities, publish-v2 cache/main bindings and companion→main→cache→manifest order, prepublication preservation versus interrupted-publication detection, known-only cleanup, root-relative marker discovery, LF/BOM CSV with supported stdlib minimal quoting, context-sensitive `skip_reusable`, TUI force, default migration to `~/Bintanong/output` without moves, actual 181/226/161/251 path maxima and single-writer limit. Original JSON is review-only; no source approval follows.
- F5 corrected Task 6 count 15→14. Authentic original red log unavailable; explicitly reconstructed parent `29eb832` plus `f802c76` tests observed 12 failed/2 passed. Frozen `f802c76` test collection confirms 14; the historical combined 61 is retained with its provenance limit. Preserved historical plans are unchanged.
- External report/evidence root: `E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_resume_2026-10-06\task-d-final-gates-report.md`. Only the three authorized documents are committed. No push, dev merge, worktree deletion, main dirty-file edit or institution-source mutation. Comparer and baseline worktree are retained for Phase F.
- Next: controller whole-range D reviews, then continue GUI integration/review/human trial, Phase E and Phase F, OCR evidence and formal Phase 1/2 preparation. Human/source-owner/real-photo and release gates stay pending; no numbered-phase advancement or institutional activation is claimed.

## Handoff reminder and Phase 3 direction (11 October 2026)

- Owner direction: Phase 2 is finished and the next intended work is Phase 3. Use the original master implementation plan, maintain this progress directory and `plans/`, and consult ingestion documents only when the implementation plan requires them.
- Created `.agents/skills/bintanong-handoff-reminder/SKILL.md` with automatic invocation enabled. It routes every Bintanong prompt to the existing phase handoff skill and requires logging material changes here alongside formal checkpoints. Added the routing rule to repository `AGENTS.md`; a skill alone is not an executable per-prompt hook.
- Reviewed master-plan sections 7 and 8: Phase 3 is embedding generation, producing reusable vector artifacts independently of persistence and retrieval. Briefly read ingestion README/current status only to check Phase 2 delivery against those prerequisites; preserved historical documentation.
- Recorded-state mismatch: `plans/INDEX.md` and `phase_state.py inspect` still report no active phase, a Phase 1 final handoff, and eligibility to advance to Phase 2. Phase 2 is preparation only, with no final Phase 2 handoff. This differs from the owner's stated completion; this reminder task does not certify or rewrite exit-gate evidence.
- Repository base: HEAD `9f2b1d9775883dacce9ffd2f6178fe18fda15e1d`; initial working tree clean. Current changes are `AGENTS.md`, this progress log, and the new reminder skill directory. No commit was made.
- Verification: system Python 3.13.7; handoff `inspect` and `validate --repo .` report valid state; `git diff --check` passed before this log entry. The skill-creator `quick_validate.py` command could not execute because system Python lacks `yaml` (PyYAML). No dependency installation occurred. These checks do not verify Phase 2 completion.
- Next action: reconcile the delivered Phase 2 work and its remaining evidence with the owner's completion statement, recover the formal Phase 2 handoff through the existing handoff workflow, then prepare Phase 3 against master-plan section 8. Reuse delivered ingestion work rather than repeating it solely because its handoff is absent. Keep this file current.
- Do not repeat: reminder creation or broad ingestion-history review; do not replace the original master plan, discard existing ingestion documents, or infer institutional activation from candidate delivery.

## Merge of updated dev (12 October 2026)

- Merged the fetched `origin/dev` work through `4a33320` into local `dev`; preserved local handoff-reminder work in commit `ad1e13b` before merging.
- Kept this current progress log despite the remote branch removing the progress directory while formalizing the Phase 2 handoff. The dated entries above remain historical records; phase status is governed by `plans/INDEX.md` and the final handoffs.
- Integrated the Phase 2 final handoff and Phase 3 embedding-generation plan, checkpoint, and final handoff. The repository ledger now records Phase 2 and Phase 3 complete, Phase 4 prepared, and no active numbered phase. Phase 4 requires owner review and a formal start.
- Integrated the SEA-LION E5 embedding adapter and resumable batch pipeline with their tests, plus MCP configuration and updated agent/handoff workflow instructions. The configured `.mcp.json` uses environment variable references for credentials.
- Merge resolution: retained `plans/plan_current_progress/current_progress.md`; accepted the remote MCP configuration and workflow updates. The legacy `extractor_split_progress.md` remains deleted as in `origin/dev`.
- Verification for this merge: `phase_state.py inspect` and `validate --repo .` both report a valid ledger with Phase 4 eligible; `git diff --cached --check` passed; `.mcp.json` parses as valid JSON; no unmerged paths remain. No tests were run for this documentation and branch integration task.
- Next action: review the prepared Phase 4 storage plan and formally start Phase 4 only after owner review. Do not repeat the completed Phase 3 implementation solely because the former progress directory was removed.

## Phase 4 initialization and task kickoff (12 October 2026)

- Owner direction: Checkout custom handoff skill, continue from previous agent, utilize appropriate skills, commit frequently in verified increments, and utilize Supabase and GitHub MCP for Phase 4.
- Formally initialized Phase 4 in `plans/phase-04-supabase-storage-plan.md` (`status: in_progress`), created `plans/phase-04-checkpoint.md` (sequence 1), and updated `plans/INDEX.md`.
- Infrastructure verification: verified local Supabase instance (PostgreSQL 17.6 + pgvector 0.8.2 on ports 54322/54321), inspected GitHub MCP (`github-mcp-server`) with repository branch list.
- Verification: `phase_state.py inspect` reports valid ledger with Phase 4 active; 19 phase state tests passing (exit 0); 10 embedding suite unit tests passing (exit 0).
- Next action: Design and apply Task 1/2 Supabase SQL migration for relational knowledge tables and pgvector embeddings.

## Phase 4 Schema and RLS migrations applied (12 October 2026)

- Completed Task 1 & Task 2: Authored `supabase/migrations/20261012000000_phase4_knowledge_schema.sql` defining 19 relational and pgvector tables with foreign keys, check constraints, and `vector(1024)` embeddings.
- Completed Task 5 (Schema & Security): Authored `supabase/migrations/20261012010000_phase4_rls_policies.sql` enabling RLS on all public tables, restricting runtime roles (`anon`, `authenticated`) to SELECT only, enforcing strict active-release chunk isolation, and adding RPC functions (`match_chunks`, `activate_knowledge_release`, `rollback_knowledge_release`) with explicit `search_path` and privilege restrictions.
- Verification: Executed `npx supabase db reset` cleanly applying all migrations to local PostgreSQL 17.6; verified 19 tables and vector column type via `npx supabase db query`; ran `npx supabase db advisors` with 0 security/performance issues found.
- Next action: Implement `backend/bintanong_storage/loader.py` and `backend/bintanong_storage/release.py` for idempotent loading and atomic release lifecycle.

## Phase 4 Completion and Handoff to Phase 5 (12 October 2026)

- Completed Task 3: Built `BatchKnowledgeLoader` in `backend/bintanong_storage/loader.py` supporting idempotent imports of manifest metadata, candidate chunks, source spans, and `vector(1024)` embeddings.
- Completed Task 4: Built `ReleaseManager` in `backend/bintanong_storage/release.py` managing immutable release memberships, draft-to-active promotions, and dynamic rollbacks.
- Completed Task 5 & Vector Retrieval: Built `KnowledgeRetriever` in `backend/bintanong_storage/retrieval.py` supporting exact cosine distance `<=>` search via `match_chunks`.
- Added administrative CLI in `backend/bintanong_storage/cli.py` (`status`, `load`, `activate`, `rollback`).
- Verification evidence:
  - 8 storage unit and integration tests passing (`test_storage_client.py`, `test_storage_loader_idempotency.py`, `test_storage_release_isolation.py`, `test_storage_vector_retrieval.py`).
  - 10 embedding tests passing across `backend.bintanong_embedding`.
  - 19 phase state tests passing in `test_phase_state.py`.
  - Supabase database advisors: 0 security or performance issues.
- Exit gate satisfied: Idempotency (0 duplicates on repeat load), Release Isolation (draft/superseded chunks inaccessible to runtime role), Permission Enforcement (runtime anon cannot write or invoke admin RPCs), and Advisor clean audit.
- Created `plans/phase-04-handoff.md`, marked `plans/phase-04-checkpoint.md` superseded, and prepared `plans/phase-05-retrieval-plan.md` (`status: ready`, `preparation_only: true`).
- Next action: Owner review of Phase 4 deliverables and formal start authorization for Phase 5 (Retrieval).

## Independent Phase 04 security verification (12 October 2026)

Repair authorized by the owner after this review. Execution plan: [Phase 04 security repair](../2026-10-12-phase04-security-repair.md). Work starts from `7c0ed85` in the existing worktree using disposable-database verification and additive migrations; advancement remains gated.

Repair Task 1: CLI-generated additive privilege migration and explicit local exposure setting implemented. The original defaults/grants caused 4 failing role subtests; after repair, `python -m unittest tests.test_storage_security -v` passed both tests, including effective mutation privileges and future table/sequence defaults. SQL fixtures/evidence remain external, and disposable databases were removed. No shared/hosted migration applied yet. Next: Task 2 approval/release visibility and publication invariants.

- Owner requested review of the Supabase RLS/access controls and Phase 04-to-05 handoff. Review baseline: clean `feat/p04-supabase-rls` at `8f53b72`.
- [Review](../phase-04-security-review-2026-10-12.md) and [decision](../../docs/decisions/phase-04-security-review.md) record four P1 findings: runtime TRUNCATE grants on all 19 tables (local/hosted; local also retains DML grants), draft curriculum children/out-of-release rules visible, activation accepts incomplete/unapproved releases, and published membership/content can change in place. P2: hosted schema has no migration history and its ACL changes are absent from the committed migration.
- Hosted Supabase MCP inspection confirmed 19 RLS-enabled tables, matching policy predicates, SECURITY INVOKER RPCs, vector 0.8.2 and zero security/performance lints. Advisors did not catch these application authorization defects. Hosted knowledge and active-pointer counts were zero.
- Fresh local SQL probes used actual `anon`, `authenticated` and `service_role` in rolled-back synthetic transactions. Both runtime roles reproduced the defects. Basic draft/current/superseded chunk isolation, sequential activation/rollback, vector visibility and admin RPC denial passed. Runtime INSERT denied; UPDATE/DELETE affected zero rows despite existing grants.
- Local anon HTTP reads succeeded; administrative RPC calls returned 401 / SQLSTATE 42501. Post-probe audit chunk/document/release and active-pointer counts returned zero, matching baseline. Raw evidence outside Git: `C:/Coding-projects/bintanong_workspace/audit-evidence/p04-20261012/`.
- Existing storage suites NOT RUN: shared-pointer deletion/fixed fixture IDs make them unsafe against arbitrary configured endpoints; system Python 3.13.7 lacks pytest. No installs or dependency changes. No hosted writes or implementation/migration changes.
- Ruling: Phase 04 plan reopened, checkpoint and handoff blocked, ledger corrected. Historical completion narrative retained. Phase 05 remains preparation only; fresh verification outranks the prior completion checkboxes.
- Next action: repair F1 through an additive least-privilege migration with isolated effective-ACL verification, then F2–F4, reconcile F5, and run the complete Phase 04 exit gate under both runtime roles before restoring advancement eligibility.




## Phase 04 security repair Task 2 verified (12 October 2026)

- Task 1 privilege commit: `c48f404`. New additive migration enforces active/approved-parent visibility, complete publication checks and immutable published evidence. Loader and release creation now use atomic administrative RPCs.
- Replaced legacy shared-pointer tests with disposable PostgreSQL fixtures and HTTP MockTransport checks. Full gate: 25 tests passed in 57.574s, including actual runtime roles, reimport identity preservation, failed-batch rollback, cosine ranking and concurrent publication/writer isolation.
- Independent review identified two additional P2 gaps in dictionary content/location validation and corpus identity. Both fixed; re-review pending. Standalone manifest loading now requires an explicit set ID; ordinary Phase 03 artifact loading derives identity from the configuration and full sorted embedding corpus.
- Hosted baseline verified against a fresh historical-only database: 146 columns, 67 constraints, 37 indexes, 19 policies/RLS flags and three functions match (line endings normalized). Original ACL drift documented. CLI recorded the three missing historical migrations without replay; institutional tables and pointer remain empty.
- Next: finalize independent review, commit Task 2, apply only the two additive migrations to local/hosted targets, inspect resulting roles/advisors/history and complete the handoff only when all gates pass. Phase 05 remains preparation only.

Task 2 final gate: 30 storage tests passed in 69.867s. Final review corrections include effective-source-text consistency, ordered source-span agreement, valid textless-table support, nullable-identity conflict rejection and stale-snapshot isolation rejection. All reviewer findings addressed; 12 embedding tests and 19 phase ledger tests passed. No disposable test databases remain. Next action: apply the two dry-run-selected additive migrations locally and hosted, verify live state, then close the security gate if earned.

## Phase 04 hosted correction deployed (12 October 2026)

- `6e762a5` commits the policy/publication/import repairs. Both local and hosted databases now have migrations 10001/10002 applied and matching history. Live roles: 17 institutional SELECT grants each; zero mutation grants or admin RPC execution, RLS enabled on all 19 tables. All knowledge tables and active pointer remain empty.
- Fresh advisors at INFO expose six missing foreign-key indexes and intentional policy-free operational tables, with no WARN/ERROR. Follow-through migration 10003 adds covering indexes and explicit restrictive runtime denials. The new policy regression failed before the migration; all 11 security tests pass afterward. Expected unused-index INFO notices on empty databases remain nonblocking.
- Next action: commit/apply 10003, compare final catalogs and function ACL/defaults, run the complete isolated suite, and record the earned Phase 04 closure. Phase 05 remains preparation only; no institutional release was activated.

## Phase 04 corrective closure — 12 October 2026

- Committed privilege repair `c48f404`, publication/import repair `6e762a5`, advisor hardening `c5beecd`. Original migrations/master/history preserved.
- All three additive migrations applied locally/hosted; verified missing historical entries recorded without replay. Final dry runs: no pending migrations. Both live roles: 17 institutional SELECT grants, zero writes/admin EXECUTE; 19 tables use RLS. Application objects/defaults use postgres ownership. Platform-managed supabase_admin defaults remain outside alteration authority; future managed-role/manual creation needs effective-ACL review.
- Catalog parity: 150 columns, 71 constraints, 47 indexes, 19 policies/RLS flags, 8 public functions, 9 private functions, 34 triggers. Security advisors clear; performance only unused-index INFO (24 hosted/18 local); zero WARN/ERROR.
- Verification: 31 storage tests passed (78.153s), 12 embedding tests (0.152s; existing deprecation warning), 19 ledger tests (17.533s). Actual SQL roles/RPCs, HTTP construction, local runtime denial smoke and hosted actual-role SELECT checks verified. Independent reviewer: no blockers. No disposable databases remain; institutional tables/active pointers still empty.
- Raw evidence outside Git in `audit-evidence/p04-repair-20261012/`. Handoff records exact versions/digests/commands/limits. Models not downloaded, executed or hashed.
- Closure: Phase 04 plan complete, checkpoint superseded, handoff complete, INDEX next phase 5; Phase 05 prepared baseline updated without starting implementation. `validate` and `can-advance` both passed: no active phase, complete latest handoff, Phase 05 eligible. Documentation commit/clean-state check follow.
- Next substantive action: review/formally start Phase 05, then matching query embeddings, authorized request-pinned scope/release access and labeled retrieval evaluation. Source approval/institutional activation retain existing boundaries. Do not repeat repaired security work from historical blocked narratives.

## Phase 05 formal start — 12 October 2026

Owner requested continuation into Phase 05. Baseline clean `10bfd6f`, isolated `p05` worktree/`feat/p05-retrieval-logic`. Prior ledger valid and can advance yes; GitHub MCP PR 6 confirms merged corrective handoff. Hosted read-only MCP: PostgreSQL 17.6/vector 0.8.2, no knowledge releases or active pointer.

Prepared plan activated and refined against master section 10. Decisions: retain model-specific Retrieval prompt confirmed in external model config; strict query wrapper prohibits legacy adapter mock/network fallback; atomic STABLE invoker RPC pins only currently authorized release and exposes stale pins explicitly. No RLS relaxation or institutional activation. Context7 docs fetched for invoker RPC/RLS and local SentenceTransformer loading.

System Python 3.13.7 has no pytest/torch/sentence-transformers; use unittest and explicit test doubles, no installs. Approved institutional retrieval cases are not yet established and remain a formal completion prerequisite. Next: Task 1 failing tests, external asset hashes, strict query/request implementation.

### Phase 05 Task 1 verified

Validated requests/settings and strict local query encoder added. Five unittest tests passed after missing-module RED; rejects unverified/missing assets, invalid vectors and token overflow, preserves matching Retrieval prompt exactly once. Fresh external weights SHA-256 df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1; ten-file inventory in external p05 evidence directory. Real execution unavailable in system Python; no installation/download. Next: atomic active-release-pinned RPC with citation/scoped search database tests.

### Phase 05 Task 2 verified

Four disposable PostgreSQL tests passed after missing-RPC RED. Additive CLI-generated retrieve_context migration binds active pin, fingerprints, exact filters, rankings, spans/versions and required-neighbor payloads in a STABLE invoker snapshot; historical RLS stays closed. Runtime EXECUTE granted only anon/authenticated. Shared/hosted application NOT RUN. Next: context budgeting/deduplication and explicit retrieval statuses; their missing-module RED tests were observed.

### Phase 05 context and pipeline verified

Ten new unittest tests pass after missing-module RED. Exact serialized-context budget, source-location overlap deduplication, whole required-neighbor groups, table-locator fallback and citation integrity implemented. Engine performs runtime-only preflight plus atomic configuration/pin recheck; explicit release_changed/configuration_mismatch/encoder_unavailable/insufficient_evidence/needs_scope/conflicting_sources/uncalibrated outcomes. Internal debug-v1 envelope preserves ambiguity; existing public runtime contracts remain unchanged. All committed evaluation cases are synthetic per evaluation/case.py; approved institutional gate remains unavailable. Next: debug CLI, synthetic k=3/5/8 calibration and full review.

### Phase 05 debug/evaluation candidate delivered

25 retrieval tests pass (19.927s). Synthetic development ten cases/three k values has full positive recall and unsupported detection; mean P@k0.200/0.120/0.075 with full-k denominator. These are manual-vector mechanics, not encoder quality or approved institutional evidence. Internal JSON CLI/help and empty local runtime release_changed smoke verified. Metric evaluator rejects final tuning; runtime policy remains uncalibrated. Whole storage suite found an obsolete runtime-RPC allowlist (two failures); exact signature update passes targeted security test. Fresh final reviewer is investigating neighbor/citation correctness. Next: reproduce/fix review findings and rerun full gates; formal phase completion still unavailable.

### Phase 05 final review repairs

Three P2 findings reproduced/fixed with RED/GREEN: transitive authorized neighbor closure, neighbor curriculum ambiguity, and unsupported fresh-cell attribution for partial textless-table overlaps. Root13 targeted tests pass; reviewer13 pass and no remaining P1/P2. Concurrent publication test passes and proves statement snapshot consistency; one original infrastructure timeout remains unreproduced. Checkpoint UTF-8 repaired after Windows default-encoding byte, ledger valid. Final broad suites underway. Hosted security advisor zero lints, read-only baseline only; shared migration remains unapplied. Asked owner for approved development-case/source paths and existing compatible Python3.13 environment while independent verification continues.

Final retrieval gate:29 tests passed24.814s, exit0. All review fixes verified and committing as a cohesive correction increment. Full storage/embedding/ledger gate sequence continues; no deployment or institutional activation.

## Phase05 verified candidate / blocked formal exit — 12 October 2026

Committed d86b3ad/d125304/14bf152/d3f93f8/44a36d4/ddf9b83. Final91 relevant unittest tests passed (retrieval29, storage31, embedding12, ledger19), all exit0; fresh reviewer no remaining P1/P2. Three review regressions fixed, runtime-RPC exact allowlist updated, live statement-publication isolation proven. One infrastructure timeout unreproduced and checkpoint encoding corrected; final results/limits in handoff. External model weights/tokenizer/config hashes freshly recorded, no downloads or model execution. Hosted security read-only baseline zero lints; local shared releases/pointers/disposable databases zero.

Phase05 checkpoint/handoff now blocked, plan retained in_progress on master section10 approved-development/model/source-file gate; checkpoint retained and INDEX updated. Synthetic manual-vector recall/unsupported measurements do not approve institution policy. Shared/local/hosted migration deployment NOT RUN. Candidate corpus/pointers inactive; default retrieval policy uncalibrated. Branch stays local with explicit verified commits; documentary closure follows.

Exact next action: owner identifies approved source-backed development-case paths and an existing compatible Python3.13 encoder environment (or explicitly authorizes setup). Run real-model matching/source citation/development calibration gates, then reviewed migration workflow before shared runtime use and earned handoff/can-advance. Pending text question is not answered by elapsed time. Do not redo Phase04/Phase05 delivered software, install dependencies without authorization, reset shared data, or begin Phase06.

Ruling: retain plan status in_progress with blocked checkpoint/handoff; phase_state.py selects only ready/in_progress plans. This keeps Phase05 the active recovery phase and cannot authorize advancement.

## Phase05 owner resume: source-backed development practice exam

Owner requests continued Phase05 TDD and a small dev practice exam with correct answers/correct source. Clean73934a3 recovered; stale checkpoint pointer repaired. Existing original BSCS prospectuses locally available despite historical E: drive absence. Both originals visually inspected via native Windows PDF rendering, no package installs. Chosen bounded12-question candidate exam includes en/tl/Taglish, direct rows, cross-edition differences, missing curriculum clarification and unsupported/wrong-program controls. Real gold institutional passages/answers and generated reports remain external; only reusable checker/grader, synthetic tests and plans committed. Formal approved-development/model gates unchanged. Next: focused RED tests, checker/grader GREEN, external packet/source hash validation and regressions.

### Source-bound practice exam checker/grader verified

12 TDD unittest tests pass after missing-module RED and focused citation primitive RED. Checker verifies original bytes and gold locator metadata; grader separates fixed-answer/control/source agreement, rejects wrong editions/citations and counts missing responses as failures. It does not approve sources, perform model inference or claim a replay as a benchmark. Both BSCS original PDF byte hashes and standing/practicum crops checked externally; no source changes. Next: readable question/key CLI and external real-source12-case packet.

### Phase05 original-backed practice exam exported

19 new TDD tests pass0.100s. External12-case/8-family exam, question sheet, source-bound answer key and validation report created at C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-dev-exam-20261012. The initial Coding-projects audit directory was discovered inside another Git root; only our artifacts moved to a verified external path, originals preserved. Four en/four tl/four Taglish, nine answerable/one curriculum clarification/two insufficient-evidence controls. Byte hashes and visual row/bbox checks performed; independent approval/production cell mapping/real retrieval run remain pending. No fabricated observations or score, no LLM answer generation. Next: final fresh review and affected regressions.

### Fresh practice-exam verification environment

19 practice-exam TDD checks pass. Full retrieval rerun found Docker daemon unavailable (missing Linux-engine named pipe), so DB fixtures could not start; no data changes and no passing DB claim. Run22 non-DB retrieval units plus embedding/ledger regressions independently; no Docker startup or installs. Fresh code/source-answer reviewer running. Final answer-key observations remain absent and no model score claimed.

### Practice-exam fresh review fixed

Reviewer confirmed original-backed answer/source correctness and found one P2 linked output file bypass. Two synthetic hardlink RED regressions now GREEN; exporter refuses existing symlink/hardlink/non-file outputs before writes.21 new tests pass0.234s; reviewer9 CLI tests pass0.179s with no remaining P1/P2. Wrong-program question scope records explicit BSIT/unknown edition; BSCS source is only background. Correct source identity/answer key remain candidate, no human source approval or real observations. Final combined unit regressions and export validation rerun; commit/report/handoff updates next.

## Phase05 source-backed development practice exam delivered

Commits f7534c8/4eedfb6/1fb9d1b/2a497c4. External question sheet/key/packet/validation at C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-dev-exam-20261012; repository report phase-05-practice-exam-report.md.12 questions,8 groups, four per en/tl/Taglish; originals visually read and hashes match existing pending CSV. Candidate proposal remains proposed, never approved.21 new TDD tests, final43 new/retrieval unit checks +12 embedding +19 ledger =74 passing; fresh review fixed one P2 hardlink bypass and now clear. DB-inclusive rerun attempted but Docker absent; no container start, no fresh DB pass or shared writes. No source-derived gold in Git, no fabricated observations/score, no model execution/dependency change.

Next action: independently review existing packet/source applicability, map source row locators to production span/cell IDs, use an authorized compatible model/database environment and record real development observations. Formal Phase05 gate remains blocked; checkpoint retained, handoff updated, no Phase06. Do not repeat delivered exam or old Phase04/Phase05 code, activate candidates, or interpret source-byte validation as institutional approval.

## Phase05 balanced college expansion: Superpowers design approved

Owner requested all-college diversification and dataset location/relocation documentation, then selected27 questions balanced three per college through the Superpowers bounded-design gate. Read-only inventory sees39 PDFs/nine folders:CAD CAH CBA CCJE CHTM CNHS CoE CS CTE. Preserve original12-case artifact, create new27-case external version; one English/Filipino/Taglish case per college. Current deep dataset root will be recorded in plans/dataset-locations.md plus AGENTS/INDEX routing, with relative packet paths/explicit --source-root preserved for future relocation. No source move/download/activation. Original-page rendering underway; next TDD coverage checks and source-backed case authoring.

College expansion implementation: ten new TDD coverage tests GREEN with21 existing exam tests (31 passed); missing live college, wrong evidence folder, language/count imbalance and relocation covered. Added dataset location guide linked from AGENTS/INDEX. Source originals unchanged; separate27-case packet still being authored externally. Next: source-row review, export, fresh reviewer and regression gates.

Owner location correction: code remains in isolated worktrees/Bintanong/p05; main checkout is workspace/Bintanong. Both exam versions moved into workspace/audit-evidence, ignored/untracked. New explicit private export checks Git ignore status in every ancestor repository;34 exam tests pass with workspace-contained temp root. No original PDF/model/main-checkout moves.29-test DB-inclusive retrieval gate now freshly passes (Docker externally available), prior unavailable-Docker notes are historical. Next: final review, verification and documentation closure.

Final college delivery:27 cases/26 dev groups/10 originals; CAD/CAH/CBA/CCJE/CHTM/CNHS/CoE/CS/CTE each3 with en/tl/Taglish one each.25 answerable/one clarification/one wrong-program control.94 distinct checks passed;34 exam plus full29 retrieval included. Fresh source/correction reviewer no P1/P2; original12 four hashes preserved, all task artifacts and current temp/raw evidence within workspace/audit-evidence. Latest check confirms no Coding-projects/workspace Git ancestor; previous marker observation is historical and no agent Git deletion. Verified code317bf54; final documentary closure follows. Phase05 blocked solely on independent source/answer approval, ingestion locator mapping and real matching model/runtime observations; no Phase06 or activation. Exact next action: institutional/domain review of prepared27-case key then real retrieval measurements in an authorized compatible environment.

Owner proceeded with source/citation/model recovery. Fresh environment discovery: only systemPython3.13.7, no local model/PDF libraries, no workspace venv, no embedding Docker container/image, no persisted actual cell/chunk artifacts in either PDF dataset or main artifacts. Preparing39-source pending register/translation and27-case independent review/mapping records; do not fabricate span IDs or institutional approval. Exact dependency proposal will remain reviewable before any install.

Readiness preparation verified:39 original hashes match inventory; nonsynthetic pending register records allparse;10 exam IDs map to byte-derived pendingversion IDs.27 independent review rows and28 unresolved actual-ingestion locator requests exported within workspace; no gold-derived corpus/observations. Strictencoder rehashedassets/promptthenfailed absent sentence_transformers. Local/hostedDBread-only counts allzero.34 exam tests pass0.840s; two pytest module imports fail absentpytest (notpassing). Fresh reviewer noP1/P2. Exact pinned environment requirements/setup prepared forowner review; next actionexplicit installation authorization or existingPython3.13 environmentpath before dependentwork. Institutional authority/approved labels and productioncell mapping remainopen.

Owner explicitly authorized reviewed pinned dependency installation in isolated readiness/venv. Starting prepared setup, all downloads/cache/tmp/logs in workspace. Existing model files read in place, no extra model downloads or shared source activation. Next: dependency check, real model/PDF execution and source mapping.

Environment/encoder increment: isolated pinned dependencies installed, pipcheck clean; targetedpytest67 pass/19subtests. Realmodeloffline27 queryvectors + source-only documentprobe verified; raw original PDFium39 PDFs/43pages/28 citedcharacterregionsresolved, no original changes. ProductionDocling conversion blockedmissingmodelassets whileoffline; no modeldownloads. Wholepytestrunning withonefailurecurrentlyseen; nextfinalsummary/rootcause and missingassetinventory. Realrankings/calibration/sourceapproval stillpending.

Wholepytest nowexecutable: first4898pass/7fail/5skip. Rootcausefourrepairablefailures fixed (legacy canonicalimport + three publicTyperexceptionassertions); Windows symlink capability skippedwhenunavailable. Focused47pass/2skip/oneassettestdeselected, fixescommitted; whole rerunpending. Two realDoclingintegrationtests remainblocked byadditional modelassets not includedinpackage approval. Exact metadata proposalHeron171.66MB + accurateTableFormer212.77MB, pinnedcommits/files/SHA recorded, no downloads.

Final installed increment: realmodel27queries + source-onlydocument probe verifiedoffline; PDFium39originals43pages28glyphregions, no changedbytes orfakeDoclingIDs. Setup/pipcheckcomplete, runtimeTorch2.14/ ST6.1/transformers5.19/tokenizers.23.3. Finalfullpytest4902pass/107subtests/6skip/2fail405.12s after fourcode/testfixes andsymlinkcapabilityskip; remainingtwo realDoclingparse tests needmissingassets. Freshreview noP1/P2, allsource/vector/geometry audits checked. Exact5-file384.43MB Doclingdownload proposal committedasmetadata only, modeldownloadpermissionnotcoveredby priorpackageapproval. Newproposedmodelcache staysworkspace onownerinstruction, existingMODELS untouched. Next exactassetauthorization/existingpath, thenproductionconversion/cellmapping andinstitutional review/retrievalmeasurements. Do not reinstall or inventformalphase completion.

Owner approved the exact five pinned Docling assets. Download completed: two repositories, five files, 384428156 bytes; immutable commits, sizes and weight/config digests verified in workspace readiness/hf-cache. Existing MODELS untouched. Phase05 resumes offline conversion and original-source cell/chunk mapping; runtime ranking evidence follows only where audit permits. Supabase retrieval migration already implemented/tested in disposable databases, shared deployment still unapplied; no LLM answers or institutional approval inferred. Checkpoint reconciled to clean baseline645d14a before this documentary update.

Offline Docling recovery verified: documented DOCLING_ARTIFACTS_PATH exposes five verified workspace hardlinks without extra downloads. Original CAD PDF converts61.042s; both previously blocked real converter tests pass65.66s. Existing39-source pending-candidate ingestion now running with original bytes only, plus full pytest rerun. Gold exam excluded from corpus construction; audit errors remain blocked. Next: inspect all conversion outcomes, actual cell/span mappings and candidate-only ranking opportunities, record honest coverage failures before institutional review.

Checkpoint at18:07:15/39 original candidate bundles completed, no observed conversion exceptions; structural audits mixed, some sources emit validated chunks while failed audits remain empty. Full pytest still running. Actual Docling region mapper is prepared and will be rerun after all39 outcomes; geometry remains field-review-pending and no database span IDs are invented. Candidate cosine experiment reuses strict real query/document encoder and exact token guard, explicitly reports offline byte-identity filters rather than authorized scope/runtime evidence. Fresh final independent reviewer checking approved model assets, original/bundle hashes and script boundaries. Next await completed outcomes, rerun mapping, execute real candidate diagnostic, inspect final review/full-suite results and document recovery conditions.

First-pass39 attempts complete:37 bundles/two JSON serialization failures in Electrical Engineering/Marine Biology. Pre-fix fullsuite4904pass/107subtests/6skip/6warnings752.06s. Original captured evidence confirms None semester alongside Summer in derived term tree. Two synthetic tests reproduce exactTypeError RED; minimal86c2720 omits unplaced courses from derived index, preserving original unknown fields/full courses and audit gates.50focusedpass36.56s; reviewer2pass0.52s/noP1/P2. Electrical retry converted80.088s, one unplaced course retained/audit error/0chunks; Marine retry and post-fix whole suite running. Actual Docling mapper final snapshot27/28regions with spans,3 with emitted chunk links; source/field ownership pending. Next preserve/reconcile retry outcomes, actual strict-model candidate cosine experiment, final artifact review and full gate documentation. No shared DB writes, source approval, LLM answers or Phase06.

Final authorized execution complete: both retries succeed,39bundles revalidated/originals unchanged,33audit error/6warn/336chunks/34binding+34extractor rejections.129actual spans near27/28goldregions,10links across3regions; field ownership pending.336finite normalized1024document vectors/exacttokens within512 match27realquery config; candidate cosine diagnostics244.835s show only3cases with same-byte chunks, no Precision/Recall/calibration/runtime-approval claim. Independent reviewer rehashes/reloads/recomputes all evidence, three document vectors replay exactly, noP1/P2. Post-fix wholepytest4906pass/107subtests/6skip/6warnings571.49s.64-file raw manifest189c5362314725494a80bb70372025f28da3daef13e397245832acbc8f51493f; all underworkspace/audit-evidence. Five old-process failed-audit term projections preserved/0chunks, listed in report for regeneration with extraction repair. Code86c2720/documentary baseline1eeb21a; closure Git commit follows. Checkpoint/handoff blocked on33failed audits/unresolved geometry/source applicability and approved-release retrieval. Next use captured raw evidence for targeted extraction/field repair and independent source/answer review, then approved runtime calibration and reviewed shared Supabase migration. Do not repeat installed/downloaded assets or whole39conversions/336vectors; no deployment, activation, invented approval or Phase06.

Final documentary closureb3f2149 clean; phase-ledger19unittest checks pass11.657s,exit0. Actual inspector valid/Phase05 active/blocked/cannotadvance; metadata names pre-documentary verified HEAD rather than an impossible self-referential commit. Final verification note updates checkpoint/current progress only, with following clean Git SHA discoverable from Git. No further production work or background ingestion/encoder tasks remain.

## Phase05 account/session continuation — 12 October 2026

Owner requests continuation from the previous account and explicit TDD/appropriate SKILL.md requirements in AGENTS. Read INDEX/readiness/master section10/checkpoint; clean baseline75457b2, activePhase05 and blocked handoff reconciled. Existing dependencies/assets/39conversions/336vectors must not be repeated. Next: diagnose saved extraction audits and geometry, reproduce a confirmed defect RED with synthetic tracked fixtures, implement minimal GREEN repair and regenerate affected candidates. Institutional review/approved runtime calibration remain separate exit gates.

### Spanning-row TDD increment

One rendered original confirms a single6-unit placement row; saved converter projects its core cells across three rows and prerequisite across two cells. Two synthetic failures reproduced; minimal cell-identity continuation correction now11tests/13subtestsGREEN0.87s. Distinct identical source rows preserved. Full suite/cached39-source regression and targeted regeneration/review next; current dirty files sections.py, new tests and phase/progress notes.

### Corpus differential and correction

Final comparison reuses39 verified saved conversions with original hashes/settings checked, changes only Financial Management (50→49courses,152→146units,error→warn); other38 unchanged. First comparison caught missing-title repetition, reproducedRED and correctedGREEN;50focusedtests/13subtests pass3.60s. Separate original-PDF regeneration now running, historical sealed candidates preserved. First fullsuite began before latest fix; finalcode needs a fresh fullsuite. Reviewer update pending. Decision record docs/decisions/prospectus-spanning-course-identity.md added.

### Targeted regeneration / final verification running

Verified new candidate Financial Management bundle49courses/146units/54chunks,56.823s; pending authority untouched, prior outputs preserved. Overall latest-source mix32auditerrors/7warnings/390candidate chunks; old336vector snapshot preserved and54new embeddings running. Three exam cases still have same-byte chunks. Final reviewer nofindings,151binding/chunk checks pass; fresh finalcode fullsuite running. New39-row extraction review queue remains pending. Next: inspect final encoder/fullsuite results, seal recovery evidence, update phase report/checkpoint/handoff and commit.

### Finalcode verification / requested owner guidance

Finalpytest4912pass/107subtests/6skip/6warnings371.98s,exit0; phaseledger19pass10.561s. New54realvectors verified71.438s and independently QAchecked; existing64sealed evidencefiles unchanged. Owner has not reviewed sources and requests guidance/workspacefolder. Created audit-evidence/phase-05-owner-review-20261012 with START-HERE,27editablecase decisions,10sourceauthority decisions,10hashmatchingPDFs/12pageimages and preserved examcopies. All labels remainpending; readerQA/documentclosure next. Verified parser/test/decision commit follows.

### Resumed verified closure and owner review

Instructions670d948;parser/test/decision280a287. Full4912tests/107subtests/6skip/6warningpass371.98s;phaseledger19pass10.561s. Current mix32errors/7warnings/390chunks/vectors,still3examcaseswithmatchingchunks. Ownerreviewkit at C:/Coding-projects/bintanong_workspace/audit-evidence/phase-05-owner-review-20261012 fullychecked27cases/10PDFs/12pageimages/76links; all labels pending. Ownerhasnotreviewedyet. Start START-HERE.md,edit REVIEW-DECISIONS.md andSOURCE-AUTHORITY.md; thenreconcile actualdecisions andcontinuefailed extraction/fieldreview beforeapprovedruntime calibration.41-file recoverymanifest528ea76ece58705e75365df2ce4e4577f6f8a594d24cedbe1d59f9aef321f6bf. Documentarycommitfollows; noPhase06/sharedchanges.

## Corpus scope clarification — 12 October 2026

Owner asked why prospectuses were reviewed inPhase05 and reports handbook and
Citizens' Charter missing, intending to add them and request organization later.
Context thesis physical pages36/55/68 identifies handbook, Charter andUSG/CSG as
core institutionalRAG sources and prospectuses among private supplemental inputs;
master permits separately verified institutional curricula. Phase05 retrieval
can retrieve source statements, while Phase06 authors/tests executable rules.
Current27case prospectus exercise prepares reviewed evidence and tests a
curriculum subset; it cannot validate handbook/Charter retrieval. Repairing all39
prospectuses is not a prerequisite stated in mastersection10. Scope clarification:
plans/phase-05-corpus-scope-clarification.md. No files moved or new inputs presumed
received. Next: owner adds policy files and later requests organization; inventory
actual files/versions/scope then prepare policy/procedure development cases.
Prospectus review/source approvals remain pending and Phase05 remains active.

## Prospectus review deferred — 12 October 2026

The owner can set aside the 27-case prospectus review for the current Phase 05.
Keep the packet and extraction evidence for Phase 06 curriculum preparation;
review applicable source facts before compiling or activating their Prolog rules.
Phase 05 now prioritizes handbook, Citizens' Charter and other policy retrieval,
including reviewed development answers and citations for those sources.
Deferral does not approve prospectus fields, score their cases as verified,
remove evidence, complete Phase 05 or begin Phase 06.

## Dataset organization authorized — 12 October 2026

Owner supplies handbook/Charter and requests category/year folders, prospectus
preservation, deferred future college/organization sources, Gitignore protection,
Context in the existing handoff loop and enough next-CLI context. Baseline7082d59;
42source files inventory includes two loose policy PDFs. Visually confirmed
Charter2025/4th edition117pages and handbook2021/394pages (approval2020separate).
Dataset now ignored; Context routing added to AGENTS and existing handoffskills.
Plan: plans/2026-10-12-policy-source-recovery-plan.md. Historical ingestion support
exists; recover actual source governance/conversion instead of restarting code.
Collection only4919cases/1816definitions/124modules; redundancy not assessed.
Next: safe folders/two moves, pending source register, byte checks and handoff.


### Verified directory organization and instruction reader check

Moved only two policy PDFs into CitizenCharter/2025/University and
StudentHandbook/2021. All42original file hashes retained,40prospectus-tree paths
unchanged;2pending byte-derived source contracts minted,approvalnull. Created
requested2024..2027/UnknownYear folders and deferredfuture areas. Fresh reader
followed new Context loop and consulted actual thesis/diagram. Stale primary
pointer and accidental leading+markers corrected; finalhand-off update next.
No productcode/test additions, conversions, model/download/dependency changes
or source activation. Next: guide/nextCLI handoff, then fresh filesystem/ledger
checks and explicit small commits.

### Organization/handoff completion and owner status clarification

Final file/Git check rehashes all45dataset files against afterinventory, confirms
40prospectus paths unchanged and42original bytes preserved; all45files and root
probe ignored, no tracked originals. Current CLI ends with documentation handoff;
owner questioned scope, and status clarified completed organization/instructions
came from prior request. No policy ingestion, embeddings orruntimechanges run.
Dated next-CLI handoff contains currentpaths/hashes,printededition2021vsapproval2020,
117/394page source limits,existingPhase1/2 support,missingactualbundles,offlineenv,
deferredsources,test-count facts,and explicit continuation prompt. New source
contracts/metadata remainpending. Final ledger/doc checks and documentationcommit
follow; nextimplementation awaits ownercontinuation in nextCLI.

### Final handoff ready for a clean-context CLI

Independent file/readerQA passes:45currentfiles checked,42originalbytes preserved,
40prospectuspaths unchanged,2pendingcontracts,117/394pages,folders/deferredscope
and Git exclusion verified. Finalhandoff is plans/2026-10-12-phase05-next-cli-handoff.md.
Owner asks a short appendable prompt; exact nextactions/boundaries already recorded.
Finaldocumentarycommit follows validated ledger/diff; no additional implementation.
