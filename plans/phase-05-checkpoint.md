---
artifact: phase-checkpoint
phase: 5
status: in_progress
sequence: 21
plan: plans/phase-05-retrieval-plan.md
head_commit: 6b14254
working_tree: dirty
updated_at: 2026-10-12T17:23:59+08:00
---

# Phase 05 checkpoint

## Completed Tasks

Recovered Phase 04 corrective handoff, verified clean baseline and owner start instruction. Phase inspector: valid, can advance yes. GitHub MCP confirms merged PR 6. Hosted MCP: PostgreSQL 17.6, vector 0.8.2, zero releases/active pointers.

## Current Task

Balanced27-question college exam delivered and reviewed at317bf54: three cases per nine colleges, one per language per college,26 dev groups/10 original sources.34 exam tests and94 distinct relevant checks passed, including fresh29-test DB-inclusive retrieval. Both versions are untracked within workspace/audit-evidence; main checkout preserved. Formal exit blocked on independent institutional/source approval, ingestion mapping and actual matching model/runtime observations.

## Repository State

Isolated worktree `p05`, branch `feat/p05-retrieval-logic`, base10bfd6f, verified implementation ddf9b83. Documentary closure follows this code commit; identify its final HEAD using Git. Expected clean tree after explicit documentation commit. No owner changes overwritten; no push/merge/deployment. Only Phase05 plan/checkpoint/handoff/report, INDEX and current progress change in closure.

## Verification Evidence

Final suites: retrieval29 passed24.814s; storage31 passed76.097s; embedding12 passed0.108s; phase-state19 passed9.579s; all exit0. Fresh reviewer: no remaining P1/P2. Hosted security baseline zero lints. Local shared releases/pointers/test databases zero. CLI help/empty runtime smoke verified. Ledger validate/can-advance run after blocked-handoff creation; Phase06 must remain disallowed. Full commands/raw evidence/limits in handoff.

## Versions and Digests

Python 3.13.7; existing PostgreSQL 17.6/vector 0.8.2. External model assets freshly hashed under `C:/Coding-projects/MODELS`; weights SHA-256 df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1, tokenizer883b037111086fd4dfebbbc9b7cee11e1517b5e0c0514879478661440f137085; complete inventory in handoff/external evidence. System Python has httpx/pydantic but no pytest/torch/sentence-transformers. No installations authorized.

## Decisions

Ruling: owner instruction to execute Phase 05 authorizes the existing written master/prepared design; refine task details inline without a redundant design-approval loop.

Ruling: retain the adapter's model-specific Retrieval instruction prompt, verified in local `config_sentence_transformers.json`; replacing it with generic `query: ` would invalidate matching configuration.

Ruling: pin active release in a single STABLE invoker RPC; stale pins return release_changed. No superseded access or RLS relaxation. Costs a retry after publication.

Ruling: keep legacy adapter compatibility; Phase 05 strict wrapper forbids its synthetic fallback and network loading. Mock encoders are explicit test-only injections.

## Known Failures or Blockers

No approved labeled institutional retrieval cases yet established; formal exit depends on them. Real model execution unavailable in system Python without existing compatible environment; no installs allowed.

## Next Action

Independently approve the balanced27-case packet/source applicability or provide authoritative replacements, map semantic locators to production ingestion spans, and identify an existing compatible Python3.13 encoder environment or explicit dependency authorization. Collect actual matching SEA-LION/runtime development observations and calibration; current DB software gate passes. Do not rebuild either delivered exam or infer institutional approval from validation.

## Do Not Repeat

Do not redo Phase 04 corrective implementation, replay/reset shared databases, download model weights, activate candidate corpus or interpret synthetic labels as institutional approval.

## Task 1 verified increment

