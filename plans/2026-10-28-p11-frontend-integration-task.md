# Phase 11 frontend integration — Codex B

## Scope and baseline

- Worktree `p11-frontend-integration`, branch `feat/p11-frontend-integration`, baseline
  `12ac411b5dbda72a3641e980e63de49c34cec870`.
- Owner confirmed **snapshot `e172f53c19bdd5d30ef5df2db4bf80ee47e27c3c`**, rather than latest,
  in this session (28 October 2026; confirmation relayed by coordinator). Do not ask again.
- Integrate its `frontend/` paths only; no whole-branch merge. Backend API tasks 1–6/9 already
  exist; inspect/reuse them. Own `frontend/`, `backend/bintanong_api/`, API tests and this record.
  Central phase snapshots belong to Claude; lane handoff goes to Claude for central review.
- Baseline requirements: master 3/11/13/16/23–26, Phase 11 plan, Phase 10 handoff,
  two-developer and model-workstream split. No new product scope or release permission.
- Read-only undergraduate advisory context, English/Taglish replies, RAG/Prolog/Hybrid routing,
  source gaps and privacy guards remain. Research source package/pins stay unchanged.

## Shared dependency proposal — awaiting owner decision

Single implementer: Codex B. Adopt **exactly** snapshot `e172f53`'s `frontend/package.json`
and `frontend/package-lock.json` as part of the approved UI snapshot, and run `npm ci` in this
worktree (no fresh version selection or other lockfile changes). Installed Next in both existing
workspace frontends is 16.3.5, incompatible with snapshot's 16.4.3 pin; no junction created.

| Change | Exact pins |
| --- | --- |
| Upgrade | next 16.3.5 → 16.4.3 |
| Existing unchanged | react/react-dom 19.3.0; @types/node 24.10.0; @types/react/@types/react-dom 19.2.2; typescript 7.0.2; Node 24.21.0 |
| Add runtime | @ai-sdk/react 4.0.156; ai 7.0.152; @radix-ui/react-separator 1.2.0; @radix-ui/react-slot 1.5.0; class-variance-authority 0.7.1; clsx 2.1.1; lucide-react 1.61.0; tailwind-merge 3.7.0; zod 4.6.7; @supabase/ssr 0.12.7; @supabase/supabase-js 2.118.0 |
| Add development | @tailwindcss/postcss 4.3.3; postcss 8.5.31; tailwindcss 4.3.3 |
| Overrides | sharp 0.35.5; source-map-js 1.2.2 |
| Scripts/module | type=module; typecheck=tsc --noEmit; test:ui=node --experimental-strip-types --test tests/*.test.mjs |

Reason: preserve co-worker design/auth and test the real SDK parser against existing stream.
Compatibility will be checked with synthetic Node tests, TypeScript, build and API regressions;
dependency adoption does not authorize auth configuration/hosted writes or public deployment.
Until approved: read-only comparison and standalone test preparation only; no product import,
package/lock mutation, installation, or dependency workaround.

## Execution and acceptance

### Shared interface proposals — pending coordinator/owner review

- `data-answer` currently contains only `status`/`conditional`; snapshot's strict SDK consumer
  requires `language` and `missingFields`, with optional canonical `clarification` (printed course
  codes, completion/enrollment kind, program/curriculum scope). Proposal: additive API metadata
  from existing validated answer/known course labels, without changing CandidateAnswer contracts.
  Reuse snapshot's API presentation implementation only after regression RED; Codex B implements.
- Snapshot forwards server-resolved Supabase bearer auth and promises verified PSU identities,
  while this lane's current FastAPI has no auth dependency/account-bound sessions. Snapshot adds
  API auth plus account admission/session binding; the latter changes shared
  `backend/bintanong_private_context/sessions.py` and is outside lane ownership. Proposal: one
  agreed implementer adopts/reviews that small account-binding change test-first; Codex B handles
  API auth/admission. Do not expose a student runtime with frontend-only identity enforcement.
- Snapshot's runtime composition also reaches shared embedding/retrieval/runtime modules.
  Do not wholesale import those stale branch versions. First reuse current research pipeline;
  any missing composition seam will receive a separate minimal proposal.

1. Compare snapshot's auth/proxy/transport/UI to current API; record concrete mismatches.
2. After dependency decision, import exact approved frontend paths; characterize supplied behavior.
3. Add failing synthetic regressions for integration mismatches; observe RED before the smallest fix.
4. Verify UI tests, typecheck/build, focused API/security/stream tests and SDK stream consumption.
5. Merge newer backend branch only when clean/conflict-free; stop/report conflicts.
6. Coordinate exclusive model slot with root, then live HTTP smoke LAST. Root coordinates full suite/review.

Acceptance: functional student chat/progress/sources, scope/clarification, upload confirmation and
deletion/session reset; no researcher ids/check-scope/predicates/hashes in rendered student text;
existing same-origin/session/ownership guards intact. Unsupported functionality is disclosed.

## Verification and recovery

- Evidence: `C:/Coding-projects/bintanong_workspace/audit-evidence/p11-frontend-integration-20261028`.
- Python: shared `p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`, `PYTHONUTF8=1`,
  `-X utf8 -B -m pytest -q -p no:cacheprovider`, external lane basetemp. Focused only initially.
- Frontend after approval: `npm run test:ui`, `npm run typecheck`, `npm run build`.
- Initial Git clean; handoff inspect valid, cannot advance; checkpoint HEAD is historical `eedbc07`
  versus verified lane baseline `12ac411`. No central metadata edits in this lane.
- No installs, hosted writes, model downloads, activation, push or main-branch merge performed.
- LIVE RUN: none. No full suite started.
- Context consulted: thesis physical 17–18 (scope/private data) and 39–44 (symbolic architecture),
  routing PNG, master 3/11/13/16/23–26, Phase 10 handoff and Phase 11 plan/checkpoint. The thesis's
  closed-world example stays illustrative; current unknown-versus-unmet requirement governs.
- Coordinator baseline verification: API presentation/stream/chat 43 pass (reused evidence,
  `p11-workstream-split-20261028/api-baseline.log`); setup copy audit 62 dataset files/lane,
  zero mismatches and environment parity. No tests claimed as run by this lane yet.

## Current next action

Await concrete dependency/lock/install approval via coordinator while comparing snapshot contracts.
