-- Phase 4: Role-Based Access Control and Row Level Security (RLS)
-- Enforces read-only isolation for runtime client roles (anon, authenticated)
-- Ensures staged, draft, or superseded chunks never leak into current retrieval.

-- 1. Enable RLS on all institutional knowledge and operational tables
alter table public.documents enable row level security;
alter table public.document_versions enable row level security;
alter table public.chunks enable row level security;
alter table public.source_spans enable row level security;
alter table public.embedding_sets enable row level security;
alter table public.chunk_embeddings enable row level security;
alter table public.programs enable row level security;
alter table public.curriculum_versions enable row level security;
alter table public.courses enable row level security;
alter table public.course_aliases enable row level security;
alter table public.policy_rules enable row level security;
alter table public.rule_source_spans enable row level security;
alter table public.knowledge_releases enable row level security;
alter table public.release_document_versions enable row level security;
alter table public.release_chunks enable row level security;
alter table public.release_rules enable row level security;
alter table public.active_release enable row level security;
alter table public.ingestion_runs enable row level security;
alter table public.evaluation_runs enable row level security;

-- 2. Explicit grants: SELECT only to anon and authenticated.
-- No INSERT, UPDATE, or DELETE privileges are granted to runtime roles.
grant usage on schema public to anon, authenticated;
grant select on all tables in schema public to anon, authenticated;

-- Ensure future tables in public also do not grant write permissions to anon/authenticated
alter default privileges in schema public grant select on tables to anon, authenticated;

-- 3. RLS Select Policies for Runtime Roles

-- Active release pointer
create policy "p4_active_release_select" on public.active_release
    for select to anon, authenticated
    using (true);

-- Knowledge releases: only active or superseded releases can be read
create policy "p4_knowledge_releases_select" on public.knowledge_releases
    for select to anon, authenticated
    using (status in ('active', 'superseded'));

-- Chunks: STRICT RELEASE ISOLATION
-- Only chunks that belong to the active release are visible to runtime queries
create policy "p4_chunks_select_active" on public.chunks
    for select to anon, authenticated
    using (
        exists (
            select 1 from public.active_release ar
            join public.release_chunks rc on rc.release_id = ar.release_id
            where rc.chunk_id = chunks.chunk_id
        )
    );

-- Chunk embeddings: STRICT RELEASE ISOLATION
-- Only embeddings matching the active release and active release's embedding set
create policy "p4_chunk_embeddings_select_active" on public.chunk_embeddings
    for select to anon, authenticated
    using (
        exists (
            select 1 from public.active_release ar
            join public.knowledge_releases kr on kr.release_id = ar.release_id
            join public.release_chunks rc on rc.release_id = ar.release_id
            where rc.chunk_id = chunk_embeddings.chunk_id
              and kr.embedding_set_id = chunk_embeddings.embedding_set_id
        )
    );

-- Source spans: visible if their chunk is part of the active release
create policy "p4_source_spans_select_active" on public.source_spans
    for select to anon, authenticated
    using (
        exists (
            select 1 from public.active_release ar
            join public.release_chunks rc on rc.release_id = ar.release_id
            where rc.chunk_id = source_spans.chunk_id
        )
    );

-- Document versions: visible if included in active release
create policy "p4_document_versions_select_active" on public.document_versions
    for select to anon, authenticated
    using (
        exists (
            select 1 from public.active_release ar
            join public.release_document_versions rdv on rdv.release_id = ar.release_id
            where rdv.version_id = document_versions.version_id
        )
    );

-- Public metadata & reference tables
create policy "p4_documents_select" on public.documents
    for select to anon, authenticated
    using (true);

create policy "p4_embedding_sets_select" on public.embedding_sets
    for select to anon, authenticated
    using (true);

create policy "p4_programs_select" on public.programs
    for select to anon, authenticated
    using (true);

create policy "p4_curriculum_versions_select" on public.curriculum_versions
    for select to anon, authenticated
    using (approval_status in ('reviewed', 'authorized'));