Five query tests passed (0.007s, exit 0) after observed missing-module RED. External asset inventory has ten files; actual model.safetensors SHA-256 is df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1 (freshly hashed, matches previous pinned value). Tokenizer SHA-256 883b037111086fd4dfebbbc9b7cee11e1517b5e0c0514879478661440f137085. Inventory retained externally as embedding-assets.json. Changelog fetched and relevant Data API exposure/ownership notices reviewed; retained PG17.6/vector0.8.2 with explicit ACLs, no upgrade. Model execution NOT RUN. Changed files: new retrieval package/query/types, query tests and progress/checkpoint.

## Task 2 verified increment

CLI-generated migration 20261012013339_phase5_retrieval_snapshot.sql passed four real-database regressions after four missing-function RED failures. 4 tests, 4.854s, exit 0. Function is STABLE/SECURITY INVOKER, runtime-only EXECUTE; existing RLS unchanged. Exact scope/edition/entity filters and fingerprint guard tested. Stale/draft pins empty under anon/authenticated. Migration applied only inside disposable databases; shared/hosted deployment NOT RUN. Untracked context/engine tests are intentional next-task RED work.

## Context/pipeline verified increment

Ten context/engine tests pass (0.002s, exit 0) after missing-module RED. Results carry byte hash/version/edition/page/locator, context text/exact token count and settings/encoder fingerprints. Required neighbors are atomic; missing neighbors/invalid citations/budget gaps yield insufficient evidence. Unknown scope stays empty; competing curriculum tags ask for scope, editions expose conflicts. Default policy is explicitly uncalibrated and never claims sufficient coverage. No administrative credential branch. Legacy Phase 01 runtime contract is not changed: debug v1 is a separate internal envelope because it preserves conflicting editions and textless-table citations that legacy RetrievalResult rejects.

## Debug/evaluation verified increment

CLI/metric tests: five passed after missing-module RED; CLI help and actual empty local release smoke verified (release_changed, no evidence/model loading). Full retrieval gate: 25 tests, 19.927s, exit 0; synthetic database evaluation: ten cases x k=3/5/8. At selected synthetic threshold0.9, mean P@k0.200/0.120/0.075, positive R@k1, unsupported detection1; manual vectors/fixture character counter, no real-model or institutional accuracy claims. Report/README/decision added.

Full storage gate initially failed two role subtests because its old allowlist excludes every RPC except match_chunks. Exact-signature allowlist now includes retrieve_context; targeted security test passed1 (2.483s). Full storage rerun pending. Fresh reviewer found two confirmed P2 cases (neighbor curriculum ambiguity and partial-overlap textless table citations); investigation continues. Shared/hosted migration deployment NOT RUN.

## Fresh review corrections verified

All three P2 findings reproduced RED then fixed: recursive authorized same-version neighbor closure, ambiguity checks including neighbors, partial textless table overlap withheld as a whole group with explicit gap. Targeted13 tests passed3.017s; reviewer independently13 passed3.097s and no remaining P1/P2. Controlled publication test proves old statement snapshot plus fresh release_changed (root5.018s, reviewer5.092s). Initial test JSON boolean encoding was corrected; one10s future timeout was unreproduced and its evidence contained the correct snapshot. Allowance now30s for Docker scheduling; no STABLE semantic defect inferred.

Reviewer identified Windows-encoded checkpoint multiplication byte; converted that byte to ASCII and validated ledger UTF-8. Future scripted document edits use explicit UTF-8. Final broad suite running externally; results pending. Hosted security MCP baseline: zero lints, no hosted changes. Full policy/model exit remains gated.

Final retrieval suite:29 passed24.814s, exit0; includes real role SQL, recursive neighbors and live statement-publication isolation. Full storage/embedding/ledger sequence still running. Correction commit follows; checkpoint will name that verified code commit in the recovery handoff.

## Final recovery ruling

Full91 relevant tests and fresh review passed. Master section10 approved-development/source-citation/real-model gate cannot pass with synthetic fixtures or absent model dependencies. Phase05 active plan with blocked checkpoint/handoff, checkpoint retained, INDEX points to recovery. No Phase06 created. Shared migration deployment NOT RUN; default runtime policy remains uncalibrated. Models/candidate corpus inactive. Owner text question for case paths/environment remains pending; no answer or dependency authorization inferred.

