# About page scope link removal — 4 November 2026

Removed the “Scope and privacy” link from the About page and its now-unused underline rule. Preserved the research-preview and advisory text; scope/privacy policy content elsewhere is unchanged.

Changed: `frontend/app/about/page.tsx`, `frontend/app/styles.css`.
Verification: `cd frontend; npm run typecheck` passed. Confirmed no “Scope and privacy” link remains in the About page; other scope/privacy content was not edited.
