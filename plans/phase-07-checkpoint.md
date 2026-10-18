---
artifact: phase-checkpoint
phase: 7
status: in_progress
sequence: 13
plan: plans/phase-07-multilingual-routing-plan.md
head_commit: 79d56f1
working_tree: promptv4 explicit graduate scope and host-only ownership IDs verified
updated_at: 2026-10-19T01:04:01+08:00
---

# Phase07 checkpoint

## Completed Tasks

Owner accepts design and explicitly directs implementation. Task1 strict immutable
request/proposal/catalog contracts, original quote indices, ownership and minimal
NFC/whitespace normalization delivered. [Implementation ledger](2026-10-19-phase07-implementation-plan.md).

## Current Task

Promptv3 repeat complete:13/15proposals,14/15effective,4/5family consistency.
Explicit Filipino graduate scope still failed; model-visible scenario request IDs
also made both earlier runs hinted debug evidence. Promptv4 clarifies excluded
audience and removes session/request/fact IDs from model input; regression RED1
->79routing tests,0.90s,exit0. Final clean same-wording run next.

Task1 committed7ed9abe; Task2 committed2de4f76. Task3 transport/prompt/router verified.
Task3 committed8fb40c3; Task4 evaluator9286c76. Independent review complete;
threeP2 findings reproduced/corrected. Actual15-case model batch is running against
9286c76; preserve its initial contract. [Review/corrections](2026-10-19-phase07-code-review.md).
Review fixes committed4fa64e4. Captured model output proves wrong offset counting;
deterministic unique literal-quote anchoring now verified, without changing meaning.

## Repository State

p07/feat/p07-router-taglish-nlp; base87ece27, inherited product c5f110b.
Only this worktree changed; stale p06 and other developer worktrees preserved.
Pre-condensation checkpoint snapshot:87ece27:plans/phase-07-checkpoint.md.
Current progress holds latest change; dated implementation plan holds task contract.

## Verification Evidence

Current-code v3 full gate:1504passed/11subtests,165.38s,exit0 (final-regressions.log).
That gate precedes v4 ownership-ID correction; final v4 gate still required.

Task1 RED22failed (package absent); initial console-encoding/long-ID problem
corrected in test reporting, then expected RED observed. Task1 GREEN238passed,
1.77s,exit0: tests/test_routing_contracts.py tests/test_bintu_inference.py
tests/test_contracts_runtime.py tests/test_contracts_runtime_fix2.py.
Command:readiness-venv python -B -m pytest -q -p no:cacheprovider with TEMP/TMP
and --basetemp under workspace/audit-evidence/p07-implementation-20261019.
Raw task1-red-fixed.log/task1-green.log. Task2 RED20failed -> GREEN207passed,0.97s,
exit0 (routing contracts/validation plus symbolic/runtime contracts); task2-*.log.
Task3 RED15 -> GREEN227passed. Actual probe exposed format-repair meta-question
and route/control schema mismatch; focused repair/schema regressions each RED1.
Original probe output saved; promptv2/decoder oneOf and repair reanchoring corrected.
Final Task3 gate229passed,2.51s,exit0; task3-final-green.log.
Task4 RED8 -> GREEN65; effective-label RED1 ->68passed. Review RED4failed/3passed
->75passed,2.43s. Full23-file gate1499passed/11subtests,266.57s,exit0, regressions.log.
Material-fact RAG regression RED1 -> final focused76passed,2.31s. Full collection
predates that last delta; final focused suite covers it. No model-score claim yet.
Quote anchoring RED1/1passed ->248passed,5.02s,exit0; anchor-*.log. Captured actual
English output replay yields correct operation/course/failed claim with3offset
corrections and no new model call; structured-quote-replay.json. Not a15-case rerun.
Prior kickoff309/phase19 remain history,
not current reruns. Phase06 accepted1415 is predecessor evidence.

## Versions and Digests

Existing Python3.13.7 readiness venv; no package/pin/lock changes.
Owner-corrected MODELS_DIR=C:/Coding-projects/bintanong_workspace/MODELS.
Gemma GGUF5,126,306,944bytes; freshly verified SHA256
3cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80.
Official runtime download authorized; image digest:
sha256:4b7be0376002b4450a357a109bab804093ff9251193cc75ed4ce0cb39953ff5c.
Task-owned bintanong-p07-router-offline loaded Gemma on127.0.0.1:18087,
CPU8threads/context8192/one slot/output768. No other containers altered.
Original model bytes stay in place; previous C:/Coding-projects/MODELS is historical.
Thesis SHA256729653540c7991496aceea1f728382d2e2262ca096e4342ce956d072e603c81c.

## Decisions

Context already consulted:actual thesis17-18/39-44/58-59, cached scope renders,
routing PNG, master3/11/12/13 and scope/gap/architecture policies. Master11.4
unknown semantics and diagram routing order govern over illustrative older prose.
Owner confirms LLM routing; curriculum primarily structured/Prolog, documents RAG,
Hybrid when both required. English/Taglish/Filipino response preference preserved;
image/private inputs later. Current Context evidence remains applicable.
Ruling:owner's explicit proceed authorizes design execution without another approval
round; exact plan supplies internal interfaces, not a new user-facing scope.
Ruling:owner model-root correction supersedes old path for this phase; no model move.
Ruling:ownership/scenario IDs are unnecessary model input; keep them host-side.
Earlier hinted runs remain debug evidence, not clean language-accuracy proof.
Ruling:unique literal quotes can anchor wrong model offsets deterministically;
count corrections and reject ambiguous/missing quotes. No semantic/fact inference.
Docker Desktop started; unrelated existing containers preserved.
Context7 Pydantic/HTTPX/llama.cpp docs fetched; deployed runtime still must be probed.

## Known Failures or Blockers

Baseline15-case complete:8/15proposed,3/15effective,2/5family consistency;
seven schema failures and two grounding failures. RAG explanations were placed in
ambiguities. Promptv3 clarifies field purpose and pre-retrieval routing; current
15-wording repeat with operation labels/raw capture next. Initial probe misread the formatting
instruction; not a passing language result. Keep original raw output and corrections.
Synthetic contract tests prove boundaries, not language accuracy. Institutional
registry/source authority/currentness/activation remain closed; four blank own-rules
unknown. Two inherited Docling failures/full-prospectus defects remain disclosed.

## Next Action

Finish bounded actual-model batch, inspect exact failed outputs and report route/
meaning results separately from guard/test success. Do not activate or advance.

## Do Not Repeat

No Phase06 review reopening/receipt recovery, model copying, institutional registry
activation, arbitrary Prolog, unapproved institutional questions, external merges
or modification of other developer worktrees. Preserve ignored evidence.
