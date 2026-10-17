# Source-aware engine database verification — 16 October 2026

Baseline `01c70b7`; production code remains `8595fb8`. The earlier conclusion
that no independent verification work remained was too broad: source-aware
engine tests used storage doubles, while actual PostgreSQL engine tests used
the legacy path. This increment checks their composition with synthetic data.
It does not resolve the real-source authorization prerequisites.

## Purpose and bounded change

Student capability: retrieve source-linked reviewed policy context and withhold
claims that the selected evidence does not establish. Evidence path:
SourceAwareEvidencePolicy → RetrievalEngine → actual runtime-role SELECT/RPC →
whole-context assembly → rendered-field/source-locator assessment. This advances
master section 10 and Task 6's integration verification. The specific question
is whether actual database transport and role restrictions preserve the
source-aware engine's tested bindings and conservative findings.

[New tests](../tests/test_retrieval_source_aware_database.py) declare synthetic
source snapshots independently of the RPC serialization. They use the existing
disposable PostgreSQL harness and synthetic storage fixture. A main clause has
one required exception; the exception's vector is below the .25 ranking cutoff,
so recovery must come through the required-neighbor path. Both clauses belong
to the same synthetic source/version and undergraduate test scope.

[Test adapter](../tests/storage_database.py) now accepts an explicit
`runtime_role`, restricted to `anon` or `authenticated`. The default remains
`anon`; explicit administrative fixture operations remain `service_role`.
Tests verify default/explicit role SQL construction and reject privileged or
injected role names. The actual integration uses both roles for SELECT and RPC,
without a privileged shortcut for engine reads.

No production module, SQL migration, dependency, model or real-source package
changes. Synthetic release activation occurs only inside uniquely named
disposable databases. Shared local/hosted releases and pending real-source
governance states remain untouched. This is neither institutional activation
nor an additional accepted-question/parameter experiment.

## Coverage

| Check | Required behavior |
| --- | --- |
| Both runtime roles | Execute SELECT/RPC under the selected unprivileged role |
| Reviewed visible fields | Actual transport matches the declared snapshot; main and required exception render together with original synthetic citations |
| Missing claim | Related context remains visible but the unsupported claim stays insufficient |
| Scope and context budget | Wrong-program filtering or a one-unit fixture budget emits no partial group |
| Snapshot mismatch | A changed declared source page rejects actual transport before evidence emission |
| Release change | An old pin stops before encoding after another synthetic release is published |
| Configuration mismatch | A mismatching embedding fingerprint stops before encoding |
| Conservative metadata | Every result remains candidate-only, activation-ineligible and answer-sufficiency unassessed; runtime authorization flag remains false |

The encoder returns explicitly synthetic unit vectors. The context counter is
the fixture's character count, not a measured model tokenizer. Model quality,
new multilingual benchmark results and actual-source authority are not tested.
HTTP/PostgREST transport is outside this adapter and retains separate existing
coverage. These limits prevent the synthetic positive path from being counted
as the remaining authorized real-source runtime validation.

## Verification

Python 3.13 readiness venv, `-B`, pytest `-p no:cacheprovider`, ignored external
basetemp and `BINTANONG_STORAGE_EVIDENCE_DIR` under workspace/audit-evidence/
p05-source-aware-database-20261016. SQL, outputs and synthetic engine JSON are
retained there; no generated artifact is staged.

The role-helper regression first observed seven expected failing subcases:
the adapter did not accept an explicit runtime role. Adding the restricted
test-only option yielded two passing tests / seven subtests. Initial integrated
coverage then passed seven tests / 19 subtests in 7.73s. A default/admin
compatibility case and actual configuration-mismatch guard were subsequently
added; final relevant regression results are recorded below when available.
There was no production defect or production implementation change.

One independent read-only reviewer found no Critical, Important or Minor issues.
The reviewer checked actual role flow, below-cutoff neighbor recovery, rendered
fields/citations and test isolation. Declined judgments: HTTP transport,
real-model quality/institutional authorization, and the then-running final test
result. Existing boundaries apply to the first two; the parent must read the
final verification result. No second review or deferred minor findings.

## Remaining phase gate

The [bounded document acceptance contract](2026-10-16-document-development-acceptance-contract.md)
and its 39 unchanged observations retain their exact disposition and three T1
context misses. This increment supplies a missing synthetic integration check,
not another calibration policy or formal exit pass. Tasks 4/6 remain open on
applicable real-source/release decisions and actual authorized runtime validation.
Do not repeat settled source reviews, embeddings or the pending school-response
question. No Phase 06 advancement follows.

Resume context: thesis physical 17–18, actual runtime routing PNG, master 10,
active plan/checkpoint/handoffs. Undergraduate advisory scope, private-file
separation and structured/Symbolic curriculum routing remain unchanged.
Supabase/Postgres skills and current Context7 RLS/function documentation were
consulted; the changelog showed no relevant local role-testing change.
References: [RLS testing](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/row-level-security.mdx)
and [invoker functions](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/functions.mdx).

Final relevant regression command:

