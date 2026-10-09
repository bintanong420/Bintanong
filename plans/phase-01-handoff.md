---
artifact: phase-handoff
phase: 1
status: complete
plan: plans/phase-01-source-governance-contracts-plan.md
final_commit: ee02fd14b4622c38fd432177d5357736dfc77006
next_phase: 2
completed_at: 2026-10-08T21:23:39+08:00
---

# Phase 1 final handoff

Nothing here is institutional approval.

## Exit-gate evidence

The software exit covers governance vocabulary and ten shared contracts, institutional/private reference boundaries, evaluation grouping/splits/rubrics, and one pending-source document/chunk/synthetic-rule/case trace. It does not complete the source-backed benchmark or authenticate institutional authorization.

| Requirement | Evidence | Boundary |
|---|---|---|
| Governance vocabulary/state transitions | knowledge/manifests/governance-vocabulary.json, transition evidence, four schemas, synthetic examples, package/test-local parity | Declared recorder roles and authorization objects are not authenticated office credentials |
| Ten contracts | backend/bintanong_contracts; inventory/contracts decision records | Isolated contracts/adapters; runtime API, embedding and tools packages unchanged |
| Institutional/private separation | Namespace, reference, session, privileged-state and register-binding regression tests | No session endpoint, persistence, retention/deletion worker or real private-input processing implemented |
| Exact trace links | evaluation.traceability; committed executable synthetic example and external BSBA-HRM exercise | Source verification/content review pending; approval not_requested/null; rule/case synthetic; no policy support claimed |
| Groups/splits/rubrics | 21 synthetic dev cases, 14 groups, no findings; deterministic split/freeze machinery and five rubric axes | No final set, final freeze or real system-scored run |
| Independent review | Spec: 3 Medium, 0 High; three confirmed inputs repaired at shared boundaries and root reproducers closed | Standards: one Medium, zero High; malformed citation primitives repaired with shared gold-span/reference checks. All four confirmed findings closed by regression tests/root reproductions. No independent re-check was requested because neither axis found a High |
| Authorized final coverage | NOT MET: 0 verified final cases, 0 Taglish; target >=50 Taglish, >=10 per category | Source-backed independent review/authorized coverage missing; never fabricated |

Task 4 uses loader.load_from_raw_json and pipeline.build_payload on a copy of the cached BSBA-HRM Docling JSON, then chunk_adapter.adapt_chunk with 612x936 page sizes from that JSON. One of 61 built chunks was checked against its own four cached table cells on physical page 1/table 0. Its exact spans, chunk content hash, complete synthetic rule draft digest and development-case digest are bound. The source version/register and chunk content-review state stay pending; a separate content_check records only the maintainer's cached-extraction check.

The original PDF/cache/copy hashes remained unchanged, but the legacy cache has no conversion byte identity: association with the hashed PDF remains pending. Original PDF content/conversion correctness, issuer/scope/effectivity and authority were not verified. The printed passage does not substantiate the fictional COURSE-A/B prerequisite; the case has empty gold spans/rules and null institutional applicability. Real trace/cells/input hashes/paths/reproduction scripts stay outside Git. The scratch builder bypassed candidate Prolog generation once; actual rule generation/execution calls were zero.

## Fresh verification

Evidence batches outside Git: codex_phase1_resume_2026-10-08 (baseline/full/final_full.txt), codex_phase1_task4_2026-10-08 (trace, source-cell checks and mutations), codex_phase1_review_2026-10-08 (archives and independent reports), codex_phase1_specfix_2026-10-08 and codex_phase1_standardsfix_2026-10-08 (red/green/mutation logs).

Root ran the broad gates directly on system Python 3.13, with disabled pytest cache and basetemp outside Git.

