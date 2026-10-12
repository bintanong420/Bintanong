---
artifact: phase-checkpoint
phase: 5
status: blocked
sequence: 49
plan: plans/phase-05-retrieval-plan.md
head_commit: 94f01b3
working_tree: policy_text.py, procedure_text.py, test_procedure_text.py, checkpoint/progress, handbook record and ingestion decisions
updated_at: 2026-10-12T22:35:00+08:00
---

# Phase 05 checkpoint

## Completed Tasks

Recovered Phase 04 corrective handoff, verified clean baseline and owner start instruction. Phase inspector: valid, can advance yes. GitHub MCP confirms merged PR 6. Hosted MCP: PostgreSQL 17.6, vector 0.8.2, zero releases/active pointers.

## Current Task

Owner authorized the next bounded task: whole394page Student Handbook candidate
ingestion. Clean baseline d58b830; fresh snapshot matches original4c9a95bf...351c8
and existing pending contract. All45dataset entries unchanged. Existing offline
environment/assets retained; checkpoint before long conversion. Image-only cover
is retained as a review gap, not silently OCRed. Charter427candidate chunks and
3table rejections preserved; no activation, embeddings/rankings orPhase06.

Whole-source conversion completed922.075s then reader refused accounting; raw/meta
retained. Actualgraph5731texts/133tables/433pictures;83native texts under pictures
were skipped.8synthetic regressions RED0.96s; minimal guarded picture-container
traversal GREEN141passed/1skipped27.69s. Actualreader now accounts for5864refs.
Replaying exact retained raw into fresh candidate output; no second PDFconversion.
24original pages rendered; sparse native-text pages include images/dividers and
blank bodies. Physical31–34requirements/waiver clauses and46/47/144/355grade
contexts inspected. Original timing wording on47needs interpretation; preserve
source conflict and distinguish undergraduate/graduate/laboratory/law sections.
No candidate completion claimed yet; retained Docling dropped-cell findings pending.

## Repository State

Isolatedp05,feat/p05-retrieval-logic; clean resume baseline3d464be reconciled.
Verified commits5940d93pre-run checkpoint,ab4a6ecretention/hierarchy andc061238final
table/reference correction. Following handoff/documentation closure HEAD found
through Git, avoiding self-referential metadata. Only explicit task paths staged;
clean tree after closure expected. Raw evidence in workspace
audit-evidence/p05-policy-source-recovery-20261012. GitHub MCP confirms remote
dev10bfd6f; Phase05 remains local. No setup/dependency change, dataset move,
database write, runtime/Prolog execution or activation.

## Verification Evidence

Current handbook preflight: approvedPython -B <handbook-evidence>/run_handbook.py
preflight, exit0;394pages, original SHA256/pending version match and45unchanged
dataset entries. Context thesis36/55/68 and routingPNG consulted, master6/7/10
reviewed; no scope discrepancy. Full product tests below are prior Charter-code
verification, not a fresh handbook-run result. No product code change yet.

Current policy task: candidate bundle/source invariance verified; focused hierarchy
suite130passed/1skipped51.30s before final table/ref correction; final correction
5targetedGREEN0.40s and actual428item sourcegraph succeeds. Whole final-code run:
4failed/4921passed/107subtests/6skips367.13s. All4failures are help subprocess text
decoding(cp1252 parent versus UTF8 child output), not reader failures. PYTHONUTF8=1
resolves all4help checks(4passed2.07s), with no code/dependency change. Fresh full
UTF8mode rerun4926passed/107subtests,6skips/6warnings362.06s,exit0. Phase ledger19tests
pass14.221s. Prior source/prospectus verification below is historical.

Finalcode4912pytest/107subtests pass371.98s,6skips/6warnings,exit0;19phaseledgerunittest pass10.561s. Focused50/13subtests pass3.60s; independent151chunk/binding/parser checks/13subtests pass18.08s. Same-input39source cached differential changesonlyFinancial Management,originalhashesunchanged. Oneoriginal regeneration56.823s emits54chunks; strict54newembeddings71.438s,tokens78..337,normdeviation<=1.11e-7; independentartifactQAclear. Allprior64sealed filesunchanged; new41-file seal528ea76ece58705e75365df2ce4e4577f6f8a594d24cedbe1d59f9aef321f6bf. Ownerkit27cases/10PDFs/12images/76links verified,allreviewdecisionpending.

## Versions and Digests

