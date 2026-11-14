# Scoped printed-observation delivery — 17 October 2026

Owner approved the [complete V1 design](2026-10-17-source-observation-design.md)
after2a472ba with “alright i approve, continue”. The inline
[implementation plan](2026-10-17-source-observation-plan.md) is committed99a1b21;
loader52619c1/storageee7567a are delivered. Final full suite5530tests/1480subtests
passes873.03s, exit0; one fresh final review is clear. This report concerns the
bounded implementation, not formal
Phase05 completion or institutional activation.

## Behavior and boundaries

SourceVerificationLoader.observe(current, observation) records V1 printed-span
observations using existing A2/C1 and the accepted undergraduate selection.
It requires acquisition verified, verification pending, content partially_reviewed
and approval not_requested/null. The closed receipt binds source ID/hash/locators,
the current C1 reference and stored selected-review scope. Distinct reviewer
Evidence appends once; only verification_state changes to observed. The actual
C1 reviewer label is retained, with compiler and compilation-time meaning separate.
Existing confirmation times remain in C1. No new human or issuing-office event
is claimed, and no scope/issuer/effectivity/approval field is inferred.

Python parses complete current, proposed and returned source contracts. It
requires an exact return and makes one admin RPC call without automatic retries
or role fallback. Existing authoring bindings become stale; ordinary bind_chunk
and load_chunks refresh verification metadata separately. The C1 content binding,
chunk text, spans, hashes, fields, source limitations and saved vectors stay intact.

CLI-generated additive migration20261016162938_phase5_source_observation.sql
adds immutable source_verification_observations, with composite source/C1 and
selected-scope references, RLS/restrictive runtime denial and mutation guards.
The admin-only SECURITY INVOKER RPC has an empty search_path and explicit
PUBLIC/anon/authenticated execution denial. Under publication/source locks it
validates receipt shape/state/evidence, source/C1/selection identity, reviewer
attribution and compilation ordering. Existing validate_selected_review checks
actual selected content/spans/fields/limits/groups/neighbors; this source's
selected snapshots must equal its complete referenced C1 selection.

Full register and relational projection comparison excludes only created_at.
Legacy/null, stale/conflicting, drifted and ever-published sources reject.
Receipt/source updates are atomic. Exact replay rechecks receipt, projection
and snapshots without UPDATE. Equal concurrent calls converge; competing calls
conflict. Timestamp comparison reuses acquisition_check_time, including existing
offset normalization/fraction semantics, without changing stored timestamp text.

Administrative evidence labels are declared attribution, not authenticated
identities. Trusted preparation remains responsible for truthful existing
confirmations. V1 observed is distinct from V2 school verification and P2
approval. Whole originals remain partially reviewed. Known F04/G01/originalG02
holds, Charter103 cutoff and handbook47 conflict remain attached. Undergraduate
applicability governs selection, including general student services and staff
actions within them; excluded audiences and unknown applicability stay excluded
or unresolved. No shared migration, publication, runtime deployment orPhase06.

## Verification

Existing readiness Python3.13.7; -B pytest without cache, external basetemp and
TEMP/TMP. Raw evidence is retained under workspace/audit-evidence/
p05-source-observation-20261017. No installation/dependency/lock/model changes.

- Loader missing-module RED50failures/subcases; initialGREEN20tests/157subtests
  0.80s, final binding composition check21tests/157subtests0.86s.
- Database missing-RPC RED1test5.99s. Initial SQL run11failed/12passed/149subtests
  76.31s exposed ambiguous key; qualifying projection columns corrected it.
  One selector typo exited4 with no tests and was corrected to actual filenames.
- One saved-package rehearsal applies/replays5V1 receipts, compares exact
  prepared derivatives, rebinds19chunks, retains54spans/52field associations/
  19saved vectors and unchanged C1/selected receipts/binding.13input hashes
  unchanged; missing-authority activation denied, zero active pointers. Both
  actual runtime roles see zero corpus rows, retrieve release_changed/noitems
  and cannot read any of the three administrative receipt tables. DB dropped.

