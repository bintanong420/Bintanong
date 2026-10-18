---
artifact: phase-plan
phase: 6
status: complete
master: plans/master_implementation_plan_original_long.md
previous_handoff: plans/phase-05-handoff.md
---

# Phase 06 — structured knowledge and deterministic reasoning

Use executing-plans inline. Master sections3/11/13 and the Phase 05 final handoff
supply the architecture; the owner approved the authoring-ledger increment on
17 October 2026 via “Approve the authoring-ledger increment”. Later implementation
boundaries retain their applicable design/source/runtime approval requirements.

## Approved completion boundary - 18 October 2026

The owner approved offline Phase06 completion for the reviewed BSCS subset and
keeping university verification, normal institutional runtime and activation as
separate release holds. After the requested recap, the owner explicitly said
"Yes, go ahead, with phase05 being your reference" and authorized fast-forwarding
to the Phase06 mainline. No additional issue was supplied. This supersedes the
older blocked recovery condition for this milestone only, following Phase05's
offline closure pattern. No institutional approval, activation or Phase07 work.

Exit:verify the source/review/bundle identities, actual73-case BSCS acceptance,
deterministic/unknown/error/isolation behavior and relevant regression evidence;
complete the handoff, supersede the checkpoint, update INDEX and validate/can-advance.
Four own-rule unknowns and full-prospectus extraction defects remain explicit.
Generated candidate PL remains review data; the typed runtime evaluates the checked
JSON projection in the fixed Prolog engine. See the complete handoff and
[specification/closure report](2026-10-18-phase06-offline-closure.md).

## Goal and constraints

Student capability: version-scoped exact course facts and, later, source-supported
prerequisite/dependency checks with provenance and explicit unknowns. Reviewed
records/specifications are authoring truth; generated Prolog is a derived artifact.
Reuse the delivered inactive candidate compiler; do not rebuild ingestion or route
eligibility through vector similarity. Undergraduate academic affairs only.

The original first increment was pure Python validation, no Prolog, eligibility result, database,
network, model, source-state promotion, installation or activation. Original data
and existing contracts/compiler/EMPTY_REGISTRY remain unchanged. Synthetic tracked
fixtures only; actual source records/outputs stay ignored under workspace.

## Approved first interface

Create `backend/bintanong_symbolic/authoring.py` and package marker; expose:
`build_curriculum_ledger(scope, sources, courses, *, reviews=()) -> dict`.
Reparse existing SourceDocumentVersion/SourceSpan contracts; return detached,
canonical JSON-compatible authoring records with a content digest, always inactive.
Scope requires program_id/curriculum_id; each course repeats those exact identities
and its source_version_id. Unknown source applicability is retained, not promoted.

Closed course keys: course_id, program_id, curriculum_id, source_version_id, facts,
prerequisites, review_state, review_refs. Facts are named value/source_spans records:
course_code required; course_title, units.total/lecture/lab, year_level and semester
optional. Missing values remain absent; units are finite nonnegative numbers,
booleans excluded. Each supplied value requires literal original-span support;
source version/hash/page/locator binding must match the owning record.

Prerequisites are explicit recursive data, never parsed/inferred from raw text:
course/co_requisite leaves reference scoped course_ids; all_of/any_of contain
nonempty ordered items; verified_none is a separate terminal; unresolved carries
a nonblank reason. Each node has complete source_spans. An unresolved node cannot
be replaced by an empty conjunction. No expression is evaluated in this increment.

Review records contain review_id/source_version_id/course_digests/reviewer_label.
course_digests binds exact normalized record content, excluding its review state/
references; altered facts/logic cannot reuse a stale review. Prepare drafts first.
Ruling: exact content binding is necessary to validate the approved review references;
it adds no authority or execution, and avoids misattributing an altered translation.
References must resolve and cover the same course/version; reviewed records need
a reference. Attribution is declared researcher input, not authenticated office
approval. An authoring reviewed label does not change source lifecycle authority.
Preserve supplied evidence and reviewed expression structure. Sorting is only for
unordered source/course/review collections; node/span order is preserved.

## Review focus

- Same course code in another version/program must not supply evidence or references.
- Numeric values need exact support, not a token found inside an unrelated amount.
- Empty/missing prerequisites cannot imply verified none; no automatic eligibility.
- Private-session data, forged extra fields and dangling review references reject.
- Caller input mutation and unstable ordering must not change authoring identity.

## Tasks and verification

- [x] 1. Approved authoring ledger: focused RED, minimal GREEN, meaningful boundary
  regressions; README describes caller trust and deferred functionality.
- [x] 2. Separately design reviewed specification → versioned Prolog compilation,
  source/review gates, unresolved references and cycle reporting; reuse candidates.
  Owner resumed Phase 06 in p06 on 17 October; the previously approved compiler
  proposal starts with the [bounded offline preview](2026-10-17-phase06-foundation.md).
  Source-to-rule reviews and partial compilation were subsequently delivered.
  The [partial review export design](2026-10-17-phase06-partial-review-export-design.md)
  was approved and implemented at `6fedc45`, preserving reviewed expressions alongside
  explicit unknown reference coverage. [Generated delivery](2026-10-17-phase06-prolog-review-delivery.md).
  Returned reviews now cover all seven modeled relationships; release holds stay separate.
- [x] 3. Separately authorize and implement typed Janus integration/registry with
  immutable bundles, request-local facts, timeout/result/concurrency limits.
  Synthetic and explicitly authorized actual-data offline paths are delivered;
  global institutional EMPTY_REGISTRY and normal institutional execution stay closed.
- [x] 4. Verify eligible/ineligible/unknown/unsupported/error and deterministic
  explanations across supported rule families; record formal phase exit evidence.

Task 1 tests: `tests/test_symbolic_authoring.py`; related existing tests:
`test_contracts_symbolic.py`, `test_rule_candidates.py`, `test_prospectus_rule_handoff.py`.
Use existing Python3.13 readiness venv, `-B -m pytest -q -p no:cacheprovider`, external
TEMP/TMP/basetemp under workspace/audit-evidence/p06-authoring-20261017. No installs.
Run focused tests RED/GREEN, related regressions, one final focused review and
applicable docs/ledger checks. Commit verified cohesive increments explicitly.

## Formal phase exit

Master11.5 requires deterministic supported decisions and explanations for fixed
inputs/rules, without false approval or unsupported definitive denial on missing
information. The approved offline milestone meets this for the reviewed BSCS subset;
institutional source authority, normal release runtime and activation stay separate.

## Context and baseline

Phase 05 closure38fe57c; can-advance succeeded before starting this plan. Existing
isolated p05 worktree retained; owner artifacts changes preserved. Actual thesis
physical17–18/39–44, runtime-routing PNG and master 3/11/13 consulted. Thesis
closed-world missing-grade denial is corrected by master11.4's unknown semantics.
SWI-Prolog is installed; janus-swi is absent from readiness venv. No runtime use,
version upgrade or dependency change in Task 1. Inactive candidate preparation was
already delivered; historical ingestion docs are supporting evidence only.
