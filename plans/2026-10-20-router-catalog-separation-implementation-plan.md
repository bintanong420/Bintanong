# Router catalog separation implementation plan

> Execute inline with focused TDD and one fresh whole-change review. No implementer
> agents or repeated review loops. Raw:workspace/audit-evidence/p09-catalog-separation-20261020/.

**Goal:** omit the reviewed alias catalog from model input while preserving host
catalog resolution,scope,facts and every existing safety/quality check.
**Architecture:** same quoted-reference interpreter and deterministic host resolver;
no new stage,model,call or guard. **Tech:**existing Python3.13/pytest.
**Spec:** [reviewed design](2026-10-20-router-catalog-separation-design.md),frozen at
df4ba7a. Owner's "aight continue" directly answers its implementation/evaluation
approval request;approval recorded20October2026. Conditional-answer choice separate.

## Constraints and review focus

- Remove ONLY reviewed_aliases from model payload. Preserve original_text,
  normalized_text,context(program_id,curriculum_id,facts course_id/state),available_operations.
- Preserve build_messages(text,context,catalog,registry) signature and full host
  catalog in both routers. No keyword prefilter or silently dropped proposal entity.
- Router promptv13/combined promptv4;one v12example unchanged. Update only catalog
  wording. Decoder/wire/normalizer/resolver/generation/Prolog/repair budgets unchanged.
- Separate/canonical/scoped selected;ctx8192,out768,temp0,seed0,cachefalse,
  reasoningnone and120/120/120/180s unchanged. No dependency/source/DB/service changes.
- Undergraduate/read-only/source-gap/privacy/release/one-week holds and75accepted
  variants persist. Accuracy first;no Phase10 or activation. No model calls until
  verified software plus exact new input/runtime/protocol freeze.

Review catalog invariance of ACTUAL sent payloads in both profiles,scope-dependent
host binding,retained session facts/private-ID exclusions and unchanged unknown/
ambiguous/conflicting/nonasserted guards. A scripted packet is not model accuracy.

## Task1:payload boundary and regression verification

Files:backend/bintanong_routing/prompt.py,combined.py,README.md;
create tests/test_routing_catalog_separation.py;update the old catalog-exposure
expectation in tests/test_routing_combined.py. Existing other interfaces unchanged.

- [x] Add four cases across both profiles:catalog-invariant complete messages with
  all other payload fields/private exclusions preserved;actual Router resolution
  of the same quoted A1 packet against two curriculum versions in the host catalog,
  retaining missing-scope behavior/call limits and no catalog in the sent payload.
- [x] Expected RED4failed1.06s before product edits. Remove the single payload field,
  correct catalog wording/version identities and update obsolete exposure expectation.
- [x] Focused GREEN4passed0.71s;routing/prompt-schema gate241passed3.80s.
  Reuse existing unknown/ambiguous/conflicting/nonasserted/session tests;no duplicate
  test matrices or old688gate. Record commands/results and commit verified code.
- [x] One fresh read-only review df4ba7a..0aaa074:no product findings;one stale
  checkpoint phrase corrected in normal handoff. No re-review or product fix pass.
  Freeze8e803b707fce21bcadfc696aee9e14434a3ab6b76844c8311957471e8ff6d106;
  240prior sealed files intact,both decoders/worked example/179other modules unchanged.

## Task2:one actual quality/timing observation

- [x] Protocola2b4f2d BEFORE inference:exact same d-en,d-fil,d-tl,h-en
  questions/references/artifacts and order,unchanged runtime/settings. Four explicit
  if/kung cases remain held. Expected response AND full quality4/4 for this gate.
- [x] Bind exact code/inputs/labels/observer/protocol/HEAD;readiness0.116103s at18088.
  Unavailable/mismatch -> NOT RUN,no startup/alternate endpoint/quiet retry.
- [x] Four requests ONCE,14calls/zero repairs;response3/4,full quality1/4:FAIL.
  No rescue probe,rereun,candidate fix or settings change. Assess each response,
  separate parts,target/failure/mode,actual Prolog,claim support and language.
- [x] Report component45.705-50.634s/exclusions separately from browser/full retrieval/
  Supabase/startup/queue. Known developer cases,not unseen or institutional accuracy.
  Stop on failure and discuss capability limits;no next prompt/classifier/sweep.
  Even4/4does not close Phase09;preserve remaining route/language/exit requirements.
- [x] Fresh docs10passed0.78s;84links/caps;240prior seals/current184file hashes
  verified. New46raw files sealed;progress/checkpoint/index current;commit follows.

No permission round between these approved tasks. Actual observation results,
not software success or input-byte reduction,determine quality/timing claims.
