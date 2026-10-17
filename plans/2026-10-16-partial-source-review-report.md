# Scoped partial-review delivery — 16 October 2026

The owner-approved [design](2026-10-16-partial-source-review-design.md) is
implemented by loader `43c0c3c`, storage `2653d72` and integrity fix `9e6526c`. It records existing
selected owner confirmations with durable exact coverage, advancing only C1
content review from pending to partially_reviewed. Five real-source receipts
and five exact replays succeeded in a removed disposable database. Shared
databases remain unchanged; candidate results remain inactive.

This closes the scoped C1 persistence gap. It is not complete source review,
institutional source authority, formal Phase05 completion or Phase06 approval.
See the [implementation plan](2026-10-16-partial-source-review-plan.md).

## Resulting behavior

`SourcePartialReviewLoader.record(current, receipt)` accepts the exact closed
selected-source-partial-review-v1 receipt and the complete expected source
register. It validates existing Evidence/source contracts, C1-only lifecycle
states, original labels/timestamps, source-event bindings, field/span references
and complete same-source neighbor coverage. It preserves caller input/history,
invokes the administrative operation once and validates the exact returned
register. Storage failures propagate without retry or credential escalation.

Original confirmation times and actual owner labels remain attached separately
from the compilation label/time. The compiler is not an independent human
source reviewer. Existing provenance paths remain verbatim inside administrative
snapshots; the change introduces no new path fields or original/private bytes.

Migration 20261016103716_phase5_partial_source_review.sql adds the administrative
source_partial_reviews table and the service-role-only SECURITY INVOKER RPC
record_source_partial_review. The table has a restrictive version FK and a
composite primary key covering that FK, explicit least privileges, RLS and a
restrictive runtime denial. Ordinary UPDATE/DELETE/TRUNCATE is rejected.

The RPC independently checks receipt shape, C1 evidence/time/source binding and
the complete source relational/register projection. It compares all selected
chunk type_fields/content identities and ordered storage span snapshots, retaining
fields, conditions, declared blanks, source limits and required neighbors.
The stored content hash is recomputed from current text/source_text under the
same lock; merely retaining an old hash cannot hide content drift.
Existing source/chunk/span statement triggers share the publication lock; no
additional snapshot-write serialization was needed. Source row locking follows
that lock. Published membership and legacy/null registers are rejected.

Receipt insertion and the derived source register update are one transaction.
Exact replay checks the immutable stored receipt, complete source projection
and current selected snapshots before returning without writes. Missing/altered
receipts, different observations, stale state or content drift fail. Concurrent
identical requests replay; competing observations do not overwrite history.

Python remains the complete source-contract validator. SQL guards this bounded
mutation; it does not inspect external evidence files or authenticate supplied
reviewer identities. Trusted administrative preparation supplies truthful
source-event bindings. No source verification, acquisition, scope, approval,
chunk flags, release membership or active pointer is promoted by C1.

## Verification performed

Existing readiness Python3.13 environment:
C:/Coding-projects/bintanong_workspace/audit-evidence/
p05-real-retrieval-readiness-20261012/venv/Scripts/python.exe.
Commands use `-B -m pytest -q -p no:cacheprovider`, external basetemp and
BINTANONG_STORAGE_EVIDENCE_DIR under the ignored raw root below.

Final fixed-code command uses that readiness executable with
`-B -m pytest -q -p no:cacheprovider tests --basetemp C:/Coding-projects/bintanong_workspace/audit-evidence/p05-c1-final-full-temp`.
MODELS_DIR stays C:/Coding-projects/MODELS; DOCLING_ARTIFACTS_PATH and HF_HOME
point to the existing readiness docling-artifacts/hf-cache directories.
HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1 prevent model downloads.

Verified environment: Python3.13.7, PostgreSQL17.6, existing CLI2.117.0,
Pydantic2.13.5, HTTPX0.28.1, pytest9.1.1 and Docling2.133.0. Runtime versions
and exact loader/migration/test SHA-256 values are retained in ignored
environment-and-code.json. No dependency or lock updates were made.

- Unit RED: 81 expected missing-loader cases/subcases.
- Unit GREEN: 11 tests / 96 subtests in2.05s with existing HTTP client tests.
  Loader/acquisition/client regression:17 tests / 124 subtests in2.33s.
