# Bintanong

Bintanong is a thesis project for a read-only academic guide to Palawan State
University undergraduate academic affairs. Its architecture combines document
retrieval with structured knowledge and Prolog reasoning. The supported study
scope is undergraduate academic affairs for 2026–2027; the complete student chat
workflow and institutional deployment are not yet delivered.

This README explains the main `bintanong_workspace/Bintanong/` checkout and its
developer workspace, including data that a Git clone does not contain. Paths below
start at `bintanong_workspace/` or are relative to the repository root as indicated.

Workspace paths reviewed **17 October 2026**; pipeline guide added **19 October 2026**.
Use the phase index for current delivery status.

## Start here when taking over

1. Read [AGENTS.md](AGENTS.md), the [phase index](plans/INDEX.md) and
   [current progress](plans/plan_current_progress/current_progress.md).
2. Follow the index to the active phase plan, checkpoint and previous handoff.
   Read the [developer pipeline map](docs/development/pipelines.md) for the source
   preparation/request flows, module responsibilities and later generation/API work.
   Institutional release remains gated; the index and Git determine current status.
3. Read the relevant sections of the
   [master plan](plans/master_implementation_plan_original_long.md). Consult the
   [thesis](Context/bintanong_thesis_for_context.pdf), especially physical17–18
   for scope, and the
   [routing diagram](Context/bintanong_full_runtime_routing_architecture.png).
4. Inspect Git before changing files. Preserve existing developer/owner changes.
   Check the ledger from the repository root:

   ```powershell
   python -B .agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .
   ```

5. Obtain the authorized local-data handoff described below before running a
   source-backed job. A missing ignored directory in a new clone is
   expected; it is not a reason to reacquire sources or repeat completed runs.

## Tracked repository structure

```text
Bintanong/
├── AGENTS.md                   Development rules and standing owner decisions
├── README.md                   Developer entry point and local-data map
├── Context/                    Thesis and intended runtime architecture
├── backend/
│   ├── bintanong_api/          API/service scaffold and model client
│   ├── bintanong_contracts/    Typed source, span, chunk and runtime contracts
│   ├── bintanong_embedding/    Embedding adapter and batch verification
│   ├── bintanong_retrieval/    Retrieval, context assembly and evidence policy
│   ├── bintanong_routing/      Multilingual LLM interpretation and validated routing
│   ├── bintanong_orchestration/ Pinned candidate route execution and integration
│   ├── bintanong_storage/      Registration, loading and release interfaces
│   ├── bintanong_symbolic/     Authoring/compiler and bounded research Prolog runtime
│   ├── bintanong_tools/        Ingestion, extraction and source-review tools
│   ├── pyproject.toml         Python version and dependency groups
│   └── uv.lock                Locked Python dependencies
├── frontend/                  Next.js interface scaffold and its lockfile
├── knowledge/
│   ├── manifests/             Tracked vocabularies, schemas and synthetic examples
│   └── rules/                 Rule workspace placeholder; no active corpus implied
├── evaluation/                Case schemas, synthetic fixtures and evaluation code
├── tests/                     Code tests and synthetic fixtures
├── scripts/                   Maintenance, inspection and asset utilities
├── supabase/                  Database configuration and versioned migrations
├── docker/                    Service/tool Dockerfiles
├── compose.yaml               CPU service definitions and tools profile
├── compose.gpu.yaml           NVIDIA override
├── docs/development/          Developer pipeline and module navigation
├── docs/decisions/            Technical decisions and verification records
├── plans/                     Formal plans, checkpoints, handoffs and progress
├── .agents/skills/            Repository workflows, including phase handoff
├── .env.example               Non-secret configuration template
├── .gitignore                 Rules for local-only files
└── .dockerignore              Files excluded from Docker build contexts
```

The tables below describe additional local directories. They are not delivered
by the tracked tree above. The presence of a module or migration does not imply
that its full planned runtime capability is active.

## Workspace and data locations

The current owner's Windows workspace is organized as follows. Other developers
must resolve their actual paths explicitly rather than assume these directories
exist on their machine.

```text
bintanong_workspace/
├── Bintanong/                                  Main checkout; run commands here
│   └── dataset/                                Ignored institutional originals
├── MODELS/                                     Model assets outside the checkout
│   ├── SEA-LION-E5-Embedding-600M/
│   └── GEMMA_4_E4B/
└── audit-evidence/                              Local execution/handoff evidence
    └── <task-or-run-name>/
```

