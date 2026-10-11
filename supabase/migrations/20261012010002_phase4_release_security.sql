-- Publication, provenance and active-release access invariants.
create schema if not exists bintanong_private;
revoke all on schema bintanong_private from public, anon, authenticated;
grant usage on schema bintanong_private to service_role;

-- Preserve the contract's ordered printed spans and textless table locators.
alter table public.chunks alter column source_text drop not null;
alter table public.source_spans alter column text drop not null;
alter table public.source_spans add column span_order integer not null default 0 check (span_order>=0);
with numbered as (
    select span_id,row_number() over(partition by chunk_id order by created_at,span_id)-1 as ordinal from public.source_spans
) update public.source_spans s set span_order=n.ordinal from numbered n where n.span_id=s.span_id;
create unique index p4_source_span_order on public.source_spans(chunk_id,span_order);

alter table public.knowledge_releases
    add column expected_chunk_count integer check (expected_chunk_count > 0),
    add column expected_document_version_count integer check (expected_document_version_count > 0),
    add column expected_rule_count integer check (expected_rule_count >= 0);
create unique index p4_one_active_release on public.knowledge_releases ((status)) where status='active';
create index p4_release_versions_version on public.release_document_versions(version_id);
create index p4_release_rules_rule on public.release_rules(rule_id);

-- Acyclic dependencies: pointer -> release memberships -> evidence -> children.
alter policy p4_knowledge_releases_select on public.knowledge_releases using (
    status='active' and release_id=(select ar.release_id from public.active_release ar));
alter policy p4_release_doc_versions_select on public.release_document_versions using (
    release_id=(select ar.release_id from public.active_release ar)
    and exists(select 1 from public.knowledge_releases kr where kr.release_id=release_document_versions.release_id));
alter policy p4_release_chunks_select on public.release_chunks using (
    release_id=(select ar.release_id from public.active_release ar)
    and exists(select 1 from public.knowledge_releases kr where kr.release_id=release_chunks.release_id));
alter policy p4_release_rules_select on public.release_rules using (
    release_id=(select ar.release_id from public.active_release ar)
    and exists(select 1 from public.knowledge_releases kr where kr.release_id=release_rules.release_id));
alter policy p4_document_versions_select_active on public.document_versions using (
    approval_state='approved' and verification_state='verified' and content_review_state='reviewed'
    and exists(select 1 from public.release_document_versions rdv where rdv.version_id=document_versions.version_id));
alter policy p4_documents_select on public.documents using (
    exists(select 1 from public.document_versions dv where dv.document_id=documents.document_id));
alter policy p4_chunks_select_active on public.chunks using (
    anchored and source_verification='verified' and content_review='reviewed'
    and exists(select 1 from public.release_chunks rc where rc.chunk_id=chunks.chunk_id)
    and exists(select 1 from public.document_versions dv where dv.version_id=chunks.version_id
        and dv.document_id=chunks.document_id and dv.byte_sha256=chunks.byte_sha256 and dv.edition_id=chunks.edition_id));
alter policy p4_source_spans_select_active on public.source_spans using (
    exists(select 1 from public.chunks c where c.chunk_id=source_spans.chunk_id
        and c.version_id=source_spans.version_id and c.byte_sha256=source_spans.byte_sha256));
alter policy p4_chunk_embeddings_select_active on public.chunk_embeddings using (
    exists(select 1 from public.chunks c where c.chunk_id=chunk_embeddings.chunk_id
        and c.content_hash=chunk_embeddings.chunk_content_hash)
    and exists(select 1 from public.knowledge_releases kr where kr.embedding_set_id=chunk_embeddings.embedding_set_id));
alter policy p4_embedding_sets_select on public.embedding_sets using (
    exists(select 1 from public.knowledge_releases kr where kr.embedding_set_id=embedding_sets.embedding_set_id));
alter policy p4_curriculum_versions_select on public.curriculum_versions using (
    approval_status='authorized' and exists(select 1 from public.document_versions dv
        where dv.version_id=curriculum_versions.document_version_id));
alter policy p4_programs_select on public.programs using (
    exists(select 1 from public.curriculum_versions cv where cv.program_code=programs.program_code));
