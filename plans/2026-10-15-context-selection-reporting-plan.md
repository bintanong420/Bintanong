# Offline context-selection reporting plan — 15 October 2026

Baseline: `e8ead56`; active Phase05 plan/checkpoint and master section10 govern.
Spec: the next action in [the prefix diagnostic](2026-10-15-context-prefix-diagnostic-report.md).
The owner authorized continuation. This is an opt-in offline helper, not a runtime
selection policy, claim classifier, school approval or phase exit.

## Design and constraints

Add `build_context_selection_report(candidates, budget, count_tokens, *,
primary_limit=None, compact_citations=False, shared_citations=False,
shared_group_metadata=False)` in `backend/bintanong_retrieval/context_selection.py`.
The caller supplies an ordered candidate list and an explicit prefix length;
`None` requests all, zero requests none. Reject bool/noninteger/negative/oversized
limits. Keep the original builder and engine unchanged. Forward display flags;
retain the exact original assembly result nested under `assembly`.

Report schema `context-selection-report-v1`, `candidate_only=true`,
`activation_eligible=false` and `claim_coverage=unknown` on every path, including
empty, invalid, unrelated and clean contexts. Do not consult queries or gold.
Record each offered primary's rank, identity/version/hash/score, whether requested
and literally emitted, and its local source-declared transitive dependencies.
Resolve dependencies only from that primary and its supplied neighbors, just as
the builder does. Distinguish absent dependency rows, malformed dependency lists,
and required IDs not literally emitted. Preserve the builder's original gaps.
Deferred primaries can already be emitted as another primary's required neighbor.
Absent output IDs can also reflect overlap deduplication: never label them missing
claims or call a group complete from chunk identity alone. No automatic prefix
choice, score threshold, gap suppression, field truncation or input mutation.

## Task 1: implement the reporting boundary under TDD

Interfaces: produces the helper/report above; consumes unchanged `build_context`.
Write synthetic tests first for full/default parity; prefix zero/all/validation;
deferred-vs-refused groups; atomic budget refusal; absent/transitive/cyclic/malformed
dependencies; a deferred primary emitted as a dependency; overlap deduplication;
invalid citations; all display modes/flags; input preservation; unknown coverage.
Run new tests and observe the expected missing-module RED. Implement the smallest
wrapper and verify GREEN plus context/reviewed-policy/engine regressions. Document
the API and its literal-ID limitation. No source-derived fixtures in Git.

## Task 2: replay and verify

Replay all4,390 saved attempts using the exact existing tokenizer and immutable
rankings in a new ignored `audit-evidence/p05-context-selection-reporting-20261015/`.
Verify exact context hashes/tokens/IDs/gaps and trace dependencies/deferred IDs;
all1,350 full-prefix baseline observations remain identical. Compare missing U1
top1 evidence versus omitted U2 extras without importing gold into the helper.
Preserve all source-limit payloads, citations, seals and original hashes. No new
embeddings, wordings, source choices or acquisition. Run the full offline suite.

## Verification and final review

Expected RED: focused import fails because the new helper does not exist.
Expected GREEN: new synthetic tests and relevant regressions pass; replay4390 and
baseline1350 match; full suite passes with existing skips/warnings explained.
Use `-B -m pytest -p no:cacheprovider`, unique external basetemps and existing
Python3.13 environment. Record raw commands/results outside Git and curated
results in repository progress/checkpoint/handoff. One final fresh-context review
is required by executing-plans; reviewer examines the bounded change and preserved
engine/default behavior. Review focus: malformed/cyclic dependencies, duplicate/
overlapping identities, deferred invalid rows, misleading completeness semantics,
and caller-controlled prefixes. Fix consequential findings with RED→GREEN.
Explicit verified Conventional Commits only. Owner artifacts remain untouched.

## Exit and next action

This task exits when reporting, regression/replay evidence and review are committed.
Then prepare representative unsupported/temporal calibration scenarios for owner
wording/expectation acceptance before new benchmark execution. Formal Phase05
gates remain open; no activation or Phase06. Existing approved18/36 wordings,
U1/U2 source confirmations, F04 hold and G01/G02 uncertainty remain settled.
