# Independent progress refresh — 10 October 2026

Fresh checkout: `C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010`, clean HEAD `57b598522cc7ed5d13e40eb8d1bcafede8c9ba1b`, five local draft commits. Read-only estimate; product, Git, archives and originals were untouched and no tests/conversions were run by this estimator. Old estimates are preserved. Numbers are subjective planning estimates, not measured accuracy or institutional/release approval.

## Recommended percentages

| Scope | Estimate | Planning range | What the number includes |
| --- | ---: | ---: | --- |
| Phase 1 accepted software exit | **100%** | Accepted scope | Shared source governance/contracts/evaluation machinery; excludes source approval, final benchmark and private runtime |
| Phase 2 whole seven-task scope | **75%** | **65–80%** | Draft ingestion tools plus still-unfinished original-backed validation, review closeout and handoff |
| Phase 2 prepared implementation only | **90%** | **85–95%** | Tasks1–6 candidate code and essential synthetic checks only; explicitly excludes whole-phase validation/closeout |
| Phase 6 whole master scope | **25%** | **20–35%** | Existing candidate generator/contracts; no new compiler implementation credit |
| Overall ingestion workstream | **70–75%** | **65–80%** | Weighted raw72%; includes remaining human/source validation, privacy recovery and integration |

Phase 2's narrower90% is not90% overall completion. Formal Phase2 remains preparation only; draft commits do not advance its ledger. Overall ingestion is not the entire13-phase platform and not an average of Phases1/2/6. Neither written design receives implementation credit.

## Basis and unchanged arithmetic

W = C:/Users/Hawksprey/source/repos/Bintanong-wt/phase2-candidates-20261010. E = E:/Hawksprey/Documents/PalSU Stuff/Bintanong dataset dump/scratch/codex_takeover_2026-10-10. Relative source citations below resolve against W; external citations against E.

Phase1 retains100% of its accepted software denominator: plans/phase-01-handoff.md:17–27 explicitly limits its exit and records0 verified final/0 Taglish cases. No deployed private-input processing/retention worker exists under that exit (same:23). These exclusions were present in the previous estimate and are not newly removed to inflate completion.

Phase2 retains all seven weights15/15/20/15/15/10/10. Credits are now95/75/80/75/85/60/40, giving **75.5%, approximately75%**, versus previous31.75%. The large increase is delivered Tasks3–6 code, not a percentage target. Task2 retains75 because this refresh supplies no additional original-backed inventory result. Parser95 includes the new partial-result refusal but retains review/platform remainder. Policy80/procedure75 retain original Handbook/Charter conversion, source reading and deferred mutations. Chunks85 retains original-output/integration validation. OCR60 retains actual engine execution, frozen manual references and measurement. Closeout40 retains unfinished independent repair acceptance, whole-phase gates and handoff. Component credits represent remaining effort, not equal-count task completion.

Evidence for that delta: docs/decisions/phase-02-policy-text.md:7–16,22–48; phase-02-procedures.md:7–38; phase-02-policy-chunks.md:11–43; phase-02-ocr-gate.md:7–41. Actual code checks confirm source-bound preflight (backend/bintanong_tools/document_ingest/register.py:58–89), governed external-output pipeline and root manifest last (pipeline.py:19–83), typed chunk/rejection accounting (policy_chunks.py:184–241), captured OCR/metadata publication (ocr_run.py:127–188), and ten-distinct-reference blocking (ocr_gate.py:145–172). These implementations supersede the old estimate's unimplemented Tasks3–6 description; they do not make the formal plan's original-backed exits pass (plans/phase-02-document-ingestion-plan.md:137–140,181–184,207–212,252–255,279–281,336–341).

The separate implementation-only number uses the same first-six-task weights normalized over90; credits95/95/95/90/95/80 yield **92.5%, conservatively rounded90%**. This measures prepared candidate functionality and essential synthetic checks. It excludes Task7, actual institutional corpus, human accuracy, broad/mutation verification, adoption and formal exit. OCR's lower implementation credit retains safe local-model startup limitations and untested actual engine operation; PPTX report-only handling is intentional under the current contract. This narrower90% must never substitute for the75% whole-task estimate.

Phase6 retains weights25/15/25/20/5/10 and credits10/50/50/0/20/20, raw25.5%, rounded25%. The actual existing generator remains backend/bintanong_tools/prospectus_extractor/prolog.py:72–218. Master plans/master_implementation_plan_original_long.md:413–420,435–457,461–463 requires reviewed source-bound authoring, approved reproducible bundles, typed Janus, supported decision semantics and rule-level tests. E/phase6_prologifier/SPEC.md:1–15,64–68 is written design awaiting owner review; it delivers none of those new runtime/compiler pieces. E/unified_ingestion_design/SPEC.md is likewise design-only, with no new ingestion bridge credit.

Overall preserves weights50% born-digital prospectus,20% OCR/photo,20% other institutional ingestion,10% shared foundation. Credits **80/40/70/100** give **72%**, up from63%, suitable short update **70–75%**. Base prospectus80 and OCR/photo40 remain unchanged: policy OCR tooling does not prove prospectus confidence/review, edition matching, photo benchmarks or safe private uploads. Other institutional ingestion rises25→70 because candidate conversion/chunk/register/report tooling now exists; actual Handbook/Charter migration and source validation keep it below the full Phase2 technical estimate. Component ranges75–85/35–45/60–80/100 yield weighted66.5–77.5%, widened65–80 for integration uncertainty. These are planning bands, not statistical confidence intervals. Machine-readable arithmetic and sensitivity are in criteria.json.

## Review state and remaining conditions

E/phase2_candidate_review/SPEC_REVIEW.md:3–5 records PASS/NONE at7fe26c0. E/phase2_candidate_review/STANDARDS_REVIEW.md:3–5,27–49 records FAIL with one Medium M1: generic ingest accepted explicit partial conversion. New HEAD57b5985 retains ConversionResult and refuses errors/non-success before export (backend/bintanong_tools/ingest.py:51–57). Saved controller evidence is48 passed,exit0 in E/phase2_partial_fix/root_acceptance.log and root_acceptance_exit.txt; no test is rerun here. The repair is committed but independently unrechecked. Existing High-only recheck authorization does not grant a new Medium recheck, and these estimates do not convert FAIL into PASS.

Previously known F review closeout/adoption collision and the session Standards High remain. E/phase_alignment/ALIGNMENT_REPORT.md:44–56,65–71 records these separate boundaries; its old Tasks3–6-unimplemented wording is superseded by fresh code above. Private cleanup/crash recovery is still material to whole-ingestion readiness. No institutional source authorization, private-data retention approval or deployment readiness is established here.

To move full scope toward90–95: close review acceptance; approve and then implement the smallest source/version-bound Phase1/2 bridge; run one combined stable synthetic smoke; perform representative original Handbook/Charter/prospectus source-span checks and record unresolved evidence; complete independent frozen OCR references/actual engine measurement; close the private lifecycle High; finish human/domain/source decisions and whole-phase handoff. Keep focused regression checks before local draft commits and consolidate deeper suites at stable checkpoints. Those deferred checks remain work, not optional percentage deductions.95–99% full completion is not defensible from committed draft code alone, and no completion date is promised.

Skipped: no new tests, original conversions, photos, deployments or source approvals. Risk: subjective estimates depend on remaining migration/validation effort; the private lifecycle High and independent repair acceptance remain open.