Python3.13.7; isolated approved venv pins Docling2.133.0,docling-core2.101.1,docling-parse7.22.2,Torch2.14.0,sentence-transformers6.1.0,transformers5.19.0,pytest9.1.1. Existing PostgreSQL17.6/vector0.8.2. SEA-LION remains under MODELS, freshly verified weights SHA-256 df5b1c55623eeb5ef09ce3f3c50e24e2db433d7d1bbcccf76d2f01ba212df5f1 and tokenizer883b037111086fd4dfebbbc9b7cee11e1517b5e0c0514879478661440f137085. Five separately approved Docling assets in workspace cache, exact immutable commits/digests in readiness report. System interpreter and repository dependencies untouched.

## Decisions

Ruling: owner instruction to execute Phase 05 authorizes the existing written master/prepared design; refine task details inline without a redundant design-approval loop.

Ruling: retain the adapter's model-specific Retrieval instruction prompt, verified in local `config_sentence_transformers.json`; replacing it with generic `query: ` would invalidate matching configuration.

Ruling: pin active release in a single STABLE invoker RPC; stale pins return release_changed. No superseded access or RLS relaxation. Costs a retry after publication.

Ruling: keep legacy adapter compatibility; Phase 05 strict wrapper forbids its synthetic fallback and network loading. Mock encoders are explicit test-only injections.

## Known Failures or Blockers

Current policy gates:3retained Charter table rejections and Docling dropped-cell
warnings; source-owner printed time-total discrepancy; pending acquisition,
issuer/applicability/effectivity and independent source/content review. Handbook
conversion, actual policy embeddings and approved retrieval calibration not run.
Fullsuite UTF8mode rerun passed. Deferred prospectus findings below are historical
context; they do not replace the current policy-source next action.

32latest-source extraction audits stillerror andemit0chunks. Only3/27examcaseshave same-byte chunks; geometry remains27/28candidate targetswith field ownershippending. Financial Management rawsuperscript/prerequisite readingorder remainsunreviewed despite repaired146-unit checksum. Ownerconfirms noanswer/source reviewyet; applicability/authority/domainapproval andapproved-release calibrationremainopen. Historical336vector diagnostics unchanged,new54vector cohortseparate. Noadditionalasset/installblocker.

## Next Action

Run whole394page handbook through existing run_ingestion using policy_candidate
and its existing pending contract into fresh handbook-candidate output. Capture
status/stdout/stderr externally; validate completion with load_candidate_bundle,
all page/item/table accounting, retained rejections and unchanged originals. Use
PYTHONUTF8=1/PYTHONIOENCODING=utf-8 and existing offline assets. If refused, preserve
raw diagnostics and diagnose before any synthetic RED/GREEN correction. Do not
reconvert Charter, move originals, repeat setup or advance Phase06.

Current exact recovery action supersedes initial run: finish existing retained-byte
replay, validate new handbook-recovered-candidate output, perform source/accounting
and sampled checks. Run full product suite on final code and read-only review of
picture traversal; commit verified increments. No repeated expensive conversion.

## Do Not Repeat

Do not redo Phase 04 corrective implementation, replay/reset shared databases, download model weights, activate candidate corpus or interpret synthetic labels as institutional approval.

## Approved asset execution recovery

Five approved files downloaded and verified:384428156 bytes, layout Heron commit8f39ad3c0b4c58e9c2d2c84a38465abf757272d8 and TableFormer commitfc0f2d45e2218ea24bce5045f58a389aed16dc23. Workspace hf-cache snapshots linked into workspace docling-artifacts, exposed through supported DOCLING_ARTIFACTS_PATH. Offline original CAD conversion succeeds; two integration tests GREEN,2passed65.66s. Existing MODELS untouched; no extra assets or repository dependencies changed. Existing run_prospectus_ingestion/load_candidate_bundle API now processing39 original immutable sources, gold questions/answers excluded from corpus construction. Full pytest rerun in parallel, both logs/results under workspace readiness root. Candidate audit errors will remain quarantined rather than bypassed for scoring.

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

## Full installed-suite diagnosis and verified corrections

