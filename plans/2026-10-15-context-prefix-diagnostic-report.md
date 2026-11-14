# Context-prefix diagnostic and Phase 05 estimate — 15 October 2026

The budget issue has two different causes: required evidence can be missing, or
complete expected evidence can be present while additional groups are refused.
The saved-ranking comparison reproduces both. Reducing every query to one primary
candidate would hide the latter refusals but lose U1's required contextual evidence.
An experimental longest-gap-free prefix preserves this selected positive set,
yet also produces clean-looking wrong contexts for unsupported/ambiguous requests.
No new runtime policy has been adopted.

Baseline: product `feaa961`, evaluation report `91bba1f`; diagnostic plan `5bfb7a1`.
See [the plan](2026-10-15-context-prefix-diagnostic-plan.md) and
[preceding approved-query observations](2026-10-15-approved-natural-query-evaluation-report.md).

## What was compared

All 27 candidates, saved rankings for 54 queries, source versions, field spans,
limitations, explicit request annotations and exact accepted wordings are reused.
There are no new embeddings, model-weight loads, source conversions, dependency
changes or content decisions. All 1,350 previous context observations reproduce
exactly before comparing alternatives.

For each saved k=3/5/8, threshold 0/0.25/0.5/0.75/0.9 and budget 2048/4096 setting,
the run assembles each available ranking prefix and its complete transitive
source-declared dependencies. It records four strategies: one primary, two
primaries, all eligible primaries and the longest prefix whose assembled context
is nonempty and has no assembly gaps. The last is experimental, not an installed
coverage rule. Prefix selection uses rankings and observed assembly gaps only;
expected-answer labels measure the results afterward.

The approved-context comparison includes 30 prior scoped positive variants, six
U1/U2 variants and nine S1/S2/P1 variants. Three A1 variants and raw versions of
the nine S1/S2/P1 cases provide diagnostic controls. Six prior BSCS curriculum
holds remain unchanged. Scope/acronym behavior is still supplied through explicit
researcher annotations; automatic language interpretation is not measured.

## Focus results: k3 / similarity0.5 / 2048 tokens

| Primary-selection strategy | Complete expected evidence, 36 positive variants | Nonempty contexts without assembly gaps | Cases with extra evidence outside the expected set |
| --- | ---: | ---: | ---: |
| One primary | 33/36 | 36/36 | 0 |
| Two primaries | 36/36 | 28/36 | 6 |
| All eligible primaries | 36/36 | 21/36 | 6 |
| Longest gap-free prefix, experimental | 36/36 | 36/36 | 6 |

“Without assembly gaps” does not mean the question is answered or its claims are
supported. It only means the selected groups fit and pass the context builder's
structural/citation checks. The actual engine was not invoked, and its default
display, source-conflict, calibration and coverage checks are not bypassed.

### U1 needs evidence beyond its best-scoring clause

One primary returns only the lost/stolen/destroyed-sticker owner-expense clause:
591 tokens, no assembly gaps, but missing the expected application-payment and
office context in all three languages. Two primaries recover that context and
its source-declared office dependency: the full expected set fits at 1,480 tokens.
The context still states that the replacement price and replacement workflow are
unavailable. Do not interpret fewer gaps as more complete source knowledge.

The expected group crosses original photo versions. The experiment preserves
separate citations and does not fabricate a cross-version service dependency or
fill the missing context from gold labels. This example rules out adopting
“always use only the top result” from U2's apparent success.

### U2's refusals are for additional overload material

The F01 primary brings its source-declared F08/F09 neighbors. This returns all
required fee-example/rate/date/effectivity evidence and missing-individual-billing
limits at 1,629 tokens in each language. The English and Taglish second primaries
are handbook overload-group members; adding those complete groups exceeds the
remaining 2,048-token budget. All-primary assembly reports budget refusals in
all three languages, although the expected U2 evidence is already complete.

The experimental longest-gap-free prefixes have lengths 1/2/1 for English/Filipino/
Taglish. Their final cited evidence is identical to the complete expected U2 set;
the second Filipino primary is already represented by the first primary's source
dependencies. The experiment explicitly records every omitted primary and its
unrepresented dependency IDs instead of silently discarding the rejected groups.

The printed P20,000, rate/hours/date and unknown individual assessment remain exact.
No replacement price, P2,000 student bill, FHE coverage or institutional authority
is inferred. Removing extra-group budget refusals alone would not justify calling
this a fully answered financial question.

### Clean assembly cannot decide relevance, audience or ambiguity

Without their explicit restrictions, all nine S1/S2/P1 variants yield nonempty,
gap-free contexts under the experimental prefix strategy. They contain undergraduate
evidence for professional-Law/faculty requests or BSCS courses for the BSIT query.
All three ambiguous “TC” variants also yield clean-looking contexts. None is proof
of a supported answer. P1 can even fit both old and proposed BSCS rows, so the
engine's separate curriculum/version checks remain essential.

With the approved explicit scope/selector inputs, S1/S2/P1 retain empty evidence
as before. A1 remains a clarification trace, not a successful empty-retrieval
metric or an automatically recognized acronym. These controls do not calibrate a
universal similarity threshold or measure automatic notice generation.

### More space admits more additional material

At 4,096 tokens the all-primary strategy still recovers all 36 positive variants,
but 15 cases contain evidence outside their expected set, compared with six at
2,048. Four positive cases still report budget refusals at k3/0.5/4096. Increasing
k to 5/8 at 2,048 increases all-primary refusal cases from 15 to 21 without improving
expected recovery. Extra space and more results do not solve claim coverage.

