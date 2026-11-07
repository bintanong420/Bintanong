# AI-assisted ingestion integration and skill research

27October2026. Owner authorizes sequential local implementation of the supplied
[execution plan](2026-10-27-ai-assisted-ingestion-codex-plan.md) and
[launch prompt](2026-10-27-ai-assisted-ingestion-launch-prompt.md).
Baseline3c1d76c,clean feat/p11-policy-ingestion-review. New launch requests local
commits only;no publication is part of this extension. T4/T5 remain separate.
Supplied message(1)/(2) exactly match the preserved26Oct workflow/feature plans.
Copied new source-plan hashes:4c4347efd174b245698ea85e3a573cec5f7e7aa2950bcf023baff0233ab57d5b;
launch bb5aa7f01a93cf0ea1337da335b83cf8f9e116ad253ed1c51259876c41d7be2e.

## Task0 integration decision

Reuse knowledge_update.prepare/template_items,ReviewSession,renderer,review UI,
export/build/verify. Existing template proposed_value is already pending and can
carry an advisory value. It lacks assistance provenance and UI controls;add only
local review-wrapper metadata,not shared SourceSpan/Chunk contracts. Generate
assistance before packet hashing. New output required when assistance changes;
never rewrite an existing finalized packet. Shared contracts remain unchanged. Verify proposal bindings against the
original source SHA,physical pages,item/field and original candidate digest.
No AI provider gets a ReviewSession or can emit approval metadata.

Use existing httpx;BintuClient and generation providers target text student
inference and do not carry multimodal evidence. A small ingestion-only inspect
boundary with a deterministic fake and an HTTP vision adapter fits better than
changing the student runtime. Credentials remain environment-only and errors are
sanitized. Existing PageRenderer sends real original page images;no invented crop.

LlamaParse is an explicit alternate input to prepare,not a second build/reviewer:
selected original pages -> persisted source-bound provider batches -> local
review-template projection -> same pending items/journal/export/build. Preserve
whole table rows/merged HTML/continuation metadata together;do not infer fee/time
or office associations. Missing/ambiguous layout stays manual. No shared schema
change is planned. Prove build/verify after explicit human fixture decisions.

Task order:authority regression/provider+native assistance;UI;LlamaParse adapter;
document hardening/evaluation;regressions and operator handoff. Each uses RED/GREEN
and focused local commits. No AI-dependent default/network tests,hosted access,
autonomous approval,model training or dependency/lock changes.

## Installed and online skills

Applied repo handoff/phase-handoff/conventional-commits,installed find-skills,TDD,
lean-build,PDF evidence guidance,and existing antislop human/UI/code where UI is
touched. Relevant installed toolchain already includes httpx/PDF renderer;no new
SDK is needed. Save user-requested memory only as one extensions/ad_hoc note.

