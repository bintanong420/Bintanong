# Phase07 proceeding-operation decoder correction

Resume e576266 from the verified checkpoint. Student capability:an affected-course
question plus a document procedure should request one dependency operation and
RAG evidence, without an unrequested eligibility check. Evidence path:LLM proposal
-> scoped resolution/capability guards. Phase exit:observable route/meaning results
and no unchecked invalid symbolic dispatch. Unresolved question:does enforcing the
existing proceeding-operation invariant during generation prevent the recorded
Hybrid extra-operation error without changing the selected operation or losing
compound clarification? Language-style errors remain a separate open requirement.

## Evidence and minimal correction

The earlier fresh Hybrid output contains list_affected_courses plus an unrequested
check_prerequisite_eligibility. The validator correctly returned compound_request.
Current prompt already says only one operation/target can proceed, but decoder
schema allows zero to four for every evidence route. This is a concrete schema/
validation mismatch, not a language-prompt hypothesis or permission to drop fields.

Split existing decoder evidence branches:RAG requires zero operations;
Symbolic/Hybrid require exactly one. Clarification retains the existing bounded
operation list; terminal controls remain action-free. Preserve strict interpretation
parsing and the downstream compound guard, including for a transport that ignores
constraints. No host selection/removal of model operations, semantic retry, new
classifier, executor, institutional data change or activation. Prompt text and
style-v1 remain unchanged; routing version becomes bintanong-router-p07-v7 because
its embedded schema/input changes. Canonical interpretation-v1 is unchanged.

