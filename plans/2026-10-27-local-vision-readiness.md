# Existing model vision check and remaining-work reasons

Owner asked to check the installed model and explain the unfinished checks.
No product code,dependencies,model weights,student runtime or hosted state changed.

## Correction to the earlier inventory

Earlier searches checked only the shared workspace MODELS directory. That was
insufficient to claim this machine had no projector. Fresh inspection also found
LM Studio's existing assets under
`C:/Users/Hawksprey/.lmstudio/models/lmstudio-community/gemma-4-E4B-it-GGUF/`:

- `gemma-4-E4B-it-Q4_K_M.gguf`,5,335,289,664bytes.
- `mmproj-gemma-4-E4B-it-BF16.gguf`,991,551,840bytes.

The shared production-selected `gemma-4-E4B-it-UD-Q4_K_XL.gguf` is5,126,306,944bytes.
Its GGUF metadata says architecture gemma4,name Gemma-4-E4B-It. Existing projector
metadata says type mmproj,vision encoder true,gemma4v,projection dimension2560;
it also includes the audio encoder. No weights were downloaded,copied or moved.
The existing LM Studio projector was read in place for this temporary probe.

[Google's model card](https://ai.google.dev/gemma/docs/core/model_card_4) confirms
image input. [llama.cpp documentation](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/docs/multimodal.md)
describes local model plus mmproj loading. Installed llama-server9264/ce02093fd
supports Vulkan;Vulkan1 is the RTX4060LaptopGPU. The repo Bintu compose commands
do not currently pass --mmproj. No image endpoint was listening on8080/8081/1234;
Ollama11434responded with an empty served-model list. These are local-only probes.

## Live image input succeeds; advisory task does not pass

Started an isolated offline server on127.0.0.1:8093 with the shared model and
existing LM Studio projector. Arguments:--device Vulkan1,--n-gpu-layers99,
--ctx-size4096,--parallel1,--offline,--no-ui,--reasoning-budget0 and
chat-template kwargs enable_thinking=false. Existing student/reviewer services
were not restarted. The probe sanitizes environment and makes no hosted request.

Server props reported vision=true,audio=true. It processed an original Handbook
physical46PNG through the existing ingestion VisionProvider/advisory path.
Source SHA4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8.
The deliberate synthetic mistranscription was
`Grade 1.0: percentage equivalent 95-97`;the visible original has98-100.
This test input was never saved into an institutional review packet.

First startup31.22s/request62.26s;adapter outcome failed. A second bounded run
captured the raw response to diagnose that failure:startup14.84s/request2.42s;
server image encoding0.878s. Separate server starts/cache states,not a standardized
warm latency benchmark or student-visible SLA. Captured model response:

```json
{"outcome":"no_change","rationale":"The candidate text matches the original text on page 46.","proposed_value":null}
```

Two distinct problems:the no_change claim is wrong for this intentionally corrupted
row;proposed_value is forbidden for nonproposal outcomes by the existing strict
advisory contract,even when null. The pipeline rejected it and retained pending
manual review. No schema loosening,prompt sweep or artificial approval was used
to manufacture success. This is a failed single-case quality/contract check,not
proof of general model accuracy or incapability. Image I/O is now demonstrated.

Both temporary servers were terminated after their probes. No source,review
journal,active pin or model configuration was changed. Raw commands,server logs,
PNG,result and captured response are ignored under workspace
`audit-evidence/p11-live-vision-20261027/` and `attempt2/`.

## Disposable database and original T4/T5

Fresh docker version reports installed client29.8.2,context desktop-linux,but no
server. Docker ps fails because dockerDesktopLinuxEngine named pipe is absent.
The existing tests/storage_database.py helper uses docker exec/psql to create a
uniquely named throwaway local Postgres database and exercise real roles/migrations.
No database command or hosted fallback was attempted during this inspection.

This infrastructure issue explains unavailable DB verification,not all missing
implementation. knowledge_update/local_release.py is absent,and the ingestion CLI
has no stage/publish/rollback commands. Original T4's bounded wrappers/recovery
tooling are unfinished. Existing shared storage primitives are not equivalent to
that delivered operator workflow. Original T5 depends on T4 and requires two-edition
and sealed-package end-to-end rehearsal;the AI extension guide does not complete it.

## Human accuracy and A/B

The28-page/84-row sample and measurement harness exist. Completed human decisions,
accepted accuracy reference and recorded cleanup times for the matched strategies
have not been collected. Human correctness decisions and minutes cannot be inferred
from unit tests,model confidence or model-generated self-review. Existing verified
source evidence should be reused where applicable,without reopening settled decisions.

The unfinished work is to produce the matched candidate sets,prepare short source-
comparison batches,conduct the review and record actual corrections/time/unresolved
counts. Automated comparisons can assist this;they are not a substitute for measured
human effort. This is work not yet executed,not a failure by the owner to provide it.
The captured row-association miss above is concrete evidence why these gates matter.
