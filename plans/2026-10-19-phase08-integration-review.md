# Phase 08 integration decisions and independent review

Scope: offline software mechanics for master13. The owner requested Phase08 resume
and organized developer pipelines in isolated p08 on19October2026. Source authority,
institutional activation, final answers and authenticated student HTTP remain held.

## Design decisions

- Reuse the delivered Router, RetrievalEngine and CurriculumRuntime. Ordinary Python
  control flow joins typed ports; no additional framework or dependency change.
- Existing retrieval debug reports and synthetic/offline research rule observations
  are not institutional answer evidence. Introduce explicitly candidate-only
  integration contracts; do not weaken institutional EvidenceBundle/AnswerEnvelope.
- Pin synthetic source hashes/chunk membership/bundle version before routing.
  Default provider denies execution; no authorized institutional loader is claimed.
- Follow-ups use explicit owned/scoped caller context. No transcript storage,
  implicit target reuse, automatic assertion persistence or private-file ingestion.
- One bounded stage budget covers retrieval embedding+storage. No separate embedding
  or SQL latency measurement is claimed. Janus keeps its subprocess bound; thread
  cancellation retains adapter admission until actual completion.
- No final answer generator or student API is added: master14/15 assign those to
  Phases09/10. Existing API remains health probes. Two known Phase07 style errors and
  all source/hosted migration holds carry forward. No new prompt/model sweep.

These implementation choices follow existing scope/phase boundaries. Their cost is
that real-source/student deployment remains unavailable until the applicable loader,
source, API and release gates are satisfied; synthetic mechanics cannot prove quality.

## Independent review and correction pass

Fresh read-only reviewer inspected base6c3b09a..core0a6db29 and relevant requirements.
48then-current orchestration tests passed. Four P2 findings were independently
reproduced; no repository changes, actual-model calls or database operations by reviewer.
Author reviewed the feedback technically and accepted all four findings:

| Finding | Correction and meaningful regression |
| --- | --- |
| Valid `rule-course_a` crashed telemetry; event construction outside guard | Permit runtime identifier underscores; unsafe adapter metadata yields bounded invalid_output with no raw body; underscore/unsafe-ID regressions |
| 256valid caller facts plus a new grounded assertion escaped as ValidationError | Build merged RequestContext inside guarded routing stage; overflow withholds dispatch and records invalid_output; 256+claim regression |
| Router model timeout and exhausted malformed JSON became semantic unavailable controls | Map fixed Router diagnostics to timeout/tool_error/invalid_output while preserving genuine controls; timeout/connection/malformed-output regressions |
| Document availability holds masked symbolic conflict/error/unknown | Apply explicit precedence, retaining both observations and scope none; nine-cell symbolic-failure/document-hold matrix plus document-conflict/release tests |

Regression RED:15failed/1passed/34deselected1.19s, expected four defects reproduced.
GREEN:67passed3.60s,exit0 across all five orchestration test files, including actual
synthetic Janus. Raw:workspace/audit-evidence/p08-orchestration-20261019/review-red.log
and review-green.log. No second independent review is claimed after these corrections.
No reviewer findings were deferred or declined; actual deployment/semantic source
contradiction detection were explicitly outside this synthetic integration scope.

Priority:release_mismatch > conflict > error > unsupported > unknown > clarify >
no_evidence > uncalibrated > ready. This is outcome reporting, not source precedence:
it never adjudicates which university rule is authoritative. Both returned component
observations stay visible. Exceptions/failed components yield no partial evidence.

## Verification boundary

Combined smoke uses actual Router, RetrievalEngine and Janus with scripted model,
manual unit vector and synthetic DB responses. It verifies each route and proves
Symbolic makes no retrieval call. It does not measure actual Bintu/SEA-LION quality,
real network latency, institutional source accuracy or population language accuracy.
No accepted institutional benchmark wording/source review was reopened.
Full scoped gate, exact command and delivery identities belong in the final handoff.
Fresh36-file gate1748passed/63subtests103.91s,exit0. Supplemental smoke extends
the fixture to seven combinations:one RAG and each of three operations on both
Symbolic/Hybrid;7passed2.62s,exit0. No product code changed after the broad gate.
Raw final-regressions.log/verify-final.ps1/operation-smoke.log under the same root.
