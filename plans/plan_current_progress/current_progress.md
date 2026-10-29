# Current progress

Updated 29 October 2026 (machine local date; inherited release/report names retain 30 October).
Phase 12 research/software evaluation write-up complete with disclosures; no active implementation phase.
p12 / `p12-evaluation-harness`. Deployment (Phase 13) cancelled by owner.
[Final handoff](../phase-12-handoff.md) · [Report](../../docs/evaluation/phase12-evaluation-report.md) ·
[Activation results](../2026-10-30-hosted-560-activation-results.md).
Last full snapshot before condensation: `76d5a92`; use `git show` for prior history.

## Latest change

Hosted research release `p12-research-faqsplit-20261030` is active: 560 chunks/vectors, 39 curriculum links.
Corrected78 superseded and retained as rollback. Staging106.11s/activation121.08s, exits0; exact readbacks,
retrieval target hit and existing-row preservation passed. Bound local artifacts and source states unchanged.
Commits: `acbb0b9` preflight, `0b4aef9` staging, `62ecb96` activation; closure docs follow.

Hosted HTTP smoke: document, prerequisite and Hybrid all answered with citations (51.0/26.7/49.5s,
outer API single observations, excluding startup/browser). Guest browser smoking penalty/source panel passed,
Handbook p.93, 0 console errors/warnings. Backend constructed110.88s, live/ready200.

Backend :8021 uses ignored `p12-hosted-560-activation-20261030/hosted-research-api-config.json`;
frontend :3216 runs from p12; model :18088 is the existing container. Old corrected78/local-documents config
cannot be used after the switch. Restart/rollback commands and exact hashes are in activation results.
.env stays ignored/untracked; no secrets or raw evidence staged. No dependency/model changes.

## Evaluation and limits

Fresh saved-output audit matches report: main v2 38/50 (76%); original C40/50, rerun39/50, A strict3/50,
content8/50; robustness Tagalog19/26, shorthand15/26, broken English2/4. No new benchmark runs.
Historical full merged suite7314pass/1608subtests,6skip/2xfail; related hosted-pin108pass inherited.
Full suite not rerun for operational/docs-only continuation; live checks/phase/link/diff validation used.
Development reuse, single author/single runs, remaining failures, unmeasured metrics/SUS/UAT, unsupported photos,
deferred PSU sign-in and no institutional validation remain disclosed. Benchmark used local documents;
hosted smoke is not benchmark parity. Undergraduate/source-gap/privacy/unknown-versus-unmet guards remain.

## Next action

No next implementation phase. Hosted answer-quality benchmarking is a separate owner/Claude follow-up;
Phase 13 remains cancelled. Preserve existing evaluations, bound artifacts and corrected78 rollback.
