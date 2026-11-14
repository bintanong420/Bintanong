# Phase 11 pre-phase research (backend API, streaming adapter, photo rows, Taglish follow-ups)

23 October 2026. Required by the AGENTS.md pre-phase research rule. Research proposes; it authorizes nothing.
Items marked **owner decision** need an explicit answer before they are used. Scope (owner, 23 Oct): Phase 11
**backend only** — master 16.1/16.3, addendum 23.3 (`POST /chat` with session context), 24.1 and 24.2. No UI.

## Environment checked before research

- Worktree `p11`, new branch `feat/p11-backend-api` from `dev` `cbaa6a7` (the worktree had been created on
  `p09-backend-api`, which also points at `cbaa6a7`). `main` holds only the initial commit; `dev` is integration.
- Ignored inputs match the main checkout byte for byte (sha256 over sorted files): `.env` (1 file),
  `.superpowers` (100), `supabase/.temp` (1), `dataset/` (62), jsonifier `dataset/` (40).
- `backend/uv.lock`, `frontend/package-lock.json` and root `package-lock.json` are identical to HEAD and to the
  main checkout (git blob hashes). `uv` is not on this shell's PATH, so `uv lock --check` was not rerun.
- `phase_state.py validate` and `can-advance`: valid, can advance (Phase 10 handoff complete).
- Running: `bintanong-p09-cuda-latency` (Gemma 4 E4B, :18088, healthy) and the local Supabase stack.
- Context consulted: thesis physical 17-18 (scope/limitations), 65-66 (isolated chat context, uploads isolated,
  no stored grades, read-only, visible AI-guide notice) and the routing PNG. No discrepancy with this scope.

## Existing assets to reuse (build faster)

| Asset | Where | Reuse |
| --- | --- | --- |
| Session store, cookie credential design (D3), uploads, worker, capture | `backend/bintanong_private_context/` | Endpoints are thin wrappers; no new session logic. |
| Answer pipeline with `routed_sink` | `Orchestrator.run`, `AnswerPipeline`, `Generator` | `POST /chat` calls the same path the roster uses. |
| Real-data composition | ignored `audit-evidence/p09-real-data-20261021/smoke.py`, `p10-20261023/multiturn.py` | Move the composition (not the data) into tracked code configured by env paths. |
| Health endpoints | `backend/bintanong_api/main.py` | Keep; add routers through an app factory. |
| Photo simulator and recorded OCR boxes | `ocr_bench/simulate.py` (tilt, perspective, hard); `audit-evidence/p10-20261023/photo-probe/ocr-rapidocr-*` | Develop row grouping on recorded word boxes; no OCR rerun needed for the geometry. |
| Roster and multi-turn harnesses | `roster13.py` (63 cases, run 15 baseline), `multiturn.py` (12 cases, run 5) | The 24.2 counted rerun and the no-regression comparison. |

## Findings

1. **The AI SDK is not installed.** `frontend/package.json` has only Next 16.3.5 and React 19.3.0. Master 2 records
   `ai` 6.0.177 as intended; it was never added. npm registry today: `ai` latest **7.0.150** (7.0.0 published
   25 Jun 2026); v6 still maintained on tag `ai-v6` = **6.0.314** (`@ai-sdk/react` 3.0.317; v7 pairs with 4.0.154).
   The v7 migration guide reports no change to the UI message stream protocol (header
   `x-vercel-ai-ui-message-stream: v1`), only a new `reasoning-file` part. v7 needs Node >= 22; the repo pins 24.21.0.
   **Consequence:** the backend adapter can target protocol v1, which both majors read. The contract test
   against the SDK's own parser needs the package installed (a frontend dependency change).
2. **No new Python dependency for streaming.** FastAPI 0.141.1 (pinned) has native SSE (`fastapi.sse.EventSourceResponse`,
   since 0.135.0; SSE line-splitting and status-code fixes in 0.140.12/0.140.13). Expected gain: the adapter is a pure
   event encoder plus a generator, unit-testable with golden byte output.
3. **Stream design (master 16.2/16.3).** Do not stream draft text: the answer is shown only after validation. So the
   stream carries transient `data-status` progress parts during routing/evidence/generation, then one validated text
   block, `source-document` parts for citations, typed `error` parts, and `finish` + `[DONE]`. Live progress needs a
   small optional progress callback in the pipeline (the orchestrator now returns its events only at the end).
4. **Cookie and CSRF (OWASP CSRF cheat sheet).** Use `__Host-` prefix (Secure, Path=/, no Domain), HttpOnly,
   SameSite=Strict. SameSite alone is not a CSRF defence: on unsafe methods also reject `Sec-Fetch-Site: cross-site`,
   verify `Origin` against a configured allowlist (never `null`), and require a JSON or explicit upload content type.
   Browsers treat `http://localhost` as secure, so Secure cookies work in development; tests must use an
   `https://testserver` base URL. The Next.js side should proxy `/api/*` same-origin (frontend work, later).
5. **Single process.** `SessionStore` is memory-only, so the API must run one worker process; more workers would
   split sessions. Disclose; no shared store (no persistence is allowed).
