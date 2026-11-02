# Knowledge-update fixes for the USG Constitution intake

2 November 2026. Branch `feat/p11-policy-ingestion-review` at `765e8ab5`. Written from the p12 session after a
read-only audit; no code in this worktree has changed yet.

## Goal

Make `knowledge_update` prepare, review and build a candidate package for the 2023 Tiniguiban USG Constitution
(34 physical pages, native text, SHA-256 `b40cca9e22d8f30dc9e48b684aa179a2f666ef1aef325c8132d170ec80b8d68d`).
The package stays local and inactive. Rehearsal and hosted staging happen from p12
(`p12-evaluation-harness`), which already has the migrations and hosted scripts. This workstream keeps its no-hosted-access rule.

No merge with p12 is needed for this work: none of the 22 modules the tool imports changed on p12 since the
`f0889c3` split (checked 2 Nov). Merge after the student sessions.

## Rules

- Test-driven: focused RED regression first, smallest fix, GREEN, then the knowledge-update suite.
- No dependency installs or downloads without an explicit owner decision (AGENTS.md).
- Synthetic fixtures in tracked tests; the real PDF and outputs stay in ignored `audit-evidence`.
- Content decisions (clause readings, scope) belong to the owner's review batches, not to these fixes.

## Tasks, in order

### 1. Native Docling conversion on the USG PDF (blocker, check first)

Recorded failure (27 Oct, `2026-10-27-ai-ingestion-results.md`): Transformers 5.10.2 needs
`huggingface-hub>=1.5.0,<2.0`; 2.2.0 was installed; Docling 2.129.0, CPU-only PyTorch.
The p12 venv built from the frozen lock (`audit-evidence/p12-env-20261031/venv`) has `docling` importable, and the
lock pins `docling==2.133.0`. The 1 Nov audit judged this blocker probably stale.

- Run `prepare` for the USG PDF alone with that venv and a fresh output folder.
- If it converts: record the environment used; no code change.
- If it fails: record the exact error, stop, and ask the owner before any dependency change.
- Done when: a packet exists with USG items whose spans point to physical pages 1-34, and `load_packet` passes.

### 2. Corrected values on multi-span fields are lost

`review.py` `export()` (lines 269-273) writes a corrected value into the span text only when the field has exactly
one span. With two or more spans (a clause crossing a page break), the export keeps the old span texts while the
reading carries the corrected value, so the build's span/field agreement check fails. The audit counted 3 of 298
existing policy fields affected; USG clauses that run across pages will hit it.

- RED: synthetic two-span field, `corrected` decision, export then build; expect the build to fail today.
- Fix: decide how a corrected value maps onto several spans. Do not invent a split of the human's text across
  page regions. Recommended: keep original spans as provenance and record the correction once, as a field-level
  human repair over all its spans, if the builder's span checks can accept that; otherwise refuse the
  correction in the reviewer with a clear message to correct per span. Pick whichever the existing builder
  contract supports and state it in the result record.
- Done when: the RED test passes, single-span behavior is unchanged, and corrected text never silently drops.

### 3. Baseline format does not match the 560 release package

`build.py` `load_package` expects a knowledge-update package (`package.json`, `chunks.jsonl`, `embeddings.jsonl`,
`recipe.json`, `source_register.json`, `claims.json`, `topics.json`). The active research release came from
`audit-evidence/p11-faq-split-20261028/runtime-package/`, which uses `draft-chunks.json`,
`draft-embedding-manifest.json`, `draft-embedding-records.jsonl`, `draft-source-versions.json`,
`draft-subject-catalogue.json` and `package-status.json`. The build also checks the package against its own
review-derivation recipe, which the 560 package does not have. This is a missing adapter, not a small bug.

Options, recommended first:
- **A. Build USG without a baseline.** Produce a USG-only package here. In p12, the staging step combines the 560
  chunks and vectors with the USG ones into the new draft release, as the 560 staging did for its own additions.
  No adapter is needed.
- **B. Write a 560-to-package importer.** Gives retained/replaced/removed membership and vector reuse against
  the live release. Larger, and the derivation check may not be satisfiable without the original review export.
  Revisit when a second edition of a source arrives (clause diff and versioning work).

Owner decides A or B before work starts on this task.

### 4. Lower priority (not needed for USG)

- `load_packet` runs on every `state()`/`save()` call and re-hashes every artifact (10.15 s on the prospectus
  packet). Cache by artifact digests per session; keep the integrity check on save. Probably tolerable on 34 pages.
- LlamaParse resume: when the upload itself fails, no job or pending pages are stored, so the next run uploads
  again without `--retry-failed`, contrary to the guide. Either record the failed attempt so a plain rerun skips it,
  or correct the guide. No LlamaParse key exists, so this does not affect USG.

## After the fixes

1. `prepare` the USG packet (Task 1 output) and hand the p12 session the packet path and commit.
2. Owner reviews in short batches; batch 1 (Preamble, Articles I-II, physical 1-2) was already shown in p12.
   Standing scope: keep the Tiniguiban limit, exclude the Article XV ASG clause on physical 23 (it names
   laboratory school, Law, Graduate School and Medicine), G03 confirmed, G01/G02 still open.
3. Build the package (option A or B), then p12 rehearses locally and stages inactive on hosted.

## Verification to record

Commands, exit codes and test counts for each task, the venv used for Docling, and the packet/package digests.
Update this branch's current progress and the ingestion checkpoint after each task.
