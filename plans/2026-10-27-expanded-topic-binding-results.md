# Expanded topic/claim bindings and routing capacity

All465normalized readings now have offline candidate subject/claim bindings through
the existing constructors. Source text,companions,hosted465draft,active78release and
local runtime pin are unchanged. [Plan](2026-10-27-expanded-topic-binding-plan.md).

| Metadata check | Result |
| --- | ---: |
| Readings assigned / unassigned | 465 / 0 |
| Source-labelled subjects | 146 |
| New source groups represented | 142 |
| Prior claim records carried | 66 |
| Total claim records | 208 |
| Visible-field claims / retained not-stated claims | 206 / 2 |
| Bound nonblank scalar source fields | 1409 |

Seven existing subjects and their66claim wordings/field references/basis receipts
remain. Their current IDs are rebound after metadata-only identity changes.
New source-specific subjects retain complete dependency assignments. The linked
INC/removal/context readings share one subject;the two linked registration readings
share another. This groups metadata without deleting or rewriting any dependency.

New claims mean narrowly labelled **printed fields**,not complete-service guarantees,
new policy conclusions or approved student question wordings. Existing human and
delegated comparisons remain distinct. A new assistant binding receipt includes
source-field event hashes,value digests and hashes of the dated comparison reports.
No human/institutional approval or source-state promotion was inferred.

## Context budgets and actual Gemma preflight

All206visible-field claim profiles assemble their complete declared fields and
transitive companions;151fit default2048E5context tokens,55need more.49subjects have
at least one such profile. Maximum7864E5tokens;proposed rounded budget7936.
These are unapplied preparation values,not changed runtime settings. Initial
per-part **English,single-claim** generation prompts were built with existing compact
cards,short evidence labels,source citations retained host-side,and declared record
coverage. All206fit8192with768output tokens plus8margin;maximum input6857.

This supplies explicit complete context;it does not test router selection,top-k
retrieval,checker/repair prompts,multilingual/Hybrid combinations,answer completeness,
model answers or end-to-end latency. No inference call occurred. Source gaps remain
visible;metadata/report success never certifies semantic answer sufficiency.

## Routing capacity finding

Exact counts use the existing local Gemma chat template and `/tokenize`,not E5
estimates. Same short transcript question,no prior turn,empty curriculum facts.
All totals below reserve768output tokens plus8margin within8192.

| Routing profile | Input tokens | Total with reserve | Fits |
| --- | ---: | ---: | --- |
| Current seven-topic menu | 6283 | 7059 | Yes |
| Full146-topic menu | 15693 | 16469 | No |
| Remove new single-claim field-name maps only | 9587 | 10363 | No |
| Remove all new field-name maps only | 9551 | 10327 | No |
| Proposed compact146-topic selection pass | 3838 | 4614 | Yes |
| Largest single detailed topic | 5162 | 5938 | Yes |
| Eight topics with largest individual detailed prompts | 6869 | 7645 | Yes |

Projection probes preserve selectable claims,not-stated facts and source context;
they were not applied. They resolve whether removing redundant field-name maps
alone fixes capacity:it does not. Do not keep trying equivalent serialization
variations,raise the context window or drop source limits to hide this failure.
The proposed selector is only a capacity prototype;no semantic selection accuracy
or universal combination/long-question capacity result is established.

The existing `bintanong-p09-cuda-latency` container was restarted with its unchanged
model mount,image,8192context/one-slot/768output profile at localhost18088. It is
idle after tokenization. No model/image download,dependency or server-setting change.

## Reviewable next routing change

Implement an opt-in candidate path using the same local model:

1. A compact source-labelled menu selects up to eight relevant subjects. It never
   answers,determines eligibility,selects the final route or supplies student facts.
2. Host validation accepts only current-menu IDs. Unknown/duplicate/overflowing IDs,
   malformed output,ambiguity or transport failure cannot authorize an answer.
3. Pass the unchanged original question and selected **complete** detailed topics
   to the existing semantic router. Preserve existing audience/language/part rules,
   source gaps,claim menus,Prolog operations and downstream validation.
4. Exact per-request template/token preflight applies to both calls,including long
   or multi-part questions. Over-capacity requests withhold/clarify rather than
   truncate evidence,discard requested parts or silently select a different source.
5. Keep the current small-menu path unchanged. Use synthetic TDD for menu binding,
   invalid selections,excluded audiences,empty/ambiguous choices,multiple document
   parts,Hybrid routing,timeouts and token overflow. Compare existing accepted cases
   and bounded new-source probes;measure the added call's latency separately.

This preserves LLM semantic routing and deterministic structured reasoning. It
adds an inference call and an upstream selection error surface;actual accuracy and
latency need measurement. Review the existing PRD/architecture baseline and write
the focused implementation plan before code. No behavior was changed in this pass.

## Verification and evidence

Ignored evidence:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p11-expanded-topic-binding-20261027`.
`prepare_bindings.py` creates catalogue/register/basis/lineage/topics. Four principal
metadata files repeat byte-identical. `validate_bindings.py` verifies all206visible
claim contexts and six negative controls:stale catalogue,absent field,missing emitted
fields,unknown claim,unresolved source limitation,and missing companion. Full
SourceAwareEvidencePolicy construction passes in21.36s with a clearly marked
placeholder embedding ID for metadata validation only;no vector availability claim.

`preflight_router.py`,`probe_menu_projection.py`,`preflight_generation.py` and
`probe_two_stage_capacity.py` retain exact template/token receipts. Prepared source
and source-span hashes remain bound to the prior normalized465artifact:
`d9ae14ded25923954a3a90ddcd843d4634eed460d9782c3e0389481536810a26`.

SharedPython3.13,`-X utf8 -B -m pytest -q -p no:cacheprovider`,external basetemp;
candidate_subject/candidate_claims/candidate_claim_reviews,retrieval_evidence_policy,
routing_document_topics/routing_topic_capacity/service_topic_context,and
orchestration_document_topics/orchestration_multi_topic suites:
**117tests/156subtests passed in2.67s**. Data-only work;no production/full-suite repeat.
Evidence scripts,artifacts,negative-control results and logs are sealed locally.

## Corrected local embedding package

Completed465vectors for the normalized source selection:13new texts encoded on CPU,
452exact text/configuration vectors reused.65.06s;1024dimensions/L2;exact tokenizer
parity and<=480tokens with truncation disabled. No new model/dependency/download.
New embedding set:`c62090be2e5a245f10138b4a77bd43f2ecb9a0c5021996eb4550f1c23a94086a`.
Every embedding matches its current chunk/content hash;complete-set identity
recomputed independently from manifest configuration and all465records.

`runtime-package/` contains six source/version/catalogue/register/embedding artifacts
and explicit `package-status.json`:candidate-only,not runtime-ready,not activated.
No budget overrides are installed there. File hashes are in the status/verification
receipt;`encode_normalized.py` and embedding verification retain encoding evidence.
This local package does not overwrite the hosted draft or the active runtime pin.

Independent service/image structural evidence,canonical overlaps,governed release
review,and actual runtime/answer checks remain. No
activation,frontend integration,university approval or Phase11completion is implied.
