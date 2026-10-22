# Phase 06 partial review export design

Status: explicitly approved by owner with review03 on 17 October2026; implemented
at `6fedc45`. [Generated delivery](2026-10-17-phase06-prolog-review-delivery.md).
The earlier generic "ok proceed" did not answer review03; its later explicit
approval is separately recorded. Reviews01/02 remain settled.

## Purpose and evidence path

Students eventually need correct version-scoped prerequisite lookups/checks.
This increment advances the compiler/provenance part of Phase06 Task2 by producing
reviewable candidate `.pl` data and an exact coverage report. Input is the existing
source-bound authoring ledger; the reviewed records remain the authoring truth.
Prolog files are generated derivatives, never independently maintained policy copies.

Current preparation contains ten records, six with owner-reviewed direct rules.
The strict preview refuses the entire selection because four reference records
remain drafts/unresolved. Three printed prerequisite cells are blank. This is a
compiler boundary, not missing extraction evidence: inventing complete rules for
those rows would violate the source-gap policy. Their unknowns must survive export.

## Proposed boundary

Add `compile_curriculum_review_bundle(ledger) -> dict` in
`backend/bintanong_symbolic/compiler.py`. Preserve `compile_curriculum_preview`
behavior/output/version. Reuse complete-ledger reconstruction, exact digest-bound
review validation, expression traversal and strict atom quoting. No new dependencies.

The new function is pure, deterministic and detached: it returns text/JSON in memory.
It does not write files, consult Prolog, calculate eligibility, register operations
or change source states. A separate offline delivery script may save returned text
as `.pl` and JSON only under ignored workspace audit-evidence for human review.

**Chosen authoring boundary:** a course's supplied fields are reviewed only when
its exact current record has `review_state=reviewed` and valid review references.
Do not use a stale receipt or auto-approve a draft code because another course
mentions it. The existing authoring schema does not authenticate a reviewer or
prove institutional authority. Partial export must state that trust boundary.

## Coverage and export rules

Return one coverage entry for every course: course_id/source_version_id,
identity_review (`reviewed` or `draft`), direct_rule (`reviewed`, `draft` or
`unresolved`), and ordered references to identities whose human review is pending.
Coverage entries carry course digests, review refs, unresolved reasons and source
spans through the full normalized ledger. Coverage never means official eligibility.

- Export `candidate_fact` values only for reviewed course records. Missing fields
  remain absent. Do not derive numeric units or remove `/L`.
- Export `candidate_requirement` only for a reviewed course whose entire authored
  expression has no unresolved node. Preserve course/co_requisite/all_of/any_of/
  verified_none exactly as already reviewed; no partial-tree pruning.
- If such an expression references a draft course identity, retain the approved
  target expression for human comparison and flag those identity dependencies.
  That reference's own prerequisite conditions remain unknown. This is a partial
  **review artifact**, never a claim that the referenced identity or chain is ready
  for runtime. Unreviewed reference facts/rules are never emitted as reviewed facts.
- Emit `candidate_reference_identity` for each course, including its source,
  digest, exact printed code and explicit identity review status. Draft names are
  labeled draft in the same ground fact; they only let the human follow references.
- Emit `candidate_coverage` for every course. A course with an unresolved condition
  has no `candidate_requirement`, even if its identity/blank reading is reviewed.
  A missing requirement never means verified_none. Preserve the reason in coverage.
- Preserve complete source records, authoring records and review receipts as
  canonical JSON atoms for audit, including their declared review states. Their
  presence in audit predicates does not add them to semantic facts/rules.

Do not compute transitive completeness or treat absence of an edge as evidence.
Version/scope binding is validated by the existing authoring contract. Dangling,
cross-version or private-namespace references and forged ledger metadata reject.

## Global diagnostics and status

Cycle checking inspects prior-completion edges in reviewed, unresolved-free
expressions only. All alternative branches are conservatively inspected. Draft
speculation must not create a cycle that blocks unrelated reviewed output.
Use a deterministic cycle witness; if found, hold the entire review bundle and
return null Prolog. Co-requisites remain distinct from prior-completion edges.

Strict quoting failure in any exported/audit text also holds the entire bundle
with `unrenderable_text`, preserving original source values. Never normalize policy
content silently. Invalid authoring input rejects before export.

