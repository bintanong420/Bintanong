# Recovery source access and answer order

Owner review: the Sources action and Source quotations disclosure compete, and the
answer leads with recovery timing before answering which courses are affected.
Candidate code `0634d12c`, worktree `p12-pr20`, PR20 feature branch only.

## Changes

- V2 recovery presentation shows affected subjects first, followed by Recovery plan,
  projected return, interpretation, assumptions and the primary checked draft. Other
  drafts/options remain expandable. This fixes the dependency-then-recovery question
  family; it is not a general semantic ordering engine for arbitrary chat topics.
- Recovery reuses the explicit-plan source channel: pinned offering routes, source
  passage digests, exact reviewed field text and page checks. A dependency package
  carrying routes requires its recovery result; its clauses must match the pinned routes.
- The adapter now carries existing field/span associations from chunk metadata into
  the source passage, matching name/value/blank status exactly. Missing or conflicting
  associations still fail. Original chunks, source wording and reviews stay unchanged.
  The same adapter constructs the pin's passage digest and the returned source cards.
- Source labels reach the source picker. Added the existing maximum academic load
  chunk pointer to the recovery source roster, under settled owner D5 (4 November),
  already recorded in the recovery plan of action and load-policy review reference.
  No new policy content, interpretation, database write or source activation.
- Remove the quotation disclosure only when returned document cards contain every
  quoted clause on its recorded page. Missing cards or page mismatches retain it.
  Full legacy/copy text is unchanged; no extra retrieval, model call or dependency.

## Verification

- RED: four new ordering/source tests failed on the prior code. The runtime metadata
  and filename regressions also failed independently before their corrections.
- Initial focused gate: 42 passed; expanded pre-metadata gate: 141 passed.
- Final source adapter/guard tests: 13 passed; presentation tests: 9 passed.
  Six real frontend component tests pass. Gates overlap; do not sum them.
- Broader affected gate: 234 passed in 431.98s across recovery/status, explicit-plan,
  source contracts, presentation, runtime catalogue and research orchestration tests.
- Saved router/style-output replay against cached reviewed BSCS 2018–2019 data:
  answered, primary Draft C, 24 source cards (13 curriculum + 11 Handbook), two
  disclosures, affected subjects first. Real Prolog/planner/generation validation;
  replayed inference is not a fresh model-routing accuracy or latency measurement.
- Real-component Edge replay at 1440/390 px, light/dark: one Sources(24), no source
  quotation disclosure, correct section order, keyboard disclosures and no overflow.
  This isolated replay does not certify the authenticated chat/source-picker flow.
- Fresh real-model request through frontend3218/API8023 on `0634d12c`: HTTP200,
  answered, affected courses first, Draft C projected return, two disclosures;
  all24 source GETs return200, including11 labelled Handbook passages and the
  maximum-load/special-class wording. Combined proxy chat plus24 source reads43.06s;
  not a warm pipeline or browser end-to-end latency measurement.
- Ignored evidence: `audit-evidence/pr20-local-staging-20261107/` under the workspace;
  `replay-recovery-sources.py`, `recovery-source-replay-debug.json`,
  `recovery-source-replay-view.json`, `source-ui-browser-review.json`, screenshots,
  `source-live-stream.txt` and `source-live-result.json`.

## Runtime and remaining checks

API8023 loads `0634d12c`; existing frontend3218 build remains `9833bb7a`.
Staging identity, frontend proxy health and fresh chat/source-endpoint checks pass.
Next: owner exploratory review, independent acceptance and paired language/latency checks.
No merge, evaluation/mainline reload or institutional release. Existing source gaps,
unknown course checks and offering/approval qualifications remain.
