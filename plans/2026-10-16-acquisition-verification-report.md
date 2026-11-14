# Acquisition second-check delivery — 16 October 2026

Owner approved the [complete A2 design](2026-10-16-acquisition-verification-design.md)
after184b33f; inline [implementation plan](2026-10-16-acquisition-verification-plan.md)
committedf92b6bc. Loader44e0856/SQLd20153e/fixdba0777 are delivered. Final full
suite passes5507tests/1323subtests, with six skips/warnings,754.26s, exit0.
One Important review finding is corrected; no other material/deferred minor.
This closes the bounded A2 implementation, not formal Phase05.

## Behavior

SourceAcquisitionLoader.verify(current, check) records a second, source-bound
byte check after existing C1 partial review. It requires acquisition observed,
verification pending, approval not_requested/null and content partially_reviewed.
The closed envelope's source ID/hash/locator order must exactly match. New
Evidence must be byte_hash_check by system/reviewer, distinct and nonblank with
no authorization reference, and dated no earlier than the specifically cited
valid A1 observation. Equal instants and existing wide-offset/fraction syntax
remain supported. No unrelated old observation can replace the cited reference.

Only acquisition_state and the one appended Evidence change. Python parses the
full current/resulting/returned source contracts and rejects altered returns.
One admin RPC call is made, without automatic retries or credential fallback.
Current A1/C1/importer interfaces stay unchanged; obsolete earlier replay may
conflict after A2 and must never downgrade acquisition.

CLI-generated additive migration
20261016152947_phase5_acquisition_verification.sql defines
verify_source_acquisition as SECURITY INVOKER with empty search_path and explicit
PUBLIC/anon/authenticated execution denial. Only service_role may execute it.
It independently guards envelope/Evidence/state/source identity, cited A1 and C1
references, distinct history and chronological ordering. Under the existing
publication lock/source row lock it compares the full register and complete
relational projection, excluding only created_at. Exact replay returns without
UPDATE but still checks projection and ever-published membership. Stale,
conflicting, legacy/null, drifted and published sources fail atomically.

This is acquisition byte verification. Source verification stays pending and
approval not_requested/null. No authenticity, current-year validity, institutional
permission or full-document content-review claim follows. Administrative evidence
labels do not authenticate a person; SQL cannot read original files or confirm
an external check. Trusted preparation remains responsible for truthful evidence.

## Evidence and verification so far

Existing readiness Python3.13.7 environment; all tests use -B, pytest without
cache and external basetemp. New ignored raw root:
workspace/audit-evidence/p05-acquisition-verification-20261016.

- Loader RED:37missing-method failures/subcases; GREEN new+A1 units13tests/
  60subtests0.58s, exit0. Existing observe() is unchanged.
- Actual database RED: missing verify_source_acquisition RPC, one failure4.85s.
- Initial DB run:14tests/115subtests pass; four failures/subcases came from three
  test-harness assumptions. Published guard test tried to set published_at on a
  draft (correctly denied by existing trigger); lock probe parsed psql t as JSON;
  direct select denial expected the RPC wrapper's exception. Corrected tests use
  real synthetic activation, to_jsonb and the direct adapter exception. No product
  change was needed for those failures. Focused corrected3tests/12subtests pass
  15.96s, including publication locking and rollback.
- Full relevant regression command includes new A2, A1, C1, selected-review
  loader/database, registration and storage security files: **94tests/630subtests
  pass376.57s**, exit0, regression-temp/regressions.log. All production changes
  remain atd20153e; one final fresh review and final full suite now running.

One real-package rehearsal succeeds in uniquely named disposable DB
bintanong_storage_test_8a49d469d7864b9492ad81c1ee4f5c7f, then drops it.
It reuses the five pending records, original A1/C1 evidence and19saved vectors/
19chunks/54spans/52field associations. Five A2 calls and five exact replays
match the previously prepared full derivatives. Accepted selected-review receipt
and binding record/replay unchanged; activation is denied for missing authority.
Both actual runtime roles see zero rows across seven corpus/release tables,
retrieve_context returns release_changed/no items and admin receipts are denied.
There are zero active pointers and no actual-source publication. All11input
hashes remain unchanged. This is negative activation/access verification, not
positive authorized-runtime relevance calibration or answer generation.

## Rulings and continuation

Ruling: inline execution without another plan/method confirmation follows the
active phase plan and explicit design approval/proceed instruction. Cost if
wrong: isolated implementation rework. Ruling: keep repository plan/checkpoint
and ignored evidence rather than skill scratch/deletion defaults, following
owner continuity/location requirements. Cost: manual ledger upkeep.

Ruling: reuse existing private partial_review_time(text), whose established
calendar/offset/microsecond semantics match the current Python contract, rather
than add another timestamp parser. Cost if wrong: parity drift shared with C1;
new A2 timestamp tests pin equal/wide-offset/long-fraction behavior independently.
No earlier migration or vocabulary is changed.

The single final review disproved complete offset parity in that ruling:
Python normalizes minute components60–99 if the total displacement is under24h,
while the C1 parser rejects them. Parent reproduced **RED4subcases** covering
both the new check and the specifically cited A1 timestamp. The one fix pass
adds private invoker acquisition_check_time(text), which normalizes only the
offset for comparison and delegates calendar/fraction validation to the unchanged
C1 helper. It rejects total displacements of24h or more, preserves original
JSON timestamp text and has explicit restricted EXECUTE grants. Final focused
**23tests/201subtests GREEN106.03s**, exit0, includes complete A2 and existing C1
loader cases. Both reviewer examples and specifically cited A1 offset forms pass;
invalid >=24h offsets remain rejected. No other product finding or deferred minor.

