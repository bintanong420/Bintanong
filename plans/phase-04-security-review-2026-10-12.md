# Phase 04 independent security review — 12 October 2026

**Historical disposition (audit baseline): Phase 04's security exit gate fails. Phase 05 must remain preparation only.**

**Remediation completed at `c5beecd`.** Findings below remain the audit record; the [corrective handoff](phase-04-handoff.md) contains current deployment/exit-gate evidence.

Review baseline: `8f53b72f45e7bd5c3c6ac35094bb08cca9eed14a`, branch `feat/p04-supabase-rls`, initially clean. Scope: committed Phase 04 schema/RLS migrations, storage clients/loader/release manager, existing verification fixtures, actual local Supabase and hosted `Project_Bintanong` (`jyrudbiuajahsucsorco`). Requirements: master plan sections 9.1–9.2, 10.1 and 18.2; Phase 04 plan and handoff.

Hosted inspection used read-only Supabase MCP catalog queries, migration listing and security/performance advisors. Local behavioral probes used actual `anon`, `authenticated` and `service_role` roles in synthetic transactions ending in `ROLLBACK`. No hosted data, grants, policies or schema were changed. No production source was activated. Implementation and migrations remain unchanged by this review.

## Findings

### F1 — P1: runtime roles retain privileges that RLS cannot restrict

Location: `supabase/migrations/20261012010000_phase4_rls_policies.sql:25`.

The migration grants SELECT, but never revokes existing table privileges. `ALTER DEFAULT PRIVILEGES ... GRANT SELECT` also adds a privilege; it does not replace Supabase's existing defaults. Local `config.toml` leaves automatic exposure enabled by default.

Fresh catalog results:

| Database / role | SELECT tables | INSERT tables | UPDATE tables | DELETE tables | TRUNCATE tables |
| --- | ---: | ---: | ---: | ---: | ---: |
| Local / anon | 19 | 19 | 19 | 19 | 19 |
| Local / authenticated | 19 | 19 | 19 | 19 | 19 |
| Hosted / anon | 19 | 0 | 0 | 0 | 19 |
| Hosted / authenticated | 19 | 0 | 0 | 0 | 19 |

Both databases also retain broad default table ACLs. Hosted `postgres` table defaults give runtime roles `rDxtm`, including TRUNCATE; local defaults give `arwdDxtm`. This invalidates the handoff's claim of zero runtime write privileges.

Current SELECT-only RLS policies still deny INSERT and make local UPDATE/DELETE affect zero rows. That does **not** make these roles read only: PostgreSQL excludes whole-table operations such as TRUNCATE from RLS. A SQL execution path operating as either role could truncate institutional tables, subject to ordinary locks and FK constraints. No TRUNCATE was executed. This review does not claim that a public PostgREST endpoint currently exposes TRUNCATE; both roles are NOLOGIN and normal REST row operations do not offer that command.

Required correction: explicitly revoke all unnecessary table privileges, including TRUNCATE, REFERENCES, TRIGGER and MAINTAIN where applicable; grant only the required reads; fix defaults for the actual migration owner and retain explicit admin grants. Verify effective privileges after fresh migrations and on hosted Supabase, rather than relying on RLS write failures alone.

### F2 — P1: related knowledge tables bypass approval and release visibility

Location: `supabase/migrations/20261012010000_phase4_rls_policies.sql:111`.

`courses` and `course_aliases` use `USING (true)`. The curriculum policy hides drafts, but its child tables do not inherit that restriction. Both runtime roles read a synthetic draft course, its raw prerequisite and alias while its parent curriculum remains invisible.

`policy_rules` checks `approval_state = 'authorized'` without checking release membership. Both runtime roles read an authorized rule absent from every release, with no active release at all. `rule_source_spans` exposes candidate rule/span identifiers despite hiding the rule and source span themselves. All three release-membership tables expose draft memberships. `documents`, `embedding_sets`, ingestion summaries and evaluation metadata are also unconditionally readable; any intended public subset needs to be explicit.

