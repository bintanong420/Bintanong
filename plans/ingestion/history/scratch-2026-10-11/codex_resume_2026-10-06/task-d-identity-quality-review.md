# Phase D F3/F6 independent code-quality review

Verdict: APPROVED. Confirmed defects: NONE. Unresolved suspicions in this task: NONE.

Reviewed committed range `641523d212839084da03d966ffbfca66c7e83e42..53e3c000958eae9cf4e12e197a6e54b7cc7b2e84` in `C:/Users/Hawksprey/source/repos/Bintanong-wt/phase-d`. This is the independent quality review following the approved specification review, not the later Phase D acceptance gate.

## Inputs and scope

Read the external task-d-identity-review-package.md, approved_execution.md F3/F6 specification, task-d-identity-report.md, task-d-identity-spec-review.md, the repository extractor-reviewer instructions, actual production changes and adapted tests. Traced all repository callers of file_sha256, run_identity, load_document/load_document_result, skip_check and provisional-source verification. Inspected installed Docling converter, pipeline and backend cleanup code instead of assuming the generated adapter was compatible.

## Quality findings

Confirmed defects: NONE. No concrete input or command was found that demonstrates an unintended regression in this range.

- `identity.py:27-53,125-127`: captured bytes are immutable bytes, hashed from the same object stored in the snapshot. There is no caller-supplied digest constructor. Every consuming boundary validates the resolved input path. Direct byte comparison detects equal-size/restored-mtime replacement and propagates missing/unreadable-file errors; it does not accept metadata equality as identity. Path resolution is consistent with the preexisting pipeline/loader behavior.
- `pipeline.py:303-320,350-359`: source verification, run identity and loading share the capture. A source mismatch occurs before output creation. A changed or deleted input refuses publication through the existing staged-failure path. Success and exception exits retain the existing stage cleanup. Snapshot fields are not copied into the JSON payload or batch records.
- `batch.py:223-246,266-279`: each item gets its capture inside the per-item exception boundary, so capture failure is recorded and later items can continue. Skip-check exceptions retain their visible reason and proceed with the existing capture. Successful, failed and skipped items release the batch snapshot reference before the next capture; there is no eager snapshot list. The loader reaches converter creation only after cache reuse fails. The existing shared-converter cache is reused rather than recreated per document.
- `loader.py:412-455`: JSON parsing uses captured data. PDF conversion uses the public installed DocumentStream type, with a fresh BytesIO for each backend attempt and the retained filename. The fallback does not reuse a consumed or closed stream. Installed Docling BasePipeline.execute uses a finally cleanup (`docling/pipeline/base_pipeline.py:106-107`); paginated cleanup unloads the input backend (`:385-391`), and AbstractDocumentBackend.unload closes BytesIO and drops its reference (`docling/backend/abstract_backend.py:45-49`). The suspected normal-path stream-retention leak therefore was not substantiated.
- `loader.py:347-383,471-493`: reused metadata is parsed from the retained meta bytes, and the raw digest is checked against the same raw bytes subsequently parsed. Returned raw/meta digests describe those retained buffers even if the paths are replaced afterward. Converted results retain the exact serialized buffers used for writing. Corrupt-cache miss behavior and conversion-error refusal remain intact; no new silent error fallback was introduced.
- `loader.py:386-390,497-509`: both public tuple wrappers preserve their signature/default/positional behavior and tuple contracts. Package exports, CLI grid loading and TUI loading still call the public loader wrapper. `prospectus.py:18-24` preserves verify_pdf and routes it through digest verification. Internal result field annotations match the evidence/document and path values carried by callers; no new circular dependency or platform-specific production path was found.

The new tests assert externally meaningful byte identity, publication preservation, cache retention, fallback streams, and batch behavior. Existing test edits adjust the fake boundary rather than removing behavioral assertions. The committed file set contains no generated PDF/output artifact, user .gitignore edit, or historical handoff file.

## Evidence and limits

This review independently inspected the committed diff, callers, test assertions and installed library lifecycle implementation. `git diff --check 641523d..53e3c00` passed; final `git status --short` was empty. No runtime test suite was rerun: no issue required an additional reproducer, and the assigned quality-review scope explicitly avoided duplicating the spec review's 336 focused tests, one source test and real DocumentStream probe. Those results and the implementer's 647-test comprehensive result are prior evidence, not newly executed counts claimed by this reviewer.

Full-file snapshot retention and direct comparison use memory proportional to one input (plus conversion/cache buffers). This is the approved snapshot design, not a newly discovered correctness defect. Batch does not accumulate snapshots across items.

## Adjacent work excluded from this verdict

The existing v1 publication manifest does not bind caches; retained-buffer binding and publication-order failure injection are explicitly queued F1. Semantic-map hashing/parsing still use their existing separate reads; semantic-map capture architecture is outside F3/F6. Root-relative discovery, LF batch/CSV output, staging-name ceilings, context-sensitive skipping, prompt wording, corpus gates and final handoff remain their separately queued tasks. Source checking does not lock the source against changes after the prepublication comparison; this disclosed concurrency ceiling is not an atomic-publication guarantee. None is treated as missing required work for this task, and this approval does not close those tasks.

APPROVED
