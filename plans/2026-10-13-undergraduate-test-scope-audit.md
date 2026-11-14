# Undergraduate test-scope audit - 13 October 2026

Owner requested cleanup of tests for the newly excluded audiences. Resume baseline
`463e01b`, clean; AGENTS/scope policy, active plan/checkpoint/handoff and relevant
master requirements read. Thesis physical17–18 and routing PNG consulted again.

Audit covers162tracked paths:140Python modules with1830test definitions,
18data-fixture files, plus supporting tracked documents. No dedicated positive
Medicine, Law-program, graduate, laboratory-school or faculty/staff-only policy
tests/benchmarks were found. The tracked policy/procedure fixtures are synthetic
parser/contract evidence. The raw source-derived grading/geometry diagnostics live
in historical ignored evidence, not the pytest suite; their corrected active review
queue already contains18undergraduate rows. Those historical seals are preserved.

Two generic PDF geometry fixtures used Law/Business Law wording. Business Law can
be an undergraduate course; these cases did not test a Law-program policy. Replace
the synthetic labels with Art/Creative Art to avoid that ambiguity, preserving
all glyph positions, token lengths, assertions and test definitions. Zero tests
deleted; two existing fixture bodies cleaned. No production behavior changed.

Retain the two negative private-fact origin guards (`staff_ledger`, `staff_entry`):
they reject institutional/staff-record claims in private context. Retain laboratory
unit tests, which concern undergraduate course components, not laboratory school.
AGENTS now expressly applies undergraduate scope to positive policy test fixtures
and retains generic parser and negative scope/privacy/security coverage.

## Fresh verification

External audit/log/temp root:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-test-scope-cleanup-20261013/`.
Use existing approved Python3.13.7 interpreter under the readiness evidence venv.
PYTHONUTF8=1/PYTHONIOENCODING=utf-8; TEMP/TMP point to `<audit>/tmp`; pytest cache
disabled and basetemp external. No installs, dependency changes or source edits.

- Baseline: approved Python `-B -m pytest
  tests/test_prospectus_b2_codex_review.py tests/test_prospectus_b2_review_fixes.py
  -q -p no:cacheprovider --basetemp=<audit>/pytest-before`:
  99passed/1skipped3.11s,exit0. This is fixture cleanup, not a new behavior fix;
  no new RED or production implementation is claimed.
- After: same command with both modules plus `tests/test_contracts_governance.py`,
  `tests/test_contracts_survivors.py`, `tests/test_policy_text.py`,
  `tests/test_policy_chunks.py`, `tests/test_procedure_text.py` and
  `tests/test_docs_hygiene.py`, basetemp `<audit>/pytest-after`:
  658passed/1skipped72.72s,exit0. The whole product suite was not rerun or claimed.
- System Python `-B <audit>/audit.py`:162paths inventoried; only the two negative
  staff-origin matches remain, no excluded-audience positive policy cases found.
  Raw audit result is `audit.json`. An initial diagnostic regex omitted the
  underscore-qualified negative origins; the corrected regex explicitly captures
  those two reviewed cases. An initial multi-file patch failed its AGENTS context
  atomically, then the corrected patch applied; no partial changes were retained.
- Final documentation hygiene after writing this report: approved Python
  `-B -m pytest tests/test_docs_hygiene.py -q -p no:cacheprovider
  --basetemp=<audit>/pytest-docs-final`:351passed0.93s,exit0. This overlaps the
  earlier related gate and is not an additional count of unique product tests.
- `git diff --check` and `phase_state.py validate` pass. The one existing skipped
  geometry-module case is guarded for Windows symlink privileges.

No parser/security tests removed and no production code, original dataset,
sealed review packet or source authority changed. Read-only GitHub MCP repository
identity checked. Current next action remains the owner's18row undergraduate
grading review, then source-bound correction/undergraduate selection. Phase05
formal exit remains blocked and Phase06 has not started.

Checkpoint head names verified baseline `463e01b`; the following seven-path
fixture/rule/documentation commit is discoverable through Git, avoiding a
self-referential metadata SHA. No raw/private artifacts are staged.
