# General chat and explicit follow-up controls

25 October 2026. Owner authorized implementation with "Lets go" after the
[accepted design](2026-10-25-frontend-follow-up-interaction-design.md).
Base067eba2 on local frontend. Phase11 stays active; this is frontend delivery,
not institutional release or a claim that backend interpretation is repaired.

## Delivered

- Undergraduate welcome, editable starters, readable thread and persistent composer.
  Current curriculum is available in the header; mobile navigation, account controls,
  appearance, PDF review and Stop reuse existing components.
- Edit as new question preserves the prior exchange. Rephrase requires the student
  to name the course and choose retake/eligibility/both; no inference from "it".
- Explicitly confirmed canonical course choices can be reviewed under "You supplied".
  Page memory holds at most32 recent choices, keyed by program/curriculum/condition.
  New choices replace the same condition; unknown and explanations stay verbatim.
  Typed chat and assistant prose are not mined for facts.
- Including earlier details starts unchecked for each new message. A nonempty
  selection requires exact outgoing-text review and explicit confirmation. The
  current API receives one new message, fresh ID and current scope; no transcript
  replay, automatic retry, server-memory change or historical-turn rewrite.
- Curriculum change, confirmed clear, successful sign-out and known401 clear retained
  choices. Failed clear preserves the conversation and choices. Sign-in expiry
  blocks a nonempty draft; source inspection now forwards401 to the same cleanup.
- One Sources control opens the existing checked inspector through a reference list.
  Distinct source IDs remain separate despite identical displayed titles/pages.
- Canonical text, status and conditional notices remain. Bare clarification adds
  an honest explanation and Rephrase instead of inventing a missing fact. UI controls
  use English per owner preference; backend answer text/language is unchanged.

## Context and boundaries

Reused the design's explicit mapping to thesis physical17–18/54/65–66, master16/23,
runtime routing PNG, repo rules and current contracts. Re-read the relevant thesis
pages, master16.2/16.3 and Phase10 handoff during delivery. Top-Design supplies
hierarchy/restraint; Good CSS and existing tokens/components supply the implementation;
repo TDD and handoff workflows supply verification/recovery. No new dependencies.

Structured facts/Prolog, document RAG/Hybrid, authorization, institutional applicability
and answer validation remain backend responsibilities. No backend/prompt/API-schema,
Supabase, source/rule, manifest/lockfile or model changes. Private PDF facts remain
separate from institutional references. No saved transcripts or academic profile.
The original options-follow-up interpretation/source-coverage gap remains open.

## Verification actually performed

Node24.21.0 executable reused from the existing cache; no installation/download.
Commands below run from frontend with that executable in place of `node`.

- `node --experimental-strip-types --test tests/*.test.mjs`:61 PASS,8.95s final run.
- `node node_modules/typescript/bin/tsc --noEmit`:PASS.
- `node --test --test-concurrency=1 tests/browser/*.mjs`:14 PASS in96.23s.
  After final label/assertion changes:13 PASS, one transient `page.goto ERR_ABORTED`
  in sign-out navigation; focused rerun of that exact case PASS in3.70s. Do not
  describe the final broad run as a clean14/14 run without this qualification.
- Focused RED/GREEN: missing explicit-detail behavior -> implemented helpers;
  reducer did not retain choices -> scoped bounded retention; general browser lacked
  new controls -> full new flow PASS. Source401 retained choices (1 !=0) -> cleanup
  regression PASS, including nonempty-draft send blocking and sign-in link.
- Browser coverage includes exact new-message text, explicit choices, unknowns,
  fresh IDs/no replay, same-title distinct references, failed-clear preservation,
  known-auth cleanup, cancellation, guided clarification, sign-out and navigation.
- Synthetic local rendered views1440/light,390/dark,320/light: no horizontal
  overflow or page errors; welcome/thread screenshots inspected. Existing browser
  checks also cover320/390/768/1440, both themes and enlarged text/dialog focus.
