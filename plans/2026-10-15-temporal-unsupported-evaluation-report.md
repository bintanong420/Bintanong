# Accepted temporal/unavailable-query observations — 15 October 2026

The nine accepted queries reveal a retrieval failure that the earlier approved
questions did not expose. At k3/threshold0.5/budget2048, only **one of six** T2/U3
variants retains the complete expected fee context. All three deadline queries
can produce nonempty, gap-free contexts that do not establish a deadline.
Neither a shorter prefix nor a single similarity threshold resolves this result.
No calibrated runtime policy is adopted; Phase05 tasks4/6 remain open.

Baseline915c795, preflightca41cea, unchanged product7456613. Execute
[the accepted plan](2026-10-15-temporal-unsupported-evaluation-plan.md) using the
[nine accepted wordings/expectations](2026-10-15-temporal-unsupported-query-proposal.md).
Actual owner acceptance binds snapshot
`34529fad525df70d2274f151538ddcecd3bcfb06f50bbc752a6a0ff984d1a5eb`.
Old12/36 and six/18 queries, all original sources and prior seals are preserved.

## Observations and limits

All27document vectors were reused. Exactly nine new queries were encoded by the
existing strict local SEA-LION encoder after asset/configuration checks. Prompted
query lengths46–55tokens and all document payloads59–478tokens remain within512.
The tokenizer warning about longer serialized context concerns counting context,
which was never sent through the embedding model; no input was truncated.

The run recorded243cosine pairs,135ranking configurations,944prefix attempts,
270strategy configurations and18distinct contexts in39.001seconds. It compared
k3/5/8, thresholds0/.25/.5/.75/.9 and budgets2048/4096. All/top1/top2 and the earlier
experimental longest-gap-free prefix are comparisons, not selection defaults.
No source-family/year hints or gold labels were supplied to ranking/assembly.
Expected labels were consulted only after rankings, contexts and strategy choices.

| Cases | k3/.5/2048 observation | Intended interpretation |
| --- | --- | --- |
| T1: three deadline variants | Overload/completion/curriculum or fee content ranks above a supported deadline; the clean-prefix strategy returns unrelated evidence in all three. | Requested second-semester2026–2027 deadline is unavailable in the selected evidence; do not substitute a date. |
| T2: three current-year fee variants | Only Filipino retains F01/F08/F09. English keeps completion rules; Taglish keeps vehicle-payment context. | Even a correct fee-context match would not verify2026–2027 validity. |
| U3: three GCash variants | Vehicle-payment/sticker evidence outranks the fee example; no variant retains its full expected fee context at2048. | Payment-related similarity does not establish GCash permission, a ban, account or workflow. |

For T2/U3 together, all-primary and clean-prefix strategies both recover1/6expected
context sets at2048. The clean-prefix strategy removes assembly-gap messages but
does not improve that recovery. At4096both strategies recover5/6; EnglishT2still
loses fee context after completion/overload groups consume the budget. Increasing
k to5or8does not improve these counts and adds refusals. No new context budget,
prefix heuristic or blanket budget-gap exception is adopted.

A threshold cannot separate this bounded context-relevance task: rejecting every
T1candidate requires threshold **>0.5753808387**, while retaining at least one fee
candidate for every T2/U3variant requires **<=0.5125070220**. Those requirements
cannot both hold. At0.75all nine queries are empty, losing useful fee context too.
This is a numerical finding about these queries/candidates, not a universal
classifier result, probability estimate or evaluation of generated answers.

T1's reference evidence is the selected Charter pre-enrollment pair; no requested
deadline is established there. The larger retained dataset includes other
enrollment notices, including different semesters/cohorts. This run does not
claim the university lacks a calendar or audit every supplied document. T2retains
the printed August4,2023/firstsemester2023–2024 effectivity and pending school
verification. U3's fee fields establish no GCash method. Known Charter cutoff,
fee individual-assessment limitation and F04hold remain attached/unchanged.

## Verification

- Independent numerical recomputation of all243scores/orderings passes; maximum
  dot-versus-normalized-cosine difference8.25e-8. The comparison used normalized
  existing vectors; raw scores are relevance measurements, not confidence.
- All944attempts reproduce through the original context builder, independently
  of the new reporting wrapper;270strategy choices and4,980offered-primary traces
  pass. Exact tokenizer counts for18contexts and234source citation bindings pass.
- All338preserved input hashes and11product/test hash bindings match; path
  normalization reveals nine unique files. No product code/tests changed.
- Fresh focused tests:87passed/93subtests in1.40seconds, exit0. Existing Python3.13
  venv with `-B -m pytest`, no cache and unique external basetemp. Files:
  test_context_selection, test_retrieval_query, test_retrieval_context,
  test_reviewed_policy_chunks, test_reviewed_record_context. The prior full
  5305tests/533subtests result remains applicable historical product evidence;
  no full-suite repeat for this read-only evaluation.

Raw evidence/scripts/labels/acceptance bindings/vectors/rankings/contexts stay
ignored in workspace/audit-evidence/p05-temporal-unsupported-evaluation-20261015/.
Previous sealed writing scripts were not rerun. No downloads, installs,
conversions, source acquisition, model duplication or dependency changes.
Candidate output stays inactive, claim coverage always unknown. No measured
automatic audience/year/payment-intent recognition or engine-success claim.

## Next action

Prepare a bounded source-subject selection design before more parameter sweeps.
All27current candidates lack canonical entity hints. Use reviewed source metadata
to describe subjects, separately from whether a requested claim is supported;
do not derive selectors from gold chunk IDs or make students name a memo.
Any experiment using a trusted caller's subject/year must be clearly annotated
and must not count as automatic NLP. Preserve unknown curriculum, source authority,
currentness and missing-claim handling, and keep the current engine unchanged.
Reuse these exact accepted queries/vectors to compare the eventual opt-in design.

The rough technical estimate stays about80% (75–85%range). This run exposes
remaining work rather than closing calibration. School verification remains
pending without blocking provisional development. F04held/G01originalG02unconfirmed/
G03onlyconfirmed/ASGoutsideundergraduate scope remain unchanged. No source
activation, institutional approval, formalPhase05exit or Phase06 is inferred.
