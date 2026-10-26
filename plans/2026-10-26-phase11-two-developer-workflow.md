# Phase 11 two-developer workflow

The owner supplied this execution order on 26 October 2026: finish the planned
Handbook/Charter verification, commit its review records, identify a fixed verified
source/package snapshot, then split the frontend/runtime and ingestion workstreams.
This supersedes the previous next action of immediately fixing grading. It authorizes
the separate ingestion tooling workstream described here; the earlier read-only
assessment's “not authorized” statement describes its historical task only.

The existing master sections 3, 11, 13, 16 and 18.3 remain the requirements baseline.
No new phase, technology, dependency, institutional scope or release approval follows.
This document records execution of the supplied plan, not a replacement product design.

## Sequence and acceptance

1. **Delivered as bounded source verification:** review the pending undergraduate Handbook/Charter material using
   [the catalogue](2026-10-26-handbook-charter-expansion-catalogue.md). Record exact
   field readings, standing-delegation applications, exclusions and unresolved issues.
   [First review](2026-10-26-handbook-charter-expansion-review-01.md) covers H26–34
   and C6–8; its two source holds are owner-confirmed. [Review 02](2026-10-26-handbook-charter-expansion-review-02.md)
   completes Batch A locator inspection; [03](2026-10-26-handbook-charter-expansion-review-03.md)
   covers Batch B; reviews04–09 finish catalogue locator inspection. The
   [shared baseline record](2026-10-26-handbook-charter-shared-baseline.md) binds all89groups
   and preserved holds; no whole-document approval is claimed. Interpretations not
   established by the owner stay held; no source repairs or scope expansion.
2. **Delivered:** preserve the current
   corrected78 package and originals without modifying them. After the planned
   review is complete, commit its records and record the full Git SHA and verified
   package/source manifest as the shared baseline: **`4e99fb655022e694c73bbd98dd6daec9d7d88fb5`**.
   A documentation commit or hash check alone cannot satisfy the review gate;
   reviews01–09 and preserved holds define the actual bounded review.
3. **Workspace prepared:** primary remains on `feat/p11-backend-api`; other branch
   `feat/p11-policy-ingestion-review` was created from that exact commit in
   `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p11-policy-ingestion-review`.
   Its start receipt is commit `c76d988`, only the dedicated task record changed.
   Current task updates belong to that branch; do not mirror them into central snapshots.
4. **Frontend integration stopped by owner until resumed:** primary integrates the supplied frontend, runs student queries,
   fixes behavior through RED/GREEN regressions, and commits small verified units.
   Locate the supplied frontend before editing; the checked-in frontend package
   alone does not establish that it is the co-worker's completed design. Fresh GitHub
   inspection and `git fetch origin frontend` found published snapshot
   `e172f53c19bdd5d30ef5df2db4bf80ee47e27c3c`; it includes UI/auth/API changes and tests.
   Owner then said “we are implementing the chatbot frontend right now”. No merge,
   frontend edit or dependency installation has occurred; avoid overlapping that work.
5. **Not started:** the other developer implements the reusable commands and separate
   local researcher review UI under the [dedicated task record](phase-11-policy-ingestion-task.md).
6. **Not started:** integrate the completed tooling branch after code review,
   ingestion tests, chatbot regressions and the relevant full suite. Verify package
   compatibility and that active source decisions, hosted release and runtime pin
   retain their intended identities. Merging tooling does not publish generated data.

## Ownership

| Area | Owner |
| --- | --- |
| Current source review decisions and active knowledge | Primary developer |
| Student chatbot frontend and API integration | Primary developer |
| Router, orchestration, generation and runtime fixes | Primary developer |
| New ingestion workflow and local researcher review UI | Other developer |
| Isolated candidate chunks and ingestion-specific tests | Other developer |
| Hosted Supabase, active release and runtime pin | Primary developer |
| Existing contracts, storage interfaces, parsers and dependency files | Primary coordinates; one agreed implementer |
| Central Phase 11 progress/checkpoint | Primary developer |
| Dedicated ingestion task record and integration report | Other developer |

## Shared interfaces and integration

Before changing a chunk/source schema, topic/claim metadata, release format or storage
interface, record the affected interface, proposed behavior, compatibility and single
implementer in the task record. Agree on the change before implementation. The owner
of that change commits it once; bring the commit into the other branch and run both
ingestion and runtime compatibility tests. Prompt/layout changes normally need no
ingestion update unless they actually change the output contract.

Use separate output directories under workspace `audit-evidence`: the primary's
existing packages remain in their recorded locations; ingestion candidates go in
`p11-policy-ingestion-review-20261026/`. Do not overwrite either baseline or runtime
package. Coordinate embedding/GPU work with the primary before measuring latency.
The RTX 4060 8 GB and shared models stay unchanged; no downloads or installs are implied.

The other workstream must use explicitly disposable **local** databases. Do not copy
the primary `.env`, hosted credentials, runtime pin or hosted job configuration.
Separate worktrees do not isolate database targets. No hosted staging, review RPC,
migration, release creation/activation or other hosted write is permitted there.
Test target refusal before mutation; fail closed for absent or unverified targets.
The local target validation design belongs to that developer's implementation and
must be tested; this written restriction is not a claim of executable enforcement.
Read-only inspection of workspace `orca-worktree-setup.ps1` confirms the existing
post-create script copies ignored files including `.env` and runs `npm ci`.
The future ingestion worktree must avoid that setup path until a configuration
that excludes hosted credentials and unapproved installs has been established.
The shared setup script was not changed or executed.

## Current comparison snapshot

Raw snapshot: workspace `audit-evidence/p11-two-developer-baseline-20261026/`
`comparison-baseline-78/`. Manifest SHA-256:
`bfd2a4993ece9212e297a0ee47592fe8debcf6f9435a908ba2ec8103811cc011`.
It preserves seven sealed runtime data files, their seal, the evidence copy of the
pin, and both original PDFs: 11 byte-verified copies. The pin copy is evidence,
not ingestion configuration; it still refers to the primary runtime package.

| Identity | Value |
| --- | --- |
| Inspected Git baseline | `7590a71550cbfeebd8e0c7f9828b99c75cf34a9a` |
| Production code last verified by full suite | `706d3c6` |
| Research release, last known hosted state | `p11-research-corrected-20261026`, 78 chunks / 39 curricula |
| Runtime seal SHA-256 | `22ceaa15c300a5fc2d8778062a9f19ebb175bee34700f68267ec651a07b34c0a` |
| Primary pin SHA-256 | `5dd2d9c95c3cc96181bdd11d3a24481f1c18a4a5c71284a55316c7d60acecc74` |
| Handbook original SHA-256 | `4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8` |
| Charter original SHA-256 | `42a93994e1467df0f32c7038d1c21f638c23ac0f1dee984463acf56caf526529` |

This is a local byte-integrity comparison, with no fresh hosted inspection or writes.
The current two natural grading failures remain. The historical full-suite receipt
was reread: 6896 passed / 1595 subtests, 6 skipped / 2 xfailed, exit 0; it is not a
fresh test run. No new whole-document, currentness, public-release or phase-exit
claim is made. Generated candidates remain inactive.
