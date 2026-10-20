# Response-time measurement contract

20 October 2026. Owner asks whether the quoted timings include startup,connection
and other costs,then asks to measure excluded factors too. This contract clarifies
the [research target](2026-10-20-response-time-research-assessment.md) and preserves
formal phase boundaries. It does not claim the API/UI or load study already exists.

The primary student-experience endpoint is submission to the complete validated
answer visible in the browser. Backend pipeline timing is a diagnostic component.
Immediate acknowledgment/progress is separate from answer availability. Do not
stream unchecked answer tokens or count an unsupported fast answer as success.

| Metric | Boundary and required breakdown | Current evidence / future gate |
| --- | --- | --- |
| Warm end-to-end latency | User submits a request to completed answer rendered;includes normal network,API/session work,admission/queueing,backend and final transfer/rendering | Not measured;Phase11 API/UI and Phase12 evaluation |
| Warm backend request | Before constructing per-request components to the returned validated backend answer | New outer timer in the scoped observation;excludes process/service startup and browser/API |
| Warm pipeline | Immediately before AnswerPipeline.run to its validated answer | Existing35–53s observations use this inner boundary;report alongside outer time |
| Service cold start | Launch event to readiness;break down backend imports/configuration,model/container boot,embedding verification/load and service readiness | Existing encoder/process observation and current startup receipt;model/Docker launch not newly measured |
| First request after cold start | Submission while the documented cold-start condition holds to complete answer;state exactly which services were cold | Not established by adding warm latency to an unrelated startup sample;future bounded controlled observation |
| Supabase connection/readiness | Client construction and initial verified reads;distinguish first/reused/reconnected HTTP requests and local/hosted endpoint | Current explicit initial readiness timer;it includes multiple release verification reads and is not an isolated TCP/TLS benchmark |
| Database/retrieval operations | Request embedding plus RPC/query time and result assembly;preserve aggregate vs separately instrumented timing labels | Existing aggregate retrieval and release events;separate SQL/encoding spans only when instrumented |
| LLM/tool execution | Per-call connection,preflight/template/tokenization,prompt processing,decoding and bounded repairs;Prolog subprocess startup/execution included | Existing physical-call and adapter timings;do not label these decode-only |
| Queue/admission wait | Submission/admission to actual work start at a stated concurrency;separate router/model/retrieval admission where relevant | Requires bounded load evaluation;not measured by serial three-route observations |
| API/network/browser overhead | Request preparation/upload,network transit,server parsing/auth/session work,response transfer and render | Phase11 instrumentation;no current estimate presented as a measurement |
| Optional private document path | Transfer,validation,OCR/parsing and private-context preparation for an authorized upload | Phase10/11/12 work;current text-only results do not cover it |

Keep overlapping/parallel spans separate;do not sum nested stages or add two
concurrent Hybrid branches as if serial. One ordinary warm request should not be
charged a resident model load each time. Conversely, do not hide a cold start
that the student actually experiences. Some reconnection/tool initialization is
inside a request and already counted;avoid double-counting it as an extra cost.

For browser end-to-end timing use a single client monotonic clock around submission
and completed rendering. Correlate with safe request IDs/server duration spans;
do not subtract absolute client/server clocks and assume they are synchronized.
Measurement instrumentation must not log raw questions,grades or private content.

Report sample counts,scenario/route/language,hardware/runtime/profile,source/release
scope,residency/warmup,output length,concurrency and success/failure semantics.
Summarize per-route p50/p95 with stated percentile method and adequate repeated
timings;with tiny samples report individual values/range and no stable-tail claim.
Repeated timings of one question are not independent semantic accuracy cases.
Include timeout/fallback/error/repair counts and durations;separate successful
supported-answer latency from all-attempt timing so failures are not hidden.

Track queueing,throughput and resource contention under a defined small load in
the later evaluation;student waiting satisfaction/task success remain separate
from mechanical schema/check success. No new benchmark wordings,participant study,
performance SLA,institutional approval or deployment is authorized by this record.
The owner's accuracy-first requirement and one-week improvement cap remain.
