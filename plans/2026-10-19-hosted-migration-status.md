# Hosted migration status - read-only observation

19October2026,15:25. Owner asks why Supabase's latest migration was seven days ago.
Read-only configured Supabase MCP list_migrations returns six applied versions:
20260920000000,20261012000000,20261012010000,20261012010001,
20261012010002,20261012010003. Latest recorded migration version dates12October.
No migration or database mutation performed for this question.
Configured get_project_url confirms projectjyrudbiuajahsucsorco, matching the
Phase04 handoff's hosted project. This is not a comparison against a different DB.

Repository supabase/migrations has13files. Seven Phase05 versions are absent from
the connected hosted migration history:

| Version | Migration |
| --- | --- |
| 20261012013339 | phase5_retrieval_snapshot |
| 20261016000000 | phase5_source_registration |
| 20261016093918 | phase5_acquisition_observation |
| 20261016103716 | phase5_partial_source_review |
| 20261016131344 | phase5_selected_release_review |
| 20261016152947 | phase5_acquisition_verification |
| 20261016162938 | phase5_source_observation |

git log -1 --date=iso-strict -- supabase/migrations identifies latest migration-file
changeee7567a,17October00:37:54+08:00. File/commit time differs from hosted history;
the list is not proof of the last data write, corpus ingestion or deployment time.
No fresh table/row,health/advisor,drift or local applied-history audit was performed.

[Phase05 remaining-exit packet](2026-10-16-phase05-remaining-exit-packet.md),lines79-84,
explicitly recorded hosted Phase04-only schema and pending Phase05 deployment;
the [final handoff](phase-05-handoff.md) completed offline research/software only.
Phase06/07 work remains offline/local; no Phase07 schema migration is required for
the current router/style increment. This does not make the hosted schema current.

Before integration relying on Phase05 database objects, reconcile the intended
hosted project, actual schema/history, migration prerequisites and tests. Review
the concrete migration set/rollout before applying it within owner-authorized
deployment scope. Schema synchronization and institutional data/release activation
are separate actions; neither is authorized by the owner's status question.
This observation does not block the current local synthetic routing evaluation.

Context7 /supabase/cli migration-history documentation confirms that repository
files and remote supabase_migrations.schema_migrations history are separate and
version comparisons alone do not audit actual schema contents. See
[official migration-list docs](https://github.com/supabase/cli/blob/develop/apps/cli/docs/supabase/migration/list.md).
Do not mark absent versions applied with migration repair merely to hide the gap;
first determine actual schema state and the intended rollout. No CLI push, pull,
repair or schema-changing command was run for this observation.