## Verification

- 4,390 prefix attempts across 1,710 strategy configurations; 424 distinct primary/
  budget assemblies and 52 unique archived contexts. All 1,350 previous observations
  reproduce exactly; no invalid-citation/dependency/record gaps occur.
- Independent replay checks every prefix, chosen strategy, omitted group, expected
  recovery and focus summary. It rebuilds all 424 distinct contexts, verifies exact
  tokenizer counts for 52 contexts and resolves 1,032 archived citation bindings.
- All 278 preserved input hashes match, including the previous 43-file evidence seal,
  its preserved originals and saved vectors. The tokenizer's exact hash is
  `883b037111086fd4dfebbbc9b7cee11e1517b5e0c0514879478661440f137085`.
- Relevant existing tests: **68 passed / 70 subtests in 1.41 seconds**, exit0:
  `tests/test_retrieval_context.py`, `tests/test_reviewed_policy_chunks.py`,
  `tests/test_reviewed_record_context.py`, using `-B -m pytest -q -p no:cacheprovider`
  and a unique external basetemp.

No product code changed. The full 5,286-test/510-subtest result for `feaa961` remains
historical verified evidence; it was not rerun for this read-only comparison.
Data scripts and raw results stay ignored under workspace/audit-evidence/
`p05-context-prefix-diagnostic-20261015/`. Never run writing scripts in the previous
sealed root. New evidence contains the comparison/replay scripts, raw attempts,
selection traces, context/token archive and preservation inventory.

## Updated completion estimate

My planning estimate remains **about 80% of Phase 05 technical work**, with a rough
**75–85% range**. This is a judgment about remaining work, not measured corpus
accuracy, a proportion of passed tests or formal phase completion. This diagnostic
reduces uncertainty about context selection; it does not close the calibration gate.

| Planned work area | Verified position |
| --- | --- |
| Query contract and matching encoder | Delivered; real local encoder/configuration exercised. |
| Release/scope-filtered retrieval interface | Delivered and tested in prior authorized fixtures; shared deployment remains separately gated. |
| Bounded context and cited evidence | Delivered; real data now expose the remaining coverage/selection decision. |
| Relevance and coverage calibration | Partial: real multilingual observations exist, but no justified global/runtime policy is installed. |
| Structured retrieval/debug response | Delivered; do not equate its assembly checks with automatic language understanding. |
| Final evaluation, governance evidence and handoff | Partial: approved 18 new / 36 prior variants, reviews and source checks exist; formal exits remain open. |

The remaining substantial work is concentrated in three packages:

1. Define and verify context-selection/coverage behavior that reports omitted
   groups separately from missing required evidence while retaining uncertainty.
2. Complete representative in-scope unsupported-case and temporal/version evaluation,
   then justify a development-only relevance/coverage policy. New question wordings
   still need owner review; gold labels must not become runtime hints.
3. Reconcile remaining source-governance/exit evidence, run the final gate and
   produce the earned Phase 05 handoff. Shared deployment/activation is a separate
   authorization boundary, not a prerequisite for every offline experiment.

School verification has no reliable response date; ordinary provisional work
continues. F04's held amount and unconfirmed G01/G02 limit their own claims rather
than blocking this diagnostic. Their resolution is not a substitute for calibration.
No new college-government sources or wider institutional approval are inferred.
The phase remains active with a blocked formal handoff; no Phase 06 is started.

## Next action

Prepare a narrow opt-in design for context-selection reporting using the existing
builder: record offered, omitted and unassembled required groups distinctly, keep
all source limits, and leave claim completeness unknown unless independently
established. The observed longest-gap-free prefix is a candidate for comparison,
not a default selection rule. Validate with adversarial synthetic controls before
any behavior change, then replay these exact saved cases.

Do not make the current engine ignore all budget messages or infer “sufficient”
from a nonempty gap-free context. Keep the outside-scope/acronym/curriculum controls,
old BSCS holds, approved wordings and school-verification boundary intact. Source
content, source precedence and new benchmark text still follow their own review.

## Final review, documentation and seal

One fresh-context independent review found no Critical/Important/Minor issues.
It rebuilt all4,390attempts without caching and with similarities replaced byzero;
all context hashes/token counts/returned IDs/gaps/limits reproduced, validating
that the diagnostic cache need not include score. All1,710strategy decisions and
13,681dependency checks passed; reviewer68tests/70subtests pass1.50seconds.
No second review, full-suite rerun or product change was needed.

Documentation/phase-ledger verification: **472 passed /11 subtests in14.47seconds**,
exit0. Phase-state validation succeeds; can-advance refuses the blockedPhase05
handoff as expected. Whitespace/local report links and seven unchanged product/test
byte hashes pass. All278preserved hashes remain unchanged after review.

New ignored evidence seal: **21 files**, excluding pytest temporary trees.
Manifest SHA256:`14bc4f94e4a0688755e45d4bd88dd06d70a526e35ef5ee1a3a2dfe6035e326e6`.
Read-only verification passes. Do not rerun writing scripts in the sealed directory;
use a new ignored root for follow-up work. Only six curated report/plan/continuity
files enter the following Conventional Commit. Owner artifact changes remain
untouched and unstaged. The checkpoint records parent5bfb7a1; the following
report commit is recoverable from Git. No push, source activation or Phase06.