alter policy p4_courses_select on public.courses using (
    exists(select 1 from public.curriculum_versions cv where cv.curriculum_version_id=courses.curriculum_version_id
        and cv.program_code=courses.program_code));
alter policy p4_course_aliases_select on public.course_aliases using (
    exists(select 1 from public.courses c where c.course_id=course_aliases.canonical_course_id));
alter policy p4_policy_rules_select on public.policy_rules using (
    approval_state='authorized' and exists(select 1 from public.release_rules rr where rr.rule_id=policy_rules.rule_id));
alter policy p4_rule_source_spans_select on public.rule_source_spans using (
    exists(select 1 from public.policy_rules pr where pr.rule_id=rule_source_spans.rule_id)
    and exists(select 1 from public.source_spans ss where ss.span_id=rule_source_spans.span_id));


-- Python canonical_text/compute_content_hash parity: NFC, Python whitespace,
-- UTF-8 JSON array with printed text first. No extension or trust bypass needed.
create function bintanong_private.content_hash(p_source text,p_text text) returns text
language sql immutable security invoker set search_path='' as $$
    select encode(sha256(convert_to(jsonb_build_array(
        pg_catalog.normalize(btrim(regexp_replace(translate(coalesce(p_source,p_text),
            U&'\0009\000A\000B\000C\000D\001C\001D\001E\001F\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000',repeat(' ',28)), ' +',' ','g')), 'NFC'),
        pg_catalog.normalize(btrim(regexp_replace(translate(p_text,
            U&'\0009\000A\000B\000C\000D\001C\001D\001E\001F\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000',repeat(' ',28)), ' +',' ','g')), 'NFC')
    )::text,'UTF8')),'hex');
$$;

