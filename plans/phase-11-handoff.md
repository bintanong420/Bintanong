---
artifact: phase-handoff
phase: 11
status: complete
plan: plans/phase-11-backend-api-plan.md
final_commit: e31ccab
next_phase: 12
completed_at: 2026-10-29T23:59:00+08:00
completion_scope: owner-approved research/software milestone with disclosed gaps; deployment cancelled (owner 29 Oct)
---

# Phase 11 final handoff (backend API, frontend integration, answer accuracy)

Owner, 29 Oct 2026: finish by 30 Oct, deployment cancelled, MVP first. Owner chose "Browser check, then close (Recommended)" after seeing the gaps listed below. This is not school approval,
institutional release, public deployment or hosted activation of the 560-chunk package.

## Exit gate (plan; master 16, addenda 23.3/24)

| Gate | Evidence | Status |
| --- | --- | --- |
| Every endpoint has API tests (session, chat, uploads, confirm, delete, sources, curricula, health, guests, auth) | `tests/test_api_*.py` (145 pass at `37688aa`) | met |
| UI message stream v1 encoder | `tests/test_api_stream.py`; frontend uses it (guest mode 04e6d38) | met; SDK parser contract test not added |
| Live HTTP: RAG, Prolog, Hybrid, follow-up, upload, deletion | 29 Oct guest smoke on the local 560 package ([results](2026-10-29-local-documents-website-results.md)) | met (single run each) |
| Website runs the evaluated composition | `d1a2d53` local-documents pin (topic selection, routing context, short review refs) | met |
| 24.2 counted Taglish follow-up rerun | superseded in part by the 27 Oct English/Taglish reply decision; counted rerun not done | **not met (disclosed)** |
| 24.1 photo/scan grade rows | not built; born-digital PDF upload only | **not met: photos unsupported (disclosed)** |
| No persistent grades, transcripts or private files; no logs with raw text | Phase 10 tests retained; memory-only sessions | met |
| Master 16 browser exit gate | Playwright guest run: document, prerequisite, upload -> confirm -> follow-up, delete; 0 console errors ([results](2026-10-29-local-documents-website-results.md)) | met (single run; dev server from the integration worktree) |
| Full suite passes | batched at `e50e18a`: 7247 pass / 1608 subtests, 6 skip / 2 xfail, exit 0 (later commits docs only) | met |

## Accuracy evidence

- 91-case simple-question gate: run 4 77/91 (`9553ed9`); honors/probation fix `f235319` (+4 live).
- Phase 12 benchmark (50 en/Taglish, four owner categories): full system 40/50, plain Gemma 3/50 strict, 8/50
  content-only ([results](2026-10-29-phase12-benchmark-results.md)); 40 cases were development cases (disclosed).

## Key commits since Phase 10 handoff

f235319 Handbook policy partial coverage · d1a2d53 local-documents pin · 37688aa alias-free student text ·
38ccb83 printed penalty row names in the selector · 7f8c02b exact penalty-row quotes · earlier: guest mode 04e6d38,
account sessions 307a2bd/df3811a, Charter layouts e574d67, FAQ 7/8 split package, F4 clarify 19d762f,
excluded-program notice 4221d26, topic families a4f33f7.

## Versions and digests

- Gemma 4 E4B `gemma-4-E4B-it-UD-Q4_K_XL.gguf` via llama.cpp CUDA image `sha256:f66a5229…` on :18088; 8192 context,
  768 output. SEA-LION E5 600M encoder (verified assets, p05 calibration).
- Local package: 560 chunks, embedding set `f7a7f1b01770834c71838eccd6347ab1db798f0fe37917c9426fb79d93592218`;
  pin `7a7585e1…`, seal `954d376e…`, config `67d9c68c…` (A/p11-local-documents-20261029).
- Hosted: active research release `p11-research-corrected-20261026` (78 chunks / 39 curricula), unchanged.

## Deviations, rulings and risks

- Deployment (master 18 / Phase 13) cancelled by the owner; hosted 560 activation deferred (about 2-4 hours).
- Remaining benchmark failures (10): summer load, leave length (Taglish), CC 5 after failing CC 4 (English),
  second-year (Taglish), graduation residence, improper uniform (Taglish), plagiarism (router picks a not-stated claim).
- Hybrid questions ask a curriculum clarification before answering their procedure part.
- Warm backend times only (median about 26 s); student-visible end-to-end latency unmeasured.
- Real PSU sign-in verification owner-deferred.
- This worktree's `frontend/node_modules` lacks `@supabase/ssr`; the browser check ran Next.js from the
  `p11-frontend-integration` worktree (same app code). Run `npm ci` in `frontend/` here before using it directly.
- Prerequisite answers took about 60-70 s in the browser (single observation).

## Next-phase prerequisites (Phase 12)

Benchmark and conditions A/C already run; Phase 12 records methodology, scoring and thesis tables from this evidence.
