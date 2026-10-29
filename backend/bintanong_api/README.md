# Student research API

`research_app.load_research_app` composes the existing CPU query encoder, reviewed curriculum
runtime and answer pipeline with optional guest access and verified PSU Google authentication. Run exactly one Uvicorn
worker: private sessions and admission limits are process memory.

Set `BINTANONG_RESEARCH_CONFIG` to an ignored local JSON file, then start the factory:

```powershell
python -m uvicorn backend.bintanong_api.research_app:load_research_app --factory --host 127.0.0.1 --port 8021 --workers 1
```

The trusted config uses schema `bintanong-research-api-v1` and requires:

- `pin_path`, `pin_sha256`, `seal_sha256`: explicit approved pin and seal identities.
- `encoder_assets_path`: existing verification JSON with `verified_assets`.
- `encoder_model_path`: the existing local SEA-LION directory under workspace `MODELS`.
- `allowed_origins`: exact student frontend origins, including scheme and port.
- `allow_guests`: set `true` for owner-approved guest chat and temporary PDF upload access;
  the default `false` keeps the authenticated-only mode. Supplied tokens are always verified.
- Optional `model_url` (default `http://127.0.0.1:18088`), `program_names` and `curriculum_names`.

Supply `SUPABASE_URL` and the public `SUPABASE_ANON_KEY` in the process environment. The factory
does not load `.env` automatically, use a service-role key, configure OAuth or download assets.
It accepts only the current 78-chunk `p11-research-corrected-20261026` package and verifies all
seven sealed files before constructing a network client or encoder. A pin with `"documents": "local"`
(owner, 29 Oct 2026) instead serves its own sealed package from local files with the gate composition
(routing context, topic selection, the pin's `review_reference_profile`); curricula and their links are
still read and checked from the hosted release, and hosted chunks are not compared. A changed pin/package fails
startup; an inactive hosted release or changed curriculum links withholds subsequent answers.

For the Next.js server, set `API_INTERNAL_URL`, `SITE_ORIGIN`, `NEXT_PUBLIC_SUPABASE_URL` and
`NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`. Student requests stay under same-origin `/api/`; bearer
identity is verified again by FastAPI; absent credentials use a separate guest session only when
enabled. No guest account or Supabase anonymous user is created. Switching guest/account access
does not adopt private state. A local public key/configuration does not establish that the
hosted Google provider, redirect allowlist or an actual PSU login is available.

`GET /health/live` is process liveness. This factory's `/health/ready` checks its pinned hosted
resources, existing local encoder, Janus and model health endpoint through one `student_runtime`
probe; it does not use unrelated local Supabase/embedding-service defaults. Factory startup loads
the CPU encoder once before concurrent requests can reach it. Readiness is not an inference,
latency or answer-quality result.

Photos/scans remain unsupported. Upload text-based PDFs, review course choices, then confirm.
Keep private inputs and all runtime evidence ignored. No institutional/public deployment or
expanded-package activation follows from running this research composition.
