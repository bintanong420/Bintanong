# Phase07 explicit inference baseline implementation plan

> Execute inline with executing-plans and test-driven-development. Existing p07
> isolation verified; owner accepts the standing prompt/validation decision.

Goal:remove implicit prefix-cache reuse from new evaluation requests and make
reported sampling defaults observable before changing semantic prompts.
Architecture:existing LlamaTransport/Router; fixed no-prefix-cache evaluation
profile, safe allowlisted server defaults in metadata, unchanged semantic schemas.
Tech:existing Python3.13/HTTPX/pytest and pinned llama.cpp image/model; no installs.
Spec:[standing decision](2026-10-19-prompt-engineering-and-validation-decision.md).

## Constraints and preflight

Student capability:reliable comparisons of multilingual routing/style behavior.
Evidence:current query -> same prompt/schema/model -> explicit request conditions
and observable reported server defaults -> existing validators/evaluator.
Exit advanced:interpretable actual-model evaluation, not a new semantic capability.
Question:are request cache policy and reported sampler settings now explicit and
verifiable without capturing arbitrary source/user text? Cache off does not prove
absolute determinism or fix the three known semantic errors.

No temperature/seed/reasoning/schema/call-limit changes, optional configuration
framework, new executor, keyword classifier or accuracy claim. Do not reuse old
cached-profile model captures as current-profile inference. Keep approved75
wordings/final-family separation/source and institutional release holds.

Preflight sources:Context7 /ggml-org/llama.cpp resolve/query confirms cache_prompt
request boolean and /props default_generation_settings.params shape; compare
pinned build547208dca. Active /props initially503while retained task model loads;
this is not a completed runtime probe. Existing template/token limits stay intact.

## Task1 - fixed request profile and safe metadata

Files:backend/bintanong_routing/transport.py, README.md;
tests/test_routing_transport.py. No constructor/Router/evaluator signature changes.
Both constrained and explicit JSON-only requests send cache_prompt=false.
Metadata adds inference_profile=p07-greedy-no-prefix-cache-v1, cache_prompt=false,
reasoning_effort=none and server_sampling_defaults. The latter is a subset of
actually reported sampler numeric controls/order; absent fields are not invented.
Keep existing temperature/seed/output/template metadata. Do not copy whole /props,
prompt, grammar, stop strings, generation history, paths or private text.
Malformed present params must yield fixed invalid_server_response before generation;
an absent params object remains compatible and produces an empty defaults subset.

- [x] RED:focused transport tests show missing explicit cache/profile metadata and
      malformed params acceptance, for both decoding modes and absent defaults.
- [x] Implement minimal fixed request setting, safe defaults selection and guard.
- [x] GREEN:transport tests, then routing/style/evaluator and inference regressions.
- [x] Document profile compatibility; semantic prompts/schemas remain byte-identical.
- [x] Commit cohesive product/tests/docs; record exact RED/GREEN commands/results.

## Task2 - bounded runtime verification and recovery

- [x] Inspect retained task server's reported defaults/build/template and startup
      settings; keep raw evidence ignored under workspace/audit-evidence.
- [x] Verify one synthetic constrained completion uses the profile and returns
      structured output; this is a transport smoke test, not multilingual accuracy.
- [x] Run applicable regression gate and independent review of this correction;
      fix important findings with focused RED/GREEN evidence.
- [x] Stop task-owned runtime after bounded verification; preserve other workers.
- [x] Update checkpoint/progress with current results and exact next action:
      fresh paired baseline on the existing synthetic cases, then one prompt change.

Ruling:no broad reasoning/sampling sweep in this increment. Report defaults as
reported values, separate from explicit request overrides and verified hardware
configuration. Keep the old reasoning-budget probe retired unchanged.

## Execution evidence

Baseline bbaf5f9; product increment29cc8d9. Raw root:
workspace/audit-evidence/p07-explicit-profile-20261019/. Same readiness Python as
standing decision, -B -m pytest -q -p no:cacheprovider, TEMP/TMP=raw-root.
RED:--basetemp=raw-root/red tests/test_routing_transport.py:
7failed/10passed0.92s,exit1; red.log. Failures are missing cache/metadata keys and
expected malformed-params refusal, not imports/environment failure.
GREEN:--basetemp=raw-root/green tests/test_routing_transport.py
tests/test_routing_router.py tests/test_routing_style.py tests/test_routing_evaluation.py
tests/test_bintu_inference.py:106passed3.43s,exit0;green.log.
Actual pinned /props reports T1/top_k64/top_p~0.95/min_p~0.05,repeat_penalty1,
one slot,b11718-547208dca. Request overrides remain T0/seed0/reasoning-none.
Broad24-file gate:1577passed/11subtests128.27s,exit0; verify-profile.ps1,
regressions.log. Independent inference_profile_review:no P1/P2,106passed2.29s,
diff check clean. No findings required another correction. This review covers this
increment; earlier whole-project/Docling limitations are not waived.
One actual constrained synthetic smoke:one model call,24input tokens, valid
{"ok":true},cache_prompt=false; smoke-profile.py,smoke.json,smoke.log. Not routing,
multilingual or answer accuracy. Task runtime stopped14:32;inspect=exited.
Evidence verifier verify-evidence.py passed8artifacts, unchanged semantic modules,
current transport bytes, request/template/build/settings and context budget;
verification.log,manifest.json. Rerun on15:08resume passed; no duplicate inference.
Context scope physical17-18 saved extraction and actual runtime PNG reread on
resume; no architecture/scope discrepancy. No weights/installs/locks changed.
Resolved profile question:stop this diagnostic. Next:one fresh15-case synthetic
baseline, then a single justified prompt intervention and matched evaluation.
Final docs/phase gate573passed/11subtests15.55s,exit0; final-docs.log under raw root.
Command:same readiness Python -B -m pytest -q -p no:cacheprovider
--basetemp=raw-root/final-docs tests/test_docs_hygiene.py
.agents/skills/bintanong-phase-handoff/tests/test_phase_state.py; TEMP/TMP=raw-root.
