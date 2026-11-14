# Phase 1 and Phase 2 alignment audit

Read-only separate architectural audit, 10 October 2026. This is not another F/P2 fix recheck, a Spec/Standards closeout, design approval, formal Phase 2 start, source approval, adoption or merge. No tests, conversions, implementation or repository writes were performed.

## Conclusion

Phase 1's completed software boundary and Phase 2's candidate-only intent align. The whole Phase 2 pipeline is not implemented or release-ready. Two Medium future-integration/planning gaps require reconciliation: the shared F/P2 CLI surface and pending-register preflight before institutional conversion. The previously confirmed session cleanup High remains open. **NEW confirmed High: NONE.**

Current formal state: no active phase, Phase 1 software complete, Phase 2 ready/preparation only (W/plans/INDEX.md:8–12,25–26). This is compatible with missing source-backed final benchmark and institutional authorization; it is not permission to start or release Phase 2. The owner asked for alignment first and has not approved the proposed lifecycle design.

## Source keys and pins

- W = C:\Users\Hawksprey\source\repos\Bintanong-wt\integration-fin (clean HEAD 0caeaba8d8221a0f75b154e94bc3167b780f1407).
- E = E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10.
- F = E/draft_review_archives/f_final; P2 = E/draft_review_archives/p2_final; S = E/draft_review_archives/session_fixed. File references below use their exact archive source, not an imagined combined tree.
- Original clean draft tips independently read: draft-f dd699958505996358864383ff9c184cb98aec985; draft-p2 ef0cdbff9dca3af7a9f80fdd3036a701c61c2a3c; draft-session 3e0d6b361d83a965bf900dd6a41d6ea5c274bf54.
- All candidate manifests checked before/after: F 352/352, P2 348/348, S 348/348; all hashes equal, no extra/missing files. Ten shared-contract Python files are byte-identical across all three candidates and W.
- Exact owner architecture viewed read-only: C:\Users\Hawksprey\source\repos\Bintanong\Context\bintanong_full_runtime_routing_architecture.png. SHA256 2cc00d834625ad176a3773d56a03b5636dba6ffb449ff32059cc47d9d034ac40 equals integration copy.
- Actual thesis W/Context/bintanong_thesis_for_context.pdf has 88 pages; SHA256 729653540c7991496aceea1f728382d2e2262ca096e4342ce956d072e603c81c. Fresh direct reads: physical 55/65/71/75, printed 54/64/70/74. Existing complete 18-page source evidence and authority report were consulted; no new legal determination is made.

## Alignment matrix