- SQL RED: actual service-role call reports the missing new RPC.
- Final focused GREEN:18 tests / 250 subtests in83.53s. Covers direct malformed
  calls, source/event/field/span/limit/dependency omissions, first/replay drift,
  missing/conflicting receipts, immutable data, actual runtime denials even
  after accidental table grants, wide-offset/fraction timestamp parity, late
  source-update rollback and a receipt waiting behind a concurrent span writer.
- Saved-package rehearsal:five receipts/five replays,19 chunks/19 reused vectors/
  54 spans,52 field associations/nine source-bound events, zero active pointers.
  Both actual runtime roles see zero corpus/release rows and cannot read receipts;
  retrieve_context returns release_changed with no items for the inactive draft.
- Parent read-only verifier:five resulting source contracts agree with exact
  original registers plus one C1 Evidence;52 field associations/nine events/
  54 spans/22 neighbor links agree. All eight rehearsal inputs and all21 earlier
  reconciliation inputs remain byte-identical. Prior8/49/119-file seals verify.

Initial implementation/fixture failures were diagnosed from actual logs. A
locator-default duplicate keyword was corrected in Python. A SQL projection's
unqualified key conflicted with its PL/pgSQL variable and was qualified. Later
mixed regression failures came from synthetic test fixtures: an unchanged null
authorization reference counted as malformed, overlapping fixture chunk IDs,
and raw PostgreSQL booleans sent to a JSON reader. Corrected tests pass in the
final focused run. Two initial rehearsal-driver calls used incorrect retrieval
parameter names; the existing migration's p_config interface resolves that
technical issue. All initial logs and disposable SQL evidence remain retained.
None of these corrections changes an institutional source or review decision.

The single independent review identified one Important integrity issue: changing
an unpublished chunk's text/source_text while retaining its old hash was accepted
on first call/replay. Parent independently reproduced all four RED subcases.
Fix9e6526c recomputes the existing SQL content hash under the lock; focused
GREEN:3 tests / 4 subtests in16.97s, including ordinary first/replay and waiting
writer regressions. No receipt schema or source meaning is expanded. No other
material findings or deferred minors. This is the single review fix pass; no
second independent review is needed to retest the same fix.

Post-review corrected-code rehearsal repeats the five receipts/five replays
with the same19chunks/vectors/54spans and52field/nineevent coverage, both runtime
roles hidden and zero active pointers. All eight original inputs remain
unchanged and the database is dropped. Initial successful evidence remains
preserved at the raw root; final corrected results live in its post-review/.

The final fixed-code full suite passes **5462 tests / 1087 subtests in551.87s**,
with six skips and six warnings, exit0. It starts from9e6526c, includes the new
four-case regression and uses the existing offline environment. No code change
follows that run. Warnings are the existing Starlette/HTTPX, GPU-marker and
Docling/Pydantic notices. No installs or warning-driven scope changes follow.

Final full-suite log SHA-256:
`2af7e45ac133fca05827f335b02f16d48122557056decad3ba93562aca8d1718`.
Fresh saved-evidence verification validates the corrected five source records,
all52field/nineevent/54span/22dependency bindings, eight unchanged rehearsal
inputs and21 unchanged historical inputs. Prior8/49/119-file seals remain exact.
All212 own retained disposable database names and four reviewer database names
are absent from the live catalog. Code and reviewer evidence hashes match.
Final-verification.json and post-review/delivery-verification.json retain details.

The initial run completed5460tests/1083subtests in585.79s with six skips/six
warnings. It is retained as historical mixed-timing evidence, not the fixed-code
gate. Documentation/phase-ledger checks independently pass516tests/11subtests
in15.97s. Phase validation exits0; can-advance exits1 as expected while the
Phase05 handoff remains blocked. Whitespace checks pass.

Independent review: workspace/audit-evidence/p05-c1-final-review-20261016/
final-review.md, SHA-256
`c2bfa3f51c6bbf4ec244657a62cd3a60d0f6abe703588601a943205b635ce61e`.
Reviewer separately ran three actual-role tests in13.87s and reproduced the
same four anomalous content-drift cases; its database was dropped. Parent owns
fix verification, real-source rehearsal and final full-suite evidence.

## Existing source package and limits

The five receipts cover the selected handbook, Charter, fee image and two
vehicle image identities. The nine source-bound events refer to eight actual
owner records; these are not nine new confirmations. The52count describes
selected field associations, not full handbook/Charter audit coverage.