Keep model weights outside all repository checkouts. Keep task data, generated
outputs and test temporaries under `bintanong_workspace`, in ignored
`audit-evidence` folders. If your workspace differs, record the path mapping in
the handoff and pass the resolved paths explicitly. From the main repository root,
the dataset is `dataset/`, models are `../MODELS/`, and evidence is
`../audit-evidence/`. Older handoffs can name the former Phase 05 worktree or model
location; resolve those references against this layout and verify recorded hashes.

### What a developer needs

| Work being performed | Required local inputs | Where to obtain or resolve them |
| --- | --- | --- |
| Read code/docs; run phase-ledger checks | Tracked repository and Python3.13 | Git checkout; no institutional PDFs or model weights needed |
| Synthetic unit tests | Suitable existing Python environment and the tracked fixtures | Dependency groups in `backend/pyproject.toml`; active environment recorded below |
| Source inspection or ingestion | Exact original PDFs/images, source inventories and applicable review records; converter/OCR assets for jobs using them | Owner-authorized data handoff, `dataset/`, relevant task's `audit-evidence` directory |
| Real embedding or query encoding | Complete SEA-LION model/tokenizer files, verified asset manifest and matching configuration | External `MODELS/` and the embedding/retrieval handoff |
| Resume saved Phase 05 retrieval work | Matching chunks, source versions, saved document/query vectors, annotations and manifests | Named evidence directories in the active checkpoint/reports; reuse compatible artifacts |
| Storage integration tests | Running local database container, its actual name and a fresh evidence directory | Existing local stack and `tests/storage_database.py`; uses disposable test databases |
| Full model-service scaffold | Approved environment/dependencies, external SEA-LION and GEMMA assets, local database/service configuration | `.env.example`, Compose files and the relevant phase decisions |

Ask the project owner for the authorized source/evidence handoff when these
inputs are absent. Do not recreate a supposedly equivalent source from a web
search, fabricate missing review events, or use synthetic vectors as real-model
evidence. Exchange credentials separately; private student uploads are not part
of the institutional corpus handoff.

## Institutional originals: `dataset/` (ignored)

The dataset is at `bintanong_workspace/Bintanong/dataset/`. The
[dataset-location guide](plans/dataset-locations.md) contains the detailed source
map, relocation history and source status; its Phase 05 worktree paths predate the
owner's move to the main checkout. Preserve original bytes, filenames and relative
paths. The present categories include:

```text
dataset/
├── CitizenCharter/
│   └── 2025/University/
│       └── PALAWAN-STATE-UNIVERSITY-Citizens-Charter-2025-4th-Edition.pdf
├── StudentHandbook/
│   └── 2021/PSU Student Handbook.pdf
├── PalSU Undergraduate Prospectus Website Dump/
│   └── Tiniguiban - Main/
│       └── <college>/<existing program and curriculum paths>/<original PDF>
├── Misc. Student related procedures/             Original memo/enrollment images/PDFs
├── Student Government Constitutions and Election Code/
├── Memoranda/                                   Organized year/UnknownYear folders
├── Incoming/                                    Dated intake/staging folders
└── Deferred/                                    Retained, deferred source categories
```

The prospectus college folders currently include CAD, CAH, CBA, CCJE, CHTM, CNHS,
CoE, CS and CTE. Folder presence is an inventory fact, not approval of every file.
Some staging/year directories can be empty. Folder years do not establish a
document's effectivity or precedence.

For the practice-exam tools, `--source-root` is the **prospectus directory**, not
the enclosing `dataset/` directory:

```text
bintanong_workspace/Bintanong/dataset/PalSU Undergraduate Prospectus Website Dump/
```

The former `backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/` location
was moved to root `dataset/`. Do not recreate it. For historical paths under
`worktrees/Bintanong/p05/dataset/`, resolve the suffix after `dataset/` under the
main checkout's `dataset/`. For the earlier backend location, also consult the
relocation map in the dataset guide. Verify the original SHA-256 when resolving
a saved path and preserve sealed records unchanged.

Select clauses and services applicable to undergraduates. Keep complete originals
as evidence even when they contain excluded audiences. Missing text, conflicting
deadlines and disputed digits remain recorded limitations. Read the
[scope policy](plans/undergraduate-scope-policy.md),
[source-gap policy](plans/source-gap-policy.md) and
[service-table policy](plans/service-table-association-policy.md) before deriving
new content. Private uploads never become institutional originals by default.

