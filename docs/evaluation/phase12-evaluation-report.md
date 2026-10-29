# Bintanong evaluation report (Phase 12)

30 October 2026. Research build, not a deployed or university-approved system. Raw outputs are in the ignored
`audit-evidence/p12-benchmark-20261029` folder; every number below comes from a file there or from a linked record.
Questions: [benchmark-questions.md](benchmark-questions.md). Accepted input forms and robustness sets:
[accepted-input-forms.md](accepted-input-forms.md). Run log and fixes: [results record](../../plans/2026-10-29-phase12-benchmark-results.md).

## 1. What was compared

| Condition | What it has | Status |
| --- | --- | --- |
| A: plain Gemma (Bintu-1 base) | Same Gemma 4 E4B artifact (Q4_K_XL) and greedy decoding, a one-line assistant prompt, no documents or rules | run |
| B: Gemma + retrieval, no rules | — | not run (owner, 29 Oct) |
| C: full Bintanong | LLM routing, document retrieval (local 560-chunk package), Prolog prerequisite rules over 39 curricula, answer validation | run |

A versus C is a whole-system comparison. It does not show that the Prolog rules alone caused any difference.

## 2. Benchmark

50 questions in the owner's four categories: enrollment procedures (14), prerequisite eligibility (14), grade
policies and academic standing (12), disciplinary policies (10). Owner-approved layout (v2): 24 English, 16 Taglish,
10 pure Tagalog. Each case lists the printed facts that must appear, and where relevant the expected status
(answered, clarification, insufficient evidence) or eligibility decision.

- 40 cases were reused from the development gate: the system was tuned on them, so their scores are optimistic.
  10 disciplinary cases were new (from printed Handbook penalty rows); 2 later fixes were made after seeing them.
- No usage data exists, so "common questions" is a judgement, not a measurement.
- Expectations were written and scored by the author. There was no second rater and no agreement measure.

## 3. Results

### Main benchmark v2 (code `cb82c53`)

| Group | C full system |
| --- | ---: |
| Enrollment procedures | 11/14 |
| Prerequisite eligibility | 12/14 |
| Grade policies and academic standing | 8/12 |
| Disciplinary policies | 7/10 |
| English / Taglish / Tagalog | 20/24 / 9/16 / 9/10 |
| **All** | **38/50 (76%, Wilson 95% 63–86%)** |

### Full system versus plain Gemma (original 50: 24 English / 26 Taglish)

Condition A was run on the original English/Taglish 50, so the paired comparison uses that set.

| | Passed | Wilson 95% |
| --- | ---: | --- |
| C full system (`7f8c02b`) | 40/50 | 67–89% |
| C rerun (`cb82c53`) | 39/50 | 65–87% |
| A plain Gemma, strict (facts and expected status) | 3/50 | 2–16% |
| A plain Gemma, facts only | 8/50 | 8–29% |

Paired exact McNemar test on the same 50 cases: C passed 37 cases that A (strict) failed, and A passed none that C
failed (p ≈ 1.5 × 10⁻¹¹). Against A facts-only: 32 versus 0 (p ≈ 4.7 × 10⁻¹⁰). Plain Gemma cannot ask for
missing facts, decline, or run a prerequisite check, which is what the strict score measures.

### Run-to-run variation

Each condition was run once per case (owner, 30 Oct; master 17.4 proposes five runs). The C rerun on the same 50
differed in one case (absence, Taglish): the topic selector chose "leave of absence" instead of "attendance" on a
byte-identical request. Eight replays on the same server build all chose attendance, so this was one-off server
non-determinism, not a code change (paired p = 1.0). Treat single-run scores as roughly ±1 case.

### Robustness sets (reported separately, not part of the 50)

| Set | Result | Note |
| --- | ---: | --- |
| Pure Tagalog twins of the Taglish questions | 19/26 | Same as the Taglish wording (19/26); all replies in Taglish |
| Shorthand Taglish (pwd, pno, ung, …) | 15/26 | 8/26 before the reviewed shortcut list; the list was built after seeing these questions, so 15/26 is optimistic |
| Loosely typed English | 2/4 | Too few to generalise |

## 4. Where the full system still fails (v2, 12 cases)

| What happened | Cases |
| --- | --- |
| Answered, but without the expected printed fact | summer load (en, Taglish: 12 units / Dean), leave length (Taglish: one academic year), graduation residence (en, Taglish: answers a different residence clause), absence (Taglish: run-to-run variation above) |
| Asked for clarification instead of answering | plagiarism (en, Taglish: router asks about a not-stated item although the printed penalty is listed), BSIT failed course (Tagalog) |
| Said the evidence was insufficient | CC 5 after failing CC 4 (en: the router dropped the course mentions), second-year standing (Taglish), improper uniform (Taglish) |

Causes not in brackets above were not diagnosed further.

## 5. Response time

Warm inner pipeline time (model already loaded; excludes encoder start-up, API, browser, network and queueing).
This is not the time a student waits.

| Run | Median | p95 | Max |
| --- | ---: | ---: | ---: |
| C full system (`7f8c02b`) | 26.4 s | 35.5 s | 44.1 s |
| C rerun (`cb82c53`) | 26.8 s | 36.8 s | 40.7 s |
| C Tagalog set | 27.6 s | 41.3 s | 44.6 s |
| A plain Gemma | 6.9 s | 9.4 s | 11.5 s |

The proposed 15–20 s warm target ([recommendation](../../Context/response-time-recommendation.md)) is not met.
Accuracy safeguards were not traded for speed.

## 6. Other evidence carried from earlier phases

- 91-case development gate: 77/91 (run 4), then honors/probation fixed (+4 live); see the
  [gate record](../../plans/2026-10-28-simple-question-gate-results.md).
- Private files: session isolation, no reach from institutional search, memory-only storage, deletion; covered by
  tests (Phase 10 [handoff](../../plans/phase-10-handoff.md)) and one live upload → confirm → follow-up → delete run
  (Phase 11 [handoff](../../plans/phase-11-handoff.md)). Photo uploads are unsupported.
- Automated test suite: see the Phase 12 handoff for the final full-suite result.

## 7. Thesis metrics not measured in this build

| Metric (master 17.3) | Why not |
| --- | --- |
| Route accuracy / per-class F1, entity slot F1 | No per-case gold route or slot labels were recorded for the 50 |
| Retrieval Precision@k / Recall@k | No relevance judgements per retrieved chunk |
| RAGAS faithfulness / relevance | Needs an evaluator model, which is a new dependency; not approved |
| BATAYAN language tasks | Not run |
| Unsupported-claim rate | No per-claim annotation; see the observation in section 4 |
| Condition B (retrieval without rules) | Skipped by the owner |
| Five repeated runs, blinded raters, inter-rater agreement | Single runs and a single author scorer (owner, 30 Oct) |
| SUS and UAT with 30 students | Not conducted |
| Cold start, per-stage latency, peak RAM/VRAM, throughput | Not measured in the benchmark runs |

## 8. Limits of these results

Fifty questions do not cover PalSU policy. Most cases were used during development. One author wrote and scored
the expectations. Results come from the research data release (local 560-chunk document package; hosted
curricula), whose known source gaps remain. Hosted activation of the 560 package is pending; the
[activation preflight](../../plans/2026-10-30-hosted-560-activation-results.md) verified the sealed hosted
configuration, but the owner-supplied connection setting is missing. No hosted activation or smoke result is claimed. No
university office has validated any answer, and nothing here shows the system is ready for students.