Discovered official [LlamaParse skill](https://github.com/run-llama/llamaparse-agent-skills),
not installed here. Its instructions require the Node LlamaCloud SDK and add a
confirmation flow;that workflow is unnecessary for this authorized Python adapter.
Treat it as researched guidance,not an installed runtime dependency. Official
[first-party PDF skill](https://github.com/anthropics/skills/tree/main/skills/pdf)
is another online alternative;installed PDF guidance already covers visual checks.
Do not install overlapping skills or packages merely for catalogue completeness.

## Current official API research

Consulted27Oct2026: [REST v2](https://developers.llamaindex.ai/llamaparse/parse/guides/api-reference/),
[configuration](https://developers.llamaindex.ai/llamaparse/parse/guides/configuring-parse/),
[response format](https://developers.llamaindex.ai/llamaparse/parse/guides/response-format/).
REST multipart POST /api/v2/parse/upload accepts file+JSON configuration and returns
top-level id/status. GET /api/v2/parse/{id}?expand=items,usage has job.status and
items.pages;1-based target_pages. Completed page items include typed rows/HTML,
merged_from_pages/merged_into_page/parse_concerns. Markdown alone loses merged
cells. Use raw typed table payloads and original page association,not flattened
word recall. Cache successful batches,save job ID before polling,fail closed for
missing/partial/failed pages;explicit rerun resumes. Timeout/auth/quota failures
stay unavailable/manual. No pricing/free-tier/credit savings assumptions.
Live provider tests optional when credentials unavailable;report NOT RUN explicitly.

## Verification status

Initial baseline attempt produced50setup errors because external basetemp parent
was absent;created parent and reran. No product defect inferred. Baseline50tests pass38.01s after that setup fix.
Full corpus evaluation needs human timing and decisions;prepare a20–40page matched
sample,harness and editable measurement sheet without inventing accuracy/effort.

Geometry gate:reviewed-policy chunk builder already requires complete original
geometry. LlamaParse items without trustworthy boxes stay manual/withheld at build;
only supplied boxes checked against original rendered page sizes may be used.
This is an existing safeguard,not a reason to invent whole-page coordinates.

## Tasks1–3 — native assistance

Authority tests RED:missing advisory module;15GREEN0.22s. Native end-to-end RED:
prepare rejects assist_provider;GREEN44tests21.49s. Final60tests31.67s cover existing
prepare/review/CLI/build/verify plus advisory/vision transport and human-corrected
build. Fake provider sees original page PNG;network/render/privilege/type failures
stay pending/manual. Resume compares assistance recipe,never reruns finalized AI.
AI suggestions live in existing proposed_value;local assistance binding contains
source SHA,candidate digest,item/field/pages,provider/model/time. No second journal.
CLI opt-in assist-mode/pages/items;vision endpoint via explicit environment only.

Owner asks whether current Gemma4E4B can supply vision. Official
[model card](https://ai.google.dev/gemma/docs/core/model_card_4) confirms image input;
[llama.cpp multimodal guide](https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md)
uses a matching projector. Local shared MODELS contains the5.13GB text GGUF but no
mmproj file. Loopback8080/8081metadata probes time out;no vision-enabled local server
or live inference verified. Reuse Gemma through the new OpenAI-compatible image
adapter once explicitly configured. No weights downloaded or runtime changed.

## Task4 — proposal UI

Stale-proposal helper RED missing export ->7Node tests/TypeScript GREEN. Real
isolated production browser1.87s verifies original/suggestion distinction,Ignore,
Use prefilling without persisted decision,manual edit,explicit audience/reason/save
and corrected journal state. Only synthetic packet/profile on3003/API8767;no owner
reviews modified. Existing3002was occupied;first launcher stopped cleanly on bind
failure,then isolated check moved to3003. Screenshot in ignored browser evidence.
Provider/no-change/uncertain/failure notices retain normal manual controls. No bulk
approval. Source/value/page/item checks disable stale application;server additionally
validates complete candidate digest. No confidence-based approval or new styles.

## Tasks5–7 — LlamaParse, hardening and evaluation

Llama adapter RED missing module;fixture initially violated original/output
separation,then real checks exposed missing renderer method/resume handling.
Reused existing renderer size/rotation methods and bounded resume validation.
Partial-batch RED re-requested nothing;GREEN retries only missing pages while
retaining successful results. Explicit failed-page RED discarded good sibling
pages;GREEN39tests20.95s preserves them. Focused pipeline71tests36.57s passes.

Native and Llama proposals both prove pending→explicit human review→same build/
verify. Raw typed tables,merged HTML,headers/footers,headings and continuation
metadata remain escaped candidate values;no fee/time/office zip is inferred.
Missing or invalid supplied geometry keeps the item manual/build-withheld.
The16Llama tests cover source/page/privilege mismatch,authentication/quota/500,
mock RESTv2,partial batches,real synthetic PDF dimensions and pending build gate.

Evaluation RED missing module;blank-vs-missing field RED caught a comparison gap.
GREEN6tests0.26s:swapped row fee/time with100%word recall reports four relation
paths;missing literal-blank cells differ;missing measurements stay null,matched
cohorts required and invalid/negative/nonfinite numbers reject. JSON/CSV/Markdown
reports keep observed/estimated cost separate;no model confidence accuracy claim.
Docker desktop engine is unavailable;actual-role DB/full DB-inclusive suite cannot
run safely here. No hosted fallback. Existing APIs/student runtime remain untouched.

Incomplete parse CLI regression RED returned success despite failed_pages;GREEN
19tests15.55s returns exit2 while keeping the result/receipt for recovery. Successful
parse remains exit0;configuration/transport exceptions remain sanitized failures.

Final envelope adversary RED3fail/1pass exposed unhandled non-object JSON/job
responses. Validate transport/job/items objects before use;GREEN48tests13.77s
includes five malformed envelopes,explicit Llama human correction→build→verify,
and Handbook TOC/body disagreement,book/section/subsection hierarchy,repeated
header/footer and physical-page continuation retained pending/manual. A fixture
initially confused the existing audience label with authoring metadata;corrected
the fixture to the real unresolved review-item contract,without changing it.
Browser save requires explicit synthetic write mode;fresh isolated replay passes
1.90s. Node7pass/1browser-skip and TypeScript pass. Owned3003/8767server stopped;
owner3001/3002reviewers not restarted.

Repository-wide available run:6949pass/745subtests,2fail,1skip,2xfail,9warnings,
401.05s,exit1. Seventeen Docker database files excluded;exact argv/exclusions in
ignored repository-command.json. Both failures are unchanged native Docling
conversion paths:installed Transformers5.10.2 requires huggingface-hub>=1.5,<2;
installed hub2.2.0 is incompatible. Installed Docling2.129.0/PyTorchCPU noted.
No dependencies,locks,models or existing converters changed to mask this failure.
Fresh native conversion is blocked in this environment;mocked preparation does
not establish its live health. Full suite is NOT green. Record repair as a
separate approved environment task;no broad refactor or hosted fallback.

Matched original-source sample created:28pages(16Handbook/12Charter),84rows for
native/native_vision/llamaparse. Originals rehashed/page counts checked;specific
sampling rationales retained in ignored sample.json. Generated summary keeps all
unmeasured metrics null. No live provider call,human timing or A/B winner claim.
Context refreshed after rollover:thesis physical17–18,runtime routing PNG,master
3.1/16:institutional preparation stays outside student requests;undergraduate
scope,private-file separation and no autonomous acquisition remain unchanged.

Final relevant regression selection after all code changes:1821passed/13subtests,
2deprecation warnings,189.53s,exit0;includes every knowledge_update,prospectus and
original review_gui test file. Exact argv/log/exit saved with final-focused prefix.
Operator guide and full results enumerate data transfer,recovery,manual table/
geometry boundaries and separate T4/T5.

Final plan checklist found the requested extraction-mismatch total was not a
measurement column:RED recorded totals disappeared from summary. Added only that
metric;GREEN7evaluation tests0.34s. Existing84blank rows remain unmeasured and final
summary in matched-summary-final includes the null total. This metric-only change
follows the1821run;provider/review/prospectus code is unchanged. No suite-wide repeat
needed for a tuple entry;the seven evaluator checks cover its affected behavior.
