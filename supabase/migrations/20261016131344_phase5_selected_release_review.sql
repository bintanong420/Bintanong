-- Exact selected content review, independent of whole-source authority.
create table public.selected_release_reviews (
    review_scope_id text primary key check (review_scope_id ~ '^[0-9a-f]{64}$'),
    receipt jsonb not null check (jsonb_typeof(receipt)='object'),
    created_at timestamptz not null default now()
);
alter table public.selected_release_reviews enable row level security;
revoke all on public.selected_release_reviews from public,anon,authenticated,service_role;
grant select,insert on public.selected_release_reviews to service_role;
create policy p5_selected_review_runtime_denial on public.selected_release_reviews
    as restrictive for all to anon,authenticated using(false) with check(false);
create trigger p5_selected_review_immutable before update or delete or truncate
    on public.selected_release_reviews for each statement execute function bintanong_private.partial_review_immutable();
create trigger p5_selected_review_lock before insert on public.selected_release_reviews
    for each statement execute function bintanong_private.lock_publication();
alter table public.knowledge_releases add column review_scope_id text
    references public.selected_release_reviews(review_scope_id) on delete restrict on update restrict;
create index p5_release_review_scope on public.knowledge_releases(review_scope_id);

create function bintanong_private.validate_selected_review(p_receipt jsonb) returns void
language plpgsql volatile security invoker set search_path='' as $$
declare d jsonb; src jsonb; c jsonb; s jsonb; f jsonb; x jsonb; old_receipt jsonb;
    dv public.document_versions%rowtype; row_chunk public.chunks%rowtype;
    snap jsonb; span_rows jsonb; at_time timestamptz; previous text; version_ids text[] := '{}';
    chunk_ids text[] := '{}'; used_versions text[] := '{}'; n integer; i integer;
