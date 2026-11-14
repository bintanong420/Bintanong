# Phase 12 session handoff — 30 October 2026

For the next session in the new Phase 12 worktree (branched from `dev`). Supersedes the 28 Oct session
handoff for current work. Phase 12 is active: [plan](phase-12-evaluation-writeup-plan.md),
[checkpoint](phase-12-checkpoint.md), [report](../docs/evaluation/phase12-evaluation-report.md).

## State at handoff

- `dev` = `a3ff208` (GitHub and local main checkout): p11 + origin/dev merged. Frontend kept p11's (it descends
  from the co-worker snapshot `e172f53`, which contains all of the old dev); backend kept p11's owner-approved
  behavior; `app.py` also accepts the co-worker composition's `supabase_probe`. Full suite on `a3ff208`:
  7314 pass / 1608 subtests, 6 skip / 2 xfail, 4 batches exit 0 (A/merge-p11-into-dev-20261030).
- Phase 12 report written; full suite on the report code (`0d6ebac`) 7271 / 1608 pass.
- Hosted Supabase (read 30 Oct, MCP): **active `p11-research-corrected-20261026` (78 chunks)**; drafts
  `p11-research-combined-20261027` (465) and `p11-research-expanded-20261025` (80). The 560 package is not hosted.
  The website serves the 560 package locally (local-documents pin, `d1a2d53`).

## Worktree setup (ignored files are not in Git)

1. Copy `.env` and `frontend/.env.local` from the main checkout (`bintanong_workspace/Bintanong`; both present,
   `.env` identical to p11's). Never stage them.
2. `npm ci` in `frontend/` (owner-approved 29 Oct for this lockfile; lockfile unchanged).
3. Start Docker Desktop if down; `docker start bintanong-p09-cuda-latency supabase_db_Bintanong`; check
   `http://127.0.0.1:18088/health`. Python: shared venv
   `audit-evidence/p05-real-retrieval-readiness-20261012/venv` (pytest, pypdfium2 for thesis pages).

## First task: hosted 560 activation (owner 30 Oct: "start there once I've created the worktree")

Owner directive 29 Oct (ledger): activate the gate-tested 560-chunk FAQ-split package as the hosted research
release through staging -> ReleaseManager activate RPC -> readback -> smoke, keeping corrected78 as rollback.
Research build only; no institutional approval or public deployment. Estimated 3-5 h.

- **Package:** `audit-evidence/p11-faq-split-20261028/runtime-package` (560 chunks / 560 vectors / 145 subjects /
  241 reviews; embedding set `f7a7f1b0…2218`; file hashes in `package-status.json`). Same chunk schema as the
  hosted 465 draft; 179 chunk IDs already hosted, **381 new**.
- **Why it is not a quick switch:** `bintanong_private.validate_release` (migration `20261022090000`) rejects a
  research release unless it has a bound selected review (`review_scope_id`), owner authorization ref
  (`research-owner-YYYYMMDD`), complete membership counts, anchored/reviewed chunks matching their document versions,
  exact spans, and unit-norm vectors per chunk. The 465 draft never got its selected-review binding.
- **Steps (each with readback; never blind-retry a write):**
  1. Snapshot hosted state (before.json); confirm active corrected78 and its 39 curriculum links.
  2. Disposable local-DB rehearsal of the full sequence (precedent `p11-hosted-expanded-staging-20261027/
     rehearse_package.py`; corrected78 path in `p11-chunk-corrections-20261026/`).
  3. Stage: new chunks + spans via `BatchKnowledgeLoader.load_chunks`, embedding manifest, vectors in batches of
     25 (a 465-vector RPC hit the statement timeout before), `ReleaseManager.create_release`, 39 curriculum links
     (precedent `stage_hosted.py`).
  4. Selected review: build and record the receipt with `backend/bintanong_storage/selected_release_review.py`
     (`record_selected_release_review`, `bind_selected_release_review`); then `designate_research_release`.
  5. `activate_knowledge_release` (ReleaseManager.activate_release); exact readback; anon visibility = 560;
     hosted smoke (precedent `p11-companion-context-20261026/hosted_smoke.py`, `release_switch.py`).
  6. Rollback if any check fails: `rollback_knowledge_release` to `p11-research-corrected-20261026`.
- **Ask the owner** before proceeding if a review/source decision is needed (e.g. a chunk whose document version
  is not `reviewed`/`partially_reviewed`); do not change source states to pass validation.
- Afterwards: update the report's section 8 (hosted activation), then write the Phase 12 handoff, supersede the
  checkpoint, `phase_state.py validate` / `can-advance`, INDEX and current progress.

## Do not repeat

Benchmark runs, absence-taglish diagnosis, paired statistics, report drafting, the dev merge, full suites above.
