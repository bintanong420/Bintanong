# Phase E Tasks 1–4 Spec recheck ROUND1

Verdict: APPROVED. Remaining scoped specification defects: NONE.

Scope: clean committed fix3c545630e30f2e388f52880c8c54656d2825d097..24dffef6940ffba3c52dc2f2525b277157d91485. Read round1/report.md and checkpoint.json; reviewed only the changed shared source guard and13 added regression/control cases. No Quality-axis or broad gates. No repository writes, installs, staging, commits, agents or owner/dev movement.

## Original findings resolved

- rag.py:94–105 now compares the complete canonical code/title/prerequisite field rather than searching a word-boundary substring. Existing loose normalization applies only to full code equality. Partial code suffix, title and prerequisite assertions are rejected explicitly.
- rag.py:107–112 now requires complete canonical unit-field equivalence and parses numeric units from the canonical printed field. Printed3/2 cannot certify claimed total3.
- rag.py:84–86 restricts each role's admitted cells to the actual table and source row, including canonical spanning cells containing that row. A different course row's prerequisite cannot certify the claim merely by being in provenance.
- rag.py:99–103 handles empty claims: empty code/title are rejected, and empty prerequisite must match the actual own field. Genuine blank/missing prerequisite controls remain blank_unreviewed and retain unreviewed wording.

The13 new cases comprise five original regressions, three complete-field/normalized-code/canonical-spanning controls, three blank-claim regressions and two genuine blank/missing prerequisite controls. The changed guard remains in candidate admission; no audit/parser/shared verifier/unit-owner behavior was changed by this fix.

## Independently observed evidence

Environment: PowerShell, system py -3.13, PYTHONDONTWRITEBYTECODE=1, cwd C:\Users\Hawksprey\source\repos\Bintanong-wt\phase-e. External logs/basetemps only.

1. py -3.13 "<batch1>\spec-repro.py"
Observed exit0. All five original probes accepted=false, explicit expected rejection reasons; no course or course aggregate emitted. Log: round1/spec-repro-recheck.log.

2. py -3.13 -m pytest -q "<batch1>\test_spec_adversarial.py" --import-mode=importlib --rootdir "<batch1>" --confcutdir "<batch1>" -p no:cacheprovider --basetemp "<round1>\spec-adversarial-temp"
Observed5passed in0.29s, exit0. Original independently written external tests were unchanged. Log: round1/spec-adversarial-recheck.log.

3. py -3.13 -m pytest -q tests/test_prospectus_chunks.py tests/test_prospectus_authority.py tests/test_prospectus_parser.py tests/test_prospectus_course_checks.py -p no:cacheprovider --basetemp "<round1>\spec-recheck-temp"
Observed297passed,13subtests passed in12.35s, exit0, no focused warnings. Log: round1/spec-recheck-focused.log. Includes all13 new regressions/controls and the existing PhaseC/parser/course-source checks.

Root broad suite/self counts were not rerun or claimed as independent observations. Task5/Task6, corpus/source/human gates and Quality review remain outside this narrow specification recheck. Stricter admission can reject unsupported transformations/continuations; later corpus evidence must identify such cases rather than weakening ownership/equality checks.

Confirmed remaining scoped findings: NONE.
Unconfirmed scoped suspicions: NONE.

APPROVED.
