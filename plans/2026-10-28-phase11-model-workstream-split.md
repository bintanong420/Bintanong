# Phase 11 workstream split: Codex and Claude

Owner decision, 28 October 2026: Codex takes the remaining Charter layout work and frontend–backend
integration; Claude takes Bintanong's answer quality from here on, starting with a gate that simple
student questions never fail. This plan extends the
[two-developer workflow](2026-10-26-phase11-two-developer-workflow.md); its rules on hosted data,
source decisions, shared interfaces and evidence folders still apply. The requirements baseline stays
the master plan (sections 3, 11, 13, 16, 23–26). No phase, scope, dependency or release change.

## Worktrees and branches

- Every new worktree lives under `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/` and
  starts from the current `feat/p11-backend-api` head, on its own branch:

| Lane | Worktree | Branch |
| --- | --- | --- |
| Codex A: Charter layouts | `.../worktrees/Bintanong/p11-charter-layouts` | `feat/p11-charter-layouts` |
| Codex B: frontend integration | `.../worktrees/Bintanong/p11-frontend-integration` | `feat/p11-frontend-integration` |
| Claude: answer quality | existing `.../worktrees/Bintanong/p11` | `feat/p11-backend-api` |

- Create with `git worktree add -b <branch> <path> feat/p11-backend-api` from any checkout.
  The existing `p11-policy-ingestion-review` worktree is untouched.
- Codex lanes bring in new `feat/p11-backend-api` commits by merging it into their branch (not
  rebasing published work) before asking for review.

## File ownership (to avoid collisions)

| Area | Owner |
| --- | --- |
| `backend/bintanong_generation/service_steps.py` and its tests (parsing/rendering Charter tables) | Codex A |
| Source-review records for those layouts; new parse/render evidence | Codex A (owner decides readings) |
| `frontend/`, `backend/bintanong_api/` and API tests | Codex B |
| Router, orchestration, generation guards/prompts, part answers, evaluation batteries | Claude |
| Central `plans/INDEX.md`, current progress, Phase 11 checkpoint | Claude |
| Each Codex lane's own task record `plans/2026-10-28-p11-<lane>-task.md` | That lane |
| Contracts, storage, package formats, dependency/lock files | Shared: propose in the task record first |

A change outside your rows, or to a shared row, is a collision: stop, write the proposed change in
your task record, and Claude reviews it with the owner before it is committed. A merge conflict in
any file is also reviewed rather than resolved by whichever side merges last.

## Shared machine limits (these decide the real speed)

- One Gemma model slot (`:18088`) and one RTX 4060: only one live model run at a time (batteries,
  roster reruns, HTTP smoke). Write `LIVE RUN: <lane> started <time>` in your task record before
  starting and clear it after; check the other records first.
- Full suite takes about 23 minutes; two at once already ran out of memory (28 Oct). Run one full
  suite at a time; use focused tests while another is running.
- Tests: shared venv `audit-evidence/p05-real-retrieval-readiness-20261012/venv` (system Python has no
  pytest), `-p no:cacheprovider`, basetemp under your lane's `audit-evidence` folder.
- No installs, downloads, dependency or lock changes without an owner instruction. Codex B: the
  frontend may need `npm ci`; ask the owner first.

## Merge flow

1. Lane finishes a small verified unit: RED/GREEN logs, focused tests, commit on its branch.
2. Lane writes the commit range, tests run and anything unresolved in its task record.
3. Claude reviews the diff against ownership and answer behaviour, merges into `feat/p11-backend-api`,
   runs the full suite and, if answers could change, the live question battery and regressions.
4. Owner reviews any collision or source reading. Nothing is pushed without the owner.

## Lane tasks

**Codex A — 21 Charter layouts.** Current state: 23/44 Charter services parse and render as printed
steps; 21 row/unnumbered/continuation layouts fall back to the model path
([results](2026-10-29-printed-service-steps-results.md)). Survey the 21 by layout family, add strict
grammar per family test-first with synthetic fixtures, refuse when unsure, never guess pairings from
list positions ([service-table policy](service-table-association-policy.md)). Show the owner ambiguous
readings in short batches with the printed text inline. Report parse/render counts on the real 559
data (both languages). Do not change host integration in `part_answers.py`/`generator.py`.

**Codex B — frontend integration.** Phase 11 plan tasks 1–6 and 9
([plan](phase-11-backend-api-plan.md)). First locate the co-worker's frontend: published `frontend`
branch snapshot `e172f53` was the last seen; confirm with the owner which frontend is current before
editing. Keep the API's student render profile free of check-scope lines, predicate names, hashes and
`ev-` ids. Live HTTP smoke last, under the shared live-run rule.

**Claude — answer quality.** (1) Shifting router clarify, option A (owner 28 Oct): one contrast example
in the router prompt; rerun battery and regressions. (2) A simple-question gate: about 30–40 basic
English/Taglish questions (one fee, one office, one requirement list, one prerequisite check, a
greeting, an excluded scope) that must all pass before other work counts. (3) Remaining wording and
abstain failures (discipline long flow). (4) Review and merge Codex units.

## Codex start prompt (paste into each Codex session)

> Work on Bintanong Phase 11, lane <A: Charter layouts | B: frontend integration>. Create your worktree
> with `git worktree add -b <branch> C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/<folder>
> feat/p11-backend-api`. Read `AGENTS.md`, `plans/INDEX.md`,
> `plans/2026-10-28-phase11-model-workstream-split.md` and the files it links for your lane. Follow
> its file ownership, live-run and full-suite rules. Create your task record, then work test-first in
> small commits. Stop and record a proposal if you need to change a file you do not own.
