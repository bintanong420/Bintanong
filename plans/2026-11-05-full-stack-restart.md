# Full app-stack restart — 5 November 2026

Owner clarified "all" after the initial development-only interpretation. Restarted both app stacks and
the shared model, preserving code/branch separation, runtime settings and ngrok forwarding.

| Service | Source / process | Verified endpoint |
|---|---|---|
| Main frontend | p12 `8f15cfe0`, Node 83544 | 3216 `/chat`, `/api/health`: 200 |
| Main API | original launcher, Python 104428 (wrapper 97716) | 8021 `/health/ready`: 200 |
| Development frontend | p12-dev `4de10408`, Node 84036 | 3217 `/chat`, `/api/health`: 200 |
| Development API | cached candidate launcher, Python 78012 (wrapper 97628) | 8022 `/health/ready`: 200 |
| Shared Gemma | `bintanong-p09-cuda-latency` container | 18088 `/health`: 200 |
| Existing public tunnel | unchanged forwarding to localhost:3216 | public `/api/health`: 200 |

Final eight endpoint checks passed around 20:14 Manila; raw timestamped results:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p12dev-language-20261105/restart-20261105.json`.
These are readiness checks, not a fresh inference/accuracy benchmark. Process IDs are a dated observation.
Temporary chat state was reset; refresh and use New chat. The public tunnel continues serving the main branch;
the development fixes remain separate on localhost:3217. No merge, source/dependency change or institutional activation.

## Recovery details

- The existing `p12-env-20261031/keepalive.ps1` supervisor (42304) automatically relaunched the main frontend
  and API after their previous process trees were stopped. Stopped the duplicate manual API startup;
  retained the supervisor and its configuration. Main API startup log reported 151.67 s to construction.
- First Docker restart failed in the NVIDIA hook: `ldconfig terminated with signal 9`. Container OOM flag
  was false; low host RAM was observed, so an OOM cause is not established. After releasing the duplicate,
  a targeted `docker start` succeeded. The model completed its cold load in approximately 3m40s per log,
  retaining one slot / 8192 context and the same mounted GGUF. No model or context downgrade.
- The cached development launcher initially exposed the generic Docker-service health probe, producing
  503 despite its pipeline being loaded. Corrected only that ignored local launcher to declare its real
  readiness check, matching the existing API composition pattern:

```python
async def ready():
    model_ok, _ = await probe_http_service(h.config.model_url, '/health')
    janus_ok, _ = probe_janus()
    return model_ok and janus_ok and encoder.load_model() is not None
# Passed as ApiServices(..., ready=ready); encoder is fully loaded before listening.
```

- Restarted only the development API after that change. RED: 8022 readiness / frontend health 503;
  GREEN: both 200 with the actual model/Prolog/encoder check. Cached composition still performs no hosted
  currentness/auth-provider probe; this readiness result does not claim those checks occurred.
- Development launcher: ignored `p12dev-language-20261105/start-candidate.py`; frontend uses existing pinned
  Node/Next through `NODE_PATH`, webpack, `API_INTERNAL_URL=http://127.0.0.1:8022`, port 3217.
  No dependency link, install or download was needed. Other projects/reviewer services were not restarted.

Next: continue the recorded language/clarification fixes in the development branch. Coordinate further model
tests with collection; both stacks still share the same model slot. Preserve the main worktree's owner notes.