create function bintanong_private.valid_locator(p_locator jsonb) returns boolean
language plpgsql immutable security invoker set search_path='' as $$
declare k text; field text; item jsonb;
begin
    if jsonb_typeof(p_locator) is distinct from 'object' then return false; end if;
    k:=p_locator->>'kind';
    foreach field in array array['cell_ids','item_ids','section_path'] loop
        if p_locator ? field then
            if jsonb_typeof(p_locator->field) is distinct from 'array' then return false; end if;
            for item in select value from jsonb_array_elements(p_locator->field) loop
                if jsonb_typeof(item)<>'string' or btrim(item#>>'{}')='' then return false; end if;
            end loop;
            if jsonb_array_length(p_locator->field)<>(select count(distinct value) from jsonb_array_elements(p_locator->field)) then return false; end if;
        end if;
    end loop;
    if k='section' then
        return coalesce(jsonb_array_length(p_locator->'section_path'),0)>0
            and coalesce(jsonb_array_length(p_locator->'cell_ids'),0)=0 and coalesce(jsonb_array_length(p_locator->'item_ids'),0)=0
            and coalesce(p_locator->>'ref',p_locator->>'table_index') is null;
    elsif k='table_cells' then
        return coalesce((p_locator->>'table_index') ~ '^[0-9]+$',false)
            and jsonb_typeof(p_locator->'table_index')='number' and coalesce(jsonb_array_length(p_locator->'cell_ids'),0)>0
            and coalesce(jsonb_array_length(p_locator->'item_ids'),0)=0 and coalesce(jsonb_array_length(p_locator->'section_path'),0)=0
            and p_locator->>'ref' is null;
    elsif k='text_item' then
        return coalesce(jsonb_array_length(p_locator->'item_ids'),0)>0 and coalesce(jsonb_array_length(p_locator->'cell_ids'),0)=0
            and coalesce(jsonb_array_length(p_locator->'section_path'),0)=0 and coalesce(p_locator->>'ref',p_locator->>'table_index') is null;
    elsif k='docling_ref' then
        return coalesce(btrim(p_locator->>'ref'),'')<>'' and jsonb_typeof(p_locator->'ref')='string'
            and coalesce(jsonb_array_length(p_locator->'cell_ids'),0)=0 and coalesce(jsonb_array_length(p_locator->'item_ids'),0)=0
            and coalesce(jsonb_array_length(p_locator->'section_path'),0)=0 and p_locator->>'table_index' is null;
    end if;
    return false;
end; $$;

-- A transaction snapshot older than publication cannot safely freeze evidence.
-- PostgREST uses READ COMMITTED; reject stronger stale-snapshot writers explicitly.
create function bintanong_private.publication_lock() returns void
language plpgsql volatile security invoker set search_path='' as $$
begin
    if current_setting('transaction_isolation') not in ('read committed','read uncommitted') then
        raise exception 'Publication writes require READ COMMITTED isolation' using errcode='23514';
    end if;
    perform pg_catalog.pg_advisory_xact_lock(420,4);
end; $$;

-- Every writer and publisher takes this lock before inspecting/changing data.
-- INVOKER functions keep the privileged role explicit; no RLS bypass helpers.
create function bintanong_private.validate_release(p_release_id text) returns void
language plpgsql security invoker set search_path='' as $$
declare rel public.knowledge_releases%rowtype; cfg public.embedding_sets%rowtype;
begin
    perform bintanong_private.publication_lock();
    select * into rel from public.knowledge_releases where release_id=p_release_id;
    if not found or rel.status='revoked' then
        raise exception 'Release is missing or revoked' using errcode='23514';
    end if;
    if rel.expected_chunk_count is null or rel.expected_document_version_count is null or rel.expected_rule_count is null
       or rel.expected_chunk_count<>(select count(*) from public.release_chunks where release_id=p_release_id)
       or rel.expected_document_version_count<>(select count(*) from public.release_document_versions where release_id=p_release_id)
       or rel.expected_rule_count<>(select count(*) from public.release_rules where release_id=p_release_id) then
        raise exception 'Release membership is incomplete' using errcode='23514';
    end if;
    select * into cfg from public.embedding_sets where embedding_set_id=rel.embedding_set_id;
    if not found or cfg.dimension<>1024 or cfg.normalization<>'l2'
       or cfg.model_id='' or cfg.model_revision !~ '^([0-9a-f]{40}|[0-9a-f]{64})$'
       or cfg.total_chunks<>(select count(*) from public.chunk_embeddings where embedding_set_id=rel.embedding_set_id) then
        raise exception 'Embedding configuration or manifest count is invalid' using errcode='23514';
    end if;
    if exists(select 1 from public.release_document_versions rdv
        join public.document_versions dv on dv.version_id=rdv.version_id
        where rdv.release_id=p_release_id and
        (dv.approval_state<>'approved' or dv.verification_state<>'verified' or dv.content_review_state<>'reviewed')) then
        raise exception 'Release contains unapproved document evidence' using errcode='23514';
    end if;
    if exists(select 1 from public.release_chunks rc join public.chunks c on c.chunk_id=rc.chunk_id
        left join public.document_versions dv on dv.version_id=c.version_id
        left join public.release_document_versions rdv on rdv.version_id=c.version_id and rdv.release_id=p_release_id
        left join public.chunk_embeddings ce on ce.chunk_id=c.chunk_id and ce.embedding_set_id=rel.embedding_set_id
        where rc.release_id=p_release_id and
        (not c.anchored or c.source_verification<>'verified' or c.content_review<>'reviewed'
         or dv.version_id is null or rdv.version_id is null
         or c.document_id is distinct from dv.document_id or c.edition_id is distinct from dv.edition_id
         or c.byte_sha256<>dv.byte_sha256 or ce.chunk_id is null or ce.chunk_content_hash<>c.content_hash
         or c.content_hash<>bintanong_private.content_hash(c.source_text,c.text)
         or (c.source_text is not null and bintanong_private.content_hash(c.source_text,c.source_text) <>
             (select bintanong_private.content_hash(string_agg(ss.text,' ' order by ss.span_order),string_agg(ss.text,' ' order by ss.span_order))
                 from public.source_spans ss where ss.chunk_id=c.chunk_id))
         or abs(extensions.vector_norm(ce.embedding)-1)>0.000001
         or not exists(select 1 from public.source_spans ss where ss.chunk_id=c.chunk_id)
         or exists(select 1 from public.source_spans ss where ss.chunk_id=c.chunk_id and
            (ss.version_id is distinct from c.version_id or ss.byte_sha256<>c.byte_sha256
             or (c.source_text is not null and (ss.text is null or btrim(ss.text)=''))
             or (c.source_text is null and ss.text is not null) or not bintanong_private.valid_locator(ss.locator)
             or ss.page is null or ss.page<1)))) then
        raise exception 'Chunk approval, source binding or embedding coverage is invalid' using errcode='23514';
    end if;
    if exists(select 1 from public.release_rules rr join public.policy_rules pr on pr.rule_id=rr.rule_id
        where rr.release_id=p_release_id and
        (pr.approval_state<>'authorized'
         or not exists(select 1 from public.rule_source_spans rss where rss.rule_id=pr.rule_id and rss.provenance_role='primary_source')
         or exists(select 1 from public.rule_source_spans rss join public.source_spans ss on ss.span_id=rss.span_id
            where rss.rule_id=pr.rule_id and not exists(select 1 from public.release_chunks rc
                where rc.release_id=p_release_id and rc.chunk_id=ss.chunk_id)))) then
        raise exception 'Rule approval or release provenance is invalid' using errcode='23514';
    end if;
end; $$;

create function bintanong_private.published_reference(p_table text,p_row jsonb) returns boolean
language plpgsql volatile security invoker set search_path='' as $$
begin
    case p_table
    when 'release_chunks','release_document_versions','release_rules' then
        return exists(select 1 from public.knowledge_releases kr where kr.release_id=p_row->>'release_id' and kr.published_at is not null);
    when 'chunks','source_spans' then
        return exists(select 1 from public.release_chunks rc join public.knowledge_releases kr using(release_id)
            where rc.chunk_id=p_row->>'chunk_id' and kr.published_at is not null);
    when 'chunk_embeddings' then
        return exists(select 1 from public.knowledge_releases kr
            where kr.embedding_set_id=p_row->>'embedding_set_id' and kr.published_at is not null);
    when 'embedding_sets' then
        return exists(select 1 from public.knowledge_releases kr where kr.embedding_set_id=p_row->>'embedding_set_id' and kr.published_at is not null);
    when 'document_versions' then
        return exists(select 1 from public.release_document_versions rdv join public.knowledge_releases kr using(release_id)
            where rdv.version_id=p_row->>'version_id' and kr.published_at is not null);
    when 'documents' then
        return exists(select 1 from public.document_versions dv join public.release_document_versions rdv using(version_id)
            join public.knowledge_releases kr using(release_id) where dv.document_id=p_row->>'document_id' and kr.published_at is not null);
    when 'policy_rules','rule_source_spans' then
        return exists(select 1 from public.release_rules rr join public.knowledge_releases kr using(release_id)
            where rr.rule_id=p_row->>'rule_id' and kr.published_at is not null);
    when 'curriculum_versions' then
        return exists(select 1 from public.release_document_versions rdv join public.knowledge_releases kr using(release_id)
            where rdv.version_id=p_row->>'document_version_id' and kr.published_at is not null);
    when 'courses' then
        return exists(select 1 from public.curriculum_versions cv join public.release_document_versions rdv on rdv.version_id=cv.document_version_id
            join public.knowledge_releases kr using(release_id) where cv.curriculum_version_id=p_row->>'curriculum_version_id' and kr.published_at is not null);
    when 'course_aliases' then
        return exists(select 1 from public.courses c join public.curriculum_versions cv using(curriculum_version_id)
            join public.release_document_versions rdv on rdv.version_id=cv.document_version_id join public.knowledge_releases kr using(release_id)
            where c.course_id=p_row->>'canonical_course_id' and kr.published_at is not null);
    when 'programs' then
        return exists(select 1 from public.curriculum_versions cv join public.release_document_versions rdv on rdv.version_id=cv.document_version_id
            join public.knowledge_releases kr using(release_id) where cv.program_code=p_row->>'program_code' and kr.published_at is not null);
    else raise exception 'Unknown protected table';
    end case;
end; $$;

create function bintanong_private.protect_published_data() returns trigger
language plpgsql security invoker set search_path='' as $$
declare prior jsonb; predicate text;
begin
    perform bintanong_private.publication_lock();
    if TG_OP='UPDATE' and to_jsonb(NEW)=to_jsonb(OLD) then return NEW; end if;
    if (TG_OP<>'INSERT' and bintanong_private.published_reference(TG_TABLE_NAME,to_jsonb(OLD)))
       or (TG_OP<>'DELETE' and bintanong_private.published_reference(TG_TABLE_NAME,to_jsonb(NEW))) then
        -- Exact unchanged inserts/upserts preserve the published row. Build an
        -- indexed primary-key lookup using trusted catalog column identifiers.
        if TG_OP='INSERT' then
            select string_agg(format('t.%I is not distinct from r.%I',a.attname,a.attname),' and ')
                into predicate from pg_catalog.pg_index i
                join pg_catalog.pg_attribute a on a.attrelid=i.indrelid and a.attnum=any(i.indkey)
                where i.indrelid=TG_RELID and i.indisprimary;
            execute format('select to_jsonb(t)-''created_at'' from %I.%I t cross join jsonb_populate_record(null::%I.%I,$1) r where %s',
                TG_TABLE_SCHEMA,TG_TABLE_NAME,TG_TABLE_SCHEMA,TG_TABLE_NAME,predicate) into prior using to_jsonb(NEW);
            if prior=to_jsonb(NEW)-'created_at' then return NEW; end if;
        end if;
        raise exception 'Published % is immutable; create new versioned evidence',TG_TABLE_NAME using errcode='55000';
    end if;
    if TG_OP='DELETE' then return OLD; end if;
    return NEW;
end; $$;

create function bintanong_private.lock_publication() returns trigger
language plpgsql security invoker set search_path='' as $$
begin
    -- Lock before row locks and use fresh VOLATILE queries after a wait.
    perform bintanong_private.publication_lock();
    if TG_OP='TRUNCATE' and exists(select 1 from public.knowledge_releases where published_at is not null) then
        raise exception 'Published evidence cannot be truncated' using errcode='55000';
    end if;
    return null;
end; $$;

do $$ declare t text; begin
    foreach t in array array['documents','document_versions','chunks','source_spans','embedding_sets','chunk_embeddings',
        'programs','curriculum_versions','courses','course_aliases','policy_rules','rule_source_spans',
        'release_document_versions','release_chunks','release_rules'] loop
        execute format('create trigger p4_protect_published before insert or update or delete on public.%I for each row execute function bintanong_private.protect_published_data()',t);
        execute format('create trigger p4_lock_publication before insert or update or delete or truncate on public.%I for each statement execute function bintanong_private.lock_publication()',t);
    end loop;
end; $$;

create function bintanong_private.protect_release() returns trigger
language plpgsql security invoker set search_path='' as $$
begin
    perform bintanong_private.publication_lock();
    if TG_OP='DELETE' then
        if OLD.published_at is not null then raise exception 'Published release is immutable' using errcode='55000'; end if;
        return OLD;
    end if;
    if TG_OP='INSERT' and (NEW.status<>'draft' or NEW.published_at is not null) then
        raise exception 'New release must be draft' using errcode='23514';
    end if;
    if TG_OP='UPDATE' then
        if OLD.published_at is not null and (to_jsonb(NEW)-'status') is distinct from (to_jsonb(OLD)-'status') then
            raise exception 'Published release metadata is immutable' using errcode='55000';
        end if;
        if OLD.status='revoked' and NEW.status<>'revoked' then raise exception 'Revoked release cannot be restored' using errcode='23514'; end if;
        if NEW.status='active' and OLD.status<>'active' then
            perform bintanong_private.validate_release(OLD.release_id);
            if NEW.published_at is null then raise exception 'Publication timestamp is required' using errcode='23514'; end if;
        elsif OLD.published_at is null and (NEW.published_at is not null or NEW.status='superseded') then
            raise exception 'Draft cannot claim publication' using errcode='23514';
        end if;
    end if;
    return NEW;
end; $$;
create trigger p4_protect_release before insert or update or delete on public.knowledge_releases
    for each row execute function bintanong_private.protect_release();
create trigger p4_lock_release before insert or update or delete or truncate on public.knowledge_releases
    for each statement execute function bintanong_private.lock_publication();

create function bintanong_private.protect_active_pointer() returns trigger
language plpgsql security invoker set search_path='' as $$
begin
    perform bintanong_private.publication_lock();
    if TG_OP='DELETE' then return OLD; end if;
    if not exists(select 1 from public.knowledge_releases kr where kr.release_id=NEW.release_id
        and kr.status='active' and kr.published_at is not null) then
        raise exception 'Pointer requires a published active release' using errcode='23514';
    end if;
    perform bintanong_private.validate_release(NEW.release_id);
    return NEW;
end; $$;
create trigger p4_protect_active_pointer before insert or update or delete on public.active_release
    for each row execute function bintanong_private.protect_active_pointer();
create trigger p4_lock_active_pointer before insert or update or delete or truncate on public.active_release
    for each statement execute function bintanong_private.lock_publication();

create or replace function public.activate_knowledge_release(p_release_id text,p_actor text default 'system')
returns void language plpgsql security invoker set search_path='' as $$
begin
    perform bintanong_private.publication_lock();
    perform bintanong_private.validate_release(p_release_id);
    update public.knowledge_releases set status='superseded' where status='active' and release_id<>p_release_id;
    update public.knowledge_releases set status='active',published_at=coalesce(published_at,now()),
        published_by=coalesce(published_by,p_actor) where release_id=p_release_id;
    insert into public.active_release(id,release_id,activated_at,activated_by) values(1,p_release_id,now(),p_actor)
        on conflict(id) do update set release_id=excluded.release_id,activated_at=excluded.activated_at,activated_by=excluded.activated_by;
end; $$;

create or replace function public.rollback_knowledge_release(p_target_release_id text,p_actor text default 'system')
returns void language plpgsql security invoker set search_path='' as $$
begin
    perform bintanong_private.publication_lock();
    if not exists(select 1 from public.knowledge_releases where release_id=p_target_release_id
        and status in ('active','superseded') and published_at is not null) then
        raise exception 'Rollback requires a previously published release' using errcode='23514';
    end if;
    perform public.activate_knowledge_release(p_target_release_id,p_actor);
end; $$;

create function public.create_knowledge_release(p_release_id text,p_release_version text,p_description text,
    p_embedding_set_id text,p_chunk_ids text[],p_document_version_ids text[],p_rule_ids text[] default '{}')
returns void language plpgsql security invoker set search_path='' as $$
begin
    perform bintanong_private.publication_lock();
    if cardinality(p_chunk_ids) is null or cardinality(p_chunk_ids)=0
       or cardinality(p_document_version_ids) is null or cardinality(p_document_version_ids)=0
       or p_rule_ids is null
       or exists(select 1 from unnest(p_chunk_ids || p_document_version_ids || p_rule_ids) x where x is null)
       or cardinality(p_chunk_ids)<>(select count(distinct x) from unnest(p_chunk_ids) x)
       or cardinality(p_document_version_ids)<>(select count(distinct x) from unnest(p_document_version_ids) x)
       or cardinality(p_rule_ids)<>(select count(distinct x) from unnest(p_rule_ids) x) then
        raise exception 'Membership lists must be nonempty where required, unique and nonnull' using errcode='23514';
    end if;
    insert into public.knowledge_releases(release_id,release_version,description,embedding_set_id,
        expected_chunk_count,expected_document_version_count,expected_rule_count)
        values(p_release_id,p_release_version,p_description,p_embedding_set_id,
            cardinality(p_chunk_ids),cardinality(p_document_version_ids),cardinality(p_rule_ids));
    insert into public.release_chunks select p_release_id,x from unnest(p_chunk_ids) x;
    insert into public.release_document_versions select p_release_id,x from unnest(p_document_version_ids) x;
    insert into public.release_rules select p_release_id,x from unnest(p_rule_ids) x;
end; $$;

create function public.load_chunk_batch(p_chunks jsonb,p_spans jsonb default '[]') returns integer
language plpgsql security invoker set search_path='' as $$
declare c public.chunks%rowtype; prior jsonb; proposed jsonb; n integer:=0;
begin
    perform bintanong_private.publication_lock();
    if jsonb_typeof(p_chunks) is distinct from 'array' or jsonb_typeof(p_spans) is distinct from 'array'
       or jsonb_array_length(p_chunks)<>(select count(distinct x->>'chunk_id') from jsonb_array_elements(p_chunks) x)
       or exists(select 1 from jsonb_array_elements(p_spans) s where not exists(
            select 1 from jsonb_array_elements(p_chunks) item where item->>'chunk_id'=s->>'chunk_id')) then
        raise exception 'Invalid chunk/span batch identities' using errcode='23514';
    end if;
    for c in select * from jsonb_populate_recordset(null::public.chunks,p_chunks) loop
        if exists(select 1 from public.chunks old where old.chunk_id=c.chunk_id and
            (old.content_hash<>c.content_hash or old.byte_sha256<>c.byte_sha256 or old.text<>c.text
             or old.source_text is distinct from c.source_text or old.version_id is distinct from c.version_id
             or old.document_id is distinct from c.document_id)) then
            raise exception 'Existing chunk identity conflicts with imported content' using errcode='23514';
        end if;
        insert into public.chunks(chunk_id,chunk_type,chunker_version,document_id,version_id,edition_id,byte_sha256,
            anchored,source_verification,content_review,text,source_text,section_path,scope,content_hash,token_count,source_label,type_fields)
        values(c.chunk_id,c.chunk_type,c.chunker_version,c.document_id,c.version_id,c.edition_id,c.byte_sha256,
            c.anchored,c.source_verification,c.content_review,c.text,c.source_text,c.section_path,c.scope,c.content_hash,c.token_count,c.source_label,c.type_fields)
        on conflict(chunk_id) do update set chunk_type=excluded.chunk_type,chunker_version=excluded.chunker_version,
            document_id=excluded.document_id,version_id=excluded.version_id,edition_id=excluded.edition_id,
            byte_sha256=excluded.byte_sha256,anchored=excluded.anchored,source_verification=excluded.source_verification,
            content_review=excluded.content_review,text=excluded.text,source_text=excluded.source_text,
            section_path=excluded.section_path,scope=excluded.scope,content_hash=excluded.content_hash,
            token_count=excluded.token_count,source_label=excluded.source_label,type_fields=excluded.type_fields;
        select coalesce(jsonb_agg(to_jsonb(s)-'span_id'-'created_at' order by to_jsonb(s)-'span_id'-'created_at'),'[]')
            into prior from public.source_spans s where s.chunk_id=c.chunk_id;
        select coalesce(jsonb_agg(to_jsonb(s)-'span_id'-'created_at' order by to_jsonb(s)-'span_id'-'created_at'),'[]')
            into proposed from jsonb_populate_recordset(null::public.source_spans,p_spans) s where s.chunk_id=c.chunk_id;
        if prior is distinct from proposed then
            delete from public.source_spans where chunk_id=c.chunk_id;
            insert into public.source_spans(span_id,chunk_id,span_order,byte_sha256,version_id,page,printed_page_label,locator,text,
                bbox,bbox_origin,page_size,extraction)
            select coalesce(s.span_id,gen_random_uuid()),s.chunk_id,s.span_order,s.byte_sha256,s.version_id,s.page,s.printed_page_label,
                s.locator,s.text,s.bbox,s.bbox_origin,s.page_size,s.extraction
            from jsonb_populate_recordset(null::public.source_spans,p_spans) s where s.chunk_id=c.chunk_id;
        end if;
        n:=n+1;
    end loop;
    return n;
end; $$;

create function public.load_embedding_set(p_record jsonb) returns text
language plpgsql security invoker set search_path='' as $$
declare c public.embedding_sets%rowtype;
begin
    perform bintanong_private.publication_lock();
    select * into c from jsonb_populate_record(null::public.embedding_sets,p_record);
    if exists(select 1 from public.embedding_sets old where old.embedding_set_id=c.embedding_set_id and
        (old.model_id<>c.model_id or old.model_revision<>c.model_revision or old.normalization<>c.normalization
         or old.dimension<>c.dimension or old.prompt_fingerprint<>c.prompt_fingerprint
         or old.preprocessing_fingerprint<>c.preprocessing_fingerprint or old.tokenizer_fingerprint<>c.tokenizer_fingerprint)) then
        raise exception 'Existing embedding set has different configuration' using errcode='23514';
    end if;
    insert into public.embedding_sets(embedding_set_id,schema_version,model_id,model_revision,dimension,normalization,
        prompt_fingerprint,preprocessing_fingerprint,tokenizer_fingerprint,total_chunks)
    values(c.embedding_set_id,c.schema_version,c.model_id,c.model_revision,c.dimension,c.normalization,
        c.prompt_fingerprint,c.preprocessing_fingerprint,c.tokenizer_fingerprint,c.total_chunks)
    on conflict(embedding_set_id) do update set total_chunks=excluded.total_chunks;
    return c.embedding_set_id;
end; $$;

create function public.load_embedding_batch(p_records jsonb,p_embedding_set_id text) returns integer
language plpgsql security invoker set search_path='' as $$
declare c public.chunk_embeddings%rowtype; n integer:=0;
begin
    perform bintanong_private.publication_lock();
    if jsonb_typeof(p_records) is distinct from 'array' then raise exception 'Embedding batch must be an array' using errcode='23514'; end if;
    for c in select * from jsonb_populate_recordset(null::public.chunk_embeddings,p_records) loop
        if c.embedding_set_id is distinct from p_embedding_set_id
           or not exists(select 1 from public.chunks ch where ch.chunk_id=c.chunk_id and ch.content_hash=c.chunk_content_hash)
           or abs(extensions.vector_norm(c.embedding)-1)>0.000001 then
            raise exception 'Embedding does not match chunk, set or normalization' using errcode='23514';
        end if;
        insert into public.chunk_embeddings(chunk_id,embedding_set_id,chunk_content_hash,embedding,token_count)
        values(c.chunk_id,c.embedding_set_id,c.chunk_content_hash,c.embedding,c.token_count)
        on conflict(chunk_id,embedding_set_id) do update set chunk_content_hash=excluded.chunk_content_hash,
            embedding=excluded.embedding,token_count=excluded.token_count;
        n:=n+1;
    end loop;
    return n;
end; $$;

create function public.load_knowledge_batch(p_embedding_set jsonb,p_chunks jsonb,p_spans jsonb,p_embeddings jsonb)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare set_id text; chunks_loaded integer; embeddings_loaded integer; already_present integer;
begin
    perform bintanong_private.publication_lock();
    set_id:=p_embedding_set->>'embedding_set_id';
    select count(*) into already_present from public.chunk_embeddings ce
        where ce.embedding_set_id=set_id and ce.chunk_id in(select x->>'chunk_id' from jsonb_array_elements(p_embeddings) x);
    perform public.load_embedding_set(p_embedding_set);
    chunks_loaded:=public.load_chunk_batch(p_chunks,p_spans);
    embeddings_loaded:=public.load_embedding_batch(p_embeddings,set_id);
    return jsonb_build_object('embedding_set_id',set_id,'total_chunks_loaded',chunks_loaded,
        'total_embeddings_loaded',embeddings_loaded,'total_spans_loaded',jsonb_array_length(p_spans),
        'total_documents_loaded',0,'duplicate_avoided_count',already_present);
end; $$;

create or replace function public.match_chunks(query_embedding extensions.vector(1024),
    match_threshold double precision default 0.0,match_count integer default 10)
returns table(chunk_id text,similarity double precision,text text,source_text text,
    section_path text[],scope text[],chunk_type text)
language sql stable security invoker set search_path=public,extensions as $$
    select c.chunk_id,(1-(ce.embedding <=> query_embedding)) as similarity,c.text,
        coalesce(c.source_text,c.text),c.section_path,c.scope,c.chunk_type
    from public.chunks c join public.chunk_embeddings ce on ce.chunk_id=c.chunk_id
    where (1-(ce.embedding <=> query_embedding))>=match_threshold
    order by ce.embedding <=> query_embedding asc limit match_count;
$$;

revoke execute on all functions in schema bintanong_private from public,anon,authenticated;
grant execute on all functions in schema bintanong_private to service_role;
revoke execute on function public.create_knowledge_release from public,anon,authenticated;
grant execute on function public.create_knowledge_release to service_role;
revoke execute on function public.load_chunk_batch,public.load_embedding_set,public.load_embedding_batch,public.load_knowledge_batch from public,anon,authenticated;
grant execute on function public.load_chunk_batch,public.load_embedding_set,public.load_embedding_batch,public.load_knowledge_batch to service_role;
revoke execute on function public.activate_knowledge_release from public,anon,authenticated;
revoke execute on function public.rollback_knowledge_release from public,anon,authenticated;
grant execute on function public.activate_knowledge_release to service_role;
grant execute on function public.rollback_knowledge_release to service_role;
notify pgrst, 'reload schema';
