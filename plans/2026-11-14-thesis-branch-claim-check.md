# Thesis claims and development/evaluation separation

Read-only review requested by owner14November2026. Manuscript:
`E:/Hawksprey/Downloads/development_bintanong_thesis (10).pdf` (208 physical pages).
No PDF, code, configuration, release or benchmark result changed.

## Verified branch state

- Local harness `2620f23f` is an ancestor of local development `ff973c92`;
  development has184 additional commits. Backend diff54files,+5456/-225lines.
- Harness is5commits ahead of published `73f95dcd`; those5change progress notes
  only. Development is3commits ahead of published `a518f1c7`.
- Remote tips checked with `git ls-remote`; no fetch, merge, push or branch switch.
- Follow-up origin inspection confirmed `main=0efbd9d9`, `dev=33c684a6`,
  `p12-evaluation-harness=73f95dcd`, `p12-dev=a518f1c7`. No origin/master exists.
  GitHub connector comparison confirms development186commits ahead/0behind the
  published harness;54backendfiles,+5445/-225lines. Origin/dev is403commits behind
  harness with0unique commits; origin/main is1925behind with0unique commits.
  Main's tip is20September and dev's29October; neither carries newer missing fixes.
  Harness already contains later transfer-direction, context-budget, source-coverage,
  shifting and evaluation-mode fixes beyond origin/dev. Branch-name age does not
  identify the actual evaluated build: use each experiment's recorded SHA/settings.
- Development adds researcher ingestion/review tools, per-topic/compound answer
  handling, clarification binding and answer presentation. Compound and compiled
  routing have opt-in gates; branch membership alone does not enable them.

## Manuscript findings (printed page; physical page is one greater)

- Scope16-17: read-only undergraduate advisory tool; researcher-managed updates;
  English/Taglish replies;22questions/66variants. Consistent with the separation.
- Method96-97: describes Docling/Gemma audit/human review/verdict, then explicitly
  says the evaluated corpus used ChatGPT/Claude assistance before Gemma was added.
  Gemma vision/reviewer code exists in development and is absent from harness.
  Its implementation can be described separately from evaluated response quality.
- Definition24 and recommendation187: mixed-intent questions were not evaluated;
  extending coverage is recommended. New compound development does not contradict
  that statement and must not inherit the existing benchmark scores.
- Artifact172-173 describes core router/RAG/Prolog and reviewed560chunks/39curricula,
  and distinguishes local evaluation from hosted smoke. It does not establish that
  the later development features were benchmarked.
- Recommendation189 says only one Gemma live trial missed a planted error.
  Development receipt `2026-11-12-full-pipeline-startup.md` additionally records a
  successful synthetic5-to15days correction and an unchanged-state USG audit.
  The single-trial wording needs a stated evidence cutoff or an update if those
  later receipts are included. Neither smoke establishes corpus-wide accuracy.
- No branch names or Git commit identifiers were found in extracted manuscript text.
  Add per-experiment version/settings provenance; do not imply all reported metrics
  came from the current development tip or one common run.
- Appendix J printed207 links only the repository root. Since origin/main is older
  than the evaluated system, add an explicit evaluated commit/tree link and identify
  development separately so a reviewer can locate the code behind the reported results.

## Verification and next action

Read complete relevant pages, visually inspected physical97/190, compared Git refs,
backend diffs and development code/receipts. Rendered pages are ignored under workspace
`audit-evidence/thesis-branch-check-20261114/`. No paired live benchmark or full-suite rerun.
Next: preserve evaluated outputs and add explicit evaluated-build versus later-development
wording, using actual experiment receipts to identify each commit/configuration.
