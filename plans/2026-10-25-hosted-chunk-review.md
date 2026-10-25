# Phase 11 hosted-chunk human review

Status: hosted snapshot verified; stable queue frozen; chunks1–18 approved; batch7 (chunks19–22) awaiting owner decisions.
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

Fresh read at 25 October 2026 22:52 Manila confirmed these counts and statuses. All 19 active IDs
are included in the draft80; no membership discrepancy. Owner approved batches1–6/chunks1–18 in separate replies, each "i approve"; other outcomes pending.

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

Ranges and individual IDs are frozen below; ordering is source group, first physical page, then
natural reading-ID order. Retain numbers even when related companions are reviewed together.
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

Current counts: approved **18**, correction-needed **0**, held **0**, pending **62**.
Queue: frozen below. Batch1/chunks1–3 approved: exact owner reply "i approve".
Batch2/chunks4–6 approved: exact owner reply "i approve".
Batch3/chunks7–9 approved: exact owner reply "i approve".
Batch4/chunks10–12 approved: exact owner reply "i approve".
Batch5/chunks13–15 approved: exact owner reply "i approve".
Batch6/chunks16–18 approved: exact owner reply "i approve".
Batch7/chunks19–22 prepared/shown as one linked group; decisions pending.
Correction register: no owner-directed corrections yet. Agent verified chunks1–18 against rendered physical46: exact row values;
rows omit the original table heading, carry no source_limits and declare no required neighbors.
Chunks10–18 preserve printed blank percentages as empty values/source_blank=true/no span indexes;
blank percentages do not supply a numerical equivalent. Inc. and IP rows only define labels.
They are individual row fragments sufficient for their grade mappings, not a complete grading policy.
The fragment/heading observation remains; approval confirms fidelity, not a database edit or activation.

### Batch7 context findings (owner decision pending)

Chunks19–22 faithfully quote selected timing spans on rendered physical47; all active/shared.
Added group metadata orders parts0–3;19 requires20–22, and20–22 each require19 (transitive closure all4).
Each carries the same unresolved conflicting_deadlines warning for applicable completion deadline/
deadline precedence. Keep that warning; source conflict is not resolved by approving a quotation.
All four are selected fragments, not the complete removal/completion procedure. No source blanks.
Original context omitted by this selection (do not silently insert into hosted text):
- Chunk19 quotes only the timing phrase. Section3.2 actually identifies a grade of “4” or “Incomplete”
  and cites “(Resolution 279, Series of 2018)”; subject and resolution reference are absent in the group.
- Chunk20 selects only section3.3's final paragraph; its preceding removal-exam details are absent.
- Chunk21 selects only section3.7's first sentence; the next original sentence is absent:
  “A grade of “4” received after removing a grade of “INC”, however, must be removed within the
  remaining portion of the prescribed period for the original grade of “INC”.”
- Chunk22 contains the complete final paragraph as selected; it retains conflicting one-term wording.
Possible separate append-only follow-up: add needed scope/reference/remaining-period context while
retaining the unresolved conflict. No correction instruction or outcome inferred before owner response.
Exact original page rendered at raw-evidence root/handbook-p47.png; no printed page verified.

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

**Await owner decisions for batch7, chunks19–22 (Handbook physical47). Do not advance on silence.**
After recording those exact decisions, prepare the next complete table group, chunks23–27, unless a correction requires clarification.
The grading-router capture remains deferred. No DB mutations, prompts/model runs or source edits.

## Frozen snapshot and verification

- Project URL verified: `https://jyrudbiuajahsucsorco.supabase.co` (project-scoped MCP).
- Raw evidence root: `C:/Coding-projects/bintanong_workspace/audit-evidence/p11-hosted-80-review-20261025/`.
- `opening-snapshot.json`: exact chunks/text/source_text/type_fields, documents/versions, spans,
  release statuses and membership; `opening-query.sql` and `opening-tool-response.json` retained.
- Snapshot SHA-256: `b15cec8f7cb83c4898453e134b5927a0fc20ff3e3cb47931a542feda9f8f2749`.
- `frozen-queue.json` SHA-256: `d689460f366d5be3d89212ff8604b9b3707392659ad04016fc37d9c32c5a5807`.
- `validation.json`:80 unique/80 draft/19 active included; groups66/8/3/3; all80 content hashes
  recomputed by the existing immutable hash function match. All five original byte hashes match
  hosted versions; all spans match their chunk's hash/version and point to positive physical pages.
  Required neighbors are present. Detailed field/association/page fidelity remains the human audit.
