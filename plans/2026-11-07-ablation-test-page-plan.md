# Local research comparison page

Owner asks whether thesis comparisons can be implemented as a test page. Worktree
`feature/p12-evaluation-ablation`, separate worktree `p12-evaluation-ablation`.
No thesis evaluation checkout edits or production mode switch.

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

Owner directed checking/unifying the other P12 branches, then explicitly required
a separate branch. Fresh fetch found the evaluation page on
`origin/p12-evaluation-harness` at `69fc7cea`; the local evaluation ref was stale.
Reuse that page for actual full-pipeline benchmark runs; add the controlled
evidence-synthesis comparison separately. C is not labelled the production pipeline.

## Inspection findings and acceptance

Imported six commits with cherry-pick provenance: roster/scoring `e03d7962`,
retrieval observation `7524b00c`, gated API `f37b1797`, page/client `14caa702`,
curriculum binding `a73b6128`, scoring/failure fixes `1e499828`. Other remote fixes
and thesis metrics exports were not merged. Existing live A/B/C executor absent;
the imported page provides full-system runs and human evaluation, not ablation.

Controlled comparison prepares one current reference answer, freezes its actual
source cards and checked symbolic report, then uses one answer prompt/model profile
for A(no evidence), B(source cards), C(same cards plus report). No gold keys or
reference prose reach generation. All outputs stay explicitly unvalidated; failed
conditions remain in the export. Document-only/unsuccessful reference cases are
not applicable. Fixed-order single runs are exploratory, not statistical evidence.
Reference benchmark runs retain their original scoring semantics; ablation records
are separate. Existing gated local JSONL storage is reused, superseding the initial
memory-only proposal; no private uploads or institutional database writes.

Initial verification: imported gates97 passed; extension/API/composition gates113
passed; all125 frontend tests and TypeScript pass. Production build, browser/live
acceptance and opt-in staging configuration remain pending. Historical thesis
conditionB remains skipped; implementing this tool is not a completed experiment.

First regressions should cover default-off endpoints/page, invalid scope/input,
condition evidence separation, failure/cancellation/admission cleanup, faithful
export and rendering without unsafe HTML or unsupported automatic accuracy claims.
Use synthetic source fixtures; live acceptance starts with one bounded case.
