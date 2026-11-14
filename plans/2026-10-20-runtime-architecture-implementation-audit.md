# Runtime architecture implementation and completion-claim audit

Owner challenged the completion claim against the supplied runtime routing diagram
on20October2026. Starting HEADe6dee83 was clean. The earlier completed Phase08/09
records describe offline candidate milestones; they do not establish that the
complete diagram operates with real services and institutional data.

## Finding

Backend orchestration/composition code exists. A configured real-service request
through the whole diagram has not been demonstrated by the inspected evidence.
Calling the overall pipeline finished from the offline milestone labels was too
broad. The immediate priority is backend integration readiness in p09, not Phase10.
Preserve the historical milestone evidence and the owner's separate-branch preference.

## Diagram to actual code

| Diagram responsibility | Implementation | What is established |
| --- | --- | --- |
| Query preparation/tokenization, multilingual interpretation and adaptive routing | [routing contracts](../backend/bintanong_routing/contracts.py), [Router.route](../backend/bintanong_routing/router.py), [model transport](../backend/bintanong_routing/transport.py) | Host normalization/grounding and model interpretation/style calls exist; transport templates/counts tokens before inference. This does not prove full-pipeline language/route accuracy. |
| SEA-LION query vector and database context retrieval | [RetrievalEngine.retrieve](../backend/bintanong_retrieval/engine.py), [query encoder](../backend/bintanong_retrieval/query.py), [RetrievalAdapter](../backend/bintanong_orchestration/adapters.py) | Component implementation exists. The orchestration smoke substitutes a manual Encoder and fake database Client. |
| Typed Prolog query and symbolic rules | [SymbolicAdapter](../backend/bintanong_orchestration/adapters.py), [CurriculumRuntime](../backend/bintanong_symbolic/runtime.py) | Existing fixed operations invoke the actual Janus runtime in synthetic smoke tests; institutional rule execution keeps its own boundary. |
| RAG/Symbolic/Hybrid dispatch and joining | [Orchestrator.run](../backend/bintanong_orchestration/orchestrator.py), [assemble](../backend/bintanong_orchestration/integration.py) | Code selects the required branches, waits for Hybrid and checks membership/version/status/scope. It consumes reported conflicts; it is not a general semantic proof that arbitrary document prose agrees with rules. |
| Augmented response generation | [AnswerPipeline.run / Generator.generate](../backend/bintanong_generation/generator.py) | The callable pipeline awaits orchestration, then generation under a remaining deadline. Actual-model observations supplied preassembled fictional IntegrationResult inputs rather than executing the preceding diagram. |
| Output validation and NO loop | [validation](../backend/bintanong_generation/validation.py), [bounded generator loop](../backend/bintanong_generation/generator.py) | Deterministic checks plus a fallible model support check; one answer repair over unchanged evidence. Actual checker-approved scope errors remain. |
| Render output | [candidate renderer](../backend/bintanong_generation/render.py), [API](../backend/bintanong_api/main.py) | Host-rendered candidate plain text exists. The API exposes health probes only; student HTTP/UI composition belongs to Phase11 and has not been built here. |

The key call chain is already coded:AnswerPipeline.run -> Orchestrator.run ->
Router.route -> retrieval and/or symbolic adapter -> assemble -> Generator.generate
-> validate/render. Code presence and test composition are different evidence from
a successful configured run of every actual service in that chain.

## Exact verification limits

- [Orchestration smoke](../tests/test_orchestration_smoke.py):actual Router,
  RetrievalEngine and Janus; FakeTransport,manual Encoder and fake database Client.
  It stops at IntegrationResult and does not generate the final answer.
- [Generation composition test](../tests/test_generation_pipeline.py):actual
  AnswerPipeline/Orchestrator/Generator control flow,but scripted routing,
  fake documentary/symbolic ports and EchoEvidence draft/check output. It is not
  an actual-model/embedding/database/Janus full-pipeline run.
- [Actual-model observations](2026-10-19-phase09-structured-generation-observations.md):
  real Gemma for final generation/checking only,with fixed fictional evidence.
  Five answers/one fallback at240s; all answers130-172s; scope concerns remain.
- [Release providers](../backend/bintanong_orchestration/ports.py):the default
  HeldReleaseProvider refuses execution before routing. The delivered usable
  provider is manually injected SyntheticReleaseProvider; an institutional release
  loader/application composition has not been delivered.

Fresh targeted verification:18passed2.94s,exit0. Selections:
`tests/test_orchestration_smoke.py`, `tests/test_generation_pipeline.py`,
`tests/test_orchestration_pipeline.py::test_default_provider_holds_without_model_or_evidence_calls`.
Existing readiness Python3.13,-B,-p no:cacheprovider,offline model flags and external
TEMP/TMP/--basetemp. Raw log:workspace/audit-evidence/
p09-architecture-claims-audit-20261020/composition.log. No new model experiment,
service startup,source activation,dependency change or database operation.

## Remaining backend integration work

Provide an explicit runnable composition of the actual model transport,query
encoder,database retrieval,typed Janus runtime and Generator. Demonstrate one full
request per route with controlled test data and a trace identifying each real
service,route,evidence/rule identity,decision,validation/repair and final output.
Do not substitute a preassembled evidence package or scripted model/vector/database
response and call that real-service integration. Keep synthetic test data clearly
labeled; do not bypass institutional release/source-authority or runtime gates.

Then assess the actual composed outputs and whole-request deadlines. Scope wording,
language fidelity,known retrieval limits and source holds must remain visible.
The current file-based can-advance result validates recorded phase artifacts; it
does not establish this broader runtime readiness. Separate HTTP/UI work remains
Phase11; its absence is not a reason to postpone the internal backend proof.

Current next action:finish the backend composition/verification work in p09 against
this diagram before proposing Phase10 advancement again. This audit corrects the
completion claim; it does not invent institutional approval or erase earlier work.