| Gate | Expected | Actual |
|---|---|---|
| Resume baseline e844cad | 3927 passed, 1 skipped, 13 subtests | 3927 passed, 1 skipped, 8 warnings, 13 subtests; exit 0 |
| Task 4 full suite | Baseline plus trace checks | 3978 passed, 1 skipped, 8 warnings, 13 subtests; exit 0; 136.81s |
| After Spec fixes | Full suite passes | 3991 passed, 1 skipped, 8 warnings, 13 subtests; exit 0; 136.05s |
| Final citation repair plus ledger | Full suite passes | 4035 passed, 1 skipped, 8 warnings, 13 subtests; exit 0; 198.12s |
| Jsonifier self-test | 80/80 | 80/80, exit 0 |
| Task 4 focused trace/examples/docs | Pass | 118 passed, exit 0 |
| Spec archived focused tests | Independent actual counts | 1284 passed: 199 evaluation, 378 fix-pass-3, 707 parity/governance |
| Standards archived focused | Independent actual counts | 1500 passed |
| Fixed evaluation focused | Pass | 272 passed, exit 0; rubrics/case 151 passed; final docs hygiene 57 passed |
| Critical Task 4 mutations | Critical guards fail tests when removed | 23 killed across final full pass plus targeted span-guard survivor run; scratch only |
| Spec-fix mutations | Critical repaired guards fail tests when removed | 12/12 killed, scratch only |
| Citation-fix mutations | Critical reference guards fail tests when removed | 12/12 killed, scratch only |
| Development corpus | No integrity findings; honest coverage | 21 cases, 14 groups, dev 21/final 0; findings[]; target NOT MET |
| Synthetic/real trace CLI | Valid with pending/synthetic state | Both valid, exit 0 |
| Protected packages and dependency/lock files | Zero diff against ec0eac7 | Zero diff |
| git diff --check / attribution | 0 errors / 0 matches | 0 errors / 0 matches |
| Owner checkout | Exact 9 known entries retained | Exact 9 entries before/after every implementation/integration commit; no owner writes |
| Phase ledger | Valid, advancement refuses until handoff | State valid, can-advance exit 0 and next phase 2; clean committed state rechecked after the ledger commit |
| Linux/macOS/containers/browsers/exact tokenizer | Only claim runs actually performed | NOT RUN |

Representative exact PowerShell gate commands (substitute the recorded scratch batch name):

```powershell
Set-Location 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-1'
$t='E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_phase1_resume_2026-10-08'
New-Item -ItemType Directory -Force -Path $t | Out-Null
py -3.13 -m pytest -q 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-1\tests' -p no:cacheprovider --basetemp "$t\bt_final_full"
py -3.13 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-1\backend\bintanong_tools\bintanong_jsonifer_prolog\bintanong_prospectus_jsonifier.py' --self-test
py -3.13 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-1\.agents\skills\bintanong-phase-handoff\scripts\phase_state.py' validate --repo 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-1'
py -3.13 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-1\.agents\skills\bintanong-phase-handoff\scripts\phase_state.py' can-advance --repo 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-1'
git -C 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-1' diff --check ec0eac7..HEAD
git -C 'C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-1' log ec0eac7..HEAD --format=%B | Select-String 'Co-Authored-By|Generated with'
```

## Commits, versions and digests

- Formal start f7b7752; consumer inventory `664beb5`; governance c7e298f.
- Shared contracts b580064 through d4ccbaa; review hardening/fix passes documented in phase-01-contracts.md and the superseded checkpoint. Fix pass 3 starts `03a7c61`; the previous High transition-from issue was independently closed before this takeover. The final Spec review included fix pass 3 and reported no new defect there.
- Evaluation `058c164` through `dd4d7e2`; Task 4 `b8b5014` and checkpoint `ae383ca`; Spec fixes `9bfcada`; citation repair ee02fd1.
- final_commit names the last implementation tip after the review repairs. Independent reviews pin ae383ca (Spec) and 9bfcada (Standards); no further independent re-check was run because both reported only Medium findings. The subsequent handoff commit changes ledger documentation only; no self-referential hash or history rewrite is used.
- Actual installed environment: Python 3.13.12, Pydantic 2.13.4, Docling 2.129.0, docling-core 2.97.1, pytest 9.0.3, FastAPI 0.136.3. Declared pins are separate; no dependency installation/synchronization or pyproject/lock change occurred.
- Schema versions are the versioned contracts/vocabulary in the consumer/contracts decision records; evaluation case/report/freeze/run/traceability v1. Prospectus payload palsu-prospectus-v3.3, chunker palsu-chunker-v1, estimate-v1 remains an estimate.
- Committed LF blob SHA256: governance-vocabulary.json: 14cb7c5aa2faf61e018bf7ab2d07a1b5460d36c223f1d8c30b672ec134c35a42; evaluation/case.schema.json: 8f978762f1bb026935bac522ac39371b72a89a8eb6cd5833100afd16dc61a5ba; traceability-synthetic.json: c179313a8c451297135801b00c87cc9084df35dc98b0f03cf17177ff9c4764a5.

