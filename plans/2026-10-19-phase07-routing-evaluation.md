# Phase07 offline model routing evaluation

Status:current candidate evaluation recorded; Phase07 remains active because
language/scope exit requirements are not satisfied. No institutional
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
run with raw capture measures the corrected setup below. The earlier hinted runs
are retained with their actual versions and are not rewritten as valid final proof.

## Clean promptv4 development result

Inference commit32747dbea36f05e6d3bceb1d58d0b9317ee8c637; same15wordings,
opaque host IDs and no session/request/fact IDs in model input. Raw:
synthetic-dev-v3.json, synthetic-model-report-v3.json, synthetic-model-run-v3.log
and model-v4-raw/ (16responses, including one format repair).

| Language | Variants | Proposed route/control correct | Effective outcome correct | Exact style label |
| --- | ---: | ---: | ---: | ---: |
| English | 5 | 5 | 5 | 5 |
| Filipino | 5 | 4 | 4 | 3 |
| Taglish | 5 | 5 | 5 | 2 |
| Total | 15 | 14 | 14 | 10 |

Canonical entity, claim and operation collections match15/15, but nine variants
have empty gold collections:the substantive scoped operations/claims are6/6.
All nine positive RAG/Symbolic/Hybrid cases validate. Greetings work3/3;
excluded requests produce the expected notice control2/3. Filipino excluded
request instead yields invalid_model_output/evidence_unavailable after retry;
no symbolic request is dispatched. Four/five equivalent families have consistent
route/meaning signatures. Eight cases use17unique exact-quote offset corrections.
These are whole-pipeline results, not unaided model offset accuracy.

Remaining exact-style mismatches:procedure-taglish ->fil, prerequisite-fil
->taglish, greeting-taglish ->fil, excluded-fil ->unknown, excluded-taglish ->fil.
Reinspection on continuation corrects the earlier diagnosis:both malformed Filipino
responses selected audience=excluded/control=unsupported_scope, but also attached
check_prerequisite_eligibility to a program mention. The invalid course reference
caused rejection; the scope label itself was correct. Original attempts14/15 are
in model-v4-raw/. Original scores/bytes remain unchanged. Keep this as a real
failed requirement. Style labels are metadata; no final answers
were generated and no response-language quality result is claimed.

This is a small tuned development trial, not a held-out/general accuracy estimate,
the accepted75institutional variants or the final thesis benchmark. No source
retrieval, grades-to-outcome conversion, Prolog execution or final answer occurred.
Do not call Phase07 complete or begin Phase08 from these results.

Reproducibility identities:
- Canonical case set:f0f85d8308d341970b6e6d051dcb735d10e1042b8e3cea84df538f4689aa236e.
- Prompt:f803f16bc2c5643dbb880c1ca43e5620023ac1c8bfd617aa13239aa302524e70.
- Output schema:c470a75026be71f1ffe1740322e51074335756f49a0ab7a4fbaef54f311067d4.
- Catalog:2207f062dce8dc42483dfd0993e7e1f5d08330294673c37f293e1a2a8180ce0a.
- Input file:f60c39ea8081adfce4f244e49d59d03c113e1e10d5ca0e9f50a7a9a0b522b55e.
- Report file:2c9b9a3fdd4779b1837666a2e84114ac8279dbe9c5d08e1a88d4b340853023b4.

## Bounded compact-pass probe and preflight correction

Question:can a small Bintu language/scope-only pass fix the remaining labels
without course-extraction schema pressure? Six selected synthetic queries were
checked, without scenario IDs. Language5/6; controls3/6, with three supported
undergraduate questions wrongly rejected. scope-only-diagnostic.json/log and
probe-scope-only.py preserve the exact prompt/results. This alternative is not
integrated. Its question is resolved negatively; do not repeat it unchanged or
start another blanket prompt sweep. Next design must retain undergraduate website
context while correctly honoring explicit excluded audience and language preference.

Actual template comparison also found /apply-template defaults differ from
reasoning_effort=none used for generation. Preflight now passes the same option;
regression RED1 ->79routing tests passed,1.02s (template-match-*.log).
Generation messages/settings are unchanged. Stateless re-tokenization of all16
recorded inference/repair messages confirms at least4185tokens of remaining context
after the768output budget/eight-token margin. No new model calls were made;
exact-template-headroom-audit.json and template-options-comparison.json retain proof.
The old report's input_tokens came from the old preflight, not the corrected count.

## Public synthetic wording roster

These contain no university rule or private student record. Canonical scope is
program-a/curriculum-a. Reviewed fixture aliases A1 ->course-a and B1 ->course-b;
see tests/test_routing_validation.py:catalog for the declared fixture records.

| Family / expected path | English | Filipino | Taglish |
| --- | --- | --- | --- |
| Procedure / RAG | How do I request a copy of my grades? | Paano ako hihingi ng kopya ng aking mga marka? | Paano ako mag-request ng copy of grades ko? |
| Prerequisite / Symbolic | I failed A1. Check if I can take B1. | Bumagsak ako sa A1. Maaari ko bang kunin ang B1? | Failed ako sa A1. Pwede ko bang i-take ang B1? |
| Affected courses + procedure / Hybrid | I failed A1. Which courses are affected, and what is the documented retaking procedure? | Bumagsak ako sa A1. Aling mga asignatura ang maaapektuhan at ano ang dokumentadong proseso ng pag-ulit? | Failed ako sa A1. Anong subjects ang affected at ano ang documented retaking process? |
| Greeting / greeting | Hello! | Kumusta? | Hi, kumusta? |
| Graduate procedure / unsupported_scope | What are the graduate program enrollment requirements? | Ano ang mga kailangan para makapagpatala sa programang pang-masterado? | Ano ang enrollment requirements para sa master's program? |

Prerequisite operation:check_prerequisite_eligibility:curriculum-a:course-b.
Hybrid operation:list_affected_courses:curriculum-a:course-a. Both preserve the
asserted course-a:failed claim; no prerequisite relationship or eligibility outcome
is asserted. Other families have no scoped course operations/claims.
