---
artifact: phase-checkpoint
phase: 11
status: in_progress
sequence: 11
plan: plans/phase-11-backend-api-plan.md
head_commit: 0c43f49
working_tree: clean
updated_at: 2026-10-25T09:00:00+08:00
---

# Phase 11 checkpoint - security, queue, abuse probe, E1 and E3 done; step 2 evaluation continues

## Completed Tasks

- Start: owner go (backend only), environment check, can-advance, pre-phase research (`2c2d335`); O1-O5 (`3ba8d7d`).
- Task 1 cookie session, origin guard, `DELETE /session` (`d42feac`, `d59d0e2`).
- Task 2 store turn tracking (`e77e3af`), `ChatTurns` (`1287bbc`), `GET /curricula` (`017efc4`).
- Task 3 student view without ids, operations or condition codes (`7e1d34d`).
- Task 4 `POST /chat` AI SDK UI message stream v1 with progress, cancel on disconnect (`c2cae2e`).
- Task 5 store upload ids (`4b73b21`); upload/confirm/delete endpoints (`8b70e21`).
- Task 6 `GET /sources/{source_id}` (`b8f829b`).
- Task 7 (24.2): owner path recorded (`d1e7f31` ledger); floor `3eb4f59`, `6abfb40`; prompt trial declined;
  [results](2026-10-24-taglish-style-floor-results.md) (`4931177`).
- Task 8 (24.1): photo rows `a495db2`..`72a196b`, scorer `7328519`/`c55a6ac`, limits as strict xfails `15dbe41`;
  [results](2026-10-24-photo-grade-rows-results.md) (`5e1eb1f`). Photos stay unsupported; no dependency added.
- Task 9: `ResearchPipeline` chat port (`6f0cf36`); live HTTP smoke on real data passed (below); docs `ef716ca`.
- Pause commit `0e4e4f1`. Security check (next-action step 1): [review](2026-10-24-phase-11-security-review.md);
  fixes S2 `e87ed7b`, S1 `15934a7`, S4 `8b67b8d`, S5 `b0dc62b`, S6 `93e795e`, S7 `72ec6d4`; docs `a6c624a`.
- Owner follow-ups (24 Oct): answer queue `d1d416c` (+ doc `c15f50f`); off-topic refusal fix `5ee7b50` (S8);
  master section 25 (PSU Google sign-in decisions, capacity, off-topic) added.

## Current Task

Step 1 (security) and the owner's follow-ups (queue, off-topic, login decisions) are done. Step 2 (retrieval/Prolog
evaluation) has started; E1 (`7c3786e`) and E3 (`05f34d2`) are fixed.
[Security measures inventory](2026-10-24-security-measures-inventory.md) written for thesis Chapter IV (owner). There is deliberately no final handoff.

