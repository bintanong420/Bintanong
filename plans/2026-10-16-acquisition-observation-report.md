# Acquisition observation delivery — 16 October 2026

The owner-approved [A1 design](2026-10-16-acquisition-observation-design.md) is
implemented in `391ef8a` (loader) and `7c40308` (atomic persistence). Five existing
source-bound byte checks now persist acquisition pending→observed in a disposable
rehearsal. The candidate remains inactive; shared databases remain unchanged.
This closes the reproduced A1 persistence gap, not formal Phase 05 completion.

## Behavior and boundaries

`SourceAcquisitionLoader.observe(current, check)` validates the complete source
contract, exact four-key byte-check envelope and existing Evidence/A1 rules.
It derives one appended Evidence and the acquisition-state change, then validates
the exact register returned by administrative `observe_source_acquisition`.
Inputs, source identity, history and all other lifecycle states are preserved.
Storage errors propagate without automatic retry or role escalation.

Migration `20261016093918_phase5_acquisition_observation.sql` was generated using
the existing local Supabase CLI2.117.0. It adds one SECURITY INVOKER function,
explicitly denies PUBLIC/anon/authenticated execution and grants service_role.
It independently checks the closed envelope, evidence types/authorization/time,
source binding and initial lifecycle boundary, derives the proposed register,
and serializes under the existing publication lock plus source-row lock.

The full stored register and its complete relational projection must match the
expected initial record or exact derived observation, excluding only created_at.
First application updates only acquisition_state/source_register. Exact replay
returns without UPDATE and still checks relational consistency. Stale/different
observations, missing/legacy registers and any published membership fail. Initial
registration deliberately remains a conflict after observation; replay the
observation with the same original expected record/check instead.

Python remains the complete contract validator. The SQL guard protects this
bounded mutation; it cannot authenticate an evidence recorder, read original
filesystem bytes or establish institutional authority. Trusted administrative
preparation binds the actual saved check. No A2, verification, content-review or
approval transition, vocabulary change, source backfill or activation is added.

## Verification

