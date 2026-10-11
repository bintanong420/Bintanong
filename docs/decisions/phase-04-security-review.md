# Phase 04 security exit gate reopened

Date: 12 October 2026. Status: audit ruling; remediation pending.

The owner requested independent verification of Phase 04's Supabase RLS and access controls before Phase 05. The review at `8f53b72` found effective runtime TRUNCATE grants on all 19 tables locally and hosted, local DML grants absent from the handoff's account, draft-course/out-of-release-rule visibility, unchecked activation and mutable published content. Hosted changes lack migration history and include ACL changes absent from committed migrations.

Evidence and recovery requirements are in [the review](../../plans/phase-04-security-review-2026-10-12.md). Actual local runtime roles reproduced the policy/lifecycle defects in rolled-back synthetic transactions; hosted catalog inspection confirmed the policy/function definitions and privileges. Structural advisors reported zero lints but did not detect these application security failures.

Ruling: the prior complete Phase 04 handoff no longer establishes the exit gate. Retain its original evidence as historical, mark the current handoff blocked, reopen the Phase 04 checkpoint, and keep Phase 05 preparation only. Authentication without release/approval predicates does not fix the shared corpus access model. No new institutional approval or activation follows from verification.

Remediation should use additive migrations and an explicit access matrix, validate publication before switching releases, preserve published content, and reconcile hosted migration history. An isolated full exit-gate rerun under both `anon` and `authenticated` is required before completion is restored. This review changes documentation only; it does not change database state or implementation.