- E1: document questions outside the 7 reviewed topics ("How do I apply for a leave of absence?", "Paano
  mag-request ng transcript of records?") route RAG correctly, but retrieval returns `needs_subject`, which
  integration maps to `clarify`. Students get a bare "Please clarify the missing information" with nothing to
  clarify. Owner chose "unavailable + office referral": `needs_subject` now maps to `no_evidence`, and the
  insufficient-evidence reply (en/fil/taglish, all such cases) says the topic is not in the reviewed sources yet
  and refers to the university office. Live re-check: both questions `insufficient_evidence`.
- E3 (fixed `05f34d2`, owner chose office referral): the router model chose `clarify` naming no operation, claim or
  back-reference (3 of 4 shifting phrasings; roster 16: 8 bare clarifications incl. Nursing/Tourism/Criminology and
  one Taglish pre-enrollment). Now diagnostic `empty_clarification` -> `no_evidence` -> E1 referral. A clarify with a
  check or back-reference still asks. Disclosed: the covered pre-enrollment Taglish case also gets the referral
  (retrieval needs a model-chosen topic, `engine.py:111`). Live: 4/4 shifting phrasings referral, right language.
- 2a fixed (`9c09ac7`): "overload"/"pwde b mg overload?" chose the overload topic but marked the part structured
  with an eligibility check aimed at the word itself (router spy: `only_document_parts_carry_topics` both attempts
  -> invalid_reference -> bare clarify). Wire normalization now makes a structured topic part whose operations
  target no listed course a document part. Live: both answered, matching Handbook table 6 rows 1 and 3. The
  two-topic overload + special-class-fee message now routes RAG but ends insufficient (first-topic-only, 2e).
- 2b `467aa9d` (owner "List for both"): no stated course fact -> list the reviewed prerequisites (and / one of /
  or take at the same time) and ask which were passed; live CC 5/L: CC 3/L and CC 4/L, CC 6/L: CC 3/L and CS 2/L.
- 2c `9e3c5b0`: a course matching no reviewed course -> "not found, give the printed code" (live CS 999, a title).
- 2d `8f15471`: `unsupported_requirement` -> no_evidence -> E1 referral (live units questions).
- 2e `1f510dd`: every chosen topic retrieved, each with its parts' words when there are several; live both topics
  return evidence, but per-part generation then ends `parts_unresolved` (r1 missing_mapping, r2 not_in_evidence);
  the single Filipino "Magkano ang special class fee?" also ends parts_unresolved. Next diagnosis.
- e2 fee `c2ef61a`: a special-class-fee part gets the host-written printed rate + printed example + "your own
  charge is not stated" + office referral (en/fil/taglish), copied from the reviewed fields; no model call or
  arithmetic. e2 partial `0046b4d`: a part declared not_in_evidence/source_gap is named ("The part about
  "<words>" is not in Bintanong's reviewed sources yet...") when another part or the structured check answers;
  ledger status `some_parts_unavailable`; a reviewer-rejected part still withholds (claims stay bound to the
  review identity); a fee part inside a mixed message keeps the host claims (not model-reviewed). Live: 3 fee
  questions and both overload + fee messages answered with PHP 370.37/hour and the 3-unit PHP 20,000.00 example.
  The Taglish fee wording was labelled fil by the router and got the Filipino reply.
- Open (seen live, `diag_partial_after.log`): Hybrid "Can I take CC 5/L? I passed CC 3/L and CC 4/L. How do I
  enroll in it?" - the router gives the document part no topic, retrieval returns nothing and the whole message
  gets the E1 referral; the structured result is lost (orchestration-level, not the generator).
- Not yet changed: `model_ambiguity` clarifications and model-chosen `evidence_unavailable` render without naming
  anything / as "temporarily unavailable" (`fallback_status`); candidates for the next diagnosis.
- E2 (minor): "What are the prerequisites of CC 6?" names CC 3/L and CS 2/L, but framed as an eligibility
  clarification rather than a plain list.
- Correct, not defects: "Can I take CC 5? I passed CC 4." (en/Taglish) reports CC 3/L as unknown, as intended.

## Repository State

Branch `feat/p11-backend-api` from `dev` `cbaa6a7`; commits through `0046b4d` plus this checkpoint commit, nothing pushed.

## Verification Evidence

- Each code task: RED observed, then GREEN; every new guard mutation-checked (each mutation failed a test).
  Latest focused runs: API files 76 passed; photo rows 27 passed + 2 strict xfails; scorer 10; style floor 27;
  routing style/router 131; research pipeline 2.
- Roster run 16 (HEAD `6abfb40`, run 15 settings): 0 of 63 status/decision changes; replies en 21/21, fil 21/21,
  Taglish 15/21 (run 15: 10/21); 23 of 25 answered texts identical, 2 changed only in language.
- Photo measurement: 42 simulated photos, 0 silent errors; plain layout exact in all 7 conditions; Report-of-Grades
  style exact in flat/dim; owner's real screenshot refused (two causes pinned as xfails).
- Security fixes: RED observed for each, then GREEN, and each guard mutation-checked. A re-probe of S1 (1000
  cookie-less requests) left a new student's `/chat` at 200.
- Answer queue: RED -> GREEN; three mutations (no busy refusal, no slot wait, no release) each failed the test.
  S8 wire fix: RED reproduced the live `part_count_mismatch`; 358 routing tests pass; two mutations caught.
- Live abuse probe (14 cases): 12/12 refused before the fix, the mixed case 2/2 after it; 0 leak markers.
- Live capacity probe: 1 student 25.6 s; 3 at once 23.5/38.5/49.4 s; 6 at once five served by 76.8 s and the
  sixth `answers_busy` in 0.5 s; statuses identical to a sequential run. Logs in `live-api/`.
- E1: RED (4 tests: integration mapping and the reply in three languages), GREEN; generation/orchestration/API/
  routing/evaluation selection 1516 passed.
- E3: RED (2 tests, expected reason) after a fixture setup fix, GREEN; 3 mutations each failed a test; selection
  (routing/orchestration/generation/API/evaluation/private) 1310 passed, 2 xfailed.
  Hosted Supabase security advisor 24 Oct: 0 lints.
- 2b-2e: RED observed for each, GREEN, isolated mutations each failed a test (2b 4, 2c 3, 2e 5). Selection
  (routing/orchestration/generation/api/evaluation/private/symbolic/runtime/contract) at 2b: 3727 passed, then 9
  traceability digest failures fixed by omitting an absent `requirement` from the dump. Full suite NOT run at
  `1f510dd`: a first run overlapped edits (discarded); the clean run was stopped by Claude Code for low memory.
- e2: RED observed for each (fee 3, partial 6 + ledger contract 4, mixed fee 3), GREEN; 13 isolated mutations
  each failed a test (one redundant guard removed after its mutation survived; one assertion added for M13).
  Selection (generation/orchestration/api/routing/evaluation/private/request + question-parts) 1401 passed,
  2 xfailed. Full suite not yet run after `0046b4d`.
- Full suite at `874f0c9`: 6478 passed, 6 skipped, 2 xfailed (photo limits), 1552 subtests, 0 failed, 19m51s
  (log `full-suite-874f0c9.log`).
- Roster run 17 (HEAD `874f0c9`, run 15/16 settings): 0 of 63 status/decision changes vs run 16, 0 exceptions;
  19 text changes, all intended (11 E1 referral wording, 3 Nursing title questions -> course not found, 2
  Criminology CDI 6/7 -> co-requisite listed, 3 proposed-BSCS CC 5 -> CC 3/L and CS 2 listed). Comparison
  `audit-evidence/p11-20261023/roster17-vs-16.txt`.
- Security re-check 25 Oct: hosted Supabase security advisor 0 lints; secret scan of `dev..HEAD` (59 commits) found
  only Python `secrets` uses, docs and test strings; tracked `.env.example` points at the local Docker DB only.
- 2a: RED (2 wire tests, `only_document_parts_carry_topics`), GREEN; 3 isolated mutations each failed a test;
  selection (routing/orchestration/generation/api/evaluation/private) 1772 passed, 2 xfailed. Live log `diag_r4_after.log`.
- Multi-turn run 6 (12 cases, HEAD `6abfb40`): same courses/statuses as run 5 on 12/12, 0 wrong carry-overs; Taglish
  turns in Taglish 3 of 4 (run 5: 0 of 4).
- Live HTTP smoke (untracked launcher `audit-evidence/p11-20261023/live-api/`, one uvicorn worker, hosted 39-curriculum
  release, Gemma :18088): RAG answered with a readable `/sources` excerpt (Handbook p.46); upload -> confirm -> CC 5
  eligible (conditional); delete upload -> unknown again; humanized Taglish conditions; foreign origin 403;
  `DELETE /session` sends Max-Age=0 with the `__Host-` attributes; a client dropped 4 s into an answer left the
  session free (next message completed). Observed, not Phase 11 regressions: "I passed CC 4 but I have not taken
  CC 3" got a generic clarification; a Hybrid next-step part was not answered.

## Versions and Digests

Python 3.13.7 (shared venv `audit-evidence/p05-real-retrieval-readiness-20261012/venv`), FastAPI 0.141.1,
SWI-Prolog 10.1.15, PostgreSQL 17.6, pgvector 0.8.2, RapidOCR 3.9.2 + onnxruntime 1.30.0 CPU (venv only, local
models), Gemma 4 E4B GGUF on :18088 (not re-hashed). Owner samples sha256: `46bf8a11...`, `0451f6f0...`,
`dccc1c2a...`. Stream chunk shapes per `ai` 7.0.150.

## Decisions

- O1-O5 as recorded; 24.2 path (floor kept, prompt trial declined); 24.1 photos unsupported, no `api` dependency.
- Only the last user message of an AI SDK request is used. 422s before the stream; turn lock inside it.
- Canonical answer text stays the researcher diagnostic; students get `student_text`.
- Owner, 24 Oct (security review): S1 evict the least recently used empty session (this replaces the Phase 10
  "503 rather than evict" rule for empty sessions only); S3 `next`/`sharp`/`source-map-js` upgrades go with the
  `ai` v7 install at UI integration; S4-S7 applied now.
- Owner, 24 Oct: answer queue of 1 running + 4 waiting, then busy. PSU Google sign-in via Supabase Auth, domain
  `psu.palawan.edu.ph` checked server-side, one running question per account, built with the UI integration
  (master 25.1). Off-topic requests are refused (master 25.3).

## Known Failures or Blockers

None blocking. Disclosed limits: 6 register-only Taglish questions reply in Filipino; photos unsupported (real
screenshot refused); master 16's browser exit gate is not met (no UI by owner direction); AI SDK contract test
against the SDK's own parser waits for the frontend install; no linter installed. Frontend `npm audit`: 1 critical
(`next` RCE advisories) and 2 high, deferred to UI integration by the owner. Proxy rate/body limits: deployment.

## Context Consulted

Thesis physical 17-18 and 65-66, routing PNG (23 Oct); physical 17-18 again on 24 Oct for the sign-in scope
decision ("authorized user/session"): consistent, no discrepancy. 25 Oct resume: physical 17-18 (unavailable/
referral wording for e2) and the routing PNG: consistent.

## Next Action

1. (Done) Security check: [review](2026-10-24-phase-11-security-review.md).
2. Fix the owner's risk-probe list ([results](2026-10-24-risk-scenario-probe-results.md); owner decisions 24 Oct in
   `owner-decisions-ledger.md`). TDD each; live re-check each with `risk_probe.py` (stdin = case ids). Order:
   a. (Done `9c09ac7`) typo/one-word overload -> bare clarify.
   b. (Done `467aa9d`) prerequisite list.
   c. (Done `9e3c5b0`) course not found.
   d. (Done `8f15471`) units -> referral.
   e. (Done `1f510dd`) every chosen topic retrieved.
   e2. (Done `c2ef61a`, `0046b4d`) fee host reply; multi-part partial answers. NEXT: the Hybrid case whose
      document part has no topic (structured answer lost to the E1 referral; see Current Task), then full suite.
   f. (7) Cebuano -> name supported languages; "Thank you" -> not "Hello"; tuition wording = referral.
   g. Passing grade: show the owner the printed region of Handbook p.304 (owner reading: 3.0/75 pass, below fails),
      then add the reviewed claim.
   h. NOW (owner approved 25 Oct, all 39 curricula + hosted upload; readings CF1-CF5 in the owner ledger).
      Dry run done: `audit-evidence/p11-course-facts-20261024/extract_facts.py` (writes facts-dryrun.json: per
      course title, units as printed, year/term banners with native char ranges, flags term_inferred True=CF2 /
      'CF3', merged_row, units_columns for BSN/BSMid) and `check_totals.py` (QA vs printed Totals; remaining
      mismatches are verified source errors or 2 checker artefacts). Reuses p09-program-reviews/draft_program.py
      columns/layout/rules_at and each spec's column_edges; runs with the shared venv python -I.
      Next, in order (TDD each):
      1. (Done `6814775`; RED 4, GREEN, 3 mutations caught; symbolic/runtime/ledger selection 293 passed)
         authoring.py: add FACT_FIELDS `units.printed` (text, e.g. "2/1", "250 Hours" not used) and `units.rle`
         (numeric); treat only units.total/lecture/lab/rle as numeric. BSN: units.printed from its Unit/s column;
         BSMid: units.lecture/rle/lab from LEC/RLE/LAB, "-" = fact omitted. Blank units = fact omitted (gap).
      2.-3. (Done 25 Oct, untracked evidence `audit-evidence/p11-course-facts-20261024/author_facts.py` ->
         `ledgers/<program>/ledger.json` + `author_facts_report.json`): 39 curricula, 2132 courses; every value
         checked by build_curriculum_ledger against its span; prerequisites/codes/earlier facts unchanged and the
         runtime payload hash identical for all 39. Spans: 429 CF2 `column_heading_owner_reading`, 52 CF3
         `owner_reading_source_error`, 14 new line-wrap joins (titles with a printed line-end hyphen, kept
         unspaced, e.g. "Management-Clinical Practicum"; for the owner spot-check). BSMid: lecture/rle/lab
         numbers, "-" omitted; BSN: Unit/s as units.printed; Thesis 1 (BSBio), SSE 18 (BSEd-SS) units omitted.
         Owner spot-check per batch (acceptance 1) still to show. Found: BSES EnS 101/L title prints "Earth Science I
         (Geology &"; its second line "Meteorology)" is clipped under the EnS 102 row (native text only) and was
         read into EnS 102's title. Only such case in 2132 titles (index-gap and join scans). Owner CF6 (25 Oct): visible text +
         gap; hidden fragment dropped from EnS 102 (applied, rerun clean). Spot-check accepted (acceptance 1).
         Original wording of items 2-3: Build fact spans from native char runs (like author_program.runs; whitespace-only canonical_text compare;
         wrapped words joined with resolution_method native_range_line_wrap_joined + repair_id). CF2 terms cite
         the column's printed SEMESTER heading; CF3 (BSBA-MM) needs an owner-reading repair on the span
         (value FIRST/SECOND SEMESTER vs printed FIRST/SECOND YEAR): check _facts/_spans before choosing.
      3. Regenerate 39 ledgers: same courses/prerequisites; new review `p11-course-facts-review-01` per curriculum
         (course_digests over new content); review_refs -> that review; old reviews kept in `reviews` as history.
         Verify prerequisite expressions and Prolog bundles unchanged except ledger hash (bundle regression).
      4. Lookups done `0c43f49` (`bintanong_symbolic/course_facts.py`: course_facts, list_term_courses; RED 5,
         GREEN, 4 mutations caught; over the 39 authored ledgers each of 2132 courses listed once, all complete).
         NEXT: router/validation/adapter wiring (a term listing has no course target: design needed), renderer.
         Original wording: Runtime: `list_term_courses(curriculum, year, term)`, `course_facts(curriculum, course)` from reviewed
         facts; router operation; en/fil/Taglish host text with printed units; title aliases only when unique.
      5. Hosted upload via the p09 loader pattern (`audit-evidence/p09-curricula-load-20261023/load_curricula.py`):
         insert new `curriculum_ledgers` rows, re-point `release_curriculum_ledgers` for release
         `p09-research-selected-20261022` (loader currently asserts no re-link: needs an update path); verify with
         Supabase MCP read-back + security advisor. Then live re-check R5/R6/R10 + roster.
   Not doing: per-college Charter notes (owner: website scope text says the Charter is university-wide; UI work).
   Roster run 17 done (above). Then the two live-smoke observations and roster 16's clarification statuses.
3. Then UI integration (co-worker's design). Website scope/guidelines must state the Charter source is the
   university-wide 2025 4th Edition (owner, 24 Oct). Install `ai` v7, `@ai-sdk/react` 4 and `@supabase/ssr`, and upgrade
   `next` (>= 16.4.3), `sharp` and `source-map-js`, all at the then-current patch, with owner approval of the exact
   pins. Build PSU sign-in (master 25.1) and a waiting screen for the `waiting` status. Add the
   contract test against the SDK's own stream parser. Proxy `/api` same-origin.
4. Then close Phase 11 with the full suite and a final handoff. Phase 12 needs its own recorded decision.

How to run things:
- Tests: `PYTHONUTF8=1 <shared venv python> -X utf8 -B -m pytest -q -p no:cacheprovider tests --basetemp=<ws>`.
- Live API: from the worktree root, `HOSTED=1 <venv python> audit-evidence/p11-20261023/live-api/serve_research_api.py`
  (port 8011, needs Gemma :18088). Then run `smoke_http.py`.
- Roster/multi-turn: `p09-real-data-20261021/roster13.py <out>` and `p10-20261023/multiturn.py <out>`, with HOSTED=1
  and PREFIX_CACHE=1.

## Do Not Repeat

Environment check, research, npm lookup, owner-sample OCR probe, tasks 1-9, roster run 16, multi-turn run 6, the
security review and S1/S2/S4-S8 fixes, E1, E3 and its live re-check, 2a-2e and e2 and their live re-checks, the security inventory, the 24-question risk probe, the chunk/topic and curriculum coverage counts, the answer queue, the abuse and capacity probes, full suite at `72ec6d4`, the three style prompts, the two reverted photo-threshold attempts.