Context7 official [llama.cpp server docs](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
document array minItems/maxItems constraints. The official
[grammar limitations](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md)
warn that some unsupported features are silently skipped. Therefore retain host
guards and verify the actual pinned build's outputs, not only schema-library tests.
No runtime/image/dependency upgrade follows from this documentation lookup.

## TDD and bounded verification

Synthetic decoder matrix covers three routes with zero/one/two operations.
RED6failed/4passed,0.80s:the six unsupported count combinations are accepted by the
old decoder; bypass guard already works. GREEN137routing tests,1.33s,exit0 after
the minimal schema change. Compound clarification retains both operations.
Raw:workspace/audit-evidence/p07-operation-constraints-20261019/red.log,green.log.

Next actual check:use the six EXISTING prerequisite/Hybrid English/Filipino/Taglish
cases, all fresh routing calls under the new schema. Reuse exact-compatible style-v1
captures with source byte hashes; no style or wording experiment. Score proposed/
effective route, exact operation name/target, entity/claim meaning and style. A
wrong operation cannot be called correct merely because only one is generated.
Record actual runtime/template/prompt/schema/code identities and capture provenance.
Do not rerun unchanged RAG/control inference merely to expand this bounded check.
Keep prior15-case/fresh2-case observations intact, including the guarded failure.
Stop this diagnostic once the operation-count question is resolved; no equivalent
prompt/field-order sweep or language-label workaround follows.

Relevant full contract/symbolic/legacy/routing regressions and review follow before
commit/closure. Independent review against e576266:no P1/P2,137passed1.42s;
SYSTEM_PROMPT/domain/router/validation/style bytes unchanged. Broad24-file gate:
1567passed/11subtests76.68s,exit0; exact command in ignored verify-regressions.ps1,
regressions.log. git diff --check passes. Existing Python3.13 venv;
no installs/locks/weight downloads/copies.
Only restart/stop task-owned bintanong-p07-router-offline with the retained image.
Runtime restarted after image digest/read-only model mount inspection; health=ok.
Phase07 remains open and no Phase08 handoff is authorized by a candidate change.

## Context and boundaries

Refreshed saved thesis scope physical17-18 and actual runtime routing PNG, plus
master12/13 and existing3/11 architecture direction. No discrepancy:new schema
constrains proposal structure before dispatch; it does not execute policy or change
the undergraduate/read-only/private-context boundaries. Prior39-44/58-59 evidence
and source/Phase06 decisions remain settled. No original sources or75accepted
institutional wordings need review for these existing generic synthetic cases.

Master2.2 explicitly defines Bintu-1 as quantized Google Gemma4E4B and names the
instruction-tuned checkpoint candidate. The supplied Gemma therefore fills the
intended model role; a separately fine-tuned checkpoint is not a prerequisite.
Earlier absence-of-checkpoint observations are identity qualifications, not an
environment blocker. Master20 disallows adding fine-tuning to the initial build
without demonstrated need and an explicit project decision; same-artifact study
comparability remains required. No model change/training/download is proposed here.

## Actual six-case result

Product bec3d8e, routing-v7. Six fresh routing calls; six style-v1 captures reused
only after exact messages/schema/settings/runtime checks. Twelve logical calls,
zero repairs. All six raw model outputs satisfy the new decoder schema and contain
the correct single operation/name/target. Canonical entities and claim meaning6/6.
Style6/6 is REUSED evidence for these previously correct cases, not an improvement
to the two known Taglish failures or a new language-accuracy study.

Proposed/effective routes5/6; only one of two equivalent families is fully consistent.
The Filipino prerequisite query selects Hybrid although its intent/reason describes
only a curriculum prerequisite check. This remains a semantic route error. No host
rerouting, extra-operation truncation or semantic retry conceals it. All three
affected-course-plus-procedure cases select Hybrid/list_affected_courses correctly,
including the previously failed Taglish case. Count correctness does not prove
route correctness or general model reliability; do not combine these six with old
RAG/control outputs to invent a current15-case accuracy result.

| Language | Proposed/effective routes | Entities/claims/operations | Style (reused) |
| --- | --- | --- | --- |
| English | 2/2 | 2/2 each | 2/2 |
| Filipino | 1/2 | 2/2 each | 2/2 |
| Taglish | 2/2 | 2/2 each | 2/2 |

Route confusion matrices, both proposed/effective:expected Symbolic ->Symbolic2,
Hybrid1; expected Hybrid ->Hybrid3.15literal offset corrections across six cases.
The count/operation question is resolved for this bounded check; stop its diagnostic.
The new semantic mismatch and unchanged style failures remain explicit phase exits.

Raw:structured-six/input.json,report.json,12stage captures; evaluation.log.
Command:existing readiness Python -B evaluate-operations.py under the raw root.
Metadata pins full product commit. Verification command:Python -B verify-evidence.py;
passed,exit0,verification.log. It asserts original case/catalog equality, current
messages/schema/model/template/configuration, raw schema validity, source-capture
byte hashes, call counts and context headroom. Manifest seals21artifacts/12captures.
Routing input3527-3563tokens within8192; minimum3853tokens headroom AFTER768output
and8reserved tokens. Replay durations are not full two-stage model latency.

SYSTEM_PROMPT SHA256 unchanged:
e84c54ce7dce6f4cba0e39c02d7388a06caf3048714aa86f49c08cce95abe65f.
New decoder schema SHA256:
5365dfc1d20c2b9cc61e8c11ea4ac943d5bc42d09fb0f5eed5ebf3404bc17d15.
Unchanged style prompt/schema:
0cbf0d85e492d178cad5fc4d822cd65b0323e74ce16f1de09887332b78ff84db /
1bb408daa26acd5a6190cea9e094fdb85186d6c82278b30514933e4461e03b22.
Six-case set SHA256:ff678f3a313dca4cfd025f522ecb35d524fceda9da9a9f2b928110c3a1955647.
Report SHA256:b7fa65866bb52fc39ba16959113ad626c5f9da935c752383108f97f2fc29557e.
Manifest SHA256:c0d13bfba36afc1d10b496634f5bc31a509c091fad9f63466b6ad223c6116c51.

Pinned runtime remains llama.cpp b11718-547208dca,official image
sha256:4b7be0376002b4450a357a109bab804093ff9251193cc75ed4ce0cb39953ff5c;
Gemma SHA2563cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80,
template74a88f94c57c14e22dcdbe08e94127f42b87c6f584cb73838e73e32126f3f6b3.
Temperature0/seed0/output768/context8192/constrained JSON/CPU8threads/one slot;
reasoning_effort=none matches template preflight and generation. Original model
mount read-only; no weights copied. Task container stopped12:25; inspect=exited.
Other containers/worktrees unchanged. Institutional approval/activation remain false.

The owner was asked whether the remaining style errors must hold Phase07 or be
documented in an offline completion review. No reply yet; a preselected answer or
elapsed time is not approval. This asks for an exit-quality target absent from the
phase plan, not permission for this already-authorized correction. Preparing a
completion review would not itself waive the route mismatch or authorize Phase08.
Keep Phase07 active with no complete handoff until its actual exit decision.

Final documentation/phase-state gate:570passed/11subtests11.29s,exit0;
final-docs.log. Command:readiness Python -B -m pytest -q -p no:cacheprovider
--basetemp=raw-root/final-docs tests/test_docs_hygiene.py
.agents/skills/bintanong-phase-handoff/tests/test_phase_state.py.
git diff --check passes; phase state validates active7; advancement is correctly
withheld because no complete Phase07 handoff exists. Final docs wrapper is in Git;
bec3d8e remains the exact verified/inferred product, not an institutional release.
