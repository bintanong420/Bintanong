# Approved natural-query observations — 15 October 2026

All **18 approved query variants** now have real offline retrieval observations.
At exploratory k=3 / similarity 0.5 / 2,048 tokens, all three languages recover
complete expected evidence for both the lost-sticker and special-class questions.
The 30 previously scoped positive controls retain complete recovery. This is
evidence recovery, not generated-answer accuracy or a calibrated runtime policy.

Product commit: `feaa961`. Acceptance: `efe67ad`; bounded plan: `d3723bd`.
The [execution plan](2026-10-15-approved-natural-query-evaluation-plan.md) and
[approved packet](2026-10-15-natural-query-review-proposal.md) preserve exact scope.

## Owner decisions applied

The owner approved the exact revised six scenarios / 18 English, Filipino and
Taglish variants at `bb57f66`, including their stated expectations. Snapshot
SHA256: `4ae2e5cdc7213d9127470c9fb2531d5ab328f2a020218c383f33a950e755b361`.
The earlier 12 scenarios / 36 variants remain unchanged, including the distinct
exact thesis CC5 wording and its approved paraphrase.

Two actual follow-up replies settle the selected source prerequisites:

- **U1:** “Confirm this office/context reading and undergraduate research use”.
  G2 section II.B.1/3 names the PSU Security Services Unit for vehicle-pass form
  and submission context. Two full contextual paragraphs are now bound to exact
  original-pixel rectangles. Use that named office for clarification of the missing
  replacement price; do not derive a replacement workflow or price from it.
- **U2:** “Confirm undergraduate research applicability with existing limits”.
  The confirmed August 4, 2023 examples may be used for undergraduate special-class
  research. This settles selected research applicability, without reopening F1,
  resolving F04 or verifying school authority/current-year validity.

Separate derivatives select V01/V05/office and F01/F08/F09: **six inactive candidates
/ 15 scalar fields**, including two new office-context fields. Original unknown
bundles, review events and prior seals remain unchanged. No active release exists.
F04 is not selected. G03 alone remains confirmed; G01/original G02 are unconfirmed,
the separate ASG physical23 clause stays excluded, and no college-local files are
inferred. Unknown per-student division and replacement price remain unavailable.

## Small codec addition

The existing reviewed-policy codec supported source cutoffs, malformed conditions,
deadline conflicts, printed discrepancies and unknown effectivity. It could not
carry an otherwise relevant clause's unstated requested claim. `feaa961` adds the
single explicit issue kind **`claim_not_stated`** to that existing vocabulary.

Default refusal and opt-in behavior, legacy/compact formats, original field/span
validation, unknown-scope refusal and source-governance flags remain. A synthetic
integration regression verifies the limitation survives cited context without
inventing an amount. Selected missing-claim gaps are normalized to exact existing
located field values in new derivatives; original gap records are preserved.
F09 also carries unknown current-school-year validity. No runtime caller, automatic
interpreter, source-admission rule or ranking algorithm was added.

## Retrieval observations

The run reuses **21 source vectors and 36 query vectors** and encodes only six new
payloads and the 18 approved questions. The corpus has 27 inactive candidates.
Exact embedded payload sizes are F01 446, F08 59, F09 377, V01 111, V05 306 and
office context 363 tokens; all fit the pinned SEA-LION 512-token limit.

| Scenario | Three-language observation | Interpretation limit |
| --- | --- | --- |
| U1 lost sticker | Replacement clause ranks first in all three languages, cosine 0.708744–0.727419. Complete three-candidate evidence fits at **1,480 tokens**. | Context retains the unavailable replacement price and missing replacement workflow; P50 remains the application/sticker payment. |
| U2 special class | F01 ranks first in all three, cosine 0.583701–0.635172. Complete F01/F08/F09 evidence fits at **1,629 tokens**. | The printed P20,000, hours/rate, date/effectivity and unknown individual assessment remain; no official P2,000 bill is generated. |
| S1 Law | Raw top matches are undergraduate overload evidence, cosine 0.533567–0.641978. | Explicit researcher-supplied professional-program context traces the required scope notice. Automatic scope recognition is **not measured**. |
| S2 employment | Raw top matches are unrelated pre-enrollment/vehicle evidence, cosine 0.550392–0.600773. | Explicit researcher faculty/employment context traces the required notice; no employment records are added. Automatic recognition is **not measured**. |
| A1 “TC” | Raw top matches vary between tourism and vehicle evidence, cosine 0.525233–0.555817. | The approved ambiguity trace requests clarification. No expansion is inferred from these scores; no acronym-interpreter accuracy is claimed. |
| P1 BSIT CC5 | Raw retrieval ranks the proposed BSCS CC5 row first in all three, cosine 0.560770–0.617450. | The existing selector returns unavailable for BSIT in the selected eight-row set. This makes no claim about the complete BSIT curriculum. Its 2018–2019 context is separately supplied as approved prior request context. |

The complete U1/U2 evidence and 30 old scoped positives are recovered at the focus
setting in all applicable language variants. Primary-ranking recall@3 differs from
complete-context recovery: U1 is 0.777778 and U2 0.444444 because required source
dependencies also supply context. Primary precision uses the existing fixed-k
denominator; required neighbors are reported separately and are never inserted
from expected-answer labels.

U1 spans separate original image versions. The evaluator checks complete evidence
recovery without inventing a cross-version service binding. Existing same-source
dependencies join V01 with office context and the three fee readings. All source
citations remain tied to their own original bytes and geometry.

