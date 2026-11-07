# Unified knowledge-update pipeline: policy and prospectus

Started 8 November 2026 at the owner's request ("combine the prospectus and policy
pipelines, combining it with how chunking works, so that it can be like the endpoint
of updating and adding institutional knowledge"; go-ahead: "so start it"). This
continues the ingestion workstream in the [combined ingestion plan](2026-11-02-combined-ingestion-plan.md);
it is not a new phase. Status: plan only. No code is written until the owner answers
the open questions below.

## Thesis support (Context/bintanong_thesis_for_context.pdf)

- Physical p.17 (Scope and Limitations): institutional knowledge changes "only ...
  through the addition and verification of authorized institutional documents by the
  researchers or authorized personnel". One reviewed path is exactly that.
- p.7 "authorized document-update process"; p.22 hot-swap of knowledge; p.64 knowledge
  base and symbolic rules updated between sprints; p.67 latest applicable version.
- Runtime routing PNG: one "Ingestion pipeline" feeds the Prolog query build; RAG and
  symbolic paths stay separate. Master plan 18.3 describes a seven-step authorized
  update workflow (cancelled Phase 13); this plan delivers its local, offline part.

## What exists (verified 8 Nov in p12-dev)

| Step | Policy (Handbook/Charter) | Prospectus |
|---|---|---|
| prepare | `knowledge_update prepare` | same packet |
| review | `/review/policy/...` | `/review/prospectus/...` (prospectus ledger) |
| build | `build.py`: reviewed chunks + embeddings | **missing** |
| rules | n/a | ignored scripts only (`audit-evidence/p06-prospectus-prolog-review-20261022/_evidence/runtime_review.py`) |
| load | T4 not built | ignored `audit-evidence/p09-curricula-load-20261023/load_curricula.py` |
| runtime | `PackageStorage` / hosted chunks | `load_release_curricula` -> `prepare_runtime_bundle` |

Two Prolog generators exist. `prospectus_extractor/prolog.py` (older candidate KB) and
the authoring ledger path (`bintanong_symbolic.authoring.build_curriculum_ledger` ->
`compiler.compile_curriculum_review_bundle` -> `bundle.prepare_runtime_bundle`). The
runtime uses only the ledger path, so this plan uses only the ledger path.

## Target

```text
prepare -> review (human decides every field)
  -> build
       policy:     reviewed chunks -> embeddings                 (RAG)
       prospectus: corrected candidate -> curriculum ledger
                   -> compiler check -> Prolog bundle            (symbolic)
  -> verify (both halves, one manifest)
  -> stage -> publish -> rollback (scratch database; one release links both)
```

## Invariants

1. Eligibility comes from reviewed ledgers and Prolog only, never from embeddings.
2. Nothing unreviewed enters a build; advice and parser success approve nothing.
3. A release pairs a chunk set and its ledgers; neither half publishes alone, and
   rollback restores both.
4. A changed source span reopens review of the rules that cite it; unchanged reviewed
   rules are not re-asked.
5. Blank prerequisite cells follow the 4 Nov owner exception; other gaps stay unknown.
6. Undergraduate scope, source-gap, service-table and F04 holds apply unchanged.
7. Local and scratch targets only. Hosted publishing needs its own owner approval.

## Tasks (test first, synthetic fixtures in tracked tests)

- [ ] **U0 read-only mapping.** Read `runtime_review.py` and `load_curricula.py`, list
  the inputs each needs from a reviewed prospectus and the 9 hosted ledger digests.
  Record any step that depends on hand decisions not stored in the packet.
- [ ] **U1 prospectus build.** Port the ledger construction into tracked
  `knowledge_update/curriculum.py`: corrected candidate + prospectus ledger ->
  `build_curriculum_ledger` -> compiler; a blocked compile stops the build with its
  reasons. Regression: rebuilding an existing reviewed synthetic packet gives a
  byte-identical ledger.
- [ ] **U2 one manifest.** `build` writes chunks and ledgers under one package
  manifest; `verify` rechecks ledger digests and Prolog bundle hashes as well.
- [ ] **U3 change detection.** Compare a new build with the previous package; a
  changed or removed span marks the affected courses for re-review in the reviewer.
- [ ] **U4 release pairing.** Extend T4 stage/publish/rollback so one release links
  chunks and `release_curriculum_ledgers` in one transaction; interruption and repeat
  tests on the scratch database.
- [ ] **U5 reviewer status.** `/review` shows per document what is built, what is
  blocked and why, and what a publish would change.
- [ ] **U6 rehearsal and guide.** Two synthetic editions through every step, then
  rollback; update `docs/development/ai-assisted-ingestion.md`.

U0 and U1 need no owner input beyond this plan. U4 depends on T4 (Stage A).

## Owner decision, 8 November 2026: work on local Supabase

"as much as possible, we're gonna keep it on local Supabase instance ... ayaw ko maaffect yung eval
testing nila". The hosted project serves the evaluators' testing, so it is read-only for this work;
staging, publishing and rollback target the local stack (`supabase_db_Bintanong`, 54321/54322).
This replaces the scratch-database target in U4 for this plan.

Before any local write, hosted and local must match. Checked 8 Nov, read-only on both sides
(hosted through GET requests): 16 tables fingerprinted on content columns plus 9 counted, all equal.
5 releases, active `p12-research-faqsplit-20261030` (560 chunks, vector set `f7a7f1b0…`), 860 chunks,
1,202 vectors, 4,322 spans, 78 curriculum ledgers. No sync was needed; nothing was written.
Evidence: workspace `audit-evidence/p12-dev-supabase-sync-20261108/fingerprint-before.json`.
Not checked: the hosted migration list (direct database connection failed with an SSL EOF; the REST
API does not expose it). Local has the repository's 18 migrations.
Rerun the fingerprint before each local publish; a local change must never be pushed to hosted
without a separate owner decision.

## Open owner questions

1. Use the ledger path as the only rule generator and leave `prospectus_extractor/prolog.py`
   out of this pipeline? (Recommended: yes; the runtime already uses only the ledger.)
2. Curriculum citation chunks: add text chunks so answers can quote the prospectus, or
   keep curricula symbolic-only for now? (Recommended: later; symbolic answers already
   carry source references.)
3. Answered 8 Nov: local Supabase; hosted stays read-only (see above).

## Research note

Bounded to repository evidence: existing modules, the 23 Oct hosted-ledger load and
the p11 ingestion plans. No new dependency, model or library is proposed, so no
external version research applies. Revisit if U4 needs a database feature not yet in
the migrations.