## Generated data and evidence: `audit-evidence/` (local only)

Each task/run has its own directory. Exact historical filenames vary by tool;
follow the corresponding report and manifest. A useful organization for a new
task is:

```text
audit-evidence/<task-or-run-name>/
├── <input inventory and source/hash bindings>
├── <conversion or candidate bundles>/
├── <review records, original-page renders and field/span bindings>
├── <embedding manifests and vector JSONL>
├── <evaluation cases, observations and reports>
├── <execution logs, raw SQL and verification results>
└── <evidence manifest/seal, when the task is sealed>
```

This is a layout convention, not a schema requiring every directory for every
task. Keep a new task's plan, decisions and human-readable handoff tracked under
`plans/`; do not leave the only current instructions in an ignored run folder.

The current `document_ingest` candidate-bundle contract has this exact shape:

```text
<candidate-bundle>/
├── manifest.json
├── source_register.json
├── chunks.json
├── ingestion_report.json
└── conversion/
    ├── manifest.json
    ├── raw_docling.json
    ├── raw_docling.meta.json
    └── prospectus_candidates.json OR procedure_candidates.json
```

The manifest binds the artifact hashes; the conversion metadata binds conversion
to the original source bytes. Older tools can have different bundle formats.
Do not rename/add files inside a validated bundle to resemble this example.
Parser success alone does not establish content review or source approval.

### Data relationships to preserve

| Artifact | Required relationship |
| --- | --- |
| Original source and source version | Exact source SHA-256, document/version/edition identity, acquisition location and independent governance states |
| Source spans | Source/version identity, physical page, locator/region and visible text |
| Chunks | Exact content hash and spans; applicable scope, field associations, limitations and required neighbors |
| Embeddings | Matching chunk identity, model/revision, preprocessing/prompt/tokenizer fingerprints, dimension and normalization |
| Review records | Actual reviewer/event attribution, exact field/span coverage, timestamps and unresolved holds |
| Evaluation cases | Scenario/language/split, expected evidence and applicable reviewed source references; separate development/final groups |
| Release/evaluation results | Exact input package/configuration and code version; an inactive draft does not become an authorized release through successful loading |

Schemas and validators live in
[contracts](backend/bintanong_contracts/),
[manifest schemas](knowledge/manifests/schemas/) and
[evaluation documentation](evaluation/README.md). Real-source JSON and JSONL
stay local; tracked examples and tests use synthetic fixtures.

### Current Phase 05 handoff artifacts

The selected document package has 19 chunks, 52 field associations, 54 source
spans and 19 saved document vectors across five source identities. It is a bounded
research selection, not the complete corpus. Its rationale is recorded in the
[accepted chunking justification](plans/2026-10-16-rag-chunking-research.md).

These paths are relative to `bintanong_workspace/audit-evidence/`:

| Directory | Important contents/purpose | Tracked recovery document |
| --- | --- | --- |
| `p05-release-readiness-20261016/` | `draft-chunks.json`, `draft-source-versions.json`, `draft-embedding-manifest.json`, `draft-embedding-records.jsonl`, `draft-subject-catalogue.json`, `draft-source-review-register.json` and package validation | [Loader readiness](plans/2026-10-16-document-loader-readiness-report.md) |
| `p05-source-registration-20261016/post-review-draft/` | `explicit-storage-documents.json`, used with the initial pending registration package | [Registration delivery](plans/2026-10-16-source-registration-report.md) |
| `p05-acquisition-observation-20261016/` | `bound-byte-check-envelopes.json`, `observed-source-versions.json` and verification | [Acquisition delivery](plans/2026-10-16-acquisition-observation-report.md) |
| `p05-partial-source-review-20261016/post-review/` | `partial-review-receipts.json`, `partially-reviewed-source-versions.json`, rehearsal and verification results | [Partial-review delivery](plans/2026-10-16-partial-source-review-report.md) |
| `p05-document-policy-selection-20261016/` | `frozen-profile.json`, `input-bindings.json`, `engine-results.json` and selected-profile verification | [Selected profile](plans/2026-10-16-document-development-profile.md) |
| `p05-source-evidence-reconciliation-20261016/` | Existing source-event mapping, attribution and retained input hashes | [Source-event reconciliation](plans/2026-10-16-source-event-evidence-reconciliation.md) |

