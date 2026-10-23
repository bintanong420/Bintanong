---
artifact: phase-checkpoint
phase: 11
status: in_progress
sequence: 9
plan: plans/phase-11-backend-api-plan.md
head_commit: 5ee7b50
working_tree: clean
updated_at: 2026-10-24T18:00:00+08:00
---

# Phase 11 checkpoint - security, answer queue and abuse probe done; awaiting owner reply on topic-less questions

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
evaluation) has started with one finding awaiting an owner reply: E1 below. There is deliberately no final handoff.

- E1: document questions outside the 7 reviewed topics ("How do I apply for a leave of absence?", "Paano
  mag-request ng transcript of records?") route RAG correctly, but retrieval returns `needs_subject`, which
  integration maps to `clarify`. Students get a bare "Please clarify the missing information" with nothing to
  clarify. Options were put to the owner (unavailable + office referral, or a clarification naming the topics).
- E2 (minor): "What are the prerequisites of CC 6?" names CC 3/L and CS 2/L, but framed as an eligibility
  clarification rather than a plain list.
- Correct, not defects: "Can I take CC 5? I passed CC 4." (en/Taglish) reports CC 3/L as unknown, as intended.

## Repository State

Branch `feat/p11-backend-api` from `dev` `cbaa6a7`; commits through `5ee7b50` plus this checkpoint commit, nothing pushed.

## Verification Evidence

- Each code task: RED observed, then GREEN; every new guard mutation-checked (each mutation failed a test).
  Latest focused runs: API files 76 passed; photo rows 27 passed + 2 strict xfails; scorer 10; style floor 27;
  routing style/router 131; research pipeline 2.
- Roster run 16 (HEAD `6abfb40`, run 15 settings): 0 of 63 status/decision changes; replies en 21/21, fil 21/21,
  Taglish 15/21 (run 15: 10/21); 23 of 25 answered texts identical, 2 changed only in language.
- Photo measurement: 42 simulated photos, 0 silent errors; plain layout exact in all 7 conditions; Report-of-Grades
  style exact in flat/dim; owner's real screenshot refused (two causes pinned as xfails).
- Full suite at `72ec6d4`: 6441 passed, 6 skipped, 2 xfailed (documented photo limits), 1552 subtests,
  0 failed, 20m00s. Log: workspace `audit-evidence/p11-20261023/full-suite-security.log`.
- Security fixes: RED observed for each, then GREEN, and each guard mutation-checked. A re-probe of S1 (1000
  cookie-less requests) left a new student's `/chat` at 200.
- Answer queue: RED -> GREEN; three mutations (no busy refusal, no slot wait, no release) each failed the test.
  S8 wire fix: RED reproduced the live `part_count_mismatch`; 358 routing tests pass; two mutations caught.
- Live abuse probe (14 cases): 12/12 refused before the fix, the mixed case 2/2 after it; 0 leak markers.
- Live capacity probe: 1 student 25.6 s; 3 at once 23.5/38.5/49.4 s; 6 at once five served by 76.8 s and the
  sixth `answers_busy` in 0.5 s; statuses identical to a sequential run. Logs in `live-api/`.
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
decision ("authorized user/session"): consistent, no discrepancy.

## Next Action

1. (Done) Security check: [review](2026-10-24-phase-11-security-review.md).
2. More evaluation that retrieval and Prolog have no remaining problems. First apply the owner's E1 answer
   (test-first), then continue from:
   - the two live-smoke observations above;
   - roster run 16 (`audit-evidence/p11-20261023/roster16/`): 19 clarification and 19 non-answer statuses.
   Use the counted harnesses; keep the evaluation families separate from tuning.
3. Then UI integration (co-worker's design). Install `ai` v7, `@ai-sdk/react` 4 and `@supabase/ssr`, and upgrade
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
security review and S1/S2/S4-S8 fixes, the answer queue, the abuse and capacity probes, full suite at `72ec6d4`, the three style prompts, the two reverted photo-threshold attempts.
