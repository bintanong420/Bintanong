# Running Bintanong against the hosted research release

How a developer runs the research backend, frontend and benchmark regression against the shared hosted Supabase
project. The repository holds the code only; university source data, the pinned release and credentials are not in Git
and come from a project maintainer.

The hosted release is a **research** release: it is not institutional approval, a public deployment or proof that the
sources are current. Undergraduate scope, source-gap, privacy and read-only advisory rules still apply.

## How it fits together

| Part | Where it comes from |
| --- | --- |
| Backend, frontend, tests | This repository |
| Documents (chunks, vectors) and curriculum facts | Hosted Supabase release named in the pin (read-only at runtime) |
| Pin, API config, sealed package, encoder verification | Ignored workspace files from a maintainer (below) |
| Hosted URL and public key | Ignored `.env` and `frontend/.env.local` from a maintainer |
| Gemma (Bintu) and SEA-LION E5 weights | `MODELS` directory beside the workspace (never in Git) |

At startup the backend loads the sealed package and checks every file against its seal. It then reads the 39
curricula from the hosted release. Before each answer it confirms that the hosted chunk set and the curriculum digests
still match the pin. If they don't, it refuses to answer instead of falling back to local data.

## What you need

1. **Supabase organization access.** An invitation to the organization that owns the hosted project, for the
   dashboard, logs and advisors. Runtime access uses only the public URL and anon (publishable) key.
2. **Credentials,** sent privately by a maintainer and never committed:
   - `.env` (repository root): `SUPABASE_URL`, `SUPABASE_ANON_KEY` and the `MODELS_DIR`/model settings from
     `.env.example`.
   - `frontend/.env.local`: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`, `SITE_ORIGIN`,
     `API_INTERNAL_URL`.
   - Only maintainers who stage or activate releases need `SUPABASE_SERVICE_ROLE_KEY` or the hosted database
     password. Running, testing or evaluating the system does not; leave them out of a copy you pass on.
3. **Workspace files,** a maintainer's copy of the ignored folders, keeping their relative layout:

   ```text
   bintanong_workspace/
   ├── worktrees/Bintanong/<phase>/        repository worktree (or the main checkout)
   ├── MODELS/                             GEMMA_4_E4B/, SEA-LION-E5-Embedding-600M/
   ├── dataset/                            original university sources (only for source/ingestion work)
   └── audit-evidence/
       ├── <hosted activation folder>/     hosted-research-api-config.json, hosted-research-pin.json,
       │                                   start_hosted_research_api.py
       ├── <runtime package folder>/       runtime-package/ (sealed chunks, vectors, catalogue, budgets)
       ├── <encoder calibration folder>/   encoder-verification.json
       └── <hosted regression folder>/     run_hosted_regression.py, compare_runs.py, cases.json, b-*.txt
   ```

   The current folder names are listed in `plans/INDEX.md` and the latest hosted activation results.
4. **Paths.** `hosted-research-api-config.json` and the pin hold absolute paths. Place the workspace at the same root
   as the maintainer (currently `C:\Coding-projects\bintanong_workspace`). If you use another root, edit
   `pin_path`, `encoder_assets_path` and `encoder_model_path` in the config and `package` in the pin. Then put the
   pin's new SHA-256 into the config's `pin_sha256`. Never edit a sealed package file: the seal check will
   (correctly) refuse it.
5. **Tools.** Python 3.13 with the backend's `api`, `embedding` and `dev` dependency groups from
   `backend/pyproject.toml` and `backend/uv.lock`, Node/npm for `frontend/`, Docker Desktop with an NVIDIA GPU,
   and SWI-Prolog for eligibility checks. A copied Windows `venv/` is not portable; build your own environment.

## Start the model server

Gemma runs in llama.cpp on `127.0.0.1:18088`, with the weights mounted read-only from `MODELS`:

```powershell
docker run -d --name bintanong-p09-cuda-latency --gpus all -p 127.0.0.1:18088:8080 `
  -v C:/Coding-projects/bintanong_workspace/MODELS:/models:ro `
  ghcr.io/ggml-org/llama.cpp@sha256:f66a5229a3e0586339d16155e9fe09c37834d7a7f4134bbdee7360b5a1f2546d `
  --model /models/GEMMA_4_E4B/gemma-4-E4B-it-UD-Q4_K_XL.gguf --host 0.0.0.0 --port 8080 --ctx-size 8192 `
  --parallel 1 --threads 8 --n-predict 768 --n-gpu-layers auto --fit-target 512 --no-webui --jinja
```

Afterwards, `docker start bintanong-p09-cuda-latency` is enough. Wait until `http://127.0.0.1:18088/health` returns 200
(503 means it is still loading). If Docker Desktop stops, every answer fails within seconds with
`model_connection_error`.

## Run the backend and frontend

From the repository root, each in its own terminal:

```powershell
# backend: research API on 127.0.0.1:8021 (ready after about 1.5 minutes; prints "app constructed")
<python> -X utf8 <hosted activation folder>\start_hosted_research_api.py

# frontend: on 127.0.0.1:3216 (must match allowed_origins in the API config)
cd frontend
node_modules\.bin\next dev -p 3216
```

Sign-in and guest settings come from the API config (`allow_guests`) and the hosted Supabase Auth settings. See
[Google sign-in setup](google-sign-in-local-setup.md).

## Run the benchmark regression on hosted data

The hosted regression runner answers the 50 benchmark questions exactly as the backend does, with documents and
curricula from the hosted release. It refuses to run with uncommitted `backend/` changes and won't reuse a suffix.
Stop the backend and frontend first on an 8 GB GPU machine.

```powershell
$env:PYTHONUTF8=1
$H="<hosted regression folder>"
foreach ($b in 1,2,3) {
  $env:GATE_ONLY = Get-Content "$H\b-6b7d2a7-$b.txt" -Raw
  $env:GATE_SUFFIX = "-<your-tag>-b$b"
  & <python> -X utf8 "$H\run_hosted_regression.py" *> "$H\run-<your-tag>-b$b.log"
  "batch $b exit $LASTEXITCODE"
}
<python> "$H\compare_runs.py" "<earlier run>\results.jsonl" "$H\run-*-<your-tag>-b*\results.jsonl"
```

Read `results.jsonl` (one line per question, with `passed` and `why`), not the log: PowerShell writes the `*>` logs as
UTF-16. A `getaddrinfo failed` exception is a hosted network drop; rerun that batch with a new suffix. Single runs
vary by about one case, and these 50 questions have been used for development, so report scores as development
results, not a held-out evaluation.

## Tests

The test suite uses synthetic fixtures and the **local** Supabase, not the hosted project. Start local Supabase (and
wait until it is healthy) before the full suite: the storage/database tests need it. Stop it again before long
model runs if memory is tight.

## Rules

- Never commit `.env`, `frontend/.env.local`, workspace evidence, university sources or model weights.
- Treat the hosted release as read-only. Staging or activating a release, changing hosted schema, or
  changing source data needs the project owner's decision and a recorded procedure; see `plans/` for the
  hosted activation records.
- Answers stay candidate research output; do not present them as official university guidance.
