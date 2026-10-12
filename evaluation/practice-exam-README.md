# Development practice exam

The practice exam is a small question sheet plus a separate answer key. It records the expected answer/control and exact original-source evidence for each question. It stays in the development split; final benchmark questions are never used for this workflow.

`evaluation.practice_exam` is a standard-library checker, renderer and fixed-key grader. Original PDFs, real institutional gold passages/answers and generated reports stay outside Git. Committed unit fixtures are invented and confer no source authority. The packet is `candidate`, with `source_approval: not_claimed`; the tool cannot promote it to verified institutional evidence.

The current original-backed packet and readable outputs are at:

```text
C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-dev-exam-20261012/practice-exam.json
C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-dev-exam-20261012/exam/questions.md
C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-dev-exam-20261012/exam/answer-key.md
C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-dev-exam-20261012/exam/validation.json
```

Twelve candidate cases, eight scenario families, four English/four Filipino/four Taglish; nine source-answerable cases, one curriculum clarification and two insufficient-evidence controls. The packet compares the printed BSCS2018-2019 sheet with the explicitly **proposed**2025-2026 BSCS sheet. It does not assert that the proposal has been approved or applies to a student. Categories: prerequisites5, enrollment2, academic standing4, grades1; discipline is not covered.

## Validate and export

From this worktree:

```powershell
$sourceRoot = (Resolve-Path -LiteralPath 'backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/PalSU Undergraduate Prospectus Website Dump').Path
python -m evaluation.practice_exam --exam C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-dev-exam-20261012/practice-exam.json --source-root $sourceRoot --output-dir C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-dev-exam-20261012/exam
python -m unittest tests.test_practice_exam tests.test_practice_exam_cli -v
```

The checker verifies actual PDF byte hashes, source-root path containment, physical-page bounds, page coordinates, source/version identity, locator references and the digest of the manually transcribed excerpt. Question families remain in dev. It refuses final-split input, approval claims, answerable cases without supporting evidence, and curriculum clarification without contrasting editions.

Bounding boxes use PDF points with a top-left origin. Physical page numbers identify PDF pages; printed labels identify printed pagination and can differ. Excerpts are manual readings from original PDF renders; table separators are added. Hashing an excerpt detects mutation, but does not automatically prove that its text or answer is correct. Source page counts/sizes and semantic row/column locators are authored inspection metadata, not a fresh PDF-parser measurement by this checker.

Outputs are refused inside any Git repository/worktree, and never overwrite an exam, observation or original-source input. Existing symlink/hardlink output files are refused before any writes. An ungraded export refuses a destination containing an older `grading.json`; use a fresh output directory to avoid carrying forward a stale score.

## Grade recorded responses

Supply a separate external JSON object keyed by case ID:

```json
{
  "dev-fiction-prereq": {
    "answer": "FICTION1.",
    "status": "answerable",
    "citations": [{
      "version_id": "ver-fiction",
      "byte_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "page": 1,
      "locator_ref": "pdf:p1:row:FICTION2:prerequisite"
    }]
  }
}
```

This example is invented; use IDs and source references from the actual external exam. Accepted control statuses are `answerable`, `needs_scope` and `insufficient_evidence`; these describe the practice-exam answer expectation, not runtime release/calibration status.

```powershell
python -m evaluation.practice_exam --exam C:/path/outside/git/practice-exam.json --source-root C:/path/to/originals --output-dir C:/path/outside/git/observed-run --observations C:/path/outside/git/recorded-answers.json
```

Answers are matched only against explicitly authored acceptable variants, with NFC/case/whitespace normalization. Numbers, negation and punctuation are retained; this is a deterministic fixed-key check, not semantic grading of unrestricted prose. Answer, control and source accuracy are reported independently and by language/category. Both cited editions are required for a comparison/clarification; optional background references cannot substitute for supporting sources. Missing responses fail. A correct answer with a wrong source/edition/page/row also fails. CLI exit2 means supplied observations have failures; exit0 without observations means source validation/export only.

The tool never manufactures responses from its answer key. Key replay or mutation tests verify the checker only; they do not measure model quality. The current packet has no actual retrieval responses or grading score. Before measuring real Phase05 retrieval, independently review the answer/source labels, map semantic row locators to the production ingestion span/cell identities, and use actual matching SEA-LION/runtime retrieval observations. No corpus activation, shared database migration, API or LLM answer generation is included.
