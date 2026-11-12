# GUI intake continuation: multiple PDFs

Owner asked to continue Claude's ingestion GUI work on 12 November 2026.
Claude session `cdff1354-51b5-4aaa-b9eb-93117b8bc58f` ended while its multi-upload
worker hit the usage limit. Resumed its existing dirty `feat/ku-multi-upload` worktree
`p12-ku-multi`, based on `d065fb04`; the evaluation checkout was left unchanged.
This continues the [GUI intake plan](2026-11-11-gui-knowledge-intake-plan.md).

## Delivered scope

- Native multi-file picker/drop, 20-file cap, editable filename-derived title/year,
  per-file kind, shared notes and explicit apply-all defaults.
- One existing POST per PDF, strictly sequential. Each upload keeps its own review,
  prepare and build. No auto-prepare, approval, activation or cloud writes.
- Per-file status, remove, retry and stop-after-current; completed uploads are not
  resent by Upload unfinished. Lost/incomplete/5xx responses require a duplicate-risk
  confirmation before either retry path sends again.
- Full-width upload area on desktop; stacked fields on phones, existing themes,
  field labels/errors, live status, focus after completion and unload warning.

## Verification and review

System Python 3.13 read thesis physical17–18; runtime routing PNG inspected.
Master18.3 and the existing GUI plan keep institutional updates researcher-controlled,
undergraduate-only and separate from private student uploads. No architecture change.
Review followed the plan's inherited independent task review requirement.

- `node --experimental-strip-types --test researcher/tests/upload-batch.test.mjs`:
  initial 12 inherited tests passed. Added regressions RED for false filename/size
  deduplication and retry while running/stopping (2 failures), then GREEN (15 pass).
- Browser test RED for enabled Retry during an active upload; later RED for the panel
  closing after the first success. Both fixed; complete browser regression GREEN,
  independently rerun by reviewer (1 pass). All API traffic intercepted, no real writes.
- `node --experimental-strip-types --test tests/*.test.mjs` in researcher: 95 pass,
  2 skipped (optional browser and existing live document-switch test).
- `node node_modules/typescript/bin/tsc --noEmit`: pass.
- `node node_modules/next/dist/bin/next build --webpack`: pass.
- `git diff --check`: pass. Cached tooling reused; no install/dependency/lock changes.
- Independent review found Stop/retry, lost-response and false-dedup defects; rereview
  approved the fixes, with explicit duplicate-risk handling accepted for this UI slice.

Browser command: set `BINTANONG_INTAKE_TEST_ORIGIN=http://127.0.0.1:3061` and
`BINTANONG_TEST_PLAYWRIGHT` to the existing cached Playwright `index.mjs`, then
`node --experimental-strip-types --test researcher/tests/upload-batch-browser.test.mjs`.
Screenshots: workspace `audit-evidence/ku-multi-20261112/{light,dark}-{1280,390}.png`.
Inspected desktop/light and phone/dark; overflow assertions pass for all four.
Modern-web-guidance `forms`: semantic controls, linked field errors, submission state,
status announcements and 48px row controls. Native multiple-file behavior checked
against MDN File API/file input guidance. Existing calm UI direction retained:
ENERGY1/RHYTHM1/MOTION1, existing palette/type, one upload action, no new visual assets.

## Remaining boundaries

- Retry is manual and not idempotent. An uncertain response can mean a saved file;
  explicit confirmation warns of duplicate creation. No automatic retry.
- Queued files live only in the browser; keep the page open. Server still enforces
  PDF/size/metadata rules, and still buffers one upload at a time.
- Full upload-to-draft rehearsal (step7), `check-draft`, Gemma/GPU verification and
  the governed local activation route remain outstanding from Claude's plan.
- Cloud publishing stays unimplemented/read-only pending the owner's choice of
  inactive drafts versus activation. Local staging does not authorize hosted changes.

Next: integrate the independently reviewed multi-upload slice into p12-dev and
rebuild/restart the researcher app, retaining the owner's USG packet unchanged.
