# Manuscript versus system: alignment notes and possible contributions (8 November 2026)

Rendered to `thesis-alignment-2026-11-08.pdf` with `docs/evaluation/ragas/scripts/build_section_pdf.py`.
Sources compared: `Context/bintanong_thesis_for_context.pdf` (printed page numbers below), the original routing figure
`Context/bintanong_full_runtime_routing_architecture.png`, the current figure
`Context/bintanong_current_runtime_architecture.png`, `docs/evaluation/phase12-evaluation-report.md`,
`plans/owner-decisions-ledger.md`, the 27 Oct reply-language decision, the Phase 10 handoff, the RAGAS/BATAYAN
results and the backend code. Novelty statements are not backed by a literature search.

---

## Bintanong: Manuscript Alignment and Possible Contributions

Prepared 8 November 2026. This compares what the manuscript (Context folder) says with what the built system does,
and lists what may count as a contribution. Page numbers are the printed page numbers of the manuscript. Nothing
here changes the system; it lists manuscript edits to make.

### 1. Critical: manuscript claims that contradict the system

These six items should be corrected before the defence. A panel member who compares Chapter III with the system
or the evaluation chapters would find each of them.

**C1. Prolog "deny when unproven" versus Bintanong's unknown-versus-unmet rule (pp. 42–43).** The manuscript
explains Negation as Failure under the Closed World Assumption: if Prolog cannot prove that a student passed
CC4/L, the condition is treated as false and the student "cannot be considered eligible". It adds that the system
"defaults to deny" when records are incomplete and calls the symbolic layer "a mathematically hard constraint".
The system does the opposite for missing information. A missing grade, curriculum, course identity or rule is
reported as **unknown** (Bintanong asks for it or says it cannot determine eligibility), and only a documented
failed or missing requirement is reported as **unmet**. "No recorded prerequisite" is not treated as proof that a
course has none, except for the owner's 4 November rule that a blank prerequisite cell in a reviewed prospectus
means none. *Change:* keep the CC5/L example, but say that an unproven condition yields "cannot determine;
please provide your grade" rather than "not eligible". Present the three outcomes (eligible, not eligible,
unknown) and replace "mathematically guarantee" and "hard constraint" with "the verdict is computed by
deterministic rules and cannot be changed by the language model". This is also one of the study's stronger design
points (Section 5).

**C2. "Exactly k chunks" reach the model (pp. 23 and 33–35).** The Definition of Terms and the KNN section say
that exactly k chunks are passed into the language model. Bintanong selects the top k = 3 by cosine similarity, then
attaches each hit's reviewed required neighbours and passes each group whole or withholds it. *Change:* add the
"Required-Neighbour Expansion" subsection, formula and corrected definitions drafted in
`docs/evaluation/ragas/ragas-followup-notes-2026-11-08.pdf` (Section 5a–5c).

**C3. Order of generation and symbolic checking (p. 58).** The manuscript says the language model first writes a
"preliminary response" from retrieved chunks, and the symbolic layer then validates that response. In the system,
the order is reversed. The Prolog check runs first; the host writes the verdict in fixed wording; the model only
explains it and drafts document answers; and output validation then checks citations, language and coverage
(one repair, then a fallback reply). The original routing figure already shows symbolic results entering
integration before generation, so p. 58 contradicts both the figure and the code. *Change:* rewrite the
Processing paragraph to follow the current architecture figure.

**C4. Deployment (pp. 18 and 62).** The manuscript plans final deployment to Vercel on entry-tier cloud hosting.
The owner cancelled public deployment (Phase 13). The system ran locally (web, API, llama.cpp model server), with
Supabase hosting the knowledge release, and was exposed temporarily through ngrok for testing. *Change:* describe
it as a research build tested locally and over a temporary tunnel, not a deployed service, and adjust the
cloud-hosting limitation.

**C5. Photo uploads and the OCR accuracy placeholder (pp. 55–57, 77).** The manuscript describes users uploading
grade photos that Docling reads, and reports a Docling character accuracy of "[X]%" on 10 scanned documents. Photo
and scan uploads are unsupported: the photo OCR probe misaligned grade rows on tilted and perspective photos, so
the system returns `photo_ocr_unavailable`. Private uploads are text PDFs only (memory-only, session-isolated,
deletable). The 10-document OCR check was never run, so "[X]%" has no value. Docling is used offline, together
with human review, to prepare the institutional documents. *Change:* remove the "[X]%" sentence (or run the
check), restate uploads as PDF-only, and move Docling to the ingestion pipeline description.

**C6. The architecture figure.** The manuscript's routing figure is the original design. The current figure
(`Context/bintanong_current_runtime_architecture.png`) adds request admission (5 questions per 5 minutes; 1
answering, up to 4 waiting), session context, query preparation pinned to one knowledge release, a source-aware
evidence check, host checks with one router repair, control outcomes (clarification, scope notice, unavailable
information, office referral) and the fallback reply. *Change:* use the current figure and describe the added
steps (Section 3).

