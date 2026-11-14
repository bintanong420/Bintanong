# Composed offline request traces — 16 October 2026

All 63 accepted variants now have one ordered diagnostic trace under each of
the two existing focus strategies: 126 traces total. Audience, entity, curriculum,
subject, context and claim results remain separate. Eighteen variants stop before
claim reporting; the other 45 reach it. No trace establishes answer permission.

Baseline `9916068`, [plan](2026-10-16-offline-request-trace-plan.md) `fbed8b5`,
observations `fa79cb3`, unchanged product `232a418`. This implements the preceding
[partial-claim handoff](2026-10-16-partial-claim-coverage-report.md) as ignored offline
diagnostic scripts. No backend, runtime API, database or routing code changed.

## What is composed

The frozen accepted identities, explicit request context and caller annotations
come from the existing matrix and source-report increments. The diagnostic calls
the unchanged curriculum selector, subject selector and claim report helper.
It consumes the exact preserved catalogues/registers appropriate to each increment;
the policy and curriculum catalogues remain separate. Historical sidecars are not
rewritten or silently upgraded to another register.

Audience comes from the existing explicit negative/request traces or the owner's
standing undergraduate website context. Ordinary users are not asked to supply
their source or declare undergraduate status. That default context establishes no
program, curriculum, grade, eligibility or source authority. The existing requirements
document and original owner-message bytes are separately hashed; its descriptive
`standing-supported-context` provenance label resolves to those recorded sections.

Explicit Law/faculty-employment requests stop at the audience gate. The existing
unresolved TC request stops at the entity gate. Unknown BSCS editions and the
selected-row BSIT absence stop at curriculum selection. These early stops carry
no subject selection, retrieved context or claim report. Raw negative retrieval
controls remain historical diagnostics, not evidence returned by these traces.

Matched curriculum selections must have exactly the same complete chunk set as
their selected curriculum subject. A supplied subject cannot bypass a missing or
contradictory curriculum. Subjects/claims remain explicit trusted researcher inputs;
there is no automatic language or intent recognition.

When reached, the context gate references the exact caller-chosen saved strategy
at k3/.5/2048, including decision/attempt indices, serialized-context byte hash,
copied token count, emitted IDs and assembly gaps. No retrieval, reranking,
encoding or context assembly is performed. Neither focus strategy is adopted
as a default or calibrated policy.

## Observed results

| Trace result | Per strategy | Both strategies | Interpretation |
| --- | ---: | ---: | --- |
| Reviewed fields available | 18 | 36 | Printed reviewed fields present; answer sufficiency unassessed |
| Insufficient evidence | 21 | 42 | Existing source limits/selected-field absence findings apply |
| Unassessed | 6 | 12 | Architecture/Nursing caller eligibility or course-name claims remain unassessed |
| Outside supported audience | 6 | 12 | Explicit Law/faculty-employment request traces |
| Curriculum clarification needed | 6 | 12 | Unknown BSCS edition; no subject/context/claim report |
| Entity clarification needed | 3 | 6 | TC meaning unresolved; no expansion invented |
| Selected program unavailable | 3 | 6 | BSIT absent from selected eight rows; not a university-wide absence finding |

All 90 reached source-claim reports retain `answer_sufficiency=unassessed`.
Eighty-nine match the existing saved report objects exactly, including the
register and catalogue identities. The remaining report is a newly composed
source-limit result for the Filipino T1 gap-free strategy, whose saved decision
selected no prefix. Its context stays `no_saved_prefix_selected` with null
hash/count/emitted IDs. It is not an older report, empty successful retrieval,
or a new observation of model behavior. The existing selected-field absence
review still establishes no requested current-semester deadline.

The seven initial structural metadata probes preserve precedence: excluded audience wins
over later hints; unresolved entity stops before curriculum/subject; unknown
curriculum cannot borrow a subject; a wrong program/version stops; missing and
unknown subjects remain distinct; mismatched matched-curriculum/subject sets
raise an error. A supplemental eighth probe exposed a diagnostic guard gap when
curriculum hints were cleared from a curriculum-kind request. The parent captured
RED, corrected the composer to call the existing selector with empty hints, and
observed GREEN: `needs_scope`/`program_required`, no later evidence. All 126 accepted
outputs remain exactly unchanged. The single reviewer independently verified this
correction. These are synthetic condition probes, not new student questions.

No original source, question, source review, curriculum edition, F04/G01/original
G02 hold, G03 confirmation or excluded ASG decision changes. Replacement price,
workflow, individual bill, timing conflict, cutoff and currentness limitations
remain attached through their existing claim reports.

## Verification and next action

The independent frozen-record audit imports no diagnostic composer. It checks
all 63 exact identities/three languages, every gate's input/order/early-stop
conditions, complete frozen-object copies, prior sidecar pointers, null context,
14 archived byte hashes/copied counts, 599 preserved hashes, 27 input hashes,
two additional website-context provenance hashes and 16 unchanged code/test/doc
digests. Separate current-helper replay checks all 90 claim and 42 curriculum
results. Those replays verify composition with the existing helpers, not an
independent measure of the helpers' semantic correctness.

Raw evidence lives ignored under workspace
`audit-evidence/p05-offline-request-trace-20261016/`. Fresh focused regressions:
46 tests/174 subtests in2.40s, exit0; documentation/ledger493tests/11subtests in15.27s,
exit0. Phase validation, three local links and whitespace pass. The single final
independent review found no unresolved issues and verified the guard correction.
Its replay checks all 126 final-composer outputs, 36 early stops with later datasets
absent, the original seven/supplemental eighth controls and four invalid-metadata/
archive-corruption guards. Parent replay of those checks passes.

The 29-file top-level observation/review seal verifies; test temporaries excluded.
Manifest SHA256:
`42041bfa071e772eb7f6e066a026fda275f33236238348b0f7db2d8ecbc3f131`.
Reviewer artifact: sibling `p05-offline-request-trace-review-20261016/final-review.md`.
Use `python -B <observation-root>/seal_evidence.py verify` read-only; never rerun
sealed writers. Final documentation/ledger493tests/11subtests pass in11.12s, exit0.
Phase validation, three plan/report links plus progress link, whitespace and
read-only seal checks pass; advancement remains blocked as expected.
No product behavior changed, so no new product TDD/full/native run is claimed.
Historical native stderr uncertainty remains unresolved.

Next prepare a representative development-case/calibration proposal from the
remaining coverage gaps and unassessed claims. Any new or changed question wording
and expected behavior must be shown to the owner before testing. Preserve the
accepted 63 cases and all saved vectors. This conditional diagnostic does not
establish calibrated relevance, automatic interpretation, source truth/authority,
current-year validity or institutional approval. Formal Phase 05 Tasks 4/6 and
source governance remain open; candidate inactive, no Phase 06 advancement.
