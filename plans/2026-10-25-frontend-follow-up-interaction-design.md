# General chat and follow-up interaction design

25 October 2026. Requested Top-Design proposal, grounded in the existing student UI,
thesis and API contracts. Design and external prototype only; no application changes.
Phase 11 remains active. No backend, source activation, dependency or scope change.
Subsequent owner authorization: "Lets go". See the
[implementation and verification](2026-10-25-chat-workspace-implementation.md);
the prototype-only statements below describe the original design pass.

## Design direction

Build a calm chat workspace with visible, student-controlled context. Keep the
conversation central; expose sources and supplied details when requested. Make a
failed follow-up recoverable without pretending that the frontend can decide policy.

- Brand essence: clarity.
- Visual tension: a quiet reading surface with precise evidence and status controls.
- Signature interaction: revise an ambiguous question, explicitly select earlier
  details, then inspect the exact outgoing message before confirming.
- Technical ambition: preserve keyboard focus, mobile reading space, streaming and
  temporary-session boundaries using existing components and platform features.

Reuse the current Inter typography, navy primary, neutral surfaces and appearance
controls. Hierarchy comes from readable measure, spacing and restrained status color.
Use brief opacity/transform transitions only when they explain a state change; honor
reduced motion. Preserve native scrolling and existing follow-to-bottom behavior.
No animation library, new fonts, marketing hero, custom cursor or new UI framework.

## Reference patterns, checked against official documentation

| Product | Useful pattern | Bintanong adaptation |
| --- | --- | --- |
| ChatGPT | Inspectable citations and a Sources view | One Sources control per answer opens the existing inspector; retain separate source identities |
| Claude | Conversational answers with directly inspectable citations | Keep answer text readable and evidence accessible beside it |
| Gemini | Explicit prompt editing and a source side panel | Edit into the composer; review before a fresh send; keep source inspection out of the main reading column |

