# Selected checker completeness: diagnosis and bounded proposal

21 October 2026. **Read-only diagnosis complete; comparison proposed, not approved
or run.** Phase09 remains active. Product HEAD8060c7b; saved delivery8dbb15d.
[Actual results](2026-10-21-task-first-observation-results.md) and the failed
[original protocol](2026-10-21-task-first-quality-gate.md) remain unchanged.

## What the saved evidence establishes

The English question asks where to send slip S and its listed charge. The router
correctly declares both parts. The supplied source gives Office K and7tokens.
Generation emits only the office claim. The selected reviewer marks that claim
supported and maps BOTH parts to it. The host verifies identities, permitted IDs,
support verdicts and mapping structure, then releases the incomplete answer.

The support verdict is correct; the fee mapping is false. Nothing was lost in
retrieval, quote binding or Prolog in this case. The reviewer prompt ALREADY says
an omitted fee is not covered by an office claim. Repeating that instruction or
adding another mapping ledger does not supply a new mechanism. One claim may
legitimately answer several parts, so prohibiting repeated claim IDs is unsound.
`semantic_completeness=unverified` accurately describes the remaining limit; it
does not make the released answer complete. This is a current selected-path error.

The saved English review HTTP trace requests `reasoning_effort=none`; its rendered
template contains no `<|think|>` activation token. The transport hardcodes that
setting for template application and completion. The resident template supports
`enable_thinking`, default false. These facts establish disabled native thinking
for this invocation, not that disabling it caused the semantic error.

## Documentation and alternatives