U2's focus contexts contain only complete expected evidence, while also reporting
budget refusals for additional unrelated candidate groups. These retained budget
messages are not hidden: this report does **not** claim a successful end-to-end
`RetrievalEngine` status. At 4,096 tokens U2 admits extra unrelated material and
uses 2,518–3,558 tokens, without improving the already complete expected evidence.
Across all observations there are no invalid-context gaps; refusals are budget-related.

## Measurement boundary

The run records 1,458 cosine scores (54 queries ×27 candidates), 1,350 ranking-case
measurements, and 1,350 context observations across k3/5/8, thresholds
0/0.25/0.5/0.75/0.9 and 2,048/4,096-token budgets. Metrics use 45 cases: 30 old
scoped positives, six U1/U2 variants, six explicit audience negatives and three
P1 variants. The three A1 variants receive diagnostic rankings and clarification
traces, not misleading empty-retrieval success labels. Six prior BSCS curriculum
holds remain separate and unchanged.

At threshold 0.5, raw retrieval returns three unrelated candidates for **each of
the nine S1/S2/P1 variants**. Explicit scope annotations or the existing curriculum
selector prevent that evidence substitution in the controlled traces. Those
annotations are inputs, not an automatic language-classifier result. No global
threshold is selected from these easy scope controls or partial-information cases.
Missing-claim handling requires claim coverage as well as semantic relevance.

This run does not test automatic date-based source selection, institutional
supersession, student-answer generation, source completeness across the university,
or the later NLP/router behavior. The owner's natural-query, short-reference and
latest-applicable-source requirements remain binding future behavior. A newer
unrelated document is not evidence of precedence for the same claim.

## Verification and recovery

- **TDD RED:** two expected failing subtests for unsupported legacy/compact issue
  kind; one parent test passed, 32 deselected, 0.51 seconds.
- **GREEN:** 94 related tests /124 subtests, 1.95 seconds, exit0.
- **Full offline suite:** **5,286 passed /510 subtests**, six skipped and six existing
  warnings, **344.68 seconds**, exit0. No installs or dependency changes.
- **Independent replay:** all 1,458 scores, 1,350 ranking measurements and 1,350
  exact context observations reproduce. All 18 strings match the approved snapshot;
  28 unique contexts /432 archived citation bindings resolve. All 235 preserved
  input hashes, including all 62 originals, match.
- **One fresh-context independent review:** no Critical/Important/Minor findings;
  33 focused tests /44 subtests pass in0.73 seconds. Six candidates rebuild exactly
  from original sources/events/spans and input immutability passes. No second review
  or full-suite/model rerun was performed.

Existing Python3.13 environment:
`audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
Tests use `-B -m pytest`, `-p no:cacheprovider` and unique ignored external basetemp.
Full command: `pytest tests -q -p no:cacheprovider --basetemp <newroot>/pytest-full --tb=short`.
Six related modules cover policy/record/service/flowchart/descriptive/retrieval
context. No models were downloaded; existing assets under `C:/Coding-projects/MODELS`
were hash-verified by the strict local encoder. Existing compatible vectors were reused.

Initial data-script parsing assumed every expectation heading was literally
“Expected:”; P1's actual approved heading differs. Corrected that caller assumption
without changing questions or expectations; initial attempt retained. The independent
checker initially counted two tokenizer special tokens for an empty context, while
the established context contract returns zero without invoking the tokenizer.
Corrected the checker; no product or saved observation changed. The >512 tokenizer
warning came from measuring assembled contexts; all embedded payloads fit 512.

Ignored evidence root:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-approved-natural-query-evaluation-20261015/`.
It contains exact source decisions, selected bindings/candidates, query packet,
new vectors, unchanged-input inventory, scores/metrics, context/token archives,
raw TDD/full-suite logs, independent replay and the reviewer result. Original
sources and earlier seals are unchanged; private/raw artifacts stay untracked.

Thesis physical17–18, routingPNG, master10, active plan/checkpoint, dataset guide
and scope/gap/service policies were consulted. No scope/routing discrepancy.
Owner artifact deletion and untracked backend artifacts remain untouched.

## Exact next action

Continue Phase05 with a bounded context-selection diagnostic on these unchanged
approved questions and saved vectors: distinguish missing required evidence from
budget refusals of additional unrelated groups, and document the effect on the
retrieval outcome before selecting a coverage policy. Do not remove material
source limits or use gold evidence as a query hint. Preserve explicit audience /
curriculum /ambiguous-entity boundaries and the distinction from later automatic NLP.

Broader representative in-scope unsupported evidence, calibration and source
governance remain formal exit prerequisites. Any newly proposed benchmark wording
needs separate owner review. School verification remains pending without blocking
ordinary provisional development. F04 remains held; no runtime, DB, Prolog, source
activation, answer-generation claim or Phase06 advancement follows from this run.

## Closure and evidence seal

Final documentation/ledger verification: **470 passed /11 subtests,13.97 seconds**,
exit0. Phase-state validation passes; can-advance returns1 as expected for the
blocked Phase05 handoff. Whitespace and report/plan local links pass. Product
feaa961 remains unchanged after its full-suite pass and independent review.

The new raw evidence seal covers **43 files**, excluding pytest temporary trees.
SHA256:`0780291a6e5e167bc9cbaafafe19175ca8c35d0487db4c620a93166698143249`.
The separate exact-acceptance snapshot seal covers three files,
SHA256:`6b5e01da7206d3d71869f61ab04a760da39967179a832241100963bc8d6372ae`.
Both seals verify read-only. Do not rerun writing scripts in either sealed root;
future diagnostics must write to a new ignored evidence directory. Exact local
package versions and model/configuration fingerprints are preserved with the run.
Only eight explicit curated report/plan/continuity files enter the following
Conventional Commit. Owner artifact changes remain unstaged. Checkpoint names
parentfeaa961; the following documentation commit is discoverable in Git.