create policy "p4_courses_select" on public.courses
    for select to anon, authenticated
    using (true);

create policy "p4_course_aliases_select" on public.course_aliases
    for select to anon, authenticated
    using (true);

create policy "p4_policy_rules_select" on public.policy_rules
    for select to anon, authenticated
    using (approval_state = 'authorized');

create policy "p4_rule_source_spans_select" on public.rule_source_spans
    for select to anon, authenticated
    using (true);

create policy "p4_release_doc_versions_select" on public.release_document_versions
    for select to anon, authenticated
    using (true);

create policy "p4_release_chunks_select" on public.release_chunks
    for select to anon, authenticated
    using (true);

create policy "p4_release_rules_select" on public.release_rules
    for select to anon, authenticated
    using (true);

create policy "p4_ingestion_runs_select" on public.ingestion_runs
    for select to anon, authenticated
    using (true);

create policy "p4_evaluation_runs_select" on public.evaluation_runs
    for select to anon, authenticated
    using (true);

-- 4. Search and Release Management RPC Functions

-- Exact cosine search on active release chunks (SECURITY INVOKER inherits caller's RLS)
create or replace function public.match_chunks (
    query_embedding extensions.vector(1024),
    match_threshold double precision default 0.0,
    match_count integer default 10
)
returns table (
    chunk_id text,
    similarity double precision,
    text text,
    source_text text,
    section_path text[],
    scope text[],
    chunk_type text
)
language sql stable security invoker
set search_path = public, extensions
as $$
    select
        c.chunk_id,
        (1 - (ce.embedding <=> query_embedding)) as similarity,
        c.text,
        c.source_text,
        c.section_path,
        c.scope,
        c.chunk_type
    from public.chunks c
    join public.chunk_embeddings ce on ce.chunk_id = c.chunk_id
    where (1 - (ce.embedding <=> query_embedding)) >= match_threshold
    order by ce.embedding <=> query_embedding asc
    limit match_count;
$$;

grant execute on function public.match_chunks to anon, authenticated, service_role;

-- Release activation: transactional and atomic
create or replace function public.activate_knowledge_release(
    p_release_id text,
    p_actor text default 'system'
)
returns void
language plpgsql security invoker
set search_path = public
as $$
begin
    if not exists (select 1 from public.knowledge_releases where release_id = p_release_id) then
        raise exception 'Release % does not exist', p_release_id;
    end if;

    update public.knowledge_releases
    set status = 'superseded'
    where status = 'active';

    update public.knowledge_releases
    set status = 'active', published_at = coalesce(published_at, now()), published_by = p_actor
    where release_id = p_release_id;

    insert into public.active_release (id, release_id, activated_at, activated_by)
    values (1, p_release_id, now(), p_actor)
    on conflict (id) do update
    set release_id = excluded.release_id,
        activated_at = excluded.activated_at,
        activated_by = excluded.activated_by;
end;
$$;

-- Release rollback: points active_release back to a prior validated release
create or replace function public.rollback_knowledge_release(
    p_target_release_id text,
    p_actor text default 'system'
)
returns void
language plpgsql security invoker
set search_path = public
as $$
begin
    if not exists (
        select 1 from public.knowledge_releases
        where release_id = p_target_release_id
          and status in ('active', 'superseded')
    ) then
        raise exception 'Target release % is not eligible for rollback', p_target_release_id;
    end if;

    update public.knowledge_releases
    set status = 'superseded'
    where status = 'active';

    update public.knowledge_releases
    set status = 'active'
    where release_id = p_target_release_id;

    update public.active_release
    set release_id = p_target_release_id,
        activated_at = now(),
        activated_by = p_actor
    where id = 1;
end;
$$;

-- Explicit privilege restriction: only service_role (migration/loader) can activate/rollback releases
revoke execute on function public.activate_knowledge_release from public, anon, authenticated;
revoke execute on function public.rollback_knowledge_release from public, anon, authenticated;
grant execute on function public.activate_knowledge_release to service_role;
grant execute on function public.rollback_knowledge_release to service_role;

