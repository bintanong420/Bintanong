# Source-bound single-field answer correction

**Goal:** answer a reviewed step-specific question without demanding the whole
procedure or permitting invented agency actions,fees or processing times.
**Baseline:** approved master23follow-ups/master26English-Taglish replies,
Phase11plan and [saved TOR failures](2026-10-27-tor-follow-up-answer-validation-results.md).
Owner's continue instruction authorizes this correction to that existing capability;
no new product scope,source approval or activation is introduced.

## Design

Keep the semantic LLM router and complete source-aware retrieval. Author a narrow
claim over the existing reviewed first-client-step field. Add an explicit optional
source-review answer mode `quoted_field`,limited to one nonblank textual field with
matching source spans. Full subject review and transitive context are still required.
Legacy reviews omit this mode and retain their byte-identical normalized output.

The retrieval adapter carries a typed field quotation only after the assessment
establishes availability. Coverage still requires every context companion;only
generation's answer citation floor narrows to that field's record. DocumentResult independently checks the
quotation against the corresponding emitted JSON source field. No invented value,
unknown field,missing context or unresolved affected claim becomes an answer.

Generation retains the model draft and ordinary support/relevance reviewer.
For this declared mode only,per-part grammar and host checks allow exactly one
source quotation with a fixed English/Taglish introduction and its bound citation,
or an explicit unavailable slot. Any extra policy,number,fee,time or reference is
rejected. This is literal quotation,not a translated/rewritten policy conclusion.
Other explanation profiles withhold this new mode rather than bypass its checks.
Whole-procedure record/order/context guards remain unchanged for legacy claims.

Rejected alternatives:remove record coverage globally(unsafe);infer a step number
with keywords(bypasses semantic routing);trim companion context(hides conditions);
replace model review with a host-only answer(changes the validation path).

## Tasks and verification

1. [x] Synthetic RED for authoring mode validation/legacy identity,adapter and
   independently bound quotation,all-context preservation,exact English/Taglish
   draft grammar/guard,unavailable slot,unsupported profile,and whole-procedure
   controls. Use source-free fixtures and observe expected failures before code.
2. [x] Minimal GREEN in candidate_claims,orchestration contracts/adapters,
   generation evidence/part answers and one small quotation helper. Preserve
   legacy serialization and inference stage counts;no general refactor.
3. [ ] Prepare an ignored derivative register/topic menu with one TOR step1claim
   using the existing row2_client_step/event/spans. Preserve original register,
   chunks/vectors/versions/holds and all other claims. Local3904diagnostic only.
   Replay the saved English/Filipino/Taglish questions;score exact field quotation,
   correct claim/citation,review outcomes and source limits separately.
4. [ ] Independent review,focused regressions and full suite at frozen code;
   docs/phase/diff checks,raw receipt assertions/seal and compact delivery commits.
   Record failed probes rather than starting a prompt/threshold sweep.

Code families:backend/bintanong_retrieval/candidate_claims.py;
backend/bintanong_orchestration/{contracts,adapters}.py;
backend/bintanong_generation/{evidence,part_answers,generator}.py plus quoted_field.py.
Tests:tests/test_quoted_field_answers.py and existing candidate/retrieval/adapter/
generation/routing/orchestration/API suites. Existing Python3.13 `-X utf8 -B -m
pytest -q -p no:cacheprovider`,external basetemp;full adds`-rs tests`.
Ignored evidence:workspace/audit-evidence/p11-quoted-field-answer-20261027.

## Live source/storage state checked on resume

Read-only Supabase MCP confirms corrected78active/active pointer;combined465draft,
old80draft and19superseded. Latest normalized local corrections are not yet in
that hosted465draft. Storage upload,source validation,answer acceptance and
activation are separate. No database write,dependency/model download,frontend,
source wording change,school approval or phase advance. Context17–18/routingPNG
rechecked;missing facts stay unknown. Preserve active package/pin and source holds.
