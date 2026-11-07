# PR20 candidate verification

Implementation targets `p12-dev` through draft PR20, head branch
`feature/p12-unified-answer-pipeline`, isolated worktree `p12-pr20`.
Base: `21be2614fb082836a89df9ce1b0dfdf568c204c8`.
Implementation: `743004ad`; negotiated legacy compatibility: `1af7882f`;
stream fixture: `be8948a5`; evaluation schema repair: `410db9ce`; dialogue fixture reconciliation: `2869f569`;
explicit hypothetical-premise retention: `b21df7bf`.
[Execution checkpoint](2026-11-07-pr20-execution-checkpoint.md) records import provenance.

## Evidence contract

All tests below use synthetic fixtures or explicitly labelled fictional research inputs.
No live model, embedding encoder or original policy PDF was exercised. The initial full
run could not reach Docker; the owner-authorized follow-up below uses disposable databases.
Release IDs vary by fixture; no production release was activated. Model digest: N/A,
no inference. Python3.13.5 and Node24.21.0 reuse existing external environments.
`compound_checks=False` remains the application default; focused tests opt in explicitly.
Compiler OFF/ON synthetic fixtures run without changing the default environment policy.

| Gate | Executed candidate | Result |
| --- | --- | --- |
| Unified focused backend | Before `743004ad` | 272 passed; overlapping development gate |
| Compound/proof/type boundary | Before `978e464d` | 32 passed, including imported executor |
| Negotiated metadata/chat/stream | Before `1af7882f` | 61 passed |
| Full default Python roster | `2869f569` | 6,712 passed; 2 xfailed; 134 failed +27 setup errors, all161 blocked by unavailable Docker; each shard exit1 |
| Exact161 Docker-blocked cases, owner-authorized rerun | `78514ae3` | 161 passed; 696 subtests passed; allfour shards exit0 |
| Final hypothetical-premise correction | `b21df7bf` | 81 passed, including new RED→GREEN regression |
| Frontend UI and real Python SSE fixtures | `be8948a5` | 105 passed, zero skipped |
| TypeScript | `be8948a5` | Passed, `tsc --noEmit` |
| Production Webpack build | `be8948a5` | Passed, Next16.4.3 |
| Default Turbopack build | Earlier candidate, same dependency layout | Failed: external node_modules junction resolution |
| Actual 390px/desktop browser | N/A | NOT RUN: browser inventory empty |
| Original PDF-backed human gold/live language accuracy | N/A | NOT RUN: isolated model/source window not opened |
| Warm pipeline/browser latency comparison | N/A | NOT RUN; test runtime is not student latency |

Full-default roster contains 6,875 selected node IDs at `2869f569`, excluding the repository's 1,796
default ingestion deselections. Collection-order modulo4 partitions have sizes
1,719/1,719/1,719/1,718; union is exact and disjoint. Ordered roster SHA256:
`04f5d8f024eee7b14340d800af41c48e0dc40dc49bb3cc097d9cb5e2fde59d2b`.
Each shard completed its manifest. Results: 1=1,675 passed/35 failed/8 errors/1 xfailed;
2=1,678 passed/32 failed/8 errors/1 xfailed; 3=1,680 passed/33 failed/6 errors;
4=1,679 passed/34 failed/5 errors. There were899 passing subtests (reported separately).
All161 failure/error trace blocks contain the same StorageDatabase constructor assertion
and missing `dockerDesktopLinuxEngine` pipe, before disposable database creation.
No application assertion or unclassified failures remain in the completed logs.
The initial full run was not green. Its Docker blocker is resolved by the follow-up below;
preserve the original result instead of relabelling that historical invocation as successful.
The external runner performs normal collection, checks every manifest member exists,
retains exactly each shard's ordered manifest and writes per-test completion/failure state.
The later `b21df7bf` adds one regression, verified in the 81-test focused gate; it is not
silently counted in the earlier roster. No unrelated product files changed afterward. The final81-test gate includes actual symbolic
research/proof checks and the original dispatch/response regressions.
This is the full default roster, not all optional ingestion/GPU/integration extras.

Exact completed logs: `final-shards/final-1.log` through `final-4.log`; independent
per-failure classification: `final-shards/db-failure-classification.json`.
Private execution logs/manifests remain under ignored workspace path
`audit-evidence/pr20-20261107/`. Docker-dependent database fixtures cannot connect to the unavailable Linux-engine pipe.
They are infrastructure-blocked, not passed. No services were started to work around it.
Read-only follow-up: Docker Desktop/backend processes absent, Docker helper stopped,
`docker-desktop` WSL stopped. Last backend activity6November18:38Manila; no conclusive
shutdown/crash cause in the consulted tail. Missing engine is confirmed, cause of exit unknown.
Initial pre-freeze monolithic and interrupted shard runs
remain failed/incomplete evidence; their partial successes are not added to final totals. The external runner needed a Windows
multiprocessing main guard and progress writes immune to test-patched file APIs; these
were runner fixes, with the parser-isolation suite passing five tests directly.
Initial REDs also exposed stale controls/wording/uncalibrated fixtures, reconciled without
weakening production guards. The final schema repair adds the already supported
`system_information` control to evaluation JSON; 150 related checks passed separately.

