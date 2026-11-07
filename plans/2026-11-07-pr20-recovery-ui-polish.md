# Recovery answer UI polish

Owner requested removing the raw four-hash DraftD heading, formal term labels and repeated
source/conditional/disclaimer chrome. Explicitly applied antislop-ui and refactoring-ui.
Worktree p12-pr20 / PR20 feature branch; staging3218/API8023 only.

## Implemented

- Display heading: `Plan D: Special classes and summer as needed`, rendered as a supported
  Markdown heading. No raw hashes, repeated preferred label or just-in-time implementation term.
- Display terms: `2nd year, 2nd sem`, `3rd year, 1st sem`, `Summer after 2nd year`.
  Applies to overview, assumptions, affected-course groups and all draft rows/alternatives.
  Legacy full text and original quoted source clauses remain unchanged.
- Single answered presentation omits its redundant title/status row and part-level source
  button. One message footer contains source/copy actions and a single quieter basis/disclaimer.
  Multi-part answers retain part-specific sources; footer offers only uncategorized sources.
  Interrupted/text-fallback answers keep source access and their qualification.
- Narrow-screen V2 tables stack labelled Term/Courses/Notes cells. All course and warning
  text remains present. Native table roles/column headers and safe React text rendering remain.
- Text width constrained to65ch; footer uses12px existing muted color without extra opacity.
  No new palette, icons, decorative cards, dependencies, model prompts or institutional rules.

## Online references consulted7November2026

- [ChatGPT search](https://help.openai.com/en/articles/9237897-searching-the-web-with-chatgpt)
  documents opening citations and a Sources control. Supports a clear source-inspection path;
  it does not prescribe Bintanong's exact footer or imply all citations should be bundled.
- [Claude citations](https://platform.claude.com/docs/en/build-with-claude/citations)
  binds supporting locations to individual response text blocks. Retain per-part evidence
  membership rather than making an unrelated source authorize another answer part.
- [Perplexity Pro Search](https://www.perplexity.ai/help-center/en/articles/10352903-what-is-pro-search)
  emphasizes direct links for checking original sources; keep inspection available.
- [Microsoft Fluent responsible AI](https://fluent2.microsoft.design/responsible-AI)
  emphasizes transparency, expectations and limitations. Keep material uncertainty alongside
  the plan; a quiet disclaimer must not substitute for actual load/prerequisite warnings.

Short result first, readable headings, progressive detail and one footer are our design
choices informed by these references, not claimed universal platform requirements. No external
model/service migration or provider citation API was introduced.

## Verification

- RED reproduced duplicate source actions, unsupported heading/long labels and absent mobile
  cell labels; corrected in shared presentation/rendering layers. Backend15 presentation
  tests pass. Frontend109 tests pass; TypeScript and production Webpack build pass.
- Existing cached Playwright and installed Edge reused: four isolated component replays at
 1440px/390px, light/dark. Real Conversation/AnswerPresentation/MarkdownText plus production CSS,
  a previously checked source-pinned recovery answer, no new inference. One Sources(13),
  heading present, keyboard Enter opens/closes native details, table labels visible on mobile,
  no page/card overflow. No package/browser install or download.
- Screenshots inspected; initial compressed term columns were unreadable despite passing
  overflow checks, which prompted stacked mobile rows. The test is an isolated rendered
  component replay, not a newly authenticated full-chat or source-picker end-to-end test.
- Disclaimer contrast, measured from browser-rendered CSS colors:6.58:1 light,7.66:1 dark.
  This is that text pair's result, not a blanket WCAG or screen-reader certification.
- Refactoring UI component review:7/8 diagnostic rows satisfied, provisional9/10. Hierarchy,
  grayscale, grouping space, secondary labels, constrained width, measured contrast and flat
  elevation hold. Existing mixed spacing values outside the strict4/8/16/24 scale remain;
  no unrelated global redesign was included.

Ignored evidence: `audit-evidence/pr20-local-staging-20261107/ui-recovery-view.json`,
`review-recovery-ui.mjs`, `ui-browser-review.json`, `recovery-ui-{width}-{theme}.png`.
Next: load verified UI on staging and owner review. Full app/source-picker/screen-reader and
independent benchmark acceptance remain separate. No merge or institutional activation.
