# Draft thesis section: BATAYAN evaluation

Draft wording for the manuscript; table numbers (B1-B4) are placeholders. Text after the first rule is the
manuscript section; `../ragas/scripts/build_section_pdf.py` renders it to PDF. All scores come from
`results/full-run-all-9-tasks-results-2026-11-08.json` (second machine, 8 Nov 2026). Item counts come from the
cached SEA-HELM datasets (`eval` splits) and add up to 3,800. The two example items are the first two Sentiment
items. Their responses were taken from the first machine's Sentiment run, which used the same model, prompt and
settings. The instrument is the one promised in Chapter IV, Research Instruments (3), citing Montalan et al.
(2025). Check before submission: the SEA-HELM citation (Susanto et al., 2025), the ChrF++ (Popović, 2017) and
ROUGE (Lin, 2004) references, and the leaderboard access date.

---

## BATAYAN Benchmark

### Evaluation set-up

The BATAYAN benchmark (Montalan et al., 2025) was used to measure the Filipino language competence of the
language model inside Bintanong. BATAYAN is the Filipino task group of AI Singapore's SEA-HELM evaluation suite
(Susanto et al., 2025). It covers three competencies: Natural Language Understanding (NLU), Natural Language
Reasoning (NLR) and Natural Language Generation (NLG), plus a toxicity-detection safety task. Every item is in
Filipino (Tagalog). Prompts are written in Filipino, and each item is answered zero-shot (no worked examples in
the prompt) in a single run.

BATAYAN tests the model, not the full Bintanong pipeline. Retrieval, source quoting and the Prolog curriculum
rules are not involved. The quality of answers grounded in PalSU documents is measured separately by RAGAS.
The model tested was the one Bintanong runs: Gemma 4 E4B, quantized to 4 bits (Q4_K_XL GGUF) and served by
llama.cpp. It used Bintanong's own inference settings: temperature 0 (deterministic output) and the
model's thinking mode turned off. The benchmark ran through SEA-HELM's official code
(commit 9be3986) on an RTX 4060 Laptop GPU with 8 GB of memory. It was run once over all 3,800 items. Every
item received a parseable answer.

**Table B1. BATAYAN tasks used (Filipino, 3,800 items)**

| Competency | Task | Items | Answer type | Chance level | Metric |
| --- | --- | ---: | --- | ---: | --- |
| NLU | Sentiment analysis | 600 | 3 classes | 33.3% | Macro F1, accuracy |
| NLU | Belebele reading comprehension | 100 | 4 choices | 25.0% | Macro F1, accuracy |
| NLU | Paraphrase identification | 400 | 2 classes | 50.0% | Macro F1, accuracy |
| NLR | Causal reasoning | 400 | 2 choices | 50.0% | Macro F1, accuracy |
| NLR | Natural language inference | 600 | 3 classes | 33.3% | Macro F1, accuracy |
| NLG | Translation, English to Filipino | 600 | free text | – | ChrF++ |
| NLG | Translation, Filipino to English | 600 | free text | – | ChrF++ |
| NLG | Abstractive summarization | 100 | free text | – | ROUGE-L F1 |
| Safety | Toxicity detection | 400 | 2 classes | 50.0% | Macro F1, accuracy |

### Metrics and formulas

**Accuracy and Macro F1.** The classification and multiple-choice tasks compare the model's answer with the
correct label. Accuracy is the share of items answered correctly. Macro F1 computes an F1-score for each class
c (for example *Positibo*, *Negatibo* and *Neutral*) and averages them, so that every class counts equally,
however many items it has:

  F1_c = 2 × Precision_c × Recall_c / (Precision_c + Recall_c)

  Macro F1 = (1/C) × Σ_{c=1..C} F1_c

**Normalized score.** A model that guesses at random already gets some answers right: one in four on a
four-choice task. SEA-HELM therefore rescales accuracy so that random guessing scores 0 and a perfect result
scores 100. The chance level is 1 divided by the number of answer options, and a negative result is set to 0:

  Normalized score = max(0, (Accuracy − Chance) / (100 − Chance)) × 100