### 2. Important: differences in scope, language and set-up

- **Reply language.** The owner decided on 27 October that replies are English or Taglish only: an English
  question gets an English reply; a Filipino or Taglish question gets a Taglish reply. Filipino input is still
  understood. The manuscript accepts English, Filipino and Taglish queries but never states this reply rule.
  State it, with its purpose (less language handling and faster responses; the benefit was not measured).
- **Corpus.** The manuscript lists the Student Handbook, Citizen's Charter, USG and CSG policies. The release
  contains the Handbook, the Charter, Charter additions (vehicle/gate pass, special-class fee, enrolment), the USG
  Constitution and election material, and reviewed curricula (39 curriculum links). College CSG constitutions
  were never supplied, so describe "CSG" only as the CSG provisions inside the USG source. Corpus size: 560
  reviewed chunks.
- **Undergraduate scope.** Medicine, Law, graduate programs, the laboratory school and staff-only procedures are
  excluded, and such requests get a scope notice. The manuscript states this (p. 17); keep it consistent in the
  evaluation chapters.
- **Benchmark design (p. 70).** The manuscript promises at least 50 queries in five categories. The benchmark has 50
  queries in four categories, because grade policies and academic standing were combined. Of the 50, 40 were reused
  from the development gate (so they are optimistic), and one author wrote and scored them. Separately, the F1 sheet
  covers 42 retrieval rows (14 RAG queries times three languages).
- **Hardware (pp. 76–77).** The manuscript lists an i7-12650H, 32 GB RAM and an RTX 4060 8 GB. Most development,
  the RAGAS answers and the first BATAYAN attempt ran on a laptop with an RTX 3050 4 GB and 16 GB RAM; the full
  BATAYAN run used an RTX 4060 8 GB machine. State which machine produced each measurement, especially response
  times.
- **Inference settings.** Not described in the manuscript: Gemma 4 E4B (Q4_K_XL GGUF) on llama.cpp, temperature 0,
  thinking mode off (`reasoning_effort` none, thinking token banned) and prompt caching. Bintu is guided by prompt
  engineering only, with no fine-tuning, consistent with p. 19. Add these settings to the methodology.
- **Response time.** The warm pipeline median was 26.4 s (p95 35.5 s) against the proposed 15–20 s target, while
  plain Gemma took 6.9 s. The limitation on p. 18 should cite these numbers; accuracy safeguards were not traded
  for speed.

### 3. System features not in the manuscript

Add these to the system description. Each is implemented in the research build.

- **Required-neighbour retrieval** with all-or-nothing assembly (C2).
- **Source-gap handling.** Clipped, missing or conflicting source content is recorded with the affected evidence
  and stated in the answer (for example, conflicting INC completion deadlines). Bintanong does not fill gaps.
- **Human-reviewed field-level chunks.** Charter service tables are stored as reviewed fields, so each step stays
  linked to its fee, time, responsible person and office, together with recorded source limitations.
- **Reviewed curriculum ledgers compiled to Prolog.** Prerequisites are authored once as reviewed records, from
  which versioned Prolog bundles are generated, rather than as hand-written rules per course.
- **Multi-part questions.** The router splits a message into parts: eligibility parts go to Prolog, procedure
  parts go to retrieval, and the whole message runs as Hybrid with one answer slot per part.
- **Host-worded verdicts and output validation.** The verdict text is fixed by the host; the model cannot change
  it; citations, language and coverage are checked, with one repair before a fallback reply.
