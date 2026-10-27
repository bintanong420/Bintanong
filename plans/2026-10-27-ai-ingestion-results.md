# AI-assisted ingestion delivery and validation limits

27 October 2026. Branch `feat/p11-policy-ingestion-review`, worktree
`C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p11-policy-ingestion-review`.
Implementation through `4ff5872`; the following documentation commit contains this
report and compact checkpoints. Its identity is obtained with `git log -1` after
delivery; do not introduce a self-referential commit hash. Tracked tree is intended
clean after that commit. Local commits only; this extension was not pushed.

The requested software paths, offline evaluation harness and operator guide are
delivered. **The full verification gate is not green:** two existing native
conversion tests fail because the installed Python dependencies are incompatible.
Live AI smoke tests and real human A/B measurements have not run. Phase 11 remains
active; this report is not a final phase handoff or permission to advance.

Owner-facing delivery correction: the running reviewer still serves an older
frontend build and the original72-record packet with zero assisted fields. The
new UI was only built/rehearsed in isolation. See the
[plan checklist and runtime audit](2026-10-27-ai-ingestion-plan-checklist.md).
Code delivery is not a completed visible integration or a passing full exit gate.

## Architecture and reuse

| Path | Final flow |
| --- | --- |
| Native | Existing extraction → pending packet → explicit human review → existing build/verify |
| Native + vision | Existing extraction → original PDF images → source-bound proposed_value before packet hashing → same pending review/save/build/verify |
| LlamaParse | Original PDF + selected physical pages → source-bound resumable REST batches → local pending review-template projection → same review/save/build/verify |

Unchanged reusable components: native document/prospectus extraction, source-span
and chunk contracts, template proposal semantics, PageRenderer, ReviewSession and
append-only journal, reviewer API, review export, source-gap/omission feedback,
reviewed-policy builders, package verification and embedding reuse/encoding.
No student API, routing, generation, runtime, storage contract, dependency manifest
or lockfile was modified. The provider adapter uses existing httpx. No second
review journal, database, renderer or build format was added.

## Changed-file inventory

Paths below are relative to the repository. New ingestion modules live under
`backend/bintanong_tools/knowledge_update/`:

| Files | Reason |
| --- | --- |
| `advisory.py` | Strict advisory outcomes, source/candidate/item/field/page binding and selective assistance; errors retain manual review |
| `vision.py` | Explicit image-capable chat endpoint/model, original images, sanitized transport errors and environment-only credentials |
| `llamaparse.py` | REST v2 upload/poll, physical-page batches, receipts, partial recovery and explicit retry |
| `llama_items.py` | Hash-bound alternate input projected into existing pending fields, preserved hierarchy/raw table relationships and geometry holds |
| `evaluation.py` | Matched samples, blank measurement sheets, relational comparison and JSON/CSV/Markdown summaries |
| `prepare.py`, `manifest.py`, `__main__.py` | Opt-in preparation, alternate artifact verification, CLI commands, immutable assistance recipe and incomplete-parse exit status |
| `researcher/components/advisory-suggestion.tsx` | Original/advice distinction, Use/Ignore/manual-review notices |
| `researcher/app/page.tsx`, `researcher/lib/review-state.ts` | Draft prefill and stale-advice checks using existing save controls |
| `researcher/tests/review-state.test.mjs`, `researcher/tests/document-switch.test.mjs` | Staleness and isolated explicit-save browser regression |
| `tests/test_ingestion_assistance.py` | Human authority, binding, modes, provider failure/privilege/transport and human-corrected build/verify |
| `tests/test_llamaparse_ingestion.py` | REST shape, partial jobs, safe errors, geometry, hierarchy, pending build refusal and human correction/build/verify |
| `tests/test_ingestion_evaluation.py` | Relationally wrong table with complete words, blank-vs-missing, matched pages and unmeasured metrics |
| `docs/development/ai-assisted-ingestion.md` | Native/vision/Llama operations, data transfer, recovery, evaluation and limitations |
| `plans/2026-10-27-ai-assisted-ingestion-codex-plan.md`, `plans/2026-10-27-ai-assisted-ingestion-launch-prompt.md` | Preserved supplied plans; original hashes in integration note |
| `plans/2026-10-27-ai-ingestion-integration.md`, this report | Research, decisions, RED/GREEN history and verification evidence |
| `plans/INDEX.md`, `plans/phase-11-checkpoint.md`, `plans/plan_current_progress/current_progress.md`, `plans/2026-10-26-policy-ingestion-checkpoint.md` | Current pointers, resumable status and remaining gates |