First wholepytest:7 failed/4898 passed/5 skipped/107 subtests447.84s. Exact failures: test_ingest_hardening refusal_exits, alias_refused_before_conversion, alias_created_during_conversion (three obsolete external-click.Exit expectations; publictyper.Exit is correct for pinned0.26.8), writer_boundary_alias[symlink] (Win1314 platformfixture capability), real_cli_stdout_parses_as_json (missing Doclingassets); test_prospectus_entrypoints self_test[legacy shim] (top-level import makes deeprelative contractimport invalid); test_tools_contract syntheticPDFparse (missingDoclingassets). Legacy failure andthreeCLIexpectations reproducedRED. Two-line shimbootstrap fixes canonicalbackend package; assertions usepublicTyperExit, source-preservation checks unchanged; symlinkfixture preflights capability and skips unsupportedplatform. Focused47 passed/2 skipped/one asset-dependent deselection20.76s; coherent correction committed. Wholepytest rerun nowrunning with8 CPUthreads. Assetmetadata-only proposal identifies pinnedHeron3files171.66MB andTableFormeraccurate v2.3.0 twofiles212.77MB, total384.43MB; no assetdownloads. Next: final rerun/readiness/code review, record precise remaining model-asset/institutional prerequisites.

## Final installed-model increment / asset recovery

Whole rerun405.12s:4902passed/107subtests/6skipped/2failed, both realDoclingtests missing offline assets. Exact test names/logs and first7fail diagnoses in readiness report. Current Python3.13 venv isinstalled and pipcheckclean; realmodel27queryvectors + one source-only documentprobe45.035s validated. No ranking observations or quality score generated. Independent reviewer all39hashes/43pages/28glyphregions and27vectors checked, no P1/P2; sourcebinding/aliascontrols intact. Metadataonly modelproposal5 pinnedfiles384,428,156bytes; downloadguard requiresowner approval, no modelsdownloaded. Owner all-new-work-inside-workspace instruction governs proposedDocling cache despite defaultskill modelpath; existingMODELS unchanged. Finaldocclosure follows66bce2a; clean expected afterexplicitstaging. Next: exact asset approval/existingpath, thenactualsourceingestion/mapping; no repeatinstall, fakeDoclingIDs, corpusactivation or Phase06.

## Account/session continuation — 12 October 2026

Owner requests continued Phase05 and explicit repository TDD/skill requirements. Clean Git baseline75457b2 reconciled; earlier head pointerb3f2149 described the preceding documentation commit. AGENTS now records RED/GREEN and appropriate skill use. Next: diagnose failed extraction from saved raw conversions, select a source-backed minimal regression, repair with synthetic tracked tests, then regenerate only affected candidates. Installed environment/assets and prior336-vector diagnostics remain complete. Remote GitHub MCP branch inspection confirms dev10bfd6f; Phase05 branch remains local. No publication or source approval.

## Spanning source-row defect reproduced and focused GREEN

Saved Financial Management conversion emits two6-unit rows sharing exact code/title/unit cellIDs but different prerequisite fragments; original page1 rendered/visually inspected confirms one6-unit placement row. Synthetic regressions observed RED for three projected courses and for accidental deduplication of distinct same-text cells. Minimal sections.py correction keys row continuation to core source cellIDs and absorbs newly encountered prerequisite evidence once. Focused11tests/13subtests pass0.87s. Initial provenance assertion incorrectly included the table header cell, corrected to course rows; this was a test-fixture error, not a product defect. Changed sections.py/new synthetic test module plus checkpoint/progress. Next: full-suite fresh verification, cached39-source before/after regression (no new conversions), targeted candidate regeneration and final independent review. All raw evidence under workspace/audit-evidence/p05-extraction-recovery-20261012. No authority/release changes.

## Corpus differential correction

First cached comparison exposed missing-title projections repeating after the initial repair. Added focused RED (3vs1), corrected missing/missing field comparison without fabricating data;50focusedtests/13subtests pass3.60s. Final same-input before/after comparison across39 hash-verified saved conversions changes only Financial Management,50→49courses/152→146units/error→warn; other38 unchanged. First exploratory helper had two import/key typos, corrected before executing evidence checks. All prior bundles preserved. New decision record explains source-cell identity; fullsuite/regeneration/review pending.

## Targeted source regeneration verified

Final cached39-source comparison: onechanged/38unchanged,32auditerrors/7warnings. Only repaired Financial Management original reconverted into separate recovery/repaired-ingestion/<digest>; verified nested manifests/source/register/binding,49courses/146units/54chunks/4binding rejections/5extractor rejections,56.823s. Original and historical sealed bundles unchanged. Fifty-four newdocument vectors running under existing strict offline encoder; original336vectors retained. Same-byte exam coverage remains3cases because repaired source is not one of the exam's ten selected originals. Independent final code reviewer no actionable findings,12focusedtests/13subtests and151binding/chunk regressions/13subtests pass. First fullsuite4910passed/107subtests/6skips/6warnings423.22s predates latesttest/fix; finalcode fullsuite currently running and its fresh result is required. Review queue has39pending rows under recovery/remaining-extraction-review.csv. Await existing independent reviewer decision-file path requested asynchronously; no institutional approval inferred.

