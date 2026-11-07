# PR20 recovery routing follow-up

Owner reproduced an unavailable answer on staging3218, then confirmed BSCS2018–2019.
The question asks what failing CC4/L blocks and how to return to regular load quickly.
This is a hypothetical curriculum dependency/recovery request, not an explicit proposed schedule.

## Diagnosis and correction

- Existing model container had exited255; Docker did not mark it OOMKilled. Cause unproven.
  Restarted the existing container, preserving model/configuration and other services.
- After recovery, the exact question still failed: topic selection succeeded, then routing
  input8065 plus output768 and guard8 exceeded the configured8192-token context.
- Condensed repeated router instructions without deleting menu facts, field values, source
  headings/context, limitations, or decoder/host validation. Router prompt version26.
- Explicitly distinguish recovery advice from checking a student-proposed schedule; retain
  literal course targets and hypothetical failure. Remove stale single-operation prompt wording;
  the host still enforces the default-OFF compound capability boundary.
- Exact live router trace after correction:7351 input tokens, Symbolic/list_affected_courses
  on reviewed CC4/L, hypothetical failed premise retained, no repair. Existing host recovery
  normalization folds the interpreted recovery parts; no new keyword routing bypass.
- Context configuration remains8192. Initial request now fits, but longer menus/history or
  repair messages can still exceed this bound. This is not universal overflow elimination.

## Verification

Synthetic regressions observed RED for excessive document instructions and missing recovery
guidance, then GREEN. Focused99 tests pass; broader routing/recovery gate1,077 passes:

```powershell
& C:/Coding-projects/bintanong_workspace/audit-evidence/p12-env-20261031/venv/Scripts/python.exe -m pytest tests -q -p no:cacheprovider --basetemp C:/Coding-projects/bintanong_workspace/audit-evidence/pr20-routing-final -k 'routing or generation_recovery_reply'
```

Raw traces remain ignored under `audit-evidence/pr20-local-staging-20261107`.
`recovery-overflow-original-request.json` preserves the initial oversized prompt;
`recovery-router-result.json` records the corrected routing trace.
Staging API reloaded at code `c5f20a4e`. Full pipeline replay answered; direct API answered
in40.09s. Frontend proxy initially still failed in6.5s. After restarting only staging frontend,
exact frontend-proxy request answered in44.37s, English, no SSE errors. Retains hypothetical
failure, dependent-course list, recovery drafts, source quotations and known prerequisite/load
limitations. No actual browser latency measurement. Transport discrepancy cause remains unproven;
frontend restart resolved the recorded reproduction. Do not claim a permanent transport repair.
The answer is long and favors DraftD although another displayed draft rejoins earlier under its
assumptions. Some terms exceed prescribed load or have unknown elective prerequisites. This check
proves availability and guarded output, not optimality/advisability of the preferred recovery plan.

## Context capacity question

The owner asked about increasing context while supporting RTX3050/16GB RAM and
RTX4060/32GB RAM. Current machine measurement: RTX4060 Laptop8188MiB total,
5687MiB used,2270MiB free. System free physical RAM was about2.8GB, reflecting the
whole concurrently running machine, not Bintanong's standalone requirement.
Current container explicitly uses `--ctx-size8192`, one slot and automatic GPU layers.

The [official llama.cpp server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
documents context/cache controls. A12288-token configuration is a proposed measured
trial, not a verified fit or changed default. Owner requested worst/best cases: RTX3050 dedicated VRAM4GB/6GB with16GB RAM;
neither larger-context memory/latency nor full-stack16GB suitability has been measured.
No cache quantization, GPU offload, dependencies or model assets were changed.
