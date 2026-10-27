# AI-ingestion plan compliance and visible-delivery audit

Owner asked what changed and whether the supplied plan was followed. This is a
read-only implementation/runtime audit; no server restart or source review occurred.
The earlier delivery wording overstated owner-facing readiness. Code and synthetic
proof exist, but the actual reviewer was not updated to demonstrate the extension.

Follow-up: [repo-directed correction](2026-10-27-ingestion-repo-followthrough.md)
now delivers a current-source production UI on3003 with a real packet copy,preserving
old tabs. Ten additional relational regressions and rotated-box withholding added.
The initial findings below remain historical evidence;live AI/native/DB/human gates
are still open. The current unassisted packet explicitly says it contains no AI advice.

## Why the opened screen looked unchanged

Fresh authenticated state from policy API8765:72items,revision0,zero assistance
fields,zero proposed_value fields. The packet uses reviewed_snapshot inputs and
has no assistance recipe or parser_result. No real Handbook/Charter AI parse or
vision verification was run. This remains the original baseline review packet.

The running UI3001 also has the older production build. Its local build marker is
e9df70117f4815948682a2e3063bfeec1f6c011a9012b8a4089d6b7edf7f746e;
the current source/API-origin fingerprint is
2544d9b9baec62367fea7c6423c13eaaf436c32104a0ea0c90e0195523469cb4.
They differ; BUILD_ID timestamp is27Oct02:07. The newer proposal component was
built/tested in an isolated synthetic app, not delivered into this running app.

Rebuilding alone would still show no AI cards: the loaded packet has no AI advice.
The UI addition is a conditional per-field suggestion card,not a general redesign.
Parser/assistance selection and evaluation were implemented as CLI operations;
no GUI upload,provider configuration or strategy-selection screen was added.

## Supplied-plan task checklist

| Task | Status | Evidence and limit |
| --- | --- | --- |
| 0: inspect existing pipeline and pin integration | Done | Existing prepare/template/ReviewSession/renderer/build reused; decisions recorded before implementation |
| 1: source-bound advisory contract/human authority | Done in code/tests | Original/reviewed values stay pending; stale binding and approval injection reject; explicit human journal save |
| 2: minimal provider and deterministic fake | Done in code/tests | Ingestion-only HTTP image adapter; existing httpx; fake and transport tests; no student provider changes |
| 3: native extraction + vision | Implemented, live unverified | Opt-in modes and original page images; no configured vision runtime; full pages used rather than source crops; only recorded field pages sent |
| 4: proposal reviewer UI | Implemented/tested in isolation; running owner UI not updated | Use/Ignore/manual edits/explicit Save tested; current owner build stale and packet unassisted |
| 5: LlamaParse alternate parser | Implemented, live unverified | REST upload/poll/batches/resume; same pending review/build path; no session API key or real provider run |
| 6: Handbook/Charter hardening | Partial validation | Synthetic hierarchy/TOC/header/continuation preservation and grouped tables tested; swapped fee/time fixture tested; no complete semantic/source accuracy validation; TOC conflicts get generic manual findings,not automatic specific diagnosis |
| 7: matched A/B harness | Harness/sample done; experiment not measured |28original pages/84blank rows; comparisons and effort metrics exist; no human gold standard,timings,cost or winner |
| 8: regression/security gate | Partial; full gate fails |1821targeted tests/13subtests pass; broader6949pass/2fail,17DB files excluded; fake-provider/browser proofs do not establish real native/live-provider readiness |
| 9: operator documentation | Done, with delivery correction | CLI workflow and full limits documented; this audit corrects visible UI readiness |

The launch explicitly permits finishing mocked integration when provider credentials
are absent. Live smoke being unrun is therefore a disclosed validation limit,not
proof that no implementation exists. It does not justify claiming operational readiness.

## Remaining acceptance checklist

- [x] Deliver the current frontend build safely in a separate real-data review copy;
  preserve the original session and any unsaved owner draft.
- [ ] Prepare a separate assisted candidate packet and demonstrate it in the owner
  reviewer. Never overwrite/re-assist the frozen reviewed baseline in place.
- [ ] Configure and verify an actual image-capable endpoint; local Gemma's image
  capability alone does not establish a matching projector/running vision server.
- [ ] Supply an authorized LlamaParse session key and run a narrow real parse if
  live comparison is wanted. No credentials should be added to repository files.
- [ ] Resolve the installed Transformers/huggingface-hub conflict in an approved
  environment and rerun the two failing native conversion checks.
- [ ] Finish real-source relational/hierarchy adjudication and matched human A/B
  measurements before claiming improved extraction or reduced cleanup.
- [ ] Run required disposable-local DB checks when Docker is available.
- [ ] Original T4 local lifecycle tooling and T5 full operator rehearsal remain
  unfinished. They are separate from extension Tasks4/5 above.

The actual implemented files,commands and local commits remain in
[results](2026-10-27-ai-ingestion-results.md). This audit did not change code,
dependencies,packets,journals,hosted data or running processes. Existing acceptance
test counts are prior recorded results,not a new test run during this audit.
