# Saved-vector course-filter comparison — 14 October 2026

The reusable course selector reproduces the CC5 diagnostic and preserves the
existing curriculum-only results. It needs a separately supplied target-code role;
it does not infer one from a course title or a question comparing two codes.
No product code, vectors, questions or source content changed in this experiment.

## Coverage and ranking results

All36accepted English/Filipino/Taglish wordings and their saved query vectors were
preserved. Eight saved source vectors bind to the same reviewed chunks and text
hashes. The144recomputed cosine dot products reproduce the baseline exactly.
Program/curriculum restrictions also reproduce the prior default observations.

| Existing question variants | Curriculum-only default | Strict course helper |
| --- | --- | --- |
| Architecture,3 | Expected evidence ranks first | Explicit `AD-2/L` hint matches the same row |
| Nursing/Tourism,6 | Expected evidence ranks first | No literal code hint; `needs_target_course` |
| Criminology,3 | Expected evidence ranks first | Two-code comparison; no single target selected |
| BSCS CC5/practicum,6 | `needs_scope` | Same curriculum clarification |
| Handbook/Charter,18 | Applicability unresolved; unranked | Same applicability hold |

The default keeps **12/12positive top matches**. Strict single-code coverage is
**3/12(25%)** among those scoped positives; its9missing-target results describe
input coverage of the optional helper. They do not make title-based queries
unanswerable through the existing semantic path, or measure its unsupported-policy
detection. Researcher hints use exact requested fragments in Q2(`CC5`) and
Q8(`AD-2/L`), independently of gold rows. No code was derived from expected evidence.
Criminology's two mentions do not authorize choosing the first mentioned code.

The12existing BSCS controlled edition branches remain researcher hypotheses, not
student metadata or12new questions. The6CC5branches reuse3accepted questions under
old/proposed editions: expected-course top1 improves **5/6to6/6**. The6practicum
branches preserve their default rankings but have no code hint for the strict
helper. The actual6BSCS questions still require the student's curriculum.

The exact thesis question “Pwede ko bang kunin ang CC5 kahit bumagsak ako sa CC4?”
already ranked CC5 first. The repaired mismatch remains the accepted Taglish
paraphrase in the old-edition hypothesis; its saved score and wording are unchanged.

## Metrics and complete contexts

The existing k=3/5/8 and exploratory threshold grid0.0/0.25/0.5/0.75/0.9 produce
405case measurements:180unfiltered,180default scoped and45strict-filter measurements
over its3eligible Architecture cases. The first two groups equal the prior metrics
exactly. The third has a different, conditional denominator and cannot establish
improvement over all12positives. No global threshold was selected or negative
institutional-case detection score produced. Scores remain cosine observations,
not correctness probabilities.

At threshold0.5 the12default positives retain recall1.0 for each k; fixed-k precision
remains1/3,1/5or1/8 when only one row is returned. The3strict eligible variants have
the same values on their narrower coverage. Nothing pads output to k rows.

The current context builder reproduces **21complete contexts/267citation bindings**:
12default,3strict Architecture and6controlled CC5contexts. These reuse question/
evidence pairs across modes and editions, not21independent student cases; there are6distinct complete strings. Each
complete serialized string equals its saved counterpart. Exact token counts are
reused only for identical complete strings: **1209–1680tokens**, all within2048.
Full field associations, source/version/page locators and limitations are preserved;
no clause or citation was truncated to make a context fit.

## Verification and recovery

Plan `4612f13`; product/helper remains `f9b1502`, last closure `80d66b6`.
Existing focused checks: **46passed/82subtests,3.60s**, using approved Python3.13
with pytest `-q -p no:cacheprovider` and external basetemp. The command covers
`test_candidate_course`, `test_candidate_curriculum`, `test_retrieval_context`,
`test_retrieval_evaluation` and `test_retrieval_query`.
The prior full5236test run is historical; this experiment did not repeat it because
product behavior is unchanged. One independent verifier found no Critical/Important/Minor issues:36strings/
144dotproducts/405measurements/315aggregates/267citations/1369hashes checked.
It counted6distinct complete context strings among the21replays. Final
documentation/ledger:458passed/11subtests,10.74s. Phase validation exits0;
advancement exits1 as expected while formal gates remain open.

The run verifies **1369preserved dependency hashes**, including both previous seals,
and resolves six original PDF paths through the byte-exact relocation map. Reviewed
preparation rebuilds the same8row index/catalogue without changing inputs.
Question/vector/text identities, source register versions and helper code digests
remain bound to the preceding evidence. Source governance and school validation
remain pending under standing provisional research authorization.

Raw evidence stays ignored at
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-course-filter-ranking-comparison-20261014/`.
`run_comparison.py` records hints, all36statuses, all12controlled branches, rankings,
metrics, contexts, hash inventory, input bindings and `comparison-summary.json`.
Complete question wording and target-hint origin are retained in the raw records.
No source conversion/model execution/download, database/runtime/Prolog/activation,
answer generation or Phase06 advancement.

## Next action

This saved-vector comparison is complete and should not be repeated merely after
a session change. Remaining Phase05 work includes handbook/Charter applicability
and governed relevance/coverage calibration. If policy applicability requires new
judgment, prepare a focused packet for the six already accepted policy scenarios,
showing the exact original pages/fields and proposed applicability treatment.
Keep settled transcriptions, source gaps, accepted questions and curriculum reviews
closed. Do not reopen school verification while its response remains deferred.
Title-to-code and multi-code query-role handling belong to the later intent/entity
work; the narrow helper must not be represented as that completed pipeline.

Actual thesis physical17–18, routing PNG, master section10, active/prior handoffs
and scope/source-gap/dataset policies were consulted; no discrepancy. Owner artifact
changes preserved. Formal Phase05 exit and Phase06 prerequisites remain open.

Evidence seal:22files/seven unchanged code digests; manifest SHA256:
`72808649d9f1872477f59ddfb28c0910dd96541dfa063e14797f8816661f7455`. Curated documentation only is committed;
raw evidence and original PDFs remain untracked.
