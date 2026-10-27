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
