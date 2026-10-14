# Shared citation context implementation plan

> Execute inline with the executing-plans and test-driven-development workflows;
> use one independent review at the end.

**Goal:** Reduce repeated citation metadata for complete policy groups while
preserving every reviewed field, limitation, citation and default behavior.

**Architecture:** Add `shared_citations=False` to `build_context`. When explicitly
enabled, serialize a context-wide source/page table and exact common locator
defaults, followed by chunk blocks with source indexes and residual locators.
Reconstruct each original locator by merging its source's defaults and residual.
Keep each evidence item's text and structured citations unchanged. Tokenize the
complete proposed display at every admission; required groups remain atomic.

**Stack:** Existing Python 3.13 and local SEA-LION tokenizer; no new dependency.
**Spec:** The next action in
`2026-10-14-confirmed-policy-applicability-report.md`, continued by the owner.

## Global constraints

- Preserve the existing full and compact citation formats unless explicitly opted in.
- `shared_citations` must be a boolean. It selects the shared format independently
  of `compact_citations`; both existing defaults remain false.
- The source-table key is the exact version ID, byte hash and physical page.
  Common locator defaults require identical JSON values and keys present in every
  locator for that source/page. Preserve original keys, values and citation order.
- Keep exact chunk IDs, complete member payloads, fields, blank markers, groups,
  unresolved source limits and full structured evidence unchanged.
- Recompute the source table/defaults from accepted plus trial evidence before
  exact budget admission. Refused trials cannot change already accepted context.
- Reuse accepted questions, ranks and all saved vectors; no model inference,
  source conversion, installs, runtime/default activation or new benchmark questions.
- Candidate use remains provisional undergraduate research. Shared audience
  selection is settled; school validation and formal Phase05 exit remain pending.
- Use ignored workspace audit-evidence; preserve owner artifact changes.

## Review focus

1. Same locator on different pages/versions must resolve to its own original source.
2. Missing keys, empty values and JSON-distinct values such as `false`/`0` must
   round-trip exactly; defaults must not invent keys or merge distinct values.
3. A failed trial must leave earlier context and token counts unchanged.
4. Complete reviewed record/flowchart groups must still reject missing neighbors,
   tampered manifests or citations, including when starting from a later part.
5. Default full and existing compact outputs must remain exactly compatible.

## Task 1: Optional shared citation display

**Files:** `backend/bintanong_retrieval/context.py`,
`tests/test_retrieval_context.py`, `tests/test_reviewed_record_context.py`,
`tests/test_reviewed_flowchart_context.py`.
**Consumes:** Validated evidence items from the existing `build_context` admission.
**Produces:** `build_context(candidates, budget, count_tokens, *,
compact_citations=False, shared_citations=False)` with unchanged result keys.
The new context prefix identifies `shared-source-locators-v1`; each source entry
has `version_id`, `byte_sha256`, `page`, `locator_defaults`. Each block contains
the original chunk ID, source-indexed ordered locators and exact original text.

- [x] Run existing context tests as a fresh baseline; write synthetic tests proving
  full group recovery below the former display budget and lossless citation decoding.
- [x] Observe expected RED for the absent shared-citation keyword.
- [x] Implement the smallest serializer addition and use it for trial/final counts.
- [x] Verify GREEN plus record/flowchart tampering, atomic-budget and default tests.
- [x] Run the full pytest suite without cache and with external basetemp; record
  commands/results and commit explicit verified code/tests/ledger paths.

## Task 2: Real offline comparison and closure

- [x] Verify the previous seal and bindings; reuse 21 chunks, 36 queries and existing
  scoped rankings. Independently tokenize the new assembled displays with the
  already bound local tokenizer, without loading model weights.
- [x] Compare complete-group minima and the same 900 context observations; decode
  every emitted citation back to the original and check unchanged fields/gaps.
- [x] Dispatch one fresh final reviewer for code/default/atomic-group correctness
  and evidence accounting; resolve Important/Critical findings in one TDD fix pass.
- [x] Commit a curated report and update checkpoint, progress, INDEX and blocked
  handoff. Seal ignored evidence; validate phase state with advancement still blocked.

## Preflight and recovery

Verified baseline `ee38320`; product code `f9b1502`. Already in the existing linked
worktree `p05` on `feat/p05-retrieval-logic`; preserve `artifacts/.gitkeep` deletion
and untracked `backend/artifacts/`. Actual thesis physical17–18, routing PNG,
master section10, Phase04/05 records and scope/source-gap/dataset policies consulted;
no scope or routing discrepancy. Source-only text plus chunk IDs already consumes
1509 overload/1536 timing tokens, so recovery under2048 must be measured, not assumed.

Self-review: one optional serializer interface, no producer/consumer mismatch;
all five review inputs have regression coverage planned. No new source-content
retention choice or owner question is required. If complete groups still exceed2048,
retain intact withholding and report the measured limit; do not truncate content.

## Task 1 verified delivery

Optional shared-citation context verified under plan1e260ec. Full pytest:
5252passed/497subtests/6skipped/6warnings in315.28s, exit0; related82passed/
97subtests1.54s after observedRED. Exact900default-format observations unchanged;
900shared observations/17strings/212archived citations/6855citation instances
round-trip.1467prior hashes preserved with exact baseline snapshots for authorized
tracked edits; original/source/register/vector/question/rank bytes untouched.
At k3/0.5,2048complete expected24/30→27/30 (policy12/18→15/18);4096still30/30.
Timing2270→1917tokens nowfits2048; overload3186→2265 still withheld intact.
68exact old/new/trial counts; no invalidcontexts or selectedthreshold. No model
inference/runtime opt-in/activation. Next verified code commit, one final fresh
review, documentation/phase checks and evidence seal. Source decisions settled.

## Final verification

Final review: independent verification PASS, no Critical/Important/Minor findings.
Separate source-reference decoding, exact token counts and complete-group budget
replay agree with saved results; prior1467 hashes remain preserved through explicit
old-byte snapshots for authorized tracked edits. No calibration/source-authority/
activation claim is made by these technical checks; existing gates stand.
