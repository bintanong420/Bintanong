# Reconcile P12 development and PR20

Owner7November explicitly requested reconciliation/integration of `p12-dev` and
PR20. This authorizes the development merge; it is not deployment, institutional
approval, source activation or completion of the remaining research acceptance.

## Inputs and preserved work

- Development head `0a0fd297`: ingestion pipeline and researcher review GUI from
  `feat/p11-policy-ingestion-review`.83 files,9777 inserted lines relative to its
  first parent. Preserve these; replacing the development tree with PR20 would lose them.
- Published PR20 head `73d5d16e`, latest application code `0634d12c`.
- PR20's two unpublished research-planning notes were already preserved on the
  separate published `feature/p12-evaluation-ablation` branch. Local PR20 was
  returned to its published head before reconciliation; no published history rewritten.
- Merged `origin/p12-dev` into the PR20 checkout with `--no-commit --no-ff`.
  Automatic merge succeeded; no conflict resolution or application-code patch needed.
- Byte-for-byte checks: staged ingestion/researcher trees match `origin/p12-dev`;
  staged student API/generation/routing/orchestration/frontend match published PR20.
- Separate ablation branch, original thesis evaluation checkout and running
  staging services remain untouched. No new dependencies, downloads or model calls.

## Verification

- Combined backend gate initially187 passed/28 failed: all28 failures were missing
  PyMuPDF in the existing P12 virtual environment. Existing system Python3.13 has
  that package; all34 PDF-ingestion cases pass there. The original215-case roster
  is reconciled across these environments; overlapping reruns are not summed.
- PR20 compound pipeline:16 passed.
- Student frontend:109 tests and TypeScript pass; application code is unchanged
  from the already-built staging candidate.
- Researcher frontend:7 passed/1 skipped; Next16.4.3 production build/TypeScript pass.
  Skipped document-switch browser case needs an actual reviewer launch session.
- No CI statuses were reported by GitHub for the pre-reconciliation PR head.
- Diff whitespace check is clean except three preserved historical Markdown
  hard-break lines in `2026-10-27-ai-assisted-ingestion-codex-plan.md`.

## Delivery

Reconciled PR20 head `12f27bd647dbded5a8d4760b2b938a9740dc5228` pushed normally.
Marked ready under the owner's explicit integration request and merged through
GitHub with the exact expected head, without bypassing repository protections.
PR20 is merged; target commit `84e7c0dbd0b4be61aaff254da23339aa4110131b`.
Local `p12-dev` fast-forwarded from `0a0fd297`; both its former head and PR20 are
ancestors of the resulting development branch. Local checkout was clean.
No closure of source PR18/19, thesis/ablation branch sync, service reload or
source/database/release activation. Remaining independent/human/latency acceptance
is not converted into a pass by the development merge.
