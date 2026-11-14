# Quoted-reference interpreter software results

Phase09;owner-approved design implemented20October2026. Task1 commit71be2fd,
Task2 commit9a72d2e;[implementation plan](2026-10-20-router-quoted-reference-implementation-plan.md)
and [design](2026-10-20-router-correction-diagnosis-and-design.md).
**Software verified;new actual-model accuracy and latency NOT MEASURED.**

## Changed behavior

The LLM emits bintanong-interpretation-wire-v1 with literal text and zero-based
occurrence references. Python computes original character spans and resolves
operation targets/claim entities to their quoted course mentions. Numeric course
references and model-calculated offsets are absent from the model schema.
Reordered mentions retain the same quoted identity;repeated and overlapping text
uses the declared occurrence. Invented/out-of-range/duplicate/non-course references,
uncontained claims/targets and invalid types reject before dispatch. The existing
shared formatting repair applies;there is no legacy model-packet fallback.

Normalization produces existing Interpretation v2. Existing aliases,curriculum
scope,mode/conflict/capability validation,question/release bindings,Prolog evidence
and generation validation remain. Prolog prerequisites and institutional records
were NOT changed. The observed earlier error was before Prolog:wrong target or
missing fact. This change cannot prove every future model interpretation correct.

Selected separate routing keeps independent response style and at most3calls with
one shared format repair. Explicit/unselected combined packet migrates to v2 and
uses the same normalizer,at most2calls. Promptv11 contains one short fictional role
contrast and asks for separate requested details;the known failure families remain
known,not unseen evaluation. No added classifier or second interpretation stage.
Internal offset_corrections remains0 because the host constructs spans.

No model/reasoning-budget/seed/cache/context/deadline changes. Unexpected reasoning
in prior server output is not declared fixed. Required RAG/Prolog/validation stay;
no accuracy-for-speed trade or unchecked streaming. Conditional/reported modes
remain nonasserted;conditional execution stays outside this approved change and
awaits its separate owner decision/design. No invented actual grades or policy.

## Verification and review

All commands used Python3.13 readiness venv,-B -m pytest -q -p no:cacheprovider,
with workspace TEMP/TMP and separate external basetemp paths. Full commands/logs
are ignored under workspace/audit-evidence/p09-router-wire-20261020/.

| Check | Actual result |
| --- | --- |
| Task1 missing-normalizer RED | 15failed0.72s |
| Task1 focused plus normalized contracts/validation | 58passed0.59s |
| Task2 literal model-boundary RED | 7failed0.93s |
| Task2 normalizer and boundary GREEN | 22passed1.12s |
| First runtime-fixture migration | 29failed/123passed4.28s |
| Corrected routing/schema/combined migration | 152passed3.67s |
| Relevant31file software gate | 688passed13.96s |

These22new focused cases check concrete quote identity,grounding and repair/mode
boundaries. Existing normalized-contract fixtures remain v2. Shared fake model
fixtures independently produce the new wire shape without production normalization;
literal wire tests separately prove acceptance and legacy/foreign-reference rejection.
Old offset-oriented assertions were migrated to host-span/occurrence behavior.
No new institutional benchmark cases,parameter sweep or unrelated extraction tests.

One fresh whole-change review ofda4673d..9a72d2e found no consequential Critical,
Important or Minor issues. Read-only;no repeated tests/model calls or checkout edits.
Its assessment checks code/dispatch safety,not independent verification of688tests
or semantic accuracy. No fix pass or re-review was needed;no deferred minors.

Review set-aside rulings:actual intent/fact completeness and separate-detail semantics
need a later actual gate;latency/reasoning suppression remain unmeasured;conditional
execution needs its separate design;institutional readiness/phase completion retain
existing holds. These remain consequential limitations,not silently waived findings.
Repository plans/checkpoints and ignored workspace audit evidence replace the
skill's default scratch-ledger/review-package locations under the owner's rules.

## Evidence and next action

software-freeze.json binds the final12changed routing/test files,selected prompt
and decoder-schema hashes,combined identity and committed product snapshot. It is
a SOFTWARE freeze,not complete executable experimental-input/readiness binding.
New evidence manifest and final docs checks are recorded in the checkpoint.
Prior74software/55observation/10research sealed files remain unchanged.
No new model calls;prior3/8 complete responses and59.6-79.1s component timings are
historical observations of the previous candidate. They do not score this code.

Next:resolve the pending conditional-answer boundary,then define/freeze one actual
candidate-quality protocol and exact runtime inputs/settings before any inference.
Keep quality,language,coverage and timing separate;do not rerun the old sealed batch
or treat software success as promotion. The
[15-20s warm browser target](../Context/response-time-recommendation.md),including
conditional20-30s complex Hybrid,remains proposed and unvalidated. Startup/readiness,
Supabase,embedding,network/API/browser and queue exclusions remain explicit.
Phase09 active;no Phase10,training,dependency/source/DB changes,push,merge,deployment
or institutional activation. No new execution/release authorization inferred.
