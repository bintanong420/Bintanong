# Source-bound candidate subject selection — 15 October 2026

With explicit researcher caller subjects, all six accepted fee-related variants
retain their complete fee context at2048tokens, compared with1/6in the preserved
raw run. This is conditional context recovery, not automatic subject recognition
or evidence that a requested claim is supported. The deadline/current-year/GCash
claims remain unestablished. Runtime behavior and activation are unchanged.

Plan `3b7c549`, product `5cd5120`, baseline `245fd73`/prior product `7456613`. Implements
[the bounded subject plan](2026-10-15-candidate-subject-selection-plan.md) and the
[verified temporal-query next action](2026-10-15-temporal-unsupported-evaluation-report.md).
No new benchmark wording or source decision; accepted9/18/36questions and all
saved source/query vectors remain byte-identical.

## Catalogue and selector

The new `candidate_subject` module builds a metadata-only inactive catalogue
from complete candidate chunks and trusted researcher assignments by source
reading ID, subject ID and provenance reference. Complete JSON payloads,
source/version/reading IDs, audience and dependencies are bound by hashes.
Current inputs must match. Every assigned dependency must share the subject;
cycles are allowed but incomplete or cross-subject groups are rejected.

Explicit canonical subject selection returns matched IDs, needs_subject or
unavailable. Missing/unknown hints never select all candidates. Each result
retains `claim_coverage=unknown`, metadata-only validation, candidate/inactive
flags and runtime_filter_implemented=false. No query parsing, source-age choice,
year validation, source-content approval, citation certification or public/runtime
interface change. The digest detects accidental changes, not forged trusted input.
Current engine/context/query/public contracts/DB and curriculum selectors are
unchanged. Unknown curriculum still requires its existing clarification.

The frozen catalogue binds all27existing chunks. Nineteen policy rows are mapped
to seven subjects using their **existing reviewed applicability-area provenance**
and source fields, before loading queries or gold. Eight curriculum rows remain
explicitly unassigned. Aliases are researcher metadata, not new owner approvals.

| Subject | Assigned selected rows |
| --- | ---: |
| grading_scale | 1 |
| overload | 5 |
| pre_enrollment | 2 |
| grade_completion | 4 |
| academic_misconduct | 1 |
| special_class_fees | 3 |
| vehicle_pass | 3 |

Catalogue SHA256:`4eb59c7ab9d78e31d161c93e7c5b0a98c62a4246c0247465cdbac0d3195a8061`.
No gold chunk IDs are used as selectors. Accepted utterance topics are explicitly
annotated by the researcher as pre_enrollment forT1and special_class_fees forT2/U3.
This is a trusted caller condition; students are not asked to identify a memo.

## Saved-score comparison

The diagnostic reuses all243scores/27document vectors/ninequery vectors. It filters
by subject before threshold/top-k and preserves complete declared dependencies.
It records486prefix attempts/270strategy configurations/sixcontexts in4.273seconds.
No model calls, re-encoding, conversion, new questions or source edits.

At k3/.5/2048 all six fee variants return F01/F08/F09 at1629tokens with no assembly
gaps. Raw all-primary recovery was1/6with six gap cases. At4096, raw recovery5/6
becomes6/6with subject annotations. The same counts hold for k5/8; no parameter
default is changed. Both the fee's missing individual-assessment limitation and
its printed2023effectivity remain intact; current-year status/GCash permission
are not established by subject membership or a clean context.

At k3/.5/2048 T1English/Taglish return the two selected Charter pre-enrollment
steps at1576tokens, retaining the known cutoff; Filipino returns no context.
Neither outcome establishes the requested second-semester2026–2027deadline.
This selected corpus is not an exhaustive calendar/source audit.

Eighteen missing/unknown-hint controls return no IDs. A counterfactual technical
probe injects vehicle_pass into the unchanged EnglishGCash question: it returns
vehicle material at1480tokens, still with unknown claim coverage. This demonstrates
the trusted-hint limitation; the module cannot detect a caller's wrong subject.
The probe does not alter the accepted benchmark or measure NLP accuracy.

## Verification and phase position

Synthetic TDD: expected missing-module RED;99tests/134subtests GREEN1.53s.
A defensive unassigned nested-reference test then exposed an alias, reproduced
RED; a one-value deepcopy correction gives100tests/134subtests GREEN1.59s.
Tests cover source/payload/audience/digest staleness, duplicate/malformed metadata,
same-subject dependency completeness/cycles, unknown subjects and nonmutation.

Independent parent verification bypasses both new helpers:27bindings/19assignments/
eightunassigned rows,486original-builder replays/270strategies/948offered traces,
sixcontext hashes/exact counts,43citations/eightsource-limit occurrences pass.
All375preserved input hashes and11unique code/test files match their recorded
snapshots. Prior375hashes preserve the raw944attempts and all earlier seals.
The previous agent's completed full-suite log records 5,323 tests and 574 subtests
passing in 332.04 seconds, exit 0, with six skips and six existing warnings. Fresh
resume checks pass: 47 focused tests/99 subtests in 1.75 seconds, and all 486 direct
replays, 948 traces, 43 citations, eight limit occurrences, 375 prior hashes and
11 code/test digests. No code changed, so the full suite was not repeated.
The single final independent review found no actionable issue. Its fresh 80 tests/
152 subtests pass in 3.62 seconds; it also replayed the 486 contexts and independently
checked source aliases, the accepted-nine caller annotations and all 24 comparison
rows. All 6,336 files already present in the diagnostic root remained unchanged
across the review (including test temporaries); this is preservation accounting,
not a count of reviewed sources.

The final 37-file seal covers top-level raw diagnostic, resume and review files;
pytest temporary directories are excluded. Manifest SHA256:
`d1063ecf6c29b3b7e0bc470682deb81bdf994145e09505d19af33d9f081c9223`.
Both bounded plan tasks are complete; formal Phase05 exit gates remain open.

Raw scripts, source-assignment basis, frozen catalogue, annotated contexts,
rankings, controls, contexts and verification live ignored under workspace/
audit-evidence/p05-candidate-subject-selection-20261015/. Never rerun writing
scripts in sealed roots. Fresh resume evidence and `seal_evidence.py` are in
`p05-candidate-subject-resume-20261015/`; the final read-only review is in
`p05-candidate-subject-review-20261015/final-review.md`, both under the same audit
parent. The seal manifest is `p05-candidate-subject-resume-20261015/evidence-seal.json`.
Run `python -B <resume-root>/seal_evidence.py verify` to verify it without writing.
Owner artifact changes, originals and weights are
preserved; no installs/downloads/dependency/DB/API or runtime changes.

Next design the claim-coverage boundary using reviewed fields/known limits and
explicit caller intent, preserving unknowns and unavailable-information/referral
requirements. Subject membership alone cannot authorize an answer; do not install
a calibrated engine policy from these conditions. Reuse accepted cases/saved
scores, retain raw/wrong-hint controls, and keep automatic-NLP claims separate.
FormalPhase05Task4/6 and school/governance gates remain open. Candidate inactive;
F04held/G01originalG02unconfirmed/G03only/ASGexcluded remain unchanged. No Phase06.