No real source, candidate packet, review journal, model, token or raw provider result
was staged. The supplied plan's three original Markdown hard-break spaces were
preserved; new changes pass whitespace checking.

## Human-authority proof

AI only supplies `proposal`, `no_change`, `uncertain` or `failed`, with optional
bounded confidence/rationale. Approval and review fields in provider output are
rejected. Assistance never receives a ReviewSession and never writes its journal.
`original_value` and `reviewed_value` stay unchanged, with `decision=pending`.

The suggestion is bound to the original PDF SHA, candidate digest, item, field,
physical pages and original value. Preparation hashes the final packet after adding
advice; loading revalidates it. A changed assistance recipe requires a new packet.
The browser disables mismatched advice; the server validates the complete digest.
Using advice only fills a local draft. The human must record audience, a reason
and an explicit save through the existing revision/operation-bound journal.

Fake-provider regressions prove that pending data cannot build; explicit human
corrections from both native and Llama paths can build/verify. The real isolated
browser check confirms no revision change on Use, followed by one corrected
journal event on Save. Confidence never selects an approval. A hallucinated value
can still be a plausible proposal: these checks establish human control, not model
truthfulness. Original-page comparison and separate symbolic authoring remain necessary.

## Verification

Evidence root `A` below is
`C:/Coding-projects/bintanong_workspace/audit-evidence/p11-ai-ingestion-20261027`.
Python 3.13.7; Node 22.22.3 versus target 24.21.0. Existing package versions were
not changed. HF/Transformers offline mode and removal of hosted database variables
were applied to broad/final Python runs. No live model or hosted connection was used.

| Check | Exit | Pass | Fail | Skip/other |
| --- | ---: | ---: | ---: | --- |
| Ingestion + all prospectus/reviewer compatibility selection (before metric-only addition) | 0 | 1821 + 13 subtests | 0 | 0 skipped; 2 deprecation warnings; 189.53s |
| Available repository suite before final envelope hardening | 1 | 6949 + 745 subtests | 2 | 1 skipped, 2 expected xfails; 17 DB files excluded; 401.05s |
| Focused parser/advisory/evaluation/CLI (before metric-only addition) | 0 | 48 | 0 | 0; 13.77s |
| Final evaluator regression including mismatch totals | 0 | 7 | 0 | 0; 0.34s |
| Documentation hygiene/contract checks | 0 | 22 | 0 | 0; 4.50s |
| `npm test` in researcher | 0 | 7 | 0 | 1 browser test skipped without launch configuration |
| Configured isolated browser save replay | 0 | 1 | 0 | 0; 1.90s |
| TypeScript `--noEmit` | 0 | type check | 0 | no test count |
| Isolated researcher production build/start | 0 | build and browser loading | 0 | Node target mismatch disclosed |
| Matched sample + blank summary | 0 | 28 pages / 84 rows | 0 | accuracy/time/cost not measured |
| CLI help, whitespace and phase-state validation | 0 | commands/schema | 0 | Phase 11 cannot advance |

The broader suite's failures are
`tests/test_ingest_hardening.py::test_real_cli_stdout_parses_as_json` and
`tests/test_tools_contract.py::ToolsContractTests::test_synthetic_pdf_fixture_exists_and_parses`.
Both fail in unchanged native Docling conversion: installed Transformers 5.10.2
requires `huggingface-hub>=1.5.0,<2.0`, but 2.2.0 is installed. Docling is 2.129.0;
installed PyTorch is CPU-only. No dependency workaround, installation or unrelated
converter rewrite was attempted. Fresh native conversion remains blocked locally.
Mocked preparation and the passing compatibility suite do not prove it healthy.

