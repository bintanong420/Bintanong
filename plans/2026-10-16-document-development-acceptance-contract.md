# Bounded document development acceptance contract — 16 October 2026

Version: `document-development-acceptance-v1`. Engineering decision at baseline
`349056b`; product remains `8595fb8`. This contract closes the specification of
the selected profile's development criteria. It does not declare the formal
Phase 05 exit gate passed or change a retrieval response.

## Capability and evidence path

For an undergraduate policy or procedure question, retrieve the selected reviewed
source fields when present and preserve an insufficient-evidence finding when the
requested claim is missing, conflicting or unsupported. A researcher supplies the
trusted subject and exact requested claims. Automatic question interpretation,
student answers and curriculum eligibility are outside this bounded capability.

Evidence path: existing source-bound reviews and catalogue, pinned saved query and
document vectors, global top-k then subject filtering, actual RetrievalEngine
context assembly, and assessment of the fields actually emitted. This advances
master 10.1 step 6 and the development portion of 10.3 / Phase 05 Tasks 4 and 6.
The unresolved question addressed here is what this profile's existing observations
can accept without conflating field availability, context recovery and permission
to answer. No additional ranking experiment is required to answer that question.

Use the [selected profile](2026-10-16-document-development-profile.md) and its
unchanged 39 accepted document variants, 19 chunks, 54 spans and five pending
source versions. The other 36 accepted variants retain their existing structured
reservations or control evidence; they are not silently counted as evaluated here.
This is a selected package, not a complete undergraduate corpus or source audit.

The fixed settings are k3 / minimum similarity .25 / 2048 tokens, policy ID
`uncalibrated-document-development-v1`, fingerprint
`6dc93d281aa0584efe41afdc1e90fdecd3aa46e598073a10d3faa41230e8aeb5`.
Embedding set:
`02fce0fc4caca1c15cc4a58f5e511f70d5dc27be77769f7cbb0f7ce423368811`.
Release ID `offline-document-development-v1` is a saved-double test pin, not an
authorized database release. All source/package/case/input hashes are already
bound by frozen-profile.json in the selected profile's sealed evidence root.

## Criteria and decision semantics

The following are engineering criteria for retaining this bounded research
configuration. They are recorded after seeing the development observations;
they are neither a preregistered rubric nor evidence of unseen-set accuracy.
Existing accepted case expectations and field reviews supply the labels.
No case wording, label, source content or ranking setting changes here.

| Check | Required finding | Saved observation and disposition |
| --- | --- | --- |
| Identity and reproducibility | Exact accepted case identities, frozen settings and unchanged bound inputs; no substitution of the historical 27-chunk diagnostic | 39 cases, 17 inputs and frozen profile verified; meets this check |
| Available reviewed fields | All 18 field-available variants have their expected complete context and the reviewed fields actually rendered with matching source locators | 18/18 complete; rendered-field audit passes; meets this check |
| Expected insufficiency | All 21 missing/conflicting/unsupported variants remain insufficient; related text must not authorize the absent claim | 21/21 insufficient; zero positive status promotions; meets this check |
| Language separation | Each language independently meets the available-field and insufficiency requirements; aggregate success cannot hide a language failure | English, Filipino and Taglish each 6/6 available contexts and 7/7 insufficient; meets this check |
| Context integrity | Every emitted group is whole, bindings resolve to the unchanged source package, and exact serialized context fits 2048 tokens | 39 token recounts, 303 citation bindings and 117 rendered fields audited; meets this check |
| Literal related-context completeness | Report the unchanged expected-context labels for every case, including insufficient cases; an empty result cannot be marked recovered | 36/39 complete; three T1 misses remain failures of related-context recovery |
| Ranking quality disclosure | Report primary and emitted metrics separately, overall and by language/category; no undeclared numerical pass threshold | Existing 17 primary and 17 emission summaries retained, including nine non-target selected-primary slots |
| Authorization and answer limits | Every result remains candidate-only and activation-ineligible, runtime authorization unverified, answer sufficiency unassessed | All 39 retain these flags; this verifies honest reporting, not authorization |

These checks have distinct outcomes. Meeting the available-field and insufficiency
checks establishes only bounded development behavior. It does not turn 36/39 into
39/39 context recovery, erase non-target selections or create an overall formal
pass. The documented context limitation remains part of the decision.

For related-context recovery, the numerator counts cases whose emitted chunk IDs
contain the full pre-existing required-context set; the denominator is all 39
cases. For available-field acceptance, use only the 18 established field-available
cases and additionally require the existing rendered-field/source audit. The
insufficiency denominator is the other 21 cases. A correct unavailable-information
disposition and a context miss can both be true for the same case. Empty evidence
needs no fabricated citation; every evidence item actually emitted needs its
resolvable original-source citation. Empty-result returned precision stays N/A.

