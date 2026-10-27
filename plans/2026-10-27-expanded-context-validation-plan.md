# Expanded corpus context validation plan

**Goal:** Verify whether the staged465selection can supply complete cited student
procedures/policies through the existing context assembler before activation.
**Baseline:** Undergraduate scope,source-gap/service-association policies and
[hosted staging results](2026-10-27-hosted-corpus-staging-results.md). Prior source
approvals remain settled. No activation,source promotion or frontend integration.
**Architecture:** Read immutable staged artifacts;use existing Chunk contracts,
reviewed-field renderer,record-group validator and runtime context builder with
the pinned local E5 tokenizer. Keep diagnostic output ignored in workspace evidence.
No production behavior changes;data-only inspection uses assertions and relevant
existing tests instead of an artificial implementation RED/GREEN cycle.

## Tasks

- [x] Audit all465chunks and complete transitive companions through existing
  runtime assembly,including exact citations/field bindings/group ordering.
- [x] Count exact serialized E5 context tokens with shared citations/group metadata;
  compare default2048budget and existing subject overrides. Preserve whole groups;
  never truncate words or omit limits to pass a budget.
- [ ] Inventory actual source/format defects and missing structural bindings.
  Distinguish source defects from packaging defects and parser acceptance from
  independent image/table association evidence. Repair only from settled visible
  evidence;new consequential source choices require a focused human review.
- [x] Apply source-backed packaging corrections in separate derivatives if needed,
  verify source/field/limit conservation and exact token counts. Production fixes,
  if required,follow focused synthetic TDD before changing behavior.
- [ ] Run relevant existing context/group regressions,record results and remaining
  runtime/answer gates,and commit a resumable checkpoint. Answer experiments follow
  structurally usable context;do not infer activation or complete coverage.

**Acceptance:** Every member classified with original physical pages,explicit
assembly/budget result and companion closure;no invented source content or
unexplained dropped fields. Any unresolved gate stays visible and draft inactive.
This advances complete student procedure answers;it is not a similarity/model sweep.

First pass: [results and corrected derivative](2026-10-27-expanded-context-validation-results.md).
105tests/121subtests pass;source-backed format corrections complete. Independent
structural evidence,expanded catalogue and per-subject runtime checks remain open.
