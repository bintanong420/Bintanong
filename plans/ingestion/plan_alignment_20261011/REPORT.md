# Phase 1/2 institutional bridge and Phase 6 source alignment

Reviewed 2026-10-11, Asia/Manila. Read-only architectural assessment of the proposed documents; no product or plan edits, tests, commits, phase advancement or approval. Independent Codex reviewer: /root/plan_source_alignment, with one same-review clarification. This is not a code Spec/Standards run or an M1 repair recheck.

## Verdict

Both proposals follow the sources as bounded, inactive candidate-preparation work. They are not yet a complete Phase 1-to-2-to-6 pipeline. Two Medium plan corrections are required: define the cross-plan structured-evidence handoff, and remove ambiguity between unresolved source semantics and invalid inputs. No confirmed High architectural contradiction. Implementation alignment and accuracy remain UNVERIFIED because neither plan has been executed.

## Source/read receipt

- M = C:/Users/Hawksprey/source/repos/Bintanong-wt/integration-fin/plans/master_implementation_plan_original_long.md. Root read all 869 lines in consecutive chunks, including the truncated first-output subsection through an explicit reread. Last heading: 22. Definition of done.
- T = C:/Users/Hawksprey/source/repos/Bintanong-wt/integration-fin/Context/bintanong_thesis_for_context.pdf, 88 physical pages. Root freshly extracted and read physical pages 17–20,41–44,53–59,65–79 (30 relevant pages); this is not a claim to have read all 88 pages this turn. Physical pages 42,43,77,78 were freshly rendered and visually inspected, including Figure 3.6, the prerequisite truth table and Tables 4.1/4.2. Physical PDF numbering differs from printed labels by one on these pages.
- A = C:/Users/Hawksprey/source/repos/Bintanong/Context/bintanong_full_runtime_routing_architecture.png. Inspected visually. Owner and integration-fin copies have the same SHA256. Visible sequence: query tokenization/NLP, LLM adaptive router, RAG/Hybrid/Symbolic branches, neuro-symbolic integration, augmented generation, output validation, render or validation-failure loop. Dotted ingestion arrow enters Prolog query build.
- Read both complete specifications and plans: unified SPEC91 lines / PLAN71 lines; Phase6 SPEC68 lines / PLAN58 lines. Exact paths, last headings and hashes are in SOURCE_RECEIPT.json. These sources were not edited.
- The independent reviewer read both complete specifications/plans, relevant master sections, all 18 previously requested physical-page extracts and the exact owner PNG. Root supplied the independent fresh original-PDF check; do not imply the child freshly extracted all PDF pages.

## Confirmed Medium findings

### M1 — Missing structured-evidence handoff between the two plans

Location: unified_ingestion_design/IMPLEMENTATION_PLAN.md:53,58–59 and phase6_prologifier/IMPLEMENTATION_PLAN.md:39.

Scenario: implement both plans exactly as written, call load_candidate_bundle(path), then try to feed its defined return value to build_rule_candidates. The loader returns source_register/chunks/report. The compiler additionally requires the curriculum payload and a mapping from each exact course and field to supporting SourceSpans. Publishing prospectus_candidates.json does not define that producer mapping or expose it through the checked API. Chunk-level evidence cannot establish every course field's provenance.

Authority: M:249–257 defines shared source/span/chunk contracts; M:278–287 requires raw structured evidence and review history; M:413–420 requires source-linked structured rule specifications and a single authoring truth. Unified SPEC:64–69 explicitly promises field-level rule binding and a downstream Phase6 handoff.

Minimum correction: explicitly schedule one checked candidate-to-compiler adapter and a synthetic end-to-end handoff acceptance case. It consumes the hash-validated structured candidate payload plus its actual raw/field-decision evidence, binds field spans to the same source version, and retains missing support as blockers. Define whether the checked bundle loader returns the verified domain payload or the adapter obtains it through a documented checked API. Do not infer field support from a whole chunk, fabricate cell mappings or introduce an independently edited rules store. Keep the compiler pure and independently testable.

This is an integration-plan gap, not a reproduced product failure. A deliberate later integration task is valid, but the two standalone modules must not be reported as the completed singular pipeline.

### M2 — Unknown prerequisite refusal conflicts with review-blocker behavior

Location: phase6_prologifier/IMPLEMENTATION_PLAN.md:42 versus :46; phase6_prologifier/SPEC.md:46,50.

Scenario: a structurally valid, source-supported prerequisite cell prints XX999, but XX999 is absent from the extracted course catalog. Plan:42 says unknown prerequisite courses refuse globally; :46 and the spec require recoverable unknown semantics to remain blocked records. An implementer could therefore discard the entire review artifact for precisely the evidence needing review.

Authority: M:435 preserves actual logical structure; M:449,453 distinguishes unknown coverage from proven failure and empty prerequisites; M:457 requires unresolved references and cycles to be flagged for review. The owner's Phase6 instruction also explicitly retains unresolved prerequisites and alternatives as review blockers.