Ruling: retain plan status in_progress with blocked checkpoint/handoff; phase_state.py selects only ready/in_progress plans. This keeps Phase05 the active recovery phase and cannot authorize advancement.

## Owner-resumed practice exam

Git clean73934a3; checkpoint prior implementation pointer repaired before new work. E: historical dataset drive unavailable. Original ignored BSCS2018-2019 and proposed2025-2026 PDFs exist in local dataset; both one-page originals rendered with native Windows.Data.Pdf (no install/download) and visually inspected. New sheet explicitly says proposed, so answers describe printed candidate source only. Source-derived exam/answers/passages/PNG/reports remain outside Git under audit-evidence/p05-dev-exam-20261012. Committed tests use invented synthetic evidence. No source/rule authorization, deployment or phase advancement.

## Practice-exam Task1 verified

TDD observed missing-module RED;12 checker/grader unittest tests now pass0.028s. Additional primitive-citation RED reproduced two page bool/float false matches and an unhashable locator crash; exact citation primitives now fail grading instead. Checks cover original byte mutation/path escape, gold source/page/locator/excerpt hashes/bboxes, final-split/approval refusal, fixed-answer agreement, source/control axes, missing responses and both editions for comparisons. Actual original hashes: new600cb36b362cff598d84c66a11598b07593c0e74e78a62658b3c61c89f5d5664; oldc781052fc7242ba520410910f171379721e9bfd0c695b2f0094a3e3981641e4d. Native renders/crops visually checked; printed vs physical page recorded externally. Next: CLI/render TDD and external12-question packet/key.

## Practice-exam Task2 verified

CLI/render missing-function RED observed;19 checker/grader/CLI tests passed0.100s. Additional RED guards now enforce all Git-root/worktree boundaries and refuse stale grading files on ungraded export. The original audit-evidence destination sits under an unrelated C:/Coding-projects Git root discovered during the guard smoke; moved only our new exam artifacts after exact resolved source/destination checks to C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-dev-exam-20261012. Original PDFs stayed untouched. Candidate12-case/8-family packet validated against two original byte hashes; four cases per en/tl/Taglish, nine answerable/one clarify/two insufficient, no institutional approval or retrieval observations. Physical page1 for both; proposed sheet printed50, older sheet printed1. Scope/core row boxes visually checked. Next: final code/source-boundary review and practice/retrieval/embedding/ledger regressions.

## Final practice-exam regression preflight

Fresh new suite19 passed; full retrieval rerun attempted and failed solely because Docker Desktop Linux-engine pipe is absent (no daemon). Two DB fixture failures prevented the29-test suite from completing; no disposable DB created. Do not treat historical29-pass evidence as a fresh run. Unchanged DB/storage code does not justify Docker startup across its existing execution boundary. Practice-exam and22 non-DB retrieval unit checks, embedding and ledger regressions now running independently. Fresh reviewer inspecting code plus actual external PDF answer key, no edits/activation. Source/answer packet remains candidate with grading null; no actual retrieval observations fabricated.

## Practice-exam review correction verified

Fresh review visually confirmed original-backed answers, proposal/effective labels and source/page/bbox locations; found one P2 existing-output hardlink bypass. Both original-source overwrite and gold-into-Git cases reproduced RED on synthetic temp files. Preflight now refuses existing symlink/hardlink/non-regular output targets before any write;21 new tests pass0.234s and reviewer independently9 CLI tests pass0.179s, no remaining P1/P2. Original institutional files untouched. External wrong-program case now records requested BSIT with unknown edition, rather than using the BSCS background source as applicability; answer/key wording unchanged. Final non-DB regressions/readable exports rerun and results in external logs. Next: commit correction and record candidate practice-exam delivery/remaining Phase05 exit gates.

## Practice-exam delivery/recovery checkpoint