- Independent review identified the source401 cleanup gap; narrow fix reviewed
  afterward with no additional concrete blocker. No broader security claim.
- `node node_modules/next/dist/bin/next build`:PASS, including TypeScript/static
  generation. Initial attempt hit Windows EBUSY on the running standalone output;
  stopping only that frontend process cleared the lock. Existing root-lockfile
  discovery warnings remain; no unrelated config/lock change.

Synthetic browser configuration: loopback Next3220, fixture18093, separate synthetic
identity/cookies; no owner cookies or Google account used. The isolated dev server
and fixture were stopped after checks. This is not authenticated owner acceptance.
Ignored evidence root:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p11-20261025/chat-implementation/`.
It contains launchers, synthetic state, visual checks/screenshots, readiness and idle
receipts. Earlier mock prototypes remain separate under `follow-up-ui/`.

## Local preview and recovery

Updated standalone frontend at http://127.0.0.1:3215, reusing existing env/launcher.
Only frontend terminal term_c27fc4d5-7f8b-44d0-89d6-4760153be9d9 was interrupted and
restarted. Existing API8021, model18088 and encoder8001 were not restarted/changed.
Public/static assets copied into the ignored standalone output after the build.
Site200; served JS contains the new Rephrase UI. Frontend/backend readiness200;
Supabase, Janus, embedding, Bintu and student_runtime probes all true.
Production login idle check is recorded separately; it does not prove signed-in chat
behavior:45seconds, zero additional navigation/HMR connections/page errors.
Provisional visual assessment:8/10; improving it requires student usability feedback
and assistive-technology checks on the actual application.
Owner-authenticated chat, actual model answers for the revised follow-up,
screen readers and real phones remain unverified. No remote push or phase closure.

User changes preserved: unstaged historical progress appendix, untracked model
directory and two historical review/sync notes. Explicit staging excludes them.

## Session recovery and Figma alignment

Resumed session01a16d9d-dec8-7d10-9369-00f693f97dd9: its final unanswered request
was to center the three welcome lines. Owner also reaffirmed Figma as the visual
direction while retaining the chat refinements. Code delivery8313279. Live Figma context/screenshots:
[workspace127:84854 and welcome127:85006](https://www.figma.com/design/tYH9AcExjq0UyIXpKJVgGa/Bintanong-AI---Frontend-Design?node-id=127-84854),
campus127:85005 and its top-to-bottom fade annotation. The existing local campus
asset is reused; no new product assets or dependencies. Figma remains direction,
not exact geometry; approved interactions and supported PDF-only claims remain.

Removed the live welcome's left-alignment override and warm canvas override;
restored the existing neutral theme and decorative campus fade on empty chat only.
The welcome shares the main column's center. Existing composer, scoped explicit
detail review, grouped sources, Edit/Rephrase and readable conversation remain.
Reasons: centered copy follows the owner/Figma; neutral colors retain the design;
campus establishes place and clears after sending to preserve answer readability.

Fresh RED: welcome text-align start != center. GREEN: six viewport/theme variants
at1440/390/320px; campus loads locally and disappears after sending; starter stays
an editable draft.61 unit checks and all15 browser tests PASS (87.97s), including
the earlier sign-out navigation case. Next production build and TypeScript PASS.
The first test setup hit an expired synthetic cookie; renewed only test credentials
before the meaningful RED. No owner session/cookies used. Screenshots inspected.
Evidence: resumed-browser-results.txt, resumed-build-results.txt, centered-welcome-*
and resumed-preview-readiness.json under the same ignored evidence root above.

Rebuilt/restarted only frontend3215 using the existing launcher/terminal. Site,
frontend health and backend readiness HTTP200; served bundle has the campus UI.
Re-read thesis physical17–18/54/65–66, master16 and Phase10 handoff; inspected routing
PNG. No scope/routing discrepancy. Backend interpretation, source activation,
owner-authenticated acceptance, real phones and screen readers remain unchanged/open.
Phase-state validation and10 documentation hygiene checks PASS. No push/phase closure.
