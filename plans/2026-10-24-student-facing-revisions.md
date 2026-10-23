# Student-facing revisions implementation and delivery

Requested 24 October 2026. [Figma section](https://www.figma.com/design/tYH9AcExjq0UyIXpKJVgGa/Bintanong-AI---Frontend-Design?node-id=127-93136)
`127:93136`, "Bintanong — Student-facing revisions · 23 Oct 2026".
Use layout direction rather than exact coordinates; preserve semantic icons,
System/Light/Dark, compact composer and short embedded-viewport scrolling.
This is an expanded frontend demo, not Phase 11 or HTTP integration.

## Context and scope

Read INDEX/current progress, Phase 10 handoff, master 16/23/24, thesis physical
17-18/66 and runtime routing evidence. Phase 10 has memory-only sessions with
30-minute idle expiry; HTTP/cookie/deletion acknowledgments are still Phase 11.
Checked `sessions.py`: session state contains facts, pending extraction and
conversation context, not a browser-accessible file store. Raw upload lifetime
cannot be promised from this UI; no automatic expiry timer was invented.
Photos are unsupported by the delivered parser. Demo selections remain metadata
only; no file contents, real extraction, policy results, transport or storage.
All 28 section frames have design context; screenshots and annotations inspected.
Read design coverage notes `127:91782`: partial design, no source-backed claims.
Raw design/code evidence stays ignored under workspace audit-evidence.

## Annotation decisions

| Node | Implement or boundary |
| --- | --- |
| 127:85005 | Campus fades from top to bottom; keep local source proportions. |
| 127:86156 | Status colors plus words/icons; unknown is not failed eligibility. |
| 127:86425 | Proposed shorter privacy copy: "Remove unnecessary data". |
| 127:86506,127:86757,127:86924,127:88212 | Separate working chat card; status beside task, not composer footer. |
| 127:87177 | Replace "temporary private context" with "Files in this chat". |
| 127:87430 | Clear per-detail review and quick metadata/detail inspection; actual file preview deferred because bytes are never read. |
| 127:87722 | Dismissible information notice; dismissal does not confirm details. |
| 127:87984 | Hide removed notes after decisions; only explicit confirmations count. |
| 127:88425 | Retain approved unavailable-information response. |
| 127:88638 | Conflict card grows with content; no fixed-height clipping. |
| 127:88859 | No redundant "Ask an academic question" button. |
| 127:89071 | Put question editing on the user's message; retry preserves question. |
| 127:89295 | Retain supported-format recovery with working reselection. |
| 127:89743 | Short failure copy and one removal action per file in each active view. |
| 127:89967 | Text-based details have a review card as well as file details. |
| 127:90235,127:90352 | Clear confirmation/pending/error in modal, not chat cards. |
| 127:90588 | Confirmed clear returns to empty New Chat. |
| 127:90816 | Rejected cleared-on-failure design replaced by preserving full chat. |
| 127:91064 | Expiry only an explicit synthetic example; no invented local TTL. Real backend idle expiry documented above. |

## Implementation steps

1. RED/GREEN interaction model: clarification, per-fact editing/confirmation,
   file invalidation, retry, expiry, clear acknowledgment and stale completions.
   Extend existing workspace reducer; keep synthetic examples in demo adapter.
2. Reuse existing UI primitives for answer/status/review cards. Add a native
   dialog for files/source inspection and clear confirmation, with Escape/focus
   return. New examples are explicitly chosen, never inferred from question text.
3. Refresh welcome copy/prompts. Keep unsupported account/settings inactive.
   Provide one Files in this chat entry point and distinct university-source view.
4. Verify TypeScript/build/tests on Node24.21; exercise both themes, keyboard/IME,
   short VS Code-sized views, long content, dialogs, recovery, reset/races and no
   student API calls. Update this delivery and current progress; commit verified
   pieces with Conventional Commits and explicit staging.

## Delivered surfaces

Implementation request authorizes the frontend slice; rejected annotations override
the corresponding static layouts. It does not establish source/institutional approval.

| Figma nodes | Interactive local implementation |
| --- | --- |
| 127:84854 | Welcome, natural-question suggestions, scope/language guidance. |
| 127:85071,127:85307,127:85528 | Clarify, explicitly submit a separate reply, cancel/Escape and resume. |
| 127:85740,127:85991 | Source inspection with unavailable evidence; advisory unknown state. |
| 127:86253,127:86506,127:86759,127:87012 | Selected files, simulated checking/reading cards, cancel and ready-to-review. |
| 127:87265,127:87555,127:87819 | Explicit per-detail confirm/edit/cancel/remove; confirmed input is not a policy decision. |
| 127:88047 | Separate working chat card with words and status color. |
| 127:88260,127:88473,127:88694 | Unavailable, conflict and excluded-scope responses; redundant CTA omitted. |
| 127:88906,127:89130,127:89354,127:89578 | Retry without duplicate question, user-side editing, file replacement/removal. |
| 127:89802 | Files/details panel, metadata inspection, typed-detail review. |
| 127:90070,127:90352,127:90588 | Modal confirmation/progress; confirmed local clear returns to New Chat. |
| 127:90816 | Rejected cleared-on-failure layout replaced by unchanged conversation/files/details. |
| 127:91064 | Explicit expiry example removes all active details/files while retaining the question. |

Select **Preview example** on `/` to inspect each family. Normal Send still uses
a fixed fictional answer; no question text chooses a policy or scenario. All
file-stage and clear results come from the synthetic adapter. A failed-clear
example deliberately keeps failing until the user cancels or starts New Chat.

## Verification and recovery

- Model/fixtures/tests: `9161699`. RED10 initial cases, RED2 concurrency cases,
  RED1 clear-freeze case; GREEN27 tests (`npm run test:ui`).
- Annotated UI/controller and final clear-freeze regression: `4510102`.
- `npm run typecheck` and `npm run build` pass with Node24.21.0/npm11.19.0 via
  `npm exec --yes --package=node@24.21.0 --package=npm@11.19.0 -- npm run <script>`.
  The system shell remains Node22.22.3; framework/dependency/lock pins unchanged.
- `student-revisions-browser.mjs`: 114 development and production checks pass.
  Both themes/all16 examples, explicit decisions, recovery, file invalidation,
  modal cancel/failure/success, IME, focus return and no student API calls/byte reads.
- `short-check.mjs`: 165 checks pass at six viewports, including short VS Code-sized
  and 125%/200%-equivalent cases. A collapsed reading area failed RED; a 12rem
  minimum preserves reading space while the main panel scrolls within its theme.
- `student-revisions-extras.mjs`: 28 checks pass: native dialogs block background
  focus and restore focus, live/persisted themes, local campus image/fade, compact
  bar, IME, local storage limited to appearance, health route/refresh (mocked probe),
  coarse-pointer 44px targets and 16px mobile input. A width regression failed RED
  before both touch-target dimensions were corrected. Native Edge can Tab into
  browser chrome; it does not focus the inert background. No custom trap needed.
- Native-dialog development replay initially closed panels immediately (RED);
  guarding obsolete close events fixes this in development and production.
- Status text/badges in both themes measure >=4.5:1. Color accompanies words/icons.
  Inspected light/dark review, file/source panels and failed-clear screenshots.
- Existing campus PNG retained, SHA256 `2781d222b8ef714a316f67cb02ebc1383f83d161d79590e1152d1955d8f7428a`;
  local file loaded with cover/fade. Semantic Lucide icons replace unrelated mockup
  icons under the owner's earlier direction. No new image or dependency required.
- Evidence/scripts remain ignored in `C:/Coding-projects/bintanong_workspace/audit-evidence/frontend-ux-20261024/`.
- Documentation hygiene: 10 tests pass with system Python3.13, no pytest cache and
  basetemp in that evidence folder. Phase ledger validates; no active numbered phase.

## Limits and next action

Owner reviews the expanded local preview. No real file parsing, source excerpts,
server deletion, automatic expiry, authentication, persistent history, deployment
or backend work. Actual file-content quick preview remains deferred. Full mobile
flows, physical keyboard/screen-reader devices, actual VS Code automation and
cross-browser verification remain unverified. Refactoring UI diagnostic stays9/10:
formal blurred/grayscale comparison remains unchecked. Existing Next lockfile/
standalone warnings and pinned-framework advisories remain. Unrelated edits and
the untracked model directory are preserved. No push or formal phase advancement.
