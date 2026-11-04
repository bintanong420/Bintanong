# Program chip visual adjustment — 4 November 2026

Removed the curriculum year from the chat scope chip, changed the selected chip from outline to ghost styling, and reduced horizontal padding/gap. The full program remains in the accessible name; its action and current program remain clear. The dialog and scope-selection behavior are unchanged. The 44px minimum control height and global keyboard focus indication remain.

Changed: `frontend/components/workspace/workspace.tsx`, `frontend/app/styles.css`.
Verification: `cd frontend; npm run typecheck` passed. No browser visual check performed.

Screenshot follow-up: applied the same borderless ghost appearance and 44px hit target to the unselected “Choose program” state, which otherwise rendered as a dark filled pill. Reduced inline padding and icon gap in both states. The screenshot's composer border remains unchanged. Fresh typecheck passed; browser/Playwright rendering was unavailable in this environment (no browser surface or installed Playwright package).