- **Course-code short forms** ("CC5", "CC 5", "CC5/L" resolve to "CC 5/L" within the student's curriculum).
- **Session context and multi-turn follow-ups.** Stated results and pending checks are kept in a temporary session,
  separate from institutional knowledge.
- **Rate limiting and queueing** (request admission, C6).
- **System-information route.** Bintanong can describe its own capabilities, scope, limits and pending
  university validation in English or Taglish.
- **Academic Recovery Planner (bounded).** Students can check a proposed recovery plan against reviewed curriculum
  and Handbook rules; drafts are labelled as needing university approval.
- **Private PDF uploads**: memory-only, session-isolated, not indexed, deletable (photos unsupported, C5).

### 4. Research questions and evaluation status

| Research question | What the manuscript planned | What was done | Gap to disclose |
| --- | --- | --- | --- |
| RQ1 Development | Integrated Taglish NLP, RAG, Prolog | Built and tested (research build) | Not deployed; not university-validated |
| RQ2 Full system vs Bintu-1 | Same benchmark, prompt, model, decoding | 50 cases: full system 40/50 vs plain Gemma 3/50 strict (McNemar p ≈ 1.5e-11) | Retrieval-only condition skipped, so the gain cannot be attributed to the symbolic layer alone; single runs |
| RQ3 RAG quality | Accuracy, Precision, Recall, F1; RAGAS | F1 sheet: macro P .8155, R .8099, F1 .7858; RAGAS faithfulness .883, context precision .896 | Recall pooled (overstated); one judge run; no Bintu-1 comparison for RAGAS |
| RQ4 Tagalog/Taglish/messy/vague | Accuracy per language, clarification | Benchmark per language (English 20/24, Taglish 9/16, Tagalog 9/10); robustness sets; BATAYAN (overall 50.72) | Shorthand result optimistic; BATAYAN measures the model only; BATAYAN items are Tagalog, not Taglish |
| RQ5 Private-file safeguards | Unauthorized access, cross-session, indexing | Unit tests plus one live upload/delete run | No formal security test protocol; photos unsupported |
| RQ6 Usability | SUS and UAT, 30 students | Not conducted as of the Phase 12 report (30 Oct) | Confirm current status |

Also promised but not measured: route accuracy and entity slot F1, unsupported-claim rate, five repeated runs,
blinded raters and inter-rater agreement, cold-start latency, per-stage latency and peak RAM/VRAM. BERTScore is
being computed by another developer; it is not named in the manuscript's Chapter IV, so add it there if it is
reported.

### 5. Possible contributions

None of these is a new algorithm, and none has been checked against the literature. They are applied design and
evaluation contributions, which suit an undergraduate applied-research thesis. Listed from strongest evidence to
weakest.

- **(1) Evaluation finding for RAG systems that expand their context.** Faithfulness measured against the top 3
  chunks was 0.525; measured against the evidence the generator actually received (hits plus neighbours, as
  reviewed fields) it was 0.883. Factual Correctness moved from 0.579 to 0.794–0.895 when the reference covered
  whole procedures. Standard RAGAS practice scores against the top-k chunks, which can understate systems that
  expand their context. Evidence: in hand. Caveat: same answers, one judge.
- **(2) Three-valued eligibility instead of closed-world denial.** Unknown is kept separate from unmet, so missing
  student data or missing rule coverage produces a request or an "unknown" result, never a false denial or
  approval (C1). This is a deliberate departure from plain Negation as Failure for advising with incomplete
  records. Evidence: implemented and tested; argued in the design.
- **(3) Dependency-closed retrieval.** Human-reviewed required-reading links between chunks, expanded after top-k
  search, kept version-consistent, and assembled all-or-nothing with a recorded gap. Related to parent-document,
  small-to-big and auto-merging retrieval; what is specific here is the reviewed links and the completeness
  guarantee. Evidence: implemented; no ablation (no-neighbour answers were never generated).
- **(4) Source-gap-aware answering.** Recorded defects in official documents travel with the evidence and are
  disclosed in the answer instead of being filled in by the model. RAGAS penalises this as "noncommittal", which
  is itself a finding about generic RAG metrics (seven Answer Relevancy zeros).
- **(5) Host-worded symbolic verdicts.** The language model explains a Prolog verdict but cannot change it.
- **(6) Localized evaluation results.** A BATAYAN run of a 4-bit Gemma 4 E4B, which is not on the SEA-HELM
  leaderboard, under deployed-system settings on laptop GPUs; and the finding that RAGAS Answer Relevancy
  understates Tagalog and Taglish answers, because the judge writes English questions (Tagalog 0.640 rises to
  0.745 with the English wording).
- **(7) Reproducible artefacts.** Shared verbatim references for RAGAS and BERTScore, and the BATAYAN run kit.

Suggested Contributions wording: "An applied neuro-symbolic advisory design for institutional documents that keeps
unknown separate from unmet, retrieves dependency-complete evidence and discloses source gaps; and an evaluation
procedure that scores generation against the evidence the generator actually receives."

### 6. What not to claim

- "Mathematically guarantees" correct guidance (p. 35). The benchmark passed 38/50 (76%).
- That the symbolic layer alone improved accuracy. The retrieval-only condition was not run.
- A new algorithm, or novelty in general, without a literature search.
- That neighbour expansion improves answer quality. No ablation was run; the 0.525 versus 0.883 result shows an
  evaluation effect, not an answer-quality effect.
- Deployment, school approval, or readiness for students.
- Photo support or any OCR accuracy figure.
- Filipino-only replies, or that BATAYAN measured Taglish.

### 7. Suggested order of manuscript edits

- First: C1 (unknown versus unmet), C3 (generation order) and C2 (neighbour expansion), because they change how the
  method is explained.
- Then: C5 (photos and OCR), C4 (deployment), C6 (figure), and the reply-language rule.
- Then: the evaluation chapter. Report each research question with what was done and the gaps in Section 4.
- Last: Contributions and Recommendations (Section 5), keeping the wording modest.
