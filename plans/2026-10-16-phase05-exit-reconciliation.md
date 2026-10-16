# Phase 05 exit-requirement reconciliation — 16 October 2026

Phase 05 remains active and blocked. The bounded document comparison is complete;
the formal retrieval exit gate is not. The next work is to define the remaining
source-aware retrieval policy and its integration boundary, using the existing
evidence. Another curriculum sweep or claim-report layer is not required.

## Resume basis and architectural check

Resumed at `a7786ee`, following the exact next action in the checkpoint and
[closed comparison](2026-10-16-document-evidence-calibration-report.md).
The checkpoint's `9c76e83` was the documented parent of that closure, not missing
implementation. Product paths remain unchanged from `232a418`.
The owner's deleted `artifacts/.gitkeep` and untracked `backend/artifacts/` are
preserved and excluded from this increment.

Read the active plan/checkpoint/blocked handoff, Phase 04 complete handoff,
[CLI handoff](2026-10-15-phase05-cli-handoff.md), ledger and current progress.
Consulted master sections 1, 3, 6, 10, 11 and 13; ingestion README for the separate
candidate-delivery status; undergraduate-scope, source-gap and dataset-location
policies. Read thesis physical pages 17–18 and 39–44 and inspected the actual
runtime routing PNG. No new architectural discrepancy: preserve the master's
existing correction that missing student facts mean unknown, rather than a
proved failure. The thesis prerequisite example remains illustrative.

## Requirements against current evidence

| Requirement | Evidence available | Remaining exit evidence |
| --- | --- | --- |
| Tasks 1/2: matching query encoder, pinned release and trusted scope/entity filters | Existing query/engine/database implementation and historical disposable-role verification; saved real-model vectors and fingerprints | Final verification of the selected integrated configuration and applicable migration/ACL/RLS state; offline rankings are not an approved-release RPC replay |
| Task 3: complete, deduplicated, bounded context | Existing context builder, required neighbors and optional reviewed-group display; sealed budget/citation observations | Verify the selected policy uses the intended formatter/strategy and preserves limits on the actual retrieval path |
| Task 4: development-calibrated relevance/coverage and insufficient evidence | Fixed k3/5/8, threshold and budget comparisons; language/category metrics; explicit source-bound claim reports | Define and test a versioned retrieval policy joining applicable evidence, requested claim and source limitations; no scalar/default policy was adopted |
| Task 5: structured source-linked retrieval result | Existing debug result with scores/configuration/locators and sealed citation bindings | Verify every result in the final gate resolves to its source and exposes the selected policy's gaps; source-field availability is not an answer-permission flag |
| Task 6: approved development cases and failure analysis | 75 accepted wordings; 39 document probes compared, 18 structured reservations, 18 existing controls; 69 variants have observations | Run the final selected retrieval policy against the applicable accepted cases, with explicit expected evidence/insufficiency and separate language/category results |
| Source governance and ingestion prerequisite | Selected owner-confirmed undergraduate fields, preserved originals/spans, inactive candidates and recorded source defects | Reconcile the selected release manifest, content/applicability decisions, review coverage and issuing-office verification at their applicable boundaries; candidate delivery is not corpus-wide approval |
| Final handoff and advancement | Valid Phase 05 ledger with blocked handoff | Fresh full exit checks, exact versions/digests and reviewed recovery closure before a complete handoff and successful can-advance |

The matrix distinguishes historical evidence from verification performed in this
resume. It does not reopen completed code delivery or require a full-document
audit of every retained original before bounded offline development.

## What the completed comparison establishes

At k3 / similarity .5 / 2048 tokens, all four tested mode/strategy combinations
retain 18 reviewed-field-available and 21 insufficient-evidence results. Related
expected context is complete for 31/39 raw and 38/39 trusted-subject probes.
These inherited observations are conditional on researcher annotations.
The fresh read-only seal check verifies all 41 observation/review files and the
recorded manifest digest:
`035eb15bc0f97d157f2e631d53aaedad3aa91fdd564f2dcf4efc30ec2c8b0c86`.

The 21 insufficient cases are not 21 failures requiring invented evidence.
Unavailable/currentness/payment claims and preserved conflicts can legitimately
remain insufficient. The remaining T1 context miss concerns an unavailable
current-year deadline; recovering related enrollment text cannot supply it.
Conversely, a clean assembly does not establish claim support. Expected context,
field availability, unsupported-case detection and generated-answer accuracy
remain separate measurements.

