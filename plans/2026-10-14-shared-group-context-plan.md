# Shared reviewed-group context implementation plan

> Execute inline with executing-plans and test-driven-development; one independent
> final review checks the completed implementation and actual evidence comparison.

**Goal:** Reduce the complete overload display below its current 2,265 tokens
without removing a field, condition, citation, source limit or group member.

**Spec:** The next action in `2026-10-14-shared-citation-context-report.md`, now
resumed by the owner after feature-branch synchronization at `a6c2c17`.

**Architecture:** Add `shared_group_metadata=False` to `build_context`, requiring
`shared_citations=True` when enabled. Pool exact common service-group metadata and
identical source-limit lists for complete validated multi-part reviewed records.
Display a group index plus residual metadata on each part. Preserve all original
payload strings and integrity digests in the returned structured evidence; replace
the per-part display-only integrity hashes with one group digest binding original
member chunk IDs and payload strings. Store the group defaults and digest alongside
the existing shared citation-source table. Count this exact trial display before
atomic admission, rebuilding the table after every accepted/refused trial.

**Stack:** Existing Python 3.13 and bound local tokenizer; standard-library JSON
and hashing only. No dependency, model, vector, runtime or source-schema changes.

## Global constraints

- All existing formats and result keys remain unchanged with the new flag absent
  or false. Neither defaults nor runtime callers opt in.
- Both flags are explicit booleans; the group option requires shared citations.
- Only successfully contract-validated marked records with service-group metadata
  qualify. Generic source text containing similar JSON is never reinterpreted.
- Pool groups by exact logical ID, document version and source hash, retaining
  ordered original chunk identities, part orders and reading IDs. Never merge
  records from different sources or versions with the same logical ID.
- Every source field, blank/state marker, source-limit message and locator remains
  fully displayed or reconstructable by exact defaults plus residuals. Only
  display integrity digests change representation; all originals stay in evidence.
- Default comparison is byte-exact. Group-context reconstruction compares every
  original payload property except the explicitly replaced display integrity hash.
- Complete groups still fail on missing neighbors, tampered manifests/citations
  and insufficient budgets. Do not admit partial content to meet 2,048 tokens.
- Reuse all accepted questions, ranks, vectors and original candidates; no new
  benchmark wording, model inference, conversions, installs or institutional approval.
- Keep ignored source-derived evidence under workspace audit-evidence, preserve
  owner artifact changes and historical remote review documents. Phase 05 stays active.

## Review focus

1. Generic JSON must remain exact text; only validated reviewed groups may be pooled.
2. Equal logical group IDs on different versions/hashes cannot share defaults.
3. Missing optional metadata keys and JSON-distinct values must reconstruct exactly.
4. A rejected trial cannot mutate prior group/source defaults or tokens; every
   field and unresolved limit must remain attached to its original part.
5. Existing record/flowchart integrity checks, atomic budget and all older formats
   must survive without runtime opt-in or changes to immutable candidate payloads.

## Task 1: Optional reviewed-group display

**Files:** Create `backend/bintanong_retrieval/group_display.py`; modify
`backend/bintanong_retrieval/context.py`; add focused tests to
`tests/test_retrieval_context.py`, `tests/test_reviewed_record_context.py` and
`tests/test_reviewed_flowchart_context.py`.
**Consumes:** Validated evidence and the chunk IDs marked as complete reviewed
group members by the existing admission path.
**Produces:** `prepare_group_display(items, reviewed_group_chunk_ids)` returns
`(group_defaults, displayed_text_by_chunk_id)` without modifying either input.
`build_context(..., shared_citations=True, shared_group_metadata=True)` uses
`shared-source-groups-v1` only when qualifying groups are present. Group entries
include exact shared service/payload metadata and a digest over original ordered
member IDs/text; part JSON contains `group_index` and residual metadata.

- [x] Verify fresh baseline and write synthetic regressions for complete group
  recovery, source limits, generic-JSON rejection, defaults/identity preservation.
- [x] Observe expected RED for the missing group option/helper.
- [x] Implement the minimal codec and admission plumbing; observe GREEN.
- [x] Run related suites and full pytest without cache/external basetemp. Commit
  explicit verified code/tests and checkpoint/progress with actual commands/results.

## Task 2: Saved-evidence comparison and closure

- [x] Verify prior seals/bindings and preserve old bytes for authorized code/test
  changes. Reuse 21 candidates, 36 questions, saved ranks and all vector artifacts.
- [x] Replay 900 existing context observations; independently reconstruct all
  policy properties/citations, compute exact group minima and 2K/4K coverage.
- [x] One fresh final reviewer checks code/defaults, group integrity, token
  accounting, preservation and real negative controls. Fix any consequential
  finding in one TDD pass; do not invent source-content decisions.
- [x] Commit curated report/ledger/handoff/INDEX; seal raw evidence and verify
  phase validity with formal advancement still blocked.

## Resume evidence and recovery

Baseline `a6c2c17`, product `dea9442`; existing linked p05 worktree and feature
branch retained. Prior push completed; do not repeat its merge/receipt steps.
Actual thesis physical 17–18, routing PNG, master section10, Phase04/05 handoffs
and scope/source-gap/dataset rules consulted; no discrepancy. Shared undergraduate
audience decisions remain settled. Owner `artifacts/.gitkeep` deletion and untracked
`backend/artifacts/` remain untouched. Use the already authorized environment and
existing external MODELS. No new source-retention decision is required for metadata.

Self-review: one optional codec/admission interface, five explicit regression
classes, immutable evidence and defaults preserved. Per-part hash replacement is
display-only and stated explicitly; do not call it byte-identical payload display.
If the complete group still exceeds2K, report the exact count and retain withholding.

## Task 1 verified delivery

Shared reviewed-group context verified under plan0b2b405. Fullpytest5264passed/
500subtests/6skips/6existing warnings in302.92s, exit0; related95passed100subtests
1.80s after observedRED. Actual complete overload2265→1961tokens, timing1917→1738;
15/4citations retained. k3/0.5 complete expected30/30 atboth2048/4096 (18/18policy);
budgetgapcases12/3 refer to rejected extras, invalid0. SixBSCSscopeholds remain.
900prior shared observations unchanged;900new/18strings/245archived citations/
7683citation instances/57old-new-trial counts. All source fields/limits/groups
reconstruct exactly except explicitly replaced display hashes; original payloads
and hashes remain exact in structured evidence.1501prior hashes/four old snapshots
preserved; no model encoding/new questions/activation. Report:
2026-10-15-shared-group-context-report.md. Next verified code commit, one fresh
review and curated closure. After this measured budget recovery, next gate is
owner-reviewed unsupported-query proposals before calibration; no more text shrinking.

## Final verification

Final review: independent verification PASS, no Critical/Important/Minor findings.
Separate group/source display reconstruction, budget admission, exact token counts,
original payload/field/limit/citation preservation and prior1501hashes/four new
baseline snapshots verified. Per-part display hashes are explicitly replaced by
a bound group digest; originals remain exact in evidence. Positive-only calibration,
institutional source approval and runtime activation remain separate existing gates.
