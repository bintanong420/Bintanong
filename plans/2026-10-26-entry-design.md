# Header cohesion and public entry design

Owner26October2026 requested a cohesive chat header and an improved landing page,
using Antislop UI/Top Design and useful patterns from Gemini, Claude and ChatGPT.
Base49238e0; existing owner progress appendix and untracked files stay excluded.
Phase11 remains active. This is frontend work in the existing owner checkout.

## Design and scope

Design read: a welcoming PalSU undergraduate guide with restrained editorial
typography and campus photography. ENERGY2/RHYTHM2/MOTION1 on the public page;
ENERGY1/RHYTHM1/MOTION1 in chat. Existing Figma direction supplies the wordmark,
neutral themes, campus identity and conversational interface. Keep refinements.

- Header: continuous background instead of a photo starting at a hard horizontal
  edge; one compact row with curriculum, options and accessible sign-out. Keep
  contextual confirmed-detail controls. Research status remains visible in the
  navigation and explained in options. No changes to authorization or clearing.
- Landing: bring the greeting and primary Ask a question action into the first
  viewport. Pair the existing campus photo with bold, left-aligned typography on
  wide screens; stack the text before the photo on narrow screens. Short examples
  explain supported tasks without fake responses or an unauthenticated composer.
- Retain public scope/privacy destinations, source limitations, research status,
  PSU sign-in, English/Filipino/Taglish, AI-guide notice and both appearance modes.
  Preserve existing fonts/primitives and all auth routes. No new dependencies.
- Reasons: typography carries the invitation; campus grounds the product in PalSU;
  whitespace separates invitation from limits; a single strong action makes entry
  clear; small hover feedback supports interaction without delaying content.

## Reference observations,26October

Official public pages were read; these are design references, not copied features.
[ChatGPT](https://chatgpt.com/) prioritizes a short question and immediate entry.
[Claude](https://claude.com/) pairs a concise headline with a direct sign-in path.
[Gemini](https://gemini.google/) supplies a distinct product identity and direct
entry. Gemini's app returned only sign-in in text; its authenticated design was
not inspected. Claude.ai's cached older page is superseded by the live Claude.com
reference. No claims about their private account views or Bintanong parity.

## Implementation and checks

1. Add focused browser regressions and observe meaningful RED for header continuity
   and landing hierarchy. Reuse the loopback synthetic fixture; no owner cookies.
2. Edit app/page.tsx, workspace/workspace.tsx, workspace/sidebar.tsx and shared
   app/styles.css. Preserve callers, accessible names and existing auth tests.
3. Verify unit/browser checks, both themes,320/390/768/1440px,200% text, keyboard,
   real destinations, image loading, measured contrast and production build/types.
   Inspect screenshots, then rebuild local3215 and record actual results here.

## Delivery and verification

Code99ac14a. No new API, authentication, model, source, dependency or lock changes.
Existing Geist/Inter preserve Bintanong's established typography; the stronger size
contrast belongs to the public invitation. Sidebar/research disclosure, options,
sign-out and confirmed-detail access remain usable; mobile uses labeled icon buttons.
The curriculum control can shrink when retained-detail actions are present.

- RED: campus top68 != main top0; mobile photo preceded the invitation. GREEN2.
- Additional RED:320px curriculum/retained-detail overlap from the shared button's
  shrink-0. Narrow flex-shrink correction -> GREEN, with a retained-detail regression.
- Additional RED: photograph caption worst-area contrast4.46:1 at320px. Strengthened
  its scrim -> GREEN. Tracked browser check hides text, reads screenshot pixels with
  the already-installed Sharp0.35.5, and checks the entire caption background area
  against the actual text color at320/1440 in both themes. No new dependency.
- `node --experimental-strip-types --test tests/*.test.mjs`:61 PASS,5.70s.
- `node --test --test-concurrency=1 tests/browser/*.mjs`:17 PASS,142.25s. This full
  run precedes only the final caption scrim correction and its pixel regression.
- Final `node --test frontend/tests/browser/chat-workspace.mjs
  frontend/tests/browser/entry-design.mjs`:3 PASS,38.21s, after that correction.
  Covers both themes,320/390/768/1440,200% text reflow, keyboard skip/focus, real
  protected entry, appearance changes, retained details, sources and auth cleanup.
- `node node_modules/next/dist/bin/next build`:PASS, including TypeScript/static
  generation. Separate `node node_modules/typescript/bin/tsc --noEmit`:PASS.
  Existing workspace-lockfile discovery warnings remain; no config/lock changes.
- Phase-state validation and10 documentation hygiene tests PASS (4.65s).
- Inspected desktop/mobile screenshots, including the dark header. Public landing
  on rebuilt standalone3215 renders1440/light and390/dark with zero page errors.
  Site/frontend health/backend readiness and served header bundle HTTP200.

All node commands use the existing cached24.21.0 executable. Synthetic browser
fixture18093 and isolated Next3220 reused; test credentials only. Both stopped after
checks. Only owner frontend3215 restarted, with public/static assets copied to its
ignored standalone output. API8021/model18088/encoder8001 were not restarted.
Evidence: `C:/Coding-projects/bintanong_workspace/audit-evidence/p11-20261026/entry-design/`;
browser-results-final.txt, final-contrast-and-header.txt, build-results.txt,
production-readiness.json, header-*, landing-* and production-* screenshots.

Scoped design gate: R03/R34/R35 PASS (viewport/theme/zoom tests and rendered build);
R25 PASS (copy/CTA contrast and caption pixel test); R26/R32 PASS (real entry,
keyboard/appearance/drawer controls); R17/R18/R23/R38 PASS (existing campus asset,
plain example questions, no invented statistics/people/academic answers);
R01/R31 PASS (caption scrim serves contrast; photo establishes PalSU identity).
Provisional visual judgment:6/10 before,8/10 after. A10/10 claim needs student
usability feedback, assistive-technology checks and measured loading performance.
No claim of completed accessibility certification or university acceptance.

Owner progress appendix and three pre-existing untracked paths remain preserved.
No deployment, push, phase closure or source activation. Owner signed-in acceptance,
real phones, screen readers and backend interpretation/source gaps remain open.
