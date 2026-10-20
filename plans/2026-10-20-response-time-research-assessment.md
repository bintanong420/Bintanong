# Response time for Bintanong's RAG and neuro-symbolic architecture

20 October 2026. Owner requests a researched judgment of sufficient response time
for this undergraduate study, specifically considering RAG and neuro-symbolic
processing, with **no sacrifice of accuracy for speed**. This is a research and
engineering assessment, not a university standard, owner-approved SLA or usability
result. Phase09 remains active. No architecture/source/release gate changes.

## Recommendation and present judgment

My proposed stopping target for latency optimization is a **typical warm, complete,
validated answer around 15–20 seconds**, preferably below10seconds for short
questions. A complex Hybrid answer taking20–30seconds can be a defensible research
prototype limitation if it preserves necessary checks and actual student evaluation
finds the delay acceptable. These ranges are my synthesis, not cutoffs established
by the papers below. They require local measurement and student validation.

I would not describe the current selected35–53second observations as a responsive
student chatbot. They remain valid evidence of a functioning, constrained research
prototype with a substantial performance limitation. A study can report an unmet
performance objective honestly; being an undergraduate project does not itself
establish that users find a long wait acceptable. Nor does a slower answer prove
more careful reasoning or higher accuracy.

Do not chase sub-second replies by replacing the LLM router, dropping necessary
retrieval/Prolog, shrinking away consequential evidence, bypassing the checker or
streaming unchecked answers. If quality fails, stop promoting the speed candidate.
The [short-reference experiment](2026-10-20-short-evidence-references-results.md)
follows that rule:strict mechanical mapping succeeded, but semantic output still
fails the quality gate, so canonical remains selected and full-chain timing stops.

## Primary evidence and what transfers

The review uses architecture research, a local educational RAG experiment and
controlled human-computer interaction work. Results and timing definitions differ;
none establishes a universal acceptable delay for a Filipino undergraduate chatbot.
Search results were used to locate primary publications; blog/vendor latency claims
and unrelated voice-agent figures were not used as acceptance evidence.

