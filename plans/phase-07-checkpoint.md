---
artifact: phase-checkpoint
phase: 7
status: in_progress
sequence: 24
plan: plans/phase-07-multilingual-routing-plan.md
head_commit: 614e3c3
working_tree: restore evidence-first style and update stage report/plan/index/progress/checkpoint
updated_at: 2026-10-19T11:58:18+08:00
---

# Phase07 checkpoint - independent style delivered, two Taglish failures open

## Completed Tasks

Contracts/resolution/transport/evaluator and scope fix delivered. Two-stage
integration ac00ac9 isolates routing and grounded conversational style using the
same model; one shared repair budget, normal2/max3calls. Original route proposal
and accepted style remain separately observable. No evidence executor or API.
[Stage results](2026-10-19-phase07-style-stage-evaluation.md),
[design/history](2026-10-19-phase07-response-style-design.md).

## Current Task

Retain exact ac00ac9 backend/tests:15/15routes/meaning,13/15styles on existing
15synthetic variants/five families. English5/5,Filipino5/5,Taglish3/5; procedure-
taglish and excluded-taglish still select fil. Explicit span instructions fail
unchanged. Label-first614e3c3 regresses four pure-language cases (11/15styles),
so retired and reverted. No further equivalent prompt trial or host dictionary.
Selected fresh two-stage verification remains pending; Phase07 stays open.

## Repository State

p07/feat/p07-router-taglish-nlp. Routing prompt d019318; retained code ac00ac9.
Restoration checked with git diff --exit-code ac00ac9 -- backend tests.
Other worktrees/dev/p06 preserved; no push/merge or source/registry mutation.
Pre-condensation snapshot:614e3c3:plans/phase-07-checkpoint.md.

## Verification Evidence

Stage RED35failed/18passed ->GREEN127routing tests1.34s. Independent review:
no P1/P2,127passed1.30s. Broad24-file gate1555passed/11subtests179.81s,exit0;
verify-style-stages.ps1/style-stages-regressions.log. Retired label-first gate:
127passed3.38s;1555passed/11subtests141.12s. Restored routing/docs/phase-state gate:
696passed/11subtests12.37s,exit0;restored-style-docs.log.
Two inherited Docling failures disclosed; no whole-project-green claim.

Retained actual composition:15/15proposal/effective/entity/claim/operation
collections correct;5/5consistent families. Six substantive structured checks,
nine empty gold collections.18offset corrections/nine cases;zero repairs.
15exact actual routing captures reused plus15fresh style calls;30logical calls.
Messages/schema/config/runtime identity equality asserted. No replay latency claim.
Failed combined-call, instruction-v2 and label-first experiments preserved and
retired. No final response, institutional retrieval or Prolog execution occurred.

## Versions and Digests

Python3.13.7/Pydantic2.13.5/HTTPX0.28.1/pytest9.1.1/Janus1.5.2/SWI10.1.15.
Existing Gemma at owner-corrected workspace/MODELS/GEMMA_4_E4B,5,126,306,944bytes;
SHA2563cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80.
Official image sha256:4b7be0376002b4450a357a109bab804093ff9251193cc75ed4ce0cb39953ff5c;
llama.cpp b11718-547208dca. Exact prompt/schema/template/case/catalog identities
and commands in stage report; raw:workspace/audit-evidence/p07-implementation-20261019/.
No installs/locks/weight changes. Only Gemma and SEA-LION embedding folders found;
supplied Gemma fills Bintu role, no separate fine-tuned Bintu-1 established.

## Decisions

Context thesis17-18/39-44/58-59/routing PNG and master3/11/12/13 consulted.
After rollover:scope17-18 reread from saved extraction, actual routing PNG viewed.
Thesis SHA256729653540c7991496aceea1f728382d2e2262ca096e4342ce956d072e603c81c.
Master unknown semantics/diagram order govern older illustrative thesis examples.
Curriculum structured/Prolog; handbook/Charter/memos RAG; Hybrid when both needed.
English/Filipino/Taglish preference required; final answers/images later.
Provenance guards cannot prove language semantics. Unknown rules/source authority/
activation holds and Phase06 acceptance stay unchanged; no source review reopened.
Task-owned bintanong-p07-router-offline running for selected fresh verification.

## Known Failures or Blockers

No environment blocker. Two Taglish labels remain wrong with the best verified
candidate. Label-first improves Taglish while damaging English/Filipino; retired.
No separate Bintu checkpoint in supplied folder. Institutional release holds,
four own-rule unknowns, full-prospectus defects and two Docling failures remain.

## Next Action

Commit restored candidate after checks, run selected fresh two-stage requests,
seal evidence and stop only the task container. Preserve language-style exit;
record the concrete remaining model/design decision without another prompt sweep.

## Do Not Repeat

Completed model calls/setup/downloads, native-thinking/compact/combined-wire/
label-first/wording sweeps, source or CSV regrading,75-wording reacceptance,
Phase06 receipt recovery, arbitrary Prolog, activation, merges or other worktree edits.