Verified code2a497c4, fresh source-boundary re-review clear.12 cases/8 groups, en/tl/Taglish4 each, nine answerable/one needs_scope/two insufficient_evidence. Artifacts outside all Git roots at C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-dev-exam-20261012; packet04f7d3c5d5c793ef8a8aaf7c272690aa0757adb49ee775f30120977cdc55e096, question sheet752032c10141629794b34cbeb13f7d2f56722153f5fc624c927d1187b12ad7eb, key9c48a3ce898904399574d28e2a642d9c9ee77809325773a59c67130cb594159d. Both original byte hashes match pending inventory; originals preserved. Final43 combined units pass0.241s, embedding12 pass0.159s, ledger19 pass12.177s;74 relevant checks.21 new tests and reviewer9 CLI checks pass. DB-inclusive retrieval attempt failed infrastructure; no Docker startup/no fresh DB pass. Gold candidate labels/source authority remain pending; no grading observations/score fabricated. Documentary closure follows code commit; Git identifies actual HEAD, expected clean after explicit staging. See phase-05-practice-exam-report.md for exact commands/limits.

## Owner-approved Superpowers bounded college expansion

Owner explicitly selected27 questions balanced three per college after Superpowers bounded-design review. Fresh inventory:39 PDF paths in nine college folders CAD/CAH/CBA/CCJE/CHTM/CNHS/CoE/CS/CTE, all currently under Tiniguiban - Main. Actual root is backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/PalSU Undergraduate Prospectus Website Dump, with owner relocation intended but not performed. Preserve earlier12-case external version, author a separate balanced27-case version from original PDF reading. Superpowers TDD applies to college coverage checks/reporting; one fresh final review. Dataset guide will be linked from AGENTS.md/INDEX so existing handoff routing finds it, avoiding a new skill or moving originals. Next: write failing coverage tests, implement verified college evidence mapping, document portable source-root usage, complete original-page review and external27-case validation.

## College coverage verified increment

Observed missing college report/validation behavior RED; ten new synthetic-college tests now pass alongside21 existing tests (31 total,0.182s, exit0). Optional declaration validates live PDF college inventory, equal counts/languages, case/source college identity and directory labels; backward compatibility and root relocation verified. Added plans/dataset-locations.md and AGENTS/INDEX routing rather than changing a generic skill. Changed evaluation checker/README, new college tests, guide and phase/progress pointers. Next: finish original-row readings and export separate27-case candidate packet/key; original12-case version preserved.

## Owner workspace location correction

Owner requires all task artifacts under C:/Coding-projects/bintanong_workspace; main checkout is Bintanong, our code checkout is worktrees/Bintanong/p05. Both new exam artifact directories moved from AppData into audit-evidence after resolved source/destination containment checks. Each task folder.gitignore hides all private files from the unrelated Coding-projects ancestor Git root; no parent Git metadata changed. Explicit --allow-ignored-output added after missing-argument RED, three new real-Git regressions GREEN;34 exam tests pass1.313s with TMP/TEMP also inside workspace. Default Git guard/input/hardlink protection retained. Fresh prior review clear; correction re-review pending. Full retrieval29 passed26.629s with externally available Docker (no startup), units53/embedding12/ledger19 pass. Next: final correction review, workspace-path verification, commit and report/handoff closure.

## Final college delivery/recovery checkpoint

Verified code317bf54; documentary closure follows with its HEAD discoverable in Git, avoiding a self-referential checkpoint SHA. Fresh reviewer clear. Final56 combined units/12 embeddings/19 ledger/29 full retrieval pass (94 distinct checks); latest full retrieval includes7 DB checks and runs from workspace-contained temp.27-case/26-group packet,10 originals, balanced nine colleges; question/key digests and all source hashes in report/manifest. Archived12-case four digests preserved. No grading.json in either set and no observations invented. Current evidence roots are outside Git: previously observed ancestor marker now absent, no agent removal. Source location guide/current progress/handoff updated, original dataset and main checkout unchanged, formal exit remains blocked. Expected clean tree after explicit documentary commit; do not repeat delivered work.

