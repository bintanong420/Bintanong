# Current progress

Updated7November2026. Active development worktree/branch: `p12-dev`.
PR20 merged at `84e7c0db`; original ingestion/researcher merge `0a0fd297` preserved.
No numbered phase started or advanced. Last full progress snapshot: `12f27bd6`.

## Current integrated state

[Reconciliation](../2026-11-07-p12-dev-pr20-reconciliation.md) and
[PR20 checkpoint](../2026-11-07-pr20-execution-checkpoint.md).
- Owner explicitly requested reconciling P12-dev/PR20; PR20 marked ready and merged
  through GitHub with expected source head `12f27bd6`. Local p12-dev fast-forwarded.
- Ingestion preparation/reviewer tools and researcher app preserved byte-for-byte
  from development; student application code preserved byte-for-byte from PR20.
- PR20 includes bounded compound execution, per-topic evidence/presentation,
  server-bound clarifications, language/recovery fixes and concise source controls.
- Recovery `0634d12c` uses one Sources action for curriculum and Handbook evidence;
  affected courses precede recovery plan. Missing evidence retains visible quotations.
- Compiler/compound defaults remain OFF; existing staging opt-ins are unchanged.
  No inferred grades, new institutional approvals or source/database activation.
- Evaluation/ablation work remains on separate `feature/p12-evaluation-ablation`.
  Original thesis evaluation checkout and its owner changes were not modified.

## Verification

- Original215-case backend roster passes across existing environments:187 initially
  passed;28 missing-PyMuPDF cases resolved by system Python3.13, all34 PDF cases pass.
  Reruns overlap; do not sum them.16 PR20 compound pipeline checks also pass.
- Student frontend109 tests and TypeScript pass. Researcher7 tests pass/1 skipped;
  its Next16.4.3 production build/TypeScript pass. Live reviewer document-switch
  case requires an actual launch session and was not run.
- No CI statuses reported on the pre-reconciliation head. Earlier PR20 verification
  and live evidence remain linked in its checkpoint; this is not a fresh full-suite run.
- Historical source/owner72Y acceptance remains qualified, not independent72/72 proof.

## Runtime and next action

No services reloaded for this branch reconciliation. Existing PR20 staging3218/API8023
and separate ablation3219/API8024 retain their previously recorded startup identities.
The new development branch is not evidence that a running3217 process has reloaded it.
No dependency/model installs or downloads. Institutional sources, F04/source gaps,
undergraduate scope and private-context separation keep their established boundaries.
GUI knowledge intake (owner 11 Nov, [plan](../2026-11-11-gui-knowledge-intake-plan.md)): `b192fc9c` plan;
`14213e9c` step 1 upload route (RED 15/16 for missing module, then GREEN; 64 knowledge-update tests,
researcher 24 pass/1 skip, TypeScript pass). Route not yet wired into `review`/CLI (step 4). Next: step 2.
Earlier next: owner review on the integrated development branch, then independent human/
benchmark, paired language/compiler and latency acceptance. No institutional deployment
or automatic closure of source PR18/19 is implied by the development merge.
