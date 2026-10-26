# Policy ingestion plan: reuse findings and design questions

26 October 2026. Read-only code/document inspection for the owner's requested
grilling round. Recommendations below are not owner decisions. No implementation,
conversion, model execution, browser verification or database access occurred.
The feature branch has not been created; hosted Supabase remains excluded.

## Reuse verified in repository code

| Component | Reuse | Remaining work or limit |
| --- | --- | --- |
| Phase 2 `document_ingest/pipeline.py:19` | `run_ingestion()` produces source-bound inactive candidates and accounting | Wrap the extractor; independently review new-edition accuracy |
| `document_ingest/bundle.py:44` | `load_candidate_bundle()` checks file containment, digests and artifact identities | Raw candidates and reviewed/runtime packages need distinct intake validation |
| `policy_text.py`, `procedure_text.py`, `policy_chunks.py` | Parsing, source locators and explicit refusals | PPTX slides remain withheld as `pending_locator_contract`; no implicit PPTX expansion |
| `reviewed_policy.py:96`, `reviewed_policy_chunks.py:64` | Existing reviewed readings and chunk builders | New UI must export exact source/event-bound readings, geometry and companion mappings |
| `reviewed_service_steps.py:58`, reviewed service/flowchart context | Cross-page actions, roles, times, fees and companion associations | Review complete logical steps; preserve unresolved fields |
| `prospectus_review_gui/`, `prospectus_extractor/ledger.py` | Rendering, loopback security, locking and decision history patterns | Course-specific session/question/answer schemas cannot directly represent policy review |
| `bintanong_embedding/batch.py:23` | Resumable batches and compatible vector reuse | Review identity and embedding configuration remain explicit |
| `bintanong_storage/loader.py:31`, `selected_release_review.py:129`, `release.py:28` | Batch loading, selected review and release lifecycle | Inject verified disposable local clients; default clients can read ambient configuration |

Paths without a package prefix in this table are under
`backend/bintanong_tools/document_ingest/`, except the explicitly named packages
under `backend/`. Existing synthetic regressions include `test_candidate_bundle.py`,
`test_reviewed_policy_preparation.py`, `test_reviewed_policy_chunks.py`,
`test_reviewed_service_steps.py`, `test_storage_loader_idempotency.py` and
`test_review_gui_client.py` under `tests/`. They were inspected, not rerun.

The main missing feature is the generic policy review/export bridge and repeatable
command workflow. Database rollback already exists; coordinating it with a local
test runtime descriptor and interruption journal remains additional work.

Saved reviewed-package replay proves repeatability, not extraction accuracy for a
new edition or approval transfer. The historical Phase 2 completion label is
qualified by [the source-exit audit](2026-10-12-phase12-progress-claims-audit.md).
Current reading-order code includes later group/furniture handling; the old Charter
failure was not reproduced and is not asserted as a current failure.

## Compatible UI direction

Owner subsequently approved alignment of both appearance and frontend stack:
Next.js/React/TypeScript UI with FastAPI services. This explicitly supersedes the
original plain HTML/CSS/JavaScript UI choice,preserving the specified workflow.
Carry the prospectus reviewer forward and extend its capabilities to policy/service
review;React browser controls need adaptation while Python behavior is reused.
Use the current
frontend's neutral light/dark palette, subtle borders, compact controls and 4/6/8px
radius scale (`frontend/app/styles.css:24,46`). Keep the dense review workspace:
queue, original PDF, extracted fields, decisions/reasons, companions, history/export.
Preserve status/highlight colors, focus/keyboard behavior and local security.

Reuse suitable frontend components/styles and reviewer evidence/status semantics.
The legacy reviewer CSS documents existing behavior;it is not the new UI stack.
Keep a separate local researcher app and FastAPI review services,preserving student
routes,authentication,runtime configuration and hosted-data boundaries.
Inter/Geist currently come from `next/font/google` (`frontend/app/layout.tsx:2`);
use a local system-font fallback unless suitable installed assets already exist.
Student appearance supports light/dark/system; the existing reviewer follows OS
preference. Shared preference storage across origins is not automatic.
Browser/light/dark/keyboard/responsive checks remain required after implementation.

Fixed fork4e99fb6 has a minimal frontend (Next16.3.5);current frontend uses
Next16.4.3 with additional existing UI primitives. A coordinated,explicit frontend
resource import is required;no stack/dependency availability follows from the fork
alone. The student proxy/authentication uses Supabase and student endpoints;it is
not suitable for local reviewer transport. Resolve file/dependency compatibility
in T0 rather than ask the owner to choose technical file paths or silently upgrade.

## Grilling restart: keep the developer specification fixed

Owner asks for the final recap and grilling pass with the current repository context.
Verbatim snapshots and explicit owner additions are linked in the feature plan.
The original round is superseded: CLI commands plus local review UI, all seven
operations and visible unsupported-layout holds are already specified. Do not
ask the owner to choose a replacement scope or omit the local release rehearsal.

The specified concurrent-writer tests do not establish collaborative editing.
The notes do not specify reviewer UI language or its primary device target.
These are the current independent product questions:

1. **Review ownership:** one active reviewer per packet, with handoff/save/reopen,
   or simultaneous edits to the same packet? Recommend one writer per packet;
   different packets can proceed independently. Preserve lock/conflict tests.
2. **Researcher UI language:** English labels/help, or multilingual labels too?
   Recommend English for this local research tool. The owner's English agent-reply
   preference does not itself decide UI language; student multilingual behavior stays.
3. **Device target:** desktop/laptop review first, or full phone review as a v1
   requirement? Recommend desktop-first comparison with readable narrow-screen
   fallback, preserving keyboard/focus and existing safety controls throughout.

Wait for answers before adopting these recommendations. Later dependent questions
follow the answers; no new implementation or review approval is inferred.