## Final verified code increment / owner review packet

Finalcode fullsuite4912passed/107subtests/6skipped/6warnings371.98s,exit0. Phaseledger19unittest tests pass10.561s,exit0. New54document vectors verified71.438s,exacttokens78..337,1024normalized dimensions,no truncation/refusals; reviewer validates all54actualchunk/config/content bindings,maximum norm deviation1.11e-7. Prior64sealed files unchanged. Overall candidate mix390chunks/vectors,32error/7warnsources,still3examcases with samebyte chunks. OnlyFinancial Management corpusresult changes; exploratory Marine output archived separately after containment checks.

Owner confirms review notyetperformed and requests a workspace folder plus guidance. Prepared audit-evidence/phase-05-owner-review-20261012/START-HERE.md,27-case editable decision sheet,10-source authority sheet,10byteidentical PDFcopies/12pageimages,question/key/candidateJSONcopies/source manifest. All decisions pending; originaldataset/packets unchanged. Packet reader QA pending. Next: commit verified parser/test/decision increment; finish owner guide QA and phase document closure. Then owner reviews printed answers/scopes and supplies authority evidence as available; remaining extraction work continues from saved conversions without inferring approvals.

## Verified resumed recovery closure

Code280a287 committed; allfinal verification and ownerkitQA above complete. Userasks guided review inworkspacefolder; concretekitdelivered, decisionspending. Following documentationcommit identifiedbyGit; head_commit isverifiedcode ratherthan selfreferentialdocumentSHA. Masterplan preserved,activePhase05 blockedhandoffretained, noPhase06.

## Corpus scope clarification — 12 October 2026

Owner questioned prospectus review during retrieval and reported missing
handbook/Charter inputs, to be added before a later dataset-organization request.
Read Context runtime diagram and thesis physical pages36/55/68, master sections
3/6/7/10/11 and prospectus provenance record. Thesis core institutional RAG
sources are handbook, Charter and USG/CSG policies; master additionally permits
verified institutional curriculum sources. Prospectus extraction review supports
source accuracy and later Phase06 rules, while current27cases are a retrieval
subset rather than policy-corpus evaluation. No executable Prolog inPhase05.
All39 repair is not mastersection10's exit gate; source-specific failures remain
quarantined. Clarification recorded in plans/phase-05-corpus-scope-clarification.md.
Clean baseline5f6d096 reconciled; only explanatory documents/progress changed.
No new dataset inventory, move, ingestion, approval, code/test run or advancement.

## Prospectus review deferred — 12 October 2026

The owner can set aside the 27-case prospectus review for the current Phase 05.
Keep the packet and extraction evidence for Phase 06 curriculum preparation;
review applicable source facts before compiling or activating their Prolog rules.
Phase 05 now prioritizes handbook, Citizens' Charter and other policy retrieval,
including reviewed development answers and citations for those sources.
Deferral does not approve prospectus fields, score their cases as verified,
remove evidence, complete Phase 05 or begin Phase 06.

## Dataset organization start / current owner inputs

Owner now authorizes categorization in the existing dataset parent, preserving
prospectuses, edition-year folders2024..2027, deferred college Charter and
organization policies, dataset Git exclusion, and Context in the resume loop.
Baseline7082d59: owner supplied two untracked loose PDFs; no code changes.
42-file external before inventory captured. Charter cover:2025/4th edition,
117pages. Handbook cover visually2021,394pages, with printed2020BOR approval;
folder year follows edition2021. Historical Phase1/2 notes already describe
policy inputs and delivered ingestion; actual handbook/Charter bundles remained
unproved. Supplemental source recovery needed, not wholesale phase restart.
Current edits: AGENTS,both handoffskills,.gitignore,new dated recoveryplan,
checkpoint/currentprogress. All dataset files now ignored. Context thesis pages
36/55/68 and supplied runtime diagram were consulted in prior scope clarification.
Next: verify instruction loop, create folders, move only two loose PDFs after
containment checks, mint two pending identities, hash-verify preserved originals,
and prepare concrete next-CLI handoff. No conversion/activation/new install.


## Context-reader and organization verification