Output includes a distinct compiler version, ledger SHA-256, full ledger, source
states, per-course coverage, diagnostics, release holds, Prolog text/digest and a
digest over the complete result. Status values:

| Status | Meaning |
| --- | --- |
| `partial_review_candidate` | Ground candidate data emitted with at least one draft identity, unresolved/draft direct rule or pending reference identity |
| `review_candidate` | All supplied identities/direct expressions reviewed and structurally complete; source authority/activation still held |
| `blocked` | No Prolog due to cycle or rendering failure |

Zero reviewed expressions still produces a clearly partial identity/coverage audit
artifact, never a runnable capability. Every output has `activation_allowed=false`,
`eligibility_executable=false`, `approval_id=null`, `runtime_ready=false` and
`partial_coverage_requires_explicit_handling` among its release holds. Retain all
source lifecycle states, synthetic labels and existing institutional holds.

## Human review delivery

When implemented/verified, generate one bundle per curriculum, with its `.pl`, JSON
coverage manifest and a plain-language table mapping each emitted expression to
the exact original page/region and existing approval receipt. Include pending
identity/condition readings in a separate clearly pending column. Do not ask again
for settled rule meanings; generated translation correctness remains reviewable.
No real-source eligibility query is executed by this increment.

Review03 subsequently received explicit approval, applied in the linked delivery.
Independently prepared old CC1/L remains a draft reference identity; its inclusion
does not establish reviewed identity or its own prerequisite coverage.
Do not expand to an entire curriculum to fill blank prerequisites.

## Implementation and verification boundary

After design approval, write a focused inline TDD plan in `plans/`. Changes stay in
the symbolic compiler/README plus synthetic `tests/test_symbolic_review_bundle.py`.
Prove partial export with reviewed target + unresolved draft references, reviewed
unknown distinct from verified_none, unreviewed facts absent, nested ordered logic,
cycle/co-requisite separation, strict quotation/injection data, stale receipts,
scope/privacy rejection, deterministic hashes and strict-preview compatibility.
Parse synthetic output only as ground data with installed SWI-Prolog and a timeout.
Reuse the Python3.13 readiness venv; no installs, weights or dependency/lock changes.
Then run related regressions/docs/phase validation and one final independent review.
Actual source-derived artifacts stay ignored. Full Phase06/runtime/release remain open.

## Design review and independent preparation

Fresh builder check on 17 October: "nothing important left". The owner subsequently
approved the complete description and review03 explicitly. Implementation/source
decision scope is bound to that later actual reply, not the generic continuation.

A separate old CC1/L reference stub is prepared at ignored workspace
`audit-evidence/p06-partial-export-preparation-20261017/`. It is **draft**, with an
unresolved condition and a code span used only as a row locator. Its original
native range is physical1 chars698–704, exact text `CC 1/L`; original hash/box/page
size were independently verified. It is not added to the delivered ten-record
selection or represented as an approved old CS1/L relationship.

`old-readiness-ledger.json` validates the stub alongside the five unchanged old
records: six old records, three reviewed, three drafts. Existing source/review
records remain identical; strict compiler remains blocked with null Prolog.
Preparation/replay checks verified all15 previously sealed extension files,
original byte hashes, native text/box, unordered deterministic rebuild and exact
compiler replay. Review03 proposals remain pending and unchanged.

Recovery: existing Python3.13 readiness executable, `-B`, then
`C:/Coding-projects/bintanong_workspace/audit-evidence/p06-partial-export-preparation-20261017/prepare_reference_stub.py`,
then repository absolute path. Preparation exits0; verification.json records the
separate replay and unchanged-source checks. Raw JSON/scripts/logs stay untracked.
This is reversible data preparation; no product behavior change or install.

Docs/phase: **539 passed / 11 subtests, 11.63s**, exit0 (`docs.log`).
Preparation manifest: 9 files, SHA-256 `e751b7f46d54719c8a4042a6ab3bc28364b72b250e9ce0e2ae73f11cddfb26d8`.
No compiler code or `.pl` was emitted during that earlier design increment.
The subsequent approved implementation/delivery is linked above.