The original phase-plan body preserves its startup/checklist wording; its completed frontmatter, this handoff and INDEX are the current state. Prepared Phase 2 prose is historical preparation and does not authorize execution.

## Compatibility, deviations and unresolved risks

- Zero diff under backend/bintanong_api, bintanong_embedding, bintanong_tools, backend/pyproject.toml, backend/uv.lock and root uv.lock against ec0eac7. Runtime legacy Direct remains an owner decision; adapter refusal does not change routing code.
- Traceability remains an integrity exercise, not a claim of actual prerequisite/rule support. Cached extraction association/content verification gaps and the three textless-span layout chunk rejections remain documented.
- Four evaluation findings were fixed at shared boundaries: normalized ordered whole-word final-text containment before Jaccard; non-null declared applicability version resolves and matches all supporting gold versions; all repeated IDs excluded from coverage and refused by freeze; shared strict reference primitive validation before citation scoring. Nullable/multiple-version scope remains a declaration; the hash-only registry cannot authenticate institution, edition, issuer or reviewer. Long semantic paraphrases require reviewer checks.
- Namespace scans are conservative ID/reference checks, not a semantic private-text detector; known filename false positives and raw-text hash retention require owner rulings. Session retention/deletion and authenticated authorization are future runtime work.
- Rubric claim matching is normalized exact annotation matching; it is not a deployed semantic judge. Lexical near-duplicate grouping needs author/reviewer assignment for cross-language families.
- Authorized source coverage, scope/effectivity evidence, 50 independently verified Taglish final cases, CSG documents, ten scanned-document references and real phone photographs remain pending.
- Owner decision lists remain open: phase-01-source-governance.md (9 items), phase-01-contracts.md (29 items), phase-01-evaluation.md (8 items). No owner policy ruling was fabricated. Phase E/GUI/B2/trial decisions remain in their parallel handoffs/status records.
- Parallel integration/phase-e-0810 is local at `3e19bd3`, excluding Phase 1; fresh course/audit comparer 44/44 identical and full 1674 passed/1skip/13subtests. Its exact payload allowlist ruling and missing saved GUI interpreter gate remain pending; system GUI 407 passed does not replace that gate. Integration report is outside Git. dev/origin/dev unchanged; no push/PR/merge into dev.

## Next-phase prerequisites and stopping point

After the final ledger validates and can-advance permits2, stop for the owner's explicit go before creating a Phase 2 plan. Start from plans/phase-02-document-ingestion-preparation.md; its old ready-state wording is historical preparation, not a current ledger pointer.

The first proposed batch is read-only inspection tooling for the 78 original paths, with reports outside Git and no source-root writes: pages/native-scanned-mixed/language/tables/labels/health/duplicates. Harden or retire ingest.py's silent regex fallback first. Inspect historical Docling helpers before using them; reuse the safe extractor/Docling stack. Handbook/USG/election/Charter/PPTX/JPG/form candidates follow the approved plan. No source approvals, embeddings or executable Prolog. Source activation and final benchmark claims still require authorized evidence and independent source-backed review.

Phase F, OCR branch integration, GUI manual acceptance and owner trials remain separate owner-go work. The owner alone cleans checkout strays, moves dev and pushes after accepted integration gates.