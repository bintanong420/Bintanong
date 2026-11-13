# RAGAS follow-up notes (8 November 2026)

Notes for later; rendered to `ragas-followup-notes-2026-11-08.pdf` by `scripts/build_section_pdf.py`.
Diagnostic scripts: `scripts/inspect_ar_fc.py`, `scripts/expanded_reference.py`, `scripts/reverify_fc.py`
(raw outputs stay in ignored `audit-evidence/ragas-20261107/`). Nothing reported has changed.

---

## RAGAS Follow-up Notes (8 November 2026)

These notes collect what was found after reviewing the low Answer Relevancy (0.584) and Factual Correctness
(0.570) scores, the decision taken, and the manuscript changes still to be made. No reported score has changed.

### 1. Decision: Option A

- Keep the reference answers as they are: the verbatim text of the passages judged relevant (TP or FN) in the
  F1 evaluation. Do not add the neighbouring chunks to them.
- Keep the reported scores: Factual Correctness 0.570 and Answer Relevancy 0.584.
- Explain the scores in the RAGAS Discussion (wording in Section 5).
- Bintanong is unchanged. It still retrieves the top 3 chunks and attaches their required neighbours.
  Faithfulness (0.883) stays measured against that full evidence.
- The BERTScore developer keeps the same references.

Option B (rebuilding the references with the neighbour chunks and re-scoring) was rejected for four reasons:

- Changing the ground truth after seeing a low score invites the question "did you change the reference
  because you did not like the result?"
- The expanded reference would be built from the same neighbour links that Bintanong uses, so a wrong link
  would be shared by the answer and the reference and hidden by the score.
- Context Recall would drop, because it checks the reference against the top 3 retrieved chunks only.
- F1, RAGAS and BERTScore currently share one human-judged ground truth.

The BERTScore results do not decide this either way, because they are scored against the current references.

### 2. Why Factual Correctness is 0.570

Each reference contains only the passages judged in the F1 sheet, which are the top-ranked search results.
Bintanong also attaches each result's required neighbours, so its answers include the remaining steps of the
same procedure. Those steps are correct, but they are not in the reference, so RAGAS counts them as false
positives.

Example: the reference for Query 4 (adding or changing subjects) holds only step 1 of the Charter procedure.
The answer correctly gives all four steps, and 20 of its claims were marked "not in reference", for a score
of 0.29.

Diagnostic check: the same answer claims were re-checked against fuller references, with no answer regenerated.

| Reference given to the judge | Factual Correctness |
| --- | ---: |
| As reported: F1-judged passages only (re-run) | 0.579 |
| Plus the rest of each procedure (required neighbours) | 0.794 |
| Plus reviewed field labels (keeps table headers such as "2nd Offense") | 0.895 |

