# Phase D F1 specification review

Verdict: APPROVED

Reviewed base: 53e3c000958eae9cf4e12e197a6e54b7cc7b2e84
Reviewed tip: 597e8c0289b8c090edf494248a9bd3fedad6aeb4
Worktree: C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d
Review seat: independent read-only specification review, performed without subagents.

## Scope and evidence

Read task-d-publish-brief.md, task-d-publish-preflight.md, approved_execution.md, task-d-publish-review-package.md and task-d-publish-report.md. Read the requesting-code-review/code-reviewer.md template, including its reasonable-user expectations and Declined to judge requirements. Inspected the actual committed diff and surrounding publisher, pipeline, loader, identity and batch implementations; searched all publisher/verifier/loader callers. Inspected all changed tests, their shared fixtures and the unchanged public loader callers. Production/tests on disk match the reviewed tip.

The approved F1 brief and reused-cache clarification supersede the older cache-first publication proposal. They require detection of mixed file generations; they do not require an atomic set or unconditional invalidation after byte-identical replacements.

## Strengths and requirement verification

- Separate exact byte bindings: publish.py:115-157 validates publish-v2, nonempty output maps, explicit main membership, separate complete PDF cache pairs and matching embedded cache maps. pipeline.py:334-349 forwards both loader-provided hashes into main run_identity before serialization. The manifest preserves that same identity (publish.py:233-242). No expected cache digest is obtained by reopening the live pair.
- Captured reused bytes: loader.py:347-381 verifies and parses the same raw bytes and captures metadata bytes with their digest. pipeline.py:337-346 refuses partial snapshots and stages those exact bytes for reused caches, retaining cache=reused. Converted stage files are checked against captured digests by publish.py:230-245. Restoring a later-tampered cache to the captured pair matches the explicit preflight clarification.
- Publication order: pipeline.py:228-259 emits essentials/prolog/rag/csv/optional markup/main. publish.py:249-250 replaces that output list, then raw cache JSON and metadata, then the manifest. Tests assert both the full order and markup immediately before main.
- Failclosed verification: read_manifest and verify_published share structural validation (publish.py:160-173); v1, empty/malformed maps, invalid hashes/run keys, overlapping case aliases, unsafe Windows/Posix leaf names and unsupported kinds are refused. Each listed file is read once and those bytes supply digest and parse checks (publish.py:176-202). Resolved escaping leaves are refused. Main identity, cache map, input digest, conversion identity/settings and metadata raw digest are crossbound; malformed raw/main/meta JSON, unreadability and missing files fail verification. NonPDF review input requires cache_files={}. Batch skip uses this verifier after identity/audit checks (batch.py:162-197).
- Deletion boundary: publish.py:252-257 only unlinks omitted known companions derived from this output stem. Previous manifest paths are never deletion candidates, so arbitrary prior cache/neighbor/escaping entries cannot widen cleanup. Cache, main and manifest are not in the allowlist.
- Failure coverage: tests/test_prospectus_publication.py:340-403 injects before/after exceptions at all nine replacements for changed PDF, changed settings, force reconversion and identical-raw variants, with changed or identical companions. A passing old manifest requires the complete previous byte set to remain unchanged; mixed sets after changed main fail, and a final replaced manifest verifies the new set. This directly covers the new-PDF/identical-raw and identical-companion case hidden by the earlier nonce fixtures. Pre-publication conversion/parser failures and changed staged caches preserve previous published bytes (lines21-57,280-297). Partial loader snapshots also preserve them (lines466-482).
- Additional regression coverage: reused pair/raw/meta modification and deletion after parse restores captured bytes (publication.py:300-332); alternate valid cache generation cannot silently rebind a previously parsed main (lines449-463); same-read digest/parse is verified (lines485-503); cache crossbinding and malformed/missing pair cases are covered (lines420-446,506-520). Batch cache corruption/deletion and v1 refusal assert exact skip reasons (test_prospectus_batch_skip.py:187-213). Unchanged verified batch skips retain artifact bytes/mtimes and avoid conversion.
- Compatibility: loader.py:497-509 still returns (document, raw_json_path), as CLI/TUI callers expect. The publisher retains six positional arguments with a keyword-only cache_hashes addition. common.py:8 remains palsu-prospectus-v3.2. CLI names, review/approval behavior and final filenames were not modified. Existing authority assertions remain after supplying the now-required complete cache fixture; the OCR fixture now declares the same settings at both identity boundaries.
- Documentation: committed extractor_split_progress.md and the external implementation report explicitly document main-before-cache v2 and republishing captured reused bytes, with the non-atomic limitation.

## Issues

Critical: NONE.
Important: NONE.
Minor specification findings: NONE.

No confirmed F1 defect or unjustified requirement deviation was found. No runnable reproduction was needed because no unresolved implementation suspicion survived source/test inspection.

## Validation evidence

Read final task-d-publish-final-fullsuite.log: 910 passed, 13 subtests passed, 3 warnings.
Read final task-d-publish-final-comprehensive.log: 916 passed, 13 subtests passed, 5 warnings.
Read task-d-publish-selftest.log: 80/80 checks passed.
These are inspected implementer-run evidence, not tests rerun by this reviewer. No broad suite or dependency synchronization was performed. The 180-case interruption matrix is real parameterized coverage (9 steps x 2 before/after x 2 companion variants x 5 input/conversion variants).

## Unresolved suspicions

NONE.

## Declined to judge

- Multiple concurrent writers, durable recovery from sudden disk corruption and authentication against an actor rewriting every artifact: the approved preflight explicitly preserves one-writer, file-by-file detection and excludes locks/rollback/authenticity guarantees.
- Remaining F2 filtering, F4 CSV/batch LF, S1 compact/default paths, S2 contextual skip and S4 prompt/toggle work: explicitly queued separate tasks; their preexisting behavior was not changed by F1 and is not an F1 regression. This approval does not declare them complete.
- F5 evidence reconstruction, real 44-document semantic comparer/counts, trial01/16/33, decision record, Task10 and later-phase/human gates: parent-owned remaining phase gates outside this publication fix; final synthetic publication tests do not establish those results.

## Assessment and final Git state

Ready for the next independent quality review: YES. F1 implementation satisfies the supplied publication specification and clarification, including the unchanged-output edge case and exact parsed-cache generation binding. This is specification approval of the stated commit range, not authorization to merge dev or declare Phase D complete.

Final HEAD remains 597e8c0289b8c090edf494248a9bd3fedad6aeb4. git diff --exit-code HEAD -- backend tests is clean; git diff --cached --name-only is empty. Overall git status --porcelain=v1 has exactly one expected coordinator logging change: M plans/plan_current_progress/extractor_split_progress.md. The root coordinator reported that it appended the post-commit review-active checkpoint. No review changes were made to repository files, index, HEAD or branch state; production/tests remain immutable at the reviewed tip. The review report is written only in the external approved scratch root.
