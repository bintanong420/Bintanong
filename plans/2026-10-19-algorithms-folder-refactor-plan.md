# Algorithms folder implementation plan

> Execute inline with focused TDD and one independent review before delivery.

Goal:provide a dedicated backend/algorithms entry point with canonical mathematical
and generic reasoning code that the panel can inspect,and explicit runtime callers.
Spec:owner's current request;master3/11/13;existing algorithm map;AGENTS scope/source
and workflow requirements. This is organization of delivered code,not a new phase.

## Design and constraints

- Move cosine_similarity and normalize_l2 unchanged into algorithms/similarity.py.
  Existing embedding adapter imports/re-exports them so existing callers still work.
- Move the existing synthetic demonstration into algorithms/nearest_neighbors.py;
  preserve scripts.demo_cosine_top_k as a forwarding command. It remains a reference
  demonstration,while actual database search is public.retrieve_context in migration SQL.
- Move generic curriculum_runtime.pl into algorithms with identical bytes. Point
  bundle preparation and the fixed Janus worker at that canonical file. Preserve
  engine-hash/bundle compatibility and LF checkout attributes;no policy/rule change.
- Add folder README with algorithms,callers,library ownership and presentation order;
  update current developer/module links. Keep historical evidence/handoffs intact.
- No new database SQL,models,dependencies,downloads,source decisions or activation.
  Phase10 remains deferred;the owner handles their branch/worktree switch.

Context consulted:thesis physical17-18,actual routing PNG and master3/11/13. Existing
structured/Prolog,LLM routing and documentRAG architecture remains. Model inference
is unnecessary. Readiness Python3.13;HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE=1 for tests;
explicit test file/method selection excludes legacy model-loading tests.

## Tasks

1. [x] Write regressions for canonical imports/math,old import compatibility,new
   demo CLI parity and bundle validation binding the relocated Prolog source.
   Observe RED;then move code minimally. Verify GREEN and existing actual Janus
   checks. Preserve Prolog SHA256
   e87ebb8cfd06e71b6e5fe15ccec0748487bf8d5044a9b71a7ce14eee1cfd9258.
2. [x] Update folder/docs/source links,byte-preserving Git checkout test and progress.
   Keep all three runtime routes and institutional holds unchanged.
3. [x] Run explicit prior41-file non-DB gate plus new algorithm/demo tests and cosine
   helper test method. Run one independent review,fix substantive findings through
   RED/GREEN,commit cohesive changes and verify clean Git/phase ledger.

## Review focus

Actual runtime must consult the relocated engine,not a stale copy. Existing bundle
hashes must remain valid. Legacy Python imports/CLI must work. No import cycle or
model loading may appear in pure math. Documentation must not imply the reference
Python nearest-neighbor demo runs the live SQL retrieval path.

## Verification evidence

Raw commands/logs:workspace/audit-evidence/algorithms-folder-20261019/.
Python3.13.7 readiness environment;all pytest commands use -B,-q,-p no:cacheprovider,
external TEMP/TMP/basetemp and offline Hugging Face/Transformers flags.

- RED:8failed,1passed,17deselected1.15s;missing canonical modules/new CLI and
  canonical-engine mutation binding failed as expected before the move.
- GREEN:106passed24.20s across algorithm package/demo,one legacy cosine method,
  saved bundles,actual Janus eligibility and dependency tests. No model execution.
- A synthetic bundle saved before relocation validates without any field change.
  Exact engine SHA256 above is unchanged. Windows Git LF roundtrip passes.
- Independent read-only code review found no substantive findings;verified function
  AST equality,engine byte identity,standalone worker paths and Docker inclusion.
- Full explicit non-DB gate:1832passed,63subtests84.51s,exit0. Exact44-selection
  command and environment:verify-final.ps1;output:final-regressions.log.
- Standard Python demo executes without project dependencies;111current local
  Markdown links resolve. Git diff whitespace and phase ledger validation pass.
- Existing handoffs/master/source states remain unchanged;Phase10 remains deferred.