Readiness Python3.13 environment:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe`.
Commands use `-B -m pytest -q -p no:cacheprovider`, external basetemp and
`BINTANONG_STORAGE_EVIDENCE_DIR` bound to the ignored evidence root below.
No installs, dependency/lock edits or model downloads.

- Loader RED: missing implementation, 31 failing cases/subcases. GREEN: 11 tests
  and 46 subtests in1.87s, including existing HTTP client checks.
- SQL RED: one actual-role missing-RPC failure. Initial GREEN: 15 tests and
  70 subtests in34.22s. Direct malformed/null/missing fields, wrong source/kind/
  recorder, wider transitions, duplicate evidence, stale/concurrent observations,
  drift on first/replay, published/legacy guards and actual role denials covered.
- Timestamp parity RED: one valid existing-contract timestamp with +23:59 and
  nanosecond fraction failed PostgreSQL timestamptz displacement limits. The
  correction validates the calendar independently of the checked offset syntax
  and retains the exact timestamp text. No contract restriction was added.
- Relevant GREEN: **58 tests / 178 subtests in123.97s**, exit0. Command selects
  tests/test_storage_source_acquisition.py, test_storage_source_registration.py,
  test_storage_loader_idempotency.py, test_storage_security.py and
  test_retrieval_source_aware_database.py; basetemp `<raw-root>/sql-regressions-temp`.

Final independent review finds no Critical, Important or Minor issues in
78ae763..7c40308. All five review-focus conditions were checked. Reviewer ran
21 acquisition/client tests / 88 subtests in40.31s, exit0, plus195 independent
null/missing/wrong-type service-role RPC cases: every case rejected with the
complete row unchanged; its disposable database was dropped.

The retained full-suite run completed **5458 tests / 844 subtests in403.12s**,
with six skips and six warnings. This continuation read the completed log and
verified backend/tests/supabase have no changes since7c40308; it did not repeat
that unchanged suite. Command: the readiness Python above with
`-B -m pytest -q -p no:cacheprovider tests`, external basetemp and the A1 storage
evidence root. Existing warnings concern Starlette/HTTPX, the GPU marker and
Docling/Pydantic deprecations. No installs or dependency changes follow.

Fresh parent read-only closure verification checks all five observed contracts
against exact initial records/checks, the six original input hashes, both saved
runtime-role denials, zero active pointers and93 retained disposable database
names absent from the live catalog. It also verifies the earlier8/49/164-file
seals unchanged. The reviewer independently tests production behavior; the
saved rehearsal/full-suite results are retained execution evidence.

Full-suite.log SHA-256:
`fbd9ffde88330d526f6c90ec8ef7e9f40a6cfd84af81f66a2d8dad768b6cd6ec`.
Reviewer focused.log SHA-256:
`39260c522545b0fbef4d82299b9771b98a15daad1f1feefdd62192f02d52cc39`.
Reviewer direct-rpc-matrix.log SHA-256:
`c042e6118e243dc25b8ec66c4d569187e0aa82672b378a3028f83c92f5bbbc61`.
Reviewer raw root: workspace/audit-evidence/p05-acquisition-final-review-20261016.
Parent verifier/result and curated evidence seal remain in the A1 raw root.

## Five-source inactive rehearsal

Ignored `rehearse_observation.py` binds six existing inputs by SHA-256: pending
versions, chunks, embedding manifest/records, fresh byte checks and explicit
document metadata. It preserves recording times/roles, locator order and the
existing `fresh-hash-{version_id}` Evidence identity. No original is reconverted
or re-encoded; no benchmark question or selected profile is changed.

Database `bintanong_storage_test_2c6c915912c14162804b51fa22cd3c5b` registers the
five initial sources, applies their five A1 observations, then replays all five.
Complete returned/stored registers agree; verification/content review remain
pending, approval not_requested/null. It reuses 19 chunks and 19 saved vectors
with 54 source spans in draft `p05-observed-source-draft-20261016`.

There are five document/version rows, one draft and zero active pointers.
Source/chunk identities, content, scope, type fields, pending chunk review
bindings and source spans remain unchanged. Both actual runtime roles see zero
rows across corpus/release tables; retrieve_context returns release_changed
with no items. The rehearsal database was dropped. All six inputs remain
byte-identical, including the original sealed pending source registers.
Observed derivatives exist only in this new ignored evidence root and the
now-removed disposable database; no shared migration or source write occurred.

Embedding set unchanged:
`02fce0fc4caca1c15cc4a58f5e511f70d5dc27be77769f7cbb0f7ce423368811`.

## Evidence, decisions and continuation

Raw root: workspace/audit-evidence/p05-acquisition-observation-20261016.
It retains RED/GREEN/regression logs, rehearsal driver/result, projected check
envelopes/observed derivatives and disposable SQL/output. Source-derived files
are ignored. Six input hashes are in rehearsal-result.json. Three earlier seals
verify read-only unchanged: reconciliation8files, readiness49files and source
registration164files. Do not rerun writers in those sealed input roots.

Ruling: execute inline without another plan/method approval because the owner
approved the full bounded design at78ae763; cost if wrong is implementation
rework within this isolated candidate. Ruling: use repository plan/checkpoint
and retained ignored evidence instead of a disposable .superpowers workspace,
following owner continuity/location instructions; cost is manual ledger upkeep.
Ruling: the one final review covers the complete approved increment78ae763 to
7c40308; earlier delivered features have separate reviews. Cost if wrong is a
missed older interaction, mitigated by the full regression suite.

Ruling: retain and verify the completed full-suite result rather than rerunning
unchanged production/tests/SQL after a session change; fresh focused independent
tests and parent evidence/documentation checks supplement it. Cost if wrong is
an unrecorded environment difference; no environment or code change is observed.

The final review declined the following broader claims. Each remains outside
this bounded delivery; these are scope rulings, not unresolved code findings:

- Earlier features beyond necessary contract/projection/transport/lock interactions:
  retain their prior reviews; cost is a missed older interaction, covered partly
  by the completed full suite.
- Institutional source accuracy/applicability/authority/currentness/authenticity
  and held content: preserve actual source gates; cost would be unsupported use
  if this technical result were misrepresented as source approval.
- Truthful original-byte checks or recorder attribution: trusted administration
  retains that responsibility; neither SQL nor a supplied Evidence ID proves it.
  Cost is false provenance if an administrator supplies untrue evidence.
- Arbitrarily corrupted existing registers or malicious administrators bypassing
  the loader: Python remains the full validator and admin trust boundary stands.
  Cost is invalid administrative data beyond this mutation's bounded guard.
- A2 and other lifecycle transitions: not implemented or authorized; cost would
  be a false capability claim if generalized beyond A1.
- Shared/hosted migration/configuration/deployment/activation: untouched; cost is
  unverified deployment behavior until separately authorized and checked.
- Live PostgREST transport: SQL-role and MockTransport coverage do not reproduce
  the live server path; cost is an unobserved transport integration issue.
- Repeating the five-source rehearsal: preserve it and verify saved records/input
  hashes rather than recreate it; cost is not independently reproducing that run.
- Repeating the full suite: preserve its completed log and unchanged code binding;
  cost is not independently reproducing that run, as recorded above.
- Retrieval calibration/model quality/answer sufficiency/executable rules/runtime
  authorization/formal Phase05 completion/Phase06: retain existing gates; cost
  would be unsupported student guidance if this result were overgeneralized.
- Final documentation/ledger closure: parent owns fresh checks and explicit
  staging; cost is a continuity defect if those checks are omitted.

No deferred minor findings. Keep the active branch/worktree for remaining Phase05
work; a bounded acquisition delivery does not authorize phase integration.

Formal Tasks4/6 remain open: existing selected profile k3/.25/2048 and bounded
offline acceptance do not prove authorized real-source runtime availability.
Preserve the existing 18 field-available/21 insufficient document outcomes and
three T1 context misses. Applicable source review/authority, governed release
authorization and final runtime/exit evidence still govern completion. No fresh
grid, new encoding, wording review, school-response question or Phase06 follows.
F04/G01/original G02 and known original cutoffs/conflicts remain held.

Context reconsulted: thesis physical17–18, runtime routing PNG, master10, previous
Phase04 handoff and active phase artifacts; no scope/routing discrepancy. Models
stay in C:/Coding-projects/MODELS. Owner artifacts/.gitkeep deletion and untracked
backend/artifacts remain preserved and unstaged. Keep the active phase worktree
and branch for remaining work; this bounded increment does not close the branch.

Final documentary verification:513 documentation/phase-ledger tests and11subtests
pass in11.73s, exit0. `phase_state.py validate --repo .` exits0;
`phase_state.py can-advance --repo .` exits1 because the Phase05 handoff remains
blocked, as intended. Whitespace check passes. No product/test/SQL change follows
the completed full suite. Final closure commit includes only this report, its
plan and the four phase-continuity files; use Git for its SHA. Keep the verified
product baseline7c40308 in metadata, avoiding a self-referential commit hash.

Curated raw evidence seal:119files; SHA-256
`3c707f884fb644622204d05ebd4bd395e2ee8b480bc86e1ea01e3afc47a9eca7`.
Creation and immediate read-only verification both pass; synthetic test
temporaries are excluded, while rehearsal SQL/output are included.
