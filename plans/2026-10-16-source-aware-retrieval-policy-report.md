# Source-aware engine policy delivery — 16 October 2026

Owner approved the [design](2026-10-16-source-aware-retrieval-policy-design.md)
after `ff53c65`. The [implementation plan](2026-10-16-source-aware-retrieval-policy-plan.md)
executed inline. Snapshot implementation `cc62c99` and engine integration
`d0f996e` are committed; review corrections are at `7d1b0fe`.
The bounded implementation is verified below; this is not a formal Phase 05
completion handoff.

## Resulting behavior

The existing retrieval engine now has an opt-in source-aware policy. It binds
actual RPC rows to a copied candidate source snapshot, checks source/curriculum
conflicts before subject filtering, assembles complete selected groups once,
and assesses the actual emitted IDs. The supplied subject and exact claims are
trusted research input; no automatic interpretation is claimed.

Reviewed absent claims and known unresolved limits force insufficient evidence,
including a limit on a selected-subject member that was not retrieved. Unknown
claims remain unassessed. Available reviewed fields stay uncalibrated; even a
caller-selected settings policy name cannot promote the opt-in result to ok.
Binding failures clear evidence/context. Missing intent and early retrieval
failures do not expose snapshot field values or run claim assessment.

The opt-in result uses debug v2 and explicitly identifies candidate-only status,
ineligibility for activation, unverified runtime authorization and unassessed
answer sufficiency. Original no-policy calls retain v1 behavior and formatting.
The approved change adds no SQL, release loader, CLI flag, API endpoint,
dependencies, embeddings, source approval or executable rules.

## TDD and regressions

The existing readiness Python 3.13 environment ran pytest with `-B`,
`-q -p no:cacheprovider` and separate external basetemps.

| Step | Observed result |
| --- | --- |
| Snapshot RED | Explicit missing-policy assertions, exit 1; no collection failure |
| Snapshot GREEN plus existing subject/claim helpers | 39 passed / 139 subtests, 0.70s, exit 0 |
| Engine RED | Unsupported policy/intent behavior: 23 failed, 10 passed, 14 subtests, exit 1 |
| Initial engine GREEN | 102 passed / 184 subtests, 1.24s, exit 0 |
| Added citation/whole-record-group regressions | 104 passed / 184 subtests, 1.35s, exit 0 |
| Review-fix RED | Five failures across two regressions/four malformed-version subcases, exit 1 |
| Review-fix focused GREEN | 106 passed / 188 subtests, 1.40s, exit 0 |

Focused command targets: `tests/test_retrieval_evidence_policy.py`, existing
retrieval engine/query/context/evaluation/CLI tests, candidate subject/claims/
claim-review tests and context-selection tests. They exercise real assembly,
claim helpers and engine control flow with synthetic storage/encoder doubles;
no institutional fixture or model inference is introduced.

## Fixed saved-case integration replay

The real engine processed all 39 already accepted document variants at k3,
similarity .5 and 2048 tokens. The replay reused saved query vectors/rankings,
source chunks/versions, annotations and reviews. A strict runtime-role double
applies the existing scope-filter semantics before top-k; the encoder double
returns the matching saved query vector. The verified local tokenizer counts
actual serialized context with saved padding/truncation defaults disabled.
Original source packaging is converted to separate stored chunk/span row shape.

| Language | Top-level uncalibrated / fields available | Insufficient evidence |
| --- | ---: | ---: |
| English (`en`) | 6 | 7 |
| Filipino (`tl`) | 6 | 7 |
| Taglish (`taglish`) | 6 | 7 |
| Total | 18 | 21 |

Every nested report's emitted IDs match the actual assembly; context counts
match the exact tokenizer and remain within budget. Every result retains the
candidate/activation/authorization/answer limits. All 16 input bindings remain
unchanged. This demonstrates component integration conditional on supplied
intent and simulated storage, not an approved-release database replay, final
routing, calibrated production policy or generated-answer accuracy.

