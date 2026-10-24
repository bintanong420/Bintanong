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
Next slice: centered starter/composer, compact header, collapsible desktop/mobile
navigation, context controls near input and state-driven interaction feedback.

## Remaining boundaries

Non-PSU human rejection/full manual flow not claimed. Phase11 lifecycle WIP,
Docling environment failures and inherited model/source-quality exits stay open.
No phase closure, public deployment, database/schema changes or new dependencies.
