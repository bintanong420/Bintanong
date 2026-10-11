# Session cleanup: source-authority analysis

2026-10-10. Read-only design-authority analysis by the separate authority-check agent. This is not a code-review verdict or approval. The existing cleanup High remains open. No implementation, tests, probes, Claude invocation, product edits, worktree edits, archive edits, Git actions, dependency changes, or subagents.

## Answer

The proposed pending-cleanup queue, operation-driven retry, sanitized errors, and upload admission/commit block improve same-store containment. They do not satisfy the unchanged master plan's full private-file deletion/restart/transient-storage/isolated-Docling contract. The proposal itself permits private parser bytes to remain after extraction failure, explicit deletion, or expiry indefinitely while a handle stays open; same-store ownership is lost on disposal/crash/restart. It adds neither memory/bounded-tmpfs processing nor an isolated conversion job. A smaller code diff does not make that weaker retention contract source-conformant.

Do not call this an unconditional violation of an explicit thesis deletion timer: the thesis does not specify such a timer. Distinguish the thesis's direct privacy obligations from the master's implementation resolutions. Likewise, master 636 says restart cleanup occurs "as designed" and master 642 limits claims to the tested boundary; neither establishes guaranteed forensic erasure in every operating-system failure. Nevertheless, allowing indefinite retained disk bytes without a restart design leaves the stated implementation requirement unresolved.

## Source identifiers

- M: C:\Users\Hawksprey\source\repos\Bintanong-wt\integration-fin\plans\master_implementation_plan_original_long.md
- T: C:\Users\Hawksprey\source\repos\Bintanong-wt\integration-fin\Context\bintanong_thesis_for_context.pdf
- D (exact owner-supplied authority): C:\Users\Hawksprey\source\repos\Bintanong\Context\bintanong_full_runtime_routing_architecture.png
- P: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\session_cleanup_design\PROPOSAL.md
- H: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\draft_review_archives\SESSION_STANDARDS_REVIEW.md
- Reviewer instructions read as Markdown only: C:\Users\Hawksprey\source\repos\Bintanong\.claude\agents\extractor-reviewer.md

## Authority and provenance

M:16-23 explicitly sets precedence: current project instructions override older thesis routing descriptions; the runtime diagram governs runtime flow; thesis supplies remaining requirements; unspecified engineering details are explicitly proposed in the master. M:36 says the thesis and architecture diagram are not the operational policy corpus. They do not establish actual PalSU thresholds, prerequisites, fees, deadlines, or exceptions.

The exact owner-supplied diagram was visually inspected, as was the integration-fin copy. Root reports both SHA256 values match 2CC00D834625AD176A3773D56A03B5636DBA6FFB449FF32059CC47D9D034AC40; this agent did not rerun hashing. The diagram shows query interpretation, LLM-based routing, RAG/Hybrid/Symbolic paths, integration, generation, and validation. Its NO-validation arrow returns to Neuro-Symbolic Integration, then Augmented Response Generation; it does not replace the LLM router with a classifier. Existing owner constraints remain preserved. It does not supply a private-file retention deadline, cleanup failure policy, or restart storage design. Do not infer a retention exception from the diagram.