## Owner resumes source mapping and real execution readiness

Owner says proceed with the pending citation/model gate work. This authorizes preparation/execution in existing compatible environments, not invented institutional approval or dependency installs forbidden by AGENTS. Clean baseline de54abc reconciled. System Python3.13.7 lacks torch, sentence-transformers, transformers, tokenizers, PDF extractors and pytest; no workspace python.exe/pyvenv.cfg found. Existing running Docker contains Supabase services only, no embedding service/image. Neither current nor main dataset has persisted JSON/cell conversions; artifacts folder empty.39-source provisional inventory stays pending. Next: mint byte-derived pending source register and exam-to-register translation, generate27-case independent review sheet/unresolved-cell mapping requests, prepare exact pinned isolated-env setup for owner authorization. All outputs/work temporaries inside workspace audit-evidence; existing weights read from MODELS without copying/downloads.

## Source/model readiness preparation verified

39 real-source pending register records minted/reparsed via existing contract after fresh original hashes match inventory; approval remains not_requested, scopes/verification/content review pending. Ten exam aliases translated to canonical byte-derived pending IDs.27-case independent source/answer review CSV ready;28 unique semantic locator requests explicitly unresolved, actual ingestion IDs empty. Strict QueryEncoder preflight verified10 localassets/prompt then refused absent sentence_transformers (1.794s); no vectors/observations. Local psql and hosted Supabase MCP read-only counts allzero versions/chunks/spans/embeddings/releases/pointers.34 exam tests pass0.840s. Two additional pytest module imports failed because pytest is absent, not counted passing; no test shim or installation. Fresh reviewer all39 hashes/10 mappings/27 reviewrows/28 requests checked, no P1/P2. Exact project-pinned workspace environment proposal/setup prepared but not executed. Current changes: INDEX, readiness document, checkpoint, handoff/progress. Artifact root workspace/audit-evidence/p05-real-retrieval-readiness-20261012; no source/corpus/database/product-code changes. Next action: obtain explicit owner installation authorization or existing compatible environment path, install/check within workspace if approved, then actual model/PDF ingestion gates; independent institutional review remains necessary.

## Owner explicitly approves prepared isolated dependencies

Owner says yes/go ahead/allow following the exact reviewed pinned dependency proposal. Authorization covers the workspace Python3.13 environment, package downloads/install/checks, existing local SEA-LION model execution and original-PDF inspection. No repository dependency/lock edits, extra model downloads, shared publication or institutional authority inferred. Resuming prepared setup script; installer logs/cache/tmp/HF cache stay in readiness artifact folder. Next: pip check/version inventory, previously unavailable pytest checks, strict local model execution and offline original-source extraction/mapping. Do not request the same package authorization again.

## Authorized environment and real encoder verified increment

Prepared isolated package installation succeeds; pip check no broken requirements, full resolved environment recorded externally. Exact top pins retained, Python3.13.7. Newly executable targetedpytest gate67 passed/19 subtests17.02s (including previously unavailable register/input-snapshot suites). Real strictSEA-LION model loads offline and executes27 originalcase queries plus one source-only documentprefix in45.035s; querytokens50..75/document193/context512, all1024-D vectors normalized, prompt/weights/tokenizer hashes match. No retrieval rankings/scores claimed. IndependentPDFium extraction39 originals/43pages/noempty pages, allbytesunchanged;28 regions resolve to actualPDFcharacters and valid pending SourceSpan contracts, productionDocling IDs remainunmapped. ExistingDocling converter offline probe blocked on LocalEntryNotFoundError missingcached model snapshot; no extra model downloads authorized/attempted. Fullpytest stillrunning, one failure seen sofar; inspect finalsummary/rootcause before any passclaim. Next: complete fullsuite diagnosis and identify exact missingDocling assets, preserve no-activation/source-review gate.
