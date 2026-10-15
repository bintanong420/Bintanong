# Source-bound claim reviews — 15 October 2026

The existing offline claim report now accepts an optional source-review register.
It distinguishes a claim not stated in the selected fields, reviewed fields missing
from context, and reviewed fields present with their required context. Unreviewed
claims and answer sufficiency remain unassessed. The original v1 output remains
identical without the register; the opt-in output is v2.

Baseline `d2906ca`, plan `f9adcd6`, product `232a418`, prior product `c86333b`.
[Bounded plan](2026-10-15-source-claim-review-plan.md);
[previous source-limit report](2026-10-15-source-limit-claim-report.md).

## Source-side preparation and trust

The new audit freezes five existing chunks and all 22 selected source fields
before loading cases, annotations, rankings, expected labels or scores. They are
the two selected Charter pre-enrollment steps and F01/F08/F09. Original transcriptions,
source spans, dates, conditions, cutoff and fee limitations are unchanged.

Three explicit researcher findings bind that complete subject selection:

| Claim | Finding and limitation |
| --- | --- |
| Second-semester2026–2027 enrollment deadline | Not stated in the selected twelve pre-enrollment fields; five-minute processing durations are not an enrollment deadline. The source cutoff remains. |
| GCash permission for special-class payment | Not stated in the selected ten fee fields. This establishes neither permission nor prohibition and is not a university-wide absence finding. |
| Printed three-lecture-unit example | Ten F01/F08/F09 field references, retaining the printed P20,000, hours/rate, date/effectivity and existing source limits. No per-student/class-total or official-current-bill interpretation. |

These are researcher source-side judgments with a hashed separate audit basis,
not newly owner-confirmed source gaps or automatically discovered facts. Source
metadata and semantic truth remain trusted inputs. The register digest detects
accidental changes, not forged reviews, reviewer identity or school authority.
No additional student-question wording was created or tested for the printed example.

## Register and report behavior

`prepare_candidate_claim_reviews` binds the existing complete subject catalogue,
known subjects, the complete reviewed chunk set, exact claims, source-audit hashes
and field refs. Visible fields require present nonblank values, review-event hash
metadata and source/version-matching spans. Partial absence scopes, duplicates,
foreign/blank fields and stale registers fail closed. Nested data is copied.

`build_candidate_claim_report(..., claim_reviews=register)` matches explicit caller
claim text exactly. Existing unresolved source limitations take precedence. A
selected-field absence finding returns `not_established`; an unmatched claim stays
`unassessed`. Visible fields return `reviewed_fields_available` only when their
referenced chunks and transitive required dependencies are supplied as emitted IDs.
Otherwise the result is `insufficient_context`, distinguishing unknown from empty
emission. IDs certify neither serialized text nor citations. Answer sufficiency
stays unassessed, including when all reviewed fields are present.

The register/report are inactive and runtime-unimplemented. They do not parse
queries, choose source authority/currentness, certify answers or alter the engine,
public contracts, original chunks or existing context selection.

## Conditional saved-context observations

All 1,430 saved raw/filtered attempts produce insufficient-evidence reports with
the explicit register/caller annotations: 930 match the two new selected-field
absence reviews, while 500 retain the prior F09 currentness limitation. All 1,430
default v1 reports remain identical to the previous saved reports. No expected
benchmark labels, gold chunk IDs, new embeddings or ranking changes were used.

These results exercise three explicitly authored source-side findings and existing
trusted caller annotations. They are not automatic unsupported detection accuracy,
an independent generalization test or a calibrated runtime policy. All nine natural
requests still depend on future query interpretation; school/source governance and
representative calibration remain separate gates.

The 37 controls retain missing/unknown-subject and unknown-claim behavior. Four
structural printed-example probes report fields available only for complete
context; example-only, empty and unknown context remain incomplete. All ten source
values/spans and both fee limitations are preserved; no fee was calculated.

## Verification and recovery

Synthetic missing-function RED(exit2), initial98tests/236subtests GREEN3.68s.
A mutation regression reproduced shared source-field refs; minimal deepcopy fix
GREEN99/2363.79s. Opt-in v2 regression RED then GREEN99/2363.86s. Independent checks
bypass the helper: three reviews/five chunks/22 fields/ten visible refs, 1,430
sidecars, 37 controls, four field probes, 2,398 copied-limit trace checks, 439 prior
hashes and 15 code/test/doc digests pass. Full offline suite: 5,365 tests and
669 subtests passed in 337.17 seconds, exit0, with six skips/six existing warnings.
Command: existing Python3.13 venv, `-B -m pytest tests
.agents/skills/bintanong-phase-handoff/tests -q -p no:cacheprovider --basetemp
<audit-root>/pytest-full`.

The full log also contains a native Windows access-violation diagnostic near99%
with a Pydantic frame, followed by normal100%/passing summary. This is not clean
stderr evidence. A bounded isolated run of the nearby unchanged synthetic PDF
conversion test passes (one test, three warnings, 18.00 seconds, exit0) without
reproducing the diagnostic. Its exact native origin remains unknown. No failed
test/process, speculative dependency/code fix or duplicate full suite is inferred.
Preserve `full.log`, `native-isolation.log` and `native-observation.json`.

The single final independent review found no issues: fresh 32 tests/125 subtests
pass in 0.43 seconds; all source/register/sidecar/input checks and seven extra
rejection probes pass. It loads the actual `d2906ca` implementation read-only
from Git and independently confirms all 1,430 serialized v1 reports are identical.
Reviewer artifacts are in sibling `p05-source-claim-review-final-20261015/`.
Final documentation/phase-ledger checks: 484 tests/11 subtests pass in 11.40
seconds, exit0. The final 40-file top-level evidence seal verifies; pytest temporary
directories are excluded. Manifest SHA256:
`2856805eb86144c723b2074b0a2523e8038c4fd2b6bc913d4244c7f3c3c5070e`.
Use `python -B <audit-root>/close_evidence.py verify` read-only; manifest is
`<audit-root>/evidence-manifest.json`. Both bounded plan tasks are verified; formal
Phase05 exit remains blocked.

Raw audit basis/specs/register, scripts, reports and checks live ignored under
workspace `audit-evidence/p05-source-claim-review-20261015/`. Preserve old seals,
originals, vectors and owner artifact changes. Do not rerun sealed writing scripts.
No installs/downloads/dependency/DB/API/Prolog/runtime change, activation or Phase06.

Next extend the source-side coverage review to the existing accepted positive
policy cases, using settled field/association decisions and saved vectors. Freeze
source findings before loading cases and keep conditional caller metadata distinct
from automatic interpretation. New ambiguous/consequential source-content choices
require focused owner review. If the native diagnostic recurs, capture a specific
reproducer before a code/dependency change. Representative calibration and final
source governance remain required before any calibrated integration. This bounded
register does not close formal Phase05 Tasks4/6, verify current-year validity or resolve F04/G01/originalG02 holds.