[Google's thinking guide](https://ai.google.dev/gemma/docs/capabilities/thinking)
includes E4B and documents activating native thinking through its template.
It does not establish improvement on our completeness task. Context7 resolved
`/ggml-org/llama.cpp` and fetched the serving controls; the actual saved service
build is **b11723-31288c9c6**. Its
[matching server source](https://github.com/ggml-org/llama.cpp/blob/31288c9c6/tools/server/server-common.cpp#L1315)
accepts a Boolean `chat_template_kwargs.enable_thinking`; a later
`reasoning_effort=none` overrides it. A nonempty effort label is not a numerical
reasoning budget. The old Phase07 probe's unrecognized `reasoning_budget` field
cannot settle this comparison; see the
[prior research](2026-10-19-phase07-accuracy-research-recommendation.md).

Options considered: more prompt examples repeat an already explicit instruction;
a second judge adds another fallible call and latency; typed fee fields require a
larger reviewed source/answer design. Replacing or training the model needs a new
owner decision. **My recommendation is one checker-only native-thinking comparison
before choosing any of those interventions.** It retains the supplied model and
current prompt/schema, isolates one inference control and adds no product feature.
It may fail, truncate or take longer. It is a diagnostic, not an accuracy guarantee.

## Exact proposed comparison

Student capability: answer every requested documentary detail while refusing to
treat source-supported unrelated prose as a complete answer. Evidence path:
saved task-first requirements, cited passage and draft -> existing part reviewer
-> existing support/ledger assessment. Phase exit advanced: resolve the next
recovery choice for the outstanding completeness/relevance safeguards. Question:
does enabling native thinking correct the known omissions without rejecting the
two saved complete multilingual answers, within the unchanged resource limits?

Use these four existing synthetic developer fixtures without changing wording,
sources, parts, claims, schema, prompt or identity hashes. Raw root is workspace
`audit-evidence/p09-task-first-20261021/`; its57file seal is
`e10ca82c572f48557b04aa258b17cdb1bd11d5c0f5ec46369fc866ba36b0fd3d`.

| Fixed order | Saved review input | Required semantic result |
| --- | --- | --- |
| 1 | `d-en-call-4.json` | Office r1 mapped; omitted charge r2 unresolved/uncertain. |
| 2 | `b-relevance-prepared.json` | Filing r2 mapped; eligibility r1 unresolved with an existing accepted reason. |
| 3 | `d-fil-call-4.json` | Both parts mapped to claims that answer them; complete Filipino retained. |
| 4 | `d-tl-call-4.json` | Both parts mapped to claims that answer them; complete Taglish retained. |

All claims remain supported; requested language/scope true; no support/structural
errors. Case1's source contains the fee: source_gap/not_in_evidence is not a valid
omission reason. Case2 reuses the prior frozen labels: structured_check_not_run,
uncertain or not_in_evidence. Do not relabel its deliberately wrong document parts
to manufacture a canonical witness. Gold labels stay outside the model input.

For each case run **off then on, once each: at most8new completion calls**. Off
uses the current request unchanged. On removes `reasoning_effort=none` and sets
`chat_template_kwargs={"enable_thinking":true}` for BOTH template and completion.
Keep the same model/build/template,ctx8192,total output768,temp0,seed0,cachefalse,
constrained schema and120s whole-inference deadline. No extra numerical reasoning
budget, output enlargement, retries, repair, seed change or follow-up sweep.
Output768 covers thought and final response; truncation counts as failure.

Before any completion, verify old seals, freeze all four exact inputs/labels and
the audit runner, and check the existing18088 resident build/template. No startup
or substitution. Verify off/on rendered prompts differ only as expected for the
mode and contain the corresponding activation state; tokenize each actual rendered
prompt and enforce context headroom. A mismatch stops with zero completions.
Use bounded HTTP/response parsing, record truthful outgoing controls and reuse
existing public draft/support/identity/ledger validators. Reconstruct packs/drafts
from the sealed result/draft records and require byte-equivalent review messages
and schema before calls. No product transport/default/configuration edits.

Record every attempted pair, raw output, finish reason, thought-field presence,
tokens and outer checker duration. Parse only final content as the review; retain
thoughts in ignored researcher evidence, never student output. Template activation
is not proof of useful deliberation. If thought output is not observable, disclose
that limitation rather than claiming a verified reasoning mechanism. Stop the
batch on operational/schema/truncation failure; finish all fixed pairs after a
semantic error so adverse observations are retained. No rescue or rerun.

## Interpretation, stop and authorization boundary

On must satisfy4/4 exact semantic expectations, including both positive controls.
Report off results separately. If the off failure does not reproduce, the result
cannot establish a correction attributable to thinking. One observation per case
is not a calibrated rate, independent test set or causal/statistical proof.
Failure or inconclusive evidence ends this diagnostic without a replacement run.
Even4/4 is only a reason to consider a later implementation/full pipeline gate;
it does not promote this mode, repair generation or close Phase09 automatically.

This proposal explicitly seeks authorization for a NEW isolated diagnostic after
the old gate stopped; old B2 remains NOT RUN under that gate. No full pipeline,
retrieval/Supabase, Prolog execution or student-visible timing is measured here.
Report checker HTTP/readiness/tokenization/inference overhead separately; compare
paired checker times only. The [saved latency recommendation](../Context/response-time-recommendation.md)
and [measurement contract](2026-10-20-response-time-measurement-contract.md) apply;
accuracy takes priority and no15-20s end-to-end claim follows.

Undergraduate/advisory/privacy/source/institutional-release holds, accepted75
variants, separate routing/structured-Prolog/RAG architecture, held if/kung policy
and one-week improvement cutoff remain. No product/DB/dependency/model change,
training, restart, release, push or Phase10. Approval permits only this finite
diagnostic and its plan/evidence, not a replacement model or automatic rescue.

## Read-only verification

One fresh brainstorming builder check: nothing important left; no edits/calls.
Root independently reconstructed4/4 exact messages/schemas with the current
public scoped draft/prepare/review functions, revalidated57sealed files and
reproduced the saved false complete ledger. Zero new model/service calls.
Evidence: workspace/audit-evidence/p09-checker-completeness-diagnosis-20261021/
diagnosis-verification.json, SHA256
`134ed42fad1788627ad6bc5a4612159f9fa073374c32d79b561528942a6eff39`.
An initial local helper selected the short-draft class instead of the selected
scoped DocumentExplanation; corrected before any HTTP or evidence write. Product,
fixtures and original seals unchanged. This verifies feasibility, not improvement.
