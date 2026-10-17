# Optional shared reviewed-group context — 15 October 2026

The complete overload group now fits the 2,048-token budget at **1,961 tokens**.
The completion-conflict group needs **1,738 tokens**. Every original field,
source limit, citation and group member remains preserved; the new optional
display shares technical metadata while keeping original structured evidence exact.

## Interface and evidence representation

Enable `shared_citations=True, shared_group_metadata=True` in the existing
offline `build_context` helper. The group flag requires an explicit boolean and
shared citations. Default, compact-citation and prior shared-citation behavior
remain unchanged when this new option is absent or false. Runtime callers do not
opt in, and no institutional candidates or release pointers are activated.

Only marked records that successfully pass the existing reviewed contracts qualify.
The admission path supplies their chunk IDs to the display codec. Generic text,
including JSON resembling a reviewed policy, stays exact text. Groups remain
separate by logical ID, document version and original source byte hash; incomplete
or mixed legacy/marked display groups retain their original representation.

The context prefix becomes `shared-source-groups-v1` when qualifying complete
groups exist. Its `policy_groups` entries contain exact common `service_group`
properties, identical `payload_defaults`, and one digest binding the original
ordered member chunk IDs and payload strings. Each member display carries a
`group_index` plus residual metadata. Merge defaults with residuals to reconstruct
every original policy property except its replaced display-only integrity digest.

All per-part integrity digests and original payload strings remain in returned
evidence, unchanged. This is an explicit display representation change, not a
byte-identical display claim. Full field lists, blank/state markers, reading IDs,
part orders, arrow mappings, source-limit messages and citations remain present
or exactly reconstructable. Existing source, manifest, citation and required-group
validation runs before display preparation. Refused trials cannot change accepted
group/source defaults; every admission uses its exact serialized token count.

## Actual saved-evidence comparison

The run reused 21 inactive candidate chunks, 36 accepted question variants,
unchanged rankings and all existing vectors. It used only the bound local
SEA-LION tokenizer, without loading model weights or performing inference.
Tokenizer SHA256:
`883b037111086fd4dfebbbc9b7cee11e1517b5e0c0514879478661440f137085`.

| Complete group | Previous shared citations | Shared group metadata | Citations retained |
| --- | --- | --- | --- |
| Overload, five parts |2,265 tokens |1,961 tokens |15 |
| Completion conflict, four parts |1,917 tokens |1,738 tokens |4 |

At the exploratory k=3 / threshold=0.5 setting:

| Observation | Previous2K | Group2K | Previous4K | Group4K |
| --- | --- | --- | --- | --- |
| Complete expected evidence, scoped variants |27/30 |30/30 |30/30 |30/30 |
| Complete expected policy evidence |15/18 |18/18 |18/18 |18/18 |
| Cases with a budget-gap entry, including rejected extras |15 |12 |6 |3 |
| Invalid context cases |0 |0 |0 |0 |

These are 30 language variants across 10 scenarios, including 18 policy variants
across six scenarios. Six BSCS variants across two scenarios still require student
curriculum scope. Complete-group context coverage is separate from unchanged
primary ranking metrics; required neighbors are not precision@k primary slots.

All 900 prior shared-citation observations replay exactly. The new 900 observations
produce 18 distinct emitted strings, 245 archived citation bindings and 7,683
repeated citation instances. Each instance decodes to its exact original locator;
all original evidence payloads remain exact. The 57 measured old/new/trial strings
include rejected context trials. Group digests match the full original member
payloads. More metadata room can also admit irrelevant extras; budget-gap entries
remain and the smaller display does not establish relevance calibration.

No new benchmark questions were introduced. All scored cases are positive;
unsupported detection is unmeasured and no global threshold was selected.
This is a bounded candidate comparison, not a whole-corpus content audit or
university-approved eligibility answer.

## Verification and provenance

Plan `0b2b405`, baseline `a6c2c17`, prior product `dea9442`. The task started on
14 October and continued on 15 October; its plan and ignored evidence directory
retain their original start date. Fresh baseline: 58 tests / 62 subtests in 10.81s.
Seven regressions observed expected absent module/keyword RED: 10 failures including
three subtest failures, 39 passed / 51 subtests in 1.26s. Related GREEN: 95 tests /
100 subtests in 1.80s. A cyclic-fixture comparison error was corrected by comparing
row data and neighbor IDs separately; no product correction was needed for it.
Full suite: **5,264 passed / 500 subtests**, six skips / six existing warnings
in302.92s, exit0. Command: authorized Python3.13 `-B -m pytest -q -p no:cacheprovider`
with external task `--basetemp` and `--tb=short`. Independent review passes with no findings; final documentation and phase
results are recorded at closure.

1,501 prior hashes verify, including inherited exact snapshots for historical
authorized changes. Four new snapshots retain the exact pre-change code/test bytes
from `a6c2c17`; originals, registers, questions, vectors and earlier raw evidence
remain unchanged. Source-derived scripts, snapshots, contexts and execution logs
remain ignored under
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-shared-group-context-20261014/`.

Actual thesis physical17–18, routing PNG, master section10, Phase04/05 records,
scope/source-gap/service-association/dataset policies consulted; no discrepancy.
Five-area undergraduate/shared-audience and all wording decisions remain settled.
School verification remains deferred pending actual evidence, and no submission or
response is inferred from the date. Phase05 formal exit and activation remain open.
Owner artifact changes and remote historical review documents are preserved.

## Next action

Preserve these completed display formats, candidate payloads and saved measurements.
The measured complete-group 2K refusal is now resolved at the tested setting, so
do not keep compacting source text or repeat conversions/embeddings on a CLI change.
The next development gate is relevance/unsupported-query calibration: prepare a
bounded set of new or changed benchmark questions and expected scoped behavior for
owner review before testing. Existing positive-only results cannot select that
threshold or claim unsupported-answer detection. Source approval and institutional
activation keep their separate standing gates; no Phase06 advancement follows here.

## Final review

Closure: **469 documentation/ledger tests and 11 subtests passed in 11.49s**.
Phase validation exits0; advancement exits1 as expected for blocked Phase05.
38ignored evidence files and14current code/test digests are sealed. Manifest SHA256:
`ae9c3829853e21d87d00e15590f3252ee4a4a7a15eddc00e93d2c4c465aa8e58`.
Product commit `f5e1a65`; the following documentation closure SHA is in Git.

Independent review checked 900 new observations with a separate display/admission
simulator, 900 preserved shared observations, 1,800 actual-token default/compact
comparisons and 900 preserved compact observations. All 57 saved token counts,
18 emitted strings, 245 archived citations and 7,683 citation instances match.
All 1,501 prior hashes and four baseline snapshots verify. Seventeen negative
controls passed, including refused trials preserving previously accepted defaults;
six BSCS scope holds remain. Fresh reviewer tests: 46 passed / 54 subtests in 1.12s.
No implementation behavior was declined for review.

Final review: independent verification PASS, no Critical/Important/Minor findings.
Separate group/source display reconstruction, budget admission, exact token counts,
original payload/field/limit/citation preservation and prior1501hashes/four new
baseline snapshots verified. Per-part display hashes are explicitly replaced by
a bound group digest; originals remain exact in evidence. Positive-only calibration,
institutional source approval and runtime activation remain separate existing gates.