**ChrF++.** Translations are compared with a reference translation by counting shared character sequences
(up to 6 characters) and word pairs (up to 2 words) (Popović, 2017). It is reported on a 0–100 scale and
works well for Filipino, whose affixes change word forms.

**ROUGE-L F1.** Summaries are compared with a reference summary through their longest common subsequence of
words (Lin, 2004). ROUGE-L precision (P) and recall (R) give:

  ROUGE-L F1 = 2 × P × R / (P + R)

**Competency and overall scores.** Each competency score is the mean of its tasks' normalized scores. The two
translation directions are first averaged into one translation score. The overall Filipino score is the mean
of the four competency scores.

### Worked example

The first two Sentiment items illustrate how an item is asked and scored (responses from the Sentiment check
run described under Limitations). The model received this
Filipino prompt (shortened):

> Ano ang sentimyento sa sumusunod na pangungusap? Sumagot gamit ng isa sa mga sumusunod na pagpipilian:
> Positibo, Negatibo, o Neutral. … Pangungusap: "UPDATE: Umabot na sa 75,000+ ang nagpunta sa grand rally sa
> Bacolod."

It answered "Sagot: Neutral", which matches the label *Neutral*, so the item is correct. For the second item,
"Super fan ako ng Showtime noon pero nung nakapanood ako ng isang episode ng Aldub, nagandahan ako haha," the
model answered *Positibo*, while the label is *Neutral*. That item is counted as wrong.

The Belebele reading-comprehension result shows how the scores are combined. The model answered 87 of the 100
four-choice items correctly (accuracy 87.0%; chance 25%):

  Normalized score = (87.0 − 25) / (100 − 25) × 100 = 62 / 75 × 100 = **82.67**

The NLU competency score is the mean of its three normalized task scores:

  NLU = (62.25 + 82.67 + 30.50) / 3 = **58.47**

The NLG competency score averages the translation score (the mean of 61.43 and 68.44, which is 64.94) with
summarization (21.87), giving 43.40. The overall score is the mean of the four competencies:

  Overall = (58.47 + 69.01 + 43.40 + 32.00) / 4 = **50.72**

### Results

**Table B2. BATAYAN results of Gemma 4 E4B in Bintanong (Filipino)**

| Competency | Task | Accuracy | Macro F1 | Normalized score | Competency score |
| --- | --- | ---: | ---: | ---: | ---: |
| NLU | Sentiment analysis | 74.83 | 72.80 | 62.25 | 58.47 |
| NLU | Belebele reading comprehension | 87.00 | 87.04 | 82.67 | |
| NLU | Paraphrase identification | 65.25 | 63.76 | 30.50 | |
| NLR | Causal reasoning | 93.26 | 93.25 | 86.53 | 69.01 |
| NLR | Natural language inference | 67.67 | 68.09 | 51.50 | |
| Safety | Toxicity detection | 66.00 | 63.33 | 32.00 | 32.00 |
| | **Overall (mean of four competencies)** | | | | **50.72** |

**Table B3. BATAYAN generation results**

| Task | Metric | Score |
| --- | --- | ---: |
| Translation, English to Filipino | ChrF++ | 61.43 |
| Translation, Filipino to English | ChrF++ | 68.44 |
| Abstractive summarization | ROUGE-L F1 (precision 15.22, recall 41.71) | 21.87 |
| **NLG competency score** | mean of translation (64.94) and summarization | **43.40** |

**Table B4. NLU and NLR scores compared with models on the SEA-HELM Tagalog leaderboard**

| Model | NLU | NLR |
| --- | ---: | ---: |
| Gemma 4 E2B (leaderboard) | 69.72 | 59.36 |
| **Gemma 4 E4B, 4-bit, in Bintanong (this study)** | **58.47** | **69.01** |
| Gemma 4 31B (leaderboard) | 76.85 | 82.85 |

Gemma 4 E4B is not listed on the leaderboard. The leaderboard models were not run with this study's 4-bit
model file or inference settings, so Table B4 gives context rather than a controlled comparison. Overall and NLG
scores are not compared, for two reasons. The leaderboard's overall score includes competencies outside
BATAYAN, and this study scored translation with ChrF++ instead of the leaderboard's MetricX-24.

