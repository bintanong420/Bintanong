# Short review reference implementation plan

**Goal:** remove measured canonical-ID overhead from an explicitly selected per-part
review prompt while preserving complete evidence and canonical host validation.
**Baseline:**ba7d8b4/codef635ccc,approved Phase11/master9/23/26 and per-part generation
decision. Existing requirements review:undergraduate students need source-supported,
English/Taglish advisory answers;source gaps,scope,privacy and full checks stand.
This corrects capacity for that capability;no new product scope or PRD approval.
**Evidence:**[current capacity](2026-10-27-559-capacity-results.md),six review samples
overflow. No new phase/research/dependency/model/default-budget change.

## Design and tradeoff

Reuse EvidenceReferences and the existing request-local alias validation.
`confirm_messages(...,references=None)` preserves canonical payloads by default.
An optional `Generator(...,review_reference_profile='short')`,restricted to `parts`,
shortens structured evidence-reference fields in review messages only. Keep source
and claim prose literal,all cards/limitations,required records/order/quotations,
claim IDs,review schema and host-bound review identity. Host drafts/final answers
remain canonical. Existing draft-reference settings remain independent/unchanged.
No RuntimeSettings/default or active research profile switch in this increment.

Rejected:global string replacement (can rewrite source words);source/context
truncation (can hide conditions);larger window/default budgets (not authorized).
Short labels reduce wire size but remain a changed model input requiring actual
semantic validation before selecting this option for any release.

## Tasks and verification

1. [x] Synthetic RED in `tests/test_generation_short_review_references.py` for
   complete structured-reference mapping,unmodified source/claim text,foreign-pack
   rejection,canonical final identity,generator wiring,unavailable/unsupported
   review verdicts and profile restriction. Existing default tests stay unchanged.
2. [x] Minimal GREEN in `part_answers.py` and `generator.py`;reuse codec and
   per-part output/identity checks. Relevant generation/references/order/quote/API
   regressions;then full suite before completion. No assertion weakening.
3. [x] Recheck only the six known overflowing review profiles using actual local
   templates/tokens;compare every source/card/ref/metadata value through the inverse
   alias mapping. No answer-accuracy claim from that fit measurement.
4. [x] Review diff/compile/available quality checks,full test results,docs/phase
   validation;seal ignored receipts and commit verified code/docs separately.

Commands:existing sharedPython3.13.7 `-X utf8 -B -m pytest -q -p no:cacheprovider`,
external ignored basetemp;full `-rs tests`. Evidence root:
workspace/audit-evidence/p11-short-review-references-20261027. Inline execution;
prior worker dispatch failed its account usage limit,so no fresh-agent review is
claimed. Root reviews source/reference conservation independently after GREEN.
Repair reachability and actual model/selector/Hybrid validation remain separate.

Execution:13expected feature failures1.30s;focused192pass3.34s. Two initial test
expectations were corrected to existing behavior:coverage keeps canonical ID order
(step order is separate),and a negative part verdict withholds immediately rather
than spending a second attempt. No existing tests or source/guard assertions changed.
All six review samples now fit;inverse alias mapping restores their exact complete
payloads. Three saved real-source TOR integrations also return the same validated
quote/en-or-Taglish style in six actual model calls. This adds a bounded changed-
path check,not expanded559/Hybrid quality evidence. Fresh full suite:7038passed,
1608subtests,6skip/2xfail/6warnings1388.54s,exit0. Docs/phase30pass/14subtests25.59s;
root diff review/AST/inverse-payload and sealed saved-input checks pass. Fresh-agent
review remained unavailable;no independent agent approval is claimed.
Repair reachability check confirms valid676/677token drafts can exceed the repair
window (8322/8331with reserves);existing overflow refusal remains required.
