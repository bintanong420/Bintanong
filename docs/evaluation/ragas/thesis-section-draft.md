# Draft thesis section: RAGAS evaluation

Draft wording for the manuscript; table numbers (R1-R5) are placeholders; Table R5 is placed in Chapter 5. Text after the first rule is the
manuscript section; build_section_pdf.py renders it to PDF. Faithfulness is reported only against the
full generator evidence; the top-3-only (.525) and plain-text (.782) diagnostics stay in README.md for panel questions. Figures come from
`ragas_scores.csv` / `ragas_summary.json`; the Query 1 worked example comes from `example-q1.json`
(`scripts/example_q1.py`: same judge, settings and evidence, re-run to record each judgment). The instrument is the one promised in Chapter IV, Research Instruments (2),
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

### Worked example: Query 1 in three languages

Query 1 is used to show how the benchmark processed one query. Like every benchmark query, it was asked in
English, Tagalog and Taglish, and all three versions were scored against the same reference answer.

**Table R1. Query 1 language versions and the passages retrieved for each**

<!-- widths: 0.9,1.6,4.0 -->
| Language | Question | Top 3 retrieved passages (rank order) |
| --- | --- | --- |
| English | How to drop subjects? | (1) Charter heading "3. CHANGING, ADDING AND DROPPING OF SUBJECTS"; (2) Charter step 1, the student fills up the DAC Form and the faculty signs it; (3) Charter step 2, the dean's signature and the DAC deadlines |
| Tagalog | Pano po magtanggal ng subject na kinuha ko? | (1) the same Charter heading; (2) the service's classification block ("Simple Transaction … Who may avail: Palawan State University Students"); (3) Charter step 1 |
| Taglish | Paano mag-drop ng subject? | the same three passages as the Tagalog version |

The reference answer for Query 1 is the verbatim text of every passage judged relevant to the query during the
retrieval evaluation: the Charter heading, Charter steps 1 and 2, and Handbook item 7 ("How to drop subjects?").
For each version, the generator received the top 3 passages together with their required neighbours, seven
passages in total. All three answers gave the same four-step Citizen's Charter procedure. Only the framing words
changed: English "What to bring", "No fee · about 5 minutes"; Tagalog and Taglish "Dalhin", "Walang fee · mga
5 minutes". The English answer begins:

> Here's the process for CHANGING, ADDING AND DROPPING OF SUBJECTS at the Academic Unit/College, based on the
> Citizen's Charter. What to bring: 1. Dropping/ Adding/ Changing Form (from College Secretary). Steps: 1. The
> student fills up the Dropping/Adding/Changing Form (DAC Form) and submit to faculty concerned. No fee · about
> 5 minutes … 2. Seek the approval of the class adviser or department chairperson … Total: NONE · about 26 minutes

The judge's intermediate decisions below come from a separate re-run of the same judge on these three items,
done to record each step. The judge is not fully deterministic, so a few decisions differ from the scored run;
Table R3 lists both.

*Faithfulness.* The judge split the English answer into 15 statements and the Tagalog and Taglish answers into 17
each, because the judge also listed the total fee and total time for those two. In English and Tagalog the one
unsupported statement was the opening line, "The process … is based on the Citizen's Charter". This framing
sentence is added by Bintanong and does not appear in the passages. Every procedural step, fee, time and deadline
was supported, for example "The deadline for dropping is before midterm examinations", which is supported by
Charter step 2. In Taglish the judge accepted the opening line but rejected "The student brings a
Dropping/Adding/Changing Form obtained from the College Secretary", which it had accepted in the other two
languages. This shows the judge's run-to-run variation.

  Faithfulness (English) = 14 / 15 = 0.933;  Tagalog = 16 / 17 = 0.941;  Taglish = 16 / 17 = 0.941

*Answer Relevancy.* For each version, the judge generated the same question three times (N = 3), so the score
equals that question's cosine similarity to the original question. No answer was labelled noncommittal.

