# Question-parts reference evaluation results

20October2026;Phase09 active. Plan8b9457f/product4f39833. This is detached offline
evaluation,not runtime selection or a fix for the saved actual-model omission.
[Plan](2026-10-20-question-parts-evaluation-plan.md) ·
[Foundation and limitations](2026-10-20-question-parts-results.md).

## Delivered capability and boundary

evaluation/question_parts.py supplies QuestionPartsReference,QuestionPartsScore
and evaluate_parts. A separately frozen synthetic-dev author reference binds its
full question plan and expected mappings to the request,release,language,complete
source cards and draft. Candidate validation reuses the existing ledger;reference
identity and claim membership are checked before scoring. Structured/unknown
reference requirements cannot be labeled answered by documents in this RAG-only path.

Requirement matching uses exact original spans and kind,ignoring r-number/order.
Mapping compares status/reason and claim sets;claim order is irrelevant. Precision/
recall are explicitly exact-span-and-kind agreement,not automatic semantic recall.
Mapping recall counts ALL reference parts,including unextracted parts. Different
valid boundaries or claim combinations need explicit human adjudication and a new
preserved reference version. Existing support failures still prevent agreement.

agrees_with_reference can be true for correct uncertainty while the ledger stays
unresolved. false_complete_against_reference exposes a mechanically positive ledger
that disagrees with frozen labels. Every score is candidate-only,no institutional
use/activation,semantic_completeness=unverified. No extractor,classifier,inference
caller,renderer,LLM prompt or Generator/profile change is delivered here.

## Frozen saved-output characterization

Raw:workspace/audit-evidence/p09-question-parts-evaluation-20261020/.
score_saved.py reuses ONE saved actual-model draft and the prior three AUTHOR-
CONSTRUCTED plan/review variants,plus one explicitly constructed uncertain control.
It reconstructs RAG integration from the saved pin,retrieval ID and complete cited
cards;prepared cards match exactly. All saved input hashes are checked. No new
model/service/DB call,no new institutional question and no old evidence modification.

Author labels are post-hoc development judgments about the known failure,not
blinded evaluation,independent human adjudication,owner/school approval or model
output. reference-author-labels.json is written before scoring and hash-checked
throughout;SHA2560754b6402bb7dc19912538710d18f5077ea63c8e16b30cee6c17ddcffe5ce755.
It expects location->c1 and fee->uncertain because this draft omits the fee. The
source fee40tokens is known;uncertainty here is an unanswered draft part,not a
source gap or unknown fee. These labels do not modify the actual saved response.

| Candidate variant | Span/kind matches | Correct mappings | Reference agreement | Mechanical false completion |
| --- | --- | --- | --- | --- |
| Declare both;omit fee mapping | 2/2 | 1/2 | false | false;ledger unresolved |
| Omit fee extraction | 1/2 | 1/2 | false | true |
| Wrong fee->location claim | 2/2 | 1/2 | false | true |
| Constructed uncertain control | 2/2 | 2/2 | true | false;ledger unresolved |

All4expectation checks pass;the two mechanical false positives are exposed against
the reference. This is scorer characterization,not four actual model/extractor
successes. saved-output-scores.json retains full scores/input hashes/origin labels.
Actual extraction/per-language/model accuracy NOT RUN;the old semantic P2 stays open.

## Verification and review

Readiness Python3.13.7,-B -m pytest -q -p no:cacheprovider;ignored TEMP/TMP/basetemp.
- RED35expected missing-module assertion failures1.43s/GREEN35passed0.72s.
- Relevant generation/evaluation regressions603passed6.81s,exit0;exact selection
  retained in relevant-selections.txt,output in relevant.log.
- One fresh reviewac94a4a..4f39833:no actionable findings;122passed1.17s,exit0.
  reviewer/review.json/tests.log retain evidence. No fix pass or re-review needed.
- Explicit56-selection gate2193passed/66subtests92.41s,exit0;exact selections/
  command in verify-regressions.ps1,output in final-regressions.log. No product
  changes afterward. No unrestricted project-suite or actual-model accuracy claim.

Reference input identity does not hash expected annotations. The parent receipt
therefore preserves the full frozen reference SHA256 above;future callers must
retain that artifact/hash too. Hash binding is provenance,not proof of label truth.

Delivery manifest seals20fixed source/reference/score/review/test receipt files:
SHA256d41e89334d19c522de4f2c59e61b2fbd746b8f69f91c55ed8ff9fb9d3f4c762d.
source-product/ preserves evaluator/test/guide and ledger dependency;the retained
verification-commands.json includes executed selections/flags. Later documentation-
only logs are explicitly excluded from this seal. Prior foundation16sealed files
and coverage103sealed files verified unchanged,including their manifests:
61bce1225350974db2f1887e031accaba34e24b658c7fa03546259a53dfa89f9 and
99b01941513be459dfe3714618174c07ee552f91d42796902240f6ced5741003 respectively.
Docs/phase gate623passed/14subtests13.74s,exit0.94local links/active snapshot
caps pass;historical123line handoff remains unchanged4022711 with its inherited
3line exception. Phase valid,active9,cannot advance.

## Preserved boundaries and next action

Selected scoped/canonical/separate unchanged;guarded/covered remain unselected.
No installs/downloads,model copy,dependency/lock/DB changes,training,Phase10,push,
merge,deployment or institutional activation. Undergraduate/read-only,structured
Prolog,unknown/source-gap/privacy/release gates and one-week accuracy cap persist.
Thesis17-18/39-44,actual routing PNG/master3/11/12.4/13/14 reconsulted;no discrepancy.
[Saved timing recommendation](../Context/response-time-recommendation.md) is unchanged:
proposed15-20s warm student-visible,conditional20-30s complexHybrid,accuracy first.
No new latency,connection/Supabase/browser/network/queue measurement or SLA claim.

Next:define a single frozen extraction/per-part-review observation using existing
transport and synthetic dev labels;validate actual outputs separately before any
runtime integration. No repeated failed prompt/model/seed/budget sweep. The current
scorer's bounded question is resolved;do not expand this characterization further.