Fresh reader followed both updated skills to thesis physical pages36/55/68 and
visually inspected the routing diagram. Reader clarity findings: stale primary
next-action pointer, accidental leading+markers and historical prospectus-heavy
handoff wording. Primary pointers/markers corrected; final recovery handoff will
record current policy focus. External organization summary verifies42original
files preserved, only2moves,40unchanged prospectus-tree files,2pending contracts,
511policy pages. New plan records source support exists but whole-policy bundles
remain unproved. No new product code/tests, installs, conversions or publication.

## Organization and next-CLI handoff closure

Only two supplied policy PDFs moved;42originals retain bytes,40prospectus-tree
paths/hashes unchanged. All45current dataset files plus rootdataset probe ignored;
no dataset files tracked. Covers identify Charter2025/fourth edition117pages and
handbook2021/394pages with approval2020separate. Two pending contracts minted;
no memoranda or deferred originals supplied, and actual policy conversion remains
NOT RUN. Read-only text profile covers511pages: Charter has nozero-text pages
(page69sparse), handbook physicalpage1imagecover has noPDFtext. No OCR accuracy
claim. Updated Context loop passed a fresh reader; exact source/phase/environment
state and paste-ready continuation prompt are in the dated next-CLI handoff.
Owner status question clarified that this CLI is now finishing only handoff/docs;
no further implementation or broad test run. Current verification is filehashes,
Git exclusion and ledger checks; previous4912pass fullsuite remains historical.

## Independent final handoff/filesystem QA

Fresh reader verified all45after-inventory entries (42originals plus3localmetadata),
all40unchanged prospectus paths,117/394PDFpage counts,2pending contracts,requested
folders and empty deferredareas. Git tracked/stageddataset lists empty; future
photos excluded. No remaining continuation-clarity findings. Checkpoint pointer
reconciled to8f9e922 before finaldocumentary commit; following docHEAD found byGit.
Finalvalidate/diffcheck passed. No producttests or ingestion rerun for these docs.

## Policy recovery resume / pre-conversion checkpoint

Fresh inventory matches45/45 organization entries including40prospectus-tree files;
both contracts synthetic:false/pending/noapproval. PDFium confirms117/394pages,
handbook page1 image-only. Covers confirm observed2025fourth and2021; BOR2020
separate. Charter includes nonstudent services and handbook school/graduate/law
sections: applicability remains section-specific and unverified. Physical/printed
page offset changes within Charter (physical6 printed5; physical69 printed65),
so do not infer a global printed-page offset. Context36/55/68 and routingPNG read;
master6/7/10 and previousPhase04 closure consulted. Existing Docling native-text
settings/OCRoff/accurate tables and local artifacts path verified from current
code and Context7. Owner confirms supplied editions latest available; no further
replacement search. Optional origin details remain pending. PDF inspection script
first hit cp1252 stdout on a thesis bullet; UTF8 stdout corrected, rerun exit0.
No product defect/code changes. Commit checkpoint before long whole-source run.

## Whole-Charter refusal / TDD recovery in progress

CLI exit1 after558.178s: raw reading order omits text or tables. Docling warnings
drop1/158,1/145 and67/67PDFcells from three table grids; logs retained externally,
first rawstage erased by existing temporary cleanup. No root/nested manifest or
candidate chunks. Diagnostic-retention regression PDF/PPTX2RED38.14s; smallest
fix writes raw/meta only after unchanged-source guard, before candidate reader.
Relevant procedure/bundle/policy suites126passed/1skipped79.97s. Source mutation
still refuses raw publication; completion manifests remain success-only.
Context7 documents children on text/table/picture items, not only groups; synthetic
text-parent hierarchy2RED2.58s reproduces currentreader refusal. Minimal text/table
child traversal inprocedure reader and textchildren inpolicy reader now GREEN:
130passed/1skipped51.30s, including duplicate/cycle refusal and source-mutation
guards. Commit this verified increment; actual Charter graph still pending second
capture, so no claim yet that synthetic repair resolves the original.

## Actual Charter graph and candidate recovery verified

Second complete conversion persisted raw11cce11c35151aa4a03af24ea12d4d847729379dd90677b4ddec3c366997fe62
in528.029s. Legacy walk misses30texts:27nested text/group fragments physical92,
3table-owned footnotes physical10/20. Newprocedure walk covers428refs but policy
walk still skips tables. Reviewer independently flags thisP2 and malformed text
descendant reference accepted by tail-only int parsing. Focused RED: tablefootnote
1failed0.53s; malformed ref1failed0.50s; tablecycle1failed0.47s. Guarded policy
table traversal and canonical textref parsing GREEN5tests0.40s; actualreader
accounts for305texts/123tables/428refs. Review excluded source accuracy/authority,
retrieval/activation and historical changes: those remain pending/separate gates.

