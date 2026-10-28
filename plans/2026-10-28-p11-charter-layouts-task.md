# Charter layouts lane task — 28 October 2026

## Scope and baseline

Execute Codex A in the owner-approved Phase 11 workstream split. Baseline `12ac411`;
branch `feat/p11-charter-layouts`, isolated Orca worktree `p11-charter-layouts`.
Own only `service_steps.py`, its parser/render tests, and layout review/evidence records.
Central progress/checkpoint remain with Claude. No host integration, dependency, source,
hosted-state, model calls, activation, or release changes.

Orca created this worktree from p11 HEAD and copied ignored `.env`, `dataset`,
`.superpowers`, and `supabase/.temp` with setup-hook copy semantics. No installs.
Shared Python 3.13 venv used, UTF-8, no bytecode/cache; temporaries and source-derived
outputs stay under workspace `audit-evidence/p11-charter-layouts-20261028`.

## Baseline requirements and context consulted

Reviewed master §§3/14 and lane plan plus original printed-service plan/results,
Phase 11 plan/checkpoint, Phase 10 handoff, INDEX/current progress, scope/gap and
service-table association policies, dataset guide and owner ledger. Existing approved
baseline reused; no new product requirements. Thesis physical17–18 and39–44 read;
runtime routing PNG inspected. Undergraduate/read-only scope and RAG/document path
remain unchanged. Phase inspect valid; checkpoint points at eedbc07, whereas lane
fork is12ac411; Claude owns reconciling central state. No phase advancement.

## Dependency tasks, acceptance, verification

1. Survey all21 refused services by explicit reviewed field family; preserve known holds.
2. Add synthetic failing parser/renderer tests, observe RED, implement narrowly, GREEN.
   Explicit row keys and scoped shared ranges may establish association; list position may not.
3. Preserve exact values, conditional requirements, blanks, source limits and citations.
   Unknown fields, missing/gapped actions, conflicts and incomplete services still refuse.
4. Recheck real559 package: counts for all44Charter subjects, both English/Taglish,
   no model calls; retain per-service refusal reasons/evidence ignored.
5. Run focused service/integration tests and relevant existing guard regressions; request
   root's full-suite slot before suite execution. Review diff and merge current primary
   only if clean/conflict-free before review; no push or merge into primary.

Evidence commands use shared venv `-X utf8 -B -m pytest -p no:cacheprovider` with lane
external basetemp. No formatter/linter configured for this Python module; `git diff
--check` plus focused tests and coordinated full suite verify it.

## Current survey / next action

All21 surveyed in ignored survey.txt. Families: explicit row keys (borrowing/computer),
unnumbered complete record rows (academic requests, claims, library services), numbered
aliases/notes (registration/activity/diploma/readmission), explicit shared field ranges
(CAV/refund/assessment), auxiliary clinical staff, paired removal staff, admission phases.
Initial TOR/complex certification services retain unresolved first-action mappings and
cannot be represented as complete tables; feedback is prose, not a client-step table.
Next: strict aliases/overview scopes and numbered-row family RED/GREEN, then remaining families.

## Unit 1 — explicit row aliases and scoped checklist metadata

RED `red1.log`:3expected failures/11pass; GREEN parser/render/integration24pass
2.89s (`green1.log`). Added strict explicit row fields, title/office/checklist/total aliases,
scoped in/out-campus headings and verbatim notes. Original row numbers survive; gaps and
mixed row/step records refuse. Real check:28/44parse;27/44render both languages.
Activity overview exceeds existing claim limits; remains refused pending bounded overview
splitting. No guard/budget relaxation. Next: complete record-row and explicit shared-range families.

## Unit 2 — complete record rows, explicit ranges, clinical/continuation fields

RED `red2.log`:1expected failure/18pass for record-local rows and printed total;
RED `red3.log`:2expected failures/24pass for explicit ranges and clinical/fee fragments;
RED `red3b.log`:also catches reverse-order mixed grammar (root review finding).
GREEN parser/render/integration38pass3.20s. Ranges require existing target steps/actions
and retain the range record's citation. Conditional authorization keeps its printed scope;
local office/person columns stay with their record. Fee start/continuation require both
fragments and conflict-free target; clinical assistant remains separate from physician.
Real559:38/44parse,37/44render both languages. Activity overview still refuses on limits.
Setup copy independently verified by root:62dataset files byte-identical and .env parity,
`p11-workstream-split-20261028/copy-verification.json`. Claude owns central reconciliation.
No full suite: Claude occupies shared slot. Next: overview splitting, admission phase,
assessment continuation and removal same-index staff pairs.

## Unit 3 — bounded overview and remaining clear layouts

RED `red4.log`:long checklist fails under claim bounds; GREEN adds exact per-field
citations and bounded overview claims (no budget increase). RED `red4b.log`:shuffled
unnumbered rows reverse source order; GREEN requires a complete single reviewed
service_group sequence and sorts its explicit part_order. Synthetic fixture metadata
updated to provide that reviewed sequence; duplicate/incomplete orders refuse.
RED `red5.log`:3expected missing-family failures/29pass; GREEN43parser/render/integration
tests1.78s (`green5.log`). Admission application/result phases keep reset step numbers,
printed result heading and shared checklist location; a missing phase heading refuses.
Assessment local columns apply only to explicitly co-recorded actions; continuation begins
at its uniquely identified action and extends only through the named final step. Window1
stays local. Removal pairs personN/officeN by the same explicit index, preserving joint
role labels; incomplete pairs refuse. Original physical54–56,66–67,112–113rendered and
visually inspected; no new source reading or policy repair required.
Real559:41/44parse and render in both languages. Remaining3:initialTOR and complex
certifications (held initial mappings),feedback (prose). Next: final field-conservation,
refusal/citation review and coordinated suite; no model or hosted calls.


## Final verification / integration gate

Self-review found split staff-pair fields lost their record citations and could coexist
with a competing single/shared person:RED2expected failures32pass (`red6.log`),
GREEN45focused1.53s (`green6.log`). Pair citations now preserved;ambiguous variants refuse.
All generation-module regressions669pass21.84s,exit0 (`focused-final.log`/exit).
Real fidelity41/44parse/render both languages,2318substantive field checks all retained
in a claim citing its own source;46unresolved limits retained. See
[results](2026-10-28-p11-charter-layouts-results.md). Bounds unchanged. No new source
ambiguity. Full suite remains with Claude after integration;shared slot occupied.
Next:commit final evidence/citation hardening,merge current primary if conflict-free,
then deliver exact range to root/Claude for review and full suite.

## Review fix pass

Root's independent review found2important cases:interleaved/missing checklist scope
headings and repeated charges from unsupported multi-target shared fee ranges. RED6fail
34pass (`red-review.log`),GREEN51focused1.79s (`green-review.log`). Repeat original
headings with scope transitions,require explicit in/out-campus/result scope heading,
and refuse multi-target fees. Real fidelity remains41/44both languages,2318fieldchecks,
46limits. No new source decisions or budget changes.

Final generation rerun675pass18.47s,exit0 (`focused-review.log`/exit).