## Acceptance coverage and limits

| Plan case | Automated evidence | Boundary |
| --- | --- | --- |
| A01 policy domain | routing_domains, routing_compiled_policy | No policy Prolog |
| A02 catalog facts | generation_course_facts, prerequisite listing | Structured lookup stays distinct from eligibility |
| A03 took/passed | routing_claim_evidence, routing_dialogue | Unknown completion preserved |
| A04–A05 curriculum editions | routing_validation, symbolic/research fixture scope tests | Actual BSCS original-backed gold NOT RUN |
| A06 blank prerequisites | Existing reviewed-none/symbolic fixture gates | No extension to blank fees or held fields |
| A07–A09 two checks/mixed | pr20_compound_pipeline, compound_symbolic | Default OFF; separate proofs, unknown and document failures retained |
| A10 independent document gaps | orchestration_multi_topic, generation_part_slots | Successful topic cannot cover missing topic |
| A11–A12 conflict/version | orchestration integration, compound release/citation tamper tests | Shared conflict/untrusted release held |
| A13 unmatched topic | document_check_not_run ledger/render tests | Not checked differs from corpus absence |
| A14 negation/language | Eighteen deterministic dialogue/compiler combinations | Real-model semantic accuracy NOT RUN |
| A15–A16 dialogue/stale reply | routing_dialogue, api_chat_turns, dialogue_context | Exact owned origin/revision/scope/slots |
| A17 unsupported compound | Bounded planner rejection/default clarification tests | No truncation to first operation |
| A18 procedures/source gaps | service_record_coverage, part slots, presentation | Required sequence and caveats preserved; original-backed acceptance NOT RUN |
| A19 legacy SSE | Actual baseline strict validator fixture and Python streams | Metadata opt-in version2; unnegotiated bytes stay compatible |
| A20 UI | SSR escaping, list markup, focus/wrapping tests | Actual viewport/accessibility interaction NOT RUN |
| A21 compiler comparison | Synthetic OFF/ON gold | Default unchanged; measured live comparison NOT RUN |
| A22 excluded audience | Routing scope/security regressions | Undergraduate advisory scope unchanged |

## Reproduction and promotion

From the repository root, use existing Python3.13 with
`-m pytest tests -q --tb=short -p no:cacheprovider --basetemp=<ignored-external-path>`.
The four-shard run uses the exact same default selection with the manifest checks above.
Frontend: existing Node24.21, `node --experimental-strip-types --test tests/*.test.mjs`,
`node node_modules/typescript/bin/tsc --noEmit`, and
`node node_modules/next/dist/bin/next build --webpack` in `frontend/`.
Set `BINTANONG_TEST_PYTHON` to that Python executable for cross-language SSE tests.
No dependency installation or lockfile change was performed.

Keep PR20 draft. Human original-backed/model/viewport/latency acceptance remains outstanding;
do not close PR18/19 as fully superseded or merge/promote the candidate before those gates.
The implementation did not reload the serving app or change the thesis evaluation checkout.
Docker startup for the later owner-authorized follow-up is recorded below.

## Owner-authorized Docker follow-up, 7 November

Owner asked to start Docker and run automated checks. Started the installed Docker Desktop;
Engine29.8.2 became ready and existing `supabase_db_Bintanong` became healthy
(image `public.ecr.aws/supabase/postgres:17.6.1.167`). No installs, resets or application
configuration changes. Model containers were not started. The owner authorization supersedes
the earlier service-start hold for this bounded check only.

Exactly the161 failed/error node IDs from the independently classified full run were rerun,
disjointly partitioned41/40/40/40 at `78514ae3`. Results:41/40/40/40 passed, all exit0;
subtests232/66/209/189 passed. SQL fixtures create uniquely named disposable databases and
drop their own databases afterward; the application database is not reset. The three pre-existing
test database names observed before this run remain; this task does not delete unrelated leftovers.
Evidence: ignored `audit-evidence/pr20-20261107/docker-rerun/{run.py,result.json,roster-*.json,shard-*.log,sql-*}`.

Reconciled original6,875-case roster across the initial run and targeted rerun:
6,873 passed and2 expected failures. This is cumulative evidence across two runs, not a
fresh monolithic all-green run. The final hypothetical-premise regression remains separately
verified in the81-test gate. No application code changed during the Docker follow-up.
Source/model/viewport/latency acceptance and promotion remain outstanding.