Minimum correction: specify an unresolved_reference record retaining XX999, the raw wording and valid spans, with dependent rule views blocked while the review artifact is returned. Global refusal remains appropriate for malformed data, foreign/forged source identity or invalid span binding, and a claimed resolved edge inconsistent with its evidence. Add this exact source-backed synthetic case to the plan. Existing prerequisites.py already separates prerequisites_unresolved from resolved prerequisites; reuse that distinction.

This is a Medium wording/semantic-contract ambiguity. No runtime failure was reproduced, and no existing review verdict is changed.

## Smaller clarifications and reuse

- Low: distinguish historical extractor 'Phase1' from master Phase1 governance/contracts (M:143–148,231–270). Call the bridge governed institutional ingestion; master Phase2 contains extraction/chunking. Historical extractor completion does not certify institutional source authorization.
- Low: unified SPEC:91 has stale design/selection-gate wording inconsistent with SPEC:3 and the current implementation plans. Use the current plan-confirmation state; the separate-subagent execution method is already selected.
- Reuse: unified Task1 should use source.bind_chunk/check_chunk_binding (backend/bintanong_contracts/source.py:349–392) after its stricter prechecks, rather than duplicating register-state/evidence binding. Check foreign preexisting span claims before calling a helper that overwrites bindings.
- Chunk IDs: no demonstrated current collision. The existing adapter hashes byte SHA, locator, content and chunker version (chunk_adapter.py:71–72). Pending register IDs are ver-<byteSHA> (register.py:65–68), and governance rejects duplicate-byte versions (governance.py:357–358). Thus current version separation is represented through the digest. Document this invariant; require an explicit migration/release-key policy before introducing another version-identity scheme. Preserve existing IDs in this bounded draft.

## Boundaries already aligned

| Boundary | Plan behavior | Source support |
| --- | --- | --- |
| Institutional preparation | Separate explicit researcher workflow; immutable bytes, pending register, hashes, manifest-last publication | M:84–95,157,278–287,659; T:17,55–56,68,75–76 |
| Candidate authority | Technical completion never grants source verification, content review, activation or institutional approval | M:36,237–241,307,413–422; T:17–20,75–76 |
| Private material | Excluded from institutional candidate bundles, rules, vectors and durable corpus; lifecycle remains separate | M:355,605–642; T:18–19,55,65–66 |
| Phase3 handoff | Existing Chunk contracts retained; estimate-v1 reported honestly; reviewed eligibility and exact model tokenizer remain required | M:249–252,293,311–322 |
| Phase4/release | No database write or activation; embeddings and reviewed rule bundle meet in compatible release later | M:88–95,346–367,538–546 |
| Phase6 scope | Reuse extractor/generator helpers; inactive JSON, field evidence, alternatives/corequisites/cycles and missing numeric evidence block usable views | M:413–435,443–463; T:41–44 as illustrative material only |
| Runtime routing | No router, Janus or answer-path edits; eventual approved knowledge feeds existing paths | A adaptive-router branches and validation loop; M:10,21,99–134,437–441 |
| Evaluation | Smokes are execution evidence; original corpus, human checks and OCR/photo measurements remain necessary | M:303–307,703–747; T:58,68–73 |

## Source contradictions that must remain explicit

- T:59 describes generating a preliminary answer before symbolic validation, whereas A routes symbolic results into integration before generation. Follow A and M:21,43. Neither proposed plan reinstates the older ordering.
- T:41–44 illustrates negation-as-failure and definitive denial from unproven completion. Follow M:45–46,449–453: unknown facts/coverage cannot become an approval or unsupported definitive denial. The example course chain is illustrative, not an authorized PalSU rule (M:459).
- T:67 and T:75–76 differ on authorization; M:49 records the selected stricter issuing-office verification/activation workflow. M:157 allows isolated candidate preparation without formal advancement. This report makes no legal conclusion or institutional approval.
- T:77 mentions student-related relational storage; T:65 and M:47,355 prohibit persistent personal academic records. Institutional relational curriculum data and transient private student facts remain separate.
- T:58 contains OCR accuracy [X]%; no measured accuracy follows from it. Existing engine smoke success is not a replacement for the ten independently transcribed references required by M:303.

## Delivery sequence and limits

1. Correct the two Medium plan contracts plus the small naming/gate/reuse notes in external design documents; do not expand into a new extraction framework.
2. Confirm the revised concrete plans before product execution. Use the already selected separate implementer, Spec, then Standards workflow; maximum root+one active child. Preserve the unrelated M1/F/session review debts and actual recheck rules.
3. Implement the shared institutional boundary and pure Phase6 candidate module in bounded local draft batches. Add the explicit checked bridge test before claiming that they form one end-to-end pipeline. Focused tests and truthful local commits remain appropriate.
4. Keep formal phases, reviewed activation, embeddings/storage/Janus/runtime/API/Docker and institutional authority at their applicable later gates. Completing these plans alone does not establish90–95% overall ingestion: OCR integration/accuracy/photos, original-source validation and private lifecycle still require evidence.

No product edits, new tests, commits, merges or original-source conversions occurred during this review. The original and proposed documents remain intact. Existing private cleanup High and independent candidate-review debt remain open. Full thesis/system correctness and implementation readiness were not certified.
