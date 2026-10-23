# Approved frontend implementation

Owner-approved plan, 23 October 2026. Base: frontend `7d188d2`.
This is an interactive synthetic desktop preview, not formal Phase 11 advancement.

## Evidence and scope

- Live Proper UI Checklist rechecked before implementation: `59:835`-`59:840`
  shell/sidebar/composer/upload/send/suggestions checked; `59:665` disclaimer,
  `59:698` source chips, `59:737` rejection and `59:739` removal checked.
- Targets: empty `27:7946`, attachments `79:11556`, rejection `79:11667`,
  answer/source chips `80:12243`/`85:12353`, status presentation `79:12016`.
  Processing semantics `59:775` remain partial. Review 3 `101:932` applies.
- Context consulted during planning: thesis physical17-19,65-66,76-79 and runtime
  routing PNG; master16/23/24, current ledger, Phase10 handoff and frontend brief.
  Figma references another thesis edition; repository scope/architecture govern.
- Backend runtime/generation/private-context services exist; public student HTTP
  endpoints remain absent. No backend contracts, reasoning or APIs change here.
- Preserve untracked model directory. Assets/fonts and UI dependencies are the
  downloads authorized by this task; no model downloads or source activation.

## Execution record

1. Interaction state: RED6failures/2passes with empty behavior; GREEN8/8.
   Command: `node --experimental-strip-types --test frontend/tests/workspace.test.mjs`.
2. Tailwind/shadcn and health-route preservation: pending.
3. Approved desktop components and local assets: pending.
4. Browser/build/accessibility verification and final review: pending.

## Rulings and exclusions

- Existing dedicated frontend checkout is the implementation workspace; do not
  switch the owner's branch or change shared backend worktrees.
- Follow icon replacement, campus fade, attachment reflow/removal annotations.
  Do not redesign tentative disclaimer/source-inspection UI or use mock academic
  claims as facts. Red-banner white text is3.76:1; correct contrast minimally.
- UI demo only: fixed fictional responses, local file metadata, no contents read,
  network upload, storage, policy selection or academic decisions.
- Clarification, source drawer, fact confirmation, symbolic-result anatomy,
  temporary-context manager, session expiry, mobile designs, general recovery,
  Settings/Admin/authentication/history persistence remain unfinished.
- Apply antislop UI/copywriting/human guidance within the approved Figma design.
  Design read: quiet light conversation workspace; ENERGY1/RHYTHM1/MOTION1.
  Campus photograph and white fade establish place and preserve reading space.

## Verification and next action

No UI completion claims yet. Next: add the UI foundation and local assets.
Pinned Node24.21 is available through npm exec without a system-runtime change. Keep raw screenshots/logs under workspace audit-evidence.
