# Local server startup,25October2026

Owner requested starting the merged local frontend56350f3. Reused existing launcher,
configuration, installed dependencies, image and external weights. No product code,
source release, dependency/lockfile or hosted data changes.

- Website http://127.0.0.1:3215 and /login return200.
- API http://127.0.0.1:8021/health/ready and frontend /api/health return200 ready:
  Supabase, Janus, embedding, Bintu and student_runtime all true.
- Anonymous API/frontend curricula return401. Authenticated list/chat is not tested.
- Model bintanong-p11-bintu reused at18088;32 NVIDIA GPU layers/context8192 unchanged.
- Strict encoder at8001 returns pinned SEA-LION configuration,1024 dimensions.
- Owner saw curriculum-list unavailable while API was still starting; requested refresh
  after readiness. Sign-in/session credentials were not accessed or exported.

## Repaired startup wiring

The old encoder container mounted backend-only p11, whose main.py lacks the strict
query router used by the frontend composition. /health200 was insufficient;
/query/configuration404 caused API startup failure. Source checkout remains1:1 with origin.
New bintanong-p11-embedding-frontend uses the SAME existing image/env/model/config mounts
and original Python entrypoint, binding main merged backend read-only at /app/backend.
The old container remains stopped for recovery. No build/download/install/weight copy.
One replacement creation omitted the image's overridden Python entrypoint and failed
before starting; only that newly created failed container was removed and recreated.
An internal strict-encoder load diagnostic passed; model/encoder cold loading took minutes.
API bootstrap retried once strict encoder became ready; final worker PID87176, exec session83795.
Frontend launcher PID73824. Temporary API sessions are new after startup.

## Verification and recovery

Ignored workspace audit-evidence/p11-20261025/local-server-start/ contains process,
container and HTTP receipts/logs. Final health-sequential.json records both readiness
successes. Simultaneous API/frontend readiness probes initially produced one transient
503 (hosted retrieval/runtime busy); sequential checks both passed. Concurrency cause
was not diagnosed, so this is readiness evidence, not a load/reliability claim.
No actual-model answer or authenticated curriculum/chat acceptance run.
Existing active p09-research-selected-20261022 remains pinned; expanded package inactive.

To stop this preview, target recorded API/frontend worker processes and the two named
model/encoder containers only. Preserve unrelated Supabase/other project services.
Old encoder can be restored by stopping the replacement and starting the retained
bintanong-p11-embedding, but its backend-only bind lacks the frontend strict query route.
