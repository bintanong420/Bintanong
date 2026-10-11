-- Operational metadata remains inaccessible even if a future permissive policy
-- or SELECT grant is accidentally added for runtime roles.
create policy p4_operational_runtime_deny on public.ingestion_runs as restrictive
    for all to anon,authenticated using(false) with check(false);
create policy p4_operational_runtime_deny on public.evaluation_runs as restrictive
    for all to anon,authenticated using(false) with check(false);

-- Cover existing foreign keys and the publication/approval lookups using them.
create index p4_active_release_release on public.active_release(release_id);
create index p4_chunks_document on public.chunks(document_id);
create index p4_curriculum_document_version on public.curriculum_versions(document_version_id);
create index p4_evaluation_release on public.evaluation_runs(release_id);
create index p4_knowledge_embedding_set on public.knowledge_releases(embedding_set_id);
create index p4_source_span_version on public.source_spans(version_id);