**Table R2. Questions generated from the Query 1 answers**

<!-- widths: 0.9,4.4,1.2 -->
| Language | Generated question (all three identical) | cos(E_gi, E_o) |
| --- | --- | ---: |
| English | What is the process for changing, adding, and dropping subjects at the Academic Unit/College? | 0.670 |
| Tagalog | What is the process for changing, adding, and dropping subjects in the Academic Unit/College according to the Citizen's Charter? | 0.503 |
| Taglish | What is the process for changing, adding, and dropping subjects in the Academic Unit/College according to the Citizen's Charter? | 0.528 |

  Answer Relevancy (English) = (0.670 + 0.670 + 0.670) / 3 = 0.670;  Tagalog = 0.503;  Taglish = 0.528

The generated questions are in English, because the answers quote English source text. Their similarity to a
Tagalog or Taglish question is therefore lower, although the three answers give the same procedure.

*Context Precision.* In English all three retrieved passages were judged useful for reaching the reference
(v_1 = v_2 = v_3 = 1), so Context Precision = (1/1 + 2/2 + 3/3) / 3 = 1.000. In Tagalog and Taglish, rank 2 was
the classification block, which the judge found not useful ("it does not contain specific instructions on how to
drop subjects"), so v = (1, 0, 1):

  Context Precision (Tagalog, Taglish) = (Precision@1 × 1 + Precision@2 × 0 + Precision@3 × 1) / 2 = (1/1 + 2/3) / 2 = 0.833

*Context Recall.* The judge split the reference into 15 statements and checked each one against the top 3
passages. In English, 14 statements were found; the missing one was Handbook item 7, which was not retrieved
(14 / 15 = 0.933). In Tagalog and Taglish, Charter step 2 was not in the top 3, because the classification block
took rank 2. The dean's signature, the DAC deadlines and the College Secretary's action were therefore missing:
Tagalog 10 / 15 = 0.667 and Taglish 9 / 15 = 0.600.

*Factual Correctness (precision).* The judge split each answer into 27 or 28 claims and checked each one against
the reference. The claims taken from Charter steps 1 and 2 were true positives. The step "Seek the approval of the
class adviser or department chairperson", step 3 (the student receives a copy) and the printed total of 26
minutes were false positives. These come from correct required-neighbour passages that are not part of the
reference.

  Factual Correctness (English) = 16 / 28 = 0.571;  Tagalog = 16 / 27 = 0.593;  Taglish = 17 / 27 = 0.630

**Table R3. Query 1 RAGAS scores: worked-example re-run and scored run**

<!-- widths: 1.55,0.825,0.825,0.825,0.825,0.825,0.825 -->
| Metric | English (re-run) | English (scored) | Tagalog (re-run) | Tagalog (scored) | Taglish (re-run) | Taglish (scored) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Faithfulness | 0.933 | 0.941 | 0.941 | 0.882 | 0.941 | 0.882 |
| Answer Relevancy | 0.670 | 0.670 | 0.503 | 0.503 | 0.528 | 0.528 |
| Context Precision | 1.000 | 1.000 | 0.833 | 0.833 | 0.833 | 0.333 |
| Context Recall | 0.933 | 0.933 | 0.667 | 0.533 | 0.600 | 0.600 |
| Factual Correctness | 0.571 | 0.560 | 0.593 | 0.630 | 0.630 | 0.630 |

Answer Relevancy was identical in both runs, and most other values differ by one or two judge decisions. The
largest difference is Taglish Context Precision: in the scored run the judge also rejected the rank-1 heading,
giving v = (0, 0, 1) and Context Precision = (Precision@3 × 1) / 1 = 1/3 = 0.333. The reported results use the scored run. Query 1 shows the pattern
seen across the benchmark: the answers stay faithful to the evidence in all three languages, while the retrieval
of the Tagalog and Taglish questions and the English-only generated questions lower the other metrics.

### Results

**Table R4. RAGAS scores of Bintanong by query language (n = 42; 14 per language)**

| Metric | Overall | English | Tagalog | Taglish |
| --- | ---: | ---: | ---: | ---: |
| Faithfulness | 0.883 | 0.891 | 0.898 | 0.858 |
| Answer Relevancy | 0.584 | 0.657 | 0.547 | 0.549 |
| Context Precision | 0.896 | 0.911 | 0.909 | 0.869 |
| Context Recall | 0.754 | 0.793 | 0.737 | 0.733 |
| Factual Correctness (precision) | 0.570 | 0.571 | 0.570 | 0.568 |

The scores of each query in each language are given in Chapter 5, Table R5.

### Analysis of low-scoring items

- *Answer Relevancy of 0 (Queries 5 and 6, and Query 13 in Taglish).* These answers quote the source and then
  state a recorded source limitation (for example, conflicting completion deadlines for an INC grade) and refer
  the student to the relevant office. The judge labelled them noncommittal, which sets the score to 0.
- *Query 13 (vehicle or gate pass).* The source describes only selected office steps of the application, so the
  answer adds notices such as "These are selected office steps, not a complete application procedure." These
  notices are not in the source text, which lowers Faithfulness. The gate-pass passages that were not retrieved
  also lowered Context Recall (0.380 averaged over the three languages).
- *Query 3 (enrolment).* Context Precision averaged 0.389 over the three languages (0.000 in Taglish). The RAGAS judge considered some higher-ranked passages
  not useful for reaching the reference answer, although the human relevance judgments used for the F1
  evaluation marked all three as relevant. RAGAS judges usefulness for the reference, not topical relevance,
  so the two measures can disagree.

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

Factual Correctness (0.570) was moderate. An answer claim counts against this score whenever it is absent from
the reference, even if it is correct. Examples are content drawn from required-neighbour passages outside the
reference, as in Query 1, or system notices such as source-limitation statements. The lowest items (Queries 4, 9 and 10) were
not analysed claim by claim, so this metric is reported without attributing its errors to a specific cause.

Limitations: each item was scored once by a single judge model. The judge's reliability on Tagalog and Taglish
was not separately validated. Query 11 was run on a later routing version; without it, the Table R4 scores change
by at most 0.012. The planned comparison against the baseline Bintu-1 model was not carried out for RAGAS.

---

## Chapter 5 entries

### Results per query (RAGAS)

Table R5 gives the RAGAS scores of every benchmark query in each language. Query 1 is the worked example in
Chapter 4. Faithfulness is measured against the full generator evidence; Factual Correctness is in precision mode. Column abbreviations: F = Faithfulness, AR = Answer Relevancy,
CP = Context Precision, CR = Context Recall, FC = Factual Correctness.

**Table R5. RAGAS scores per benchmark query and language (n = 42)**

<!-- widths: 2.5,0.9,0.62,0.62,0.62,0.62,0.62 -->
| Query (English version) | Language | F | AR | CP | CR | FC |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1. How to drop subjects? | English | 0.941 | 0.670 | 1.000 | 0.933 | 0.560 |
|  | Tagalog | 0.882 | 0.503 | 0.833 | 0.533 | 0.630 |
|  | Taglish | 0.882 | 0.528 | 0.333 | 0.600 | 0.630 |
| 2. How to shift/change curricular program? | English | 0.840 | 0.932 | 0.500 | 1.000 | 0.620 |
|  | Tagalog | 0.867 | 0.584 | 1.000 | 1.000 | 0.870 |
|  | Taglish | 0.867 | 0.595 | 1.000 | 1.000 | 0.870 |
| 3. How to enroll for the next semester? | English | 0.818 | 0.676 | 0.583 | 0.735 | 0.380 |
|  | Tagalog | 0.786 | 0.613 | 0.583 | 0.853 | 0.440 |
|  | Taglish | 0.849 | 0.634 | 0.000 | 0.676 | 0.520 |
| 4. How to add or change subjects? | English | 0.933 | 0.756 | 1.000 | 0.900 | 0.290 |
|  | Tagalog | 1.000 | 0.580 | 0.833 | 0.421 | 0.260 |
|  | Taglish | 0.941 | 0.663 | 0.833 | 0.421 | 0.260 |
| 5. How to remove a grade of 4? | English | 0.947 | 0.000 | 0.833 | 0.438 | 0.520 |
|  | Tagalog | 0.944 | 0.000 | 1.000 | 0.312 | 0.500 |
|  | Taglish | 0.944 | 0.000 | 1.000 | 0.312 | 0.520 |
| 6. How to complete an INC grade? | English | 0.929 | 0.000 | 1.000 | 1.000 | 0.370 |
|  | Tagalog | 0.933 | 0.000 | 1.000 | 1.000 | 0.460 |
|  | Taglish | 0.929 | 0.000 | 1.000 | 1.000 | 0.460 |
| 7. How do I get off probation? | English | 1.000 | 0.897 | 1.000 | 1.000 | 1.000 |
|  | Tagalog | 1.000 | 0.798 | 1.000 | 1.000 | 1.000 |
|  | Taglish | 1.000 | 0.736 | 1.000 | 1.000 | 1.000 |
| 8. What do I do when I lose, forget my ID or to retrieve a confiscated ID? | English | 1.000 | 0.874 | 1.000 | 1.000 | 1.000 |
|  | Tagalog | 1.000 | 0.782 | 1.000 | 1.000 | 1.000 |
|  | Taglish | 0.400 | 0.849 | 1.000 | 1.000 | 0.670 |
| 9. What is the penalty for cheating in an exam? | English | 0.923 | 0.840 | 1.000 | 0.692 | 0.500 |
|  | Tagalog | 0.889 | 0.693 | 1.000 | 0.692 | 0.330 |
|  | Taglish | 0.933 | 0.769 | 1.000 | 0.692 | 0.330 |
| 10. How to secure a good moral certificate? | English | 0.979 | 0.685 | 1.000 | 0.800 | 0.340 |
|  | Tagalog | 1.000 | 0.583 | 1.000 | 0.588 | 0.350 |
|  | Taglish | 1.000 | 0.586 | 1.000 | 0.588 | 0.370 |
| 11. How to secure transfer credentials? | English | 0.897 | 0.644 | 0.833 | 0.607 | 0.390 |
|  | Tagalog | 0.902 | 0.694 | 0.833 | 0.586 | 0.470 |
|  | Taglish | 0.902 | 0.698 | 1.000 | 0.724 | 0.370 |
| 12. How do I claim accident insurance? | English | 1.000 | 0.936 | 1.000 | 1.000 | 1.000 |
|  | Tagalog | 1.000 | 0.685 | 1.000 | 1.000 | 1.000 |
|  | Taglish | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 13. How to obtain a vehicle or gate pass? | English | 0.571 | 0.580 | 1.000 | 0.308 | 0.430 |
|  | Tagalog | 0.667 | 0.543 | 1.000 | 0.333 | 0.430 |
|  | Taglish | 0.700 | 0.000 | 1.000 | 0.500 | 0.430 |
| 14. How to avail the use of university rooms and facilities? | English | 0.700 | 0.706 | 1.000 | 0.688 | 0.590 |
|  | Tagalog | 0.704 | 0.598 | 0.639 | 1.000 | 0.240 |
|  | Taglish | 0.667 | 0.624 | 1.000 | 0.750 | 0.520 |
| **Mean** | **English** | **0.891** | **0.657** | **0.911** | **0.793** | **0.571** |
| **Mean** | **Tagalog** | **0.898** | **0.547** | **0.909** | **0.737** | **0.570** |
| **Mean** | **Taglish** | **0.858** | **0.549** | **0.869** | **0.733** | **0.568** |
| **Mean** | **All** | **0.883** | **0.584** | **0.896** | **0.754** | **0.570** |

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
