# Local research comparison page

Owner asks whether thesis comparisons can be implemented as a test page. Worktree
`p12-pr20`; no evaluation-worktree edits or production mode switch. Design only so far.

## Proposed smallest slice

- Local, opt-in researcher page under `/dev/`, absent from student navigation.
- One question and selected curriculum per run; explicit condition labels and
  sequential execution on the shared model slot. No automatic 72-case run.
- Show unscored experimental outputs, evidence and per-condition outcomes/timings.
  Record failures and refusals rather than dropping them from the export.
- Download a run manifest and results with question, condition, source snapshot,
  code/prompt/model identities, decoding settings and scope. Memory-only run state;
  no private uploads, institutional corpus changes or application database writes.
- Reuse the current model transport, pinned release provider, orchestration and
  existing admission/origin boundaries. The student proxy is explicitly allowlisted;
  a hidden frontend route alone would not enforce a researcher-only boundary.
- API routes must also be opt-in/local; experimental baseline output must never be
  labelled a validated student answer or inherit full-pipeline source/status claims.

## Required methodological choice (asked through the UI)

1. Controlled symbolic-evidence ablation: same applicable question, documentary
   context, answer prompt/model/settings; vary symbolic evidence and dependent checks.
   Requires documenting shared evidence and rejecting inapplicable cases rather than
   quietly substituting another context or calling them proof of Prolog's benefit.
2. Whole-system comparison: baseline Bintu-1, RAG-only and actual full Bintanong.
   Useful system comparisons, but routing/prompt/validation differences must be
   reported; the RAG-only/full difference is not automatically a pure Prolog effect.

The choice changes the executor and interpretation, not merely the column labels.
Await the owner's selection before implementing condition execution.

## Inspection findings and acceptance

`evaluation/` has benchmark/grouping/traceability contracts; no reusable live A/B/C
executor was found in tracked Python. Existing `/dev/health` is a UI precedent,
not an evaluation runner or an access-control solution. No dependency is needed
merely to build the page. Historical conditionB remains skipped.

First regressions should cover default-off endpoints/page, invalid scope/input,
condition evidence separation, failure/cancellation/admission cleanup, faithful
export and rendering without unsafe HTML or unsupported automatic accuracy claims.
Use synthetic source fixtures; live acceptance starts with one bounded case.