```powershell
python -B -m pytest -q -p no:cacheprovider tests/test_retrieval_source_aware_database.py tests/test_retrieval_database.py tests/test_retrieval_evidence_policy.py tests/test_retrieval_engine.py tests/test_retrieval_context.py tests/test_storage_source_registration.py tests/test_storage_security.py tests/test_storage_loader_idempotency.py --basetemp "$checkRoot/regressions-temp"
```

Here `$checkRoot` is the ignored raw root above; the command uses the existing
Python 3.13 readiness venv and sets BINTANONG_STORAGE_EVIDENCE_DIR to that root.
Result: **99 tests / 148 subtests pass in 108.63s, exit 0**. This includes the
final eight new tests and the relevant existing retrieval/storage regressions.
No full product-suite repeat is needed after this test-only change.

Fresh catalog inspection confirms all 29 databases created by these runs are
absent after harness cleanup; it neither drops nor inspects another worker's
database content. Four retained synthetic role outputs (two runs × two roles)
pass independent status/flag/group-count checks and have recorded SHA-256 hashes
in cleanup-and-output-verification.json. Raw SQL records include both runtime
roles. Owner artifact bytes and the unchanged product/schema/evaluation trees
were also verified. Final documentation/ledger checks are recorded at closure.

Closure checks: documentation/phase ledger 522 tests / 11 subtests pass in
11.79s, exit 0; phase validate exits 0, can-advance exits 1 (expected blocked).
Whitespace checks pass. This commit contains test coverage, the restricted test
adapter option and recovery documentation only. Product/schema/evaluation trees
remain unchanged; owner artifact changes remain unstaged. The synthetic composed
path is verified; the real-source release gate remains unresolved.

## HTTP transport failure follow-up — 16 October 2026

Product fix `b0d6c6d`, baseline `4872b29`. A subsequent bounded check of the
previously separate HTTP client reproduced a raw ReadTimeout escaping its
StorageError boundary. RetrievalEngine catches StorageError, so this could
crash a request rather than return the documented storage_error envelope.
HTTP status failures already had the correct error classification.

Focused regressions first observed 27 failing transport subcases. The storage
client now routes its existing five HTTP methods through one request wrapper
that translates only HTTPX RequestError into generic StorageError, retaining
the diagnostic cause. Public error text excludes raw transport details/URLs.
There are no retries, administrative fallbacks, engine schema changes or new
retrieval permissions. Existing request shapes, successful response handling
and permission-error classification remain intact. Non-request programming
errors still propagate from the client.

Composed synthetic tests exercise both legacy and source-aware engines at the
release read, embedding-set read and retrieval RPC. Connection/timeouts return
storage_error with no evidence or context, stop subsequent requests and retain
runtime credentials. Source-aware conservative flags remain unchanged. Client
regressions also cover protocol failures and mutation paths without retries.
The focused client/engine/policy/CLI suite passes 38 tests / 61 subtests in 5.33s.

One independent reviewer found no Critical, Important or Minor issues and
separately passed all six client/composed test methods. Live HTTP/server
behavior, database/institutional authorization and the parent's full-suite
result were explicitly outside that review. Those boundaries remain; no second
review or deferred minor finding. No live request, source mutation, model or
shared schema/database change is involved in this correction.

Raw logs are ignored under workspace/audit-evidence/
p05-storage-transport-errors-20261016: initial-reproduction.log, red.log,
green.log, review.txt and full-suite.log. Exact Python3.13 readiness venv,
-B/-p no:cacheprovider and external basetemp are used. Current Context7
[HTTPX exception documentation](https://github.com/encode/httpx/blob/master/docs/exceptions.md)
confirms the request-error hierarchy. Thesis17–18/routing/master10 were
reconsulted; the standing undergraduate advisory/source-release limits persist.
The full suite is still pending at this entry; its final result follows below.

Final follow-up verification: **5421 tests / 763 subtests pass in 366.39s**,
with six skips / six dependency warnings, exit 0. Command: Python3.13 readiness
venv `python -B -m pytest -q -p no:cacheprovider tests`, external basetemp
workspace/audit-evidence/p05-http-full-temp, storage evidence variable bound to
the follow-up raw root. Product/test/schema bytes match b0d6c6d; no subsequent
code changes. Fresh catalog check confirms all 35 disposable databases created
by this full run are absent. Owner artifact bytes remain preserved/unstaged.

closure-verification.json records exact SHA-256 hashes for the reproduction,
RED/GREEN, review and full-suite logs; full-suite.log hash is
`d4541056f1282dcfef7fa993ccd3703c7ba6800bd352f86e797149b67a5341d4`.
No new source review, real model encoding or shared migration/activation. Formal
Tasks 4/6 retain their source/release and final runtime prerequisites. Final
continuity checks follow; no repeat product suite after documentary edits.

Final follow-up closure: 522 documentation/ledger tests and 11 subtests pass in
11.82s, exit 0. Phase validate exits 0; can-advance exits 1 (expected blocked).
Whitespace checks pass. No code changes followed the full 5421-test result;
only these continuity updates are staged. Raw follow-up logs remain ignored;
owner artifacts remain preserved and unstaged.