The selected profile's `input-bindings.json` identifies four saved query-vector
inputs, also relative to the audit-evidence root:

```text
p05-development-retrieval-preflight-20261014/current-query-embeddings.jsonl
p05-approved-natural-query-evaluation-20261015/new-query-vectors.jsonl
p05-temporal-unsupported-evaluation-20261015/new-query-vectors.jsonl
p05-document-evidence-calibration-20261016/new-query-vectors.jsonl
```

Keep their case identities, configuration and input digests. The profile selects
the relevant accepted document cases; these files are not instructions to run
every historical case again.

The source snapshots have an explicit lineage: registration starts from
`draft-source-versions.json` (pending); acquisition uses the bound byte-check
envelopes and yields `observed-source-versions.json`; C1 uses that observed
expected register plus the exact partial-review receipts and yields
`partially-reviewed-source-versions.json`. These are retained evidence snapshots
from disposable rehearsals, not assertions that a shared database contains them.

Transfer complete manifest-bound packages and their referenced inputs, not just
the few filenames in this table. The delivery reports linked from the phase index
identify exact hashes, seals and dependencies. Initial pending registers and later
observed/partially-reviewed snapshots represent different steps; do not exchange
them blindly. Successful selected review does not imply whole-source review.

For sealed directories, use the recorded verifier in **verify mode only**.
Do not rerun historical writers inside them, edit timestamps/paths, or replace
their manifests. New checks/logs belong in a new sibling evidence directory.
Reuse compatible saved vectors rather than encoding again because a developer
or CLI account changed.

## External models and tool assets

```text
<MODELS_DIR>/
├── SEA-LION-E5-Embedding-600M/
│   ├── model.safetensors
│   ├── config.json
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   ├── modules.json
│   └── <remaining original tokenizer/SentenceTransformers files and subdirectories>
└── GEMMA_4_E4B/
    └── gemma-4-E4B-it-UD-Q4_K_XL.gguf
```

Retain the complete supplied model directory, not only the weight file. The
current owner location is `bintanong_workspace/MODELS/`, beside the main checkout.
Set `MODELS_DIR` in the ignored local `.env` to the resolved host path for
`../MODELS/`; `.env.example` still names the former model location. Compose mounts
it read-only at `/models`, and the embedding service resolves that container path
through `MODELS_ROOT`. Model-relative paths are configured in `.env.example`.
Do not copy/download weights into Git.

Real retrieval also needs its verified asset manifest: a JSON mapping of
model-relative filenames to SHA-256 values. Use the active embedding/retrieval
handoff for actual asset digests and encoder fingerprints. Example environment
values and model revision IDs are not a fresh verification of file bytes.
See [retrieval setup](backend/bintanong_retrieval/README.md).

The owner's existing Python3.13 environment is:

```text
bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe
```