The retrieval engine still defaults to `uncalibrated-v1`, and its final gate
checks that policy-name prefix. Offline subject/claim helpers are not joined into
that engine. Giving settings another name is not calibration or a reviewed
source-aware policy. See [engine](../backend/bintanong_retrieval/engine.py) and
[settings](../backend/bintanong_retrieval/types.py). This is an existing integration
gap, not permission to activate a configuration.

## Boundaries that prevent unnecessary work

- Phase 05's gate runs without LLM answer generation. Unassessed answer
  sufficiency is reported honestly; answer generation/validation belongs to the
  later master phases and is not a new Phase 05 prerequisite.
- Trusted scope/entity input is already the Phase 05 contract. Automatic
  multilingual interpretation/routing remains Phase 07; final policy tests must
  disclose supplied inputs and must not derive runtime subjects from gold IDs.
- The 18 structured reservations are future structured/Symbolic capability
  evidence. The six D1/D2 variants need no new vector experiment to close this
  document-retrieval diagnostic. Prior curriculum probes remain preserved.
- Current-school-year authority, F04's disputed digit, G01/original G02 and known
  source cutoffs/conflicts stay held. Do not request unavailable continuations or
  repeat settled applicability/wording decisions. School verification is raised
  on actual new evidence or before institutional activation, not as a blanket
  development stop.
- The final thesis benchmark and blind generalization evaluation remain separate
  from this exposed development set. No new question batch is needed here.

## Exact next action

Specify the smallest source-aware retrieval-policy contract for Task 4 before
changing implementation. Name the student capability: retrieve applicable
document evidence and expose unsupported or limited requested claims without
turning relevance into permission. Its evidence path is the existing pinned
retrieval/context result plus reviewed source metadata and explicitly supplied
trusted request information. Its exit target is master 10.1 step 6 / 10.3.

Resolve one interface question: what trusted request and source-review data must
the engine receive to distinguish relevant context from supported, missing or
unassessed claims, while preserving old debug behavior? Inspect and reuse the
existing subject/claim helpers. Keep scope/edition conflicts and empty results
explicit; do not add another offline sidecar. Prepare the design and focused
synthetic RED/GREEN acceptance cases before implementation. Do not implement
Phase 07 NLP, executable Prolog or a new scalar default under this task.

After that bounded implementation, evaluate the selected policy with saved
accepted-case inputs/vectors wherever compatible. Reconcile source/release
governance separately, then run the formal runtime/database and full exit checks
when their prerequisites are available. Shared database changes, activation and
Phase 06 retain their existing boundaries. This report is a verified progress
checkpoint, not a complete phase handoff.

## Verification in this resume

Used the existing Python 3.13 readiness environment, without installing anything:

```powershell
$p05Python = 'C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe'
$reconcileRoot = 'C:/Coding-projects/bintanong_workspace/audit-evidence/p05-exit-reconciliation-20261016'
& $p05Python -B -m pytest tests/test_retrieval_engine.py tests/test_retrieval_query.py tests/test_retrieval_context.py tests/test_retrieval_evaluation.py tests/test_retrieval_cli.py -q -p no:cacheprovider --basetemp "$reconcileRoot/runtime-tests"
& $p05Python -B -m pytest tests/test_docs_hygiene.py .agents/skills/bintanong-phase-handoff/tests/test_phase_state.py -q -p no:cacheprovider --basetemp "$reconcileRoot/docs-tests"
python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py validate --repo .
python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py can-advance --repo .
python C:/Coding-projects/bintanong_workspace/audit-evidence/p05-document-evidence-calibration-20261016/seal_evidence.py verify
git diff --check
```

Focused retrieval checks: 36 passed / nine subtests, 0.82s, exit 0.
Documentation/ledger preflight: 498 passed / 11 subtests, 12.86s, exit 0.
Phase validation passes; can-advance returns 1 as expected for blocked Phase 05.
The 41-file seal matches; product-path comparison against `232a418` is empty.
Final documentation verification is recorded in the checkpoint/current progress.
Raw logs stay under the ignored reconciliation root above.

No source conversion, vector encoding, sealed writer, full/native suite, database
operation, model download or dependency change was performed.