Sources: [ChatGPT search](https://help.openai.com/en/articles/9237897-searching-the-web-with-chatgpt),
[Claude web search](https://support.claude.com/en/articles/10684626-enable-and-use-web-search),
[Gemini prompt editing](https://support.google.com/gemini/answer/13275745?co=GENIE.Platform%3DDesktop&hl=en),
[Gemini sources](https://support.google.com/gemini/answer/14143489?co=GENIE.Platform%3DDesktop&hl=en).
These references support interaction patterns, not a claim that Bintanong has their
tools, history persistence, web access or conversation-memory capabilities.

## Layout and visible states

Desktop: retain the existing sidebar and account controls, a compact curriculum
header, a centered readable thread and a persistent composer. Sources and supplied
details open in the existing drawer/dialog pattern. Mobile: collapse the sidebar,
keep curriculum accessible, use full-width dialogs and at least 44px button targets.
Do not force scrolling when the student is reading an earlier answer.

Owner reaffirmed25October: keep the supplied Figma's general look and feel while
retaining these refinements. Center all welcome copy, retain the neutral themes and
local campus fade, and keep active conversations free of the decorative photograph.

Show curriculum as scope, not proof of grades. Label earlier confirmed popup choices
"You supplied" and explicitly distinguish them from verified university records.
Keep ordinary text questions possible without a compulsory rephrasing wizard.
Only show a count as included in the next message when the student selected it.

Keep canonical answer text, conditional notices and status intact. When a response
requests clarification but supplies no supported questions, add this UI explanation:
"No specific clarification question was provided." Offer Edit/Rephrase and review of
earlier supplied details. Do not invent a missing grade, course or policy condition.
Supported canonical questions continue to use the existing opt-in clarification UI.

Keep the existing Stop control. Waiting feedback may show real elapsed time and
actual transport stages; no fabricated progress percentage, tool trace or early
unvalidated answer. UI work does not establish faster inference.

## General chat workspace: same design, not just follow-up recovery

Owner addition25October: include the general chat interface patterned after ChatGPT,
Claude and Gemini; follow the thesis, master plan, repo instructions and skills too.
General means the whole supported undergraduate conversation, not general-purpose AI.

The companion `chat.html` preview covers the full shell and links to `index.html`
for the more detailed follow-up recovery. Its Preview state controls are demonstration
controls only and must not appear in the shipped student interface.

| Surface | Proposed behavior |
| --- | --- |
| Start screen | Keep "Ask away, Bintanong."; explain the undergraduate scope briefly; three small starter actions prefill an editable question without sending |
| Sidebar | New chat, current temporary conversation and existing account/help controls; mobile opens a keyboard-accessible navigation dialog; no invented saved-history list |
| Header | Visible program/curriculum picker using real checked options; retain appearance and temporary-session information; no selectable model or RAG/Prolog mode |
| Conversation | User messages visually distinct; assistant answers use an open reading column with clear typography; keep actual answer text and status; long content wraps safely |
| Composer | Persistent multiline input; PDF attachment; explicit Send; Enter/Shift+Enter and IME behavior retained; disabled/Stop states follow the real request |
| Message actions | Edit as a new question and Copy; source access when sources exist; show recovery actions on the relevant result rather than crowding every answer |
| Evidence | Sources drawer with title/page/section/excerpt when returned and authorized; private PDF details remain separate from institutional citations |
| Working | Real queued/processing states and optional honest elapsed time; Stop remains available; never reveal an unvalidated policy draft |
| Errors | Preserve the question; distinguish request failure, interrupted response, unavailable service and expired session; offer recovery appropriate to the actual transport state |
| Unknown/withheld | Preserve canonical clarification, insufficient-information and error distinctions; show specific supported questions, source gaps or applicable referral only when supplied |
| Files | Show selected/uploaded/extracted/needs-review states from existing contracts; explicit confirm and remove; leave uncertain fields unknown; PDF only at current runtime |
| Clearing | Confirm destructive clearing; real app resets after server acknowledgement; on failure preserve visible state and offer retry rather than falsely claiming deletion |

The visual proposal combines a prompt-first start screen and clear navigation with a
quiet reading column, contextual answer actions and inspectable evidence. This is an
adaptation, not a pixel-exact reconstruction of the three products. Verified official
references additionally include [ChatGPT home/new chat](https://help.openai.com/en/articles/9125172-the-chatgpt-home-page)
and [Gemini chat/composer/mobile menu and prompt editing](https://support.google.com/gemini/answer/13275745?co=GENIE.Platform%3DDesktop&hl=en).
The earlier Claude citation reference supports inspectable grounding and an actual
search indicator; it does not authorize a web-search toggle in Bintanong.
Keep current account/auth and help actions; the prototype account/PDF/scope controls
explain their boundaries rather than impersonating a connected account or upload.

## Requirement-to-interface mapping

| Authority consulted | Consequence for this design |
| --- | --- |
| Thesis physical17–18, reread directly | Undergraduate academic affairs, advisory only; unavailable evidence cannot become a made-up answer or automatic web acquisition |
| Thesis physical54, reread directly | Clarification helps identify vague intent; no fabricated generic grade question to fill an empty API packet |
| Thesis physical65–66, reread directly | Isolated private context, no stored academic records, clear AI/adviser notice; no cross-chat personal profile |
| Master16.1–16.3, reread | Existing chat/upload/delete/source endpoints and tested transport; concise progress, final validated answers, conditional facts, keyboard/mobile support |
| Master23.1–23.3, reread | Visible thread and bounded server context are different; no automatic full-transcript replay; clear conversation and preserve session ownership |
| Runtime routing PNG, inspected | Router/retrieval/Prolog/integration/validation remain backend responsibilities; no frontend route guessing or raw-predicate controls |
| AGENTS.md scope/source/owner rules | Unknown differs from unmet; private files are not institutional knowledge; no dependency/model/source activation or unrelated edits |
| Current components/contracts | Reuse Workspace, EmptyConversation, ConversationStarters, Conversation, Composer, dialogs, reducer and source inspector; preserve cancellation and lifecycle behavior |
| Top-Design | Deliberate hierarchy, restrained color, spacing, focus and purposeful transitions; academic reading and accessibility constrain visual effects |
| Ponytail full and Good CSS | Reuse house components/tokens, native scrolling and small adaptive layouts; no new UI or animation dependency |
| Handoff reminder/phase handoff | Record exact proposal scope and verification; Phase11 stays active and proposal delivery does not clear its exit gates |

Researcher-only debug details, raw reasoning and architecture controls remain outside
the student flow. No voice, image generation, model selector, autonomous enrollment,
shared chats, ratings backend or persistent projects are added by imitation.
English UI copy follows the current owner preference; multilingual input support and
the existing language contract remain separate from this design-only work.

Implementation acceptance extends the focused follow-up tests with welcome-to-chat,
draft-only starters, safe text rendering, keyboard/IME send, source drawer focus,
conditional/unknown/error rendering, Stop/disconnect/expiry, upload review/delete,
failed clear preservation and narrow-screen/light-dark behavior. Use the existing
tests and real transport; do not reproduce demo state switches in application code.

## Exact recovery flow for the reported example

1. Preserve the failed "What choices do I have to pass it?" exchange in the thread.
2. Edit question copies it into the composer. Rephrase offers editable starting
   points: asking about retaking a named course, eligibility for a named course,
   or both. The student chooses/types the target; never infer CC4 from "it".
3. "Include earlier details" shows earlier explicitly confirmed choices for this
   curriculum. Nothing is selected for the new message by default.
4. The student selects CC4/L not passed and CC3/L passed. Keep unknown available;
   omission must not become a failed grade or a completed course.
5. Review displays the exact new question and selected declarative statements:

   ```text
   What do the reviewed institutional sources say about retaking CC 4/L?
   Can I take CC 5/L under my BSCS 2018–2019 curriculum?

   I have not passed CC 4/L.
   I have passed CC 3/L.
   ```

6. Explicit confirmation sends a fresh message through the current API with a new
   request ID. Append the revised exchange and retain the original. No automatic
   retry, hidden transcript attachment or retroactive server-context rollback.

The question templates assert neither that retaking is permitted nor that another
eligibility route exists. Institutional evidence and reviewed rules decide that.
If the backend still withholds or lacks sources, preserve that result honestly.

## State and authority boundaries

Retain only explicitly confirmed choices in page memory, scoped by curriculum,
printed course identity and fact kind. Reuse existing validation and formatting.
Do not extract facts from assistant prose or silently turn typed text into records.
Changing curriculum invalidates incompatible choices. Confirmed new chat, sign-out
and known session expiry clear them alongside current workspace cleanup.
No localStorage, saved academic profile, database write or cross-session memory.

The payload remains the current question plus explicitly reviewed statements and
curriculum scope. Respect existing length limits and preserve unknown-versus-unmet.
Never reintroduce question headings or "Your reply:" into declarative grade facts.
Editing an earlier turn means reusing its text as a new question; it cannot promise
ChatGPT-style conversation branching without server support.

Group source access visually, not semantically: preserve every unique source ID,
even if four references display the same title/page. Inspect through the checked
source endpoint. Never fabricate a title, excerpt or "verified" badge.

## Existing components to reuse

| Responsibility | Existing location |
| --- | --- |
| Page state, scope, send/clear lifecycle | `frontend/components/workspace/workspace.tsx` and existing workspace reducer |
| Message actions, status and source entry | `frontend/components/workspace/conversation.tsx` |
| Editable draft, inclusion indicator, Stop | `frontend/components/workspace/composer.tsx` |
| Supported clarification and exact review | `clarification-dialog.tsx`, `preview-dialog.tsx` in the same workspace directory |
| Source details | `frontend/components/workspace/source-panel.tsx` |
| Safe declarative formatting and limits | Existing `student-clarification.ts` helpers |
| Layout, focus, light/dark/system | `frontend/app/styles.css` and current appearance control |

Before implementation, locate every caller and existing test for these components.
Use focused RED -> GREEN regressions for explicit inclusion, exact payload/no replay,
unknown preservation, curriculum/new-chat/sign-out cleanup, empty clarification
recovery, and distinct source IDs with identical labels. Check keyboard focus,
Escape, narrow screens, streaming/Stop and a stale/expired session failure.

Frontend-only deliverables: composition, editing, explicit reuse of confirmed choices,
review, sources presentation and accessible recovery controls. Automatic server memory,
new canonical clarification fields, policy interpretation and prerequisite-list status
changes require separate API/backend work and are excluded from this proposal.

## Repo and thesis grounding

Read alongside the [integration plan](2026-10-24-student-ui-backend-integration-plan.md),
[follow-up diagnosis](2026-10-25-options-follow-up-diagnosis.md),
[prior phase notes review](2026-10-25-pre-phase11-follow-up-notes-review.md) and
[direct thesis review](2026-10-25-thesis-conversation-context-review.md).
Thesis physical pages17–18 delimit undergraduate advisory scope;9/40 motivate useful
failed-course recovery;54 supports meaningful clarification;65 supports isolated chat
without stored academic records. The routing PNG/master3/11/13 preserve structured
course facts, deterministic reviewed prerequisite rules and document RAG/Hybrid.
IDs-only conversation memory is an implementation choice, not a thesis requirement.
This proposal preserves the current bounded contract rather than changing it.
The owner's current English-only preference overrides older reply-language guidance.

## Prototype and verification

Interactive sample and evidence live outside Git under
`C:/Coding-projects/bintanong_workspace/audit-evidence/p11-20261025/follow-up-ui/`:
`index.html`, local reused `inter.woff2`, `check.mjs`, `checks.json`, and
`desktop.png`, `mobile.png`, `review.png`. It is visibly labelled sample text;
Confirm draft does not send. It is not substituted into the real student app.

Browser self-check PASS at1440x1040 and390x844: no horizontal overflow; explicit
choice inclusion and exact review; sample clear removes choices; Escape closes the
dialog; zero HTTP requests and page errors. Desktop, mobile and review screenshots
were visually inspected. Command: existing cached Node executable runs `check.mjs`.
No authenticated app acceptance, dark-mode, screen-reader or backend-answer claim.

General chat companion: `chat.html`, shared extracted `sample.css`, `check-chat.mjs`,
`chat-checks.json`, `chat-welcome.png`, `chat-conversation.png`, `chat-mobile.png`,
`chat-dark.png` in the same ignored evidence folder. General checks PASS at1440x1040
and390x844: draft-only starter, safe text rendering, Shift+Enter, Stop, edit/error
recovery, four distinct references, light/dark switch, clear, mobile menu/Escape,
no horizontal overflow, zero HTTP requests/page errors. Welcome/mobile/dark and
review screenshots inspected; fixed dark New-chat contrast during visual review.
The first general check failed before `chat.html` existed, then found a New-chat
accessible-name mismatch; the final run passes. This is prototype interaction proof,
not a claim that application behavior, privacy enforcement or answer quality passed.
The earlier dark-mode exclusion applies to the original follow-up sample; the general
sample now has visual coverage. Screen-reader/real-phone/authenticated acceptance
remain unverified. Both sample self-checks passed again after the final CSS change.

Provisional interaction/visual assessment:8/10 for this sample, not a measured user
study or a literal promotional-site hero score. To approach10: integrate the actual
components without regressions, validate dark mode and assistive technology, and
observe students successfully recovering the reported follow-up with real evidence.
