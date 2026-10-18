# Phase07 offline model routing evaluation

Status:development evaluation in progress; Phase07 not complete. No institutional
execution, final benchmark, approved source release or student-answer quality claim.

## Fixed development scope

Five generic synthetic scenario families /15variants:document procedure,
prerequisite check, affected-course-plus-procedure, greeting and excluded graduate
procedure. Each has English/Filipino/Taglish wording. A1/B1 and program/curriculum
identities are fictional reviewed-alias fixtures; no PalSU rule is asserted or run.
These are not additions to the accepted75institutional development variants or
the sealed final benchmark. Gold fields never enter the model prompt.

Raw evidence:workspace/audit-evidence/p07-implementation-20261019/.
Original synthetic-dev-v1.json and synthetic-model-report-v1.json remain unchanged.
Original inference commit9286c76, promptv2; existing Gemma SHA256
3cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80.
Owner explicitly corrected model root to workspace/MODELS and authorized official
runtime download. Image sha256:4b7be0376002b4450a357a109bab804093ff9251193cc75ed4ce0cb39953ff5c;
llama.cpp b11718-547208dca; template SHA256
74a88f94c57c14e22dcdbe08e94127f42b87c6f584cb73838e73e32126f3f6b3.
CPU8threads/context8192/one slot/output768; temperature0/seed0/constrainedJSON.
Offline timeout240seconds per model call; at most one format repair. Other tests
ran concurrently, so elapsed times are not a controlled latency benchmark.

The first two development runs also exposed scenario-family words in model-visible
request IDs. Gold fields themselves were not passed, but those identifiers were
unnecessary hints. Preserve these runs as debugging evidence, not clean evaluation
accuracy. Current code removes session/request/fact IDs before prompt construction;
ownership and lineage remain host-side. Focused regression records this correction.

## Baseline observations, not a passing result

- Proposed route/control correct:8/15. Effective outcome correct:3/15.
- Entity collection9/15, claim collection9/15, response-style8/15. Empty gold
  collections contribute to these counts; these are not nine successful fact checks.
- Equivalent-family consistency2/5. Diagnostics:3model_ambiguity,
  7invalid_model_output,3model_control,2invalid_grounding.
- RAG chosen for all three procedure questions, but the model filled ambiguities
  with an explanation that document retrieval was needed; guards correctly withheld
  dispatch. All three greeting controls worked.
- Six structured variants failed the original output contract. One bounded captured
  replay showed correct operation/target/failed-claim text with wrong offsets.
  Excluded EN/Taglish selected unsupported_scope but had wrong quote offsets;
  Filipino excluded output failed schema. Do not silently mark these repaired.
- Baseline evaluator predates operation/target scoring and host quote anchoring.
  Its counts are historical observations; they do not test current code.

## Evidence-driven corrections and next check

Unique complete literal quotes can now be anchored by host code, with correction
counts; repeated/missing quotes are never guessed. One actual captured English
output replay (no new model call) proves correct typed course-b operation and failed
course-a claim after three offset corrections. See structured-quote-replay.json
and [code-review/correction evidence](2026-10-19-phase07-code-review.md).

Promptv3 explicitly distinguishes unresolved interpretation questions from route
explanations, and states that routing precedes retrieval. The backend still holds
any genuine model ambiguity; no keyword classifier or automatic RAG substitution.
The revised development input keeps the same15wordings and adds explicit expected
operation bindings. A bounded repeat will capture every raw model response and
score current route/control, entities, scoped operations/targets, claims, language
style and offset corrections. Its results are pending, not inferred from tests.

## Promptv3 repeat and final correction

The same15-wording repeat at79d56f1 produced13/15correct raw proposals,
14/15effective outcomes,15/15entity/claim/operation collections,14/15response
styles and4/5consistent families.17unique-quote offset corrections were recorded.
All nine RAG/Symbolic/Hybrid variants validated. English excluded audience was
correctly withheld by its audience guard despite a RAG proposal. Filipino graduate
request was misread as undergraduate/program prerequisites and failed the typed
course-target check. Its two raw attempts are preserved in model-v3-raw/.
This is a known guarded failure, not successful multilingual scope handling.

Promptv4 makes explicit graduate/pang-masterado scope override the undergraduate
default and distinguishes program admission from course operations. It also removes
all ownership/scenario identifiers from model-visible context. A final same-wording
run with raw capture will measure the corrected setup. The earlier hinted runs
are retained with their actual versions and are not rewritten as valid final proof.