begin
    perform bintanong_private.publication_lock();
    if not bintanong_private.partial_review_object(p_receipt,array[
        'receipt_format','review_scope_id','supported_scope','decision','sources','chunks'])
       or p_receipt->'receipt_format' is distinct from '"selected-release-review-v1"'::jsonb
       or p_receipt->'supported_scope' is distinct from '"undergraduate_academic_affairs"'::jsonb
       or jsonb_typeof(p_receipt->'review_scope_id') is distinct from 'string'
       or p_receipt->>'review_scope_id' !~ '^[0-9a-f]{64}$' then
        raise exception 'Closed undergraduate selected review required' using errcode='23514';
    end if;
    d := p_receipt->'decision';
    if not bintanong_private.partial_review_object(d,array['evidence_id','reviewer_label','compiler_label',
        'recorded_at','timestamp_meaning','owner_response','decision_document','acceptance_record_sha256',
        'coverage_inventory_sha256','draft_chunks_sha256']) then
        raise exception 'Closed selected-review decision required' using errcode='23514';
    end if;
    for x in select value from jsonb_each(d) loop
        if jsonb_typeof(x) is distinct from 'string' or x#>>'{}' !~ '[^[:space:]]' then
            raise exception 'Nonblank selected-review decision text required' using errcode='23514';
        end if;
    end loop;
    if d->>'acceptance_record_sha256' !~ '^[0-9a-f]{64}$'
       or d->>'coverage_inventory_sha256' !~ '^[0-9a-f]{64}$'
       or d->>'draft_chunks_sha256' !~ '^[0-9a-f]{64}$'
       or d->>'decision_document' ~ '(^/|:|\\|(^|/)\.\.?(/|$)|//|/$)' then
        raise exception 'Exact decision digests and repository path required' using errcode='23514';
    end if;
    at_time := bintanong_private.partial_review_time(d->>'recorded_at');
    if jsonb_typeof(p_receipt->'sources') is distinct from 'array'
       or jsonb_typeof(p_receipt->'chunks') is distinct from 'array'
       or jsonb_array_length(p_receipt->'sources')=0 or jsonb_array_length(p_receipt->'chunks')=0 then
        raise exception 'Nonempty selected source/chunk coverage required' using errcode='23514';
    end if;
    previous := null;
    for src in select value from jsonb_array_elements(p_receipt->'sources') loop
        if not bintanong_private.partial_review_object(src,array['version_id','source_sha256','partial_review_evidence_id'])
           or jsonb_typeof(src->'version_id') is distinct from 'string' or src->>'version_id' !~ '^ver-[A-Za-z0-9_.:-]+$'
           or jsonb_typeof(src->'source_sha256') is distinct from 'string' or src->>'source_sha256' !~ '^[0-9a-f]{64}$'
           or jsonb_typeof(src->'partial_review_evidence_id') is distinct from 'string'
           or src->>'partial_review_evidence_id' !~ '[^[:space:]]'
           or (previous is not null and src->>'version_id' collate "C" <= previous collate "C") then
            raise exception 'Sorted distinct C1 source references required' using errcode='23514';
        end if;
        previous := src->>'version_id'; version_ids := array_append(version_ids,previous);
        select * into dv from public.document_versions where version_id=previous;
        select receipt into old_receipt from public.source_partial_reviews
            where version_id=previous and evidence_id=src->>'partial_review_evidence_id';
        if dv.version_id is null or old_receipt is null
           or dv.byte_sha256 is distinct from src->>'source_sha256'
           or old_receipt->'source_sha256' is distinct from src->'source_sha256'
           or old_receipt#>>'{evidence,evidence_id}' is distinct from src->>'partial_review_evidence_id'
           or dv.content_review_state not in ('partially_reviewed','reviewed')
           or not coalesce(dv.source_register->'evidence' @> jsonb_build_array(old_receipt->'evidence'),false)
           or at_time < bintanong_private.partial_review_time(old_receipt#>>'{evidence,recorded_at}')
           or exists(select 1 from jsonb_array_elements(old_receipt->'source_events') e
               where at_time < bintanong_private.partial_review_time(e->>'recorded_at')) then
            raise exception 'Current source and ordered original C1 review required' using errcode='23514';
        end if;
    end loop;
    previous := null;
    for c in select value from jsonb_array_elements(p_receipt->'chunks') loop
        if not bintanong_private.partial_review_object(c,array['chunk_id','content_hash','type_fields','spans'])
           or jsonb_typeof(c->'chunk_id') is distinct from 'string' or c->>'chunk_id' !~ '^[0-9a-f]{64}$'
           or jsonb_typeof(c->'content_hash') is distinct from 'string' or c->>'content_hash' !~ '^[0-9a-f]{64}$'
           or (previous is not null and c->>'chunk_id' collate "C" <= previous collate "C")
           or jsonb_typeof(c->'spans') is distinct from 'array' or jsonb_array_length(c->'spans')=0
           or jsonb_typeof(c->'type_fields') is distinct from 'object' then
            raise exception 'Sorted distinct selected chunk snapshots required' using errcode='23514';
        end if;
        previous := c->>'chunk_id'; chunk_ids := array_append(chunk_ids,previous);
        select * into row_chunk from public.chunks where chunk_id=previous;
        select value into src from jsonb_array_elements(p_receipt->'sources') where value->>'version_id'=row_chunk.version_id;
        if row_chunk.chunk_id is null or src is null then
            raise exception 'Declared selected source required' using errcode='23514';
        end if;
        select * into dv from public.document_versions where version_id=row_chunk.version_id;
        select receipt into old_receipt from public.source_partial_reviews where version_id=row_chunk.version_id
            and evidence_id=src->>'partial_review_evidence_id';
        select value into snap from jsonb_array_elements(old_receipt->'chunks') where value->'chunk_id'=c->'chunk_id';
        select jsonb_agg(to_jsonb(v)-'span_id'-'created_at' order by span_order) into span_rows
            from public.source_spans v where v.chunk_id=row_chunk.chunk_id;
        if snap is distinct from c or row_chunk.byte_sha256 is distinct from dv.byte_sha256
           or row_chunk.document_id is distinct from dv.document_id or row_chunk.edition_id is distinct from dv.edition_id
           or row_chunk.byte_sha256 is distinct from src->>'source_sha256'
           or row_chunk.content_hash is distinct from c->>'content_hash'
           or row_chunk.content_hash is distinct from bintanong_private.content_hash(row_chunk.source_text,row_chunk.text)
           or row_chunk.type_fields is distinct from c->'type_fields' or span_rows is distinct from c->'spans'
           or jsonb_typeof(c#>'{type_fields,applicability_basis_ref}') is distinct from 'string'
           or c#>>'{type_fields,applicability_basis_ref}' !~ '[^[:space:]]' then
            raise exception 'Selected C1/current content or source snapshot differs' using errcode='23514';
        end if;
        used_versions := array_append(used_versions,row_chunk.version_id);
        n := jsonb_array_length(c->'spans'); i := 0;
        if jsonb_typeof(c#>'{type_fields,field_associations}') is distinct from 'array'
           or jsonb_typeof(c#>'{type_fields,required_neighbor_chunk_ids}') is distinct from 'array' then
            raise exception 'Complete selected fields and neighbors required' using errcode='23514';
        end if;
        for f in select value from jsonb_array_elements(c#>'{type_fields,field_associations}') loop
            if jsonb_typeof(f->'span_indexes') is distinct from 'array'
               or not exists(select 1 from jsonb_array_elements(old_receipt->'source_events') e
                   where e->'event_sha256'=f->'event_sha256') then
                raise exception 'Bound selected field event required' using errcode='23514';
            end if;
            for x in select value from jsonb_array_elements(f->'span_indexes') loop
                if jsonb_typeof(x) is distinct from 'number' or x#>>'{}' <> i::text then
                    raise exception 'Complete ordered selected span coverage required' using errcode='23514';
                end if;
                i := i+1;
            end loop;
        end loop;
        if i<>n then raise exception 'Uncovered selected source span' using errcode='23514'; end if;
    end loop;
    if not version_ids <@ used_versions then raise exception 'Unused selected source' using errcode='23514'; end if;
    for c in select value from jsonb_array_elements(p_receipt->'chunks') loop
        for x in select value from jsonb_array_elements(c#>'{type_fields,required_neighbor_chunk_ids}') loop
            if jsonb_typeof(x) is distinct from 'string' or not (x#>>'{}'=any(chunk_ids))
               or not exists(select 1 from jsonb_array_elements(p_receipt->'chunks') neighbor
                   where neighbor->'chunk_id'=x and neighbor#>'{spans,0,version_id}'=c#>'{spans,0,version_id}') then
                raise exception 'Complete same-source selected neighbor required' using errcode='23514';
            end if;
        end loop;
    end loop;
end; $$;

create function public.record_selected_release_review(p_receipt jsonb) returns jsonb
language plpgsql volatile security invoker set search_path='' as $$
declare saved jsonb;
begin
    perform bintanong_private.validate_selected_review(p_receipt);
    select receipt into saved from public.selected_release_reviews where review_scope_id=p_receipt->>'review_scope_id';
    if saved is not null then
        if saved is distinct from p_receipt then raise exception 'Selected review identity conflict' using errcode='23514'; end if;
        return saved;
    end if;
    insert into public.selected_release_reviews(review_scope_id,receipt) values(p_receipt->>'review_scope_id',p_receipt);
    return p_receipt;
end; $$;

create function bintanong_private.validate_selected_release(p_release_id text,p_scope_id text) returns void
language plpgsql volatile security invoker set search_path='' as $$
declare receipt jsonb;
begin
    select r.receipt into receipt from public.selected_release_reviews r where review_scope_id=p_scope_id;
    perform bintanong_private.validate_selected_review(receipt);
    if exists(select 1 from public.release_rules where release_id=p_release_id)
       or (select count(*) from public.release_chunks where release_id=p_release_id)<>jsonb_array_length(receipt->'chunks')
       or (select count(*) from public.release_document_versions where release_id=p_release_id)<>jsonb_array_length(receipt->'sources')
       or exists(select 1 from public.release_chunks rc where rc.release_id=p_release_id and not exists(
           select 1 from jsonb_array_elements(receipt->'chunks') c where c->>'chunk_id'=rc.chunk_id))
       or exists(select 1 from public.release_document_versions rv where rv.release_id=p_release_id and not exists(
           select 1 from jsonb_array_elements(receipt->'sources') s where s->>'version_id'=rv.version_id)) then
        raise exception 'Exact selected release membership required' using errcode='23514';
    end if;
end; $$;

create function public.bind_selected_release_review(p_release_id text,p_review_scope_id text) returns jsonb
language plpgsql volatile security invoker set search_path='' as $$
declare rel public.knowledge_releases%rowtype;
begin
    perform bintanong_private.publication_lock();
    select * into rel from public.knowledge_releases where release_id=p_release_id for update;
    if not found or rel.status<>'draft' or rel.published_at is not null
       or (rel.review_scope_id is not null and rel.review_scope_id is distinct from p_review_scope_id) then
        raise exception 'Unpublished selected draft and unchanged binding required' using errcode='23514';
    end if;
    perform bintanong_private.validate_selected_release(p_release_id,p_review_scope_id);
    update public.knowledge_releases set review_scope_id=p_review_scope_id where release_id=p_release_id;
    return jsonb_build_object('release_id',p_release_id,'review_scope_id',p_review_scope_id);
end; $$;

revoke all on function bintanong_private.validate_selected_review(jsonb),
    bintanong_private.validate_selected_release(text,text),public.record_selected_release_review(jsonb),
    public.bind_selected_release_review(text,text) from public,anon,authenticated;
grant execute on function bintanong_private.validate_selected_review(jsonb),
    bintanong_private.validate_selected_release(text,text),public.record_selected_release_review(jsonb),
    public.bind_selected_release_review(text,text) to service_role;

-- Acyclic runtime dependencies; administrative review bodies are never read.
alter policy p4_document_versions_select_active on public.document_versions using (
    approval_state='approved' and verification_state='verified'
    and exists(select 1 from public.release_document_versions rdv
        join public.knowledge_releases kr using(release_id)
        where rdv.version_id=document_versions.version_id
          and (document_versions.content_review_state='reviewed'
            or (document_versions.content_review_state='partially_reviewed' and kr.review_scope_id is not null))));
alter policy p4_chunks_select_active on public.chunks using (
    anchored and source_verification='verified'
    and exists(select 1 from public.release_chunks rc join public.knowledge_releases kr using(release_id)
        where rc.chunk_id=chunks.chunk_id
          and (chunks.content_review='reviewed'
            or (chunks.content_review='partially_reviewed' and kr.review_scope_id is not null)))
    and exists(select 1 from public.document_versions dv where dv.version_id=chunks.version_id
        and dv.document_id=chunks.document_id and dv.byte_sha256=chunks.byte_sha256
        and dv.edition_id=chunks.edition_id and dv.content_review_state=chunks.content_review));

create or replace function bintanong_private.validate_release(p_release_id text) returns void
language plpgsql security invoker set search_path='' as $$
declare rel public.knowledge_releases%rowtype; cfg public.embedding_sets%rowtype; selected boolean;
begin
    perform bintanong_private.publication_lock();
    select * into rel from public.knowledge_releases where release_id=p_release_id;
    if not found or rel.status='revoked' then
        raise exception 'Release is missing or revoked' using errcode='23514';
    end if;
    selected := rel.review_scope_id is not null;
    if selected then perform bintanong_private.validate_selected_release(p_release_id,rel.review_scope_id); end if;
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
        (dv.approval_state<>'approved' or dv.verification_state<>'verified' or (dv.content_review_state<>'reviewed' and (not selected or dv.content_review_state<>'partially_reviewed')))) then
        raise exception 'Release contains unapproved document evidence' using errcode='23514';
    end if;
    if exists(select 1 from public.release_chunks rc join public.chunks c on c.chunk_id=rc.chunk_id
        left join public.document_versions dv on dv.version_id=c.version_id
        left join public.release_document_versions rdv on rdv.version_id=c.version_id and rdv.release_id=p_release_id
        left join public.chunk_embeddings ce on ce.chunk_id=c.chunk_id and ce.embedding_set_id=rel.embedding_set_id
        where rc.release_id=p_release_id and
        (not c.anchored or c.source_verification<>'verified' or (c.content_review<>'reviewed' and (not selected or c.content_review<>'partially_reviewed'))
         or c.content_review<>dv.content_review_state
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
