# Policy Ingestion and Review — Feature Branch Plan

## Readiness and goal

This revised plan is ready for implementation. It replaces the earlier CLI-only plan by including a small local review UI.

Build a repeatable workflow for new Handbook and Citizens’ Charter editions that reduces researcher effort while preserving source accuracy, undergraduate scope and release controls.

- Branch: feat/p11-policy-ingestion-review.
- Base: current Phase 11 commit 7590a71; recheck Git state before branching.
- Work in a separate worktree; integrate back into feat/p11-backend-api.
- Prioritize this before new Handbook/Charter chunk expansion. Keep grading defects tracked separately.
- First implementation commit saves this plan and updates Phase 11 progress/checkpoint. This remains a Phase 11 increment.

## Researcher workflow and interfaces

Provide one command suite with prepare, review, build, verify, stage, publish and rollback operations.

Prepare: accept original PDFs or existing hash-verified candidate bundles, explicit source metadata and an optional baseline package. Preserve originals; produce candidates, extraction findings and a review packet.

Review: open a local browser interface with:

- A queue searchable by document, section, review state and finding.
- Original PDF pages beside extracted text/table fields, with available source-region highlights.
- Separate audience decisions: undergraduate-applicable, excluded or unresolved.
- Content decisions: accept, correct or hold, with reasons and source-gap recording.
- Related blocks and required companions visible together for complete service review.
- Saved progress, decision history and an export action.

Start every new candidate unreviewed. AI-assisted sessions may prepare proposed readings, grouping and mappings using the existing formats. The UI records actual decisions; it does not infer approval from a proposal or an opened page.

Build and verify: consume reviewed decisions and produce compatible chunks, receipts, embeddings, topic assignments, claim reviews and runtime metadata.

Stage: load a verified package as an inactive draft.

Publish/rollback: operate through explicit commands using existing authorization and release controls. The review UI has no database-publication button in v1.

No student-facing API changes are planned.

## Implementation sequence

1. Define the packet and command boundary.
   - Add the workflow under backend/bintanong_tools/knowledge_update/.
   - Use a manifest referencing originals, candidate artifacts, review inputs, baseline selection and target release.
   - Reuse existing contracts; introduce only the wrapper and review-session metadata needed to connect them.
   - Produce review templates without inventing audience labels, institutional authority or reviewer evidence.
2. Implement the local review UI.
   - Use existing FastAPI and plain HTML/CSS/JavaScript dependencies.
   - Reuse suitable PDF rendering, queue, locking and security patterns from the prospectus reviewer while preserving its existing behavior.
   - Bind decisions to exact source/candidate identities and append history rather than overwrite earlier decisions.
   - Refuse stale or mismatched evidence. Missing geometry or unsupported extraction remains a visible hold.
   - Preserve original text separately from corrected extraction.
3. Connect reviewed output to package building.
   - Reuse reviewed-policy builders and source/service/flowchart bindings.
   - Preserve blanks, cutoffs, conflicts, conditions, procedure order and complete companion groups.
   - Require explicit retained/replaced/removed membership when extending a baseline.
   - Build matching subject and claim metadata; never interpret successful database insertion as answer coverage.
4. Generalize verification and release operations.
   - Replace package-specific paths, counts and release IDs with validated manifest inputs.
   - Reuse compatible embeddings; enforce tokenizer and complete-context budgets.
   - Support initial and supplementary source-review paths through existing loaders.
   - Make staging retryable without duplicating or changing conflicting records.
   - Journal publication state, verify hosted/package agreement and restore the previous release and runtime descriptor on failure. Use a stopped-service maintenance window for v1.
5. Document and rehearse.
   - Provide synthetic examples and operator instructions.
   - Rehearse the existing sealed package locally using saved decisions and vectors.
   - Use the next approved expansion batch through the delivered workflow.

## Verification and acceptance

Use RED → GREEN → REFACTOR and small verified commits.

Required scenarios:

- Two synthetic document editions processed without editing Python.
- Included, excluded, shared-audience and unresolved content.
- Staff actions inside valid undergraduate services.
- Corrections, blank fields, source gaps, cross-page steps and missing companions.
- Save/reopen, revised decisions, stale evidence, concurrent writers and safe source-text rendering.
- Wrong-source decisions, altered artifacts, missing topic/claim metadata and incompatible embeddings.
- Actual-role disposable database tests for initial review, supplementary review, inactive staging and retries.
- Publication interruption and rollback restoring both release and runtime configuration.
- Browser verification of comparison, navigation, correction, persistence and export.

Run focused suites and the full repository suite with shared Python 3.13, pytest cache disabled and external evidence/basetemp directories. Disclose unavailable checks. Validate Phase 11 artifacts before delivery.

Acceptance: a researcher can inspect supported candidates, save source-bound decisions and produce a verified staged package through reusable commands. Originals and release history remain intact; incomplete review cannot silently become published knowledge.

## Boundaries

- AI assistance stays in review sessions; no built-in model reviewer or model training.
- No automatic semantic comparison or transfer of approval between editions.
- No new dependencies, schema migrations or public hosting are planned.
- Credentials remain backend-only; the UI is loopback-only with the existing reviewer’s access protections.
- Generated and source-derived artifacts stay ignored under workspace audit-evidence.
- Unsupported layouts are reported honestly; arbitrary-PDF automation is not an acceptance claim.
- Implementation does not authorize new source content, hosted activation, Phase 11 completion or Phase 12 advancement.