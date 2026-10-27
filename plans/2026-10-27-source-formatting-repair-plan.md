# Source Formatting Repair Implementation Plan

> Execution: inline with the existing reviewed-policy builders; preserve the active Phase11 gates.

**Goal:** correct the three concrete delegated-review packaging defects without changing source wording.
**Architecture:** immutable336input overlay;separate source-derived correction overlay and old/new map.
Reuse existing pending-policy builders,source contracts and local exact E5tokenizer. Native character
ranges and original glyph boxes bind new fields;whole companion groups are rebuilt together.
**Spec:** [delegated comparison/results](2026-10-27-delegated-source-review.md),
[service associations](service-table-association-policy.md),active Phase11plan and source-gap/scope policies.

## Constraints and validation

- No productrequirement/productionbehavior change;reuse the approved baseline,no new PRD approval.
- Source-data reauthoring only. Existing builder regressions plus executable before/after data
  assertions verify the repair;no production code/dependency/lock/model/hosted changes.
- Preserve originals,336baseline,human/assistant review receipts,all gaps and unaffected chunks.
- Move only printedfooter110to audit/provenance;no other nonblank source glyph may disappear.
- Separate metadata/requirements/headings/totals and source-backed time/person/office values.
- Preserve complete borrowingcontinuation and every required companion;no guessed geometry.
- Exact E5tokens<=480,no truncation;split at field boundaries if required and retain full group links.
- Corrected candidates remain pending/inactive;no activation/embedding/rules/frontend work.

## Tasks

- [x] Pin inputs and inspect three records/original page images.
- [x] Run focused data assertions on the current336overlay;observe the three known failures.
- [x] Reauthor feedback,borrowing and computer-use groups with existing builders and exact native spans.
- [x] Verify GREEN,sourceglyph conservation,unchanged candidates,gap/approval mapping,repeat determinism,
  contracts,complete neighborclosure,original hashes and exact token counts.
- [x] Run existing reviewed-policy/service-context regressions with external basetemp,no pytest cache.
- [x] Record output seals,repair map,verification evidence and remaining broader structural gates.

Commands:sharedPython3.13 -X utf8 -B <ignoredrepairscript>;focused before/after assertions;
pytest test_reviewed_policy_preparation.py,test_reviewed_policy_chunks.py,test_reviewed_service_context.py,
test_reviewed_service_steps.py,test_reviewed_record_context.py,test_reviewed_descriptive_context.py,
test_reviewed_flowchart_context.py;git diff --check;phase_state validate.

## Delivery

All tasks verified;see[results](2026-10-27-source-formatting-repair-results.md).
Three concrete records repaired;broader structural gates remain as recorded there.
