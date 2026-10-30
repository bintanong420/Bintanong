# Test-suite audit and consolidation results

[Approved plan](2026-10-30-test-suite-audit-plan.md). Worktree p12, branch `p12-evaluation-harness`.
Baseline `3ad52e5`; final test code `4ed03dc`. **Tasks 1–7 complete; ready for external Claude review.**
Last expanded audit snapshot before condensation: `4ed03dc` (`git show` preserves its history).
Evidence root **A**: `C:/Coding-projects/bintanong_workspace/audit-evidence/p12-test-audit-20261030/`.

## Task status and decisions

| Task | Result |
| --- | --- |
| 1 Baseline | 7,365 collected; 7,357 passed / 6 skipped / 2 xfailed / 1,608 subtests; four exits0 (`db643c0`) |
| 2 Measure | Frozen inherited roster:105 collecting files /4,646 cases; complete per-test lines/arcs report |
| 3 Quick wins | One identical ledger duplicate removed; zero-test evaluation helper renamed (`4e80c56`) |
| 4 Contracts | 25 ->11 files; all2,032 cases retained (`f071293`); checker binding corrected (`4ed03dc`) |
| 5 Other redundancy | One covered OCR text-format case removed with oracle/mutation proof (`0f7849b`) |
| 6 Tool decision | Owner: "Keep all three tools and their distinct tests"; no tool retired |
| 7 Verify/report | 7,355 passed / 6 skipped / 2 xfailed / 1,608 subtests; four exits 0; coverage preserved |

Owner approved **coverage 7.17.0 + pytest-cov 7.1.0 in the evaluation venv only**; pytest 9.1.1 unchanged.
No dependency/lockfile or model changes. Owner subsequently replaced full-suite-after-each-commit with
**focused checks during audit; one full suite at the end**. The intermediate quickwins full run was stopped
at that instruction; its partial logs are not claimed as full-suite evidence.

The GUI/OCR bench/prospectus fixer are offline ingestion/data-preparation tools. Baseline inherited cases in
those families total1,787; final1,785. Their functional checks are reported separately from live runtime evidence.
Contracts serve shared boundaries; the evaluation harness also has its own role. No default test/CI selectors changed.

## Collected counts

Counts include parametrized cases, not just function definitions. Families are disjoint filename groups;
contracts includes `test_source_governance_manifests.py`. Frozen current-file creation author determines inheritance.
`test_api_auth.py` was recreated by the owner at `b1bc98b`; its former inherited incarnation is excluded.

| Family / role | All before | All after | Inherited before | Inherited after |
| --- | ---: | ---: | ---: | ---: |
| Contracts / shared boundaries | 2,032 | 2,032 | 2,032 | 2,032 |
| Prospectus / offline intake | 1,291 | 1,290 | 1,290 | 1,289 |
| Review GUI / offline review | 407 | 407 | 407 | 407 |
| Evaluation harness | 272 | 272 | 272 | 272 |
| OCR / offline tooling | 100 | 99 | 90 | 89 |
| Other / mixed runtime and tooling | 3,263 | 3,263 | 555 | 555 |
| **Total** | **7,365** | **7,363** | **4,646** | **4,644** |

Collecting files292 ->278; inherited105 ->91. `before-after-counts.json` records per-family file/case counts.
No negative, privacy, scope, security, source-gap or original mutation-survivor test removed.

## Removed tests and retained coverage

1. `tests/test_prospectus_b2_codex_review.py::test_item8_the_untouched_entry_is_still_applied`
   -> retained `test_o1_old_ledgers_still_read_and_apply_unchanged` in that file.
   Identical function AST except name, including signature/decorators/assertion; same module globals.
   Every measured production line/arc is a subset across10 production files. Keep the descriptive compatibility test.
2. `tests/test_ocr_bench_engines.py::test_text_is_rebuilt_line_by_line`
   -> retained `test_the_tesseract_adapter_writes_text_words_and_run_metadata` in that file.
   Same TSV, real parser/formatter and exact `CS 101\nIntro\n` text oracle; retained test also checks words/metadata.
   Only external Tesseract discovery/version/run are stubbed. Every line/arc is a subset in one production file.
   Both tests pass originally and both fail when a process-local mutation removes formatter newlines.

`removal-proof.json`, `ocr-original-pair.log` (2pass), `ocr-mutant-pair.log` (2 expected failures) preserve proof.
The mutation is an ignored pytest fixture, not a production edit. No other test met the removal proof rule.
This does not certify every retained test as indispensable.

## Consolidation and review

Folded 14 fix-pass/survivor files into per-module base/answer/governance/runtime/source/symbolic/adapter files.
Embedding, adversarial, package/schema parity and the independent schema checker remain distinct responsibilities.
Preserved 235 moved test functions, their signatures/decorators/bodies and distinct assertions after explicit binding
renames and exact fixture-matrix expansion. Final 7,363 collected cases map one-to-one, apart from the two proven removals.
`contracts_fixtures.py` holds13 exact path/ID/prose matrices; all16 substitutions preserve values/order, including
separate model/schema ID variants. Original source and mutation rationale remain in Git and `contracts-originals/`.