Large changes: Query 4 from 0.26 to 1.00, Query 10 from 0.35 to 0.98, Query 1 from 0.63 to 0.96-1.00, and
Query 9 from 0.33 to 0.89 once the offence-column headers are kept. Still low afterwards: Query 13 (its "selected
steps" and "confirm with the office" notices), Query 8 Taglish (a real wording slip, see Section 4) and
Query 2 English (0.62, not checked claim by claim).

### 3. Why Answer Relevancy is 0.584

- **Noncommittal rule.** Seven answers scored 0 (Queries 5 and 6 in all three languages, and Query 13 in
  Taglish). They quote the source, state the recorded source limitation (for example, conflicting INC
  completion deadlines) and refer the student to the office, which the source-gap policy requires. RAGAS
  sets the score to 0 when all three judge calls label an answer noncommittal. This is unstable: in the re-run,
  Query 13 Taglish scored 0.54 instead of 0.
- **Language gap.** The judge always writes its generated questions in English, so Tagalog and Taglish
  questions look less similar to them. Measured against the English wording of the same question (non-zero
  rows only), the three languages are nearly equal:

| Language | Cosine with the row's own question | Cosine with the English wording |
| --- | ---: | ---: |
| English | 0.768 | 0.768 |
| Tagalog | 0.640 | 0.745 |
| Taglish | 0.697 | 0.748 |

- **Normal ceiling.** Even good English answers reach about 0.75-0.9. The generated questions are more specific
  than the student's (for example "...at OSAS according to the Handbook?"), and some answers are broader than the
  question: Query 1 asks about dropping and receives the full change/add/drop procedure.

### 4. Low Faithfulness rows (checked statement by statement)

- Query 13 (0.57-0.70) and Query 14 (0.65-0.70): all policy content is supported. The unsupported statements
  are host-added notices ("selected office steps", "confirm with the relevant office", "shown exactly as
  printed"), source labels the judge cannot verify ("based on the Citizen's Charter", "(Handbook)"), and one
  judge misreading: "Total: None · about 3 Minutes" was read as "total time is none" (None is the fee).
- Query 8 Taglish (0.40-0.50): a real error. The Handbook says the student "shall report such loss to the
  Security Personnel **or** secure for a temporary pass". The answer says "mag-report ng loss sa Security
  Personnel **para** makakuha ka ng temporary pass" ("so that you get a temporary pass").
- Two small system issues (not fixed): Query 14's notice says "part of the cited source is cut off or unclear",
  but its recorded limitation is a total-time mismatch (1 day + 15 minutes against a printed 3 minutes). The
  total line should label the fee and the time separately ("Fee: None · Time: about 3 minutes").

### 5. Manuscript changes still to make

**(a) Chapter III, after the argmax_k formula: new subsection "Required-Neighbour Expansion".** The manuscript
currently says that exactly k chunks are passed to the model, which does not match the implementation.

Draft text: Long procedures and tables in the institutional documents span several chunks. During source review,
each chunk that cannot be understood without other chunks records them as required neighbours, for example a
procedure that continues across pages or a penalty row that depends on a shared clause. These links form a
dependency graph G = (V, E), in which each chunk is a node and each required-reading link is a directed edge.
Links connect only chunks from the same source version. After the top-k search, the system adds to each
retrieved chunk every chunk reachable from it in G:

  C(q) = union of Closure(c) over every chunk c in TopK(q)

where Closure(c) is c together with all chunks reachable from c through required-reading links. Each closure is
passed to the language model as one complete group, in printed order. If any member is missing, or the group
does not fit the context budget, the whole group is withheld and the gap is recorded; no clause is truncated.
The value of k therefore limits the number of search results, while the expansion ensures that each result
reaches the model complete.

**(b) Definition of Terms.**

- *Top-k Retrieval* (corrected): the selection phase of the KNN algorithm in which the k document chunks with the
  highest similarity to the student's query are selected. Each selected chunk is then passed to the language
  model together with its required neighbours.
- *Required neighbour* (new): a chunk that must accompany another chunk for it to be understood correctly, such
  as the continuation of a procedure or a shared clause. Recorded during human source review.

**(c) Figure 3.5.** Add a step after top-k retrieval: "Expand required neighbours, then assemble complete groups".

**(d) RAGAS section, Discussion, Factual Correctness paragraph (replace).** Factual Correctness (0.570) was
moderate. The reference for each query contains only the passages judged in the retrieval evaluation, which
are the top-ranked search results. Bintanong, however, also attaches each result's required-neighbour passages
(Chapter III), so its answers usually include the remaining steps of the same procedure. Such steps are
correct but absent from the reference, and RAGAS counts them as unsupported. For example, the reference for
Query 4 contains only the first step of the adding/changing procedure, while the answer correctly gives all
four steps. The metric therefore reflects the coverage of the reference rather than errors in the answers.
Optional sensitivity sentence: When the reference was extended to the complete procedures containing the judged
passages, Factual Correctness rose to 0.79.

**(e) RAGAS section, Discussion, Answer Relevancy paragraph (add).** The judge generates its questions in
English. Measured against the English wording of the same queries, the Tagalog and Taglish answers scored
0.745 and 0.748, close to English (0.768), so the language difference in Answer Relevancy mainly reflects
the comparison across languages rather than lower answer quality.

### 6. Likely panel questions and short answers

- *Why is Factual Correctness low?* The reference holds only the judged passages; Bintanong also passes each
  passage's required neighbours (Chapter III), so its correct extra steps count against it. Show Query 4.
- *Does attaching neighbours bypass k?* No. k limits the number of search results; the neighbours are not
  searched. They are fixed, reviewed links that complete each result, a form of parent-document or
  small-to-big retrieval.
- *Why not put the neighbours in the reference?* The references come from the independent human relevance
  judgments shared by the F1, RAGAS and BERTScore evaluations. Building them from the system's own links would
  be circular.
- *Why are seven Answer Relevancy scores 0?* RAGAS treats a stated source limitation plus an office referral as
  noncommittal, but the study requires that disclosure whenever the source is incomplete or conflicting.
- *Is the neighbour design a new algorithm?* No. It applies graph reachability (transitive closure), a standard
  technique. What is specific to Bintanong is that the links are human-reviewed, version-consistent and
  assembled all-or-nothing, and that faithfulness was evaluated against this expanded evidence.

### 7. Scope advice

Keep the contribution modest ("applied and evaluated a dependency-aware retrieval design"), not "a new
algorithm". A literature search and a no-neighbour ablation would be needed for a novelty claim; they are
optional graduate-level extras, not needed for this thesis.
