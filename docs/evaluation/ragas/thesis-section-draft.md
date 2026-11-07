# Draft thesis section: RAGAS evaluation

Draft wording for the manuscript; table numbers (5.x) are placeholders. Faithfulness is reported only against the
full generator evidence; the top-3-only (.525) and plain-text (.782) diagnostics stay in README.md for panel questions. Figures come from
`ragas_scores.csv` / `ragas_summary.json`; the worked example comes from `example-q9.json`
(same judge, same evidence). The instrument is the one promised in Chapter IV, Research Instruments (2),
citing Es et al. (2024).

---

## Retrieval-Augmented Generation Assessment (RAGAS)

### Evaluation set-up

The RAGAS framework (Es et al., 2024) was used to evaluate the quality of Bintanong's retrieved context and
generated answers. The evaluation used the 14 document-based (RAG) benchmark queries, each asked in English,
Tagalog and Taglish, for 42 query–answer pairs. These are the same 42 saved answers used for the Accuracy,
Precision, Recall and F1-score evaluation, so no answer was regenerated for this measurement. RAGAS uses a
separate large language model as a judge. DeepSeek (`deepseek-chat`) served as the judge, and the
SEA-LION-E5-Embedding-600M model computed sentence embeddings. Each query has one reference answer, taken
verbatim from the official Student Handbook or Citizen's Charter. It consists of every passage judged relevant
to that query during the retrieval evaluation. The three language versions of a query share the same reference.

Five RAGAS metrics were computed. Context Precision and Context Recall evaluate the retrieval stage.
Faithfulness, Answer Relevancy and Factual Correctness evaluate the generation stage.

### Metrics and formulas

**Faithfulness.** This metric measures whether the generated answer stays within the evidence given to the
generator, and therefore indicates hallucination. The judge breaks the answer into individual statements and
decides for each one whether the evidence supports it.

  Faithfulness = (number of answer statements supported by the evidence) / (total number of answer statements)

In Bintanong, a retrieved passage is never given to the generator alone. When the source documents were
chunked and reviewed, each passage that cannot be understood without other passages recorded them as
*required neighbours*. Examples are a procedure that continues across pages, or a penalty row that depends on a
shared clause. When a passage is retrieved, its required neighbours are retrieved with it. The group reaches
the generator only if it is complete, as reviewed fields with their labels and any recorded source limitation.
Faithfulness was therefore measured against this full evidence, which was rebuilt from the deployed knowledge
base. For all 42 answers, the rebuilt number of neighbours matched the number logged when the answer was
generated.

**Answer Relevancy.** This metric measures whether the answer addresses the question asked. The judge writes
N = 3 questions that the answer would respond to. The score is the average cosine similarity between the
embedding of each generated question (E_gi) and the embedding of the original question (E_o):

  Answer Relevancy = (1/N) × Σ_{i=1..N} cos(E_gi, E_o)

If the judge labels the answer as *noncommittal* (evasive or uncertain), the score is set to 0.

**Context Precision.** This metric measures whether the relevant passages are ranked above irrelevant ones in
the top K retrieved results. For each rank k, v_k = 1 if the passage at rank k is relevant to the reference and
0 otherwise.

  Precision@k = relevant passages within the top k / k

  Context Precision@K = Σ_{k=1..K} (Precision@k × v_k) / (number of relevant passages in the top K)

**Context Recall.** This metric measures whether retrieval found the information that the reference answer
requires. The reference is split into statements, and each one is checked against the retrieved passages.

  Context Recall = (reference statements found in the retrieved passages) / (total reference statements)

**Factual Correctness (precision mode).** This metric measures how much of the answer agrees with the reference
answer. Answer claims supported by the reference are true positives (TP); claims not supported by it are false
positives (FP).

  Factual Correctness (precision) = TP / (TP + FP)

Precision mode was used because the references are complete source passages. In recall or F1 mode, a correct
but concise answer would be penalised for not repeating every sentence of the reference.

### Worked example

Query 9 (English) is used to illustrate the computation: *"What is the penalty for cheating in an exam?"*
Retrieval returned two passages, both from the Student Handbook: the penalty row for "a. Any form of cheating
in examinations" (rank 1) and the clause "Additional corrective measures for all acts of academic dishonesty"
(rank 2). Bintanong answered:

> Here is what the source says: Cause: "a. Any form of cheating in examinations"; 1st Offense: "Automatic grade
> of zero (0) on the examination/ activity or failing grade of five (5) upon discretion in the subject where it
> was committed."; 2nd Offense: "Suspension for two weeks"; 3rd Offense: "Suspension for one month";
> Subsequent Offenses: "Dismissal". … Measures: "Withdrawal of degree; Withdrawal of honors; Disqualification
> from graduation with honors; Cancellation of registration". Recorded source limitation: "Unavailable
> information: which additional corrective measures apply automatically to an individual act." Please confirm
> with the relevant university office.

*Faithfulness.* The judge extracted 13 statements. Twelve were supported by the evidence, for example "The
second offense results in suspension for two weeks", which is supported by the reviewed field
"2nd Offense: Suspension for two weeks". The unsupported statement was the closing referral, "Please confirm
with the relevant university office". Bintanong adds this sentence by design, and it does not appear in the
source. Faithfulness = 12 / 13 = **0.923**.

*Answer Relevancy.* The judge generated three questions from the answer. Their cosine similarities to the
original question were:

