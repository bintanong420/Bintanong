# Current progress

## Codex continuation (4 Nov; Claude usage limit)

Recovered Claude's three exact tasks and resumed compiler, approved wording and plan-check helpers in their
existing worktrees. [Continuation log](../2026-11-04-codex-continuation-log.md) holds changes, commits and recovery evidence.
Compiler, approved wording and backend plan helpers merged locally. Compiler 71 focused pass; branch broad
2165 pass / 2 xfail; source-backed offline memory 15/15; live compiler memory scenarios 12/12. Integrated checks
underway; API restarted with compile OFF. Plan helpers still need chat wiring; see dated helper report.
Next: finish integrated live off/on conversations/per-college cases; no push or phase advancement.

Updated 31 October 2026 (machine local date). Worktree p12 / `p12-evaluation-harness`.
Phase 12 research/software write-up complete with disclosures; no active numbered implementation phase.
Post-phase test-suite audit tasks 1–7 complete; Claude review passed (nits only). Phase 13 remains cancelled.
Last expanded progress snapshot before condensation: `db643c0`; recover prior history with `git show`.

## Memory and eligibility (3 Nov, owner-requested; branch `feat/memory-eligibility`, worktree `p12-memory-eligibility`)

Owner plan `plans/prolog/Bintanong_Backend_Memory_and_Eligibility_Plan.md`, Tasks 1–4, implemented and pushed
to `origin/feat/memory-eligibility` (3 Nov; no PR yet). The owner's intent (3 Nov): Prolog results are the evidence, Bintu reasons over them and writes
the conclusion, and the chat keeps what the student said. Delivery, verification and open gates:
[results](../2026-11-03-memory-eligibility-results.md). Verified: the full suite has the same 82 failures and 9 errors as
the baseline (missing jsonschema/cv2/docling) and zero new failures; 17/17 source-backed cases pass on the reviewed ledgers.
Live with Gemma, the rerun passed 7/7 turns after four defects found live were fixed (BSCS demo, Civil/Mechanical
Phy 11/L, Lawrence). Model container stopped again.
**Next action:** the other developer (32 GB machine) runs the `curricula` and `recorded` gates with `evaluation/memory_eligibility/` (README there); then owner decides on push/PR.

## Teammate frontend fixes (3 Nov, owner-directed; local commits, not pushed)

Owner decision: chat is locked until a program is chosen (undergraduates always have one); this supersedes the
"skip and ask policy questions without a curriculum" behaviour. BSCS asks the start year: before 2023-2024 ->
`bscs-2018-2019`, 2025 and later -> `bscs-proposed-2025-2026`. `dedea05` light default theme; `f0e86dc` college grouping
(prospectus corpus college folders) and sample sets; `e846fd5` picker beside the chat bar, lock (also refused in send
code), mid-chat switching, scope kept on New chat, Enter hint removed, sidebar logo -> `/`, tinted Learn more, rotating
samples (8 Handbook FAQs). Prerequisite samples are an empty placeholder (`frontend/lib/sample-questions.ts`) awaiting
another developer's 39 x 3 handover (39 curricula: BSCS counts twice). Verified: unit 77/79 (2 need pytest, absent on
this machine), tsc, `next build`, `scope-onboarding.mjs` 3/3 against mocked APIs, screenshots 390/1440 light/dark.
Not run here (fixture on the other machine): `account-controls.mjs`, `chat-workspace.mjs` still use the old dialog
selectors and need updating there. Backend still accepts chats without a program (frontend-only lock).
Round 2 (`63880e5`, `6eb12c9`): colleges collapsed until tapped/searched; program button shows short names (BSCS);
light bulb toggle in chat header (light default), removed from /about; phone bottom-sheet picker; composer re-measures
after unlock. Verified: unit 79/81 (2 need backend deps absent here), tsc, scope-onboarding 3/3, 375px screenshots.
Round 3 (`7ce7438`, `fb9314b`): "Try asking" alternates every 4 s between 3 random Handbook FAQs and the selected
curriculum's prerequisite checks (from `Context/sample-query-results-20261103.md`, 115/116 pass; Psychology tracks have
1 tested question each); About "i" icon at top left once chatting (new tab keeps the chat).
**Known failure to fix later:** `bsba-buseco-2018-2019` "Can I take BE 2001 next semester? I haven't taken GE-PC yet."
returned `clarification_needed` (lists GE-PC, asks which passed) instead of not eligible. Swapped in the UI for
"Can I take BE 2001 if I already passed GE-PC?" (passed for BSBA FM, same rule; not yet run live for BusEco).

