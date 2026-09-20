# Bintanong

Bintanong is an AI-powered academic guide built first for Palawan State University. Phase 0 establishes a Docker-first compatibility foundation; it does not yet implement the complete student chat workflow.

## Local Phase 0 workflow

Requirements: Docker Desktop with Compose, Node.js 24 LTS, and the supplied model directories outside this repository.

1. Copy `.env.example` to `.env` and adjust `MODELS_DIR` if necessary.
2. Install the project-local CLI with `npm ci`.
3. Start the loopback-bound local Supabase stack with `npm run supabase:start`.
4. Apply migrations from a clean database with `npm run supabase:reset`.
5. Start CPU services with `npm run compose:up`.
6. On a configured NVIDIA host, use `npm run compose:gpu` instead.

Tool jobs use the Compose tools profile:

```console
docker compose --profile tools run --rm ingest --help
docker compose --profile tools run --rm evaluate --help
```

The default services are `web`, `api`, `bintu`, and `embedding`. Supabase and application containers share the external `bintanong-local` network, whose default published-port binding is restricted to loopback.

See `plans/INDEX.md` for durable phase state and `docs/decisions/phase-00-compatibility.md` for execution-time version decisions.
