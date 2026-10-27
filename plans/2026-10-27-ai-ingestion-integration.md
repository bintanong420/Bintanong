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