## Live stack on the joel laptop (3 Nov)

RTX 3050 4 GB (Gemma 35/43 layers on GPU), `.wslconfig` memory=6GB (owner). Venv
`audit-evidence/p12-env-20261031/venv` built with pip, api+embedding+dev extras constrained to `backend/uv.lock`
versions (uv marks api/embedding as conflicting). Hosted-560 API :8021 (startup ~100-112 s), Next dev :3216, ngrok
3.39.13 tunnel https://snorkel-overturn-defiance.ngrok-free.dev (new account; added to API `allowed_origins` and
`SITE_ORIGIN`; backups `.before-ngrok-20261103`). Live checks: CS 12/L eligible 64.7 s, drop subject 43.5 s, BusEco
"Can I take BE 2001 if I already passed GE-PC?" eligible 33.9 s (replacement now verified), shifting via tunnel 52.7 s.
Stopped 3 Nov via `scripts/start-bintanong.ps1 -Stop` (API, Next, ngrok, model container); restart steps above.
Guests are public while the tunnel is up; Google sign-in via the tunnel needs `<tunnel>/auth/callback` in Supabase.
Capacity: 1 running + 4 waiting answers, then 503 `answers_busy`; no per-client rate limit. Frontend now retries a busy
refusal every 15 s (4 times, then manual Try again), with Try again now/Cancel and no interrupted bubble
(browser test `busy-retry.mjs` 3/3).
Per-person limit (`81bf231`, `a25c44b`, owner): 5 admitted questions per 5 min, per account or per guest browser
(anonymous `__Host-bintanong_client` cookie, survives New chat; clearing cookies resets it; IP limits rejected for shared
campus networks). 429 `rate_limited` + `retryAfter`; UI waits m:ss and auto-sends. Verified: API tests 197+5 pass,
browser 7/7, live via proxy: 5 answered, 6th 429 (239 s), still 429 after New chat. API restarted (pid in launcher-logs).

## Stack launcher (2 Nov)

`1b726d58` `scripts/start-bintanong.ps1`: Docker Desktop -> model `bintanong-p09-cuda-latency` :18088 -> hosted-560 API
:8021 -> Next dev :3216, health-gated; `-Ngrok`, `-Stop`. Verified cold start (model ~100 s, API ~80 s), `/health/ready`
ready, rerun no-op. `-Stop` and `-Ngrok` not yet exercised. Logs/pids: `audit-evidence/launcher-logs/`.

## Hosted reads (2 Nov)

`5f9973eb`: the per-request pin no longer reads `chunks` (it read the whole table with text and vectors on every
readiness check and chat); it confirms the release row and curriculum links. Basis: published evidence is immutable by
database trigger; hosted release confirmed published. Startup chunk comparison stays (ids/hashes, 92 KB). Ledgers load
one at a time with a 3-attempt read retry in the loader; the storage client's no-retry contract is unchanged. 19 MB of
ledgers still load at startup because Prolog runs locally. Tests: 60 pass after the final retry move; the wider run
before it was 602 pass / 3 subtest fails from the since-removed client retry. Not yet run live. Wi-Fi corrupts larger
Supabase downloads; WARP drops itself ("Settings Changed"). Model container is `bintanong-p09-cuda-latency`, stack stopped.

## Failing-case fixes and tone (2 Nov, owner-approved; local commits, not pushed)