| Primary source | Method and finding used | Applicability and limit |
| --- | --- | --- |
| [Lugones et al., Aurora,2026](https://arxiv.org/html/2602.17999v1) | Advising system combines normalized curricular data, Prolog and LLM explanations. Authors report0.71s mean over20queries and describe five runs/query; experimental hardware i9-14900KF/RTX4070Ti/32GB, with DeepSeek-R1-Distill-Qwen-7B. | Closest architecture comparison. It shows that neuro-symbolic processing does not inherently require tens of seconds. Its synthetic benchmark, stronger hardware, model, prompting and inference path differ; the headline is author-reported and not reproduced here. Do not import its timing, planning scope or institutional rules. |
| [Hakim et al., SymRAG,PMLR284,2025](https://proceedings.mlr.press/v284/hakim25a.html), [preprint implementation discussion](https://arxiv.org/html/2506.12981v1) | Routes among symbolic, neural and hybrid paths using query complexity and resource information; evaluates reasoning benchmarks including HotpotQA/DROP. | Supports reporting route-specific cost and doing only required computation. It is not PalSU prerequisite authoring, a student usability experiment or a license to send a required Hybrid query through a cheaper path. Bintanong does not adopt its online utility/resource adaptation. |
| [Mishra and Brahmanapally,AI6(6):119,2025](https://www.mdpi.com/2673-2688/6/6/119) | Locally deployed course-catalog RAG comparison reports means7.17s for Llama3.2:3.21B,14.20s for Llama3:8B,16.43s for Llama3.1:8B and37.94s for Phi-4:14.7B; largest reported Phi-4 observation82.51s. | Educational/local RAG makes15–20s a plausible engineering research target. These are observed model timings, not student-approved thresholds. Different hardware, questions, outputs and validation prevent a direct ranking of Bintanong. Relevance ratings are not evidence of multilingual prerequisite correctness. Publication of38s results does not make38s desirable. |
| [Tan et al.,2026,CHI-associated author manuscript](https://arxiv.org/html/2604.06183v1) | Controlled experiment with240participants and2/9/20s **time to first token**, then streaming at25tokens/s, across Creation/Advice tasks. No significant latency effect on prompting;9s was rated more useful than2s, while20s elicited some frustration/reliability concerns. | Important counterevidence to treating10s as an absolute human tolerance limit. Does not establish that20s with no answer visible,35–53s buffered output or PalSU policy questions are acceptable. Perceived thoughtfulness is not factual correctness; no artificial waiting should be added. |
| [Schlechte et al.,QoMEX2025,DOI10.1109/QoMEX65720.2025.11219949](https://ieeexplore.ieee.org/document/11219949/) | Accessible publisher abstract reports2189ratings from178workers and non-linear effects of end-to-end latency and response length on waiting satisfaction. | Confirms that response length and total waiting belong in evaluation. Full paper was unavailable through the consulted endpoint; no exact threshold, unseen effect size or acceptability curve is inferred from the abstract. |
| [Zhang et al.,Explaining the Wait,CUI2024](https://repository.tudelft.nl/record/uuid%3A943b2e86-d448-4a36-a4e7-d5dd72c9407f) | Online study N=194 following a ten-person pretest. Justifications improved transparency/trust in the immediate-response condition, with no effect in the dynamic-delay condition. | Truthful progress can explain what is happening, but does not prove a long delay acceptable. This corrects an overly broad reading that an explanation always offsets waiting. Pre-generated recorded dialogues differ from this live system. |
| [Nielsen,Response Times:3Important Limits,1993](https://www.nngroup.com/articles/response-times-3-important-limits/) | Classical guidance distinguishes roughly0.1s instantaneous feedback,1s uninterrupted flow and10s focused attention. | Useful interface guidance, not an LLM/neuro-symbolic acceptance standard. It motivates immediate acknowledgment and progress during longer work; a status message is not an answered question. |

Some publisher endpoints rate-limited full HTML/PDF access. For the local RAG
paper, the publisher's indexed sections6.2/6.5 supplied the reported timing values;
hardware-normalized comparisons and a user acceptance conclusion remain unavailable.
The table marks abstract-only use explicitly. The primary sources do not supply a
validated common threshold that could simply be copied into this study.

## What Bintanong's measurements actually explain

Reuse [the selected runtime report](2026-10-20-fast-replies-results.md), rather than
starting another parameter sweep. Actual saved traces show:

| Existing warm observation | RAG | Symbolic | Hybrid |
| --- | ---: | ---: | ---: |
| Complete backend validated answer,s |35.662|35.058|52.967|
| LLM routing plus language selection,s |14.306|16.876|17.199|
| Retrieval including query encoding,s |0.330|not required|0.435|
| Structured/Prolog adapter,s |not required|0.422|0.850|
| Draft generation,s |14.714|12.647|28.688|
| Separate support check,s |6.267|5.065|6.144|

Hybrid retrieval and symbolic work overlap after their inputs are ready; do not
add those two durations as if both lay serially on the critical path. Release
checks/integration/transport account for the small remainder. All four LLM calls
together account for approximately98–99%of these observed request durations.
This is one observation/route, not a distribution or general bottleneck guarantee.

For this workload, describing the35–53second wait as the inherent cost of RAG plus
neuro-symbolic reasoning would be misleading. Warm retrieval and the Prolog adapter
are each below one second here; repeated LLM inference dominates. Symbolic alone
still takes35seconds because the surrounding neural calls remain. Prolog provides
reviewed deterministic decision logic; the LLM support checker is a different,
fallible component and cannot certify the entire answer.

For RAG/Symbolic, the relevant executor cost lies between interpretation and draft.
For Hybrid, a useful decomposition is:

`T = T_route + T_style + max(T_retrieval,T_symbolic) + T_draft + T_check + T_guards`.

Retries, queueing and startup add separately. The existing routing/style stage
alone already exceeds10seconds;shorter generation references cannot by themselves
establish a sub10second complete response. Startup has an additional measured
25.131s encoder cost/26.408s process cost in the old observation, not a per-query
cost once a resident application is ready. Server/model boot is another measure.

## Measurement and accuracy conditions before calling latency sufficient

Use submission-to-complete-validated-answer as the primary endpoint. Report backend
timing now; browser rendering/network/queue time will belong to later API/UI work.
Report acknowledgment/progress separately. No unvalidated answer tokens should be
exposed to obtain an attractive first-token number.

Keep route, language, source/curriculum scope, actual outcome, support correctness,
repairs/fallbacks and output length next to timing. A quick unsupported answer or
abstention must not count as a successfully answered fast query. Compare speed only
after the candidate preserves the necessary quality;inspect actual claims and
scope independently of schema success or a same-model positive checker verdict.

For the later performance study, predefine representative accepted cases by route
and English/Filipino/Taglish, repetition order, warmup and device/profile. Repeated
case runs estimate runtime variability, not independent language accuracy samples.
Use enough observations for meaningful route-specific p50/p95 and uncertainty;
50–100timings/route is a proposed starting budget, not a statistical guarantee.
Disclose sample counts and percentile method;do not infer p95 from these three
observations. Include failures/timeouts, cold startup and planned small-concurrency
queueing separately, keeping the student audience and privacy gates.

The owner has already accepted the75institutional language variants; no wording
review should be reopened. Execution still needs the applicable source/rule/release
conditions. The current fictional observations cannot establish performance on that
corpus. Add a brief waiting-satisfaction/abandonment measure and task success to the
planned student evaluation;SUS alone does not isolate acceptable waiting time.
Do not claim participant recruitment or an approved protocol from this suggestion.

Freeze latency work when the best **quality-preserving** candidate meets the agreed
study target and user evidence supports the wait, or at the standing improvement
cutoff. Otherwise disclose the unmet objective. The one-week accuracy-work cap is
not permission to waive validation or start an indefinite model/prompt sweep.

Suggested manuscript position,after actual results are finalized: this is a local
advisory RAG/neuro-symbolic research prototype whose route-specific validated-answer
latency is measured alongside factual support and decision correctness. State the
actual hardware and unresolved quality/waiting limits; do not claim that architecture,
undergraduate project status or a positive checker makes the response acceptable.
