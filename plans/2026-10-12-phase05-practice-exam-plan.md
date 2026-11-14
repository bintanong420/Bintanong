# Phase 05 development practice exam implementation plan

Goal: a small practice exam with manually checked original-source answers, reproducible citation/source checks and TDD verification. This continues master section10/Phase05 Task6 under the owner's instruction; it does not approve institutional sources or start Phase06.

Architecture: `evaluation/practice_exam.py` reads an external, versioned development-only JSON packet, verifies original PDF byte identities and gold source locator metadata, renders a readable question sheet/answer key and optionally grades externally supplied observations. Source-derived originals, gold answers/passages and generated reports stay outside Git. Tests contain invented synthetic data and verify checker/grader behavior; the actual exam remains candidate until independent source/answer review.

Existing Python3.13 standard library only; no packages, locks, model downloads, shared database writes or activation. Native Windows PDF rendering is a read-only inspection aid, not an OCR/extraction authority. The proposed2025-2026 sheet must be labeled proposed; filenames do not confer institutional approval. Never tune on a final set.

## Task1: source-bound packet validation and grading

- Create `tests/test_practice_exam.py` first. RED: missing module/function.
- Create `evaluation/practice_exam.py`: `validate_exam(exam, source_root)` verifies schema/dev split, unique IDs, question-family split, candidate review status, path containment, PDF bytes, page/bbox/locator and excerpt digests; refuses unsupported coverage masquerading as answerable. `grade_exam(exam, observations)` measures exact normalized answer-key agreement, expected control and exact source citations separately. Missing/wrong source is a failure even when an answer matches. Gold-key replay is not a retrieval benchmark.
- Test wrong edition/hash/page/locator, source mutation, invalid review promotion, final split, incomplete observations and unanswerable controls. Handle multi-source comparison as requiring both sources.
- GREEN: `python -m unittest tests.test_practice_exam -v`; explicitly commit code/tests/checkpoint/progress.

## Task2: original-source practice exam and debug workflow

- TDD CLI/report tests before adding `render_exam(exam)` and `main`: CLI accepts `--exam`, `--source-root`, external `--output-dir`, optional `--observations`; writes question sheet, answer key and validation/grading reports outside Git. No LLM answer generation or public API.
- Build12 candidate questions outside Git from directly inspected BSCS2018-2019 and explicitly proposed2025-2026 originals: direct prerequisites/units/standing, practicum edition comparison, curriculum ambiguity, missing grade policy and wrong-program scope. Group language paraphrases together.
- Record original digests, physical vs printed page, semantic row/column locator and bounding boxes, manually transcribed supporting excerpt, expected answer/control and review pending. Candidate source-label validation does not certify printed content automatically. Map to production ingestion span/cell IDs before a real retrieval benchmark; report this remaining condition.
- Validate actual originals and produce readable sheet/key plus report. Mutation tests ensure source/citation errors are detected. Do not fabricate runtime observations or benchmark scores.

## Task3: regression, review and recovery

- Run practice-exam/retrieval/embedding unittest suites and phase ledger checks; storage regressions only if database code changed. Inspect every result, keep logs externally.
- One fresh-context final code/source-boundary review as required by executing-plans/requesting-code-review; reproduce/fix actionable findings with RED/GREEN.
- Update Phase05 plan/checkpoint/current progress/report/handoff with exact artifacts/counts/digests/commands and remaining approved-label/real-model prerequisites. Commit cohesive increments. Keep branch local and Phase05 active until its real exit gate passes.