DockerDesktopLinuxEngine is unavailable. The 17 excluded files require actual local
Postgres roles/database behavior; they were not silently counted as passing or
replaced with hosted access. Exact exclusions and argv are in
`A/repository-command.json`; complete output/exit are `repository.log` and
`repository-exit.txt`. Final focused argv/log/exit have the `final-focused` prefix.

Reproducible commands (each temp/output directory must be fresh; environment-only
credentials never appear in command text):

```powershell
# Final focused tests: exit0,48pass
py -3.13 -m pytest -q -p no:cacheprovider tests/test_llamaparse_ingestion.py tests/test_ingestion_assistance.py tests/test_ingestion_evaluation.py tests/test_knowledge_update_cli.py --basetemp "$A/envelope-green-confirmed"

# Compatibility selection before the final metric column: exact argv in final-focused-command.json.
$files = Get-ChildItem tests/test_*.py | Where-Object { $_.Name -match '^test_(knowledge_update_|ingestion_assistance|ingestion_evaluation|llamaparse_ingestion|prospectus_|review_gui_)' } | Sort-Object Name | ForEach-Object { $_.FullName }
py -3.13 -X utf8 -B -m pytest -q -p no:cacheprovider @files --basetemp "$A/final-focused-tmp"

# Broad run: tests/ with these explicit database-file exclusions.
$dbFiles = 'test_retrieval_database.py','test_retrieval_source_aware_database.py','test_storage_concurrency.py','test_storage_curriculum_ledgers_database.py','test_storage_loader_idempotency.py','test_storage_release_isolation.py','test_storage_research_release_database.py','test_storage_security.py','test_storage_selected_review_database.py','test_storage_source_acquisition.py','test_storage_source_acquisition_verification.py','test_storage_source_partial_review.py','test_storage_source_registration.py','test_storage_source_verification_database.py','test_storage_supplementary_review.py','test_storage_supplementary_review_database.py','test_storage_vector_retrieval.py'
$excluded = $dbFiles | ForEach-Object { '--ignore=tests/' + $_ }
py -3.13 -X utf8 -B -m pytest -q -p no:cacheprovider tests @excluded --basetemp "$A/repository-tmp"

# Final metric-only regression: exit0,7pass
py -3.13 -m pytest -q -p no:cacheprovider tests/test_ingestion_evaluation.py --basetemp "$A/metric-green"
py -3.13 -m pytest -q -p no:cacheprovider tests/test_docs_hygiene.py tests/test_contracts_fix3_docs.py --basetemp "$A/final-docs-tmp"

# Browser: isolated synthetic reviewer only; current launch link required.
$env:BINTANONG_REVIEW_TEST_LAUNCH = "$A/browser/launch-url.txt"
$env:BINTANONG_REVIEW_TEST_WRITE = 'isolated-rehearsal'
node --experimental-strip-types --test researcher/tests/document-switch.test.mjs
# Browser rehearsal was stopped after verification; its old link is no longer live.
Remove-Item Env:BINTANONG_REVIEW_TEST_LAUNCH,Env:BINTANONG_REVIEW_TEST_WRITE
Set-Location researcher
npm test
node node_modules/typescript/bin/tsc --noEmit
# Production build used the existing _frontend/serve launcher with sanitized environment:
node node_modules/next/dist/bin/next build --webpack
Set-Location ..
py -3.13 -m backend.bintanong_tools.knowledge_update evaluation-sample "$A/sample-input/sample.json" --out "$A/matched-sample"
py -3.13 -m backend.bintanong_tools.knowledge_update evaluate "$A/matched-sample/measurements.csv" --out "$A/matched-summary"
py -3.13 -m backend.bintanong_tools.knowledge_update --help
git diff --check
py -3.13 .agents/skills/bintanong-phase-handoff/scripts/phase_state.py validate --repo .
```

The original production build targeted the isolated copied researcher app and its
explicit API origin via `_frontend`, not a new owner-app build. Browser screenshots
and launch helper are ignored under `A/browser/`. Only synthetic packets were saved;
the test now also requires an explicit synthetic write flag. Owned ports 3003/8767
closed; existing owner services on 3001/3002 were not restarted.