The initial full-suite run was stopped after this finding on only the exact
task-owned Python processes, identified from command-line/basetemp. Its partial
output is retained as interrupted-before-fix-full-suite.log; it is not passing
or final-code verification evidence. Final full verification follows the fix.
The reviewer found no other material issues or minor polish items; no second
independent review is needed. Review reproduction and its dropped DB are under
workspace/audit-evidence/p05-acquisition-verification-review-20261016.

Final review boundary rulings:

- Earlier features beyond their A2 interactions retain their prior delivery
  boundaries; broad regressions cover the interactions. Cost if wrong: a missed
  unrelated older defect; this increment does not claim a whole-system audit.
- Original-source accuracy, authority and phase advancement retain actual source
  gates. Cost if wrong: unsupported guidance if byte identity were misrepresented;
  inactive status and pending verification/approval are preserved.
- Shared deployment/hosted behavior remain outside this local delivery. Cost if
  wrong: environment differences need their applicable deployment/runtime checks;
  no shared application is claimed.
- Deliberate administrative forgery/arbitrary superuser corruption remain outside
  the trusted administration model. Cost if wrong: false evidence supplied by a
  privileged actor; declared labels are not authenticated identities.
- Final whole-suite, evidence seals and all parent-owned cleanup remain the
  parent's gates, not reviewer claims. Cost if wrong: incomplete delivery evidence;
  do not claim closure before those actual results are verified.

Ruling: narrow A2 normalization wrapper replaces the earlier reuse-only choice
because the approved existing-contract parity requirement is binding. Cost if
wrong: an extra private helper to maintain; focused offset tests and unchanged
earlier migrations constrain the risk. No source decision or wider feature added.

The existing C1-before-A2 boundary is retained from the builder-reviewed design;
no new source-content or owner wording decision is inferred. Original PDFs/raw
conversions, F04/G01/originalG02 holds, Charter cutoff, deadline conflicts and
undergraduate scope remain unchanged. Full-source byte hashing does not admit
excluded audiences. No new models, conversions, embeddings, benchmark variants,
parameter sweep, runtime/API/Docker deployment or shared migration application.
No Phase06/executable institutional rules or institutional activation follows.

Context consulted this resume: actual thesis17–18/routing PNG, master10 and
prior same-session39–44/master3/6/11/13, scope/source-gap/dataset guidance and
active phase documents. Existing isolated feat/p05-retrieval-logic retained;
owner artifacts/.gitkeep deletion and untracked backend/artifacts preserved.
Current Supabase Context7 invoker/ACL docs and relevant changelog inspected;
CLI2.117.0/PostgreSQL17.6 retained without installation or version updates.

## Final corrected-code verification — 17 October 2026

Final productdba0777: **5507passed,6skipped,6warnings,1323subtests passed in754.26s**,
exit0. Command: existing readiness Python `-B -m pytest -q -p no:cacheprovider
tests --basetemp <raw-root>/fixed-final-full-temp`, external TEMP/TMP and
BINTANONG_STORAGE_EVIDENCE_DIR=<raw-root>/final-full-db. The six warnings concern
existing pytest markers and Docling/Pydantic deprecations. No environment change,
whole-suite repeat after this successful result, new independent review or
real-package re-rehearsal is needed.

The real package was rehearsed before the timestamp wrapper correction; its
actual Z timestamps remain on the unchanged delegated-parser path. The focused
corrected-code regressions and full suite verify that path plus the additional
normalized offsets. Eleven saved input hashes remain byte-identical, so no new
original-byte measurement, source review, encoding or package replay is required.

Fresh verify_delivery.py checks all11rehearsal input hashes, six historical
seals (8/49/119/489/16047/10files), and all177owned/reviewer disposable database
names absent. Candidate release remains inactive, source verification pending,
approval not_requested/null, C1 and selected review unchanged. Rehearsal database
was dropped; no actual source was published and no shared migration applied.

| Final product file | SHA-256 |
| --- | --- |
| source_acquisition.py | `7e51a7ea493eda535f489fe17dad3049dcab7988578c6a2d8b2cf1e778caf48a` |
| 20261016152947_phase5_acquisition_verification.sql | `3bb2dadb0b21d5e21c04a42140875f9ca3b9bcac5cb62ded41f228cd04a732e6` |
| test_storage_source_acquisition_verification.py | `942723ea79b0b98ef208af6e2936dee0c7c685a266f387c117a84ecae3e46ede` |

The phase worktree/branch and owner artifact changes remain preserved. Formal
Tasks4/6 require actual applicable source/release/authorized-runtime exit evidence;
A2 byte-state bookkeeping supplies no authority. Do not createPhase06, apply the
shared migration, activate sources or repeat completed reviews/experiments.
New evidence seal and final documentary/phase checks are recorded below.

New curated evidence seal created and verified:14825files, manifest SHA-256
`a7b3d2791ae4bd89a9b367861bd8fa889172bf291b4802948fbaa21d8acd5317`.
Only `python -B seal_evidence.py verify` is allowed in that sealed root from now
on. Curated scripts/logs/results and owned disposable SQL are included; synthetic
temporary trees excluded. Final documentation logs use sibling
p05-acquisition-verification-checks-20261017. Keep branch/worktree as already
directed; no integration/deletion menu or push is needed for this increment.

Final documentation/phase-ledger **537tests/11subtests pass12.09s**, exit0.
Phase validation succeeds; can-advance remains blocked as expected, whitespace
clear. Approved bounded implementation plan is complete. This following
documentation-only commit closes delivery; productdba0777 and its recorded hashes
remain unchanged. Discover the documentary SHA through Git rather than embedding
a self-referential hash. No further A2 implementation or unchanged tests,
rehearsal, review, source measurement or retrieval experiment remains authorized
or necessary to finish this approved increment.
