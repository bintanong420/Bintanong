# Phase 06 machine scaffold and next-chat handoff

Prepared 17 October 2026 for **Hawksprey420**, using this machine's files and tools.
This is workspace preparation, not a Phase 06 completion or runtime authorization.

## Open this workspace

```powershell
Set-Location C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p06
git status --short
git branch --show-current
py -3.13 -B .agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .
```

Branch: `chore/p06-hawksprey420-scaffold`, based on `85366d4` of
`feat/p06-prolog-janus-rules`. The original branch remains checked out at
`C:/Users/Hawksprey/source/repos/Bintanong`; a second branch avoids switching or
resetting that checkout. Keep Phase 06 work here; do not merge, push or prune other
worktrees as part of resuming. Git identity is already Hawksprey420; no identity
configuration or previous authorship was changed. GitHub MCP confirmed baseline
`85366d40a48f3d4ddd6d1e9f894676ad5f001184` exists remotely; no remote mutation.

Read AGENTS.md, both Bintanong handoff skills, INDEX, current progress, Phase 06
plan/checkpoint and this handoff. Product `6fedc45` is already delivered.
Reviews 01–03 and the partial-export design are approved; do not ask again.

## Available ignored files

- `dataset/`: byte-preserving copy of this checkout's legacy backend dataset;
  **55 files: 50 PDFs, four PPTX files and one CSV**. Prospectus subtree: 39 PDFs
  plus its CSV. Both BSCS originals match the hashes in translation review 01.
  This is an inventory, not a reviewed/approved corpus or the other machine's
  62-file inventory. Original source paths and filenames remain intact.
- `artifacts/`: all 32 available files preserved, including tracked `.gitkeep`;
  historical outputs retain their original content and are not current approvals.
- `plans/progress_plans/`: present but empty in the source and destination.
- `.env`: copied from tracked `.env.example`, **example values only**. No local
  secret-bearing environment file was available to transfer. Service hostnames
  are Docker-network defaults, not a verified running local configuration.
- `backend/.venv/`: freshly created with `py -3.13 -m venv --system-site-packages`;
  no dependency installation. It inherits this machine's global packages. The
  old checkout's 1.2 GB environment was not copied or modified; venvs are not
  portable dependency bundles. This new environment is not lockfile-reproducible.
- Fourteen `.superpowers` files are preserved in raw evidence under
  `source-superpowers/`, not activated as a new chat's execution state. Bytecode,
  pytest caches and generated caches were not transferred.

Raw evidence: `C:/Coding-projects/bintanong_workspace/audit-evidence/p06-machine-scaffold-20261017/`.
`copied-files.json` binds all 101 copied files to source/destination SHA-256;
`machine.json` records package versions, model hashes and missing historical paths.
Dataset, local configuration, environment and generated outputs are ignored.

## Models and tools on this machine

`C:/Coding-projects/MODELS` is now an external directory junction to existing
`C:/Coding-projects/bintanong_workspace/MODELS`. No weights moved or duplicated.
Both SEA-LION and GEMMA weight hashes match `.env.example`. Keep models external.
The original checkout's untracked `SEA-LION-E5-Embedding-600M/` remains untouched.

| Component | Fresh observation | Consequence |
| --- | --- | --- |
| Python | bare `python`: 3.11.15; launcher default: 3.14; `py -3.13`: 3.13.12 | Always select 3.13 explicitly |
| Local venv | 3.13.12, Pydantic 2.13.4, pytest 9.0.3 | Works for tested scope; pins are 2.13.5/9.1.1 |
| Old checkout venv | 3.13.5, Pydantic 2.13.5, pytest 9.1.1 | Available fallback only; previous readiness venv is absent |
| SWI-Prolog / Janus | 10.1.6 / system distribution 1.5.2 | Janus package presence only; import/bridge not validated |
| Node / npm | 22.22.3 / 10.9.8 | Frontend pins Node 24.21.0; no node_modules available |
| Git / uv | 2.55.0.windows.5 / 0.11.24 | Available; no lockfile change or sync performed |
| Docker | CLI 29.8.2; Linux daemon pipe absent | Runtime/container validation unavailable |
| Supabase CLI | 2.117.0 | Version observed only; no DB calls |
| gh / Poetry / Poppler CLI | absent | GitHub MCP available; PyMuPDF available for source inspection |

No tools were installed/upgraded. Do not mistake locally installed older packages
for the previous developer's pinned readiness environment. Janus execution, API,
Docker, database, frontend build and model inference were not exercised.

## Missing evidence and recovery

The prior `audit-evidence/p06-review-bundle-20261017/` (921-file sealed delivery),
`p06-bscs-authoring-selections-20261017/`, `p06-authoring-20261017/`, earlier foundation/
extension receipts and Phase 05 readiness/closure evidence are absent locally.
The dataset's later memo/enrollment additions are not present in this copied tree.
Tracked reports/approvals remain authoritative history; their external artifact
links do not become valid merely because this worktree now exists.

**Next action:** recover the original ignored Phase 06 evidence directories from
the previous developer's machine/storage into the shared audit-evidence parent,
then verify recorded manifests/hashes before generated-output human inspection.
Follow dependency links in the generated-delivery report for original authoring
inputs/receipts. Do not recreate receipts, claim a replay, silently reconstruct
missing authoring records or reopen settled reviews. Independent synthetic work
can proceed within its own authorized scope while evidence transfer is pending.

## Verification and boundaries

Fresh related baseline: **330 passed in 53.63s**, system Python 3.13.12, exit 0.
Exact command, from the worktree, with TEMP/TMP under the raw root:

```powershell
py -3.13 -B -m pytest -q -p no:cacheprovider tests/test_symbolic_review_bundle.py tests/test_symbolic_compiler.py tests/test_symbolic_authoring.py tests/test_contracts_symbolic.py tests/test_rule_candidates.py tests/test_prospectus_rule_handoff.py --basetemp=C:/Coding-projects/bintanong_workspace/audit-evidence/p06-machine-scaffold-20261017/symbolic-temp
```

Documentation/phase checks and final asset checks are recorded in current progress
and the checkpoint; raw logs stay ignored. No product code, dependency manifests,
lockfiles, source approvals, candidate registry or institutional rules changed.
Context rechecked: master 3/11/13, actual thesis physical 17–18 and 39–44, routing
PNG. Undergraduate/read-only/private separation stands. Thesis closed-world denial
on missing facts remains superseded by master 11.4's explicit unknown semantics.
