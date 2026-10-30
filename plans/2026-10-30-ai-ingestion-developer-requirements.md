# AI-assisted ingestion: developer request and repository requirements

30 October 2026. Owner supplied the developer's original request again and named
E:/Hawksprey/Downloads/message (1).txt and message (2).txt. This reconciles the
existing plan;it does not introduce new source approval,scope or model training.

## Developer request

> since ai-assisted ung ingestion pipeline natin
> try mo 2 ways, ung isa ung sa workflow ko na any custom  llm. gagamitin nya ung scripts tas titignan ung image for further verification tas human verification
> tas ung isa via llamaparse kasi ai din ung pag parse nila duon, check mo nalang kung may api key kahit free tier lang, baka pwede mangyari dun is hiwain ung pages ng handbook at cz kasi masyado marami baka di kaya ng isang free tier acc
>
> kasi through scripts alone di talaga kaya tas if may human verification pa after, possible ung human ung magpalit personally nung data sa chunk

## Verified source notes

Both supplied text files match the preserved repository text after BOM/line-ending/
trailing-whitespace normalization. Original byte SHA256:
- message (1).txt:4dd54518f743e09c3d8ba0bd0c1a76fe6640c058c4f1e8671ba3963e67ec2473;
  preserved [two-developer workflow](2026-10-26-policy-ingestion-developer-workflow.md).
- message (2).txt:444f037dc5cfb8243f4a7e0b32940d07e260d59faa1a9308bbbb7d3197c371f6;
  preserved [feature plan](2026-10-26-policy-ingestion-developer-plan.md).
- Apply the [workstream plan](2026-10-26-policy-ingestion-workstream.md) amendments:
  researcher Next/React/TypeScript with FastAPI;local-only verification,no hosted access.
- The [AI extension plan](2026-10-27-ai-assisted-ingestion-codex-plan.md),sections5,
  9–12,15–20,and its [launch prompt](2026-10-27-ai-assisted-ingestion-launch-prompt.md)
  define the two assistance paths and human authority. AGENTS.md overrides the
  supplied plan's discretionary dependency language:install/download changes need
  an applicable owner instruction. No fine-tuning or new weights are authorized.

## Required behavior and current implementation

| Developer intent | Required integration | Current evidence and remaining work |
| --- | --- | --- |
| Scripts plus any suitable custom LLM | Native extraction → original page images → configurable advisory provider → existing human review | Existing VisionProvider serves this boundary. Owner's Gemma GGUF plus existing projector processed a page on27Oct;the captured suggestion/format failed. A real assisted packet through human save/build still needs demonstration. |
| AI parsing through LlamaParse | Selected-page parsing/batches → existing candidate representation → same human reviewer/build | Adapter,resume,partial recovery and synthetic checks exist;real provider comparison remains unrun. |
| Human can personally correct chunk data | Editable reviewed value,explicit save with history,then build corrected chunks | ReviewSession.export carries corrected values and source-bound review events;build consumes the export. Preserve originals and derive chunks/identities/vectors through the existing builder;do not hand-edit finalized packages. |

HITL is the planned handling for incorrect AI suggestions. Section16 explicitly
expects a hallucinated suggestion to require human review. A missed grade reading
is recorded quality evidence,not an independent requirement for flawless AI or a
reason to prohibit a supervised trial. Preserve the failed test;do not relabel it
as correct. A/B measurements remain needed before claiming improved correctness
or less reviewer effort.

The model's response must still be usable within the advisory boundary. Malformed
responses retain manual review;privileged metadata and stale/wrong-source bindings
reject. The local validator currently rejects proposed_value:null on no_change.
Specific prompt/schema or narrowly defined provider normalization is an engineering
option to test,not an existing allowance to accept arbitrary malformed output.
No AI result,including no_change,can approve content or remove the human save.

## Fresh LlamaParse availability and official-source check

No LLAMA_CLOUD_API_KEY or LLAMAPARSE_API_KEY configured in current process,Windows
User/Machine environment or .env declarations in repository root/backend/researcher.
Only key presence was checked;no secret values logged. Other credential stores and
account dashboards were not inspected;no provider request or upload performed.

Official sources checked30Oct:
- [API](https://developers.llamaindex.ai/llamaparse/parse/guides/api-reference/):
  authenticated v2 upload/poll and file-id parsing endpoints exist.
- [Page selection](https://developers.llamaindex.ai/llamaparse/parse/guides/configuring-parse/):
  page_ranges.target_pages selects1-based physical pages;unselected pages are not
  processed/billed according to the provider. Existing adapter uses that option,
  but uploads the complete original PDF for each new batch. It does not physically
  split the PDF. Physical derivative splitting would need original-page/hash mapping.
- [Plan pricing](https://www.llamaindex.ai/pricing) lists Free10Kcredits/month;
  [parse pricing](https://developers.llamaindex.ai/llamaparse/general/pricing/)
  lists Agentic10credits/page and additional layout costs. Actual account balance,
  entitlements and remaining quota are unknown. Batching does not increase quota
  or inherently reduce total cost for the same pages/options. Select a bounded
  in-scope sample and retain cross-page service context;no paid run inferred.

## Next action and limits

Fit the existing local Gemma provider output to the advisory contract with focused
RED/GREEN tests,then demonstrate a fresh assisted packet through original-page
comparison,human correction/save and build/verify. Record bad suggestions rather
than demanding perfect output before HITL. Native conversion still has its recorded
dependency conflict;no installation authorized by this requirements reconciliation.
Real LlamaParse comparison waits for a configured authorized key and known quota.

This turn changes documentation only. No model/native-parser run,source review,
packet/journal mutation,cloud upload,dependency install,hosted access or push.
No new corpus-wide quality claim,phase closure or T4/T5completion.

Verification:documentation hygiene/contracts22passed in1.70s;phase statevalid.
No application test or live inference was needed for this documentation-only update.
