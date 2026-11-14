# Phase09 CUDA and prompt-display observations

20 October 2026; p09/feat/p09-generation-validation. Implementation:5d92f9c
(CUDA configuration),24423f4 (compact schema display). Owner explicitly approved
downloading/testing the pinned official CUDA runtime; existing model weights were
reused. [Bounded plan](2026-10-20-phase09-latency-plan.md) and
[prior actual-service baseline](2026-10-20-live-backend-composition-results.md).
Phase09 remains active; Phase10 remains separate and unstarted.

## Measured behavior

Each new request traversed the actual application,LLM router/style,required
SEA-LION/PostgREST/pgvector and/or Janus path,integration,draft,support check and
validated rendering. No route override,preassembled evidence or fake inference.
Inputs are the unchanged fictional English requests from the prior delivery.

| Route | Prior CPU seconds | CUDA + compact display seconds | Time reduction |
| --- | ---: | ---: | ---: |
| RAG | 277.492 | 85.297 | 69.3% |
| Symbolic | 304.913 | 79.815 | 73.8% |
| Hybrid | 355.696 | 148.043 | 58.4% |

All3answered,4model calls each,1draft/1check/0repairs. Typed decisions and full
decoder schema hashes match the corresponding CPU observations. Requests/spec
hashes also match. These are single observations,not percentiles,load tests or
evidence that general student latency meets a product target. Explicit budgets
remain240s inference/generation,300s stage,600s request;default budgets unproven.

Before changing prompts,a CUDA Hybrid run with the original messages answered in
171.410s versus355.696s CPU. The same4160token routing prompt took6.813s to read
on CUDA versus93.972s CPU;319output tokens took28.209s versus47.450s. This supports
the configured CUDA runtime gain. CPU buildb11718 and CUDA buildb11723 differ;
this is not an isolated same-binary hardware experiment.

| Profile/route | Router + style s | Retrieval s | Janus s | Draft s | Check s |
| --- | ---: | ---: | ---: | ---: | ---: |
| CUDA original Hybrid | 47.816 | 64.284 | 2.318 | 45.351 | 13.884 |
| CUDA compact RAG | 25.309 | 23.678 | — | 25.489 | 10.765 |
| CUDA compact Symbolic | 40.135 | — | 0.409 | 28.067 | 11.159 |
| CUDA compact Hybrid | 54.152 | 22.099 | 0.426 | 55.774 | 15.966 |

Hybrid retrieval/Janus run concurrently;do not add both columns as sequential work.
Each process creates a fresh encoder/application. Original CUDA retrieval includes
64.284s of cold host/import/model startup cost;later runs took22–24s. The same-GPU
original-to-compact Hybrid model-call total actually rose107.042s ->125.884s while
retrieval fell64.284s ->22.099s. Compaction reduces prompt tokens (Hybrid router
4160 ->2480) but a separate end-to-end speed benefit is **not established**.
Generation length and observed decode speed also varied;no parameter sweep follows.

## Changes and retained boundaries

The localhost18088 sidecar reserves one NVIDIA GPU,mounts existing weights read-only
and refuses missing host paths/implicit image pulls. Official linux/amd64 manifest:
`sha256:f66a5229a3e0586339d16155e9fe09c37834d7a7f4134bbdee7360b5a1f2546d`.
Compressed layers2,594,107,748bytes(~2.42GiB). Buildb11723-31288c9c6;template hash
74a88f94c57c14e22dcdbe08e94127f42b87c6f584cb73838e73e32126f3f6b3 matches the CPU.
RTX3050Laptop4096MiB,driver596.36. Initial8layers used~1.1GB;one capacity adjustment
to24layers loaded successfully,2135MiB used/1828MiB free at final idle check.
Context8192,one slot,threads8,output768,temp0,seed0,reasoning-none/cachefalse retained.

CPU container bintanong-p07-router-offline is stopped intact to free RAM. CUDA
container bintanong-p09-cuda-latency is running;the runner must explicitly use
`--url http://127.0.0.1:18088`. Defaults still point to18087. See
[setup and rollback](../docker/bintu-cuda.md). No new model weights,project installs,
dependency/lock changes,hosted migrations or institutional source activation.

`compact_for_prompt` deep-copies schema display,removes title annotations and
factors identical parent/oneOf constraints. Real property names/literal objects,
descriptions,required fields and differing branch constraints remain. Full original
decoder schemas,host validation,instructions,source payloads,four-call topology and
repair/deadline limits are unchanged. Generation JSON whitespace is compacted too.
Prompt bytes changed:prior prompt captures are not fresh evaluations of this profile.

## Output assessment and limitations

RAG's2claims correctly identify the fictional desk and40token fee. Symbolic's2claims
describe the scoped prerequisite check and satisfied condition;canonical rendering
preserves the actual operation/curriculum/course. Hybrid's4claims include the
prerequisite,desk and fee,but c2 says the prerequisite check was "resolved and
verified,indicating eligibility" and cites only the document. That passage states
the prerequisite,not the student's executed check. The canonical eligible result
is correct,however this claim needs the symbolic evidence and tighter scope.
The same-model checker accepted it. Count7/8claims as clear support/scope fits and
1as a citation/scope concern in this small independent assessment,not accuracy.
The original CUDA run retained the earlier Hybrid "eligibility confirmed" concern.

No language-wide or institutional accuracy improvement is claimed. All new inputs
are English/fictional;two earlier Phase07 Taglish style errors remain disclosed.
Opaque runtime/source IDs still hurt readability. Institutional release,source,
privacy/auth and later private-file gates remain. Candidate output is inactive.
The one-week prompt improvement cap/no parameter training decision still applies.

## Verification and recovery

TDD:display helper RED missing module ->6passed1.69s;actual builder RED4failures.
After wiring,3legacy tests assumed byte-identical displayed/decoder schemas;updated
that assumption while preserving exact decision constraint and decoder immutability.
Focused GREEN200passed3.01s. New tests check actual4builders,unchanged request/evidence
payloads,valid/invalid schema acceptance and160audience/route/control/operation
combinations. Full relevant47-selection regression gate/result recorded below.

Raw root:C:/Coding-projects/bintanong_workspace/audit-evidence/p09-latency-20261020/.
`run_observation.py`,`verify_compact.ps1`,`compact-batch.log`,four reports/traces,
`cuda-24-final-server.log` and `comparison.json` bind calls,tokens,outputs and timing.
Input/code hashes are captured before inference. Delivery manifest also binds the
helper source and the official image/pull/Compose evidence in the parent directory.
Initial pull log records a skip because pull_policy=never;the approved pull uses
`pull --policy always`,then start uses `up --pull never`. No hidden second download.

Fresh47-selection regression gate:1892passed/66subtests95.14s,exit0;exact roster and
command in `verify-regressions.ps1`,output `final-regressions.log`. Independent final
review found no new current-schema production/Compose defect and confirmed the
Hybrid citation caveat;`independent-latency-review.md` records its lightweight checks.
Full decoder/transport hashes unchanged;no broad legacy suite or new model sweep.
Final delivery manifest SHA256:
36d0d060022be5287da2bf7ec5d415fae4ba5f596a59e1c26232b6a25519d901.
All85listed raw/source/config files rechecked against their hashes. The manifest
excludes this mutable documentation wrapper and test temporaries. Final docs hygiene
584passed1.20s;86local links resolve across the seven current delivery documents.

Next Phase09 action:address the demonstrated Hybrid prose/citation limitation in a
bounded RED/GREEN task before a broader reviewed multilingual quality evaluation.
Keep source/release gates and separate Phase10 boundary;do not infer readiness from
schema validity or these faster timings.
