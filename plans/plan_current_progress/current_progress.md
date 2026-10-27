# Current progress

Updated 27 October 2026. Phase 11 active; `feat/p11-policy-ingestion-review`.
Last full snapshot before condensation: `d3f4114`; recover with `git show`.
[Phase checkpoint](../phase-11-checkpoint.md) · [Ingestion checkpoint](../2026-10-26-policy-ingestion-checkpoint.md).

## Latest delivery

[AI ingestion results](../2026-10-27-ai-ingestion-results.md) and
[operator guide](../../docs/development/ai-assisted-ingestion.md): native extraction
can receive original-page vision advice before packet hashing; alternate LlamaParse
batches feed the same pending reviewer. Use/Ignore/edit still require explicit human
save. Stale source/candidate bindings reject; failures retain manual review.
No second journal, shared contract, student API/runtime, dependency or model change.
Commits 1711066/c338146/16ed7d6/45924ce/4ba7fb4/d3f4114/4ff5872 are local; no push.

Final compatibility run: 1821 passed/13 subtests,189.53s,exit0. Includes ingestion,
prospectus and original reviewer paths. Focused48pass; Node7pass/1browser-skip;
TypeScript passes; configured synthetic browser1pass1.90s with explicit save.
Later mismatch-total metric fix:7evaluation tests pass;22documentation checks pass.
Production build verified in isolated app. Synthetic3003/8767 stopped; owner
3001/3002 reviewers not restarted. Installed Node22.22.3 differs from target24.21.0.

Full available repository run:6949pass/745subtests,2fail,1skip,2xfail,401.05s,exit1.
Both failures are unchanged native Docling conversion: Transformers5.10.2 needs
huggingface-hub>=1.5,<2, but installed2.2.0. Fresh native conversion is blocked;
mocked pipeline success does not clear it. Seventeen local DB test files excluded:
DockerDesktopLinuxEngine unavailable. No hosted fallback or dependency workaround.

Gemma4E4B supports images; local GGUF exists,matching mmproj/working image endpoint
not verified. Vision and LlamaParse live smoke NOT RUN: endpoint/key unavailable.
Matched28-page real-source sample/84rows and summaries created under ignored
workspace audit-evidence/p11-ai-ingestion-20261027; metrics remain blank/null.
No human accuracy,time,cost or cleanup-improvement claim. Complex table JSON and
continuation metadata remain manual; missing verified geometry stays build-held.

## Preserved state

- [Backend merge](../2026-10-27-backend-c370f00-ingestion-merge.md): local backend
  c370f00 merged here at3c1d76c. Student/source/runtime owners remain separate.
- [Policy/prospectus UI](../2026-10-27-save-control-and-prospectus-review.md):
 72policy records/298fields and39prospectus bundles are separate local packets.
  The newer336/465upstream evidence was not silently regenerated or imported.
- Frozen78copy is nested comparison-baseline-78/comparison-baseline-78;
  baseline11file/7seal verification preserved in ingestion checkpoint/report.
  Original PDFs rehashed for the new sample; no baseline mutation.
- Existing active release/pin and other worktrees untouched. Inherited hosted
  research state is historical,not freshly queried. T4/T5 remain unfinished.
- Undergraduate scope, source gaps, F04 and other holds, unknown-versus-unmet,
  private-file separation and separate reviewed symbolic authoring remain intact.
- Context refreshed: thesis physical17–18,routing PNG,master3.1/16. Prior39–44
  curriculum evidence retained; no student architecture discrepancy introduced.
- Repo handoff/TDD and installed relevant skills applied; official online options
  researched, no skills/dependencies installed. User-requested memory note retained.

## Next action

Resolve the existing native Python dependency mismatch in an approved environment,
rerun its two failing checks, then run configured live smoke/matched human evaluation.
Original T4 local lifecycle tooling and T5 operator rehearsal remain separate next
workstream tasks. No hosted access, activation, phase advancement or automatic push.
