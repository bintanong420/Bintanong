# Dataset locations and relocation

Recorded 2026-10-12 from the owner's Phase 05 worktree. Read this guide when resuming source reading, ingestion or practice-exam work; discover files again rather than assuming another worktree contains the ignored dataset.

The current dataset parent is:

```text
C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05/backend/bintanong_tools/bintanong_jsonifer_prolog/dataset
```

The original PDF corpus root passed to `evaluation.practice_exam --source-root` is **one level below** that parent:

```text
C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p05/backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/PalSU Undergraduate Prospectus Website Dump
```

This deep codebase location is temporary; the owner intends to relocate it. No relocation was performed during the exam expansion. Existing ignored originals remain read-only. New originals, conversions, gold answers and raw evidence belong outside Git; do not force-add the existing dataset.

## Observed corpus

All current PDF paths are under `Tiniguiban - Main/<college>/...`. Fresh inventory found 39 PDF paths, across nine college directories:

| College directory | PDF paths | Balanced dev questions |
| --- | ---: | ---: |
| CAD | 1 | 3 |
| CAH | 6 | 3 |
| CBA | 9 | 3 |
| CCJE | 1 | 3 |
| CHTM | 3 | 3 |
| CNHS | 2 | 3 |
| CoE | 4 | 3 |
| CS | 6 | 3 |
| CTE | 7 | 3 |

These counts describe paths, not approved curricula, distinct documents or exhaustive program coverage. College labels follow the actual directory spelling, including `CoE`. One source program per college supplies the bounded exam; CS includes two curriculum editions. Do not infer document content from filenames: one Accountancy-named PDF inspected during this work was a brochure, so the CBA exam uses the inspected HRM curriculum instead.

## Portable source resolution

Exam packets store paths relative to the corpus root, alongside exact original SHA-256/version/page/locator identities. The CLI requires `--source-root`; it has no hardcoded dataset root or automatic environment-variable resolution.

```powershell
$datasetRoot = (Resolve-Path -LiteralPath 'backend/bintanong_tools/bintanong_jsonifer_prolog/dataset/PalSU Undergraduate Prospectus Website Dump').Path
python -B -m evaluation.practice_exam --exam C:/path/outside/git/practice-exam.json --source-root $datasetRoot --output-dir C:/path/outside/git/exam
```

For the future move, choose an owner-approved location outside all Git roots, preserve the campus/college relative tree and original bytes, and pass that new root explicitly. Re-inventory the live PDFs, revalidate hashes/college coverage, and update this guide and the current checkpoint/progress log with the new location. Test coverage proves that a changed root with unchanged relative paths and bytes validates. A newly added college causes an all-college packet to fail validation until its declared coverage and cases are updated.

## External evaluation artifacts

- Original 12-case BSCS version: `C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-dev-exam-20261012/`.
- Balanced 27-case version and source-reading images: `C:/Users/joel/AppData/Local/Bintanong/evaluation/p05-college-expansion-20261012/`.
- Each version has `practice-exam.json` and `exam/questions.md`, `exam/answer-key.md`, `exam/validation.json`.

These locations are outside every Git root. `C:/Coding-projects` itself contains an unrelated Git root, so a sibling evidence directory there is not an acceptable destination. No real retrieval observations or institutional approval are established by exporting or validating an exam.
