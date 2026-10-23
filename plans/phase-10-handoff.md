---
artifact: phase-handoff
phase: 10
status: complete
plan: plans/phase-10-private-files-session-plan.md
final_commit: 193ab7b
next_phase: 11
completed_at: 2026-10-24T01:30:00+08:00
completion_scope: owner-approved offline research/software milestone; photos unsupported and other limits disclosed
---

# Phase 10 final handoff (private files and session context)

Owner, 23 Oct 2026: "close with disclosures as long as you are sure that we are to proceed and no more left work
here". Before closing, the missing master 15 "transient parser job" deliverable was built (`193ab7b`). This is not
school approval, institutional release, deployment or activation.

## Written exit gate (plan; master 15.3 and 23.4)

| Gate | Evidence | Status |
| --- | --- | --- |
| Session B cannot reach A's file, extraction, facts or context | `test_private_context_sessions.py`, `test_private_context_conversation.py` | met |
| Private content not reachable through institutional search | private package imports no storage, retrieval, embedding or ingestion code (`test_private_context_isolation.py`) | met (tested boundary) |
| File text cannot steer routing, rules or ownership | rows carry only matched code, candidates and marks (`test_instructions_inside_the_file_never_leave_the_extractor`) | met |
| Gone after delete, expiry, failure and restart | memory-only store; no temp files; a refused confirmation stores nothing | met |
| No grades or ids in logs, errors or exports | package has no logging, print or file writes; reasons are fixed codes | met |
| No persistent personal records or conversation store | nothing written to disk or Supabase | met |
| Multi-turn: resolve or clarify, 0 wrong carry-over | counted run 5 at `ea64ead`: 12/12, 0 wrong ([results](2026-10-23-multi-turn-observation-results.md)) | met |
| No previously correct single-turn answer lost | roster run 15: all 63 statuses and decisions equal run 14; 25 answered texts byte-identical | met |

## Delivered (`backend/bintanong_private_context/`)

| Module | What it does |
| --- | --- |
| `sessions.py` | Memory-only store. Opaque `token_urlsafe(32)` credential, SHA-256 digests only, 30 min idle expiry (D3), delete/wipe, 1000-session bound. Slots for facts (cap 256), pending extraction and conversation context. |
| `uploads.py` | Streaming byte cap (15 MiB). Type sniffed from the bytes only. PDF page cap 20. Images opened with only the sniffed Pillow plugin, 60 MP cap. |
| `grades.py` | Born-digital PDF rows matched only by the session curriculum's reviewed aliases (short forms included). Unknown codes counted, never matched. The student states passed/failed per row; a grade is never mapped. |
| `worker.py` | Spawned child parser job with a 30 s timeout. Timeout or crash refuses the upload and ends only the child. |
| `conversation.py` | `capture` (check target, else a single course; ids only) and `follow_up_context`. |

Routing:
- `ConversationContext` and `RequestContext.conversation` carry the previous turn.
- `previous_course_quote` (the model marks the words, the host supplies the course) is offered only with stored
  context.
- Carried scope fills only an unnamed scope for a check or back-reference.
- Words that name a course are never a back-reference.
- Single-operation index repair.
- Optional `Orchestrator.run(routed_sink=...)`.

Single-turn prompt `6a9c2e7e...` (Phase 09 v17) and schema `7cde5320...` are unchanged.

## Commits (from `ccc3cea`)

`9b2cdb4` plan · `4d596be` sessions · `55aba06` D4 deps · `bd39906` uploads · `34f22fc` grades · `aabb5ee`,
`0f2b70d`, `ff448ba` conversation/router/sink · `13e4c7f`, `304368a`, `9950e09`, `c470ca1`, `ea64ead` live-precheck
fixes · `48ee1f1` isolation tests · `193ab7b` worker and fact cap · docs/checkpoints in between.

## Versions and digests

- Python 3.13.7, FastAPI 0.141.1. pypdfium2 5.13.0 and Pillow 12.3.0 were added to the `api` extra (D4); the
  uv 0.12.17 relock changed no version and `uv lock --check` passes.
- Shared test venv (not the repo): onnxruntime 1.30.0 CPU installed (D1), rapidocr aligned to the locked 3.9.2,
  pypdfium2 5.14.0 (drift; images follow the lock). RapidOCR model hashes are in workspace
  `audit-evidence/p10-20261023/rapidocr-models.json`.
- Gemma 4 E4B, the Phase 09 GGUF (not re-hashed), served by `bintanong-p09-cuda-latency`.
- Node 24.21.0 / npm 11.19.0.

## Exit verification

- Full suite at the final tree `193ab7b`: **6295 passed, 6 skipped, 1552 subtests, 0 failed** (20m12s; log in
  workspace `audit-evidence/p10-20261023/full-suite-final.log`). Earlier trees: 6218, 6238 and 6284 passed.
- Command: `PYTHONUTF8=1 <venv python> -X utf8 -B -m pytest -q -p no:cacheprovider tests --basetemp=<audit-evidence>`.
- Mutation checks on every new guard (recorded in the checkpoint history).
- No linter is installed in the venv or on the host; not run.
- Security review (manual, private package): no blocking finding; the risks are listed below.

## Disclosed limitations and risks

1. Photos and scans are unsupported. The RapidOCR probe silently misaligned grade rows on tilted, perspective
   and hard photos ([probe](2026-10-23-photo-ocr-probe-results.md)), so uploads return `photo_ocr_unavailable`.
2. HTTP endpoints, the cookie and `DELETE /session` are Phase 11. Phase 10 delivers and tests the backend
   functions only.
3. The worker has no per-process memory limit on Windows. Memory is bounded by the caps and, in deployment, by
   the container. A 60 MP JPEG may take about 180 MB to decode.
4. Turn-1 statements ("I passed CC 4") are not carried (master 23), so follow-ups may ask for them again.
5. Taglish follow-up host lines come out mostly Filipino (known Phase 09 limit). Document follow-ups keep the
   topic but withhold details outside the reviewed facts.
6. Grade-row matching was tested on synthetic layouts only; real PalSU grade-report formats are unverified.
7. 12 multi-turn cases and one attempt each: not an accuracy rate. The Phase 12 multi-turn family is still due.
8. Frontend `npm audit`: 3 pre-existing findings (2 high, 1 critical), not addressed.

## Next-phase prerequisites (Phase 11, master 16 + 23.3)

- Pre-phase research per AGENTS.md, then the owner summary.
- Wire `POST /chat` with `SessionStore`, an HttpOnly/Secure/SameSite cookie, `routed_sink` -> `capture` ->
  `set_conversation`, and `DELETE /session`.
- Upload endpoint: raw body -> `read_capped` -> `validate_upload` -> `extract_isolated` -> confirm UI ->
  `confirm_pending`.
- Keep the institutional release, undergraduate-scope, source-gap, privacy and one-week-cap boundaries.
