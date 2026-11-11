# Combined ingestion plan: release rehearsal and AI-assisted review

Recorded 2 November 2026 at the owner's request ("can we combine the Oct 26 + 30 ai
plan?"). Phase 11 task plan in `feat/p11-policy-ingestion-review`; not a new phase.

This file is the single ordered checklist. Detailed steps, tests and exits stay in:
- [Workstream plan, 26 Oct](2026-10-26-policy-ingestion-workstream.md): T0–T5.
- [AI adaptation plan, 30 Oct](2026-10-30-ai-ingestion-adaptation-plan.md): Tasks 0–5.

Both remain authoritative for their tasks. Combining changes sequencing only: the
30 Oct line "Original T4/T5 remain separate" now means separate code and gates,
with one shared end-to-end rehearsal and one operator guide. No boundary is relaxed:
AGENTS.md, undergraduate scope, source-gap/service-table policies, F04 hold, advice
never approving anything, no hosted access, no push, no phase advancement.

## One pipeline

```text
prepare (native, +vision advice, or +LlamaParse candidates)
  -> review (human saves every decision; advice is only a prefill)
  -> build -> verify
  -> stage -> publish -> rollback   (disposable local database only)
```

AI work improves the first two steps. T4 adds the last three. T5 rehearses all of it.

## Shared resources and limits

- Scratch database (owner-approved 2 Nov, T4/rehearsal only): Postgres
  `bintanong-p11-t4-scratch` at 127.0.0.1:55432 and PostgREST `bintanong-p11-t4-rest`
  at 127.0.0.1:55433, network `bintanong-p11-t4-net`, label
  `purpose=p11-t4-disposable-rehearsal`. Secrets ignored under workspace
  `audit-evidence/p11-t4-scratch-db/`. Never the owner's local Supabase (54321/54322),
  the `postgresql-x64-18` service or any hosted target.
  Superseded 8 Nov by the owner: T4 targets the owner's local Supabase (54321/54322); hosted
  stays read-only ([unified plan](2026-11-08-unified-knowledge-update-plan.md),
  [GUI intake plan](2026-11-11-gui-knowledge-intake-plan.md)).
- GPU: the owner's p12 harness runs Gemma on :18088 (~3.5 of 8 GB), API :8021, web
  :3216. Ingestion Gemma (5.1 GB model + 1 GB projector) runs only when the owner
  says the GPU is free. Projector: `MODELS/GEMMA_4_E4B/mmproj-F16.gguf` (2 Nov).
- LlamaParse: needs an owner-configured key and known quota.

## Ordered checklist

### Stage A: no GPU, no owner input (now)

- [ ] **T4** stage/publish/rollback in `local_release.py`, test first. Explicit target
  only: reject missing, hosted, ambiguous and owner-stack targets before connecting.
  Apply migrations to the scratch database; test anon versus service-role access,
  repeat staging, conflicting identities, interruption and journal recovery of the
  previous local release and a local test descriptor.
- [ ] **AI Task 0 (read-only part)**: versions, ports, binary/model/projector paths and
  hashes, pilot roster (Handbook 46, Charter 11–12 plus companions), candidate bundles.
- [ ] **T5 guide draft**: `docs/development/policy-ingestion.md` for the seven commands,
  local target setup and recovery; link the existing `ai-assisted-ingestion.md`.

### Stage B: after owner confirms this combined plan (no GPU)

- [ ] **AI Task 1**: accept a redundant `proposed_value: null` on non-proposals; keep
  malformed, wrong-type and privileged responses failing to manual review. Synthetic only.
- [ ] **AI Task 3, synthetic part**: wrong advice corrected, saved, reopened and built;
  changed content never reuses an old vector.

### Stage C: when the GPU is free

- [ ] **AI Task 2**: launch ingestion Gemma with the new projector after a VRAM check;
  document launch/cleanup; one restart proof.
- [ ] **AI Task 3, real part**: fresh native+vision packet for the pilot pages; owner
  reviews in short batches; build only actually reviewed fields.

### Stage D: when a LlamaParse key and quota exist

- [ ] **AI Task 4**: same pilot pages through `parse-llama`, separate pending packet,
  same human review and build. Without a key it stays NOT RUN.

### Stage E: joint delivery

- [ ] **Joint rehearsal (T5 + AI Task 5)**: two synthetic editions, then the sealed
  baseline, then a human-reviewed assisted packet, each through prepare → review →
  build → verify → stage → publish → rollback on the scratch database.
- [ ] **Measurement (AI Task 5)**: actual corrections, minutes and advice errors per
  strategy; missing data stays blank, no invented winner.
- [ ] **Final checks**: affected ingestion/prospectus/reviewer/storage suites, Node and
  TypeScript, synthetic browser, then the available full Python suite. Update guide,
  results, progress and checkpoint. Remove scratch containers when the owner agrees.

## Open owner inputs

1. Confirm this combined plan (unblocks Stage B).
2. Say when the GPU is free (unblocks Stage C).
3. LlamaParse key and quota, if wanted (unblocks Stage D).
4. Human review of real pilot fields (Stage C onward); nothing is approved for you.