| Boundary | Status | Actual evidence and remaining boundary |
|---|---|---|
| Phase 1 software exit and formal Phase 2 eligibility | ALIGNED | INDEX:8–12; phase-01-handoff.md:17–27,85,100. Ten contracts/governance/split protocol and honest pending trace complete the software exit; source approval and the final benchmark remain unmet. Formal owner-go still required. |
| Pending identities, state transitions and institutional/private separation | ALIGNED PLAN ONLY | P2 plan:25–28,236–250 consumes exact Phase 1 models and pending-only states; actual governance.py:177–204 defines required fields, :88–105/:222–227 enforces evidence-backed transitions. Tasks 3–6 and register minting do not exist in P2 candidate (document_ingest contains only __init__.py and inspection.py). |
| Institutional manifest/register preflight before conversion | GAP | Master:278 and Phase 1 plan:52 require registration/manifest validation before parsing; P2 Task 3:147–160 specifies snapshot/conversion, while Task 5:236–242 mints pending records after Task 3/4 output. The prepared plan lacks an explicit pre-conversion SourceDocumentVersion validation step; see Medium A2. |
| SourceSpan/Chunk binding, raw text, page geometry and editions | ALIGNED PLAN ONLY | P2 plan:161–180,198–212,219–255 preserves raw printed text/all provenance and requires geometry/digest binding. Actual source.py:151–208,273–345,349–392 enforces digest/page/geometry, joined text, and register-bound states. Future producers remain unimplemented. Existing extractor mapping limitations remain documented, not silently weakened. |
| Hardened generic parser and F CLI registration | GAP | F ingest.py:17–60,63–78 and P2 ingest.py:38–104 target the same module with incompatible command forms. Whole-file adoption drops one draft's behavior; see Medium A1. No combined candidate exists or was executed. |
| F source-root candidate adapter vs institutional provenance | GAP | F prospectus.py:21–37,56–68,261–274,287–297 implements pending provisional digest identity before output and null approved_source_version_id. It does not mint a Phase 1 SourceDocumentVersion or bind chunks. This is intentionally review-only; institutional bridging, actual original conversion and original-backed accuracy remain unproved. |
| PPTX slide locator | ALIGNED PLAN ONLY | Actual SpanLocator kinds source.py:114–141 and SourceSpan:151–166 have no slide locator; P2 plan:198–205,360–361 explicitly rejects PPTX units as pending_locator_contract without calling slides PDF pages. Future Task 4 is not implemented; owner schema decision remains open. |
| OCR accuracy and final benchmark | BLOCKED | P2 plan:268–281 requires frozen independent references and ten-document gating; handoff:27,94 has 0 verified final/0 Taglish against >=50/10 per category. Separate prospectus photo benchmark and real phone photos remain gates; test counts are not OCR accuracy or completed institutional evaluation. |
| Private SessionFact trust boundary | ALIGNED | Shared governance.py:461–485 enforces private_session/session_only/user-origin facts and namespace separation. S/store.py:22,136–180,194–218 applies capability lookup, session ownership, whole-result validation, deleted/expired late-result refusal and cache clearing. No API or real parser is wired. |
| Private parser storage/deletion/crash recovery | BLOCKED | Known High S/store.py:188–192 excludes TemporaryDirectory cleanup from sanitizer, and uses ordinary temporary disk storage. Master:613–619,636–642 requires transient storage, isolated bounded conversion and deletion/failure/restart design. See carried blocker K1; same-process indefinite retry proposal is unapproved and insufficient for full compliance. |
| LLM routing and output-validation loop | ALIGNED PLAN ONLY | Master:10,21,42 and exact PNG specify LLM RAG/Hybrid/Symbolic -> integration -> generation -> validation; NO returns to Neuro-Symbolic Integration. Shared routing_adapter.py:41–53 refuses legacy Direct and requires typed Symbolic/Hybrid predicates. Existing API bintu_client.py:14,48 still permits Direct; this known compatibility/owner boundary is unchanged, not evidence of delivered diagram-wide runtime. |

## Confirmed future-alignment findings

### A1 — Medium: CLI and hardened-parser adoption collision

Files: F/backend/bintanong_tools/ingest.py:8,17–60,63–78; P2/backend/bintanong_tools/ingest.py:38–104. F/docs/decisions/draft-phase-f-tools-cli.md:19,32,60 already records the change to subcommands; P2/docs/decisions/phase-02-ingest-hardening.md:6 preserves one command.

Concrete source-level reproducer (not run in this audit): F's existing test_prospectus_command.py:36–43 invokes `ingest parse <path>` and asserts both commands appear; P2's test_ingest_hardening.py:151–153 invokes the module with `<fixture.pdf>` directly, and :213 invokes `[source, -o, output]`. F registers two commands; P2 registers one and has no prospectus registration. Selecting F's whole file restores its old regex fallback, forced page count and direct output.write_text; selecting P2's whole file removes F prospectus command/import. Simply registering prospectus on P2 also changes the root CLI form expected by P2's current invocation tests.

Impact: both drafts can pass independently while a future integration loses a command or restores unguarded output writes. This is a confirmed adoption conflict, not a claim that a deployed combined system currently fails. F's inherited generic parse body was not the subject of its native-diagnostic fix recheck.