Owner verdicts on the 12 `7327ade` failures: Fail #2-5, #7-13; Pass #6. First failure: pre-selector #2,3,4,7,8,11; draft
#5; checker #9; hold #10; host validation #12; router split #13; none at Prolog or KNN. Context consulted: thesis physical
11, 50, 53-54 (fluent, student-friendly replies; clarify vague intent). Tone baseline (238 answers): "supplied evidence"
lead-in on all 171 answered, 14 generic clarifies, 56 use "you/mo/ka". Prerequisite scan (39 hosted ledgers, anon
read-only): 2,132 courses, 1,139 unresolved (1,050 blank, 89 printed conditions); blanks stay unknown (ledger 27-29).
- `6aad1683` no lead-in in student view; scope asked as a question; shared program name uses the selected one or lists
  full names; whole-unresolved rules say what is printed (blank = not listed, printed condition = unverified quote, with
  adviser/college referral); a split printed code ("HPC 8 / FL 2") names one course.
- `d1fb38a4` a not-stated claim no longer hides a printed service title (Charter 2.4 Certifications now labelled).
- `605c9571` (owner 9A) held-record quotes use plain labels + "Heads-up"; clean records cited beside them are quoted.
- `041e40b1` a fee/time/requirements question beside a not-stated note on another kind of field gets the printed facts;
  dry run over 1,108 recorded routing outputs: 2 triggers, both #7-8; #10 hold kept.
