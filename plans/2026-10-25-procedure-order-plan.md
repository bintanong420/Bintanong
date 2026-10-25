# Reviewed procedure order implementation plan

**Goal:** reject a simple procedure answer that cites all reviewed steps in the
wrong order, even if the model's ordinary reviewer approves it.
**Spec:** existing Phase11 simple-query requirement, service-table-association
policy, source-gap policy and owner decisions ledger. No new product scope.
**Architecture:** extend the existing claim-review/record-coverage path with an
optional explicit source sequence. Preserve it through retrieval, evidence,
draft guidance, ordinary review and the existing draft/final coverage guard.
No new router/answer path, per-question rules, dependencies or model calls.
Existing unordered records and serialized identities remain unchanged.
**Baseline:**8375cf1 (code4425538), clean p11; full6774+1595 subtests,exit0.

## Contracts and acceptance

- A source claim review may supply `procedure_order`: unique reading IDs for
  all its reviewed, nonblank client_step fields, one document version/hash.
  Existing basis_ref/basis_sha256 bind the reviewed evidence; source order is
  explicitly authored, never inferred from reading IDs, source rank or hashes.
- Existing DocumentRecordCoverage gains optional source_ordered=false. When true,
  chunk_ids is the reviewed sequence. Absent/false serializes exactly as before.
- PreparedEvidence carries only explicitly ordered coverage as record_order;
  include it in the existing review identity only when present. Aliases change
  identifiers, not sequence. Reviewers see canonical ordered references.
- Each required step must be cited by exactly one separate claim, in the reviewed
  sequence within that part's rendered claims. Combined, repeated, reversed or
  interleaved step citations enter existing bounded repair/withholding. This
  validates cited-record sequence, not sentence meaning; ordinary support and
  field/cutoff guards remain necessary. Do not silently reorder model prose.
- Merging preserves identical ordered requirements and rejects incompatible
  ones; unordered coverage keeps existing union behavior. Other topics/parts and
  declared unavailable slots retain existing treatment.

## Task 1 — one connected regression/fix

1. RED synthetic tests in tests/test_procedure_record_order.py for source-review
   validation, shuffled field refs, adapter/merge, old serialization parity,
   review binding, canonical/short draft order, approving reviewer, one repair,
   combined/repeated citations, final bypass, other subject/unavailable slots.
2. Small edits in retrieval/candidate_claims.py, orchestration/contracts.py,
   adapters.py and orchestrator.py, generation/evidence.py and part_answers.py.
   Reuse existing coverage guard at both generator and final validation.
3. GREEN focused and relevant retrieval/generation/orchestration/runtime suites;
   independent scoped review; commit verified code/tests with Conventional Commits.

## Task 2 — existing source evidence and full verification

1. Reuse the reviewed four-step Charter packet/source spans and standing
   delegation. Verify original physical102-103 and explicit ordered reading IDs;
   preserve the absent printed Step2 label, Step3 cutoff and total discrepancy.
   Record this as delegated sequence metadata, not fresh human confirmation.
2. Derive an ignored order-only candidate register/package separately from the
   sealed80-record package. Original54 files, chunks, vectors and source readings
   remain byte-identical; expanded hosted release remains inactive. No DB work.
3. Replay saved wrongly ordered draft through the current deterministic guard,
   no new model completion. Bind original evidence/draft hashes and authoring
   record. Record structural result and remaining semantic/language limits.
4. One full tests/ suite on frozen final code, no cache/external basetemp; save
   head/log/exit/process creation binding. Reuse prior runs for unchanged code.
5. Diff/link/phase checks, compact progress/checkpoint/recovery. No phase advance,
   default profile selection, source activation or frontend work.

Validation: shared Python3.13 -X utf8 -B -m pytest -q -p no:cacheprovider with
unique workspace/audit-evidence/p11-procedure-order-20261025 basetemp; full tests/.
No installed linter/formatter. Current [Pydantic wrap-serializer docs](https://github.com/pydantic/pydantic/blob/main/docs/concepts/serialization.md)
fetched via Context7; use the repository's existing omitted-default pattern.
Consulted thesis physical17-18/routing PNG, master3/13/14/16, scope/gap/association
policies and Phase10 handoff; undergraduate/read-only/RAG-vs-Prolog boundaries stand.
