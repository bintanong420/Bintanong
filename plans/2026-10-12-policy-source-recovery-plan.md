# Policy source recovery and dataset organization plan

> **For agentic workers:** Use the Bintanong phase handoff workflow and the
> executing-plans skill for implementation. Use TDD for product changes. This
> bounded organization task uses byte inventories, path checks and Git exclusion
> checks; it does not add product code or tests that assert documentation text.

**Goal:** Preserve the prospectus tree, organize current policy originals by
printed edition year, and recover the missing real-policy source work without
restarting delivered software phases.

**Architecture:** Filesystem categories organize acquisition candidates. Existing
byte-derived source contracts and approved knowledge-release metadata continue
to determine runtime versions, scope, effectivity and publication. Folder names
do not establish approval, precedence or automatic supersession.

**Spec:** Owner request of 12 October 2026; `plans/phase-05-corpus-scope-clarification.md`;
master sections 6, 7 and 10; thesis and routing diagram under `Context/`.

## Owner instructions and routine choices

- Keep `PalSU Undergraduate Prospectus Website Dump/` and its contents unchanged.
- Work in the existing `backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/`.
- Provide 2024, 2025, 2026 and 2027 folders for Charter, handbook and memoranda.
- Preserve the university Charter separately from future college-specific ones.
- College Charter photos and organization policies are deferred; they may arrive
  later. Do not wait for all of them to process supplied university documents.
- Ignore root `/dataset/` and the actual nested dataset directory in Git.
- Extend the existing handoff-reading loop with targeted `Context/` inspection.
- Keep repository plans/checkpoints and an explicit next-CLI handoff up to date.

Routine choices: `CitizenCharter`, `StudentHandbook` and `Memoranda` category names;
`UnknownYear` for unresolved editions; `University` scope folder for the supplied
Charter; central `Deferred/CollegeCitizenCharter` and
`Deferred/OrganizationPolicies` holding areas. Create actual college/organization
subfolders only when inputs arrive. Preserve original filenames, use additional
edition subfolders for same-year revisions if needed, and refuse overwrites.
The handbook cover visibly says 2021, so add that real edition year rather than
placing the file under 2024 or its printed 2020 approval date.

## Task 1 — Recover instructions and protect source files

- [x] Inspect Git, ledger, handoff routing, master and relevant ingestion history.
- [x] Inspect new PDF covers; capture an external 42-file byte inventory.
- [x] Add dataset ignore rules and verify existing/new paths are excluded.
- [x] Add targeted Context reading to AGENTS and both existing handoff skills.
- [x] Verify the updated resume loop through a fresh reader check and commit the
  cohesive instructions/protection increment.

## Task 2 — Organize originals and mint pending identities

- [x] Create the category/year/deferred directories and ignored dataset README.
- [x] Verify resolved source and destination containment and destination absence;
  move only the two loose policy PDFs, preserving their bytes and filenames.
- [x] Rehash the entire prospectus tree and confirm unchanged relative paths.
- [x] Use existing register helpers to mint two pending source records; record
  observed cover metadata separately, keeping scope and authority pending.
- [x] Write external before/after inventories, move journal and a verification
  summary; confirm no original PDF or image is tracked/staged.
- [x] Update dataset guide, checkpoint, current progress and the next-CLI handoff;
  run ledger/doc checks and commit the verified organization documentation.

## Task 3 — Supplemental Phase 1–2 real-policy work, next continuation

University Charter candidate now verified:427chunks/3retained table rejections.
Handbook processing and source/content approval remain pending. Follow
[execution evidence](phase-05-policy-source-recovery.md) and
[latest continuation](2026-10-12-phase05-policy-recovery-handoff.md); saved raw
conversion can be reused for diagnosis. Task3remains partial.

- [ ] Verify acquisition origin/URL, issuer, printed edition, applicability and
  supersession evidence for each actual source. Use existing source contracts;
  never derive authority from its folder or filename.
- [ ] Inspect mixed text/image content and student-relevant sections. The Charter
  has 117 pages and the handbook 394; cover text alone is not an extraction gate.
- [ ] Run the existing policy/Charter candidate ingestion path in the approved
  offline environment, first a bounded source-backed smoke case, then whole
  documents in recoverable increments. Preserve original physical page numbers,
  reject incomplete spans and retain candidate quarantine.
- [ ] Independently validate sampled policy/procedure spans and meaningful
  conditions, exceptions, numbers and tables; measure OCR only where needed.
- [ ] Prepare reviewed policy development cases, execute matching embeddings and
  retrieval, and calibrate development cases only. Keep final cases held out.
- [ ] Recheck the Phase 05 exit gate and write an earned final handoff only when
  approved source-backed retrieval evidence actually exists.

This plan does not revoke historical Phase 1–4 software handoffs, activate a
corpus, complete Phase 05, start Phase 06 or authorize new installations. Existing
isolated dependencies and five Docling assets remain available; reuse them.

## Test-count concern

Read-only collection before the new documentation reports 4,919 cases from 1,816 definitions in 124 modules.
Examples include 331 documentation character checks, 222 source-register parity
variants and 180 publication-interruption variants. This is not a finding that
the suite is necessary or redundant; a later targeted coverage/duplication audit
can decide that. No tests are removed or rewritten as part of organization.
