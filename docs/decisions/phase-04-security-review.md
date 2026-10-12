# Phase 04 security exit gate reopened

Date: 12 October 2026. Status: audit ruling; remediation pending.

The owner requested independent verification of Phase 04's Supabase RLS and access controls before Phase 05. The review at `8f53b72` found effective runtime TRUNCATE grants on all 19 tables locally and hosted, local DML grants absent from the handoff's account, draft-course/out-of-release-rule visibility, unchecked activation and mutable published content. Hosted changes lack migration history and include ACL changes absent from committed migrations.

Evidence and recovery requirements are in [the review](../../plans/phase-04-security-review-2026-10-12.md). Actual local runtime roles reproduced the policy/lifecycle defects in rolled-back synthetic transactions; hosted catalog inspection confirmed the policy/function definitions and privileges. Structural advisors reported zero lints but did not detect these application security failures.

Ruling: the prior complete Phase 04 handoff no longer establishes the exit gate. Retain its original evidence as historical, mark the current handoff blocked, reopen the Phase 04 checkpoint, and keep Phase 05 preparation only. Authentication without release/approval predicates does not fix the shared corpus access model. No new institutional approval or activation follows from verification.

Remediation should use additive migrations and an explicit access matrix, validate publication before switching releases, preserve published content, and reconcile hosted migration history. An isolated full exit-gate rerun under both `anon` and `authenticated` is required before completion is restored. This review changes documentation only; it does not change database state or implementation.

## Authorized remediation, 12 October 2026

The owner instructed continued fixes. Repair plan: [Phase 04 security repair](../../plans/2026-10-12-phase04-security-repair.md). The additive implementation now passes 25 isolated storage tests. Administrative RPCs remain INVOKER, all runtime reads are acyclic and tied to the active approved release, and published data is frozen under a common publication lock. Operational run tables are admin only.

Independent review added content-hash/location validation and corpus-bound default embedding identities. Missing/unknown contract schema versions cannot silently bypass a declared contract; administrative DB-row dictionaries undergo explicit content/source checks. Normal Phase 03 artifacts derive set identity from the full corpus, so changed corpora can use the same pinned encoder configuration without mutating an old release. A manifest-only operation needs an explicit set identity.

Hosted historical objects match a fresh baseline exactly apart from function line endings and the previously recorded ACL drift. CLI history repair records those existing objects without replaying CREATE POLICY or altering institutional data. Deployment and final gate remain pending; the initial reopening ruling is retained as history.

## Corrective closure ruling

At `c5beecd` all audit/reviewer findings are corrected. Gate: 31 storage, 12 embedding and 19 ledger tests passed; deployed catalog/function/trigger digests match; six migration versions recorded; both runtime roles have zero mutation/admin-function privileges. Security advisors clear; performance INFO only expected unused indexes. This supersedes the reopening ruling for current status while preserving its evidence.

Hosted platform-managed `supabase_admin` defaults are outside postgres alteration authority. Application objects/migrations use verified postgres ownership with closed defaults and explicit ACLs; managed-role/manual creation still needs fresh effective-privilege review. No institutional release/approval is inferred. Phase 05 is eligible but remains preparation only.
