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

Semi-alignment is feasible without changing the other developer's FastAPI/plain
HTML/CSS/JavaScript stack or specified researcher workflow. Use the current
frontend's neutral light/dark palette, subtle borders, compact controls and 4/6/8px
radius scale (`frontend/app/styles.css:24,46`). Keep the dense review workspace:
queue, original PDF, extracted fields, decisions/reasons, companions, history/export.
Preserve status/highlight colors, focus/keyboard behavior and local security.

Use scoped reviewer CSS variables (`prospectus_review_gui/static/review.css`).
Avoid importing the student's chat layout, authentication or frontend build stack.
Inter/Geist currently come from `next/font/google` (`frontend/app/layout.tsx:2`);
use a local system-font fallback unless suitable installed assets already exist.
Student appearance supports light/dark/system; the existing reviewer follows OS
preference. Shared preference storage across origins is not automatic.
Browser/light/dark/keyboard/responsive checks remain required after implementation.

## Grilling round 1: open owner decisions

1. **Operator workflow:** keep prepare/build/verify and local release commands in
   the terminal, with the browser dedicated to review, or drive those actions from
   the browser too? Recommend the specified CLI plus review-only UI for v1.
2. **Reviewer concurrency:** one active reviewer per packet, or simultaneous shared
   editing? Recommend one writer per packet with save/reopen and a decision trail;
   different packets can be reviewed independently.
3. **Delivery milestones:** require the full seven-command lifecycle before any
   usable delivery, or deliver prepare/review/build/verify first and the disposable
   local stage/publish/rollback rehearsal second? Recommend two milestones while
   retaining both in the overall acceptance scope.
4. **Extraction expectation:** support inputs the existing PDF/candidate path can
   process and visibly hold unsupported cases, or require additional scanned/layout
   support before v1 acceptance? Recommend existing supported paths plus visible
   holds, with any additional OCR/layout work scoped separately from the wrapper.

Wait for answers before settling these branches or changing the feature plan.
Later questions will follow the decisions, rather than assume them in this round.
