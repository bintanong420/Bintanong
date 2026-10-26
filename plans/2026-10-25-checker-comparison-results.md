# Bounded checker comparison — stopped on truncation

25 October 2026. The [approved comparison](2026-10-21-checker-completeness-diagnosis-and-proposal.md)
has ended under its stop rule: **2 of at most8 completion calls attempted; no retry or replacement**.
Native thinking does not meet the gate within the fixed768-token output limit. No production
default/model/source/release changed. Phase11 remains active; expanded research release inactive.

## Authorization and verified controls

Owner approved the original diagnostic before /clear. After the first preflight stop, owner replied
"continue" to the original-code/server-start recovery, then "continue" to ONE healthy preflight repeat.
See [recovery evidence](2026-10-25-checker-comparison-recovery.md); the initial zero-call stops remain
preserved. Healthy repeat passed; there were no additional inference attempts.

- All57 saved evidence files and the prior diagnosis seal verified. Isolated181-file code snapshot
  from8060c7b matches original source byte hashes. All4 exact messages/schemas/identity hashes match.
- Resident build `b11723-31288c9c6`, model identity/path, template and server defaults match saved props;
  context8192. Existing container only; no recreation, downloads, installs or model substitution.
- Off request unchanged; on removes `reasoning_effort=none` and adds
  `chat_template_kwargs.enable_thinking=true` to template application and completion. No logit bias.
  Rendered prompts differ only by the expected thinking marker. All8 prompts fit8192 with768+8 headroom.
- Temperature0, seed0, cachefalse, schema constrained, output768 including thoughts/final,120s whole
  checker deadline. Frozen labels remain outside model input. Original public validators reused.

## Observations

| Fixed input | Thinking off | Thinking on |
| --- | --- | --- |
| English omitted charge (`d-en`) | Semantic FAIL;18.94s,354 output tokens | TRUNCATED;37.84s,768 output tokens; no final content |
| Eligibility versus filing (`b-relevance`) | Not run after stop | Not run after stop |
| Complete Filipino (`d-fil`) | Not run after stop | Not run after stop |
| Complete Taglish (`d-tl`) | Not run after stop | Not run after stop |

Off reproduced the original defect: the sole office claim c1 was mapped to both office r1 and
omitted-charge r2. All support verdicts and structural/identity checks passed, and the host ledger
reported `all_declared_parts_mapped`. Thus supported prose and a valid ledger still do not prove
semantic completeness. The correct result requires r2 uncertain/uncertain because the source gives
the charge but the draft omits it; source_gap/not_in_evidence would be incorrect here.

On returned `finish_reason=length`, an observable nonempty `reasoning_content` field and ZERO final
content characters. The field's presence establishes thought output, not useful/correct deliberation.
No thoughts were shown to students or quoted here. Truncation was rejected before review parsing;
remaining six calls were skipped exactly as required. The4/4 on gate is unsatisfied, not a measured
0/4 semantic score. No multilingual/relevance inference comparison was obtained.

## Timing and limits

Outer checker times above include HTTP and local final validation/assembly, excluding preflight.
Preflight HTTP aggregate0.177s includes props, template application and tokenization, not process/client
setup. Rendered/tokenize counts span1342–1661; first pair1342/1344. Server usage reports1343/1345
prompt tokens for that pair (one-token accounting difference, far within headroom).
Cold model startup elapsed time was not measured. Supabase, embeddings/retrieval, Prolog, full pipeline,
API/browser/student-visible end-to-end and load/queueing are not measured. No SLA or stable latency
percentile follows from these two serial observations; the first follows a model startup.

One pair is neither a calibrated accuracy estimate nor causal/statistical proof. This result rejects
enabling this mode under the tested resource contract; it does not establish that thinking can never
help at another budget. No larger-budget experiment, second judge or prompt sweep is authorized here.

## Evidence and next action

Workspace `audit-evidence/p11-checker-comparison-20261025/recovery/`: frozen inputs/labels/runner,
`preflight-ready.json`,2 attempt files,2 result files,`single-attempt.lock`,`summary.json`,
`analysis.json`,`delivery-manifest.json`. Raw responses/thoughts stay ignored. Delivery manifest SHA256:
`f8003582d72abab842b619724c5c9ad5b317ffb87f98e37fd1f6e5bc5b530adc`.
Shared Python3.13 `-X utf8 -B`: `compare.py preflight` exit0; `compare.py run` exit0 because it recorded
the mandated failure/stop (not a quality pass); `summarize.py` exit0. Offline assessor checks passed.
No production tests/full suite rerun for this diagnostic-only increment;5856e82 full suite/review pending.
Fresh delivery verification:15 sealed files,181 original-code hashes,exactly2 fixed attempts and120
local documentation links pass. Phase-state validation and Git whitespace checks pass.

Keep production thinking disabled; do not repeat this diagnostic automatically. Return to the pending
g2 quality correction using the current per-part generation path, preserving source-gap/precedence
holds and complete procedure steps. This historical checker probe does not diagnose or fix those
current production failures. Define a bounded correction from their existing live traces, then TDD,
review/full suite/live revalidation before any research pin switch. Frontend integration still follows
pending backend work. No phase advancement or institutional/public release permission is inferred.
