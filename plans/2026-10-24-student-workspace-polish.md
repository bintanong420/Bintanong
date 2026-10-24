# Student workspace UI/UX polish

Owner24Oct: PalSU email login works; requested overall frontend polish aligned
with the existing backend. Authentication success is owner-verified, not an
automated claim of a full authenticated acceptance run.

## Scope and direction

Continue the selected Figma/approved original workspace direction and antislop
during implementation: ENERGY1/RHYTHM2/MOTION1, existing campus photo, neutral
theme tokens and shared controls. Conversation is the focal point; status colors
explain actual backend states. Retain the landing/auth concepts already delivered.
No backend academic decision, retrieval, routing or generation changes.

Origin refreshed: backend remains4a134bf; no newer backend commits missing.
Read actual API stream/presentation/upload contracts and frontend transport,
reducer, controller, composer, conversation, source/file/dialog/sidebar callers.
API metadata supplies status/language/missing fields/conditional flag/sources;
frontend must display these without inventing eligibility or successful answers.

## Verified first slice

- Distinguish clarification, incomplete information, source conflict, excluded
  scope, temporary unavailability and abstention using the backend status and
  reply language. Answered/greeting do not receive a fabricated success label.
- Curriculum picker shows loading, unavailable/empty states and an explicit retry;
  failed choices cannot be saved. General policy questions remain available.
- Show the selected program/curriculum, label source actions and PDF empty state,
  explain actual15MiB/20-page limits and selected-versus-left-out review rows.
- Place Stop where Send normally appears while a response is pending; preserve
  draft editing, cancellation, uncertain-request handling and acknowledged clear.
- Improve control sizes, dialog close visibility, mobile transcript scrolling,
  safe-area spacing and keyboard hints. Remove unused Settings placeholder.

## Evidence

- Existing public student-workspace seam: new notice tests RED missing export,
  then GREEN8 focused and48 complete frontend tests. No new testing dependency.
- Actual browser curriculum failure RED missing retry action; GREEN recovery
  enables explicit curriculum selection. Retry only reloads GET/curricula.
- next typegen, TypeScript and final production build PASS.
- Actual Next/FastAPI browser regression:10 families/16 requests PASS, including
  PDF parser/review/remove, sources, clarification, failed clear, Stop and sign-out.
-29 additional checks PASS: empty/conversation themes at320–1440px,200% text,
 44px mobile buttons, long-transcript composer access, dialog focus, expired auth.
- Rendered text measured minimum6.58:1 across light/dark and source-conflict states.
- Moving Stop into the composer exposed a real browser default-action race: React
  changed the clicked button back to Submit before its default action finished,
  sending the next draft. Tracked browser regression observed RED then GREEN after
  preventing that click's default action; draft retained and only one POST/chat.
  Run `node --test tests/browser/composer-stop.mjs` with BINTANONG_BROWSER_URL,
  BINTANONG_BROWSER_STATE and PLAYWRIGHT_MODULE pointing at the isolated fixture,
  its ignored synthetic storage-state JSON and existing Playwright installation.
- Isolated synthetic Next3218/FastAPI18092 exercises actual transport/parser;
  production preview3215/API8021 and the owner's working session remain separate.
  External scripts/screenshots/results live under ignored workspace
  audit-evidence/p11-20261024/workspace-polish.
- Initial fixture venv lacked ReportLab; existing system Python3.13 used instead.
  Turbopack rejected the external node_modules junction; isolated preview uses
  installed Next's webpack mode. No packages/locks/config in the repo changed.

## Owner steering: chatbot structure and interaction

Owner found the interface too static and requested references from ChatGPT web,
Claude web and Gemini web. This expands the visual/interaction pass beyond the
first slice's state clarity. Design dials now ENERGY1/RHYTHM2/MOTION2: useful,
short transitions tied to user actions and actual request state, with reduced
motion support; no simulated text generation or fabricated progress.

Read-only live inspection: ChatGPT signed-out web shows a centered starter/composer
and an expandable sidebar; Gemini signed-out web shows a quiet menu and prominent
composer. Screenshots saved in the ignored evidence directory. Claude requires
login here; its authenticated chat was not inspected. Official current guidance
documents its composer options and sidebar behavior instead.