| Claim | Explicit source and classification | Consequence for this proposal |
| --- | --- | --- |
| Private uploads are isolated to the authorized user/session; no automatic institutional indexing; evaluate cross-session exposure | THESIS: T physical18-19 / printed17-18, physical55 / printed54, physical65 / printed64. MASTER preserves and operationalizes this at M:31-32, 239, 260, 627-638. | Private cleanup state must not become institutional data. The proposal intends this, but no fresh implementation evidence was gathered. |
| No personal academic records including grades, enrollment status, or student identification will be stored | THESIS: T physical65 / printed64, continuing minimization discussion physical66 / printed65. MASTER resolution M:47 preserves institutional curriculum persistently and private student facts transiently. | Indefinite leftover grade/parser files cannot be assumed authorized merely because they are private or fail-closed. The transient-vs-persistent distinction is a master resolution, not literal thesis wording. |
| Process private uploads in memory or bounded tmpfs; exclude persistent volumes, institutional buckets, ordinary logs, backups | Explicit MASTER implementation requirement M:613; not prescribed in the required thesis pages. | The proposal's ordinary Windows temporary-directory cleanup queue does not establish this storage boundary. No claim of full Phase10 compliance is supported. |
| Isolated Docling conversion job, bounded resources, no runtime fetch once cached | MASTER M:614. THESIS T physical77 / printed76 Table4.1 names Docling2.93.0 as local OCR for user photos and institutional indexing, without prescribing process isolation. | A generic in-process callback plus queue is not evidence of an isolated Docling job. Proposal approach3 P:27 is an architectural option, not delivered compliance. |
| Delete original bytes and temporary parser files after extraction; minimal context retained for short documented session | MASTER M:618. Shortness is an implementation requirement; the direct thesis wording is non-storage/minimization. | P:25,44,76 explicitly permit residual disk bytes beyond extraction, deletion, and expiry with no deadline. Queue ownership does not equal deletion. |
| Remove session state on explicit deletion, expiry, and failure cleanup; temporary data disappears after these events and restart as designed | MASTER M:619,636; deletion surfaces M:654-655,663. The specified thesis pages do not directly define these lifecycle/restart mechanics. | P:38 can still expire/delete facts/cache, but that is distinct from physical parser-file deletion. P:44,76 exclude crash/restart/store-disposal recovery. |
| OCR artifacts/errors/traces/telemetry/evaluation exports do not persist grades or identifiers | MASTER M:637, supported generally by THESIS privacy/minimization T physical65-66 / printed64-65. | P:33,39 sanitize lifecycle errors in design. H:5 records a pre-existing native exception leak and retained private bytes. Sanitization alone does not resolve physical retention. |
| 30-minute idle lifetime | Explicitly PROPOSED MASTER value M:621, subject to research privacy protocol. | It is not a thesis-mandated deadline or approval to retain raw files. Proposal's existing30-minute/8-hour fact TTLs do not authorize indefinite parser-file retention. |
| Stop new uploads and reject in-flight commit until pending cleanup resolves; retry only on purge/access | PROPOSAL P:25,35-40. Neither THESIS nor the read MASTER sections prescribes this exact mechanism. | Reasonable containment inference, but no autonomous recovery, retention deadline, or restart ownership is supplied. |
| Developer owner approval authorizes exceptional indefinite privacy retention | PROPOSAL's requested decision P:42-46; no such authorization rule was found in THESIS or MASTER. | Owner review can authorize a draft engineering scope; it cannot by itself establish conformity to an unchanged privacy protocol or replace issuing-office authorization. |

## Institutional approval discrepancy

T physical66-67 / printed65-66, under Institutional Document Authorization, claims explicit written authorization is not legally required for publicly available documents and proposes office request letters for accuracy/courtesy. T physical75-76 / printed74-75 nevertheless says issuing-authority formal written approval, signed by adviser and chairperson, will be requested before digitization/indexing, then conversion proceeds once approval is obtained. This is a manuscript discrepancy, not a legal conclusion from this analysis.

M:49 explicitly resolves it by following the acquisition procedure on physical75-76, recording issuing-office verification/authorization before activation; M:237-241 requires source identity, issuer, scope, authorization/verification state, and a separately approved institutional ingestion path. M:157 permits prospectus conversion/review preparation without advancing the formal ledger; M:307 says human correction does not establish issuing-office or curriculum-version approval. This allows isolated review-candidate preparation and does not manufacture institutional approval.

No evidence of completed institutional approval or an approved exceptional-retention privacy protocol was reviewed. The owner has not approved P. Do not treat the owner's design decision as office authorization for institutional knowledge or as the research privacy protocol. Conversely, these sources do not identify a new legal requirement that every internal cleanup-code change itself receive institution approval; do not invent that requirement.

## Other required sections and boundaries

M section4: bounded modules have reviewable artifacts and exit gates; Phase10's result includes isolated private context with deletion/leakage checks (M:138,152). Preparatory correction artifacts stay candidates and do not advance the formal phase ledger (M:157).