Fresh read-only Codex review additionally checked50 moved helper ASTs,235 mapped functions and16 matrix uses.
It found a P2 global rebinding: survivor `VOC=base.VOCAB` overwrote independently loaded checker vocabulary.
A focused probe reproduced12 false checker errors after a process-local production-transition mutation.
Separate `_PACKAGE_VOCAB`/checker bindings restored: RED1fail -> GREEN1pass; contracts2,032pass (8.48s).
Minor stale decision/removal-count wording was corrected. Separate external Claude review remains pending.

Review rulings: executor owns final suite/coverage; historical mutation suite not rerun (no original survivor
removed); remaining-test indispensability is unproven; institutional source correctness is outside this audit.
Normal passing results, coverage/counts and function ASTs alone do not prove global-binding independence.

## Verification and coverage

Python3.13.7: `C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe -X utf8`.
Environment `PYTHONUTF8=1`; pytest always `-p no:cacheprovider --basetemp=A/<dedicated temporary folder>`.
Local `supabase_db_Bintanong` started/healthy; existing Gemma container untouched and unused by the audit.

| Check | Evidence/result |
| --- | --- |
| Baseline full suite | `baseline-results.json`,4 log/XML batches; 7,357pass/6skip/2xfail/1,608subtests, all exits0 |
| Focused quick wins | `quickwins-focused.log`:290pass/1skip; builders' executable AST unchanged |
| Contracts | Before2,032pass; final2,032pass; `consolidation-verification.json`: no missing/extra cases |
| OCR after removal | `ocr-after.log`:98pass/1skip; original/retained tests catch the same formatter mutation |
| Independence correction | `checker-independence-{red,green}.log`: expected fail then pass; full contracts green |
| Final inherited run | `coverage-final-run.json` / `.log`:4,638pass/6skip/13subtests, exit0,407.25s |
| Final full suite | `final-results.json` / `final-N.log` / `.xml`:7,355pass/6skip/2xfail/1,608subtests; all four exits0 |
| Repository checks | Diff whitespace clean; dependency/lock and backend/scripts/evaluation/knowledge trees unchanged |

Complete measured Python scope: **backend/, scripts/, evaluation/** over the frozen inherited roster.
Initial scope omitted root evaluation; corrected with272-case before/after runs (both pass), original tests from
`git archive 3ad52e5` and identical production hashes. Original raw data retained; new path-normalized complete
baseline data includes that supplement. Final coverage is a fresh single run over all91 mapped inherited files.

| Coverage | Before | Final after |
| --- | ---: | ---: |
| Covered statements / total | 14,444 /24,492 (58.9744%) | 14,444 /24,492 (58.9744%) |
| Covered branches / total | 4,631 /9,720 (47.6440%) | 4,631 /9,720 (47.6440%) |
| Previously covered lines/branches lost | — | **0 /0** |

`comparison-final.json` checks exact sets, not only percentages; production Python hashes unchanged.
`comparison-families.json` also finds zero lost production lines/arcs within each of all six families.
Python coverage excludes native SQL/Prolog/JS, schemas and test-local checker code. Those obligations remain
protected by assertions; zero/subset Python coverage is not evidence of uselessness or institutional accuracy.
Complete baseline report:3,009 subset candidates /534 zero-production records, including skipped cases.
Other-family1,226 candidates were triaged by input/assertion differences; full-body normalization found no further
pairs. Examples retained: ledger generator/details vs list/pending state, GUI rollback/call order vs immutability,
and non-finite rejection vs canonical JSON. Corpus/source/private-file and release guards preserved.

## Evidence, boundaries and next action

Ignored evidence under A includes commands, batch lists, collection inventories, per-test gzip line/arc sets,
coverage databases, matrix/move proofs and mutation probes. Use compact `coverage-*-complete.json`/`coverage-final.json`;
initial context-rich `coverage-before.json` is2.92GB. Parallel data basenames were isolated after an initial pre-test
WinError32; failed preflight log retained. No data/corpus originals, private inputs or raw evidence staged.

Commits: `db643c0` baseline, `4e80c56` quick wins, `f071293` consolidation, `0f7849b` OCR removal,
`4ed03dc` checker independence. No push. Phase12 remains complete; Phase13 deployment cancelled.
Context consulted: thesis physical17–18, routing PNG, relevant master1–3/11–13 and phase12 handoff; no scope change.
Final batch passes1,839/1,841/1,837/1,838; skips0/0/4/2; xfails2/0/0/0; subtests344/479/358/427.
Pytest durations237.56/332.73/414.16/395.93s; all exits0. `final-summary.json` verifies sums against collection.
Closure edits are documentation only; relative links/diff/phase-state and existing docs-hygiene checks apply.
Next: external Claude review of local commits. Keep branch/worktree; no merge/push or Phase13 advancement.
