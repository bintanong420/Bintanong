# Phase 11 hosted-chunk human review

Status: plan saved; hosted snapshot and numbered queue not yet created in this session.
Owner confirmed saving this plan on 25 October 2026 for recovery across sessions.
This is a review operation within Phase 11, not a new implementation phase.
Recovery baseline: `82ae498`; previous checkpoint/recovery snapshots remain available there.

## Goal and expected membership

Review all 80 unique hosted chunks in small related batches using readable exact text.
The incoming handoff reports fresh hosted reads of project `jyrudbiuajahsucsorco`:

- Active: `p09-research-selected-20261022`, 19 chunks.
- Draft/inactive: `p11-research-expanded-20261025`, 80 chunks, including those same 19.
- Draft includes 38 additional disciplinary records reviewed previously, alongside the older
  exam-cheating record. Preserve and identify that older record; review shared IDs only once.

These counts are incoming evidence, not a fresh read by this session. Reconcile unexpected
membership changes before showing review cards. No owner chunk outcomes have been recorded here.

## Execution and snapshot

1. Resume via INDEX, current progress, Phase 11 checkpoint and session recovery; inspect Git.
   Refresh thesis physical pages 17–18 and routing PNG; consult relevant Context/master evidence.
   Apply undergraduate scope, source-gap and service-table-association policies and settled
   decisions in `owner-decisions-ledger.md` and the existing source-review record below.
2. Use read-only Supabase queries to recheck both releases and snapshot all 80 unique IDs,
   exact stored text, source text, filename/version/hash, physical pages/source spans,
   limitations, companion relationships and release membership. Hosted records are the input;
   do not substitute a local package for the hosted snapshot.
3. Save raw snapshots, query text/results and validation evidence ignored under
   `C:/Coding-projects/bintanong_workspace/audit-evidence/p11-hosted-80-review-20261025/`.
   Verify the raw evidence is ignored/untracked before staging any documentation.
4. Freeze an explicit number-to-chunk-ID queue in this ledger, linked to the raw snapshot and
   its digest. Assign numbers once; do not renumber after corrections or across sessions.
   Distinguish active/shared, draft-only and preserved older records. Log any later drift.
5. Verify 80 distinct IDs, all active 19 included, expected group counts, file/page mappings
   and source hashes. Compare provenance to existing sealed/source evidence as needed.
   If hosted access fails, record the exact blocker; never label cached data a fresh read.

## Frozen review order and batch size

| Queue range reserved | Source group | Count | Order |
| --- | --- | --- | --- |
| 1–66 | Handbook | 66 | Physical page/topic; start with grading, physical p.46 |
| 67–74 | Citizens’ Charter | 8 | Physical pp.102–103; linked client/agency fields together |
| 75–77 | Special-class-fee image | 3 | Identify original image and fields |
| 78–80 | Vehicle-pass images | 3 | Identify original images and linked clauses |

Ranges reserve the requested order; individual IDs remain unassigned until hosted verification.
Usually display 2–3 short related chunks per reply. Keep linked continuation groups together,
including four-chunk groups. Judge completeness only after the whole linked group is visible.
Wait for the owner's decisions before advancing. Silence never approves a chunk.
Keep raw hosted JSON available on request; do not flood the conversation with it.

## Required review card

For each stable number show:

- Topic, exact chunk ID, active/shared or draft-only status, and any preserved-older status.
- Exact filename and physical PDF page(s). Include printed page numbers only when verified;
  identify images as images rather than assigning PDF pages.
- Exact original wording/field values, without paraphrasing; preserve meaningful conditions,
  punctuation, blank fields and limitations. Explicitly distinguish blank from absent fields.
- All added retrieval context and known limitations, separated from original wording.
- Companion IDs/numbers, required relationships and whether this is only a fragment.

Use readable layout without dropping meaningful stored content. An accurate fragment is not
automatically a self-contained answer source. Show exact original regions if a new source
ambiguity needs judgment; distinguish source defects from extraction or metadata problems.

## Ledger and correction register

After freezing the queue, maintain one row per unique ID with these fields:
`number | chunk ID | topic/pages | release status | source fidelity | missing context/fragment |
owner decision (exact words) | outcome | proposed correction | unresolved issues | batch/evidence`.
Allowed reviewed outcomes: **approved**, **correction-needed**, **held**. Pending is unreviewed.
Keep exact owner corrections and questions; do not replace them with inferred policy meanings.
Link long exact decision transcripts or evidence when needed while retaining resumable state here.

Current counts: approved **0**, correction-needed **0**, held **0**, pending **80 expected**.
Queue: not initialized. No review cards have been shown in this session.
Correction register: empty; no new findings asserted.

## Reuse and boundaries

Reuse the already settled source approvals, including last night's 38 disciplinary records.
Authority: [partial-topic source review](2026-10-24-partial-topics-source-review.md), frozen SHA-256
`a619ba37500831b6db1a58306aa4f2b9b11c4909170b0b2d643335f39acf39b9`;
[owner ledger](owner-decisions-ledger.md) and [resume evidence](2026-10-25-phase11-resume-verification.md).
This audit checks hosted fidelity/context; it does not reopen settled policy readings. Despite the
older standing delegation, this operation explicitly waits for owner decisions on displayed batches.

Preserve undergraduate-only/advisory scope, unknown-versus-unmet, privacy and source-gap rules.
Keep F04 held, missing item 22, weapon exception/fraud precedence holds, Charter cutoff and
25-versus-20-minute discrepancy. Do not invent missing text, fees, conditions or process endpoints.
Keep originals and historical evidence unchanged. Source approval is not institutional authority,
currentness, activation or public deployment permission.

Do not update published chunks, activate the draft, rechunk, re-embed, change prompts, run models,
fix the grading router or advance Phase 11 during this audit. Corrections become a separate,
reviewable follow-up through the existing append-only release process. No downloads/dependency changes.

## Validation and completion

- Validate cards against every meaningful hosted field, including blanks/conditions/limits.
- Record 80 unique outcomes; report approved, correction-needed and held counts separately.
- Produce grouped findings and a proposed correction list; audit completion is not correction delivery.
- Recheck hosted hashes/membership against the opening snapshot to confirm unchanged audited content;
  reconcile any external drift without overwriting the baseline or attributing it to this audit.
- Update this ledger, current progress and checkpoint after material decisions, before waiting or
  changing sessions. Keep one next-batch cursor; update recovery only when its recovery state changes.
- This review-only operation needs snapshot/card/ledger checks, not a full software-suite rerun.

## Single next-batch cursor / recovery

**Preflight pending → freeze the hosted 80-ID queue → show the first 2–3 related Handbook grading
chunks from physical p.46 → wait for the owner's decisions.** No chunk is approved by this plan.
The grading-router capture previously next in recovery is deferred, not completed or discarded.
No fresh hosted read or database mutation occurred during this plan-save turn.
