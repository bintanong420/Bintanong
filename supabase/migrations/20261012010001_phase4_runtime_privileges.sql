-- Additive repair: Supabase's existing grants are not replaced by GRANT SELECT.
revoke all privileges on all tables in schema public from public, anon, authenticated;
revoke all privileges on all sequences in schema public from public, anon, authenticated;
revoke create on schema public from public, anon, authenticated;
grant usage on schema public, extensions to anon, authenticated, service_role;
grant all privileges on all tables in schema public to service_role;
grant all privileges on all sequences in schema public to service_role;

grant select on public.documents, public.document_versions, public.chunks,
    public.source_spans, public.embedding_sets, public.chunk_embeddings,
    public.programs, public.curriculum_versions, public.courses, public.course_aliases,
    public.policy_rules, public.rule_source_spans, public.knowledge_releases,
    public.release_document_versions, public.release_chunks, public.release_rules,
    public.active_release to anon, authenticated;

-- Defaults belong to the object creator, not the schema owner. Handle the
-- migration owner and other Supabase creators only when permitted to do so.
do $repair_defaults$
declare creator record;
begin
    for creator in
        select oid, rolname from pg_roles
        where rolname in (current_user, 'postgres', 'supabase_admin')
          and pg_has_role(current_user, oid, 'MEMBER')
    loop
        execute format('alter default privileges for role %I in schema public revoke all on tables from public, anon, authenticated', creator.rolname);
        execute format('alter default privileges for role %I in schema public revoke all on sequences from public, anon, authenticated', creator.rolname);
        -- PUBLIC's built-in EXECUTE default is global, so revoke globally.
        execute format('alter default privileges for role %I revoke execute on functions from public, anon, authenticated', creator.rolname);
        execute format('alter default privileges for role %I in schema public revoke execute on functions from public, anon, authenticated', creator.rolname);
        execute format('alter default privileges for role %I in schema public grant all on tables to service_role', creator.rolname);
        execute format('alter default privileges for role %I in schema public grant all on sequences to service_role', creator.rolname);
    end loop;
end;
$repair_defaults$;

drop policy if exists p4_ingestion_runs_select on public.ingestion_runs;
drop policy if exists p4_evaluation_runs_select on public.evaluation_runs;

revoke execute on function public.match_chunks from public, anon, authenticated;
grant execute on function public.match_chunks to anon, authenticated, service_role;
revoke execute on function public.activate_knowledge_release from public, anon, authenticated;
revoke execute on function public.rollback_knowledge_release from public, anon, authenticated;
grant execute on function public.activate_knowledge_release to service_role;
grant execute on function public.rollback_knowledge_release to service_role;
