# Ingestion continuation — 14 November 2026

Owner asked to continue the unfinished-work checklist. Bounded slice:
`check-draft` CLI and GUI intake step 7, from `p12-dev` at `a518f1c7`.
Task branch/worktree: `feat/ku-draft-rehearsal` / `p12-ku-rehearsal`.
Delivered code/checks `4f4d4079`, independently reviewed and fast-forwarded into
local `p12-dev`; no remote push or runtime reload. Both worktrees clean after integration.
No numbered phase started; Phase 12 remains complete with disclosures.

## Delivered and remaining checklist

- [x] Expose existing retrieval checks through `check-draft` with required package,
  cases, external report and existing workspace model. Exit 0 pass / 2 miss / 1 error;
  argument errors use argparse exit 2 without a report. No database calls/downloads.
- [x] Add PDF and PNG synthetic intake-to-draft rehearsals: upload, prepare,
  explicit review/save/reopen, build metadata, build, verify, question checks,
  inactive staging/readback and repeat staging. Held reading excluded; prior active
  release and original upload bytes preserved.
- [x] Reconcile the GUI intake checklist and document command/measurement limits.
- [ ] Live Docling/image/embedding-to-local-database rehearsal and local readback.
- [ ] Governed fresh-upload activation route, authorization and live rollback proof.
- [ ] Real assisted-packet human review/build and matched effort/accuracy measurements.
- [ ] Unified prospectus ledger build, combined manifest, changed-span review and
  paired document/rule release rehearsal (U0–U6; GUI infrastructure is not completion).

## Verification

System Python 3.13, pytest cache disabled, fresh basetemp under
`C:/Coding-projects/bintanong_workspace/audit-evidence/ku-rehearsal-20261114/`.

- Baseline CLI/checker roster: 28 passed (`baseline-fixed`). Initial invocation
  failed with 25 setup errors because the new basetemp parent did not exist;
  directory created and baseline rerun without application changes.
- RED: CLI `-k check_draft`: 3 expected failures for absent subcommand / 1 pass.
- GREEN: CLI/checker roster 32 passed (`green-cli`); synthetic rehearsal 2 passed.
- Final explicit CLI gate: 5 passed / 4 deselected, including real LocalEncoder
  refusal for a missing model (no fallback mock vectors).
- Independent reviewer: approved, no findings; 34 CLI/checker/rehearsal tests pass.
- Complete knowledge-update test-file roster: 378 passed in 204.18s, exit 0
  (`knowledge-gate`). The subsequently added missing-model CLI case also passes in
  the final five-case CLI gate; do not add overlapping totals.
- `git diff --check` passes; phase inspector valid, no active numbered phase.
- CLI `check-draft --help` passes from the committed task worktree.

Exact commands: `py -3.13 -B -m pytest tests/test_knowledge_update_cli.py
tests/test_knowledge_update_draft_checks.py -q -p no:cacheprovider --basetemp <fresh>`;
rehearsal file separately; final CLI adds `-k check_draft`.
Full workstream roster selects `rg --files tests -g 'test_knowledge_update*.py'`.
Overlapping counts are not summed. No fresh whole-repository/frontend suite.

## Boundaries and context

Conversion, embeddings, fingerprints and storage in the rehearsal are test doubles;
the test uses the real preparation/review/build/verify/check/stage implementations.
This proves component composition, not real conversion, model accuracy, browser
acceptance or a live database transaction. No sources/review packets/services/
database state changed; no activation, hosted writes, dependency changes or push.

Consulted current INDEX/progress, Phase 12 handoff, GUI/unified plans, owner ledger,
master sections 3/11/13/18.3, thesis physical 17–18 and runtime routing PNG.
Undergraduate advisory scope, private-input isolation, source gaps and source/review
gates are unchanged. Original October blockers are historical, not fresh failures.

## Next action

Rehearse a synthetic document with actual local conversion/embeddings and inactive
local database staging using the current fingerprint/freeze preflight. Keep source
approval and activation decisions separate; do not repeat the completed mock rehearsal.