| Reference | Evidence | Application to Bintanong |
| --- | --- | --- |
| ChatGPT | [Web experience/release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes), live signed-out page | Center the initial question box; keep conversation and input dominant. |
| Claude | [Chat interface](https://support.claude.com/en/articles/8114491-get-started-with-claude), [sidebar and appearance](https://support.claude.com/en/articles/8887527-customizing-your-appearance-settings) | Collapsible navigation, discoverable secondary options, quiet controls. |
| Gemini | [Composer/file entry](https://support.google.com/gemini/answer/14903178?hl=en&co=GENIE.Platform%3DDesktop), live signed-out page | Group supported context/file controls with the composer; spacious conversation. |

These are design inferences from the observed interfaces and official guidance,
not copied capabilities. No model picker, voice, saved history or unsupported tools.
Second slice delivered: centered starter/composer, compact header, collapsible
desktop navigation, native mobile drawer, context controls near input, native
options popover, request indicator and short panel/answer transitions. Reduced
motion disables movement; pending animation only exists during an actual request.
The plain starter/sidebar still uses approved PalSU imagery and actual scope.

Second-slice verification:48 UI tests, TypeScript and production build PASS;
10 browser families/16 requests and29 layout/interaction checks PASS on revised UI.
Two tracked browser regressions PASS: Stop/draft protection and desktop/mobile
navigation, focus return, unsent example selection, context controls not submitting,
and reduced motion. Starter grouping test observed RED before the layout change.
Measured rendered text minimum6.58:1 light/7.73:1 dark on empty and source-conflict
states; new screenshots reviewed after animations settled.

## Guided live clarification delivery

Owner supplied a real screenshot and requested the previously specified Claude
Code/Codex-style clarification prompt. The existing live response only exposes
missing field categories; the prototype form is not connected. Inspect thesis
physical18/20 and the13Oct frontend specification, then connect selectable,
system-supported options, alternative explanation and explicit confirmation.
Do not infer course options from prose or turn unknown into failed/ineligible.

### Recovered implementation plan

Recovered exact Codex session01a16c88-a2f7-7e63-b82a-f32c00d47160 from its account-local
24Oct transcript; last turn hit the usage limit before implementation. Git1c0ab97
contains both earlier UI slices. Existing owner progress/review/model files stay intact.
The13Oct specification already selects the interaction; no new design approval needed.

- [x] Extend only the public answer projection/stream with printed course codes and
  completion/enrollment question kinds from canonical unknown facts and reviewed labels.
  Keep canonical answers, router, Prolog and generation validation unchanged.
- [x] Extend the existing strict frontend metadata contract and reducer; connect a
  one-question-at-a-time dialog using native focus/Escape handling, supported curriculum
  choices, explicit unknown/alternative explanation and a final review/send action.
  Dismissal preserves the prompt/draft. Send a self-contained clarification through
  the existing chat validation path; never mark UI choices as trusted facts.
- [x] Observe focused Python/transport/reducer/browser RED then GREEN; run relevant
  API/frontend suites, TypeScript/build and browser accessibility/mobile regressions.
  Record bounded evidence and commit verified increments with explicit paths.

Scope: API presentation/stream and its caller, frontend metadata/transport/reducer,
workspace/conversation/new clarification dialog, shared styles and synthetic tests.
Risks: stale prompts, accidental/default submission, lost composer drafts, scope
drift, unknown becoming failed and contradictory explanations being dropped.
Reuse PreviewDialog/shared controls/theme; ENERGY1/RHYTHM2/MOTION2 retained. Flat
radio rows make the next action clear; the existing accent marks selection only.
Context rechecked: thesis physical17–18,20,65–66 and routing PNG; master16/23,
Phase10 handoff. The thesis requires clarification; the13Oct owner specification
supplies the Codex/Claude-style interaction, without changing authority boundaries.

### Verification and recovery

Commits:4dcd9bf API projection/strict transport;68b70e1 connected dialog/reducer/UI.
Projection/transport/reducer regressions observed RED (missing metadata and lost
composer draft) then GREEN. Browser RED: no dialog; GREEN: explicit confirmation,
dismiss/resume, unknown and explanation, single POST and retained composer draft.
Reviewer found that unrelated busy operations unmounted a dismissed prompt and
lost its draft. Browser RED reproduced loss after failed clear; keeping the dialog
mounted gives GREEN. Reviewer rechecked the correction; no remaining blocking finding.
At320px/200% text, inherited sticky header covered Continue; static clarification
header and wrapping action buttons fixed it. Both normal/review states now reflow.

- `node --experimental-strip-types --test tests/*.test.mjs`:55 PASS. Pinned Node
  24.21 executable; frontend cwd. Final production build/TypeScript PASS.
- `py -3.13 -X utf8 -B -m pytest -q -p no:cacheprovider` with files selected by
  `rg --files tests -g 'test_api*.py' -g 'test_private_context*.py' -g 'test_generation*.py'`:
  667 PASS,2 expected unsupported-photo xfails in33.59s; external pytest-regression basetemp.
- `node --test --test-concurrency=1 tests/browser/guided-clarification.mjs
  tests/browser/composer-stop.mjs tests/browser/workspace-navigation.mjs`:4 PASS.
  Set BINTANONG_BROWSER_URL=http://localhost:3218, BINTANONG_BROWSER_STATE to the
  ignored synthetic-browser-state.json and PLAYWRIGHT_MODULE to the existing npm
  cache e41f203b7505f1fb/node_modules/playwright/index.mjs. BINTANONG_BROWSER_EVIDENCE
  names the ignored evidence directory for optional screenshots. Run sequentially:
  the single synthetic account correctly refuses overlapping browser requests.
- Actual synthetic Next/FastAPI integration:10 families/16 requests PASS, including
  PDF parser/review/remove, sources, failed clear, Stop and sign-out. Updated only
  the obsolete clarification-action expectation in the new evidence script copy.
- Eight dialog checks:320/390/768/1440px,light/dark, keyboard radio navigation and
  no overflow. Actual rendered text minimum5.88:1 light/6.52:1 dark; choice borders
  minimum6.58:1/7.73:1. Screenshots inspected;320px/200% review and focus-return tested.
- Existing native dialog traps focus/handles Escape; no initial option, implicit
  choice submission or new testing/UI dependency. EN/Filipino/Taglish host-copy
  tests are separate from actual-model language/decision acceptance.

Ignored evidence: workspace audit-evidence/p11-20261024/guided-clarification
(fixture, synthetic state/PDF, check-workspace.mjs/results, inspect-clarification.mjs,
clarification-accessibility.json/screenshots, startup logs). No private artifacts staged.
Next/login3215 restored200 with existing local config. Actual API8021 restart
failed in load_release_curricula -> compiler._rebuild -> authoring._facts:
`facts require course_code and only supported field names`. The same runtime JSON
was used in the recovered session; exact current hosted-field incompatibility is
undiagnosed. No hosted data, source decisions or validation guard changed. No live
model clarification round-trip is claimed. Prototype/browser checks use the isolated
synthetic services; the real chat remains unavailable until API startup is repaired.

### UI delivery gate (scoped)

| Gate | Result and evidence |
| --- | --- |
| Hard gate | PASS: no new assets, marketing claims, external navigation or dummy controls; all added controls exercised; mobile/review/200% reflow and contrast measured. |
| Purpose | PASS: shared tokens/controls retained; flat choices identify the next answer; selection accent conveys state; native modal provides task focus. |
| Liveliness | PASS: existing ENERGY1/RHYTHM2/MOTION2 retained; one question is the focal point; existing request/panel feedback and reduced-motion behavior reused. |
| Craft/accessibility | PASS: keyboard radio navigation, Escape/focus return, no defaults, explicit review/send, loading/unavailable/unknown paths and draft-preserving failed clear verified. |

This is UI/software verification, not actual-model accuracy, complete accessibility
certification, Phase11 closure or institutional-release readiness.

## Remaining boundaries

Non-PSU human rejection/full manual flow not claimed. Phase11 lifecycle WIP,
Docling environment failures and inherited model/source-quality exits stay open.
No phase closure, public deployment, database/schema changes or new dependencies.
