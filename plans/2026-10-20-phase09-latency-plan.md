# Bounded Phase09 latency improvement

20October2026;baselinec490fe8,p09/feat/p09-generation-validation. Owner resumes
after the overnight pause and confirms the CUDA setup was overlooked. Capability:
the same natural query should reach validated output faster,with its route,
evidence,canonical decision,language preference and release limits preserved.

## Evidence and design

Reuse the three actual-service baselines:277.492s RAG,304.913s Symbolic,
355.696s Hybrid. No repeat setup/source review/benchmark wording acceptance.
The existing CPU container uses8threads/one slot/no GPU;RTX3050Laptop4096MiB is
available. Hybrid routing alone spent93.972s reading4160tokens and47.450s generating
319tokens. This supports reducing prompt overhead as well as evaluating CUDA.

1. Prepare a digest-pinned CUDA sidecar on localhost18088 with the existing weights
   mounted read-only,initial8GPUlayers and identical8192context/output768/profile.
   Validate Compose before any download. No new weights or project dependencies.
   The repository prohibits downloads without applicable owner direction;prepare
   the concrete runtime/configuration first,then resolve that boundary explicitly
   if a new image is needed. Preserve the existing CPU container for rollback.
2. Independently compact repeated schema text in model prompts. Preserve the FULL
   decoder schemas,strict host validation,all instructions/source data,existing
   four calls and repair/deadline limits. Factor common oneOf fields only in the
   displayed schema;remove redundant title annotations with property names intact.
   Observe RED for equivalence/input-size boundaries,then GREEN. Do not drop the
   support check or replace LLM routing with keywords to report a speed gain.
3. Run one bounded matched actual-service observation for each route after the
   chosen runtime/profile is fixed. Keep old/new conditions and timing components
   explicit;do not combine cold/warm encoder or CPU/GPU changes into a causal claim.
   Compare actual outputs,not schema success alone. Stop the diagnostic once the
   stated latency question is answered;no prompt/model/seed parameter sweep.
4. Run relevant regressions and one independent final review. Record measured
   improvement,failures,configuration/digests and remaining language/scope limits.

Ruling:preserve the current call topology initially. Its independent style and
support stages have known quality limits;removing them before a matched comparison
would change behavior and conceal the latency source. Compact representation and
hardware are narrower interventions. No claimed response target until measured.

Thesis physical17–18/39–40,actual PNG,master12/14 and standing prompt decision
consulted. Undergraduate/read-only/structured-Prolog/unknown/source/release holds
stay;Phase10 remains separate. Existing owner-corrected workspace/MODELS root is
reused. Python3.13 readiness environment,no pytest cache,external evidence/temp.
Raw:workspace/audit-evidence/p09-latency-20261020/. Keep current plan/checkpoint/
progress in repository;no sole external plan and no untracked private artifact staged.