RED/GREEN history and initial setup failures are retained in the integration note:
missing advisory/provider/CLI hooks, stale binding, partial pages, literal blank vs
missing, incomplete CLI exit, malformed response objects. Latest malformed-envelope
RED was 3fail/1pass; fixture refinements corrected mistaken audience expectations,
without weakening the existing unresolved audience contract. Normal provider tests
use deterministic fakes or httpx MockTransport, not live credentials.

## Live integrations and evaluation

- Vision smoke: **NOT RUN** — no configured working image endpoint. Shared MODELS
  has the 5,126,306,944-byte Gemma 4 E4B GGUF, no matching mmproj; loopback metadata
  probes timed out. Google's [model card](https://ai.google.dev/gemma/docs/core/model_card_4)
  confirms image capability, which does not establish this runtime's readiness.
- LlamaParse smoke: **NOT RUN** — no `LLAMA_CLOUD_API_KEY` in this session.
- Database role/lifecycle tests: **NOT RUN** — local Docker engine unavailable.
- Real human A/B: **NOT MEASURED** — sample and harness exist; no invented timings,
  correctness scores, costs, improvement or winning strategy.

Matched sample: Handbook physical pages
3,26,30,43,44,45,46,49,52,53,54,60,61,63,64,69 and Charter
11,12,13,14,15,46,47,48,103,104,105,106. Original hashes:
Handbook `4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8`;
Charter `42a93994e1467df0f32c7038d1c21f638c23ac0f1dee984463acf56caf526529`.
Rationales and complete originals remain local. Mixed/excluded clauses on whole
pages are evidence context, not scope approval. The 84-row sheet has three matched
strategies and blank metrics; summaries preserve nulls. Human adjudication, correction
counts and reviewer timing are necessary to decide whether either strategy helps.

## Limits and remaining work

The geometry adapter only accepts one valid supplied box with matching original
page dimensions and zero rotation. Otherwise it stays manual/build-withheld.
Complex tables are preserved as grouped typed JSON/HTML, not automatically authored
canonical service fields. TOC/body and repeated-header problems remain flagged for
manual association review, not silently fixed. Cross-page raw continuation metadata
is preserved; completeness and fee/time/office associations still require review.

Vision is nondeterministic advisory inference, uses full original pages and only
recorded field-page context. It cannot establish institutional truth. LlamaParse
depends on external API availability and sends the complete PDF for each uploaded
batch. A lost upload response can leave an unknown remote job and repeat-cost risk;
poll receipts reduce but do not eliminate that window. Provider `latest` can drift.
No currency conversion or automatic accuracy classification is performed.
The final metric-only correction preserves recorded extraction-mismatch totals; its
RED/GREEN proof is separate from the earlier compatibility run. The existing 84 blank
rows remain unmeasured; the updated null summary is in `A/matched-summary-final/`.

Remaining AI-extension validation: repair the pre-existing native dependency conflict
in an approved environment, rerun the two failures, configure a supported vision
server/key if wanted, run narrow live smoke tests, then conduct the matched human
evaluation. Broad DB-inclusive regression remains unverified until local Docker works.
No further product architecture is required merely to collect those observations.

Original T4 remains disposable-local lifecycle/stage/publish/rollback tooling and
its role/recovery proof. Original T5 remains full operator delivery/rehearsal through
that lifecycle. This extension's guide does not complete either task. Unrelated
student routing, frontend integration, hosted release, source-content holds and
institutional approval stay with their existing owners/gates. No trusted Prolog is
generated from AI; reviewed symbolic authoring remains a separate boundary.

## Local commits

1. `1711066` docs: pin integration points and supplied plans.
2. `c338146` feat: source-bound native vision assistance.
3. `16ed7d6` feat: advisory UI with explicit save.
4. `45924ce` feat: resumable LlamaParse candidates and evaluation metrics.
5. `4ba7fb4` fix: nonzero incomplete-parse status.
6. `d3f4114` fix: safe malformed-envelope refusal and final source-hardening tests.
7. `4ff5872` fix: retain recorded extraction-mismatch totals; seven evaluator checks pass.
8. Documentation commit containing this report, operator guide and current snapshots.

Read [operator instructions](../docs/development/ai-assisted-ingestion.md) for commands
and [integration decisions](2026-10-27-ai-ingestion-integration.md) for primary-source
API/skill research. No skill, dependency or model was installed.
