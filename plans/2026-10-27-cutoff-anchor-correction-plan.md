# Cutoff notice anchor correction plan

Execute inline using the executing-plans workflow. This is a source-data correction
through unchanged existing codecs, not a product-scope or production-behavior change.
No artificial PRD or full production-suite repeat is needed; validate actual data
with a failing regression first, conservation checks and relevant codec suites.

**Goal:** attach the two existing unresolved notices to the exact preserved cutoffs.
**Spec:** [release closure checklist](2026-10-27-expanded-release-closure-checklist.md),
source-gap policy and owner's reminder to preserve source cutoffs,27October.
**Architecture:** derive a new inactive465 selection from the normalized candidate;
reuse make_source_limits/serialize_reviewed_fields and immutable correction receipts.
Source fields, original spans, existing review events and source governance stay exact.

## Files and interfaces

Ignored evidence root:workspace/audit-evidence/p11-cutoff-anchor-correction-20261027.
Create test_cutoff_anchors.py (data regression),correct_cutoff_anchors.py (derivation),
verify_correction.py (independent conservation),corrected-candidate-chunks.json,
correction-receipts.json,id-map.json and package-status.json. Track only this plan,
the results and current handoff updates. Production files/tests remain unchanged.

## Acceptance and task order

- [x] RED: run two exact-field regressions against the normalized465 baseline.
  H60 must name step3_process with literal `Complet e &`;H64 must name
  step9_details with its exact sentence ending `during`. Verify span indexes,
  physical page and unresolved affected claims. Expect two assertion failures.
- [x] GREEN: reconstruct the two notices through make_source_limits,relocating
  H64's notice to its final existing companion. Re-serialize only affected contexts,
  count exact E5tokens without truncation and deterministically rebind affected
  dependency identities. Never invent a source continuation or declare resolution.
- [x] Verify all465source_text/fields/spans unchanged,all other limits unchanged,
  complete dependency closure,contract/context parsing and original/package/pin
  hashes. Repeat derivation byte-identically;record stale downstream artifacts.
- [x] Run focused source-limit/chunk/context/retrieval suites,docs/phase checks,
  inspect the diff and commit the verified source-data delivery documentation.

## Review focus

Check wrong-field notices even when affected-claim counts are conserved;H64's
cross-chunk relocation;blank/unknown semantics;source-gap persistence in complete
context;identity/embedding/catalogue staleness. No new wording review,model call,
budget/default-selector integration,hosted write,activation or branch advancement.

Data correction and focused checks delivered;[results](2026-10-27-cutoff-anchor-correction-results.md).
