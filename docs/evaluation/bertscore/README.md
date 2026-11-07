# Bintanong BERTScore export (42 questions)

Files: `bertscore_pairs.jsonl` (full, with retrieved context) and `bertscore_pairs.csv` (Excel-friendly, UTF-8).
One row per question: 14 RAG benchmark rows (Q1-Q14 = benchmark rows 11-24) x English / Tagalog / Taglish,
the same 42 questions as `Context/for_f1scoreprecisionaccuracyrecall_completed.pdf`. These are saved outputs
from the 7 November 2026 metrics run (code `1e499828`; Q11 rerun on `48a45001`), generated from the
ignored run logs; regenerate rather than hand-edit candidate answers.

- `candidate_answer`: Bintanong's saved answer. No Gemma, `.env`, database or dataset is needed.
- `reference_answer`: filled 7 Nov 2026 from `../references/reference_answers.jsonl` (owner-agreed rule): the
  verbatim Student Handbook / Citizen's Charter text of every chunk judged relevant (TP or FN) for that query in
  any language variant of the final-metrics judgments. The same reference serves English, Tagalog and Taglish,
  and RAGAS uses the identical file. `reference_chunk_ids` (JSONL) lists the chunks. See the references README
  for limits: references are long source text, not concise model answers, so BERTScore recall will run low.
- `retrieved_context`: the top-3 chunks the system retrieved. Context only, not a reference.
- Q11 is a two-turn case (English asked "leaving or incoming?", answered with "Leaving PalSU") and ran on
  newer routing code than the other 41 rows. Report it separately or note it.

Suggested scoring (on your own branch; `pip install bert-score`):

```python
from bert_score import score
P, R, F1 = score(candidates, references, model_type="xlm-roberta-large", lang=None)
```

Use one multilingual model for all three languages so scores are comparable. Report P/R/F1 per language and overall.
Do not use `rescale_with_baseline` unless a baseline exists for the chosen model and language.