Its parent also contains the established `hf-cache/` and `docling-artifacts/`.
Conversion/OCR tasks can require these approved assets in addition to SEA-LION
and GEMMA. Resolve `DOCLING_ARTIFACTS_PATH`, Hugging Face cache paths and offline
settings from the [dataset/environment guide](plans/dataset-locations.md#current-real-execution-environment)
and the task's verification report. Reuse the existing environment and assets;
do not reinstall or trigger automatic downloads during a handoff. OCR backends
can require additional tools/assets; follow the relevant OCR plan rather than
installing all optional dependency groups.

A Windows virtual environment is machine-specific. For a different machine or
operating system, hand over the dependency locks/setup reports and provision a
compatible Python3.13 environment under the applicable owner instruction;
copying the old `venv/` directory is not a portable setup method.

## Environment and local execution

Python is pinned to3.13 by `backend/pyproject.toml`; Node/npm pins are in the root
and frontend `package.json` files. Python dependency groups and `backend/uv.lock`,
plus the JavaScript lockfiles, define the recorded environments. Existing
workspaces reuse them. New-machine dependency/model provisioning requires the
applicable owner instruction; this README does not perform it.

Copy `.env.example` to an ignored `.env` only when creating a missing local
configuration. Preserve an existing `.env`; do not print or commit its secrets.
The example describes the Compose scaffold. The storage HTTP client separately
reads `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` and optional
timeout/DB settings; see [storage documentation](backend/bintanong_storage/README.md).
Administrative credentials stay server-side. A Docker-internal database hostname
is not automatically resolvable from a host-side Python process.

The root package exposes historical scaffold commands for starting local
Supabase, CPU/GPU Compose services and tools. Read
[Phase 0 compatibility](docs/decisions/phase-00-compatibility.md) and the active
phase authorization before running them. `supabase:reset` resets local database
state; it is not a resume step. Running Compose can build images/download
dependencies, and shared migration application/activation have separate gates.
The service scaffold is not a complete student application.

For tests, use an existing suitable environment, disable bytecode/pytest cache,
and put all temporaries in a new task directory. Example from the repository root:

```powershell
$workspaceRoot = (Resolve-Path -LiteralPath '..').Path
$pythonPath = "$workspaceRoot/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe"
$runRoot = "$workspaceRoot/audit-evidence/dev-$([guid]::NewGuid().ToString('N'))"
New-Item -ItemType Directory -Path $runRoot | Out-Null
$env:TEMP = $runRoot
$env:TMP = $runRoot
$env:BINTANONG_STORAGE_EVIDENCE_DIR = "$runRoot/database"
& $pythonPath -B -m pytest -q -p no:cacheprovider tests/test_retrieval_context.py --basetemp "$runRoot/pytest"
```

Adjust the interpreter/workspace to your actual environment. The example is a
focused synthetic context test, not a full phase exit check. Database integration
tests additionally require Docker and the local database container. Set
`BINTANONG_STORAGE_TEST_CONTAINER` to the actual name if it differs from the
harness default `supabase_db_Bintanong`. The harness creates uniquely named
`bintanong_storage_test_<uuid>` databases, applies migrations only there and drops
its own database; it does not reset the shared application database.

After those integration prerequisites are satisfied, an example focused storage
check uses the same environment and fresh run directory:

```powershell
& $pythonPath -B -m pytest -q -p no:cacheprovider tests/test_storage_source_registration.py --basetemp "$runRoot/pytest-storage"
```

## Git exclusions and developer handoff checklist

| Local path | Handling |
| --- | --- |
| `/dataset/` | Ignored originals and local source inventories; obtain separately |
| `/artifacts/*` | Ignored generated output; the tracked placeholder is now `backend/artifacts/.gitkeep`; use task audit-evidence for new phase work |
| `/uploads/`, `/data/private/` | Ignored private/session inputs; keep separate from institutional knowledge |
| `/plans/progress_plans/` | Ignored bulk scratch copies; curate current documents into tracked `plans/` |
| `.env`, `.env*.local` | Ignored local settings/secrets; `.env.example` is the tracked template |
| `node_modules/`, `.venv/`, build/test caches | Local dependencies/generated files; not the handoff's source of truth |
| `bintanong_workspace/audit-evidence/` | Local-only storage beside the main checkout; verify Git boundaries if relocating |
| `bintanong_workspace/MODELS/` | Model weights beside the main checkout; ignored weight extensions are an additional safeguard |

Ignore rules are path-specific. In particular, `/artifacts/*` does **not** cover
`backend/artifacts/`; only its `.gitkeep` placeholder is currently tracked.
Preserve local owner material and check the actual ignore status of any new output
location before writing source-derived data.
Git ignore status also does not imply exclusion from every Docker build context.

Before handing work to another developer:

- Provide the branch/commit plus [current progress](plans/plan_current_progress/current_progress.md)
  and the active checkpoint/handoff. Record dirty owner changes separately.
- List the exact required source/evidence/model packages, their actual paths,
  SHA-256/manifest references and any old-to-new path mapping. Share authorized
  data through the agreed channel, outside Git; exclude credentials/private uploads.
- Include reviewer events, source limitations, accepted benchmark references and
  compatible saved vectors. Do not describe candidate artifacts as approved.
- Verify that the recipient can resolve the required ignored inputs and existing
  environment before they rerun anything. Missing files and unresolved source
  decisions must remain explicit.
- Use explicit Git staging. Never force-add local datasets, model weights, private
  inputs, generated corpus JSON/Prolog/vectors or bulk scratch copies.

For ingestion-specific work, consult [ingestion plans](plans/ingestion/README.md)
only when relevant. Curriculum identities, versions, units and prerequisites
belong to structured knowledge and reviewed deterministic rules; document RAG
provides explanations and procedures. The
[phase index](plans/INDEX.md) remains the authority for what may begin next.
