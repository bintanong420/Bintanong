# Complete scratch planning/progress document audit

Snapshot: 11 October 2026, Asia/Manila. Baseline repository commit: `61516754c9d6f32c11956c0145bc96b206fdbb65`. This corrects the earlier selective 13-document import; that import was not an exhaustive migration.

## Result

- Enumerated all 47,476 `.md`, `.markdown` and `.rst` files visible under the specified scratch root, excluding Git internals, node_modules and .venv dependency trees. No symlink following was requested.
- Classified 3,248 planning/progress/review/decision document paths. Of these, 2,596 match current repository text, 432 match Git blobs reachable from published dev history, and 217 missing paths are now represented by 202 distinct verbatim archived documents. Duplicate normalized content maps to one destination. The remaining three paths are two copies of a raw source inventory and a generated course audit, explicitly excluded as source-derived artifacts.
- Also inspected 65 named `.json`/`.txt`/YAML state/plan candidates. Preserved 31 development-state checkpoints/authorizations/status records as Markdown with the original JSON body and source SHA-256. The other 34 are operational/schema/test/other-repository artifacts or generated responses/diffs and remain external.
- No identified development-document candidate remains unmapped. This is document coverage, not a claim to have read every historical narrative, re-run its tests, validated its assertions, or completed the software phases.

## Browse and verify

- [Development-document coverage table](development-document-coverage.csv): every candidate source, classification, disposition, destination and source digest/Git blob where applicable.
- [Excluded tree summary](excluded-tree-summary.csv): counts by scratch directory and exclusion category, with a digest of each sorted path list.
- [Imported historical document index](../history/scratch-2026-10-11/README.md): all 233 added historical documents.
- [Current ingestion status](../CURRENT_STATUS.md): current delivery and remaining work.

For `already-git-history`, the blob is reachable from the recorded dev baseline, not just an unpublished worktree branch. Reproduce its contents with `git show <git_blob>`. Current-file matches normalize CRLF to LF. Historical imports are not new active plans and do not supersede later approvals or current phase metadata.

## Exclusions and audit limits

Generated prospectus pages, review sheets/triage output, test fixtures and temporaries, mirrored agent skills/instructions, third-party documentation, raw source excerpts, raw source inventories/course audit output and session transcripts were classified but not imported. Binary documents, private records, raw conversion JSON/Prolog, model caches and execution logs are not development documentation and remain outside Git. No originals were moved, removed or changed.

The full machine-readable classification is external execution evidence at `scratch/documentation_inventory_20261011/coverage_final_before_import.json`; its SHA-256 is `784c6c374129c185fc75c035aa467b6e44f007199ccae92d7c9ac6fc03250e6b`. The repository tables preserve the actionable document mapping and all exclusion counts without importing thousands of test-output filenames. New files created after enumeration require another inventory pass; this is a timestamped snapshot, not a continuing synchronization service.

## Count reconciliation

| Disposition | Markdown/reStructuredText paths |
| --- | ---: |
| already-current-repository | 2596 |
| already-git-history | 432 |
| archived-in-repository | 217 |
| excluded-generated-source-or-review-artifact | 3410 |
| excluded-raw-source-or-session-transcript | 3 |
| excluded-snapshot-agent-instructions | 3344 |
| excluded-snapshot-other-documentation | 149 |
| excluded-source-derived-inventory-or-audit | 3 |
| excluded-test-output | 37264 |
| excluded-third-party-documentation | 58 |
| Total | 47476 |

Verification for this migration checks source/destination hashes, CSV count reconciliation, published-history blob availability, explicit staged scope and formal ledger validity. It does not grant institutional approval or repeat independent code review.
