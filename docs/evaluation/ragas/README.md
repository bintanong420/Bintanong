# Bintanong RAGAS evaluation (42 questions, 7 November 2026)

RAGAS scores for the same 42 saved answers as the F1 sheet and the BERTScore export: 14 RAG benchmark rows
(Q1-Q14 = rows 11-24) x English / Tagalog / Taglish. These are the saved outputs from the 7 Nov metrics run
(code `1e499828`; Q11 rerun on `48a45001`). Nothing was re-generated. This is a research measurement on
public PalSU sources, not university validation.

Files: `ragas_scores.csv` (one row per question), `ragas_summary.json` (by language, by query, excluding Q11),
`scripts/` (exact scripts and frozen package list; API key and raw logs stay in ignored `audit-evidence/ragas-20261107/`).
Thesis section: `thesis-section-draft.md` -> `ragas-thesis-section.pdf` (worked example = Query 1 in three languages,
`example-q1.json` from `scripts/example_q1.py`; per-query table in the Chapter 5 part).
Low-score review, Option A decision and pending manuscript changes (8 Nov): `followup-notes-2026-11-08.md` /
`ragas-followup-notes-2026-11-08.pdf`.

## Set-up

| Item | Choice |
| --- | --- |
| RAGAS | 0.4.3 (separate venv; langchain-community pinned to 0.3.31 because 0.4.x breaks the ragas import) |
| Judge LLM | DeepSeek `deepseek-chat` via its OpenAI-compatible API, temperature 0; one run per row. DeepSeek accepts only one completion per request, so Answer relevancy's three questions are three separate calls |
| Embeddings | local SEA-LION-E5-Embedding-600M, STS prompt (Answer relevancy only); no download |
| Telemetry | RAGAS usage tracking off |
| Reference | `../references/reference_answers.jsonl`: verbatim text of every chunk judged relevant (TP or FN) for the query in the F1 judgments; the same reference for all three languages and for BERTScore |
| Tokens | about 677k input / 322k output across the three scored runs (pilots and spot inspections excluded) |

## Results

| Metric | Overall | English | Tagalog | Taglish | What it measures |
| --- | ---: | ---: | ---: | ---: | --- |
| **Faithfulness** | **.883** | .891 | .898 | .858 | Share of answer statements supported by the evidence the writer received |
| Answer relevancy | .584 | .657 | .547 | .549 | How well the answer addresses the question (see note: 7 rows scored 0) |
| Context precision | .896 | .911 | .909 | .869 | Relevant retrieved chunks are ranked first (top 3, against the reference) |
| Context recall | .754 | .793 | .737 | .733 | Share of reference statements found in the top 3 retrieved chunks |
| Factual correctness (precision) | .570 | .571 | .570 | .568 | Share of answer claims also found in the reference |

Excluding Q11 (newer code): faithfulness .881, answer relevancy .577, context precision .897, context recall .763,
factual correctness .582. Per-query values are in `ragas_summary.json`.

## How to read these numbers

**Faithfulness context.** The writer receives each top-3 chunk plus its required-neighbour chunks (usually the
rest of the same procedure), as reviewed, labelled fields with any recorded source limitation.
`writer_context.py` rebuilds that evidence from the served package using the runtime's neighbour rule; for all
42 rows the rebuilt neighbour counts match the logged `attached_count`. The field layout is our rendering, not a
byte copy of the writer prompt. The same judge scored three context versions:

| Context given to the judge | Faithfulness |
| --- | ---: |
| Top 3 chunks only (plain text, as first exported) | .525 |
| Writer evidence, plain chunk text | .782 |
| Writer evidence, reviewed field labels + source limitations (headline) | .883 |

The jump comes from evidence the judge had not been shown: with top-3 text only, real Charter steps from neighbour
chunks looked unsupported. With plain text, a table such as the cheating penalties loses its column headers
("1st Offense", "2nd Offense"), so a correct answer looked unsupported. The remaining unsupported statements are
mostly host-added text, for example "Please confirm with the relevant university office" or the "completion
deadlines conflict" summary. Those statements are deliberate, but they are not in the source.
Lowest rows: Q08 Taglish .40, Q13 (.57-.70), Q14 (.67-.70). These were not inspected one by one.

**Answer relevancy.** The answer scores 0 when the judge calls it noncommittal. That happened on 7 rows: Q5 and Q6
in all three languages, plus Q13 Taglish. Those answers quote the source and then state the recorded source
limitation and an office referral, which the source-gap policy requires. Without those 7 rows the mean is .701
(English .766, Tagalog .638, Taglish .698). The metric also compares a question generated from the answer with
the original question. Tagalog/Taglish questions compared with mostly English source wording are likely to score
lower, so language differences here are not a clean language-quality comparison.

**Reference-based metrics.** References are full source passages, not ideal short answers:
- Context recall is optimistic, because only chunks that appeared in some top-3 list were ever judged.
- Factual correctness is reported in precision mode. A recall or F1 mode would penalise concise, correct answers
  for not repeating every reference sentence.
- Factual correctness is still below 1 when an answer adds correct content from neighbour chunks or
  host-added notices that are not in the reference.

## Limits

- One judge run per row, no repeat sampling. The judge is a general model, and LLM-judge scores can vary between
  runs and judges. Treat differences of a few points as noise.
- The judge reads English, Tagalog and Taglish answers against English source text. Its reliability on Filipino
  was not separately validated.
- Q11 is a two-turn case on newer routing code. Report it separately or with the excluding-Q11 figures.
- These are 42 answers to 14 RAG questions. They say nothing about Prolog/structured prerequisite answers,
  which these rows do not cover.
