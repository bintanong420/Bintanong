# Related context and missing-content feedback

27 October 2026. Local researcher tool, Phase 11 ingestion workstream.
Owner requested the backend branch merge, a clearer related-record selector, and
a way to flag text missed by extraction or retrieval. The owner clarified that
unhighlighted text can already be present on the same PDF page.

## Delivered behavior

- Merge `0bb3dad` incorporates `origin/feat/p11-backend-api` at `e5495b4`.
  All 18 incoming commits are documentation/review changes; no API source diff.
  The two central snapshot conflicts retain the ingestion worktree state and
  link incoming review decisions. No origin/dev/student frontend merge or push.
- `0959a43` adds omission feedback to the existing locked, hash-chained review
  journal and authenticated local `/api/decision` route. Page/source/version,
  optional normalized region, visible wording, note, researcher and time are bound
  to the packet. Reports remain pending, independently of field/audience approval.
- `0349730` replaces the native multi-select with searchable checkboxes, selected
  record previews, unique page labels, Remove and Show page controls. Current
  record regions retain amber outlines; selected related context uses dashed blue
  outlines. A legend distinguishes them without relying on color alone.
- Show page keeps the current field draft and scrolls to the selected context.
  Unmarked text is not automatically classified as a pipeline omission.
- Report missing content supports a pointer-marked region or a whole-page report
  without dragging. The form accepts visible text and an explanatory note, with
  optional stage attribution including Not sure yet. Save/retry/history/export
  are real local operations; feedback does not create a field or alter a chunk.
- Saving feedback retains unsaved field text, audience and companion selections.
  Original-source defects still use the separate existing source-problem form.

## Source inventory and limits

The running packet remains the verified 72 baseline candidates, 298 fields:
66 Handbook and 6 Charter records. The frozen snapshot still has 78 chunks/vectors.
Incoming documents describe 336 inactive candidates and a registration correction
overlay, but the ignored `audit-evidence/p11-omitted-chunks-20261026/` directory is
absent here. Git does not deliver ignored data. Do not claim those 336 records are
in this GUI or silently regenerate them. The owner can transfer that exact sealed
evidence for a later verified import; keep the 78-chunk baseline unchanged.

Related context is manually selected, not inferred from page proximity. Context
on another page needs its recorded link; unsupported geometry remains unhighlighted.
Feedback preserves a report of a possible omission, not a diagnosis of Docling/RAG
or a content correction, policy decision, institutional approval or activation.

## Verification

- RED: omission API test returned422 because the old command schema required an
  existing field. Region-normalization test failed on the missing helper.
- The browser regression against the previous running UI failed on its native
  multi-select. The isolated updated UI passes searchable selection, context
  highlighting and page-link checks.
- Backend affected suite:274 tests /80 subtests pass in60.55s, using system
  Python3.13, pytest without cache, external basetemp `omission-regressions`.
  Coverage includes save/reopen/export, invalid pages/regions/types, source tamper,
  unknown document, forbidden approval injection, stale revisions and replay.
- Six Node state tests and TypeScript pass. Updated Next16.4.3 production build
  and startup pass using existing dependencies; no installs or lockfile changes.
- Isolated browser rehearsal passes in9.50s: select related record, see dashed
  source regions, navigate to context, mark an area, submit pending feedback,
  preserve the unsaved audience/companion draft, inspect history/Escape, download
  and verify export. All institutional fields remain pending in the test packet.
  Layout has no horizontal overflow at390px and720px zoom-equivalent widths;
  no captured runtime exceptions. This is bounded browser evidence, not full
  keyboard/assistive-technology or whole-corpus accuracy acceptance.
- Browser writes occur only in an isolated copied packet with reviewer
  `Automated rehearsal - not a content finding`, ports3002/8766. Main reviewer
  remains3001/8765. The isolated profile does not use a personal browser profile.
  Evidence/scripts/screenshot: workspace
  `audit-evidence/p11-policy-ingestion/feedback-browser-20261027/`.
  Screenshot: `related-context-desktop.png`.
- Backend command: system `py -3.13 -m pytest -q -p no:cacheprovider`, the nine
  knowledge-update test files including feedback, plus reviewed-policy
  preparation/chunks, service steps and review GUI client. Final repeat uses
  external basetemp `feedback-final-regressions`:274 tests/80 subtests pass in74.55s.
- Browser command: set `BINTANONG_REVIEW_TEST_LAUNCH` to the isolated launch-url.txt
  and `BINTANONG_REVIEW_TEST_WRITE=isolated-rehearsal`, then
  `node --experimental-strip-types --test researcher/tests/document-switch.test.mjs`.
  Writes require the rehearsal reviewer and port3002. The normal integration mode
  only edits browser drafts; no persisted content decisions.

Final main-port verification:updated production build/start succeeds;tracked browser
integration on3001passes in6.32s without persisted writes. Authenticated state shows
72records/revision0;before/after journal hash is unchanged (no journal at either time).
The frozen11files/7seals/78chunk-vector bindings pass again. Current launch link saved
in the existing ignored launch-url.txt;regular browser open requested successfully.
The separate rehearsal service was stopped after verification.

No hosted Supabase, embedding/model execution, release/pin changes or deployment.
Node22.22.3 differs from the declared24.21.0 target; builds/startup passed with that
disclosure. Full repository suite, database roles and release rehearsal remain open.
T4/T5 stage/publish/rollback tooling remains unfinished; Phase11 stays active.