Final relevant326tests/216subtests pass185.23s, exit0: new unit/DB files,
selected-review database regressions and three source-contract files.

One fresh final reviewer (gpt-6-astra/high) inspected2a472ba..ee7567a against
the complete design/plan and returned no Critical, Important or actionable minor
finding. No fix pass or second review is required. Its independent two-file run
finished but the final summary/exit code was not retained, so its test outcome
is explicitly inconclusive, not passed; no rerun. All11reviewer-created DBs are
confirmed absent. Root's retained relevant run and final full suite are the
authoritative test evidence. Raw assessment is final-review.txt in the new root.
Final full-suite, integrity and seal results follow.

## Final unchanged-code regression result

Final productee7567a: **5530passed,6skipped,6warnings,1480subtests passed in873.03s**,
exit0. Command: existing readiness Python `-B -m pytest -q -p no:cacheprovider
tests --basetemp <raw-root>/final-full-temp`, external TEMP/TMP and
BINTANONG_STORAGE_EVIDENCE_DIR=<raw-root>/final-full-db. The warnings concern
existing Starlette/HTTPX and Docling/Pydantic deprecations and a pytest GPU marker.
No dependency or environment change follows. No unchanged full-suite repeat,
second review, real-package rehearsal or retrieval experiment is needed.

Fresh verify_delivery.py confirms all13rehearsal inputs byte-identical, eight
prior seals intact (8/49/119/489/16047/10/14825/10files), and all150owned/reviewer
disposable database names absent. The rehearse database was dropped; no actual
source published, zero active pointers, and no shared migration was applied.

| Final product file | SHA-256 |
| --- | --- |
| source_verification.py | `d3b3e9e89d01b101017a1204dd45d5af20c08e035756656f944b441d2ff0dc5b` |
| 20261016162938_phase5_source_observation.sql | `48972cfbf116fefc50ae6599c4867cda351850e7ae0fdd189eca37991eaf319c` |
| test_storage_source_verification.py | `299c14de7f731edbf82a9a7bc25f94e50b0e123d58016c32bf3d1240b70c9032` |
| test_storage_source_verification_database.py | `ed0a3f77d2f78c5d110d307e718dc22f3fa42881d4362d67e9f07523ef1f274b` |

New curated evidence seal created and verified:11663files, manifest SHA-256
`28d0b6e7efffb1541f4242e93796dd91af944aaaa3d18ea6b77f0d4d3808b6c2`.
Only `python -B seal_evidence.py verify` is allowed in that root from now on.
Curated scripts/logs/results and owned disposable SQL are included; synthetic
temporary trees excluded. Final documentation logs use sibling
p05-source-observation-checks-20261017. Final docs/phase-ledger541tests/11subtests
pass17.25s, exit0; phase validation succeeds and can-advance remains blocked as
expected, whitespace clear. Following explicit documentary commit closes the
approved bounded plan; discover its SHA through Git. Keep branch/worktree/owner dirt; formal actual
source/release/authorized-runtime exit evidence is the next prerequisite.

## Decisions and recovery

Ruling: execute the approved plan inline without another method/plan confirmation;
the explicit approval/proceed instruction and active Phase05 plan already supply
it. Cost if wrong: isolated rework. Retain repository plan/checkpoint and ignored
raw evidence instead of skill scratch deletion, per owner location/preservation
rules; cost: manual ledger upkeep. Keep the existing branch/worktree and owner
artifact changes; no integration menu, push or deletion is needed.

Consulted actual thesis17–18, routing PNG, master6/10, scope/source-gap policies
and active ledger; no discrepancy. Context7 Supabase invoker/privilege docs and
current changelog consulted; installed CLI2.117.0/PostgreSQL17.6 retained.
Formal Phase05Tasks4/6 require actual applicable source/release/authorized-runtime
exit evidence. Reuse completed source reviews, vectors and accepted questions.
