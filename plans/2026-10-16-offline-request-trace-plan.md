# Offline request trace design and execution plan

> Execute inline with executing-plans and one final independent review.
> Baseline `9916068`, unchanged product `232a418`. No product extension planned.

**Goal:** Compose existing gate evidence into one inactive, inspectable trace for
all 63 accepted variants under both existing focus strategies. Continue the
[partial-claim handoff](2026-10-16-partial-claim-coverage-report.md).

## Contract

Input is the unchanged accepted query identity, explicitly trusted request context,
applicable existing source/claim catalogues and a selected saved-context decision.
No new query parser, model, policy default, source reading or gold-label inference.
Use the existing selector/report functions where they exist. The diagnostic's
explicit audience/entity branches preserve recorded scope decisions; they do not
implement or measure automatic classification.

| Order | Gate and input | Stop/result boundary |
| --- | --- | --- |
| 1 | Explicit audience from accepted request trace, otherwise supported website undergraduate context | Law/faculty employment stays excluded; return no institutional evidence |
| 2 | Existing explicit unresolved TC ambiguity | Clarify canonical entity; no invented expansion or retrieval evidence |
| 3 | Existing explicit curriculum hints, when applicable | Replay current selector; unknown BSCS clarifies, unavailable BSIT stays limited to selected rows |
| 4 | Trusted subject or subject derived from matched curriculum's complete version/chunk set | Replay subject selector; curriculum set must equal selected subject snapshot |
| 5 | Caller-chosen saved all-primary or experimental gap-free decision at k3/.5/2048 | Preserve context hash/tokens/IDs/gaps; a null decision is not empty successful retrieval |
| 6 | Existing exact caller claims/register and emitted IDs | Run unchanged claim report; known limits, missing fields and unknown claims remain distinct |

Output contains ordered gate records with their input provenance, stopping reason,
context-selection state and source-claim report when reached. Every trace remains
candidate-only, inactive, `answer_sufficiency=unassessed`, with automatic
interpretation/runtime integration/calibration unimplemented. Early scope/entity/
curriculum stops have no subject/context/claim report. Source limitations may be
reported even when saved context is absent; the context state stays visible.

The trace is a diagnostic composition of trusted conditions. It does not validate
source authority/currentness, authenticate annotations/reviewers, evaluate truth or
establish an answer-success rate. No API/runtime/DB/Prolog/router behavior changes.

## Inputs and independent checks

- [ ] Verify prior partial-claim seal, preserved inputs and unchanged code digests.
  Keep originals, old catalogues/registers and owner artifacts untouched.
- [ ] Freeze all 63 identities and existing request/curriculum/subject/claim inputs
  from the prior matrix and four source-report increments. Keep the policy and
  curriculum catalogues separate. No inferred curriculum/source-currentness choice.
- [ ] Compose 126 traces (63 × two caller-chosen saved strategies) using current
  helpers; preserve every gate's evidence and short-circuit all excluded/ambiguous
  requests. No retrieval, encoding, reranking or context assembly.
- [ ] Compare reached reports with their existing sidecars where a saved prefix
  exists; record null-prefix reports separately without fabricating an older run.
- [ ] Add structural precedence checks: excluded audience beats later supplied
  hints; unresolved entity beats curriculum/subject; unknown curriculum cannot be
  bypassed by a subject; mismatched curriculum/subject sets are rejected. These
  are synthetic metadata probes, not new accepted questions or policy facts.
- [ ] Independent verifier must reconstruct all gate decisions/identity sets,
  exact helper outputs, report/context pointers, provenance hashes and null states.
  Distinguish replay checks from the independent frozen-evidence audit.
- [ ] Focused existing selector/claim regressions and documentation/ledger checks.
  No unchanged full/native-suite repetition or dependency/model work. An actual
  product defect would require separate RED/GREEN before changing behavior.
- [ ] One final independent review; seal raw evidence and update report, INDEX,
  CLI/blocked handoffs, checkpoint/current progress through explicit verified commits.

Raw scripts/JSON/logs live ignored under workspace
`audit-evidence/p05-offline-request-trace-20261016/`; repository records live in
`plans/`. Source content and all accepted wordings stay unchanged. Source governance,
representative calibration and formal Phase 05 Tasks 4/6 remain open; no activation
or Phase 06 advancement. The master plan remains unchanged.