Fixed-k primary precision remains .495726 and primary recall .753419. Returned
primary precision .875 is defined for 36 cases. Emitted requested-primary
precision .875 / recall .753419 have their own recorded definitions. These
related-evidence metrics are not answer support, and no new threshold is fitted
to their observed values. Full language/category results remain in the profile.

## Concrete result behavior

Keep the existing v2 engine result unchanged. Complete reviewed fields remain
`status='uncalibrated'`, `coverage='partial'` and
`gaps=['development_calibration_pending']`. Missing/conflicting/unsupported claims
remain `status='insufficient_evidence'`; evidence may be present while coverage
is partial, or absent with coverage none. The existing policy's source findings
and exact gap reasons remain the explanation. This contract introduces no
response schema, helper, loader, CLI option, policy-name bypass or new positive
status. It does not reinterpret coverage partial as an answer-sufficiency claim.

The three misses are `temporal-t1-en`, `temporal-t1-tl` and
`temporal-t1-taglish`. Global top-three candidates belong to other subjects;
subject filtering leaves no evidence. The current-year enrollment deadline is
also absent from the selected reviewed sources. Preserve both findings. A search
for older enrollment prose would not establish the requested date. An actual
answer/referral renderer is not evaluated by these retrieval observations.

F04's disputed digit, G01/original G02, original cutoffs, deadline conflict,
version/current-year limits and scope decisions retain their existing treatment.
No missing fee, prerequisite or process ending is inferred. Curriculum facts and
eligibility remain with the structured/Symbolic architecture and applicable gates.

## Decision and remaining gate

Retain the fixed profile for provisional offline document research. Its existing
observations meet the bounded available-field/insufficiency/integrity criteria
with the explicitly recorded related-context limitation. No further behavior
change is justified just to rename those observations or make every question
retrieve some text. This is an engineering disposition, not a new owner wording
approval, institutional decision or blind final acceptance.

Formal Tasks 4 and 6 stay open. Returning relevant, authorized context on the
actual runtime-role path remains unverified for this real-source package. The
[source-event reconciliation](2026-10-16-source-event-evidence-reconciliation.md)
identifies absent office confirmation/authorization and scoped completed-review
state decisions; it does not justify writing approved status strings. Existing
synthetic runtime-role tests establish software guards; saved doubles bypass
actual release authorization. Neither substitutes for that remaining evidence.

The next gate-bearing work is to bind actual supported source/release decisions
to the existing governance contract, then perform the authorized runtime-role
retrieval and applicable final exit checks when their prerequisites and execution
authorization exist. Do not repeat the school-response question while it is
pending. On receipt, inspect its actual scope before proposing a concrete governed
transition; do not prebuild a speculative updater or treat research continuation
as approval. No new source review, vector run, parameter sweep or additional
acceptance sidecar is required by this contract. Phase 06 remains unavailable.

## Verification and recovery

Use the existing sealed profile evidence, under ignored workspace/audit-evidence/
p05-document-policy-selection-20261016. Its read-only reviewer_verify.py checks
the 741 scores, 39 cosine ranking agreements/token counts, citations, rendered
fields, 17 primary/emission groups and input identities without production helper
imports or evidence rewrites. Its seal is
`6f8154ecf056fdb94c75b294b7e4b1b5c93c04e737ac70d4e73ef5e772b02428`.
Run seal_evidence.py only in verify mode. Later logs belong in an ignored sibling
checks folder. No new generated source artifact or result schema is necessary.

Context consulted on resume: thesis physical 17–18 (original-page renders), actual
runtime routing PNG, master section 10, scope/source-gap policies and active
phase plan/checkpoint/handoffs. No architectural discrepancy. Owner artifact
changes remain preserved and unstaged. Verification and the single builder check
are recorded below after their results are available.

The single builder check reports “nothing important left”; no implementation or
source-authority review is inferred. Fresh read-only reviewer verification passes
741 scores, 39 ranking/token checks, 303 citations, 117 fields, 17 primary and
17 emission summaries, 17 inputs and 18 unchanged raw top-level files. Profile
and source-event evidence seals verify unchanged. A separate read-only assertion
checks all 39 conservative flags, 18 available contexts, 21 insufficient results
and the three literal context misses against this contract.

Documentation/phase-ledger checks pass 521 tests / 11 subtests in 11.96s; the
final check also passes in 11.60s, both exit 0. Phase validate exits 0 and
can-advance exits 1 (expected blocked); whitespace checks pass. No product or
test code changed, so the previous full product suite was not repeated. Raw
check logs are in sibling p05-document-acceptance-checks-20261016. The contract
and continuity documents form one documentary commit; owner artifacts remain
unstaged. No formal acceptance or Phase 06 advancement follows.

Subsequent code inspection identified an independent integration-verification
seam: source-aware engine tests used doubles while actual database engine tests
used the legacy path. The [synthetic database integration](2026-10-16-source-aware-database-verification.md)
now verifies that composition under both real roles without changing these
criteria or the 39 observations. It does not establish actual-source release
authorization. The earlier lack of an identified implementation task was not
proof that every integration seam had already been verified.
