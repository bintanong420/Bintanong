# Current progress

Updated12November2026. Active development worktree/branch: `p12-dev`.
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
13 Nov owner: review panel broken/verbose/slow, boxes broken, look poor. Fixed: `f6dad397` proxy passes page
geometry (boxes); `345c6926` read-only views reuse a fully checked packet (USG 596 items: state 10.9 s -> 0.15 s,
page 6-8 s -> 0.05-0.4 s, build plan 8 s -> 1.3 s; saves/build/verify keep the full check); panel rebuild
`f5692aaf`..`dc024cb8` (viewport layout, Matches/Fix text/Unclear, windowed list, Tools menu, status badges).
Review blocker fixed: the note is never auto-filled (owner statement); one-click suggestion chip instead.
Researcher 80/1-skip, tsc, build pass; `document-switch.test.mjs` (live launch) not run. Server restarted, USG reopened.
12 Nov Codex resumed Claude's interrupted multi-upload worker; independently reviewed and merged `7dfb301e`.
[Continuation and proof](../2026-11-12-gui-multi-upload-continuation.md): up to20 separate PDFs, sequential
uploads, editable metadata, stop/retry; lost responses require duplicate-risk confirmation. Fixed false
deduplication, Retry cancelling Stop, and panel closure after the first upload (RED/GREEN).95 unit pass/2skip;
browser transport1pass, tsc/build pass. Real production proxy2/2 synthetic uploads confirmed, then removed;
USG reopened596items, source/packet/review log hashes unchanged (derived export regenerated). Hidden intake
PID52268/API8765/UI3050 restarted; new launch link in ignored `ku-multi-20261112/intake.stderr.log`.
13 Nov owner "clean design": `3a7414db`..`e358e001` one token system across all tabs (neutral palette, one accent,
4px spacing, 12-24px type, 4/6px radius), tightened copy; reviewed APPROVE (no behaviour change, AA in light/dark,
390px no overflow, keyboard walk, windowing row height intact). Researcher 95/2-skip, tsc, build. Local Supabase
db/rest/kong started (gateway binds 0.0.0.0:54321 per existing config). Server restarted on p12-dev, USG reopened
(state 171 ms; sources hosted=1 local=5). Then alignment `2fd62577`..`3e3a7f5e` and beautify `b33ec5e8`,`f4318000`
(button font reset moved into `@layer base`, 2px accent focus, title steps, surface panels; 48-run audit: 0 overflow,
min contrast 6.1:1). Real-data fixes `8862f644`..`40fc26b0`: records show the last heading of their heading path (USG titles were
one shared path), Prospectus page title, site icon. Full PDF view `d5946137`..`d1b59066` (Sonnet APPROVE, 5 mutations,
4 caught; unchecked sha-format check is redundant): native browser PDF viewer in Documents and Knowledge via
`/api/source/{id}` and new verified `/api/knowledge/pdf?sha256=`; frame-ancestors 'self' only on those two routes;
review pane decluttered. 372 py + researcher 102/3-skip, tsc, build. Live USG Full PDF verified; restarted on Node 24
with Gemma env, USG reopened. Then note suggestion as a labelled pill `0a05a9ec` and record header
alignment `cf1eee83` (Audience and Save one equal-height row); researcher 102 pass, tsc, build; live USG 1440/390 checked.
12 Nov whole-pipeline startup: images `eb47a413`, on-demand Gemma review audit `f5d77d94` integrated after
independent review. [Runtime receipt](../2026-11-12-full-pipeline-startup.md): student3217/API8022 ready200;
ingestion3050/API8765 with Docling/SEA-LION paths and Gemma configured; local Supabase db/rest/gateway/
Auth/Storage/meta/Studio running. Shared vision-capable Docker Gemma18089 confirmed16384context,
vision=true; native older runtime replaced after model500. Exact transfer-credentials question now
clarifies direction (HTTP200,17.65s), not unavailable; synthetic vision5→15days proposal passes5.03s.
Integrated78Python pass; researcher96pass/3skip, tsc pass; audit browser1pass. USG596items reopened,
protected source/packet/review-log hashes unchanged. No cloud writes/review saves/activation; host RAM tight.
Next: step7 + `check-draft`; local activation route and cloud draft-versus-activation remain undecided.
Known limit: upload buffers up to ~256 MiB in memory (local single-researcher tool).
No institutional deployment or closure of source PR18/19 is implied; hosted stays read-only.
