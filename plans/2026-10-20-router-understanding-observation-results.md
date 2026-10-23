# Frozen router-to-answer actual-model observation

Phase09,20October2026;execution HEAD1f0ead3,product8fafaf7. The
[frozen protocol](2026-10-20-router-understanding-quality-gate.md) ran ONCE with
actual local Gemma and actual Janus on eight fixed fictional developer cases.
**Gate FAIL:3/8 responses satisfy the frozen response requirements;no promotion.**
This author assessment uses known development cases,not independent human
validation,an institutional accuracy rate or an unseen final evaluation.

## Actual responses and timing

| Case | Final result | Outer seconds | Model calls | Assessment against frozen reference |
| --- | --- | ---: | ---: | --- |
| d-en | answered/en | 79.120694 | 4 | Office K and7tokens supported;complete response |
| d-fil | answered/fil | 71.325650 | 4 | Both facts supported;complete response |
| d-tl | answered/taglish | 59.633463 | 4 | Both facts supported;complete response |
| s-en | clarification/en | 27.689650 | 2 | Failed ZX101 marked reported;host does not execute Prolog |
| s-fil | clarification/fil | 41.284290 | 2 | Failed fact omitted;actual ZX201 check returns unknown |
| s-tl | answered/fil | 37.262567 | 2 | WRONG target ZX101 returns eligible;expected ZX201 and Taglish |
| h-en | clarification/en | 43.090027 | 2 | Failed fact omitted;ZX201 unknown;document answer withheld |
| h-tl | temporarily unavailable/unknown | 39.747983 | 1 | Router hits768-token limit;truncated output rejected |

Four answered statuses include only three responses meeting the requirements.
The validated wrong-course result demonstrates that canonical Prolog consistency
and a bound ledger do not establish that the operation answers the question.
Actual Prolog correctly computed three supplied requests;two lacked the failed
fact,and one targeted the wrong course. None of five structured scenarios produced
the required scoped ZX201 ineligibility result.

Each successful RAG answer contains both required claims with the frozen source
reference. Nevertheless,all three routers collapse two documentary requests into
one part:complete responses3/3 do not establish separate-part extraction. Separate
semantic parts appear in4/8cases:three Symbolic cases and h-en. Its leading "and"
is harmless;that boundary difference is not a semantic failure. Host-aligned quotes
match the original question in all7usable plans;raw offsets require existing
alignment and are not an accuracy result. Final requested language is met in6/8;
Taglish eligibility becomes Filipino,and truncated Hybrid has unknown style.

## Measurement boundary and observed work

The outer timer wraps AnswerPipeline.run,including routing,required generation/
support calls,actual symbolic work,host validation and observation writes. A fixed
document adapter supplies the exact frozen passage. EXCLUDED:query embedding,
vector search,Supabase,API/browser processing,external network,queue/load measurement,
fixture preparation and service startup. Local model HTTP and its props/template/
tokenization calls ARE included. This is candidate-component timing,not a complete
real-service pipeline or student-visible latency measurement.

Complete responses take59.6-79.1s;routing29.649-45.852s and generation/support
29.984-33.264s. Failed or incorrect responses take27.7-43.1s and cannot count as
successful-answer timings. Three actual Janus adapter executions take0.309-0.397s,
including child/runtime overhead,not isolated Prolog inference. This small sequential
developer batch establishes no population p50/p95 or student waiting acceptance.

Initial standalone props readiness0.116906s;fresh pre-batch readiness0.124200s.
Neither isolates connection establishment or measures Supabase readiness. The
already loaded service was reused;no cold-start measurement. Browser,Supabase,queue
and concurrent-server contention measurements remain unavailable. These results
do not meet or validate the saved
[15-20s warm browser proposal](../Context/response-time-recommendation.md),including
the conditional20-30s complex-Hybrid range. Accuracy remains the first constraint.

Exactly21model calls:8interpretations,7styles,3document drafts,3support/part reviews;
84local HTTP exchanges. No routing/answer repair used;no case rerun. Server usage:
37672prompt/6713completion tokens. Seven router responses contain a reasoning
field despite requested reasoning_effort=none;the final one has finish_reason=length.
Actual reasoning was not reliably disabled. This observed configuration/behavior
mismatch does not prove its total latency effect. No separate reasoning-token count
is exposed. These are local Gemma counts,not the owner's Codex quota;the earlier
[Codex usage observation](2026-10-20-session-token-usage-observation.md) is separate.

## Reproducibility and limits

Ignored raw:workspace/audit-evidence/p09-router-gate-20261020/:exact inputs,generated
synthetic authoring/bundle/release,preflight/pre-inference bindings,single-attempt
lock,21full call traces,8results,author assessment and logs. Cases SHA256
c1071bbab22cd200a400b500e8622c077a43c18e4ab7c814abfd8d3258daad34;
input binding39c7d7916778414a66fe2cdb9d1e63419cae35e1567d74075d303ad6ef63aad4;
observer793f98d0a2c6c657665a5896da0751b1c759c0f97f5351c5df7dc1e49d98e569;
pre-inference2865ee99006da25c7bfa40cb0f558ebf696f414cef616998521bc072660dd2b5.
Existing endpoint18088 matches frozen model/template/context8192. Output768,temp0,
seed0,cachefalse and120/120/120/180s budgets unchanged. No installs,downloads,
weight rehash/copies,DB writes,configuration changes or institutional rules.

Preparation first accessed nonexistent runtime.bundle;the retained failed log
precedes all inference. Corrected to the existing bundle compiler,then verified
all8input contracts/code hashes before inference. Post-run verification confirms
8results/21calls,frozen input/product hashes and all74prior sealed files unchanged.
New raw manifest is recorded in the checkpoint. Earlier1668tests/66subtests remain
historical software evidence;not rerun or represented as semantic quality here.

The reference fixes failed ZX101 as the supplied scenario condition. Future repair
must preserve asserted/reported/hypothetical distinctions and scope conditional
reasoning appropriately;never coerce conditional/third-party statements into
established student facts. No relaxed guards,unchecked streaming,post-failure
prompt/model/seed/budget correction or rescue probe followed. Accepted75institutional
variants unchanged;no Phase09 completion or Phase10. Next:one bounded correction
design from sealed traces for target/fact meaning,separate parts and runtime
reasoning mismatch;specify quality criteria before further model execution.
