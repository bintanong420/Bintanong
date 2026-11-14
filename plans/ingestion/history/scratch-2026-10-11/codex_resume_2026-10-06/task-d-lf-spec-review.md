# Phase D F4 LF independent specification review

Verdict: APPROVED
Review seat: /root/d_lf_spec (independent, read-only specification review)
Base: 4a0cdb794a337b9cc91846d16585478c3bb5fde0
Tip and observed HEAD: 52da4aaca7d734e83054b1ecd39221ac09302a3b
Worktree: C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d

## Requirements and evidence inspected

Read task-d-lf-brief.md, task-d-lf-report.md, task-d-lf-review-package.md and preflight-ledger.md, including its latest F4 hypothesis correction at lines 42-43. Read the current requesting-code-review/code-reviewer.md reviewer template. Inspected the actual immutable Git diff, changed production writers and tests, the existing publisher helper, Python requirement, and every repository reference to write_manifest, write_review_csv and write_text_lf. Inspected the original LF RED log, bare-CR characterization log, both existing-runtime probes and final focused/full log results. The implementation report was not treated as sufficient evidence by itself.

The current requirement is native QUOTE_MINIMAL. The earlier QUOTE_ALL instruction is explicitly superseded by the ledger correction and does not create a missing-work finding.

## Strengths and spec alignment

- backend/bintanong_tools/prospectus_extractor/batch.py:148-165 preserves the path, parent creation, schema version, timestamp expression, all summary fields and records. Its sole serialization change uses the existing publish.write_text_lf. publish.py:55-57 writes UTF-8 bytes directly, preventing Windows newline translation without changing JSON formatting or adding a trailing newline.
- backend/bintanong_tools/prospectus_extractor/views.py:40-51 preserves the exact 23 columns, utf-8-sig BOM, newline="" file opening and default minimal quoting. Only DictWriter's record terminator becomes LF. Lines 57-82 preserve every row value transformation, including zero-valued page and unit fields.
- The real call paths share these writers: batch.py:288 writes the batch manifest and pipeline.py:251-253 writes the staged CSV. No caller-specific workaround, schema, artifact name or default output-root change was introduced.
- tests/test_prospectus_batch_skip.py:190-208 uses the actual writer and raw bytes, checks Unicode, independently parses JSON, checks the exact public keys/schema/summary/records and bounds the generated timestamp. Restoring the old Windows text writer would fail the byte assertion.
- tests/test_prospectus_publish.py:27-63 uses the actual CSV writer, asserts BOM and Unicode bytes, removes only the known embedded title bytes before checking record separators, and parses with newline="" to preserve field data. The independent expected row specifies all 23 fields in order and exact values. Comma, embedded CRLF and bare CR without comma are covered. Restoring default CRLF record separators would fail this regression; stripping embedded CR/CRLF would fail raw-byte and parsed-value assertions.
- The diff retains stdlib minimal quoting and does not normalize field contents. The main and GUI-review runtime probe logs both show Python 3.13.5 quoting bare CR and preserving it through CSV parsing. backend/pyproject.toml:4 restricts the backend to ==3.13.*.

## Issues and concrete reproductions

Critical: none.
Important: none.
Minor: none required for the F4 specification.
No new defect was identified, so no additional reproduction or broad test run was justified.

## Verification provenance and boundaries

The original task-d-lf-red.log contains three authentic raw-byte assertion failures: Windows CRLF in batch JSON and both original CSV cases. task-d-lf-cr-red.log contains three passing cases and is correctly described as an attempted RED that passed, not failing TDD evidence.

The saved fresh focused log reports 361 passed, exit 0. The saved fresh main full log reports 956 passed, 13 subtests passed and three upstream deprecation warnings, exit 0. Those runs used the existing main venv and the two approved API/embedding exclusions. I inspected these existing logs rather than repeating the suites. I did not execute the deferred GUI-review comprehensive suite or final D selftest. A saved stdlib runtime probe is not proof of that comprehensive suite.

git diff --check for the immutable review range passed. Commit metadata contains the requested Co-Authored-By trailer. The index was clean. The only observed worktree modification was the expected controller progress checkpoint:

```text
 M plans/plan_current_progress/extractor_split_progress.md
```

No repository, index, HEAD, main checkout, dependency or branch mutation was performed by this review. Only this external review report was written.

## Unresolved suspicions

None within the F4 LF specification. This approval does not extend evidence beyond the inspected code and recorded test boundaries.

## Declined to judge

- S1 default output-root and temporary-path changes: expressly outside this F4 task and absent from its production diff.
- S2 skip context and S4 TUI behavior: separate queued work, unchanged by the LF writer edit.
- F5 historical evidence correction: separate task; only F4 RED/characterization provenance was assessed here.
- Final Phase D gates, complete GUI-review test suite, standalone final selftest and downstream integration: explicitly deferred, not prerequisites for this narrow review verdict.
- Prospectus extraction accuracy against the original corpus: serialization-only change; no extraction/parser behavior changed, and this review makes no corpus-accuracy claim.
- New atomicity, concurrent-writer or rollback guarantees for the directly written batch manifest: not added or changed by replacing newline translation with the existing byte writer; such guarantees were not claimed by this task.

## Assessment

APPROVED for Phase D F4 LF specification at the exact tip above. The two production serialization edits implement the current requirement while preserving public data contracts and embedded field contents. Independent quality review and the remaining Phase D work still follow; this is not final Phase D completion or merge authorization.