The saved-case replay was repeated after the material review correction to verify
the corrected engine at `7d1b0fe`. It retains the same 18/21 totals and 6/7 per
language. Original replay outputs remain intact; corrected-code records live in
the raw root's `post-review-replay/` directory. This adds no new questions, model
encoding, score calculation or parameter grid.

The first summary used a `fil` language key while the accepted roster uses `tl`.
The initial summary is preserved; the corrected summary derives all three
language totals from the existing 39 result records, without repeating retrieval
or encoding. No product behavior was affected.

Raw logs, script, inputs digests, original/corrected summaries and full results:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-source-aware-policy-20261016/`.
Saved encodings, prior seals and original datasets remain untouched.

## Full verification and review

The first `pytest tests` run passed 5,385 tests / 685 subtests with six skips and
six upstream warnings in 392.35s, exit 0. It predates the review corrections and
is not final-code verification. The corrected-code full run at `7d1b0fe` passed
**5,388 tests / 689 subtests**, with six skips and six upstream warnings, in
359.99s, exit 0. It used the same existing offline environment, external
basetemp/TEMP, Docling caches/assets and MODELS_DIR. No dependency, lock or asset
changes were required. Full-suite logs and exact exit metadata are retained.
The existing cached converter tests execute their synthetic fixtures; replay
loads only the tokenizer and makes no new embedding/model-weight calls.

The single fresh whole-change reviewer inspected `ff53c65..d0f996e` and separately
ran 80 focused tests / 161 subtests. Two Important findings were reproduced by
the implementer before correction: generic chunk IDs could overstate availability
when only a footnote rendered, and malformed transport version objects could
crash citation assembly. Both are corrected at `7d1b0fe` and covered by the
106-test focused GREEN result above. Generic fields now require literal value/
source-span text and its source locators in actual evidence; marked records keep
their already validated whole-field codec. Missing rendered fields are explicit
in the nested report. Non-dictionary version objects fail binding before assembly.
No second review was requested; no Critical or Minor findings were reported.

The reviewer declined source correctness/currentness, actual database
authorization, NLP intent inference, calibration and Phase 05 completion.
Ruling: retain these as separate unfinished boundaries, with explicit
false/unassessed flags and inactive output. The consequence of misreading those
limits would be treating candidate evidence as approved institutional guidance.

## Remaining Phase 05 work

This increment implements a conservative source/claim gate in actual retrieval;
it does not adopt a calibrated default or finish formal Tasks 4/6. A matching
snapshot release ID is a consistency check, not source authority or verified
runtime release membership. The governed loader/real-role release verification,
selected-policy calibration and source/release governance retain their gates.

The owner's requested technical estimate remains roughly 80% (75–85% range),
not a measured weighted completion value. Core retrieval already existed; this
increment integrates its claim checks. Do not reopen accepted wordings, repeat
curriculum sweeps or use another sidecar to fill unavailable source content.
Preserve F04/G01/original G02 and all known source limitations. Phase 05 remains
active/blocked; candidate output remains inactive, and no Phase 06 begins.

## Evidence closure and next action

The 26-file raw seal verifies with SHA-256
`115d92e7544bb5b550ba944c6f87342741441ec918cb307b07d58aef00a1ad6b`.
It covers top-level evidence and the corrected replay, excluding test temporaries.
The prior 41-file document-comparison seal also verifies unchanged. Both roots
are now read-only; never rerun their writer scripts. Closure-only checks/logs
use the separate ignored `p05-source-aware-policy-closure-20261016/` sibling.

Next reconcile the selected policy's calibration and governed source/release
loader requirements using the existing evidence, then verify the applicable
runtime/database path when its prerequisites are available. This is further
Phase 05 work, not a new curriculum sweep, source-content approval or Phase 06.
The p05 branch/worktree stays in place for that continuation; owner artifact
changes remain unstaged. Final document/phase-ledger checks are recorded in the
active checkpoint and current progress.

Closure preflight: 501 documentation/phase-ledger tests / 11 subtests pass in
13.06s, exit 0; phase validate0/can-advance1 (expected blocked), continuity links,
verified-code/owner-change preservation, whitespace and read-only seals pass.
The final same-suite closure output stays in the separate closure sibling.
