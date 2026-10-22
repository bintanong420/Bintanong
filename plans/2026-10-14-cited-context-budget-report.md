# Optional compact citation context — 14 October 2026

Baseline22896c1; diagnostic plan782dbfe; code093ea4a. Manual assembly of the eight
reviewed curriculum candidates found that repeated citation identity prefixes made
six contexts exceed the default2048 budget. This is retrieval display overhead,
not defective source text or a new source-retention decision.

`build_context(..., *, compact_citations=False)` now supports an opt-in display.
Each chunk's context groups citation locators by exact version/hash/physicalpage
and serializes that group as JSON. Every locator, including duplicates and its
order within that source/page, remains. The returned structured citation list and
evidence text remain identical. Default serialization and runtime engine/settings/
RPC calls remain unchanged; no caller automatically opts in.

## Actual context sizing

Existing strict offline SEA-LION tokenizer counted serialized text including all
citations; no context was embedded or ranked. Each candidate was supplied manually
with similarity null, separately from other curriculum editions, to check assembly.
This does not recover evidence through an approved release or establish quality.

| Candidate row | Payload tokens | Default cited context | Opt-in cited context |
| --- | ---: | ---: | ---: |
| Old BSCS CC5 | 286 | 2000 | 1209 |
| Proposed BSCS CC5 | 475 | 2883 | 1680 |
| Old BSCS practicum | 292 | 3528 | 1917 |
| Proposed BSCS practicum | 478 | 2891 | 1688 |
| Architecture AD2 | 292 | 2179 | 1284 |
| Nursing Microbiology | 350 | 2310 | 1349 |
| Criminology CDI7 | 289 | 2013 | 1242 |
| Tourism immersion | 286 | 2625 | 1574 |

Default:2/8fit2048,all8fit4096. Opt-in:all8fit2048, exact1209–1917tokens. All113
citations and all eight complete evidence payloads/row bindings remain intact.
The builder still withholds a whole group when its exact serialized size exceeds
the selected budget. It never truncates the clause or drops a required neighbor.

Ignored packet:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-cited-context-budget-20261014/`.
It contains baseline/compact full contexts and counts, budget replays1024/2048/4096/
8192, code-baseline binding/snapshot, raw diagnostic and regression logs.

## Verification and review

Synthetic TDD RED:6 failures/7passed0.48s for missing opt-in flag. Related GREEN:
**83 passed,125 subtests passed,1.70s**, exit0. Command:
`python -B -m pytest tests/test_retrieval_context.py tests/test_retrieval_engine.py
tests/test_reviewed_flowchart_context.py tests/test_reviewed_record_context.py
tests/test_reviewed_policy_chunks.py tests/test_reviewed_heading_metadata.py -q
-p no:cacheprovider --basetemp <packet>/pytest-green`; `green.log`.

One fresh final reviewer: no Critical/Important/Minor findings.10focusedtests/
3subtests,1000synthetic default differential comparisons and100randomized compact
binding/order/determinism/budget checks pass. No secondreview or deferred findings.
Reviewer declines institutional authorization/effectivity, actual corpus retrieval
quality, the separately running fullsuite and historical preservation investigation.
Rulings: these remain separate gates; the helper review does not approve activation,
semantic calibration or institutional content. Fullsuite/preservation are checked
by actual outputs recorded here, rather than inferred from the reviewer verdict.

Fresh real replay compares opt-in structured evidence with all eight saved default
contexts, exact token counts, all113 citation locators and unchanged source payloads.
Of1274 preserved hash bindings,1273current dependency files remain identical. The
one authorized changed context.py is preserved in its exact original-byte snapshot,
matching the historical expected hash and baseline-code binding. The first replay
expected that authorized code file to remain unchanged; the failure is retained.
The corrected check resolves exactly that historical binding, with no exception
for source/original/register/chunk changes and no replacement of old evidence.

Final fullsuite aftercode093ea4a: **5212 passed, 6 skipped, 6 warnings, 464 subtests passed in 341.98s (0:05:41)**, exit0; `full-tests.log`.
Command:`python -B -m pytest -q -p no:cacheprovider --basetemp <packet>/pytest-full`.

Existing Python3.13.7/packages/modelweights retained. Strict tokenizer load rechecks
all ten external model assets; configuration matches previous real query execution.
Source originals, accepted46fields, owner events, old/new curricula, known source
cutoffs/conflicts and prior sealed packets remain unchanged. No downloads, dependency
changes, database writes, answer generation, executable rules or new memorandum intake.

## Remaining gates and next action

Closure:435documentation/ledger tests and11subtests pass11.24s; phasevalidate0/
canadvance1expectedblocked; diffcheckpasses. 25files/two currentcode digests
sealed; SHA256:90d89fd72afc8a33827e94a514127f391a430f026ce824d6b4113d1a7caa9b7c.1273current hashes and one
exacthistorical code binding retained; sourceverification remainsdeferred.

Ruling: keep citation compaction opt-in until later governed integration selects it;
the cost is that existing runtime calls continue using the legacy display meanwhile.
School verification/use authorization remains deferred at the owner's request,
and policy undergraduate applicability/release/calibration gates remain open.
Preserve the verified query/evidence packet and this lossless context option for
that integration; do not repeat row/evidence/cohort questions or invent observations.
Bring source verification up before activation or when the owner reports a reply.

Future batch excludes college-specificCharters and may include memoranda such as
student vehiclegatepass. No memorandum has been newly received or processed.
Show any new proposed questions before testing. Phase05 remains blocked on its
formal exit gate; no Phase06. Scope thesis17–18/routing PNG/master10/current phase
handoffs reconsulted; no scope/routing discrepancy. Existing isolated worktree retained.
