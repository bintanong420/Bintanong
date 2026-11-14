# Printed service steps:host-rendered long procedures

**Owner29Oct:** "Let's do A, what you recommend, lets give them the printed steps directly" — answer
long Charter procedures by showing the reviewed printed steps directly,with a short framed lead,
instead of model-written prose ([why](2026-10-28-segmented-procedure-drafting-results.md)).

Student capability:complete,exact service steps (what to do,office actions,office,person,time,fee),
checklist and printed total,fast. Evidence path:existing reviewed Charter chunk fields retrieved
for the selected subject -> deterministic host rendering (like the fee host reply) -> existing
final validation. Applies [service-table association policy](service-table-association-policy.md):
each agency action keeps its own/shared time,person,office;shared fees stay with their parent step.

## Design

1. **Strict step table at answer time** (`service_steps.py`):from one service's retrieved records in
   source order,consume every field by an explicit grammar — metadata,requirement/where-to-secure
   pairs,`stepN_client_step`,`stepN_[shared_]fee|time|person|office`,`stepN_subactionK_action|time|
   person|office|fee`,`stepN_action` and printed totals. Any unknown field,missing client step/action,
   step gap or blank-vs-value conflict -> no table (today's behaviour). Survey:23/44Charter services
   parse completely;21 row/unnumbered/continuation layouts stay unsupported until reviewed rules.
2. **Host reply** for document parts on a supported service:checklist,ordered steps,printed total,
   values verbatim from the source fields;English or Taglish frame per the27Oct reply decision.
   One reply serves all parts on that subject;claims group records (<=8evidence ids each) within
   the8-claim cap. No model wording for the steps;existing final validation still applies.
3. **Owner sample:** real renderings beside printed fields for3services (good moral,library card,
   one shared-time service) before enabling in the answer path. No source/default/activation change.

## Tasks (TDD,synthetic fixtures)

1. RED/GREEN parser:numbered/shared/subaction fields,totals,checklist;refusals for unknown field,
   step gap,missing action. Real-data check:23services parse,21refuse (ignored evidence).
2. RED/GREEN renderer en/taglish;claim grouping<=8ids;verbatim values.
3. Owner sample review (inline);then RED/GREEN host integration beside fee/grade host replies;
   focused + full suite;live re-check good-moral/library-card/entrance-health + regressions.
