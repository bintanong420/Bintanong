# Independent STANDARDS review — 9bfcada3e524c6328e3f70a3661c2b4ca5f1c6de

CHANGES NEEDED — 1 Medium; 0 High, 0 Low.

1. **Medium — malformed cited-page types receive perfect scores.** `evaluation/rubrics.py:89-95` validates citation keys but never their values; `:116` then builds tuples/sets whose Python equality treats `True == 1` and `3.0 == 3`. A valid verified fixture with integer gold page 1, and an otherwise correct output carrying JSON `page: true`, receives evidence=1, total=1.0 and no flags. Gold page 3 with output `page: 3.0` does likewise. This violates the owner's external-input/type-validation standard and the rubric's promise to refuse malformed outputs. Reject non-integer/bool pages and validate citation hashes/version/locator values before comparison; reuse established constraints without adding dependencies. Add a focused malformed-page regression.

Exact runnable reproducer: adjacent `standards-reproducer.py`; `py -3.13 "E:\Hawksprey\Documents\PalSU Stuff\Bintanong dataset dump\scratch\codex_phase1_review_2026-10-08\standards-reproducer.py"` with `PYTHONDONTWRITEBYTECODE=1`. It imports only the pinned archive and its tests.

Fresh independent focused evidence: **1,500 passed**, zero failures/skips (all evaluation files, fix-pass-3 contracts, parity, governance/governance-fix2 and manifest checks). System Python 3.13; archive/tests first import path, explicit archive rootdir/confcutdir, importlib, disabled bytecode/cache, external basetemp. Both synthetic and external real trace JSON independently pass `check_trace`, retaining pending verification/content review and null approval_id. External builder/cell-check/log evidence confirms the declared cached-extraction exercise and Prolog-builder bypass. No protected API/embedding/tools/dependency-file diff.

The added modules have focused responsibilities, reuse shared contracts/vocabulary and stdlib hashing/JSON, and introduce no dependency or unjustified abstraction. Scope/duplicate/leakage corrections operate at shared protocol boundaries. No additional smell merits a correctness-free rewrite.

Documented pending cache/PDF association, synthetic rules/cases, absent source authorization/final coverage, hash-only registry limitations, legacy Direct routing, and future authentication/persistence/retention implementation are limits/owner decisions, not findings. This review grants no source approval or Phase 1 completion.
