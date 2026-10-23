# Frontend UX corrections

Owner direction,24October2026: Figma is a rough visual direction, not a1:1 target.
Correct misalignment/iconography, add automatic light/dark/system appearance, and
replace the oversized composer with a compact text-field bar. This supersedes
the earlier exact-frame geometry/icon-asset choices for this frontend slice.
Implementation commit: `2bfc3c2` on `frontend`; no push or deployment.
Context rechecked: thesis physical 17-18 and runtime routing PNG. Undergraduate
read-only scope/private-file separation match this demo; no routing discrepancy.

## Changes and boundaries

- One shared content width for toolbar,welcome,conversation and composer; remove
  asymmetric offsets. Smaller notice below the composer; preserve its meaning.
- Semantic icons from the existing Lucide dependency: SquarePen for New Chat,
  MessageSquare for example chats,Settings gear,FileText/FileImage for attachments,
  X for removal,and distinct user/assistant message symbols. No placeholder music
  or library icons for unrelated actions; icons inherit both theme palettes.
- Single-line composer with36px controls, multiline growth capped at160px;
  attachments flow above the draft while actions remain aligned to its bottom.
- Native appearance selector defaults to System. CSS color-scheme/light-dark
  follows OS changes live; explicit Light/Dark overrides and cross-tab updates.
  Only this visual preference is saved locally; no chats/files/grades persisted.
  Validated pre-paint bootstrap avoids a saved-preference theme flash. Storage
  denial falls back safely and does not disable the controls. Health stays scoped.
- Crop the campus image with object-fit:cover instead of stretching it. Keep
  the campus identity/fade,neutral visual direction and existing fonts.
- No dependencies/backend/APIs changed;unfinished product flows remain excluded.

## Verification

Baseline browser RED: empty composer 80px, input 78px, upload 80px; the at-most-60px
check failed. GREEN: empty bar 54px, input and both actions 36px; multiline grows
to 160px and shrinks after editing. Appearance RED: 3 tests failed before behavior;
GREEN: 3 appearance tests plus 9 existing interaction tests.
Focused-state RED: two outlines; GREEN: one visible composer boundary.

Verified with Node 24.21.0/npm 11.19.0 using `npm exec --yes
--package=node@24.21.0 --package=npm@11.19.0 -- npm run <script>` in `frontend`:
`test:ui` (12 pass), `typecheck` and `build` (pass). System shell remains Node
22.22.3; use the pinned invocation above. No package or lockfile versions changed.

Production Edge/Playwright: 47 theme/layout checks plus 27 interaction regressions
pass. This covers live OS changes, overrides, reload, cross-tab sync, invalid saved
values, blocked storage, compact growth/shrink, shared column geometry, semantic
icons, both-theme contrast/focus, long content and 720px/390px basic reflow.
Interaction regressions cover suggestions, keyboard/IME, attachments/reselection,
unsupported selection, reset during pending work, fictional source chips, no student
API requests and `/dev/health` with a mocked ready probe. No hydration/page errors.
Measured normal text >=4.5:1, enabled action icons and composer boundary >=3:1.
Visual review: light/dark empty workspace, rejection and conversation screenshots.
The initial dark capture caught a color transition; waiting for completion confirms
the existing palette is correct (New Chat 13.03:1), so no palette workaround added.

`py -3.13 -m pytest tests/test_docs_hygiene.py -q -p no:cacheprovider --basetemp
C:/Coding-projects/bintanong_workspace/audit-evidence/frontend-ux-20261024/pytest`
passes all 10 tests; phase-ledger validation is valid with no active numbered phase.
Browser scripts and images
stay ignored in `C:/Coding-projects/bintanong_workspace/audit-evidence/frontend-ux-20261024/`.
Initial Refactoring UI diagnostic 6/10: hierarchy, sizing/spacing and alignment
needed correction. Final diagnostic 9/10: seven checks satisfied; a formal blurred/
grayscale comparison remains unverified. No user-acceptance or mobile-design claim.

Existing Next workspace-lockfile/standalone-launch warnings remain; they do not
fail the build. Existing pinned-framework security advisories remain outside this
correction. No real backend, cross-browser or physical assistive-device validation.

References:[CSSlight-dark](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/color_value/light-dark),
[color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/color-scheme).

## Next action

Owner reviews the revised preview; any further visual feedback stays within the
bounded frontend demo. Unfinished flows and real transport need separate work.
