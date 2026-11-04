# Program chip visual adjustment — 4 November 2026

Removed the curriculum year from the chat scope chip, changed the selected chip from outline to ghost styling, and reduced horizontal padding/gap. The full program remains in the accessible name; its action and current program remain clear. The dialog and scope-selection behavior are unchanged. The 44px minimum control height and global keyboard focus indication remain.

Changed: `frontend/components/workspace/workspace.tsx`, `frontend/app/styles.css`.
Verification: `cd frontend; npm run typecheck` passed. No browser visual check performed.
