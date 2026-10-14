# Provisional curriculum retrieval results — 14 October 2026

Real offline retrieval now runs against the eight reviewed undergraduate curriculum
rows while school verification remains pending. The owner authorized this thesis
experiment; no source register approval, release activation or eligibility answer
was created. Plan commit: `c92f51c`; product code remains at `093ea4a`.

## Actual coverage

The existing 36 English, Filipino and Taglish query vectors were reused unchanged.
Eight source payloads were encoded with strict local SEA-LION, no document prompt,
512-token maximum and 1024-dimensional L2-normalized vectors. Payloads contain
286–478 tokens; document encoding took 7.000 seconds, complete execution 26.059
seconds. Model identity and all ten asset digests match the recorded query encoder.
Weights remain under `C:/Coding-projects/MODELS`; no downloads or dependency changes.

| Accepted questions | Variants | Treatment |
| --- | ---: | --- |
| Q8 Architecture, Q9 Nursing, Q10 Criminology, Q11 Tourism | 12 | Real unfiltered/scoped rankings and positive-case evaluation |
| Q2 CC5 and Q12 BSCS practicum | 6 | Unfiltered diagnostics; actual selection requires curriculum clarification |
| Q1, Q3–7 policy questions | 18 | Unranked; source-candidate applicability unresolved |

Scope hints come from accepted case metadata. This experiment does not demonstrate
automatic program/edition extraction from a student's free-text question. Unranked
and clarification cases are excluded from numeric evaluation, not converted into
empty gold sets or successful unsupported-information detections.

## Results and observed failure

All 12 explicit-edition questions ranked the expected row first among all eight
rows, with four successful positives in each language. Correct-row cosine scores
range from 0.605983 to 0.716006. Program/version selection leaves one candidate for
each case, so scoped positive success alone is a weak test. All 12 fully cited
contexts fit 2048 tokens: 1242–1574 tokens, no gaps, 153 citation bindings across
the repeated language variants. Source fields and citation arrays match the prior
complete compact contexts; cosine values are observations, not probabilities.

For the exact thesis question **“Pwede ko bang kunin ang CC5 kahit bumagsak ako sa
CC4?”**, unfiltered ranking is:

| Source row | Cosine similarity |
| --- | ---: |
| Old BSCS practicum | 0.583309 |
| Proposed BSCS CC5 | 0.582294 |
| Old BSCS CC5 | 0.571793 |

The English CC5 variant instead prefers proposed CC5, while the Filipino variant
prefers old CC5. Similarity cannot determine the student's applicable curriculum.
Twelve controlled old/proposed-edition branches reuse the same six BSCS questions
and scores; these are research hypotheses, not additional student metadata or new
questions. Eleven rank the expected course first. The Taglish CC5 question under
the old-curriculum hypothesis still ranks practicum above CC5 (margin 0.011515).
This is a recorded retrieval failure requiring technical investigation. No source
wording, expected evidence or query was altered to hide it.

At exploratory threshold 0.5, recall@3/5/8 is 1.0 for the 12 positive cases in both
modes. Unfiltered retrieval also returns unrelated rows: 24/47/65 false-positive
slots at k=3/5/8. Scoped retrieval returns the sole expected row and no unrelated
row. Precision uses the evaluator's fixed k denominator: 1/3, 1/5 and 1/8 even
when only one row is available. Thresholds 0.75 and 0.9 reject every positive.
No global threshold or runtime policy was selected. Positive-only observations on
eight rows cannot establish negative detection, whole-corpus quality or calibration.

## Verification and evidence

Independent checks reproduce 144 dot products, 360 case/threshold/k measurements,
all 12 controlled branches, 36 unchanged strings and 153 citation bindings. Eight
vectors are finite and normalized; six original PDF hashes, 1302 current dependency
hashes and one exact historical context-code snapshot remain unchanged. The first
verification attempt incorrectly required an optional `span_id` key; the diagnostic
was corrected to use the context contract's nullable value. Both logs are retained;
no product or source defect was inferred from that checker mistake.

Relevant existing tests: **32 passed, 52 subtests passed in 1.71 seconds**. Product
code was not changed; the previous full-suite result remains historical evidence,
not a fresh full-suite run for this experiment. Documentation and ledger verification:
**451 passed, 11 subtests passed in 10.87 seconds**. Phase state is valid;
advancement remains blocked as expected.

Generated vectors, observations, contexts, checks and logs stay ignored under
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-provisional-curriculum-retrieval-20261014/`.
The [complete current question list with observed rankings](</C:/Coding-projects/bintanong_workspace/audit-evidence/p05-provisional-curriculum-retrieval-20261014/ALL-CURRENT-QUERIES-AND-OBSERVATIONS.md>)
shows all 36 accepted wordings and the exact coverage/status of each. Prior packets
and seals remain unchanged. The new manifest digest is recorded in the checkpoint.

## Next action and pending human evidence

Investigate course identity in offline curriculum retrieval, starting with the old
BSCS Taglish CC5 mismatch and preserving all reviewed fields/citations. Compare a
bounded course-code-aware candidate selection with the recorded cosine baseline;
use synthetic TDD for any new product behavior. Do not infer a student's edition
from a similarity score or treat prerequisite-course mentions as target-course IDs.

No new human content verification is required for this completed diagnostic. School
authenticity/current-SY/source-use validation remains deferred until actual evidence
arrives or institutional activation is considered. Existing owner row/evidence/cohort
decisions remain settled. Policy applicability and final Phase 05 gates stay unresolved.
The incoming batch excludes further college-specific Charters and may include
memoranda such as undergraduate vehicle gatepass; no new batch has been processed.

Context consulted: thesis physical17–18 (printed16–17), routing PNG and master-plan
section10. No scope/routing discrepancy; undergraduate read-only advisory scope,
source-gap limits and private-input separation retained. Phase 06 is not authorized.
