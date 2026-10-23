# Student-facing revisions implementation and delivery

Requested 24 October 2026. Figma file `tYH9AcExjq0UyIXpKJVgGa`, section
`127:93136`, "Bintanong — Student-facing revisions · 23 Oct 2026".
Use layout direction rather than exact coordinates; preserve semantic icons,
System/Light/Dark, compact composer and short embedded-viewport scrolling.
This is an expanded frontend demo, not Phase 11 or HTTP integration.

## Context and scope

Read INDEX/current progress, Phase 10 handoff, master 16/23/24, thesis physical
17-18/66 and runtime routing evidence. Phase 10 has memory-only sessions with
30-minute idle expiry; HTTP/cookie/deletion acknowledgments are still Phase 11.
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

## Current state

Design/annotation inspection complete. Implementation and verification pending.
Unrelated progress edits and the untracked model directory must remain untouched.