Final rehearsal database bintanong_storage_test_349dd520bc32417bab0fde4ee94858c0
was dropped. It held five source versions, five C1 receipts,19 chunks/vectors,
54 spans and one inactive draft. All chunk and span rows remained unchanged.
Source acquisition stays observed, verification pending, approval not_requested
with null ID; only content review/evidence advance. Complete original source
inputs and historical pending/A1 records remain unchanged outside this removed DB.

Earlier successful rehearsal bintanong_storage_test_913267dfe71d4e888cc1f2e5616faab8
and both earlier driver-failure databases were also dropped. The same embedding set remains:
`02fce0fc4caca1c15cc4a58f5e511f70d5dc27be77769f7cbb0f7ce423368811`.
No model encoding, conversion, parameter grid, benchmark wording or source
selection is repeated. The earlier two failed rehearsal DBs were also dropped.

F04/G01/originalG02 remain held. Preserve original Charter cutoffs, conflicting
completion deadlines, current-year/authority gaps and proposed/cohort labels.
School response remains pending; no repeated request or inferred approval.
Keep the selected document profile and its18 field-available/21 insufficient
observations, including the three T1 related-context misses, unchanged.

## Recovery and decisions

Raw root: workspace/audit-evidence/p05-partial-source-review-20261016. It retains
RED/GREEN/mixed regression logs, current rehearsal driver/results, exact scoped
receipts/derived registers, verifier and raw SQL. These files remain ignored.
Do not rerun writers in the earlier sealed roots. Models remain strictly under
C:/Coding-projects/MODELS; approved Docling assets stay in their existing cache.
No install, download of model/dependency assets, lock or dependency change.

Ruling: retain established inline execution without another plan/method approval
because the owner explicitly approved the complete C1 design and said go ahead.
Cost if wrong: bounded implementation rework in this isolated candidate.
Ruling: use repository plan/checkpoint/progress plus ignored audit-evidence
instead of an additional skill workspace, honoring owner storage/continuity
instructions. Cost if wrong: manual ledger upkeep.
Ruling: review the complete approved increment b5ddea9..2653d72 and necessary
older interactions; earlier delivered features retain their own reviews.
Cost if wrong: a missed older interaction, mitigated by the full regression suite.

Final review boundary rulings, all accepted without widening this C1 operation:

- Declared identities and external event-file truth remain trusted administrative
  assertions; SQL cannot verify external history. Cost if wrong: false provenance
  supplied by an administrator, not authenticated review evidence.
- Source wording, complete review, currentness and school authority retain their
  actual source gates. Cost if wrong: unsupported guidance if C1 is misrepresented
  as approval; inactive status and pending verification/approval are preserved.
- Nonprojected chunk attributes such as token counts/source labels are outside
  this selected-field receipt. Cost if wrong: unrelated metadata drift is not
  detected by C1; text/hash coherence was material and is now checked.
- Shared deployment, runtime activation and formal Phase05/06 readiness remain
  outside this feature. Cost if wrong: unverified deployment/authorization claims;
  no shared migration or activation was performed.
- Malicious superuser trigger disabling or fabricated direct admin inserts are
  outside the trusted administration model. Cost if wrong: administrator-created
  false data; ordinary writes and accidental runtime grants are explicitly tested.

No deferred minors. Preserve the current phase branch; completion of this
bounded feature does not authorize phase integration or worktree deletion.

Context consulted: thesis physical17–18, same-session runtime routing PNG,
master6/10, active phase documents and source-gap/dataset guidance. No scope or
architecture discrepancy. Owner artifacts/.gitkeep deletion and untracked
backend/artifacts stay preserved/unstaged. Keep the active worktree/branch.
Formal Tasks4/6 still require applicable source/release governance and actual
authorized runtime exit evidence. C1 bookkeeping alone does not close them.

Final curated evidence seal:489files, SHA-256
`35869101f033d6aa0a645d799aa17bec42090ba868fb409c243d33a61390b7ab`.
Creation and immediate read-only verification pass. Synthetic test temporaries
are excluded; source-derived initial/post-review rehearsal SQL and results are
included. Do not rewrite this sealed root; later checks use sibling folders.

This documentary commit closes the approved implementation plan and updates
the phase index/checkpoint/blocked handoff/current progress. Product9e6526c
is the verified metadata baseline; discover the final documentary SHA in Git
instead of creating a self-referential hash. Shared migrations and activation
remain unapplied; owner artifact changes remain unstaged. All review rulings
and their costs are recorded above; no deferred minors.
