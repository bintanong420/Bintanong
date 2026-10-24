# Original frontend + Lawrence Phase 11 API integration

Owner go24Oct, then corrected direction: bring Lawrence's API into the original frontend. Working branch
feat/p11-frontend-integration derives from frontendc17dcb2; merge227efaa brings origin/feat/p11-backend-api34a21ca.
Main owner checkout and both previous implementation branches remain intact. No push/deployment performed.

## Implemented

Original shell/campus assets/compact composer/message alignment/system themes retained. Root now uses actual
chat, scope picker, source inspection, PDF review/confirmation/removal, Stop, waiting/busy and acknowledged
New chat. /chat redirects to root; /dev/health retained. Example selector/simulated services leave the student path.

SDK7 adapter consumes Lawrence's messages/SSE/source/error contracts. Per-account admission, verified PSU
Google auth, account-owned private sessions and checked language/missing-field summary are narrow additions.
Canonical academic results, source guards and Lawrence's routing/generation/queue/parser remain authoritative.
Tracked research composition validates hosted39 curricula/19-document-chunk release and the existing derivative
review index; reuses a strict resident encoder port. Original source/register/provenance limits remain.

Dependencies approved individually: Next16.4.3, ai7.0.152, @ai-sdk/react4.0.156, @supabase/ssr0.12.7,
@supabase/supabase-js2.118.0; sharp0.35.5/source-map-js1.2.2. React19.3.0/TypeScript7.0.2 retained.
No Python dependency/model download/database change. npm audit reports0 vulnerabilities.

## Verification actually performed

- Merge:83 selected API tests pass; frontend files byte-unchanged in merge.
- Auth/metadata: RED14+2 observed, GREEN131 selected API/private-session tests.
- Transport/state: RED missing modules; installed SDK7 parses actual Python-emitted synthetic stream.
- Current frontend:43 tests pass on Node24.21; TypeScript and Next16.4.3 production build pass.
- Composition: RED missing loader/cleanup; public-key guard RED1.174 API/runtime/private-session/docs tests pass
  before final review; system Python3.13.12. Own earlier venv3.13.5 lacks ReportLab; no new install.
- Actual Next/FastAPI synthetic browser fixture:10 control families/16 requests pass, including real isolated
  PDF parsing, explicit choices, same-file reselection, rejection/removal isolation, sources, failed clear,
  Stop/account-slot release, sign-out, IME/Shift+Enter, light/dark/system and short-window/reflow.
- Browser exposed scope display-label leakage into upload query. Focused regression RED then GREEN after
  filtering to programId/curriculumId. Full-page screenshot briefly shows an offscreen skip-link artifact;
  live computed position is y=-160, focus remains TEXTAREA, so no CSS workaround was introduced for that artifact.
- Configured research API readiness200 with all probes including student_runtime; unauthenticated curricula401.
  Actual pipeline samples: Symbolic answered/validated4 sources32.643s. Initial RAG unavailable91.235s and Hybrid
  insufficient_evidence43.689s. Subsequent bounded RAG traces with and without selected curriculum both return
  ready retrieval and a validated handbook1.0 ->98-100/Excellent answer with1 source card/page46. No scope/filter
  change retained: scoped RAG already worked on the unchanged backend. These are observations, not an SLA,
  broad model accuracy or completed live-browser academic route acceptance.

Ignored scripts/logs/screenshots remain in workspace audit-evidence/p11-20261024 (integrated-ui-browser*,
selected-runtime-observation*, selected-rag-*, frontend-integration-runtime.json). Only synthetic student
inputs were used; credentials, private files and raw model/source evidence remain untracked.

## Remaining

Google provider is disabled in hosted Supabase; real PSU/non-PSU OAuth acceptance needs external configuration
and a human login. Auth fails closed; no bypass shipped. See [setup](../docs/development/student-ui-integration.md).
Inherited E3 shifting clarification, pending-intent/replay, broader aliases, actual PDF layouts and complete
Hybrid/language/latency acceptance remain open. Photos/scans unsupported. Figma tools were unavailable;
existing checked UI/annotations/assets were reused, not freshly reapproved.

Phase11 remains active. This delivery does not imply all formal phase exits, school approval, source activation,
public deployment or Phase12 permission. Final independent review/full-suite result is recorded below when available.
