# Independent SPEC review — ae383ca05f98a4a2d2e25979110bbef2504850aa

CHANGES NEEDED — 3 Medium findings; 0 High, 0 Low.

1. **Medium — embedded final text escapes leakage detection.** `evaluation/protocol.py:180` uses whole-example token-set Jaccard. Append the exact final query and acceptable claim to 100 unrelated context tokens: `prompt_example_findings` returns `[]`. Spec: phase plan line 72, “final answers/examples never tune prompts”; README line 7 prohibits final queries/gold answers in tuning. Check normalized containment before the near-duplicate heuristic.

2. **Medium — verified applicability version is unchecked.** `evaluation/case.py:127` validates only version-id shape; `evaluation/protocol.py:102` resolves gold spans without resolving scope. Replace a verified final fixture's scope.version_id with `ver-unregistered-wrong-1`, retaining registered gold spans: validation returns `integrity_ok=True`, no findings, coverage 1. Spec: phase plan line 74 requires “applicable version/scope” and source-backed review; README line 9 keeps missing verified scope pending. Resolve the declared version and its supporting-version association; no office policy needs inventing.

3. **Medium — duplicates inflate coverage and are sealed.** `evaluation/protocol.py:190` counts repeated IDs independently; `:131` silently collapses them when sealing. Five verified Taglish fixtures, one per category, repeated ten times produce coverage `MET`, total 50, despite five distinct IDs. `make_freeze` accepts them and seals five digests. Separate duplicate findings in set validation do not protect these public APIs. Spec: phase plan lines 74/82 require fifty independently verified cases; README line 35 requires verified totals. Refuse duplicate IDs when sealing and prevent repeated IDs contributing coverage.

Runnable exact reproducers: adjacent `spec-reproducers.py`, system `py -3.13`, bytecode disabled.

Fresh archived focused checks: **199 evaluation + 378 fix-pass-3 contracts + 707 parity/governance = 1,284 passed**, zero failures/skips. Archive/tests import paths, importlib, explicit rootdir/confcutdir, no pytest cache, external basetemp. Initial collection-path errors were environment setup. Both synthetic and external real traces pass the archived checker.

Task 4 pending cache/PDF association, synthetic rules, absent authorization/final coverage, declared-role authentication and Direct routing are documented limits/owner decisions, not findings. No protected-package edits or source activation found in the supplied diff.