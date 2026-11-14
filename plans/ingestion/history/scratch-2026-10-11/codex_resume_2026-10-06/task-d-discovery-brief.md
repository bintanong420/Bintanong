# D F2 discovery task brief

Base: 597e8c0289b8c090edf494248a9bd3fedad6aeb4. Worktree: C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d.
Scope ONLY F2. Prior F3/F6 and F1 specification/quality approved. Preserve root review checkpoints already dirty in plans/plan_current_progress/extractor_split_progress.md and include them in focused commit.

Read approved_execution.md, preflight-ledger.md (final superseding rulings), task-d-remaining-brief.md, actual scan_inputs/scan_pdfs callers/tests, package-split cross-phase rules and current TDD/verification/implementer skill instructions. PowerShell only; no child agents. Shared scan_inputs must inspect ignored directory components only via path.relative_to(root).parts[:-1], never filenames or absolute ancestors. Remove blanket failed exclusion. Skip actual diagnostic per-run subtrees marked by failure.json, retaining legitimate failed directories and nondiagnostic siblings. No filesystem abstraction/config or unrelated diagnostic parsing.

Regression cases: selected root under failed/FAILED and ignored-looking ancestor; legitimate nested failed without marker; failed.pdf filename; diagnostics including descendants/cached Docling JSON; legitimate sibling beside diagnostic run; explicitly requested JSON; recursive/nonrecursive scanning. Trace alias and batch/TUI callers and fix once.

Save red/green/full logs and task-d-discovery-report.md externally. MAIN_PY=C:/Users/Hawksprey/source/repos/Bintanong/backend/.venv/Scripts/python.exe. No baseline rerun before red. Before commit run red regressions, green focused scan/batch/TUI relevant suite, and full main tests --ignore=tests/test_api_probes.py --ignore=tests/test_embedding_service.py -p no:cacheprovider with external --basetemp. Complete GUI-review suite/standalone selftest deferred to final Phase D gates: label NOT RUN for task, no reused baseline counts. No install/sync; no generated repo artifacts. checkpoint.py after red/green/broad and commit boundaries with active commands/sessions/errors/next action, --progress at own boundaries.

Stage explicit paths. Commit final trailer Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>. Never edit main checkout/switch/push/dev merge/remove worktrees/cleanup preserved files. Parent performs independent spec then quality review. Report exact commit/range/observed results/status/path and remaining fixes; no Phase D completion claim.

Controller ruling: inspect failure.json in candidate parent directories within selected root, including root, never above root. Do not require a literal failed component. Selected failed root/marked-run root must exclude marked runs; any user folder with failure.json is intentionally diagnostic until marker removed. Add explicit selection and unrelated-sibling coverage.