| Generated question | cos(E_gi, E_o) |
| --- | ---: |
| What are the penalties for cheating in examinations? | 0.957 |
| What are the penalties for cheating in examinations and additional corrective measures for academic dishonesty? | 0.843 |
| What are the penalties for cheating in examinations and the additional corrective measures for academic dishonesty? | 0.838 |

Answer Relevancy = (0.957 + 0.843 + 0.838) / 3 = **0.879**. Question generation is not deterministic. The
scored run, reported in Table 5.x, gave 0.840 for this item.

*Context Precision.* Both retrieved passages were relevant (v_1 = v_2 = 1), so Precision@1 = 1/1 and
Precision@2 = 2/2. Context Precision = (1 × 1 + 1 × 1) / 2 = **1.000**.

*Context Recall.* The reference for Query 9 has four Handbook passages (pp. 88–90): the general cheating row
and the additional corrective measures, which were retrieved, and two other examination-cheating rows (items e
and g), which were not. The judge split the reference into 13 statements and found 9 in the retrieved passages.
Context Recall = 9 / 13 = **0.692**. The missing statements are the penalties for items e and g, which shows
that retrieval returned the general rule but not the related specific offences.

### Results

**Table 5.x. RAGAS scores of Bintanong by query language (n = 42; 14 per language)**

| Metric | Overall | English | Tagalog | Taglish |
| --- | ---: | ---: | ---: | ---: |
| Faithfulness | 0.883 | 0.891 | 0.898 | 0.858 |
| Answer Relevancy | 0.584 | 0.657 | 0.547 | 0.549 |
| Context Precision | 0.896 | 0.911 | 0.909 | 0.869 |
| Context Recall | 0.754 | 0.793 | 0.737 | 0.733 |
| Factual Correctness (precision) | 0.570 | 0.571 | 0.570 | 0.568 |

### Discussion

Faithfulness was high, 0.883 overall and at least 0.858 in every language. Answers stayed close to the
institutional documents, which supports the design choice of quoting reviewed source fields instead of letting
the model paraphrase freely. Most of the statements judged unsupported are notices Bintanong adds deliberately, such as source-limitation statements and referrals to the relevant university
office. These follow the study's source-gap rules even though they are not in the source text.

Context Precision (0.896) shows that relevant passages were usually ranked first. Context Recall (0.754) shows
that the retrieved passages usually covered most of the reference, but related clauses were sometimes missed,
as in the worked example. Context Recall is likely overstated, because only passages that appeared in some
system's top results were judged for relevance.

Answer Relevancy was the lowest metric (0.584). Seven answers scored 0 because the judge labelled them
noncommittal: Queries 5 and 6 in all three languages, and Query 13 in Taglish. Each of these answers quotes the
source and then states a recorded source limitation, such as conflicting completion deadlines, and refers the
student to the relevant office. RAGAS treats such a hedge as evasive, while the study requires it whenever the
source is incomplete or conflicting. Without these seven items, Answer Relevancy was 0.701 (English 0.766,
Tagalog 0.638, Taglish 0.698). English scored higher than Tagalog and Taglish on this metric. Part of the gap
may come from comparing a Filipino question with questions generated from mostly English source wording, so
it is not a clean comparison of language quality.

Factual Correctness (0.570) was moderate. The references are complete source passages, and answers sometimes
included correct content from neighbour passages or host notices that are not part of the reference. Both
lower the precision score without indicating a factual error.

Limitations: each item was scored once by a single judge model. The judge's reliability on Tagalog and Taglish
was not separately validated. Query 11 was run on a later routing version; without it, the Table 5.x scores change
by at most 0.012. The planned comparison against the baseline Bintu-1 model was not carried out for RAGAS.

---

## Chapter 5 entries

### Summary of Findings (RAGAS)

- Bintanong's answers were highly faithful to the institutional documents: Faithfulness 0.883 overall
  (English 0.891, Tagalog 0.898, Taglish 0.858). Most unsupported statements were deliberate source-limitation
  notices and office referrals, not invented content.
- Retrieval ranked relevant passages first (Context Precision 0.896) and covered most of the needed
  information (Context Recall 0.754). Related clauses were sometimes missed.
- Answer Relevancy was 0.584 overall, or 0.701 without seven answers that RAGAS scored 0 for stating
  documented source limitations. English answers scored higher than Tagalog and Taglish answers.
- Factual Correctness against full source passages was 0.570 (precision mode).

### Conclusion (RAGAS)

Bintanong's generation stage keeps its answers grounded in the reviewed PalSU documents in all three supported
input languages, which meets the study's aim of a hallucination-resistant advisory system. The main measured
weaknesses are incomplete retrieval of related clauses, and a mismatch between generic relevance metrics and
the system's required disclosure of source gaps.

### Contributions

- An evaluation procedure for neuro-symbolic RAG systems that scores faithfulness against the complete evidence
  the generator receives (retrieved passages plus required neighbours, as reviewed fields).
- Shared verbatim source references for 14 PalSU queries in three languages, usable by RAGAS and BERTScore alike.

### Recommendations

- Add retrieval of related clauses within the same policy section (for example, other examination-cheating
  offences) to raise Context Recall.
- Report Answer Relevancy both with and without answers that disclose documented source limitations. Future
  work could adapt the noncommittal criterion so that a cited source gap is not treated as evasion.
- Repeat the RAGAS scoring with several judge runs or judge models, validate the judge on Filipino text, and
  include the baseline Bintu-1 comparison planned in Chapter IV.
- Extend the reference set to cover more queries per category, toward the 50-query benchmark planned in
  Chapter IV.
