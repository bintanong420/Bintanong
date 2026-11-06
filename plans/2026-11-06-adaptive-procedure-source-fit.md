# Adaptive procedure source fit

Owner report: “How to secure good moral certificate?” answered from the Handbook,
although the Citizens' Charter contains the procedure. Owner correction: preserve
rules and make selection adaptive; do not replace every good-moral source choice.

## Diagnosis and boundary

- Saved failing router trace `api-call-1793955794505600000.json` selects Handbook FAQ.
  A fresh unchanged run selected Charter instead: the defect is inconsistent source fit.
  The old requirements helper corrects checklist requests; it does not force FAQ selection.
- Existing Charter topic has checklist, seven step claims, totals and an aggregate claim.
  Source: Citizens' Charter2025 fourth edition, physical52–53,
  `ver-42a93994e1467df0f32c7038d1c21f638c23ac0f1dee984463acf56caf526529`.
  Ten linked reviewed records, no recorded source limits. Source records remain unchanged.
- Both good-moral topics lack a shared family; Handbook FAQ also covers unrelated services.
  Assigning its whole topic a good-moral family would misclassify those other services.

## Change

Expose existing `stepN_client_step` bindings as workflow fact counts in topic selection
and fact indices in interpretation. These are metadata projections, not newly authored
steps or authority. Semantic guidance compares requested information with actual reviewed
coverage: procedure, checklist, policy and an explicitly requested source remain distinct.
No new rule says “always use Charter”. The old forced good-moral requirements switch is
removed: it could override an explicitly Handbook-bound requirements question.

Within an already selected topic, a semantic `document_procedure` intent and whole part retain original requested
claims and adds reviewed client-step claims when the union fits the existing eight-claim
bound. Specific policy/step questions, requirements and not-stated claims keep their scope.
Overflow raises a validation error into the existing bounded router repair rather than
silently omitting steps. Policy-only or mixed intents do not trigger this expansion.

Review-bound non-numbered `*_procedure` values also reach the menu as partial procedural
context. This exposes the vehicle memo's initial-payment fragment without inventing a
complete application workflow, full requirements or replacement price. Original reviewed
claims, source limitations, field assignments and the selected-fragment boundary remain.

## Verification

- Menu regression RED: missing workflow metadata. Whole-procedure regression RED:
  checklist-only selection omitted step facts. Synthetic fixtures contain no source text.
- Python3.13 existing venv, pytest cache off, ignored external basetemp under
  `audit-evidence/benchmark-fixes-20261106/source-fit-*`.
- Focused routing/menu gate258 passed; integration/ordering/generation gate184 passed.
  These overlap, not a summed full-suite result. New tests: `test_routing_source_fit.py`.
- Prompt-only live trial still picked FAQ or only a first step. Menu projection then
  selected Charter but only checklist; the selected-topic coverage guard corrected that.
- Final four live router cases: exact English and Filipino how-to select Charter checklist
  plus all seven steps; requirements-only selects checklist only; explicit Handbook
  request remains Handbook. Correct English/Taglish styles observed.
- Ignored evidence: `good-moral-router-before.json`, `good-moral-router-after.json`,
  `good-moral-router-workflow-menu.json`, `good-moral-router-final.json`.
- Final dev API reload and exact3217 HTTP answer check remain to verify generation.
  No full72 run, original-source change, dependency change or institutional activation.
- Review found whole-policy broadening, capacity omission and explicit-source requirements
  override. Corrected each with focused regressions. Reviewed five-case live router check:
  both how-to languages retain all seven steps; requirements stays narrow; explicit Handbook
  whole and requirements questions stay Handbook (`good-moral-router-reviewed.json`).
- Latest combined routing/menu/generation gate362 passed6.56s; independent resume gate64
  passed2.08s. Gate-pass live probes encountered model_connection_error; not verified yet.