These are actual SELECT policies, not missing-RLS advisor warnings. All hosted/local policy predicates match, so the same policy defects exist hosted. Hosted knowledge tables are currently empty; no existing institutional record exposure is claimed.

Required correction: define a table-by-table access matrix; bind released rules and related entities/provenance to the allowed release and appropriate approval state; withhold administrative run metadata unless intentionally public. Avoid creating recursive policy dependencies when restricting membership tables. Authentication or a generic `auth.uid()` predicate alone does not solve release isolation for a shared institutional corpus.

### F3 — P1: activation accepts incomplete and unapproved releases

Locations: `supabase/migrations/20261012010000_phase4_rls_policies.sql:194`; `backend/bintanong_storage/release.py:32`.

`activate_knowledge_release` checks only whether the release ID exists. Neither the Python manager nor the SQL function validates document approval, chunk review, source bindings, embedding coverage/content hashes/configuration or declared row counts. Creation writes the release header and memberships through separate HTTP requests, so an interrupted creation leaves a draft that this activation function still accepts. Activation can also promote a `revoked` release; it does not require an eligible status.

The local probe created a release with an unapproved document version, pending chunk/source review and **zero embeddings for its member chunk**. Invocation as `service_role` succeeded. Both runtime roles immediately read the pending chunk and unapproved document version. The transaction was rolled back. Hosted activation has the same function body.

Required correction: fail activation before changing the active pointer unless all required approval, source, vector and completeness checks pass. Separate synthetic verification fixtures from institutional activation eligibility. Test partial imports and revoked targets. Serialize concurrent publication and validate a consistent membership snapshot; concurrency was not exercised in this review.

### F4 — P1: published release membership and content are mutable

Locations: `backend/bintanong_storage/loader.py:114`, `:119`, `:152`; release-membership tables in the schema migration.

There are no non-internal hosted table triggers protecting published memberships or shared chunk/embedding content. The loader merges changes into existing chunks, embedding sets and embeddings, and deletes/reinserts spans through independent requests. It has no guard against changing data referenced by an active or historical release.

In a local transaction, `service_role` changed an active chunk's text and removed/reinserted its release membership. Runtime reads immediately reflected those changes under the same release ID. No new publication or release-version change was needed. This disproves the handoff's immutable-membership claim and allows a later load to alter current or historical evidence without a release switch. The service role is intentionally privileged; the defect is the supported publication workflow's missing invariants, not an anonymous privilege escalation.

Required correction: make published membership/content immutable through the supported loader and database lifecycle; reject conflicting identities; use new versioned rows/releases for changes; publish a complete staging transaction rather than exposing separate span deletion/insertion requests. Verify rollback still resolves the original content.

### F5 — P2: hosted deployment is not recorded in migration history

Hosted MCP `list_migrations` returns an empty list. `to_regclass('supabase_migrations.schema_migrations')` returns NULL, even though all 19 tables, policies and three RPCs exist. Local history contains the three committed migration versions. Hosted INSERT/UPDATE/DELETE privileges have been revoked through changes absent from the committed RLS migration, while local privileges remain broad.

Required correction: reconcile the hosted schema/ACL baseline and actual migration history with committed migrations before a normal push. Do not blindly replay CREATE POLICY statements against the already existing hosted policies or treat matching table names as proof of a reproducible deployment.

## Verified behavior that is correct

- RLS is enabled on all 19 knowledge/operational tables locally and hosted; runtime roles are neither superusers nor BYPASSRLS roles. `service_role` intentionally has BYPASSRLS.
- The three RPCs are SECURITY INVOKER with explicit search paths. Both runtime roles lack EXECUTE on activation/rollback; `match_chunks` is executable under runtime RLS.
- Synthetic draft chunks remain hidden before activation. Sequential activation hides the prior release's chunks, exposes the selected release's chunks and embeddings, and rollback restores the prior membership view. Exact vector search returned the single allowed test vector.
- Local runtime INSERT and both administrative RPC calls returned SQLSTATE `42501`; UPDATE and DELETE affected zero rows. Local HTTP probes using the anon client read the empty active pointer and received HTTP 401 / SQLSTATE `42501` for each administrative RPC.
- Hosted security and performance advisors both returned zero lints. This is a useful structural result, but it does not test approval/release semantics or certify least privilege.
- Local PostgreSQL is 17.6; hosted engine reports 17.6.1.166. Both have vector 0.8.2. No additional public views were found in the hosted catalog inspection.

