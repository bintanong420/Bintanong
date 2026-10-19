# Phase07 residual style review

19 October 2026. Resumed from 9b6df0b with a clean working tree. This completes
the handoff's saved-evidence review, without another inference experiment.
Router-v9/be39e67 and style-v1 remain unchanged; Phase07 remains active.

## Observed errors

The retained 15-case development composition has 15/15 proposed routes and
15/15 effective outcomes, with 13/15 response-style labels. English and Filipino
each pass 5/5; Taglish passes 3/5. Its style outputs were reused exactly from the
explicit-profile baseline, not freshly inferred during the routing evaluation.

| Case | Original synthetic question | Expected | Observed |
| --- | --- | --- | --- |
| procedure-taglish | Paano ako mag-request ng copy of grades ko? | Taglish | Filipino |
| excluded-taglish | Ano ang enrollment requirements para sa master's program? | Taglish | Filipino |

Both outputs leave english_fragments empty and quote the entire mixed question
in filipino_fragments. Their schema, array/label consistency and literal grounding
pass. The accepted style follows the model output; the evidence does not identify
a host projection or repair defect. Literal grounding cannot validate a fragment's
language. The failure is observable semantic attribution; its underlying model
mechanism is not established. The master's question remains a negative scope test,
with the correct unsupported_scope decision. No graduate policy is supported.

## Existing alternatives

| Saved alternative | Style result | Reason it remains retired |
| --- | --- | --- |
| v2 span guidance | 3/5 bounded cases | Both target errors unchanged |
| v3 label-first prompt/schema | 11/15 full cases | Fixes targets but mislabels four pure-language course questions |
| Compact enum-only ablation | 12/15 full cases | Both targets unchanged; prerequisite-fil newly wrong |
| v4 balanced examples | 8/10 completed pairs; baseline 9/10 | No fixes; prerequisite-fil regresses; five outputs incomplete |

The v3 targeted 5/5 result is already superseded by its full-case regression.
The v4 result is partial; it is not an 8/15 estimate. Earlier stage/ablation runs
predate the explicit no-prefix-cache profile, so these are historical engineering
rejections, not a controlled cross-profile ranking or population accuracy study.
See the [stage report](2026-10-19-phase07-style-stage-evaluation.md) and
[explicit-profile comparison](2026-10-19-phase07-prompt-comparison.md).

## Review verification

Ignored raw root:
C:/Coding-projects/bintanong_workspace/audit-evidence/p07-style-review-20261019/.
Existing readiness Python3.13, -B review_saved_styles.py, exit0; review.log.
The read-only verifier checks 212 source-file hashes, including the sealed current
manifest/report, prior stage manifest/artifacts and 21 retired-v4 captures. It
checks all 15 retained styles against their original captures, source-byte seals,
case text, contract and literal grounding, and reproduces the reported error sets.
Historical artifacts were not rewritten. Runtime inspection confirms exited.
Zero fresh model calls; no runtime restart, dependency/model/source/registry change.

review.json SHA256:
b3a6645cfc5ae83c38ddc7e1950f2da0879d1be3d6a289a8b8cd855cdce42d98.
The review verifies saved observations, not new model accuracy or final answers.
Context physical17-18 freshly read with existing pypdfium2; PDF hash matches the
kickoff manifest. Actual routing PNG and master12 inspected; no new discrepancy.
Prior39-44/58-59 and master3/11/13 architecture evidence remains applicable.

Fresh documentation/phase gate:579passed/11subtests11.85s,exit0;docs-phase.log.
Existing readiness Python3.13 -B -m pytest -q -p no:cacheprovider
--basetemp=raw-root/docs-phase tests/test_docs_hygiene.py
.agents/skills/bintanong-phase-handoff/tests/test_phase_state.py; TEMP/TMP=raw root.
git diff --check and phase_state.py validate pass; Phase07 cannot advance.

## Disposition and decision boundary

Keep the stronger verified style-v1 candidate and frozen router-v9. None of the
saved alternatives meets the existing no-regression selection rule. Another
equivalent instruction, example, schema-order or seed trial is not justified.
Preserve both errors and their expected labels; do not fix a score by changing gold,
adding a vocabulary override or counting a valid schema as correct language.

The next owner decision is whether to carry these two observed style errors as
explicit limitations into a Phase07 offline completion review, or keep Phase07
open for a separately justified style-design change. Recommendation: retain the
current candidate and review offline completion with disclosed limitations before
spending more of the one-week accuracy allowance. This is a recommendation,
not owner acceptance, a numerical pass threshold or a completed phase handoff.
No prior approval of the English/Filipino/Taglish requirement is reopened.

Any completion review must still verify all other exits and disclose the small
synthetic sample, reused style outputs, lack of final-answer language evaluation
and institutional holds. Phase08 stays gated; undergraduate/read-only/private/
source-gap/EMPTY_REGISTRY boundaries and the standing prompt decision remain.
