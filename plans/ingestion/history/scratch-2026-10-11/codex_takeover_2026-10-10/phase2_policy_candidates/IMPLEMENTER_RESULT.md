# Phase 2 Task 3 candidate-policy/preflight draft

Status: root focused acceptance passed, authorized local draft commit complete. No self-review verdict. This is a draft continuation, not formal start, source adoption or phase exit.

Worktree: `C:\Users\Hawksprey\source\repos\Bintanong-wt\phase2-candidates-20261010`

Branch: `draft/phase2-candidates-20261010`; base before root gate: `0caeaba8d8221a0f75b154e94bc3167b780f1407`. Local commit: `a9043513128215c0b45ce213a39e60922382d16a`; worktree clean after commit. Exactly twelve intended paths were staged explicitly; cached diff check passed. No attribution trailer. Evidence: commit.log.

## Actual essential checks

| Run | Actual result | Exit | Evidence |
|---|---|---:|---|
| Initial TDD red | 2 collection errors: missing new register/policy_text modules | 2 | red_01.log |
| First focused green | 46 passed, 0.61 seconds | 0 | green_01.log |
| Multi-page character-range regression red | 5 failed, 31 deselected: full item text incorrectly repeated across page spans and malformed/missing ranges accepted | 1 | red_02.log |
| Final focused green | 52 passed, 46.68 seconds | 0 | green_02.log |
| Root focused acceptance | 118 passed, 73.81 seconds (root-reported actual result) | 0 | root_focused.log, root_acceptance_exit.json |
| Archive source adoption | All seven archived source/test/doc SHA256 values equal adopted bytes | 0 | archive_hash_parity.json, adoption.log |
| Diff formatting | No errors | 0 | boundaries.log |
| Protected paths/formal ledger and plan | Empty diff against base | 0 | boundaries.log |

The final focused set runs the actual loader with a synthetic raw document, stub converter and stub Docling rehydration. It verifies captured bytes, explicit stage/output paths and no subprocess relaunch. No real installed model conversion was run by the implementer. Root acceptance is recorded separately above; independent review verdicts are not claimed here.

## Changed paths (explicit staging only)

Seven verbatim archive adoptions:

- backend/bintanong_tools/ingest.py
- backend/bintanong_tools/document_ingest/__init__.py
- backend/bintanong_tools/document_ingest/inspection.py
- docs/decisions/phase-02-ingest-hardening.md
- docs/decisions/phase-02-inspection.md
- tests/test_ingest_hardening.py
- tests/test_document_inspection.py

Five new Task 3/preflight files:

- backend/bintanong_tools/document_ingest/register.py
- backend/bintanong_tools/document_ingest/policy_text.py
- tests/test_register_minting.py
- tests/test_policy_text.py
- docs/decisions/phase-02-policy-text.md

Source hashes for all twelve paths are in source_hashes.json. No protected contract/extractor/API/embedding/dependency/lock files, formal phase metadata, integration GUI or current-progress documents changed.

## Task 5 consumer interfaces

`register.mint_pending_register(manifest, *, synthetic=False)` returns a tuple of actual Phase 1 SourceDocumentVersion contracts. Entry keys are exactly filename, sha256, acquisition_locator. `pending_version(snapshot, locator, *, synthetic=False)` mints one from captured bytes. `load_pending_register(records)` reparses the whole set and calls check_register. `version_for_snapshot(snapshot, records)` performs the same preflight and selects the captured source hash. All initial states are enforced; category source_document only; IDs derive from the whole byte digest. Identical bytes merge logical locators; different bytes are separate editions; no filename authority.

`policy_text.extract_policy(snapshot, register, *, input_root, out, converter=None, printed_page_labels=None)` returns frozen PolicyCandidates and writes raw_docling.json, raw_docling.meta.json, policy_candidates.json and completion manifest under a new/empty external output folder. The caller supplies an actual InputSnapshot and pending register. Installed imports precede the loader; missing installed Docling raises before relaunch logic can execute. No production monkeypatch.

`read_policy_items(raw, version, *, printed_page_labels=None)` reads raw structures and is also the synthetic test interface. It does not authenticate a caller-supplied raw JSON association to bytes. PolicyCandidates carries version, raw_item_count, page_count, units, item_omissions and page_omissions. `check_invariants()` enforces exact raw item and physical page accounting; `as_dict()` is the JSON/report interface. PolicyUnit carries exact source_text, raw item ID/label, all pages and raw provenance JSON, heading path, printed_scope, exception_to, SourceSpan tuple and rejection_reason. Every anchored span uses SourceSpan.parse and check_span_binding. Missing/invalid geometry and missing/malformed/gapped multi-page character ranges leave explicit unanchored units.

## Rulings and practical limits

- Register mint/validate comes before conversion in this draft, as the necessary Task 5 prerequisite prefix. Formal plan sequencing/status is unchanged.
- Raw text-item reader used without a real Handbook spike because synthetic cases establish actual adapter loss (empty items and multi-page provenance). Institutional spike/measurements remain NOT RUN.
- Exceptions and printed scopes are conservative candidate annotations. No semantic policy interpretation, USG-to-CSG inference, authority, source verification or approval is claimed.
- Shared namespace checks refuse private-session IDs/facts; they are not a semantic personal-data detector. Authorized source selection remains the caller's boundary.
- Printed folios are explicit caller observations; PDF page-label strings are not silently substituted.
- Multi-page character ranges are required to avoid invented per-page text assignments. A single provenance entry without ranges uses that raw item's full text. Tables remain for later procedure/chunk work.
- No completion manifest means incomplete output. Failed partial output must be retried into a new folder; originals never receive writes.

Skipped: four institutional conversions, real-model synthetic conversion, Handbook spike, ten-document OCR/photo gates, broad suite, mutation campaign and independent review verdicts. Scope, issuer/effectivity, human content review and all institutional authorization remain pending; this is not merge-ready or phase-exit evidence.