## Evidence and practical limits

External evidence root: `C:/Coding-projects/bintanong_workspace/audit-evidence/p04-20261012/`.

- `run_audit.py`, generated `visibility-anon.sql` / `visibility-authenticated.sql`, their `.out` logs and `post-rollback.sql` / `.out`: role-level synthetic reproductions. Command: `python C:/Coding-projects/bintanong_workspace/audit-evidence/p04-20261012/run_audit.py`, exit 0. The successful exit means the probes ran; the returned visibility values demonstrate security failures.
- `local-catalog.sql` / `.json`, `hosted-catalog.json`: effective ACL/policy/default/function/extension snapshots. Hosted MCP queries and the local Docker/psql queries exited successfully. The query results agree on every SELECT policy predicate.
- Cleanup query returned audit chunk/document/release counts of 0 and active-pointer count of 0, matching the original local baseline. Hosted chunk/embedding/release/active-pointer counts were all 0.
- Existing `tests/test_storage_*.py` were inspected but not rerun. Their setup/cleanup deletes the shared active pointer and uses fixed global fixture IDs; running them against an arbitrary configured Supabase endpoint could destroy release state. System Python is 3.13.7; pytest is unavailable there, and no dependencies were installed. These limits do not prevent the direct SQL/HTTP verification above.
- The prior claim of 8 passing storage tests is historical evidence only. Those tests do not cover effective table ACLs/TRUNCATE, the authenticated role, draft curriculum children, out-of-release rules, approval/completeness rejection, immutability or concurrent activation.
- Hosted Data API exposure settings, authenticated JWT HTTP requests, concurrent activation and a full import/exit-gate suite were NOT RUN. Hosted policies/privileges were checked directly, with synthetic behavioral reproduction performed locally under both roles.
- Phase 05 pinned-release/scope support is still future work: `match_chunks` accepts neither a release ID nor a scope filter. That is a documented prerequisite, not proof that the current Phase 05 implementation failed.

Reviewed migration SHA-256 values:

| Migration | SHA-256 |
| --- | --- |
| `20260920000000_enable_vector.sql` | `4a915b03677970e0043876db380d5d00c44687e45c94a57da8ce51212c649d94` |
| `20261012000000_phase4_knowledge_schema.sql` | `3c855a7d814777c1d5c530f14a5ed5e3e2320f95bd495ec844fdefc05c56d8a4` |
| `20261012010000_phase4_rls_policies.sql` | `2b70ba63a08f0beb279e41fae337d7ba544dec8d9fa71e91df4f52ca726072b4` |

## Recovery and phase ruling

Reopen Phase 04's security verification. Preserve the original completion narrative as historical, attach this corrective review, and change its handoff to blocked. Phase 05 remains a prepared plan with `preparation_only: true` and cannot begin based on the invalidated exit evidence.

Next implementation unit: fix and verify F1 with an additive migration and effective ACL checks in an isolated database, then address F2–F4 and reconcile F5. Re-run the complete Phase 04 exit gate under both runtime roles before issuing a complete handoff. Hosted remediation and any institutional activation retain their applicable execution boundaries.

## Documentation consulted

- [PostgreSQL 17 row security](https://www.postgresql.org/docs/17/ddl-rowsecurity.html): RLS excludes TRUNCATE/REFERENCES and defaults to denying row operations without matching policies.
- [Supabase Data API security](https://supabase.com/docs/guides/api/securing-your-api): grants and RLS are separate controls; automatic exposure requires deliberate privilege handling.
- [Supabase database functions](https://supabase.com/docs/guides/database/functions): invoker/definer behavior and EXECUTE restrictions; current documentation fetched through Context7 `/supabase/supabase`.
- [Supabase changelog](https://supabase.com/changelog): current index fetched; recent entries did not explain or remedy these application policy defects.