Smallest future requirement: retain P2 parse_document, stderr/JSON behavior, alias refusal and atomic publication, add F prospectus registration/body, and decide/document one compatible CLI interface with updated affected callers/tests. Inspect tools/scaffold tests and container help/CLI examples at that point; do not change Docker now. Owner must choose backward compatibility or an explicit migration to `ingest parse PATH`; no default is adopted by this audit.

### A2 — Medium: prepared institutional conversion sequence lacks explicit pending-register preflight

Files: W/plans/master_implementation_plan_original_long.md:278; W/plans/phase-01-source-governance-contracts-plan.md:52; W/plans/phase-02-document-ingestion-plan.md:147–160,214–242,252–254.

Concrete plan reproducer: follow Tasks 2 -> 3 -> 4 -> 5 literally. Task 2 produces inspection/source manifests with path/digest/size, Task 3/4 run conversion from snapshots, and Task 5 then creates pending SourceDocumentVersion records from the inspection report. No described Task 3 input requires a Phase 1 register record or check_register preflight before conversion. The present Tasks 1–2 implementation is not accused of regression; generic parse_document may remain a lower-level converter. Existing external acquisition inventory is byte-copy evidence, not a demonstrated Phase 1 contract validation step in this future institutional workflow.

Impact: a future converter may emit candidate text before the required institutional identity/governance record is structurally validated. The prepared plan's later binding can reject output, but it does not establish the pre-parse manifest invariant.

Smallest future requirement: mint or load the pending identity record from the digest manifest and validate it at the institutional conversion preflight; keep chunk binding/reporting later. If a separately existing valid register is to be reused, name it as the required input and validate the digest against the current snapshot. Do not infer approval; all pending/approval-null rules stay.

## Previously known blockers, not new findings

### K1 — High, open: private parser cleanup can retain bytes and leak a native path

S/backend/bintanong_session/store.py:188–192; existing independent E/draft_review_archives/SESSION_STANDARDS_REVIEW.md:5. Reproducer E/session_standards_evidence/runner.py:85–114 writes fictional private bytes, holds its own Windows file handle, then raises; TemporaryDirectory exit raises raw PermissionError/WinError32 with private filename/traceback and retained bytes. Existing evidence shows caller bytearray wiped and no facts committed; that does not delete parser files. No reproducer was repeated here.

Master:613–619/636–642 and thesis physical65/printed64 remain the authority boundary. Current ordinary unbounded TemporaryDirectory, generic in-process extractor and no real restart design do not establish isolated bounded transient conversion. The earlier pending cleanup/retry proposal could retain private bytes indefinitely and lose ownership on crash; it was not approved. Error sanitization alone cannot close K1. Design/implementation remains queued, not done.

Other carried boundaries: F's latest independent Spec is FAIL on the preceding fix archive; final native-error repair is tested but not re-reviewed, Standards not run (E/draft_review_archives/F_SPEC_RECHECK.md:3–6). P2's permitted Spec and owner-exception Standards rechecks report PASS for scoped Tasks 1–2 only (P2_SPEC_RECHECK.md:3–7; P2_STANDARDS_RECHECK.md:3–6); this audit grants neither another recheck nor adoption. M01's adapter guard regression was recovered; historical 52/52 mutation kills are unproved. Source authorization, printed edition/scope/effectivity, CSG documents, human GUI/B2 acceptance, tokenizer limits, OCR references/photos and final evaluation stay open.

## Contract and provenance details

SourceDocumentVersion uses `byte_sha256`, `acquisition_locators`, four `{state,evidence_ref}` fields (`acquisition_state`, `verification_state`, `approval_state`, `content_review_state`), and `approval_id`; it is not F's three-field provisional source row (`pdf_sha256`, `source_locator`, `source_verification`). P2 Task 5 proposes distinct doc-/ver-/edition- IDs from bytes, logical locators, scope pending and approval not_requested/null. Pending is accepted without evidence; `not_stated` requires reviewer absence evidence and cannot be minted just because extraction found nothing (governance.py:88–105,225–234; governance decision:41,63–67).

