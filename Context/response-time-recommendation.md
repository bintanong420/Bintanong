# Response-time recommendation to preserve

Recorded20October2026 at the owner's request. This is the researched engineering
recommendation for Bintanong's undergraduate RAG and neuro-symbolic study.
It is a proposed target,not an approved SLA,a measured achievement or a universal
threshold established by the cited research. The owner requires **accuracy first**.

## Recommended target

- Aim for a typical warm,complete,validated answer in **15-20seconds**.
- Prefer **under10seconds** for short questions when all necessary checks remain.
- **20-30seconds for a complex Hybrid answer** can be disclosed as a research
  prototype limitation if needed checks remain and actual student evaluation finds
  the wait acceptable. Undergraduate-project status does not establish acceptance.
- These ranges refer to **submission until the complete validated answer is
  visible in the student's browser**,including normal API/network/rendering and
  queueing. A backend-only duration or first progress message does not meet this
  definition. These targets remain unproven by the existing observations.

The recommendation synthesizes local educational RAG measurements,neuro-symbolic
architecture research and human-computer interaction evidence. It is not a cutoff
copied from one paper. Hardware,models,questions,output lengths and timing boundaries
differ. Slower answers do not prove better accuracy;published slow prototypes do
not establish that students find the wait acceptable.

## Accuracy and stopping rule

Never drop required RAG/Prolog reasoning,consequential source content,source/version
checks,privacy controls or answer validation to meet the time target. Reject quality
regressions. Keep LLM semantic routing and deterministic reviewed curriculum checks;
do not substitute keyword routing or unsupported model judgments. No unchecked answer
streaming. A faster incorrect or unrelated answer is a failed result.

Freeze the best quality-preserving candidate when measured performance and student
evidence support the target,or at the existing improvement cutoff. Otherwise report
the unmet objective honestly. The one-week accuracy-work extension does not waive
source/release/phase gates or authorize indefinite prompt/model sweeps or training.

## Metrics that must accompany the recommendation

| Metric | What to include or distinguish |
| --- | --- |
| Student-visible end-to-end | Submission,API/auth/session work,queueing,network,backend,transfer and rendering |
| Warm backend and inner pipeline | Separate outer request construction from the timed pipeline;record route/language and validated outcome |
| Cold start and first request | Imports/config,model/container startup,embedding load/readiness;state which services were cold |
| Supabase connection/readiness | Initial verified reads versus reused/reconnected requests;local versus hosted;readiness is not an isolated TCP/TLS handshake |
| Tools and processing | LLM connections/preflight/template/tokenization/inference/checks/repairs,retrieval/embedding,Prolog startup/execution |
| Load and optional uploads | Queue/admission/concurrency,throughput,upload/validation/OCR/private-context preparation when applicable |

Report failures/timeouts/abstentions and success latency separately. Use per-route
p50/p95 only with adequate repeated samples and a stated method;current isolated
samples do not establish tail latency. Measure student waiting satisfaction and task
success separately. Mark unavailable metrics explicitly. Do not double-count nested
spans,parallel Hybrid work or resident startup as a cost on every warm request.

## Detailed evidence and measurement definitions

- [Research assessment and seven primary sources](../plans/2026-10-20-response-time-research-assessment.md).
- [Measurement contract and excluded factors](../plans/2026-10-20-response-time-measurement-contract.md).
- [Current progress](../plans/plan_current_progress/current_progress.md) points to the latest verified candidate/results;historical timing samples are not live metrics.
