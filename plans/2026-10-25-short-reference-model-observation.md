# One-case short-reference model observation

Student capability: receive a grounded requirements-and-steps answer rather than a
generation failure for the saved Taglish pre-enrollment question. Evidence path:
reuse the exact saved IntegrationResult, then ordinary per-part generation,
canonical-reference restoration, source guards, review and final validation.
Phase11 service-quality exit remains open; this observation isolates the output
overhead question and does not establish routing/retrieval or language accuracy.

## Baseline and bounded method

- Original code2ce3daf, documentation successor9bab934; clean production/test tree.
  Existing full-suite.head binds2ce3daf; exit0,6763 passed,1595 subtests passed,
  6 skipped,2 xfailed,6 existing warnings,1306.19s. Read the completed result;
  do not rerun the suite for this observation-only increment.
- Before observation, apply and verify the owner's subsequent approved
  [exact-excerpt plus referral](2026-10-25-service-cutoff-referral-plan.md).
  Bind that new code commit; its behavior change requires its own full suite.
- Reuse `p11-taglish-infer-20261025/observation/procedure-taglish/integration.json`
  and the exact question from its results.jsonl. Bind their SHA-256 hashes and the
  code tree. No fresh router, encoder, database, source extraction or release work.
- One Generator.generate call, explanation_profile=parts/reference_profile=short.
  Same server,768 cap,seed0,temperature0,thinking off,prefix reuse. Capture input
  before inference, raw HTTP completion before parsing, fixed error args[0],
  call duration and final answer. Maximum4 completions (the existing two drafts
  plus two ordinary reviews); no harness retry, rescue or output-cap change.
- Stop on unexpected input mismatch, unhealthy server, transport failure or
  exhausted ordinary repair. No equivalent reruns or parameter sweep.
- Inspect completion finish reason/tokens, restored final citation identities,
  cutoff fidelity, step omissions/order/office association, and reply language.
  Token savings/completion success alone cannot pass the semantic-quality gate.
- Timings are saved-evidence generation/review only; routing,retrieval,encoder,
  API/browser/network-to-student,cold start and queueing are not separately
  measured. No student-visible latency claim or SLA.

## Boundaries and validation

Expanded80-record release remains inactive; default stays canonical. Owner chose
exact printed terms plus an office referral; the presentation choice is resolved.
The existing source cutoff/precedence/source-gap/privacy/undergraduate rules stand.
The observation itself changes no production/test/dependency/model/source/pin,
so it needs no additional suite beyond the separately verified referral increment.
Validate the harness by compilation, strict saved
contract parsing, provenance checks, captured call bounds and final host validation.
Raw research evidence stays ignored under workspace/audit-evidence/
`p11-short-reference-model-20261025/`. Record actual results here before finishing.
