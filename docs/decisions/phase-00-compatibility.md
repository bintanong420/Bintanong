# Phase 0 Compatibility Decision

Date: 2026-09-20
Status: accepted candidate cohort; immutable locks and image digests follow smoke tests

## Policy

The master-plan and thesis versions are historical inputs. Phase 0 selects the newest stable mutually compatible cohort available at execution time and excludes prereleases.

## Selected cohort

- Python 3.13.15.
- FastAPI 0.141.1, Uvicorn 0.53.0, and Pydantic 2.13.5.
- httpx 0.28.1 and asyncpg 0.31.0.
- Torch 2.14.0 and NumPy 2.5.3, with CPU execution mandatory.
- Sentence Transformers 6.1.0.
- Docling 2.129.0.
- janus-swi 1.5.3 with SWI-Prolog 10.0.2 stable, built against the API Python.
- pytest 9.1.1, pytest-asyncio 1.4.0, reportlab 5.0.1, and uv 0.12.17.
- Node.js 24.21.0 LTS Krypton with npm 11.19.0.
- Next.js 16.3.5, React 19.3.0, TypeScript 7.0.2, and ESLint 10.11.0.
- Project-local Supabase CLI 2.117.0. Its PostgreSQL and pgvector versions become authoritative after local reset.
- llama.cpp v0.4.1: server-v0.4.1 for CPU and server-cuda-v0.4.1 for CUDA 12.
- Host baseline: Docker 29.6.1 and Compose 5.3.0.
- GPU target: RTX 3050 Laptop, 4096 MiB, driver 596.36; retain at least 512 MiB headroom.

## Fixed supplied artifacts

- Bintu: GEMMA_4_E4B/gemma-4-E4B-it-UD-Q4_K_XL.gguf; SHA-256 3CF61DE12DAA015EE0F7B68E7B7C541405BF220E1E942BAD8B47CAB827D7DF80.
- SEA-LION: SEA-LION-E5-Embedding-600M/model.safetensors; SHA-256 DF5B1C55623EEB5EF09CE3F3C50E24E2DB433D7D1BBCCCF76D2F01BA212DF5F1.
- Whole model directories are mounted read-only and a generated manifest verifies accompanying files.

## Evidence

- The exact top-level Python pins completed a pip no-install resolution on CPython 3.13.
- Context7 official snapshots confirmed current FastAPI container, Docling CPU/local-artifact, and Sentence Transformers encoding APIs.
- PyPI and npm metadata supplied stable versions and runtime constraints.
- The Node distribution index identifies v24.21.0 as LTS Krypton.
- Supabase documents project-local CLI installation, a loopback-bound network, and db reset reproducibility.
- The official llama.cpp workflow creates numbered image tags as image-source-tag.

## Rejected combinations

- Master-plan historical pins: obsolete as execution-time authority.
- Python 3.14: Python 3.13 has confirmed wheels and a successful joint resolution with less native-extension risk.
- Host Python 3.13.7: behind the current 3.13 patch.
- Node 26: not the active LTS line on the decision date.
- Supabase CLI 2.118.0-beta.55: prerelease with no required capability.
- Moving llama.cpp tags: not reproducible.
- CUDA 13 image: CUDA 12 is the documented broad-compatibility image and is sufficient here.
- Full GPU residency: the GGUF exceeds the 4 GiB budget; partial offload is required.
- Separate PostgreSQL container: the real local Supabase CLI stack is required as a versioned unit.

## Sources

- https://pypi.org/
- https://registry.npmjs.org/
- https://nodejs.org/dist/index.json
- https://supabase.com/docs/guides/local-development
- https://github.com/ggml-org/llama.cpp/releases/tag/v0.4.1
- https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md
- https://www.python.org/ftp/python/
- https://www.swi-prolog.org/download/stable

## Pending finalization

After smoke tests, record lockfiles, Supabase PostgreSQL and pgvector versions, OCI digests, llama.cpp metadata, and any runtime-driven downgrade.