M section6: institutional truth requires source governance, separate private context, and source-span provenance including both PDF position and printed label (M:237-260). The cleanup proposal cannot reclassify private uploads as authorized institutional records.

M section7: preserving original institutional bytes and extraction/review history (M:278,285,305) applies to canonical institutional ingestion. It is not permission to retain private student parser files indefinitely. Private uploads instead follow section15. Parsing is separate from embeddings and database writes (M:274,307).

M section11.4: operational reasoning errors must not become policy outcomes, and missing authoritative coverage yields unknown/unsupported rather than invented rules (M:447-453). This is a separate reasoning boundary; upload cleanup failure cannot be represented as a successful upload or institutional result. This last application is an engineering inference, not a cleanup requirement explicitly stated in section11.4.

M section16: explicit session/file clearing belongs to the student-facing flow (M:654-655,663), and transport cancellation/retries/disconnects must not duplicate completed requests or expose cross-session state (M:677). A future cleanup design must connect these paths; the current proposal supplies no API or deployment integration, and no such work was performed here.

## Source-conformant next step

Keep the High open. Reframe the next reviewable artifact as an architectural lifecycle design grounded in M:613-619,636-642: transient memory/bounded-tmpfs storage, an isolated bounded conversion job with explicit resource ownership, cleanup after extraction/failure/deletion/expiry, and a documented crash/restart behavior. Define observable deletion success, what occurs when deletion cannot complete, admission/commit behavior, and the tested operating-system/deployment boundary. Isolated workers may release worker-owned handles on orderly exit; they do not automatically solve external handles, filesystem faults, or every crash. Treat that as a design assumption to resolve, not proven success.

The bounded queue/error correction can remain a candidate containment component or synthetic-only standalone prototype. It must not be presented as closing the full privacy/deletion finding or satisfying Phase10 while indefinite retained bytes and restart loss remain. If exceptional retention is proposed, specify a real bound and recovery trigger and reconcile it explicitly with the research privacy protocol and master requirements before real private-record use. No owner approval has been inferred; no implementation is authorized by this report.

## Read receipt

- M sections read in full consecutive chunks: section1 lines8-52 (45); section4 lines136-158 (23); section6 lines231-271 (41); section7 lines272-308 (37); section11.4 lines443-454 (12); section15 lines605-643 (39); section16 lines644-682 (39). Total236 lines. Blank separators included; no section contents skipped.
- T actual physical page count88. Fully extracted and read18 required physical pages:17-20,55-56,65-67,68-71,75-79. Printed labels are physical minus1 for this set:16-19,54-55,64-66,67-70,74-78. Do not cite TOC numbers as physical positions.
- Page headings/content read: Scope/Limitations/Operational Definition of Terms (17-20); supplemental private-file inputs/institutional inputs/pre-processing (55-56); Informed Consent/Data Privacy/Read-Only System Architecture/Responsible Use/Institutional Document Authorization/Participants and Dataset (65-67); dataset/system benchmark/Knowledge Base Documents/User Evaluation Participants/Research Instruments/System Performance Instruments (68-71); acquisition and formal-approval procedure/Implementation/Table4.1 Software and Language Stack/Table4.2 Hardware Stack/deployment (75-79).
- Visual spot checks: T physical65/printed64;67/66;75/74;77/76. Confirmed privacy wording, both authorization statements, printed labels, and Docling stack-table row. Exact owner-supplied D runtime PNG and the integration-fin copy visually read. Other required pages were read through full text extraction, not individually rendered visual review.
- P all76 lines read; H all9 lines read. The H reproducible High is carried forward as documented evidence, not rerun. Reviewer Markdown read; its test rerun and APPROVED/CHANGES NEEDED ending are not applied because the current task explicitly forbids tests and review verdicts and is an authority analysis.
- SOURCE_EXCERPTS.md contains all236 master source lines and all18 complete extracted thesis pages. New evidence/report/render files are confined to this external session_cleanup_authority_check directory.

Not checked: no new tests/probes, real parser, API/deployment/restart behavior, independent legal verification, or completed institutional/privacy approval.
Residual risk: private bytes may remain indefinitely under the bounded proposal, and same-store cleanup ownership may disappear on crash/restart; the High remains open.
