---
artifact: phase-plan
phase: 10
status: complete
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-09-handoff.md
---

# Phase 10 private files and session context implementation plan

**Goal:** a server-owned, memory-only student session that holds confirmed private grade facts and a
small structured conversation context, with isolation, expiry and deletion tests. Neither may reach
institutional retrieval or persistent storage.
**Spec:** master 15 and addendum 23; [pre-phase research](2026-10-23-phase-10-pre-phase-research.md);
[conversation-context requirement](2026-10-23-conversation-context-requirement.md); Phase 09 final handoff.
**Worktree:** `p10` / `feat/p10-private-files-pipeline` from `ccc3cea`.
**Execution:** inline TDD (RED -> GREEN -> REFACTOR) per step, small cohesive commits, synthetic
fixtures only in tracked tests, one fresh whole-change review before exit.

## Owner decisions (23 Oct 2026)

- D3: opaque `secrets.token_urlsafe(32)` credential in an HttpOnly, Secure, SameSite=Strict cookie;
  30-minute idle lifetime; in-process memory only (no Redis or database).
- D1 (OCR engine install, Docling pin) and D2 (Gemma 4 E4B vision measurement): deferred to step 5.
- D4: add pypdfium2 5.13.0 and Pillow 12.3.0 (already locked through `tools`) to the `api` extra.
  Uploads arrive as a raw request body, so python-multipart is not added.

## Design and constraints

New package `backend/bintanong_private_context/` (master 20 `private_context`), following the
existing `backend/bintanong_<name>/` layout:

| Module | Owns |
| --- | --- |
| `sessions.py` | `SessionStore`: issue, resolve by credential, touch, expire, delete, wipe; injectable clock; per-session bounded slots for confirmed facts, pending extraction and conversation context. |
| `uploads.py` | Byte cap while streaming, signature sniffing (`%PDF-`, PNG, JPEG), PDF page cap, image open with `formats=['JPEG','PNG']`, pixel cap. Filename and Content-Type are never trusted. |
| `grades.py` | Born-digital PDF text (pypdfium2) -> candidate rows (course code, grade, term) with line evidence; short-form course matching against the session's curriculum; unknown codes stay unknown. |
| `conversation.py` | Conversation-context contract (topic/subject, course, program, curriculum ids and bounded labels), capture after a validated answer, and follow-up reference checks. |

- Raw file text never reaches the router or generator. Only student-confirmed rows become
  `ScopedFact`s inside `RequestContext.facts`, with the session's own `session_id`.
- Bytes are dropped once extraction returns. No temp files in step 3 (pypdfium2 reads bytes). Nothing is
  logged with grades, file text or credentials. Session state is cleared on delete, expiry, failure and
  restart (memory only).
- Retrieval and Prolog still run fresh each turn. Context ids are rechecked against the curriculum.
  Ambiguity or a topic switch leads to clarification, never a guess.
- Existing `RequestContext`, `ScopedFact`, runtime catalog and orchestrator are reused, not
  duplicated. No change to institutional contracts, Supabase schema or release state.
- HTTP wiring (`POST /chat`, `DELETE /session`, upload endpoint) belongs to Phase 11. This phase
  exposes the backend functions and tests them. A thin FastAPI router is added only if an
  isolation test needs the cookie boundary.

## Tasks (dependency order)

1. **Session store.** Credential issue/resolve, idle expiry, delete, wipe, slot bounds. Tests: cross-session
   access denied (facts, pending upload, context), expired/deleted credential rejected, forged/short
   credential rejected, restart leaves nothing.
2. **Dependency wiring (D4).** Add the two pins to the `api` extra and refresh `uv.lock` without
   changing any locked version. Then do upload validation with synthetic hostile files: oversize,
   wrong signature, renamed type, page bomb, pixel bomb, non-JPEG/PNG Pillow formats, truncated PDF.
3. **Born-digital PDF grade facts.** Extraction -> candidate rows -> student confirmation -> `ScopedFact`s.
   Tests: confirmed rows reach `RequestContext.facts`; unconfirmed or unknown codes do not; injected
   instructions in the PDF never reach routing text; bytes released.
4. **Conversation context (section 23 backend).** Capture, router input (bounded tokens), host reference
   check, clarification on ambiguity or a topic switch; isolation/expiry tests. Router prompt changes
   need a counted roster rerun.
5. **Photo OCR (gated on D1/D2).** Run the existing `ocr_bench` (simulated photos first) and wire only a
   configuration that meets Q11. Otherwise disclose that photo input is unsupported.
6. **Exit.** Full suite, ruff, a security review of the new package, the counted roster rerun (no lost
   single-turn answer), handoff.

## Verification

Test Python `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider <tests> --basetemp=<audit-evidence dir>`.
Full suite before each phase-level claim. Baseline at `ccc3cea`: 6201 passed, 6 skipped (Phase 09 handoff).

## Exit gate

The master 15.3 isolation cases and the 23.4 isolation/expiry/deletion cases pass. No persistent
personal academic record or conversation store is introduced. Multi-turn cases either resolve or
clarify, with zero wrong carry-over in the counted run. No previously correct single-turn answer is lost.
Report the tested boundary only. Institutional release, activation and school approval stay held.
