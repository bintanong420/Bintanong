---
artifact: phase-plan
phase: 0
status: in_progress
master: plans/master_implementation_plan_original_long.md
previous_handoff: null
---

# Phase 0 Docker and Compatibility Foundation

> **For agentic workers:** Use `executing-plans` or `subagent-driven-development`, follow TDD, update `plans/phase-00-checkpoint.md` after each verified task, and do not create Phase 1 until a verified Phase 0 handoff exists.

## Goal

Build a reproducible Docker-first foundation that proves local Supabase/pgvector, FastAPI with Janus, Docling, SEA-LION embeddings, Bintu GGUF inference, GPU partial offload, and Next.js-to-FastAPI health connectivity on the available development machine.

## Global Constraints

- The master plan governs architecture and scope, but its software versions are historical rather than binding.
- Select a current stable, mutually compatible dependency cohort from official documentation and registries; pin only after smoke tests pass.
- Preserve the supplied Bintu and SEA-LION artifacts without conversion or re-quantization.
- Target the available RTX 3050 Laptop GPU with 4 GB VRAM and retain a measured CPU fallback.
- Do not ingest institutional or private documents in Phase 0; use a synthetic PDF fixture.
- No checkpoint can complete a phase. Only a verified `phase-handoff` with `status: complete` permits Phase 1 planning.

## Review Focus

- A stale checkpoint must not override newer commits or a dirty working tree.
- Missing or modified model files must fail with an actionable error before inference.
- Dependency outages must produce typed readiness failures rather than false-ready responses.
- GPU tuning must retain VRAM headroom and avoid treating full-model residency as required.
- Local Supabase must remain loopback-bound and no service-role secret may reach browser code.

## Tasks

- [x] **Task 1: Durable phase continuity** — create and test the phase-state validator, project handoff skill, index, plan, checkpoint, and artifact contract.
- [ ] **Task 2: Current compatibility matrix** — resolve current stable versions from official sources and record selected/rejected combinations.
- [ ] **Task 3: Repository and container scaffold** — add pinned manifests, Dockerfiles, Compose profiles, environment/ignore files, and shared-network bootstrap.
- [ ] **Task 4: API, Janus, and Supabase probe** — implement liveness/readiness, Janus query, pgvector migration, and database compatibility checks.
- [ ] **Task 5: SEA-LION embedding service** — verify model manifests and expose health/encode interfaces with 1,024-dimensional finite vectors.
- [ ] **Task 6: Docling tools** — parse a committed synthetic PDF and expose deterministic ingestion/evaluation command help.
- [ ] **Task 7: Bintu llama.cpp compatibility** — verify GGUF integrity, structured JSON generation, CPU baseline, queue/timeout behavior, and RTX 3050 partial offload.
- [ ] **Task 8: Next.js health surface** — implement the same-origin health proxy and ready/degraded status page.
- [ ] **Task 9: Integrated verification and handoff** — run the complete exit gate, record measurements and exact pins, write the final handoff, supersede the checkpoint, and update the index.

## Public and Internal Interfaces

- API: `GET /health/live`, `GET /health/ready` (`200` ready, `503` degraded).
- Embedding service: `GET /health`, `POST /encode` with a non-empty text list and 1,024-dimensional vectors.
- Bintu: internal OpenAI-compatible llama-server chat endpoint with compatibility JSON Schema fields `route`, `confidence`, and `reason`.
- Tools: `ingest --help`, synthetic PDF parse command, and `evaluate --help` through the Compose `tools` profile.
- Continuity: `phase_state.py inspect|validate|can-advance --repo <path> [--json]`.

## Exit Gate

Phase 0 is complete only when fresh evidence proves both Compose configurations render; local Supabase resets with pgvector; API-to-database and Janus probes pass; English and Tagalog/Taglish embeddings are finite and 1,024-dimensional; Docling parses the synthetic fixture; Bintu produces schema-valid output on CPU and partial CUDA offload; the browser displays readiness; failure modes are typed; no prohibited files are tracked; and a fresh-context simulation resumes without repeating completed work.
