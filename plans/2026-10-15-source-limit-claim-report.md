# Source-limit claim reporting — 15 October 2026

The optional offline report can expose an existing source limitation without
mistaking a matching subject or complete context for an answer. In the saved nine
cases, all three T2 variants match the fee memo's existing current-year limitation;
the deadline and GCash claims remain unassessed. This deliberately does not claim
that all nine unsupported cases are detected automatically.

Baseline `85986fd`, plan `3af3052`, product `c86333b`, prior product `5cd5120`.
[The bounded plan](2026-10-15-source-limit-claim-report-plan.md) follows
[the source-subject increment](2026-10-15-candidate-subject-selection-report.md).

## Behavior and trust boundary

`candidate_claims.build_candidate_claim_report` validates the existing complete
subject catalogue against the current chunks. An explicit researcher subject and
requested claim string are required. The function matches that string exactly to
existing unresolved `source_limits[].affected_claims`; case, substring and field-name
similarity cannot establish a match. Matching claims are `not_established` and the
report says `insufficient_evidence`. Unmatched claims remain `unassessed`; there
is no affirmative support result. Missing claims cannot pass vacuously.

The report copies declared limits from the whole selected subject snapshot,
including limits whose chunk was not retrieved. Each record explicitly identifies
its chunk/reading and whether the supplied emitted IDs contain that chunk. Missing
context IDs mean unknown emission, while an empty list means no IDs supplied as
emitted. Literal IDs do not certify serialized text or citations. Other-subject
context IDs remain visible. Unknown/duplicate context IDs, stale payloads and
malformed/foreign limit identities are rejected.

All results remain candidate-only, inactive and runtime-unimplemented. This uses
trusted source-review metadata, not source-content verification, semantic claim
inference or authentication. It cannot discover an undeclared gap, certify an
answer, resolve a source conflict, verify a school year or authorize payment.
The engine, context builder, queries, public contracts and curriculum selectors
are unchanged. Existing context-selection reports retain unknown claim coverage.

## Saved-context observations

The new source-side vocabulary and researcher claim templates were frozen before
loading accepted cases or saved attempts. T2 uses the exact existing F09 phrase
`current-school-year institutional validity`. T1/U3 receive descriptive caller
claims with no fabricated source-limit match. No benchmark `source-claim-labels.json`,
gold context IDs or expected behavior were consumed by the helper or preparation.
These caller annotations are conditions, not measured automatic NLP.

The sidecar run covers 944 raw and 486 subject-filtered saved attempts: 1,430
reports, with 37 controls. It makes zero model calls and does not rerank, assemble,
encode or edit a context. Independent checks confirm all 1,430 statuses, source
limit copies and emission traces against the unchanged snapshots.

| Selected request | Raw attempts | Subject-filtered attempts | Claim outcome |
| --- | ---: | ---: | --- |
| T1 deadline | 324 | 138 | unassessed |
| T2 current-year validity | 320 | 180 | declared limitation; insufficient evidence |
| U3 GCash permission | 300 | 168 | unassessed |

All 500 T2 reports retain F09's limitation. In 223 of them, the source chunk
carrying it is absent from the emitted context IDs; the report preserves that
distinction. At k3/.5/2048/all primaries, raw T2 context contains that chunk in
one language variant, while subject-filtered context contains it in all three.
This changes neither the source finding nor the existing retrieval observations.

Empty context does not erase T2's limitation. Missing/unknown subjects and unknown
claims stay unresolved. The saved wrong-subject control remains unassessed.
No missing field becomes zero, free, permission, prohibition, expiry or approval.
T1/U3 still need a principled claim-assessment design; benchmark labels must not
be promoted into runtime inference to make those cases appear solved.

## Verification and recovery

Synthetic missing-module RED observed (exit2); focused GREEN: 89 tests and
189 subtests passed in 3.59 seconds. Independent stdlib verification bypasses the
new helper: 1,430 reports/37 controls/500 matched-limit references, 27 catalogue
bindings, 413 preservation hashes and 14 code/test/doc digests pass.
Full offline suite: 5,353 tests/622 subtests pass in 365.95 seconds, exit0,
with six skips and six existing warnings. Command: existing Python3.13 venv,
`-B -m pytest tests .agents/skills/bintanong-phase-handoff/tests -q -p no:cacheprovider
--basetemp <audit-root>/pytest-full`. The single final independent review found no
issues: fresh 75 tests/159 subtests pass in 1.90 seconds, plus all sidecar/control/
source identity/preservation checks and extra synthetic edge probes. Its review
records that the full suite was still running at review time; the parent verified
the completed full-suite log/exit file before committing the unchanged product.

The final 25-file top-level evidence seal is verified; pytest temporaries are
excluded. Manifest SHA256:
`7e82de3b73ed40530225d239990689546a4cc1484588692234785f469963fed1`.
Manifest: `<audit-root>/evidence-manifest.json`; read-only check:
`python -B <audit-root>/close_evidence.py verify`. The final review is in sibling
`p05-source-limit-claim-review-20261015/final-review.md`. Both bounded plan tasks
are verified; formal Phase05 exit remains blocked.

Raw scripts, annotations, reports, preservation inventory and checks are ignored
under workspace `audit-evidence/p05-source-limit-claim-report-20261015/`.
Never run writing scripts in a sealed evidence directory. Originals, prior seals,
vectors, accepted 9/18/36 wordings, external weights and owner artifact changes
remain untouched. No installs, dependency/DB/API/runtime/Prolog changes or activation.

Next design independent source-side assessment for undeclared missing and positive claims
without feeding benchmark expectations into inference. Positive support,
representative calibration, source governance and formal Phase05 Tasks4/6 remain
open. F04 held, G01/original G02 unconfirmed, G03 only and excluded ASG provenance
remain unchanged. No Phase06 advancement.
