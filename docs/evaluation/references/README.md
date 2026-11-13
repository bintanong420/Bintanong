# Shared reference answers (Q1-Q14, benchmark rows 11-24)

Ground truth for both the RAGAS and BERTScore evaluations, so both use the same references.
`reference_answers.jsonl` (full, with chunk metadata) and `reference_answers.csv` (Excel-friendly, UTF-8).

Rule (owner, 7 Nov 2026): the reference for a query is the verbatim text of every chunk judged relevant
(TP or FN) for that query in any of its English / Tagalog / Taglish variants in the 7 Nov final-metrics
judgments (`Context/for_f1scoreprecisionaccuracyrecall_completed.pdf`). Text is copied from the saved run logs,
not retyped; chunks are joined in source/page order with a blank line between them. No chunk was judged
relevant in one variant and irrelevant in another variant of the same query.

Limits:
- Only chunks that appeared in a top-3 list were judged, so a relevant chunk that never surfaced is missing.
  Context-recall-style scores are therefore optimistic.
- References are full source passages, not short ideal answers. A correct, concise answer covers only part
  of them, so recall-side scores (BERTScore R, RAGAS factual-correctness recall) understate answer quality.
- Q11 ran on newer routing code (two-turn "Leaving PalSU"); report it separately or note it.
- These are research references from public PalSU sources, not university validation.