- `1a880935` (cherry-pick of `2a2eef6f`) draft prompt: answer first, second person, printed terms exact.
- Case files (backups `cases.before-20261102.json`): #6 drops "misadvising"; 13 prerequisite cases reject bare clarify.
Verified: RED/GREEN per fix; related suites 1,920 pass; default suite on `6aad1683` no failures (Docker up); live probe on
`d1fb38a4` 16/18 (both misses #7-8, fixed in `041e40b1`). Full 97/91/50 live run on `1a880935` running (`run-1a880935-*`).
Open for owner: #10 (link, both-fines reply, limitation placement), #11 (B or B+), #4/#3 links, #5 target answer.

## Model GPU speed check (2 Nov, measured; nothing restarted)

The running `bintanong-p09-cuda-latency` (pinned `f66a5229`, `--n-gpu-layers auto`, ctx 8192, parallel 1) is fast:
fixed 1841-token prompt, 256 greedy tokens: prompt ~3,200 tok/s, decode ~55 tok/s, 3.4 GB VRAM. Per-call log in real
turns: decode 39-50 tok/s. The old 12-23 tok/s records do not describe this container; offload is no longer the
bottleneck, so the 43/43 test and the `.wslconfig` change are dropped. Three guest questions through the local proxy:
26.5, 21.7, 21.1 s, answer text in one delta at the end. Third-question split: 5 model calls 13.5 s (~390 generated
tokens ~10 s; a 4.5-5.3k-token prompt re-read each turn ~1.5 s because one slot alternates with a ~7k cached prompt),
3.5-4.9 s gap before the draft call (in-process CPU query embedding + hosted Supabase RPC, ~220 ms round trip), ~4 s
other gaps. Another session's pytest held CPU near 91% during the runs, so the gaps may be inflated. Not a load test.

## Ingestion GUI audit (1 Nov, read-only)

Audited `feat/p11-policy-ingestion-review` at `68aaee6` (separate worktree, 133 commits ahead of origin, 190 behind p12).
Delivered: prepare/review/build/verify, researcher UI, vision and LlamaParse adapters, evaluation harness. Fresh: 135/135
Python (107 in p12 venv, 28 need system-Python `pymupdf`), Node 24.21 7 pass/1 skip, tsc clean. Not done: adaptation plan
Tasks 0-5, T4 stage/publish/rollback, T5, any real assisted packet, any institutional review decision or real bundle.
New defects: resume re-uploads failed pages without `--retry-failed`, contradicting the guide; a corrected multi-span
field fails build (traced in code, 3 of 298 fields affected); `load_packet` runs per request (10.15 s prospectus packet).
Docling and Docker blockers look stale. Evidence: `audit-evidence/p12-ingestion-audit-20261101/`. No code changed there.

## USG Constitution loading request (1 Nov)

Owner asked to run Phase 04 Supabase chunking for the USG Constitution. Inspection only so far; no chunks, vectors,
hosted or local database writes, and the active 560 release is unchanged. Evidence: `dataset/` is absent on this
machine; the original (34 pages, native text, about 69,500 characters, 24 articles) is at
`C:\Users\Hawksprey\source\repos\Bintanong\backend\bintanong_tools\bintanong_jsonifer_prolog\dataset\handbook_citizen_charter\Student Handbook and Constitutions\`
and its SHA-256 matches the recorded `b40cca9e…`. It was not in the 30 Oct hosted snapshot or the 560 bound chunks.
Phase 04 only loads prepared artifacts, so chunks, source register, review receipts, vectors, a new release and pin must
be created first. Only G03 is a confirmed reading; G01/G02 stay unconfirmed; the Article XV ASG clause stays excluded.
Blocked here: `.env` has no service-role key or `SUPABASE_HOSTED_DB_URL`; Docker is stopped (no local Supabase);
0.8 GB RAM free; `p11-faq-split-20261028` and `p05-source-observation-preparation-20261017` are not on this machine.
Hosted checked 1 Nov (read-only, anon key; drafts are invisible to it): active `p12-research-faqsplit-20261030`,
560 chunks, 39 curriculum links, 5 documents, 0 chunks from this PDF; 8 Handbook chunks only mention USG.
Owner chose short human-review batches for clause text (no directive-only approval), after the load target is settled.
Owner chose stage inactive, after syncing hosted changes to local. Admin credentials are in `.env.example`, not `.env`
(tracked file; never stage it). Service-key REST confirms no USG document on hosted, drafts included (5 documents, 5
releases, 860 chunks). Synced local one way, hosted read-only: migrations 13 -> 18 by `db push --local` (no reset), then
all 25 public tables in one transaction into the empty local database; counts and chunk id/hash set match (digest
`6e4c9af2…`), local active release matches, anon sees 560. Hosted's own migration list is unverified; every REST-returned
table matched local columns. auth/storage not copied. Evidence: `audit-evidence/p12-usg-load-20261101/`.
Blocker for staging: session pooler connects but never answers (from Windows and Docker), so the slow release RPCs
cannot run yet. Next: review batch 1 (Articles I-II) with the owner, then chunk, embed and rehearse locally.
2 Nov, read-only: `feat/p11-policy-ingestion-review` (`knowledge_update`, `researcher/`) already covers prepare, review,
build and verify, plus explicit retained/replaced/removed membership and retained-vector reuse. Proposed for USG instead
of adapted one-off scripts, pending owner choice; compatibility with the 560 package is untested. It has no automatic
clause diff in `baseline.py`/`build.py`, and T4 stage/publish/rollback is undone, so hosted staging stays in p12.

## ngrok access (31 Oct)

Guest chat works through `ngrok http 3216` (https://overbill-subpar-palm.ngrok-free.dev). `dea1b8b`: the proxy trusted
only `request.url`, which stays loopback behind a tunnel; it now also trusts `SITE_ORIGIN` and forwards the verified
origin; `allowedDevOrigins` follows `SITE_ORIGIN`. Ignored config changed: `frontend/.env.local` `SITE_ORIGIN`, tunnel
added to hosted API `allowed_origins`. Stack restarted via `audit-evidence/p12-env-20261031/keepalive.ps1`.
Verified: RED then 67/67 unit, tsc clean; real browser via the tunnel: page, curricula, POST 200, streamed leave-of-
absence answer with one source, no console warnings. Open: Google sign-in via the tunnel needs the owner to add
`<tunnel>/auth/callback` in Supabase, and sign-in from 127.0.0.1 is refused while `SITE_ORIGIN` is the tunnel;
`frontend/proxy.ts:29` redirect behind the tunnel and PDF upload through it are untested. Guests are public while
the tunnel is up. Limits in place: answer admission (`backend/bintanong_api/admission.py`, 1 running + 4 waiting,
then 503), 2 parallel uploads, 1,000 sessions. Per-client rate limits are planned at a reverse proxy
(`plans/2026-10-24-phase-11-security-review.md`) and none is configured on this tunnel. Not deployment approval.

## UI-only port to `frontend` (1 Nov)

Owner asked for the UI change on `frontend`, "only the UI changes" for now. `2a8bda89` cherry-picked as local `47198ac8`
(not pushed), guest/scope logic excluded; three conflicts resolved. tsc clean; 61/61 unit; webpack build passes; browser
12 pass / 6 fail. The six (account-controls ×3, guided-clarification ×2, workspace-navigation) also fail on untouched
`frontend` against the p12 fixture; root cause not investigated. Evidence: `audit-evidence/p12-teammate-ui-20261031/pick-*`.

## Teammate UI integration (31 Oct)

Owner asked to integrate the teammate's enhanced UI (`worktrees/Bintanong/bintanong-teammate-enhanced-ui`, an
unversioned mock-data Next app). Its design was ported onto the live workspace; the folder itself is unchanged.
Ported: mascot logo/favicon, orange welcome backdrop, Gemini-style sidebar, "Hi, I'm Bintanong" welcome with
pills above a pill composer, user/assistant avatars and bubbles, public `/about` page. Dark mode kept (the
teammate build is light-only; mascot gets a light backing). Assets resized: logo 190 KB -> 13 KB, photo 2.5 MB -> 215 KB.
Not ported: mock chat/multi-session data and sidebar search (one server session per browser), timestamps,
header account avatar, dependency/config changes, Tailwind rewrite. Live starters, sources, clarification,
files, sign-in and 44 px targets kept. Landing/login keep their layout and heading; they only gain the mascot.
About copy corrected: dropped "Graduation Tracking" and "Curriculum Flowchart" (no such capability; thesis
physical 17-18 consulted). Open: the binturong name-origin line is the teammate's; no repo/thesis source confirms it.
Verified: tsc clean; 66/66 unit; production build; browser suite (isolated synthetic fixture on :3219, evidence in
`audit-evidence/p12-teammate-ui-20261031/`) 17 pass / 10 fail on the last full run. Baseline on unchanged code was
17 / 9 of 26; the same nine fail after (older sign-out expectations, missing PDF fixture path; not investigated).
The tenth (`live clarification`) and an earlier `Stop` failure are intermittent: Send still disabled after a
page fill under load; each passed 3/3 alone. Real pipeline via :3216 -> :8021: CC 5/L returned CC 3/L and CC 4/L
in 19 s, an enrollment question returned one source, both themes/phones rendered with no page errors.

## New-machine handoff run (31 Oct, 32 GB machine, HEAD `7327ade`)

Following the [current handoff](../2026-10-30-eight-failures-handoff.md). Environment and logs:
`audit-evidence/p12-env-20261031/` (venv from frozen lock exports; portable Node 24.21.0, system Node stays 22).
Step 1 passed: backend `app constructed` in 145 s; browser guest question answered in 17 s with one source.
Step 2 passed apart from one known guard: default 5,604 pass / 1 fail; `--include-ingestion` 7,399 pass / 1 skip
/ 2 xfail / 1 fail. The failure is `test_scaffold_contract` rejecting uncommitted `.env.example` credentials.
Collected 5,607, not the handoff's ~5,576 (deselected 1,796 matches); the extra 31 are not yet explained.
Steps 3-6 on hosted, single development runs, 0 exceptions in every set:
97-case 88/97 twice (general 26/33, CoS 48/48, other 14/16; baseline 77/97; no pass or status flips, 3 texts differ);
50-case 50/50 twice (baseline 49/50); 91-case gate 88/91 (new hosted baseline). Median warm pipeline 10-15 s.
97 failures: section, honors, grad residence, absence, good-moral, certification fee, transfer fee, two BSHM.
91 failures: library card, certification fee, overdue fee (all `insufficient_evidence`). Honors stays a disclosed
limitation by the 30 Oct owner choice unless its answer text shows otherwise. Run folders: `run-7327ade1-*`.
A first 50-case repeat stopped before any question on a hosted 500 statement timeout while loading curricula
(`-full2`, no observation); the `-full2b` retry completed. Backend startup makes the same read.

Setup findings the handoff omits:
- `api` and `embedding` conflict in one `uv sync`; export each from the frozen lock (76 pins, no clash) and install.
  The default suite also needs the `tools` extra plus `jsonschema` and `opencv-python`, at lock pins.
- Eight encoder text files were LF here; verified hashes are of CRLF bytes, so startup would refuse them. Copied
  the verified bytes from a local copy; 10/10 assets match; LF originals in `encoder-lf-backup/`.
- Use `next dev -H 127.0.0.1 -p 3216`; without `-H`, Next blocks `/_next/hmr` and the page reloads repeatedly.
- System Python 3.13.12 does not match the lock (18/76), so runs use the venv. A 16 GB WSL limit is set.

Resolved 2 Nov: owner moved the hosted secrets into ignored `.env`; `.env.example` and `.gitignore` match HEAD again.
Local stash `3f3b096b` (31 Oct, "dont include the env vars") still holds the live values; no branch or remote ref
contains it. Docker Desktop stopped by itself at 04:38:58 (cause unknown; run discarded).
Google sign-in docs use port 3215 while this setup uses 3216; guest use unaffected.

## Latest delivery: test-suite audit

[Completed plan](../2026-10-30-test-suite-audit-plan.md) · [Counts, removal proofs and results](../2026-10-30-test-suite-audit-results.md).
Overall collected: **7,365 -> 7,363**; inherited Hawksprey420 cases: **4,646 -> 4,644**.
Contracts: **25 -> 11 files**, all **2,032 cases retained**; 235 moved test functions verified against originals.
Fourteen fix-pass/survivor fragments folded into module files; shared path/ID matrices centralized.
Two removals: identical ledger compatibility duplicate, and OCR text-format case covered by a retained real
adapter test with the same oracle. Per-test line/arc subsets documented; both OCR tests catch lost-newline mutant.
Evaluation helper renamed; five imports fixed; executable builder AST unchanged.

Final test code `4ed03dc`: **7,355 passed / 6 skipped / 2 xfailed / 1,608 subtests**, four batch exits 0.
Fresh inherited run: **4,638 passed / 6 skipped / 13 subtests**, exit 0.
Coverage before/after: **14,444 / 24,492 statements; 4,631 / 9,720 branches** (`backend/`, `scripts/`, `evaluation/`).
Exact covered sets preserved globally and within every family; production Python hashes unchanged.
Root evaluation coverage corrected using original archived tests and hash-verified production code.
No negative/privacy/scope/security/source-gap/original mutation-survivor case removed.

Owner approved coverage 7.17.0 + pytest-cov 7.1.0 in the evaluation venv only; no lock/dependency edits.
Owner amended verification to focused checks during audit and one final full suite; interrupted intermediate
run is recorded separately and never claimed as full evidence. Owner kept review GUI, OCR bench and prospectus
fixer as offline ingestion tools. Their inherited families: 1,787 -> 1,785 cases, separate from runtime evidence.
No test-command/CI default changed. Local Supabase started/healthy; Gemma untouched and unnecessary here.

Fresh Codex review checked helpers/matrices and found a shared vocabulary binding that weakened checker
independence. Separate package/checker bindings restored; process-local probe RED fail -> GREEN pass, contracts
2,032 pass. Passing counts/ASTs alone do not prove binding independence. External Claude review done; see below.
Commits: `db643c0` baseline; `4e80c56` quick wins; `f071293` consolidation; `0f7849b` OCR; `4ed03dc` checker fix.
Claude review (30 Oct, read-only): all 7,363 IDs map to originals; 115 moved bodies differ only by helper
renames/module-prefix drops/equal fixture matrices; no remaining top-level rebinding. Runtime suite (187 files, no
prospectus/GUI/OCR or tool-importing tests, DB up): 4,843 pass / 2 xfail, exit 0. Nits only: 7-8 blank-line runs,
duplicate `BIND`, misnamed `_typed_chunk`/`_source_record`, alias `_chunk_adapter_reason`.
Owner (30 Oct): keep ingestion tools but out of the default suite. `tests/conftest.py` deselects prospectus/GUI/OCR
files unless `--include-ingestion` or named: default 5,576 / 7,372 collected (1,796 deselected). Selection test
RED 9 fail -> GREEN 9 pass; remaining default files 728 pass / 3 skip; with the runtime run, all 5,576 accounted.
Closure documentation follows. Raw evidence/temp/scripts remain under ignored workspace audit-evidence.
No production behavior, source corpus, dependency/model/lock changes, merge or push.

## Research release and accuracy follow-ups

[Phase 12 handoff](../phase-12-handoff.md) · [Frozen report](../../docs/evaluation/phase12-evaluation-report.md) ·
[Activation](../2026-10-30-hosted-560-activation-results.md).
Hosted research `p12-research-faqsplit-20261030`: 560 chunks/vectors, 39 curricula; corrected78 retained for rollback.
Bound artifacts/source states unchanged. Owner manages backend :8021 (hosted-560 config), frontend :3216,
model :18088. Do not repeat activation or use the old corrected78/local-document config after the switch.
Frozen main v2: 38/50. Participant research, independent scoring and institutional validation remain unavailable.
[Hosted-parity development regression](../2026-10-30-hosted-regression-results.md): 47/50 on `63b9653`, no exceptions;
separate from frozen evaluation. Remaining: summer-load-en Dean omission, grad-residence-taglish, uniform-taglish.
Student-evaluation prep (owner 30 Oct): next week, screen-shared sessions, 2 students per program, mainly College
of Sciences (prior questionnaire evidence) plus a few other colleges; priority is common queries. RAGAS later.
Checker fix: evidence-ID hex matched digit expectations; hosted/gate runners now strip IDs (47/50 and frozen 38/50
rescored unchanged). `f08712d`: omitted printed exception -> repair (RED 8 -> GREEN 8; gen/orch/API 1,014 pass;
104-draft dry run: 8 triggers, all summer load; live repair replays EN/Taglish include 12 units + Dean). A prompt-only
variant was replayed and reverted (1 gain, 3 regressions). `12b35d1`: one printed row naming the part's word
replaces an unrelated row (uniform Taglish); `ac867c6`: a selected topic whose heading names more part words wins
(graduation residence Taglish). Dry runs over 273 routing outputs: 4 and 1 triggers, all correct. Live hosted
subsets: 8/8 and 6/6 incl. all three former failures. Full 50 on `ac867c6` running (Claude, `-claude-full`).
Common-query set: `audit-evidence/p12-common-queries-20261030/` (97 cases: 33 general rewordings reusing reviewed
expectations, 48 CoS across all 6 CoS curricula, 16 from 6 other colleges); first run before any fix.
Full 50 on `ac867c6`: 49/50 (probation-tagalog withheld by style check on a verbatim printed INC sentence).
`41dfd00`: verbatim printed sentence allowed among Taglish claims; 26 non-EN live 25/26 (cheating-tagalog router
nondeterminism, raw model chose not-stated fact; not a code regression). Common set first run on `41dfd00`:
77/97 (general 20/33, CoS 43/48, other 14/16; median warm 21 s). Found: Charter host replies citing held malformed
records crashed (final_malformed_source_fidelity; regression since 28 Oct gate) -> `1468505` routes them to the
per-part quote path; live 10-case probe 6/10, no crashes. `754ee9a`: an ambiguous topic selection carries no
document topic (structured checks proceed); live 8/8 incl. all 5 CoS Taglish term listings. `48ff8d6`: owner-
approved Filipino penalty-row words (uniporme excluded; docs table + sync test) and best-row narrowing; 440-output
dry run: 4 intended changes; live discipline probe 8/8. Open: topic choices (absent, good-moral requirements,
honors wording), certification-of-grades and transfer fee, BSHM clarification. Full 97 rerun was stopped by the
host for low memory (no results); rerun the 97 and 50 on HEAD. Claude restarted :8021 on `48ff8d6` (owner-authorized).
Owner 30 Oct: test runs move to another developer's 32 GB machine; setup, runtime files and run order are in
the [current handoff](../2026-10-30-eight-failures-handoff.md).
Owner restarts :8021 to serve the new HEAD.
Honors guard kept by owner; INC now answers printed quotes with limitation/referral. Prior repair history remains
in `db643c0`, dated results and [accuracy handoff](../2026-10-30-eight-failures-handoff.md).
No live model benchmark or student-visible latency claim from this audit.

## Boundaries and next action

Preserve undergraduate scope, source gaps, privacy, unknown-versus-unmet, printed terms and release guards.
F04 stays held; research activation is not institutional approval or public deployment.
Next: owner sets the score target; then fix failures in order CoS > general > other colleges and add new common-query batches. No push/merge or Phase 13 advancement.
