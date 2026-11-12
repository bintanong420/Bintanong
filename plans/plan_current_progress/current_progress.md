# Current progress

Updated7November2026. Active development worktree/branch: `p12-dev`.
PR20 merged at `84e7c0db`; original ingestion/researcher merge `0a0fd297` preserved.
No numbered phase started or advanced. Last full progress snapshot: `12f27bd6`.

## Current integrated state

[Reconciliation](../2026-11-07-p12-dev-pr20-reconciliation.md) and
[PR20 checkpoint](../2026-11-07-pr20-execution-checkpoint.md).
- Owner explicitly requested reconciling P12-dev/PR20; PR20 marked ready and merged
  through GitHub with expected source head `12f27bd6`. Local p12-dev fast-forwarded.
- Ingestion preparation/reviewer tools and researcher app preserved byte-for-byte
  from development; student application code preserved byte-for-byte from PR20.
- PR20 includes bounded compound execution, per-topic evidence/presentation,
  server-bound clarifications, language/recovery fixes and concise source controls.
- Recovery `0634d12c` uses one Sources action for curriculum and Handbook evidence;
  affected courses precede recovery plan. Missing evidence retains visible quotations.
- Compiler/compound defaults remain OFF; existing staging opt-ins are unchanged.
  No inferred grades, new institutional approvals or source/database activation.
- Evaluation/ablation work remains on separate `feature/p12-evaluation-ablation`.
  Original thesis evaluation checkout and its owner changes were not modified.

## Verification

- Original215-case backend roster passes across existing environments:187 initially
  passed;28 missing-PyMuPDF cases resolved by system Python3.13, all34 PDF cases pass.
  Reruns overlap; do not sum them.16 PR20 compound pipeline checks also pass.
- Student frontend109 tests and TypeScript pass. Researcher7 tests pass/1 skipped;
  its Next16.4.3 production build/TypeScript pass. Live reviewer document-switch
  case requires an actual launch session and was not run.
- No CI statuses reported on the pre-reconciliation head. Earlier PR20 verification
  and live evidence remain linked in its checkpoint; this is not a fresh full-suite run.
- Historical source/owner72Y acceptance remains qualified, not independent72/72 proof.

## Runtime and next action

No services reloaded for this branch reconciliation. Existing PR20 staging3218/API8023
and separate ablation3219/API8024 retain their previously recorded startup identities.
The new development branch is not evidence that a running3217 process has reloaded it.
No dependency/model installs or downloads. Institutional sources, F04/source gaps,
undergraduate scope and private-context separation keep their established boundaries.
GUI knowledge intake (owner 11 Nov, [plan](../2026-11-11-gui-knowledge-intake-plan.md)). Workflow follows
Binturong `docs/engineering-workflow.md`: one task branch/worktree per step, independent review (Sonnet;
Fable for the DB write), p12-dev as integration. Merged, each reviewed with mutation checks:
steps 1-2 upload + build metadata (`14213e9c`..`285bd93c`); step 3 prepare job (`95f6ab84`,`1f7da136`);
step 4 SessionSlot + `knowledge_update intake` command (`92ce5032`,`b9a94617`); Intake page
(`1594dc6a`..`5d8d3eb5`); step 5 T4 `local_release.stage_draft` (inactive local draft only; exact
127.0.0.1:54321; proxy-free client; Fable blocker D1 fixed). 131 py tests (offline) + researcher 31/1-skip,
tsc, next build. Live smoke 12 Nov via proxy: upload, refusals, real Docling prepare done (3 items, min free
RAM 1.0 GB), open/reopen, build plan; Gemma path and browser click-through untested; T4 never run on a DB.
12 Nov: owner chose the recorded per-side freeze rule. Merged: 5b draft checks (`a73f9999`..`42a687ce`,
retrieval-only, report bound to package digests, Sonnet-reviewed) and step 6 freeze rule + `stage`/`activate`/
`rollback` commands (`f726db15`..`e512ef1f`, Fable-approved, D1-D3 fixed). 194 offline tests pass together.
Fable confirmed: activating a fresh upload is refused by `validate_release` (sources pending, no bound selected
review); the tool never writes approval states or binds reviews. Owner decision needed: may local uploads be
activated before school approval, and if so the governed research route (acquisition verification, source
observation, review receipts, `bind_selected_release_review`, `research-owner-YYYYMMDD` ref).
12 Nov later (owner: one `/review` route, view chunks local+online, side-by-side source pages): merged
knowledge API `bc33ec6e`,`8565a917` (build job; read-only sources/chunks/page/packet items; hosted anon-only
GET, reviewed) and unified workspace UI `e37bcc56`..`13a70dba` (tabs Intake/Documents/Prospectus/Knowledge,
compare extraction, knowledge browser). 322 py + researcher 50/1-skip, tsc pass. Live server: p12-dev, flags
--model-dir MODELS/SEA-LION-E5-Embedding-600M --hosted-env p12/.env --source-root p06/dataset (44 PDFs).
Live UI/UX review passed on real data (560 hosted chunks, 21/21 pages shown).
Merged after review (`feat/ku-documents-library`, through `59e3830d`): Documents "Existing knowledge" library,
documents API + document filter, readable chunk text (crash-safe), page cache, live-review D1-D8, review
blockers fixed, owner intuitiveness goals; UI/UX + antislop + modern-web-guidance skills applied. 353 py +
researcher 67/1-skip, tsc pass. Server restarted on p12-dev; real-data check: 5 hosted documents, readable
prose. Smoke upload deleted; owner upload `55cf92c8332fd964` (USG, prepared) kept.
Next: step 7 + `check-draft` command; owner decisions (activation route, first local stage + container, Gemma/GPU).
Known limit: upload buffers up to ~256 MiB in memory (local single-researcher tool).
Earlier next: owner review on the integrated development branch, then independent human/
benchmark, paired language/compiler and latency acceptance. No institutional deployment
or automatic closure of source PR18/19 is implied by the development merge.