Duplicate bytes are one registered version with many logical locators; differing bytes cannot silently share an edition (governance decision:67). Chunk.bind copies register states/evidence references rather than promoting extraction labels (source.py:377–391); check_chunk_binding checks byte digest, document/version/edition IDs and exact states/evidence references (:349–374). SourceSpan requires physical page distinct from optional printed folio; bbox requires origin/page-size and valid geometry. Split original_page/page_offset must agree (:151–198). Raw punctuation/negation/superscripts remain a producer obligation; normalized whitespace validation does not certify actual PDF transcription.

The existing chunk adapter remains prospectus-specific: chunker/method checked at chunk_adapter.py:87–90, page-size supplied or refusal at :191–209. P2 Task 5 deliberately uses a distinct policy chunker and Chunk.parse, not that adapter (plan:219–225). Existing raw-layout hash/three textless-span limitations and cached PDF association are documented in phase-01-contracts.md:39–41,87 and phase-01-handoff.md:29–31,90. A valid cached trace or thousands of tests never authenticates source approval or original conversion correctness.

## Historical prose and current state

Phase 1 plan:11,78–83,93 preserves startup/uncompleted prose, but handoff:85 explicitly says completed frontmatter, INDEX and final handoff supersede it. Phase2-workstream-status.md:3 is explicitly a 7 October snapshot; its open PR/old dev/Phase 1 ready wording is stale against the fresh integration commit and current ledger. The preparation document's earlier ready-state prose is also expressly historical (handoff:100). These are preserved notes, not new contradictions or instructions to repeat already integrated work.

Plan/handoff statements about nine owner entries are historical. Root's current pickup rule is four preserved owner entries; this audit did not touch the owner checkout. Fresh Git and current owner instructions outrank those older gates.

## Read receipt and evidence limits

Complete consecutive reads: W/plans/INDEX.md (42); phase-01-source-governance-contracts-plan.md (97); phase-01-handoff.md (104); phase-02-document-ingestion-plan.md (374, three consecutive chunks); phase-02-document-ingestion-preparation.md (39); phase2-workstream-status.md (46); W/docs/decisions/phase-01-consumer-inventory.md (100), phase-01-source-governance.md (123), phase-01-contracts.md (111). Draft decisions fully read: draft-phase-f-tools-cli.md (70), phase-02-ingest-hardening.md (20), phase-02-inspection.md (21), draft-session-lifecycle.md (80). Truncated combined output was reread in smaller consecutive ranges; no claim is based on title alone.

Master full selected sections:1 lines8–52;4 136–158;6 231–271;7 272–308;11.4 443–454;15 605–643;16 644–682 (236 total lines). Reviewer role and Spec prompt were read as Markdown only. Exact PNG visually viewed; four thesis pages reread directly from actual PDF. Existing complete18-page source read and independent session authority analysis supplied broader thesis context.

Actual source inspection: both complete candidate ingest.py files; shared source.py; relevant governance.py/routing_adapter/chunk_adapter validators; F provisional source/run_candidate/source-root guards; P2 tree walk/final manifest publication; session capability/extraction/deletion/cache boundaries; API health-only surface and legacy router. No native-diagnostic implementation recheck or new runtime experiment was performed.

candidate_hashes_before.json and candidate_hashes_after.json attest immutable archives. source_evidence.json records exact PNG/PDF hashes and ten-file shared-contract parity. An initial parity helper included pre-existing W/__pycache__ files and stopped at its assertion; subsequent comparison correctly scoped source Python files, showing all ten byte-identical. No candidate code or bytecode was written and no cache was removed.

Skipped: no tests/suite repetition, real institutional conversions, real private uploads, mutation batches, source activation, actual ACL/container/browser/Linux/macOS/service-restart/deployment runs, authenticated office/privacy approvals or new legal verification. This bounded audit does not certify a release.

Residual risk: adoption must reconcile the two Medium alignment gaps; the known High prevents private-upload readiness. No lifecycle design, code change, extra F/P2 recheck, API/Docker work or institutional use is authorized by this report.