### Discussion

BATAYAN defines no passing score; it compares models with one another and with chance. Judged against chance,
the model was strongest on the two skills Bintanong relies on most. It answered 87.0% of the Filipino reading
comprehension items correctly (normalized 82.67), which tests understanding a Filipino passage and answering
from it. It answered 93.3% of the causal reasoning items correctly (normalized 86.53). Sentiment analysis was
moderate (normalized 62.25) and natural language inference was middling (51.50). Paraphrase identification
(30.50) and toxicity detection (32.00) were weak. Both are yes-or-no tasks, so 65–66% accuracy is only modestly
better than guessing. Neither task is part of Bintanong's role, because the system answers questions from
reviewed documents rather than judging paraphrases or moderating content.

Translation reached ChrF++ 61.43 from English to Filipino and 68.44 from Filipino to English. This is relevant
because Bintanong reads Filipino and Taglish questions about English source documents. Summarization scored a
ROUGE-L F1 of 21.87. Its recall (41.71) was much higher than its precision (15.22), which suggests summaries
longer than the references. Bintanong does not summarize freely: it quotes reviewed source fields, and the
faithfulness of that output is measured by RAGAS.

Compared with the leaderboard (Table B4), the 4-bit E4B scored higher than Gemma 4 E2B on reasoning and lower
on understanding. Both scores were well below the much larger Gemma 4 31B. This places the model within the
range of small open models. The lower NLU score could come from 4-bit quantization, from turning thinking off,
or from greedy decoding. These causes were not separated in this study.

Limitations: each item was answered once, with deterministic decoding. As a check, Sentiment was also run on
another machine (RTX 3050, 4 GB) with the same model and settings and gave Macro F1 73.48, against 72.80. This
suggests that hardware changes the scores by less than one point. Translation was scored with ChrF++ because
the MetricX-24 judge model (13 billion parameters) does not fit the available GPUs. Summarization was not
scored with BERTScore. The benchmark's items are Filipino (Tagalog); Taglish competence is reflected only
indirectly, through translation and through the Taglish queries in the RAGAS and F1 evaluations. The planned
comparison against the baseline Bintu-1 model was not carried out for BATAYAN.

---

## Chapter 5 entries

### Summary of Findings (BATAYAN)

- On the BATAYAN Filipino benchmark (3,800 items, zero-shot), Bintanong's model (Gemma 4 E4B, 4-bit) scored
  NLU 58.47, NLR 69.01, NLG 43.40 and Safety 32.00, for an overall normalized score of 50.72.
- It was strongest in Filipino reading comprehension (87.0% accuracy) and causal reasoning (93.3%). It was
  moderate in sentiment analysis and natural language inference, and weak in paraphrase and toxicity detection.
- Translation reached ChrF++ 61.43 (English to Filipino) and 68.44 (Filipino to English).
- Its NLR score was higher, and its NLU score lower, than Gemma 4 E2B's on the SEA-HELM Tagalog leaderboard.

### Conclusion (BATAYAN)

The language model inside Bintanong has strong Filipino reading comprehension and reasoning, the capabilities
it most needs to interpret student questions and work with institutional text. Its weaknesses lie in tasks
outside Bintanong's role, such as paraphrase and toxicity detection. Its overall Filipino competence is in the
range of small open models.

### Contributions

- A BATAYAN evaluation of a 4-bit quantized Gemma 4 E4B, a model not listed on the SEA-HELM leaderboard, run
  with the inference settings of a deployed advisory system on consumer laptop GPUs.
- A reproducible run kit (SEA-HELM commit, recorded local changes, fixed package versions and server
  settings), with which a second machine reproduced the Sentiment result within one Macro F1 point.

### Recommendations

- Score translation with MetricX-24 and summarization with BERTScore when a larger GPU is available, so that
  NLG results can be compared with the leaderboard.
- Repeat the benchmark with thinking enabled and with full-precision weights, to measure what quantization and
  the latency-oriented settings cost in Filipino competence.
- Run the baseline Bintu-1 model through the same benchmark, as planned in Chapter IV.
- Add a Taglish (code-switched) evaluation set, since BATAYAN's items are in Filipino only.
