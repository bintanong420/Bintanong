# English/Taglish response migration plan

**Goal:** implement the owner's accepted two-reply-style policy while retaining
English/Filipino/Taglish input comprehension and grounded evidence.
**Spec:** [accepted decision](2026-10-27-english-taglish-response-decision.md),master26,
Phase11plan. User explicitly authorized the change and continuation;no new approval.
**Architecture:** keep semantic routing/Prolog/RAG and existing call/repair limits.
Version the response-style wire;Taglish needs literal Filipino evidence,with
English fragments optional. Generate/render all new replies from English/Taglish
targets;legacy `fil` remains parseable as historical input and maps to Taglish at
the generation boundary. Historical raw evidence/results/source files unchanged.
**Execution:** inline TDD in existing isolatedp11;independent review;small commits.

## Requirements review and decisions

Existing approved baseline covers undergraduate advisory questions,private sessions,
natural multipart/follow-up requests and cited evidence. Only output targets change;
accepted input wordings/source approvals remain. Retain the previous control/route,
entity/claim guards and source limits. Preserve unknown-versus-unmet semantics.
Thesis17–18and runtime PNG consulted on resume;input languages remain consistent
with thesis,while master26records the revised reply-scope decision.

No new dependencies,downloads,source/hosted/pin changes,frontend integration or
activation. Fewer output targets reduce maintenance;latency gains require actual
measurement. Do not remove review/evidence checks to improve speed.

## Tasks

1. [x] Regression-first style wire and routing tests:Tagalog-only -> Taglish with
   no fabricated English fragment;English -> English;Taglish -> Taglish;unknown
   remains unknown;invalid/ungrounded fragments reject;separate and combined
   routers/clarifications use the same targets. Observe RED then implement style
   v2/schema/prompt and migrate synthetic inference fixtures/current assertions.
2. [x] Generation boundary RED:legacy `fil` input IntegrationResult produces
   Taglish host and documentary targets;English/unknown unchanged. Normalize before
   evidence/review identity construction. Generation schemas/prompts/checker
   instructions expose only current reply targets;old record contracts/helpers
   remain readable for historical evidence. Preserve validation/review identity.
   Update current test expectations for changed owner targets,not assertions of
   source fidelity/canonical decisions. Version evaluation policy and report raw
   versus current expected style without rewriting accepted input cases.
3. [ ] Bounded actual-model style/routing+host/document output observations in
   English/Filipino/Taglish with same saved questions;verify claims/route/style
   separately. Preserve source English terms. Record call counts/stage times and
   exclusions;do not claim browser latency or a speedup from tiny samples.
4. [ ] Independent review,relevant routing/generation/API/context tests and full
   project suite at final code. Docs/phase/diff checks;record final limitations,
   versions,commands,results and next action. No phase advancement.

## Files and verification

Routing:style.py,evaluation.py;generator.py and generation prompt/schema helpers;
shared response-policy function with no keyword inference. Tests include a focused
test_reply_language_policy.py plus existing style/routing/generation/API regressions.
SharedPython3.13 `-X utf8 -B -m pytest -q -p no:cacheprovider`,external basetemp
under workspace/audit-evidence/p11-reply-policy-20261027. Full command adds`-rs tests`.
No new lint tool installs;disclose unavailable static/lint tools as before.
Review focus:literal evidence provenance,non-English input/unknown handling,
repair/clarification styles,claim/ledger hash consistency and legacy record replay.
Document-only/course quote grammar fix remains a separate next increment.

## Implementation evidence

Style wirev2,combinedv4,router promptv22. Literal Filipino evidence permits Taglish
with empty English fragments;Filipino-only reply enum removed. Generation preparation
normalizes legacy fil before review/ledger identity;old record parsers/host dictionaries
remain for historical compatibility,not a newly selectable live reply target.
Current test expectations change approved reply strings only;original Filipino/Taglish
questions and source/citation/decision/hold assertions retained.
Initial policy RED13/1pass included five invalid control fixtures;repaired their
required understanding field,then generation-only RED7confirmed legacy outputs.
Schema RED1,prepare-boundary RED1 and input-family reporting RED1observed separately.
New14policy tests first GREEN;expanded18tests include metadata/combined cases.
First broad regression45failures chiefly old output expectations;after migration
and fixture correction1235passed32.93s. Independent review caught stale routing
prompt language instruction;fixed with separate input/reply explanation.
Final independent104tests pass7.27s;no blocking findings. Follow-up broad1236passed/
1old prompt-version assertion failed;updated v21->v22without changing behavior assertions.
Bounded actual-model observations underway;no latency gain claim.
