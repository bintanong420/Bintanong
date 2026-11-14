# Phase D F1 code quality review

Verdict: APPROVED

Reviewed base: 53e3c000958eae9cf4e12e197a6e54b7cc7b2e84
Reviewed tip: 597e8c0289b8c090edf494248a9bd3fedad6aeb4
Worktree: C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d
Review seat: separate, read-only code quality review after specification APPROVED; no subagents.

## Scope and evidence

Read task-d-publish-review-package.md, task-d-publish-brief.md, the relevant F1 rulings and remaining-work boundaries in task-d-publish-preflight.md, approved_execution.md, task-d-publish-report.md, and task-d-publish-spec-review.md. Read requesting-code-review/code-reviewer.md, including its reasonable-user expectations and declined-to-judge requirements.

Inspected the immutable committed production diff and surrounding complete publisher/pipeline code, loader snapshot/caching/public wrapper implementation, identity construction and shared digests, batch skip flow, CLI/TUI loader callers, every changed test, and their shared fake loader/converter/pipeline/snapshot fixtures. Searched publisher/verifier/loader callers. Confirmed backend and tests on disk match reviewed tip; the sole dirty progress checkpoint is outside this reviewed range.

## Strengths

- Root-cause ownership is coherent. pipeline.py:334-349 forwards the two captured loader digests and puts the same cache map into the serialized main identity. Reused bytes are explicitly restaged, retaining cache='reused'; converted staging is checked against those expected digests. It never substitutes live-cache hashes for the parsed generation. loader.py:347-381 and 470-493 establish where the captured pair comes from. Missing partial snapshots refuse publication instead of inferring content.
- One shared validation boundary serves both read_manifest and direct verify calls (publish.py:115-173). It refuses unsupported schema, malformed/empty maps, unsafe names, case aliases/overlap, invalid lowercase SHA256 digests, missing main binding, and incorrect PDF/nonPDF cache identity shapes. Conversion settings/input/hash crosschecks use the existing identity helper rather than duplicated digest logic.
- Verification is conservative and uses actual file bytes (publish.py:174-205). Each listed file is read once; hashing and parsing use that same value. Main identity must equal manifest identity, and metadata must match PDF identity/settings and the listed raw digest. Missing, unreadable, corrupt and escaping resolved leaves fail closed. This closes the cache-generation gap for batch.skip_check as well as publication.
- Prepublication validation runs before target replacement (publish.py:223-245). The small existing replacement/retry helper remains the sole replacement owner. Pipeline diagnostics and staging cleanup retain intentional error propagation. The approved six positional publication parameters remain; cache_hashes is keyword-only, and public load_document still returns its two-tuple.
- Publication and deletion responsibilities stay narrow (publish.py:249-257). The existing ordered output sequence is followed by raw/meta and manifest. Stale cleanup uses only the five known companions; previous manifest contents cannot expand deletion to caches or neighbors. No transaction, lock, new dependency, or speculative abstraction was introduced.
- Tests exercise the dangerous invariant. test_prospectus_publication.py:340-403 covers before/after every replacement, stable/changing companions, changed PDF/settings, reconversion, and identical-raw variants. A valid previous manifest requires every published byte to equal the previous snapshot; after changed main replacement, the old generation cannot verify. This avoids the earlier nonce-only false confidence.
- Additional tests cover captured converted/reused digests, postparse replacement/deletion restored to captured bytes, staged corruption preserving previous output, partial loader results, alternate valid cache generation, identity mismatches with honest hashes, malformed bytes and same-read behavior (publication.py:250-332,420-520). Batch cache corruption/deletion and old-v1 rejection assert exact skip reasons (test_prospectus_batch_skip.py:187-213). Changed authority/OCR doubles supply the actual newly enforced contract without weakening production checks or authority assertions.

## Issues

Critical: NONE.
Important: NONE.
Minor: NONE.

No concrete F1 regression, root-cause omission, data-integrity defect, unjustified abstraction or material maintainability issue was found. No nit-driven rewrite is recommended.

## Validation evidence

Inspected final external logs directly:

- task-d-publish-final-fullsuite.log: 910 passed, 13 subtests passed, 3 warnings.
- task-d-publish-final-comprehensive.log: 916 passed, 13 subtests passed, 5 warnings.
- task-d-publish-selftest.log: 80/80 checks passed.

These are inspected implementer-run evidence, not executions by this reviewer. No broad suites were rerun. No targeted executable probe was needed because no suspected defect remained after code/caller/test inspection. Synthetic publication tests establish publication consistency, not correctness of real institutional extraction.

## Unresolved suspicions

NONE.

## Declined to judge

- Concurrent writers, whole-set atomic visibility/rollback, and durable recovery from filesystem corruption: approved preflight explicitly preserves one writer per stem and detectable file-by-file publication. A coherent previous set can still verify after byte-identical early replacements; no new lock framework is required.
- Artifact authenticity against an actor rewriting main, cache and manifest together: manifest integrity is a local coherence check, and authentication of a completely forged set is explicitly outside F1.
- F2 directory/diagnostics filtering, F4 CSV/batch LF, S1 compact staging/temp/default-root path limits, S2 contextual skip safety, and S4 prompt/toggle behavior: approved separately queued work; existing surrounding behavior is not changed by this F1 diff. This review does not mark those tasks complete.
- F5 reconstruction, real 44-document comparer/counts, trial01/16/33 evidence, decision record, Task10 handoff and subsequent phase/human gates: parent-owned phase gates outside this committed publication fix.

## Assessment and actual Git state

Ready for the controller to continue the Phase D queue: YES. Exact cache generation binding, failclosed verification, ordered detectable publication and allowlisted cleanup are implemented in the existing owners, with meaningful regression coverage. Approval applies only to the stated F1 range; it does not declare Phase D complete or authorize a dev merge.

Final HEAD: 597e8c0289b8c090edf494248a9bd3fedad6aeb4.

git diff --exit-code 597e8c0289b8c090edf494248a9bd3fedad6aeb4 -- backend tests: exit 0, no output.
git diff --cached --name-only: empty.
Actual git status --porcelain=v1:

    M plans/plan_current_progress/extractor_split_progress.md

This is the expected coordinator postcommit checkpoint and is outside the immutable reviewed range. No repository/index/HEAD/branch/worktree changes were made by the reviewer. Only this external report was written.
