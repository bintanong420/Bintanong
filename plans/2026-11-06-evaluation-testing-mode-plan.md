# Evaluation testing mode: feasibility and proposed plan

Status: proposal awaiting owner decisions. Nothing implemented. Not a numbered phase.
Purpose: measure the thesis metrics Phase 12 reported as not measured (Accuracy, Precision, Recall, F1), with
RAGAS/BATAYAN later. Owner runs queries in the website, saving agent tokens.
Context consulted: thesis physical 17-18 (scope) and text on evaluation metrics; master 17.3; Phase 12 report section 7.

## Findings

- `research.py:35`: runtime already uses top_k=3, min_similarity=.25 (uncalibrated).
- Topic filter runs before kNN (`p_chunk_ids`, `engine.py`; narrowed further by requested claims). In the 560-chunk
  package: 145 topics, median 2 chunks; 39% have 1, 61% have <=3, 91% have <=8. As-run top 3 therefore often returns
  the whole topic, so it mostly measures the router's topic choice rather than kNN.
- Control and Symbolic-only turns run no retrieval. Several topics mean several top-3 sets, each with its own query.
- `_trace` (`engine.py`) logs ids/similarities only, has no request link, and is skipped on early returns.
- `evaluation/retrieval.py` already has P@k/R@k from `gold_chunk_ids`; lacks F1/Hit@k; rejects non-dev splits.
- `routed_sink` already exposes the route per turn. `student-proxy.ts:8` allowlists paths.
- Roster: `Context/The_Bintanong_Benchmark_Queries (4).pdf`, SHA-256 `be467633...a9a3`, the same hash recorded on
  5 November. Subset A rows 1-10 (30 variants, rule-based); Subset B rows 11-24 (42 variants, retrieval).
- Round-4 export/audit named in the plans is not on this machine.

## Owner decisions (6 November 2026)

- Roster stays the 24 x 3 = 72 queries; no added questions. Consequences to disclose: no out-of-scope or unanswerable
  case, so correct refusal is not measured; questions informed earlier fixes, so these are development results.
- Queries are typed one at a time; no batch runner.
- Page shows both top-3 lists: topic-bound and all-chunk.
- Answer keys are prepared and shown where possible; where a question has no acceptable key, humans judge it.
- Row 10 is treated as a Handbook (RAG) question. Candidate clause: `handbook_prerequisite_policy`, page 31.
- Implementation plan: [tasks](2026-11-06-evaluation-testing-mode-implementation.md). Execution not yet approved.

## Metric definitions (master 17.3: define unit, positive class, denominator, averaging)

| Level | Unit | Metrics | Gold needed |
| --- | --- | --- | --- |
| Route | query | Accuracy, per-class P/R/F1, macro-F1, confusion matrix | one expected route per question |
| Retrieval | ranked chunk per query, RAG/Hybrid only | P@3, R@3, F1@3, Hit@3 (MRR optional) | relevant chunks per question, set independently of top 3 |
| Final answer | query | Accuracy = (correct answers + correct refusals)/all; P = correct answers/answers given; R = correct answers/answerable; F1 | answerable or not; verified answer; owner mark |

Chunk-level accuracy is not reported: about 557 true negatives per query make it near 100% regardless of quality.
Report by language and category. Disclose that P@3 ceiling is .33 and F1@3 ceiling .50 when one chunk is relevant.

## Proposed design

1. Dedicated `POST /evaluation/run`, mounted only with an explicit launcher flag on the dev API; off means 404. Plus
   an evaluator credential, proxy allowlist entry, and a `/dev/evaluation` page. Student `/chat`, stream and transport
   schema stay unchanged.
2. Per-request observer through existing seams, so the student answer path behaves the same.
3. Each run: fresh session (no memory carry-over), uploads off, serial admission kept, student rate limit not consumed.
4. Record per run: commit, release, embedding set, question, language, route, topics; per retrieval the query, as-run
   top 3 and unfiltered top 3 (rank, chunk id, similarity, full text, source, used-in-answer flag); answer, citations.
5. Page: single question box, answer, the chunks, relevance and answer marks, JSON/CSV export.
6. New offline scorer `evaluation/system_metrics.py`; `evaluation/retrieval.py` re-sorts by threshold and is left as is. Saved records keep what RAGAS needs later.

## Tasks (TDD; dependency order)

1. Freeze roster and write gold labels (expected route; answerable; relevant chunks pooled from topic bindings plus
   top 8 unfiltered kNN). Retrieval keys cover rows 11-24; row 10's route must be decided. Language variants of a row
   share gold unless wording differs: rows 15, 18, 20 differ materially; check 12, 13, 14.
2. Metric scorer with synthetic fixtures, including ceilings and zero-denominator handling.
3. Observer plus evaluation route; regressions: flag off is 404, student stream byte-compatible, no private content.
4. Dev page and export; browser check on dev ports.
5. Pilot of 5 questions; owner run on a frozen commit; scored report; update Phase 12 section 7.

## Risks and limits

Single-author
labels are disclosed. Mode must never reach gathering/main. Shadow unfiltered kNN is observation only, never evidence.
Baseline Bintu-1 comparison (thesis) is not covered. RAGAS evaluator model needs a separate owner decision.