- First grading cards: `handbook-p46.png` inspected; no reliable printed page label visible.
  Source heading is exactly "2.2 UNDERGRADUATE LEVEL/SCHOOL OF LAW"; use undergraduates only.
- Context refreshed: thesis physical17–18 and runtime routing PNG; no scope/routing discrepancy.
- Hosted records still say partially_reviewed/observed; this ledger does not change their states.
- No database write tools used. Final membership/hash drift check remains due at audit completion.

## Frozen numbered outcome queue

Full source provenance and companions are in the snapshot; raw hosted JSON is available on request.
Each pending row has no owner decision, proposed correction or resolved question until recorded.
`Older` denotes the preserved active exam-cheating record; shared IDs occur once.

| No. | Exact chunk ID | Reading/topic | Physical page(s) | Release | Fidelity | Missing context | Exact owner decision | Outcome | Proposed correction / unresolved issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `13488cc8c115d77a41753bbefd98e1f14524f543b6948cb90f2a762f7d267f2d` | handbook-grading-1 | 46 | active/shared | Agent: row values match p46 | Table-row fragment; heading absent; no declared companions | "i approve" (batch1, 25 Oct 2026) | approved | None; no unresolved row-value issue |
| 2 | `4e3e4d50d8f09f073c66fa1f9e62a068300064795e4ca48beaf9fdcb1d009f69` | handbook-grading-2 | 46 | draft-only | Agent: row values match p46 | Table-row fragment; heading absent; no declared companions | "i approve" (batch1, 25 Oct 2026) | approved | None; no unresolved row-value issue |
| 3 | `51fd3434d782f99a36e2d051dc686666555fcba5d0bf3f9d8be8f8c4fed799c5` | handbook-grading-3 | 46 | draft-only | Agent: row values match p46 | Table-row fragment; heading absent; no declared companions | "i approve" (batch1, 25 Oct 2026) | approved | None; no unresolved row-value issue |
| 4 | `2362cdc8b2b2bd57c37c14416487a24048a62197429ec8e0d77893eb275f7326` | handbook-grading-4 | 46 | draft-only | Agent: row values match p46 | Table-row fragment; heading absent; no declared companions | "i approve" (batch2, 25 Oct 2026) | approved | None; no unresolved row-value issue |
| 5 | `5f2d95e5f09b2c25e5d33760610bbd8990084b148a2b2ac05dbbe9d44390ca3a` | handbook-grading-5 | 46 | draft-only | Agent: row values match p46 | Table-row fragment; heading absent; no declared companions | "i approve" (batch2, 25 Oct 2026) | approved | None; no unresolved row-value issue |
| 6 | `99ba38b440a29cbaa258aa42d656aa1fe7cdcb65cc606a25ed7a8e45cf35d65b` | handbook-grading-6 | 46 | draft-only | Agent: row values match p46 | Table-row fragment; heading absent; no declared companions | "i approve" (batch2, 25 Oct 2026) | approved | None; no unresolved row-value issue |
| 7 | `6e021489ad45845b81289f848185a8ea2ed9332459e56c90984c66cb0537f8b3` | handbook-grading-7 | 46 | draft-only | Agent: row values match p46 | Table-row fragment; heading absent; no declared companions | "i approve" (batch3, 25 Oct 2026) | approved | None; no unresolved row-value issue |
| 8 | `c1e71d273ba876f3e1f4d690db68af8da4d19d56c4f38d8b8ed9357abd091bd7` | handbook-grading-8 | 46 | draft-only | Agent: row values match p46 | Table-row fragment; heading absent; no declared companions | "i approve" (batch3, 25 Oct 2026) | approved | None; no unresolved row-value issue |
| 9 | `1c65b0fb43daf204f4ae5a3c15c7654a2695fdf09f9cbaf99c433f5a4d697278` | handbook-grading-9 | 46 | draft-only | Agent: row values match p46 | Table-row fragment; heading absent; no declared companions | "i approve" (batch3, 25 Oct 2026) | approved | None; no unresolved row-value issue |
| 10 | `bb704bc3bdd62af0207d5889e00640c48faba10031a154e43c6b8f4b0c7d11ef` | handbook-grading-10 | 46 | draft-only | Agent: values/blank match p46 | Table-row fragment; blank percent; heading absent; no declared companions | "i approve" (batch4, 25 Oct 2026) | approved | None; printed blank retained |
| 11 | `3ad00c67166519bfeb566c1d708f79b8ef92756365b8b36f5cd5cc4717cceb45` | handbook-grading-11 | 46 | draft-only | Agent: values/blank match p46 | Table-row fragment; blank percent; heading absent; no declared companions | "i approve" (batch4, 25 Oct 2026) | approved | None; printed blank retained |
| 12 | `dee78e9625915026bf7661adf8cd5ba889cecd4ed4abc1efcc8c3082e3b10d9d` | handbook-grading-12 | 46 | draft-only | Agent: values/blank match p46 | Table-row fragment; blank percent; heading absent; no declared companions | "i approve" (batch4, 25 Oct 2026) | approved | None; printed blank retained |
| 13 | `13d8167617121133130f93f1e209a03e8e0fe1b163020e045b1ca8fcfa216ab3` | handbook-grading-13 | 46 | draft-only | Agent: values/blank match p46 | Table-row fragment; blank percent; heading absent; no declared companions | "i approve" (batch5, 25 Oct 2026) | approved | None; printed blank retained |
| 14 | `98d87011903004a99b05ce44b1609622b8ef018373689d586d8ef17f83146d13` | handbook-grading-14 | 46 | draft-only | Agent: values/blank match p46 | Table-row fragment; blank percent; heading absent; no declared companions | "i approve" (batch5, 25 Oct 2026) | approved | None; printed blank retained |
| 15 | `246e133f06ecf8a938939041692deab53a167ae1b2d4bfd804ae1f5badc49d28` | handbook-grading-15 | 46 | draft-only | Agent: values/blank match p46 | Table-row fragment; blank percent; heading absent; no declared companions | "i approve" (batch5, 25 Oct 2026) | approved | None; printed blank retained |
| 16 | `6d53029b1811ae651ca7299ba1fd198211545327ba2366ee6a3722594778c8c3` | handbook-grading-16 | 46 | draft-only | Agent: values/blank match p46 | Table-row fragment; blank percent; heading absent; no declared companions | "i approve" (batch6, 25 Oct 2026) | approved | None; printed blank retained |
| 17 | `083b8a6557647c5e35873f9da7c85c504ce8674235298269b576c2dc16a71d48` | handbook-grading-17 | 46 | draft-only | Agent: values/blank match p46 | Table-row fragment; blank percent; heading absent; no declared companions | "i approve" (batch6, 25 Oct 2026) | approved | None; printed blank retained |
| 18 | `0521286530fde3366c9480fffb7e302cedd4a8e212af626501e73a6e5682ecbf` | handbook-grading-18 | 46 | draft-only | Agent: values/blank match p46 | Table-row fragment; blank percent; heading absent; no declared companions | "i approve" (batch6, 25 Oct 2026) | approved | None; printed blank retained |
| 19 | `00d246b8d5d184d36b4f458c78be4a6ae5993db81dc625d43a7daf384fa5b0f2` | handbook-completion-timing::part:0 | 47 | active/shared | Agent: selected quote matches p47 | Phrase only; subject/resolution absent; requires20–22 | — | pending | Conflict unresolved; context follow-up proposed, owner decision pending |
| 20 | `cf9b6c64eda1205f7e73033d0c0a85e46142dc2079ade35720fba5e22f1ada9a` | handbook-completion-timing::part:1 | 47 | active/shared | Agent: selected quote matches p47 | Selected final paragraph3.3; requires19 | — | pending | Conflict unresolved; context follow-up proposed, owner decision pending |
| 21 | `fe0c5a6848f942d9ee8bc948851039c7b35aa855d7cdf840bdd92c27b4617fd9` | handbook-completion-timing::part:2 | 47 | active/shared | Agent: selected quote matches p47 | First sentence only; remaining-period condition absent; requires19 | — | pending | Conflict unresolved; context follow-up proposed, owner decision pending |
| 22 | `5b85dd8084f1488750f63e98e41cac74ca1ab36bbf5492e3dcf2f0eda19ba618` | handbook-completion-timing::part:3 | 47 | active/shared | Agent: selected quote matches p47 | Final paragraph3.7; requires19 | — | pending | Conflict unresolved; context follow-up proposed, owner decision pending |
| 23 | `75a416e9c27b2b825d9552d057a53a5299ecc9fc75ff8fd6a3402d17bc1dd6e2` | handbook-table-6-arrows | 62 | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 24 | `f33b476401751a161527a3e4f1f2456d806fe3e8b68e78e9194979cd76873e26` | handbook-table-6-row-1 | 62 | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 25 | `f2bf449a9efd9f86ae7f468a81d94fc9e66253bf93da14218f7466ebd3590cb3` | handbook-table-6-row-2 | 62 | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 26 | `860a406301031b1604fc71be5876919c1da9fe9132f842bf651a80c82530a0fe` | handbook-table-6-row-3 | 62 | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 27 | `e9a58311aaf00eaa3f9f6be9d155ff2ad29b8f44c7c2d28487efc10468ff0e58` | handbook-table-6-row-4 | 62 | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 28 | `c783f1f2080cd2c7f9cd90fc747c1182acc979a0956824501f589ea4ab8336d4` | handbook-disciplinary-I | 87 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 29 | `9975ff9d98d0bacad2afd4dd71f4cfd02ae31082b3c17e95eeb98b1b2ea5ebee` | handbook-disciplinary-II.1 | 87 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 30 | `be5664bd8ccf0b542e12fb0efba80a107503f4c761c53eb118e52a1d6c5c7a37` | handbook-disciplinary-II.2 | 87 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 31 | `1a9820e53bdf94d4ab700d7f146b192b3788772e9c18aee0dcec8203b013023b` | handbook-disciplinary-II.3 | 87 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 32 | `04d70fde0576107e8e6cf9f76d72eb0100ba61bde5e74ee77e1d55ab72991232` | handbook-disciplinary-II.4 | 88 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 33 | `daeee0bde86cb1a1ea66f9253ea95f77d8db66ae35d471affc0e8fee2b616e73` | handbook-disciplinary-II.5 | 88 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 34 | `e8c188625b5f8a71be24b214f69576c8f55e9059594a0859b25aa1af1306778e` | handbook-disciplinary-II.6 | 88 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 35 | `2b8b681dacab938bde6e78d5a2e51f9cd4324b2a763dbcd0f40d35d0a8501a81` | handbook-disciplinary-II.7a | 88 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 36 | `a0ac5dca10456bffccba3992edf926bfb489c786e59873741ceb6fed4eb27ae4` | handbook-table-10-row-4 | 88 | active/shared; older exam-cheating | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 37 | `c34f803760d0667de323428c293e92766ce7e8447e58c02a665a27f54933ba4a` | handbook-disciplinary-II.7b | 89 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 38 | `df69670b89f5027177498b087b2c52d2ac6de5beaf0a7999582dcb89b1a38dc8` | handbook-disciplinary-II.7c | 89 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 39 | `5bb9af0bfb4b13bfa9022504883db4ad0f802272831dbd448c7e7f3a6b77a929` | handbook-disciplinary-II.7d | 89 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 40 | `022123ffe00872b5c699c589e2e0cc4fa18415347f54166d276b270294fb7ddf` | handbook-academic-dishonesty-shared-measures | 90 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 41 | `c5e6fa708dfa02509c147aa077a8abc4377d59a7cf8856ab081b881de2f32318` | handbook-disciplinary-II.7e | 90 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 42 | `faf0c9ec30a7119e443580ac17fe0209718a0d74549007b3335a7e0e4d0db404` | handbook-disciplinary-II.7f | 90 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 43 | `1c4a9263439990bc71e8483396eb45e369ee9c0e25f2f002dff1f635b3baae56` | handbook-disciplinary-II.7g | 90 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 44 | `7471c13443ee0f0983c91344d086fd2feac73f0065885990ed0413b50785d548` | handbook-disciplinary-II.7h | 90 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 45 | `61a3bfcb55acbb71406ff140be911c1e9b86a628600be8a90c63d36e206b5714` | handbook-disciplinary-II.8a | 90 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 46 | `67ba34c2fb22063bdf3830ded36edf758d3a0b7886dc654f30002a0e7fe34ae1` | handbook-disciplinary-II.8b | 90,91 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 47 | `4a552fb9fa4febe66ecff1a965dc225bb5686e03bf89723a04c568c5da14a35b` | handbook-disciplinary-II.9 | 91 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 48 | `fcc3bb91c7a2191ae8d0e68c4ac37ec3178abe2f25d636ee5eb1230a659a4f52` | handbook-disciplinary-II.10 | 91 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 49 | `a468ff84285a9c1ebb0cc5c3af972e2db865aafe056ab32dd1673fac2e9a7763` | handbook-disciplinary-II.11 | 91 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 50 | `3eae9c9fa4756542eb7fcb9d3b158242c79f6c4eca3495398d4c3ab8fc83e4d3` | handbook-disciplinary-II.12 | 91 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 51 | `1bdd53a8297184a558b3799a6d8b89eac6781ad930ab4d073581ac6f6e723c2d` | handbook-disciplinary-II.13 | 91 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 52 | `3d56b215a4d2e11b9220bdac963999360ec330698a0409e63d7c75c8cd80871b` | handbook-disciplinary-II.14A | 92 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 53 | `c918dde8e539e37cd3b12f9e217355ff6bd1d1fb03ec21e46c9b3fcd8c5c246b` | handbook-disciplinary-II.14B | 92 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 54 | `339816c8e918f400deb256f9de7a5a06d9d65f4c44916bb0f5bd687e26c6bca3` | handbook-disciplinary-II.15 | 92 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 55 | `41f02e25840bcaca4d84dab6331b1309a9d7014a82b59afcfaa57d4737fb4b81` | handbook-disciplinary-II.16 | 92 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 56 | `7449490493d083d0caf4c5be964a5704f4065d8c3ee100ab40ae2f9b07bffddb` | handbook-disciplinary-II.17 | 93 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 57 | `a7f81ff24b6b7d0792f8ac777fa5212be319b44fa944057e970c9cef04bacad5` | handbook-disciplinary-II.18 | 93 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 58 | `bec7d125000ca049eb9006a7fdf366aa57d72e996d139856f7da89f8ce029f79` | handbook-disciplinary-II.19 | 93 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 59 | `edb8d3e39253ee83d1dfaba0682028bec30903406d065d150b1ff4bb21387e3c` | handbook-disciplinary-II.20 | 93 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 60 | `004cfe275fbfb0ae4385fae6074c4716213f9e60a3686254e3a4272f0eb52004` | handbook-disciplinary-II.21 | 93 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 61 | `4b7ec542a372f58ecc42c62131e8a2f4209e11b85ac8dc37dffe442bb433a262` | handbook-disciplinary-II.23 | 93,94 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 62 | `74e921b225ac2bc39143b83bad573ec4793da9111805ae61371342b35a9b8844` | handbook-disciplinary-numbering-gap | 93 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 63 | `70f12caa6e7b0a3f260be9a461aca5f3c233ca0595d48f92262dbb2c07f21e2d` | handbook-disciplinary-II.24 | 94 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 64 | `3d1c889fabe31a6e9756c8704e8755aa40ce72de0a696476a1073427f7e16a75` | handbook-disciplinary-II.25 | 94 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 65 | `a5271913253117e8d37b9019bb7dfcc5cda2fdffa5c0fa226e16140b3d2e55c2` | handbook-disciplinary-II.26 | 94 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 66 | `c58a0eb763927348cf68a469bbb9db802ca30eb45936cc8719e76c279aba5f5c` | handbook-disciplinary-II.27 | 95 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 67 | `74027db2099b4287071dd40fdc7f2d9b00f4dc1ae2ff93946206d65b41e94452` | charter-pre-enrollment-header-checklist | 102 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 68 | `6a9eccd5aaf01c122209bff33a86f463d7409f4a86007619d996f553e3f87c2f` | charter-pre-enrollment-step-1 | 102 | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 69 | `2bcb9a1b246a076bfac640c01257c3fce3fe5fbcbd4cad9541d15acbc33848a5` | charter-pre-enrollment-step-1-expanded | 102 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 70 | `5986959e1ae1405d59dc3cef582c6e908225592a61f1dec9d454b2ace2b1f7d7` | charter-pre-enrollment-step-2-expanded | 103 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 71 | `28397902f9402e097d6167caab2b529f95934bbeb9533d1b58c893c03dbce290` | charter-pre-enrollment-step-3 | 103 | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 72 | `63dc784901145eb7d65b87f66f94e24c4fb15885bbea107ef5920482da142531` | charter-pre-enrollment-step-3-expanded | 103 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 73 | `01d7da512b86903ec99c58afed072160c9c365ef94304b48e7d36e1a60893413` | charter-pre-enrollment-step-4-expanded | 103 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 74 | `e26aa871228b71eaf2f84d86f9c1b393de16c7f0450e3a1125964825c4608472` | charter-pre-enrollment-total | 103 | draft-only | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 75 | `6eb18cb61b68a289417652c94bfe7d27a5e176da353089bae12fd24721f6e44e` | F01 | image | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 76 | `d44db1c77211a75a3e845825f032433a7572a975e69e3c5aba1f7a9d29ecad89` | F08 | image | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 77 | `bb2b7d5e3742187d33910260d5f9edd0d9a39731ed6be664e6fbd05c8efa8b90` | F09 | image | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 78 | `1167f48dd292b9eca5bf76cf165f1e363812f12f6398c94a0075c5d0fb7f1418` | V01-G2 | image | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 79 | `8c164a09202401220f98a404c137619d7ed40e92e8e69090d97c1bd040336bdc` | V05-G3 | image | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
| 80 | `1e4acc750776f674c708bc4a7918cf7f7de3d198b88b9a789370dab15105774b` | V07-office-context | image | active/shared | Not assessed | Not assessed; see snapshot companions | — | pending | None proposed; owner review pending |
