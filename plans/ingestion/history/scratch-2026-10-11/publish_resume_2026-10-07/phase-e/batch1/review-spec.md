# Phase E Tasks 1–4 independent specification review

Verdict: CHANGES NEEDED.

Scope: committed 1236c9911de6efc60914839642a86b5911185933..3c545630e30f2e388f52880c8c54656d2825d097 in C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-e. Read-only checkout review. Only external scratch reports, reproductions, tests and logs were written. No broad gates, installs, staging, commits, push, owner/dev movement or agents.

Authority: full historical Tasks 1–4, exact phase-e-first-batch-brief.md overrides, .claude/agents/extractor-reviewer.md, docs/decisions/prospectus-rag-provenance.md and latest progress/handoff sections. No applicable filesystem AGENTS.md found in the worktree tree; user AGENTS instructions apply. The requested installed superpowers spec-reviewer-prompt.md does not exist; installed task-reviewer-prompt.md was read as current reviewer guidance. Explicit controller rerun instructions override its generic no-suite-rerun guidance.

## Confirmed specification defects

1. P1 / Important — backend/bintanong_tools/prospectus_extractor/rag.py:94. Word-boundary regex containment does not verify the complete own-field claim. Canonical code CS 101/L accepts claimed CS 101; canonical title Introduction to Computer Science accepts claimed Computer Science; canonical prerequisite CS 100 and MATH 1 accepts claimed raw CS 100. Each produces a course chunk and aggregates, with no rejection. The prerequisite chunk can literally say printed as "CS 100" while source_text contains the full conjunctive requirement. The code normalization fallback at line97 is full equality, but the earlier substring branch bypasses it. Reproduce with test_spec_adversarial.py cases code_suffix, title_subphrase, prerequisite_subphrase. Require complete field equivalence under explicitly supported parser transformations; preserve existing normalized whole-code equality and genuine source-backed banner/title transformations.

2. P1 / Important — backend/bintanong_tools/prospectus_extractor/rag.py:102. Unit raw matching uses the same substring regex, and line105 parses the candidate raw rather than proving equivalence with the complete canonical unit evidence. Canonical printed 3/2 accepts candidate units=parse_units('3'), total_units=3; emitted summary says 3 total, lecture3, laboratory0 although canonical parse_units('3/2') is total5, lecture3, laboratory2. No rejection; aggregates use the wrong3 total. Reproduce test_spec_adversarial.py case unit_fraction_prefix. Check the complete unit-field representation under permitted normalization/footnote handling and derive/check numeric values from that canonical source.

3. P1 / Important — backend/bintanong_tools/prospectus_extractor/rag.py:80. own_role_cells is reused, but its generic ownership contract only removes off-row cells when they are in evidence_ids; this builder filters by table at lines82–83 and proves row ownership only for code at line85. Canonical course CS101 on row1 with blank prerequisite can add the actual prerequisite cell of CS777 on row7 to provenance, claim CS100 and get an accepted chunk with no rejection. This is another real canonical row, not a fabricated cell. Reproduce test_spec_adversarial.py case other_course_row. Require same-row role evidence unless an existing parser-backed continuation relationship proves ownership. Do not rewrite the shared verifier/parser simply to tighten the chunk assertion boundary.

All five repro cases fail the expected-rejection assertion independently. They are confirmed batch defects, not planned Task5–6 omissions.

## Independent evidence

Environment: PowerShell, system py -3.13, PYTHONDONTWRITEBYTECODE=1, worktree cwd above; every test uses no cacheprovider and external basetemp.

Focused command:
py -3.13 -m pytest -q tests/test_prospectus_chunks.py tests/test_prospectus_authority.py tests/test_prospectus_parser.py tests/test_prospectus_course_checks.py -p no:cacheprovider --basetemp "<batch1>\spec-temp"
Observed: 284 passed, 13 subtests passed in15.88s. Retained spec-focused.log. No focused warnings. These counts are independently observed; root broad/self counts were not rerun here.

Adversarial command:
py -3.13 -m pytest -q "<batch1>\test_spec_adversarial.py" --import-mode=importlib --rootdir "<batch1>" --confcutdir "<batch1>" -p no:cacheprovider --basetemp "<batch1>\spec-adversarial-temp"
Observed: 5 failed in0.37s, exit1; each failure is acceptance of an unsupported claim. Retained test_spec_adversarial.py and spec-adversarial.log. Earlier default external collection encountered inaccessible E:\WpSystem\__init__.py; importlib/rootdir/confcutdir corrected the collection boundary without repository changes. spec-repro.py/spec-repro.log also print accepted summaries and source_text for the five initial probes.

Preservation command: py -3.13 "<batch1>\test_spec_adversarial.py"
Observed: prerequisite_phrase and build_hierarchical_rag_chunks have identical function ASTs to base1236c991. Retained spec-preservation.log. courses.py diff preserves elective parsing logic apart from source_item_id; pipeline diff is the permitted minimum document/layout/evidence_ids call-site.

## Verified scope / strengths

chunking.py supplies stdlib identity/content normalization, native origin-aware spans, page grouping, explicit unanchored identity, estimated review budget and packing. Tests cover edition/locator/content/version dependence, filename/dict/line-ending independence, multi-page/native-origin behavior, source_text separation, duplicate IDs, oversized-course rejection and aggregate omission.

Summary paths retain accepted course spans, elective text-item IDs and slot spans, omission metadata and repeated split headers; prerequisite_phrase preserves PhaseC wording. Numeric/context/placement-derived fields and unsourced metadata are labelled; the unsupported negative downstream completeness claim is omitted. The confirmed assertion defects above undermine which members count as accepted, rather than the basic aggregate omission mechanism.

No new dependencies, embeddings, vector writes or source approvals are present in this batch. Task5 hierarchical upgrade and Task6 captured-PDF identity, v3.3, payload rejection reporting and JSONL integration are explicitly deferred and are not defects in this review. Corpus/human/source-owner gates remain separate; no full-corpus accuracy claim follows from these tests. Historical plan is preserved and deviations recorded as authorized.

Suspicions / unconfirmed correctness findings: NONE.

CHANGES NEEDED: complete own-field source equivalence, canonical unit equivalence, and same-row or parser-proven continuation ownership (rag.py:94,102,80).
