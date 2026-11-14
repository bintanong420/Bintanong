# Unified Task3 dispatch brief

## Global constraints

- Baseline is clean draft/phase2-candidates-20261010 at57b598522cc7ed5d13e40eb8d1bcafede8c9ba1b; verify fresh Git and usage before execution.
- Every PowerShell starts Set-Location to the actual worktree; all paths absolute; py -3.13 -B; pytest -p no:cacheprovider with a new external basetemp. Offline, no installs/downloads/dependency/lock changes.
- No owner writes, protected-ref movement, push/PR/merge/history rewrite or attribution. Explicit staging only. Originals/private/generated artifacts outside Git.
- No embeddings, executable .pl files, Janus, routing, API/Docker or institutional activation. Candidate completion never grants source/content approval.
- Preserve pending-only register preparation. Keep existing loaders/contracts/extractor APIs intact. Do not adopt entire F files or reuse its unreviewed fixes implicitly.
- Stop new batches at>=85% of either Codex window; save promptly above85%; never spend toward90%.
- M1 repair remains independently unrechecked. A new feature review must not masquerade as its prohibited Medium recheck; retain that separate review debt until an explicit exception.


## Task3: Connect the checked prospectus bundle to inactive rule candidates

**Depends on:** unified Tasks1–2 and the Phase6 pure compiler task. Execute after the compiler is tested and independently reviewed.

**Files:** create backend/bintanong_tools/document_ingest/prospectus_rules.py and tests/test_prospectus_rule_handoff.py; extend docs/decisions/phase-02-unified-ingestion.md. No extractor/contracts/runtime changes.

**Produces:** `prepare_rule_candidates(bundle_path:Path)->dict[str,Any]`. It uses load_candidate_bundle, requires prospectus_candidate kind and passes the verified domain_payload, exact registered source, derived per-course/per-field SourceSpans and applicable review evidence to build_rule_candidates. It returns inactive JSON in memory; no publication, .pl, network or runtime execution.

- [ ] Write RED using actual synthetic snapshot/converter -> run_prospectus_ingestion -> checked bundle -> prepare_rule_candidates; assert exact field cell/page/version support, inactive flags and the retained unresolved XX999 blocker. Changed candidate/raw/settings hashes, foreign cell/page/version, missing/ambiguous field provenance and policy/private bundle misuse must never acquire usable rule support.
- [ ] Map only explicit extractor field ownership/provenance and corresponding actual raw normalized cells/text. Reuse installed evidence/locator helpers. Whole-row or whole-chunk spans cannot stand in for unrelated individual fields. Retain missing/unlocatable/ambiguous field support as compiler blockers; malformed/forged ownership or source binding refuses. Derived category/year/semester/program/elective fields without direct support remain blocked. Retain raw source text and documented correction decisions without inventing approval.
- [ ] Run focused RED/GREEN and one combined synthetic end-to-end acceptance case. Record a documented library command for an external checked prospectus bundle; outputs remain external JSON review data and source hashes remain unchanged. This closes the cross-plan interface gap, not corpus accuracy/source authorization.
- [ ] Root focused acceptance, explicit staging of the three paths, local draft commit, frozen read-only archive, separate fresh Spec then Standards. Preserve existing unrelated review debts and exact recheck limits.


## Dispatch boundaries
No descendants/commits/staging: root accepts and commits, then separate fresh Spec and Standards. Read owner extractor-implementer.md and S/subagent-driven-development/implementer-prompt.md as Markdown only; use actual Codex. Every PowerShell first selects candidate worktree; all paths absolute. Process-only PYTHONPATH must equal the candidate worktree; assert module origins. READ_ONLY_CODEX_USAGE.ps1 changes caller cwd, so explicitly restore after it. System py -3.13 -B; no-bytecode/offline; pytest no-cache with unique external basetemp. No install/download/dependency/lock/global interpreter changes. No protected refs or owner checkout writes; no adoption/merge/PR/push/attribution. Routine fixture corrections within scope need no new permission pause. Save exact commands/exits/RED/GREEN externally under delivery_execution_20261011. Actual Codex quota stop new batches>=85 either window; save promptly>85.

## Existing ownership helpers to inspect, not reimplement
Finalized courses retain row provenance and _source table_index,row_index,column_group; field ownership is present in sections.CourseCandidate FieldCandidates, but parse_curriculum_evidence drops those candidates in its return projection. Inspect existing normalized evidence, detect_column_groups/tokenize_table/build_curriculum_sections/_assemble_section_candidates and _candidate_to_raw_course to regenerate exact direct ownership from checked raw conversion and match exact candidate course values. Do not treat union row cell IDs as individual-field support. Do not modify protected extractor helpers; missing/ambiguous or semantically repaired support remains a blocker until explicit review evidence exists. SourceBBox.origin and actual captured page sizes must be retained; as_evidence_dict omits origin, so do not assume TOPLEFT. Derived category/term/program/elective without direct support stays blocked. Guard against ownership that points at a legitimate but unrelated cell.

Exact shared spec/plan directory: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\unified_ingestion_design
Exact compiler spec/plan directory: E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_takeover_2026-10-10\phase6_prologifier

Task2 producer reports captured PDF geometry is retained in conversion metadata pdf_page_sizes keyed by 1-based physical page string, [width,height] points. Loader validates contiguous finite positive geometry and raw Docling page-size agreement with 0.01pt tolerance. Verify actual accepted implementation at dispatch; use this hash-checked captured geometry for field spans, never infer from a whole chunk or blindly trust raw converter page size.
