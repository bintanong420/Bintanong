# Fraud-precedence correction — verification record

Code `e1d7e8b`; [bounded plan](2026-10-25-fraud-precedence-correction.md).
Reuses approved source-review batches 4/7 and source-gap policy. No source,
dependency, router prompt, model mode, package, migration or release-pin changes.
The expanded release remains inactive. Phase 11 is still active.

## Resulting behavior

In the selected `parts` profile, an answered model slot citing either record with
the recorded unresolved admission-fraud precedence limit is replaced before claim
numbering/review. The comparison copies both rows' visible fields and penalty
column labels, names II.6/II.8a, says precedence is unresolved, declines to choose
a student's sanction and refers to the right university office. English, Filipino
and Taglish framing surrounds verbatim printed quotations. Blank cells remain
unspecified; no penalty or administrative decision is inferred.

Both cards must be present, unique, internally usable and from the same source
version/hash. Missing/incompatible counterparts or an unresolved malformed-source
hold make only that slot `source_gap`. The ordinary per-part relevance/support
review still assesses the corrected comparison; its verdict remains fallible.
The discarded model-selected sanction cannot reappear through a positive verdict.
Independent slots/canonical structured results retain their existing paths.

Claim assembly reserves capacity for remaining slots and existing host replies.
When necessary, both rows fit one claim with both evidence IDs; if they do not fit,
the affected slot is unavailable. No increase to the eight-claim/1200-character caps.
Resolved/other not-stated limits and uncited overlap records are unchanged.

## Evidence

Ignored root: `C:/Coding-projects/bintanong_workspace/audit-evidence/p11-fraud-precedence-20261025/`.
Shared Python 3.13.7: `-X utf8 -B -m pytest -q -p no:cacheprovider`, external basetemp.

- Initial console RED: 11 expected behavior failures, 1 foreign-version fixture
  setup error, 3 passes. The fixture was repaired. `baseline-version-red.log`
  confirms the corrected cross-version case fails against isolated pre-fix
  `to_draft` from c1fc29a. No working production files were reverted.
- Focused initial GREEN: 15 passed. `regression.log`: 506 generation/understanding
  checks passed in16.02s.
- `review-red.log`:2 failures/15 passes reproduce a newly added counterpart's
  source-hold bypass and eight-part draft overflow. `review-green.log`:508 passed.
- Independent review found P2: marking comparison slots `host` bypassed the
  question-relevance check. `relevance-red.log`:7 failures/11 passes (six coverage
  assertions and one false-positive answer). Fixed by retaining normal `answered`
  review status; fictional questions now actually request sanctions. Final
  `relevance-green.log`:509 passed in10.98s, including18 precedence cases.
- Reviewer assessed version mismatch, missing/duplicate counterparts, uncited
  limits and numbering/binding; no other blocker reported. Institutional source
  accuracy and actual-model language quality were outside that code review.
- Actual sealed-field component check: both rows/values/citations preserved in
  all three language templates. Separate claim lengths635/410(en),655/422(fil),
  643/414(Taglish); combined1046/1078/1058, all below1200. This verifies copied
  fields and capacity, not semantic retrieval/model accuracy. See
  `real-field-component.json`.
- Full `tests/` suite on committed e1d7e8b PASSED6695 +1595 subtests,6 skipped,
  2 xfailed,6 existing warnings,1364.78s (22m44s),exit0. `full-suite.head`,
  `full-suite.log`,`.exit` bind it. No production/test changes during the run.
  No installed linter/formatter; none run. Git whitespace check passes.
- Fresh read-only Supabase MCP release check: original p09 release active/19chunks;
  expanded p11 release draft/inactive/80chunks. `hosted-release-readback.json`.
  All54 sealed package files match their saved lengths/hashes; seal SHA256 remains
  `137dbe0e7558f50fd7c6f95dfb6babd45fc71e431265d7291ac36b0c50e3c924`.
- Delivery verification checks unchanged tested code, final suite exit/counts,
  live failure classification and inactive-release readback;19 evidence files
  sealed and40 local links resolve. Manifest SHA256
  `974ee73e7dd4a5704c790f201c6bf176fc3e6957bd25f000c2773b76400ddde3`.
  Phase-state validation passes; no Phase11 completion/advancement is claimed.

## Bounded live replay and remaining gates

The existing model container was stopped after Docker restarted. Started that
same installed container; no rebuild/download/model setting change. Reused exactly
one saved question: “What is the sanction for fraudulent admission requirements?”
against the inactive local80-chunk package. No hosted activation/pin switch.

The router requested Hybrid and an irrelevant prerequisite operation while its
only part was documentary. Result: `evidence_unavailable`, route null, no retrieval
or generation. Reply: temporarily unavailable.43.469s resident-model inner-pipeline
time includes routing, excludes composition/encoder startup/browser/API, and does
not isolate queueing. It is a failed-run duration, not successful answer latency.
`live-fraud/integration.json` and `model-outputs.jsonl` distinguish this failure
from the correction. No retries, router patch or additional model experiment.

The live gate remains open. Other known service/plagiarism routing, omitted steps
and progression, Hybrid/clarification/Nursing questions and the simple-query battery
remain. Preserve all release/roster/switch gates and frontend integration deferral.
The checker experiment is closed; thinking stays disabled. The previously verified
malformed-source guard was not reworked; ordinary regression coverage remains.

The correction is verified as a software increment. The next action is focused
recovery of the fraud question's spurious structured routing operation, followed
by the remaining expanded-candidate quality failures. No source switch or phase
advancement follows from this delivery.