Exact verified raw/meta capture replayed through run_ingestion in30.429s; new
charter-recovered-candidate validates with load_candidate_bundle. Report:427chunks,
305covered texts,0rejected/omitted texts,120emitted tables,3rejectedtables;117pages,
no pageomissions. Rejections retained:table0physical3ambiguous/missing headers,
table10physical12ambiguous roworder,table94physical92blank celltext. First/capture
Docling dropped-cell warnings retained, not discharged by accounting completeness.
Independent verification matches45original/metadata entries and existingpending
Charter contract; allscope/authority/content states pending.192sample spans across
physical6/7/69/102/103/109/110:175whitespace/NFCexact,17typographic apostrophe/dash
substitutions. Classified findings retained without changing candidate text; no
whole-document accuracy assertion. Printed25minute total versus four5minute rows
remains source-owner clarification. Final wholepytest inprogress; no pass claim yet.

## Final policy-code verification and evidence seal

Finalsuite4926passed/107subtests,6skips/6warnings362.06s,exit0, using approvedvenv,
pytest tests -q -p no:cacheprovider, externalpytest-final-utf8basetemp, existing
offline asset flags andPYTHONUTF8=1/PYTHONIOENCODING=utf-8. Initial4CLIhelp failures
diagnosed as mismatched subprocess decoding;4focusedchecks pass2.07s and whole
rerun succeeds without extra code/dependency changes. Phaseledger19pass14.221s.
Final45entry original/metadata inventory unchanged;70task files sealed with
manifestc3dc18e7693f392e357e6a1fe705b7cb5d9fb2e7ef844cfee2c1e1bd282bd779.
Raw evidence ignored; known3table/source-time-total findings pending. Context/ignore
instructions already delivered, no dataset moves or policy authority promotion.

## Handbook continuation / pre-conversion checkpoint

Owner explicitly says continue with handbook. Clean d58b830 reconciled; priorcode
c061238 remains unchanged. Existing source file394pages matches
4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8. Native-text profile
freshly captured; firstpage image-only as previously observed. Existing pending
record loaded, no authority/scope promotion.45entry inventory matches priorseal.
New ignored evidence root workspace/audit-evidence/p05-handbook-source-recovery-20261012;
run_handbook.py uses existing pipeline, approved Python/assets, same byte-bound
contract, whole original and durable execution status. No new product code/tests,
dependencies, model copy/download, database writes or prospectus review. Context
thesis36/55/68/routingPNG consulted; institutional policy versus private/symbolic
boundaries unchanged. Commit checkpoint before long single-source operation.

## Handbook original-page inspection during whole conversion

Pre-run checkpoint7fe2f07committed. Whole394page pipeline currently running with
existing pending identity, native-text/OCRoff settings and offlineassets. Rendered
24original pages into new ignored evidence, sourcehashverified. Sparse original15
is campusmap image;17organizationchart image;25illustrated BookIdivider;16heading
withblankbody;80/119blankbody/furniture. No blanket OCR/contentcoverage inference.
Physical31waiver requires qualifyingconditions;32/33distinct applicant lists;
34cross-enrollment negative/9unit conditions;46undergraduate/lawtable versus144LES
and355graduategrade contexts. Physical47contains succeeding-term/one-year timing
wording and needs source-owner interpretation; no precedence inferred. All notes
are agentreview, not approved answers or executable rules. Rawconversion not complete;
continue waiting for final manifests/report before any ingestion-success claim.

## Handbook refusal / native picture children corrected with TDD

Original run922.075s,exit1,"raw reading order omits text or tables". Existing raw
retention fix worked:7,533,900byte JSON and718byte source/settings metadata remain
in incomplete handbook-candidate/conversion, no manifests. Actualgraph5731texts,
133tables,433pictures; all83legacyunvisited texts have picture parents/children.
Includes captions/headings/ordinary native text, not additional OCR.8focusedRED
cases0.96s cover PDF/PPTX order plus public policy/procedure cycles/malformed/missing
picture references. Minimal guarded group/picture container traversal in both
readers GREEN141passed/1skipped27.69s; actualreader5864refs succeeds. Existing
order preserved and raw unchanged; no array-order fallback. Exact retained source-
bound conversion now replaying through existing converter-injection/pipeline and
checked consumer. Independent source-content/authority review remains pending.