6. **Duplicates, cancellation, disconnect.** One in-flight chat per session (second request -> 409 typed error).
   A client disconnect cancels the pipeline task and skips conversation capture, so a half-finished turn never becomes
   context. A retry with the same client message id after completion returns `already_answered` instead of rerunning.
7. **Composition gap.** The real-data composition exists only in ignored scripts. `RuntimeApplication` is the
   synthetic-only composition. A tracked factory (paths and release id from env, data stays ignored) is needed to run
   `POST /chat` on real data. The query encoder loads sentence-transformers in-process, which the `api` Docker extra
   lacks: the live API runs in the shared venv this phase; container deployment remains master 20 work.
8. **Student-facing text leaks diagnostics.** Rendered answers include lines such as
   `Sakop ng check: check_prerequisite_eligibility; curriculum_id=...; offline-research-runtime-v1-<hash>` and raw
   `ev-<hash>` ids. Master 16.2 keeps routing labels and predicate names in researcher diagnostics.
9. **24.2 root cause (lead, to be confirmed test-first).** The renderer has Taglish templates, but the Taglish F3/D3
   turns (turn 1 too) were rendered with Filipino ones: the style model chose `filipino` although the message has
   English ("i-take", "Passed", "for that subject"). The owner's 22 Oct floor only lifts `english_only` -> `taglish`
   when Filipino function words appear; there is no symmetric floor. Not follow-up specific.
10. **24.1 photo rows.** The probe's OCR text was good; row grouping by vertical centre failed under tilt and
    perspective. Standard remedies, in cost order: estimate skew from word-box baselines (median slope / line fit),
    rotate box centres, then group; perspective needs a homography from the page quad (OpenCV
    `getPerspectiveTransform`). Refuse when residuals or row-spacing are inconsistent, when a row lacks exactly one
    mark, or when two codes share a row. All needed libraries are locked (rapidocr 3.9.2, onnxruntime 1.30.0,
    opencv-python 5.0.0.93, numpy 2.5.3) but only in the `tools`/`ocr-cpu` extras, not `api`.

## Recommended order (dependency order; each step test-first, small commits)

1. Phase plan and checkpoint.
2. App factory, session cookie dependency, CSRF guard, `DELETE /session` (issue, expiry, deletion, isolation tests).
3. `POST /chat` (JSON) on an injected pipeline: session context in, `routed_sink` -> `capture` -> `set_conversation`,
   clarification replies through the same context, typed errors, one in-flight request per session.
4. UI-message-stream v1 encoder (golden tests) and the streaming `POST /chat`, with disconnect/cancel/retry tests.
5. `POST /uploads` -> pending rows; `POST /uploads/{id}/confirm`; `DELETE /uploads/{id}`.
6. `GET /sources/{id}` from the pinned release only.
7. Student render profile (if approved), then 24.2 style fix with the counted roster and multi-turn reruns.
8. 24.1 deskewed grouping and strict scorer on recorded boxes and simulated photos; wire into uploads only if approved.
9. Tracked real-data composition, live HTTP smoke, full suite, handoff.

Steps 2-6 are independent of 7-8; 24.1 geometry can run in parallel with the API work.

## Owner decisions needed

- **O1 AI SDK:** keep the frontend install deferred until the frontend starts (backend targets protocol v1), and
  which major then: 6.0.314 (master's "SDK 6") or 7.0.150 (current, same wire protocol).
- **O2 Photo OCR in the API:** add the already-locked rapidocr 3.9.2 + onnxruntime 1.30.0 CPU (+ opencv) to the
  `api` extra once the geometry passes on simulated photos; and provide private real phone photos for a
  "supported" claim. Without both, photos stay disclosed as unsupported.
- **O3 `GET /curricula`:** a read-only program/curriculum list for the picker (uploads and checks need a curriculum).
  Not in master 16.1.
- **O4 Student render profile:** move diagnostic lines and raw evidence ids out of the student text into a
  researcher-only field; the validated content is unchanged.
- **O5 Style floor:** a symmetric floor, `filipino` -> `taglish` when the message has literal English conversation
  words (common English function words, and English verbs with Filipino affixes such as "i-take", "nag-cheat").

## Sources

- AI SDK UI message stream protocol: https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol
- AI SDK 7 migration guide: https://ai-sdk.dev/docs/migration-guides/migration-guide-7-0
- npm registry metadata, queried 23 Oct 2026: `npm view ai dist-tags`, `npm view @ai-sdk/react dist-tags`
- Cloudflare changelog, AI SDK v6/v7 support (23 Jul 2026):
  https://developers.cloudflare.com/changelog/post/2026-07-23-ai-sdk-v6-v7-support/
- FastAPI SSE tutorial and release notes: https://fastapi.tiangolo.com/tutorial/server-sent-events/,
  https://fastapi.tiangolo.com/release-notes/
- OWASP CSRF Prevention Cheat Sheet:
  https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- Repository: `plans/2026-10-23-photo-ocr-probe-results.md`, `plans/2026-10-23-multi-turn-observation-results.md`,
  `plans/phase-10-handoff.md`.
