-- Shared validation retains original C1 semantics; supplementary reviews do not update source state.
create function bintanong_private.validate_partial_review_receipt(
    p_expected_register jsonb,p_receipt jsonb,p_require_initial boolean,
    p_allow_source_blanks boolean default false) returns void
language plpgsql immutable security invoker set search_path='' as $$
declare ev jsonb; e jsonb; c jsonb; f jsonb; s jsonb; fields jsonb; x jsonb;
    key text; source_hash text; evidence_at timestamptz; span_number integer;
    event_ids text[] := '{}'; used_events text[] := '{}'; chunk_ids text[] := '{}';
begin
    if jsonb_typeof(p_expected_register) is distinct from 'object'
       or not bintanong_private.partial_review_object(p_receipt,array[
            'receipt_format','version_id','source_sha256','acquisition_locators','evidence',
            'reviewer_label','compiler_label','review_scope','source_events','chunks']) then
        raise exception 'Closed C1 source and receipt objects required' using errcode='23514';
    end if;
    source_hash := p_expected_register->>'byte_sha256';
    if p_receipt->>'receipt_format' is distinct from 'selected-source-partial-review-v1'
       or p_receipt->>'review_scope' is distinct from 'selected_fields'
       or jsonb_typeof(p_receipt->'version_id') is distinct from 'string'
       or p_receipt->'version_id' is distinct from p_expected_register->'version_id'
       or jsonb_typeof(p_receipt->'source_sha256') is distinct from 'string'
       or p_receipt->'source_sha256' is distinct from p_expected_register->'byte_sha256'
       or jsonb_typeof(p_receipt->'acquisition_locators') is distinct from 'array'
       or p_receipt->'acquisition_locators' is distinct from p_expected_register->'acquisition_locators' then
        raise exception 'Exact C1 source binding required' using errcode='23514';
    end if;
    foreach key in array array['reviewer_label','compiler_label'] loop
        if jsonb_typeof(p_receipt->key) is distinct from 'string' or p_receipt->>key !~ '[^[:space:]]' then
            raise exception 'Nonblank C1 labels required' using errcode='23514';
        end if;
    end loop;
    ev := p_receipt->'evidence';
    if not bintanong_private.partial_review_object(ev,array['evidence_id','kind','recorded_by','recorded_at','authorization_ref'])
       or jsonb_typeof(ev->'evidence_id') is distinct from 'string' or ev->>'evidence_id' !~ '[^[:space:]]'
       or ev->'kind' is distinct from '"content_review_record"'::jsonb
       or ev->'recorded_by' is distinct from '"reviewer"'::jsonb
       or jsonb_typeof(ev->'recorded_at') is distinct from 'string'
       or ev->'authorization_ref' is distinct from 'null'::jsonb then
        raise exception 'Distinct C1 reviewer evidence required' using errcode='23514';
    end if;
    evidence_at := bintanong_private.partial_review_time(ev->>'recorded_at');
    if p_require_initial then
    if p_expected_register#>>'{acquisition_state,state}' is distinct from 'observed'
       or jsonb_typeof(p_expected_register#>'{acquisition_state,evidence_ref}') is distinct from 'string'
       or p_expected_register->'approval_id' is distinct from 'null'::jsonb
       or jsonb_typeof(p_expected_register->'evidence') is distinct from 'array' then
        raise exception 'C1 requires observed acquisition and initial authority states' using errcode='23514';
    end if;
    foreach key in array array['verification_state','approval_state','content_review_state'] loop
        if p_expected_register->key is distinct from jsonb_build_object('state',
            case when key='approval_state' then 'not_requested' else 'pending' end,'evidence_ref',null) then
            raise exception 'C1 requires initial review and authority states' using errcode='23514';
        end if;
    end loop;
    end if;
    if exists(select 1 from jsonb_array_elements(p_expected_register->'evidence') v where v->>'evidence_id'=ev->>'evidence_id') then
        raise exception 'Duplicate C1 evidence ID' using errcode='23514';
    end if;
    foreach key in array array['source_events','chunks'] loop
        if jsonb_typeof(p_receipt->key) is distinct from 'array' or jsonb_array_length(p_receipt->key)=0 then
            raise exception 'Nonempty C1 events and chunks required' using errcode='23514';
        end if;
    end loop;
    for e in select value from jsonb_array_elements(p_receipt->'source_events') loop
        if not bintanong_private.partial_review_object(e,array['event_sha256','representation','source_sha256',
                'owner_event_sha256','actual_owner_label','recorded_at','timestamp_meaning']) then
            raise exception 'Closed source-bound C1 event required' using errcode='23514';
        end if;
        for key in select jsonb_object_keys(e) loop
            if jsonb_typeof(e->key) is distinct from 'string' or e->>key !~ '[^[:space:]]' then
                raise exception 'Typed C1 event members required' using errcode='23514';
            end if;
        end loop;
        if e->>'event_sha256' !~ '^[0-9a-f]{64}$' or e->>'owner_event_sha256' !~ '^[0-9a-f]{64}$'
           or e->>'source_sha256' is distinct from source_hash
           or e->>'event_sha256'=any(event_ids)
           or e->>'representation' not in ('original_file_bytes','existing_indent2_encoded_event_object')
           or bintanong_private.partial_review_time(e->>'recorded_at') > evidence_at then
            raise exception 'Distinct ordered source-bound C1 event required' using errcode='23514';
        end if;
        event_ids := array_append(event_ids,e->>'event_sha256');
    end loop;
    if not exists(select 1 from jsonb_array_elements(p_receipt->'source_events') v
        where v->'actual_owner_label'=p_receipt->'reviewer_label') then
        raise exception 'Original bound reviewer label required' using errcode='23514';
    end if;
    for c in select value from jsonb_array_elements(p_receipt->'chunks') loop
        if not bintanong_private.partial_review_object(c,array['chunk_id','content_hash','type_fields','spans'])
           or jsonb_typeof(c->'chunk_id') is distinct from 'string' or c->>'chunk_id' !~ '^[0-9a-f]{64}$'
           or jsonb_typeof(c->'content_hash') is distinct from 'string' or c->>'content_hash' !~ '^[0-9a-f]{64}$'
           or c->>'chunk_id'=any(chunk_ids)
           or jsonb_typeof(c->'spans') is distinct from 'array' or jsonb_array_length(c->'spans')=0 then
            raise exception 'Distinct complete C1 chunk snapshot required' using errcode='23514';
        end if;
        chunk_ids := array_append(chunk_ids,c->>'chunk_id');
        fields := c->'type_fields';
        if jsonb_typeof(fields) is distinct from 'object'
           or not fields ?& array['reading_id','context_format','applicability_basis_ref','field_associations','source_limits','required_neighbor_chunk_ids']
           or jsonb_typeof(fields->'reading_id') is distinct from 'string' or fields->>'reading_id' !~ '[^[:space:]]'
           or jsonb_typeof(fields->'context_format') is distinct from 'string' or fields->>'context_format' !~ '[^[:space:]]'
           or jsonb_typeof(fields->'field_associations') is distinct from 'array' or jsonb_array_length(fields->'field_associations')=0
           or jsonb_typeof(fields->'source_limits') is distinct from 'array'
           or jsonb_typeof(fields->'required_neighbor_chunk_ids') is distinct from 'array' then
            raise exception 'Complete C1 field metadata required' using errcode='23514';
        end if;
        span_number := 0;
        for s in select value from jsonb_array_elements(c->'spans') loop
            if not bintanong_private.partial_review_object(s,array['chunk_id','span_order','version_id','byte_sha256','page',
                    'printed_page_label','locator','text','bbox','bbox_origin','page_size','extraction'])
               or s->'chunk_id' is distinct from c->'chunk_id' or s->'version_id' is distinct from p_receipt->'version_id'
               or s->'byte_sha256' is distinct from p_receipt->'source_sha256'
               or jsonb_typeof(s->'span_order') is distinct from 'number' or s->>'span_order' !~ '^[0-9]+$'
               or (s->>'span_order')::integer<>span_number
               or jsonb_typeof(s->'page') is distinct from 'number' or s->>'page' !~ '^[1-9][0-9]*$'
               or jsonb_typeof(s->'locator') is distinct from 'object' or jsonb_typeof(s->'extraction') is distinct from 'object' then
                raise exception 'Ordered source-bound C1 span required' using errcode='23514';
            end if;
            span_number := span_number+1;
        end loop;
        if (select count(*) from jsonb_array_elements(fields->'field_associations')) <>
           (select count(distinct v->>'name') from jsonb_array_elements(fields->'field_associations') v) then
            raise exception 'Distinct C1 field names required' using errcode='23514';
        end if;
        for f in select value from jsonb_array_elements(fields->'field_associations') loop
            if jsonb_typeof(f) is distinct from 'object' or not f ?& array['name','value','source_blank','event_sha256','span_indexes']
               or jsonb_typeof(f->'name') is distinct from 'string' or f->>'name' !~ '[^[:space:]]'
               or jsonb_typeof(f->'source_blank') is distinct from 'boolean'
               or jsonb_typeof(f->'event_sha256') is distinct from 'string' or not (f->>'event_sha256'=any(event_ids))
               or jsonb_typeof(f->'span_indexes') is distinct from 'array' or (jsonb_array_length(f->'span_indexes')=0 and not (p_allow_source_blanks and f->'source_blank'='true'::jsonb and f->'value'=to_jsonb(''::text))) then
                raise exception 'Complete C1 field/event/span binding required' using errcode='23514';
            end if;
            if p_allow_source_blanks and f->'source_blank'='true'::jsonb
           and (f->'value' is distinct from to_jsonb(''::text) or jsonb_array_length(f->'span_indexes')<>0) then
            raise exception 'Source blank requires empty value and no invented span' using errcode='23514';
        end if;
        used_events := array_append(used_events,f->>'event_sha256');
            if (select count(*) from jsonb_array_elements(f->'span_indexes')) <>
               (select count(distinct v) from jsonb_array_elements(f->'span_indexes') v) then
                raise exception 'Distinct C1 span indexes required' using errcode='23514';
            end if;
            for x in select value from jsonb_array_elements(f->'span_indexes') loop
                if jsonb_typeof(x)<>'number' or x#>>'{}' !~ '^[0-9]+$' or (x#>>'{}')::integer>=span_number then
                    raise exception 'Valid C1 span index required' using errcode='23514';
                end if;
            end loop;
        end loop;
    end loop;
    if not event_ids <@ used_events then
        raise exception 'Unused C1 event lies outside declared field coverage' using errcode='23514';
    end if;
    for c in select value from jsonb_array_elements(p_receipt->'chunks') loop
        for x in select value from jsonb_array_elements(c#>'{type_fields,required_neighbor_chunk_ids}') loop
            if jsonb_typeof(x)<>'string' or not (x#>>'{}'=any(chunk_ids)) then
                raise exception 'Complete same-source C1 dependency closure required' using errcode='23514';
            end if;
        end loop;
    end loop;

end; $$;

create function bintanong_private.review_source_projection(target jsonb) returns jsonb
language sql immutable security invoker set search_path='' as $$
    select jsonb_build_object('version_id',target->'version_id','document_id',target->'document_id',
        'edition_id',target->'edition_id','filename',target->'filename','byte_sha256',target->'byte_sha256',
        'acquisition_locators',target->'acquisition_locators','acquisition_state',target#>'{acquisition_state,state}',
        'verification_state',target#>'{verification_state,state}','approval_state',target#>'{approval_state,state}',
        'content_review_state',target#>'{content_review_state,state}','source_register',target)
        || (select jsonb_object_agg(pair.key,pair.value) from jsonb_each(target) pair where pair.key=any(array[
            'issuer','campus','college','program','cohort','printed_revision','effective_from','effective_to','supersession']))
$$;

create function bintanong_private.validate_partial_review_chunks(
    target jsonb,p_receipt jsonb,p_pending_only boolean) returns void
language plpgsql stable security invoker set search_path='' as $$
declare c jsonb; chunk_row jsonb; span_rows jsonb;
begin
    for c in select value from jsonb_array_elements(p_receipt->'chunks') loop
        select to_jsonb(v) into chunk_row from public.chunks v where v.chunk_id=c->>'chunk_id';
        if chunk_row is null or chunk_row->'version_id' is distinct from target->'version_id'
           or chunk_row->'document_id' is distinct from target->'document_id'
           or chunk_row->'edition_id' is distinct from target->'edition_id'
           or chunk_row->'byte_sha256' is distinct from target->'byte_sha256'
           or chunk_row->>'source_verification' is distinct from (case when p_pending_only then 'pending' else target#>>'{verification_state,state}' end)
           or chunk_row->>'content_review' is distinct from (case when p_pending_only then 'pending' else 'partially_reviewed' end)
           or chunk_row->'content_hash' is distinct from c->'content_hash'
           or chunk_row->>'content_hash' is distinct from bintanong_private.content_hash(
                chunk_row->>'source_text',chunk_row->>'text')
           or chunk_row->'type_fields' is distinct from c->'type_fields' then
            raise exception 'C1 stored chunk snapshot differs' using errcode='23514';
        end if;
        select jsonb_agg(to_jsonb(v)-'span_id'-'created_at' order by span_order) into span_rows
            from public.source_spans v where v.chunk_id=c->>'chunk_id';
        if span_rows is distinct from c->'spans' then
            raise exception 'C1 stored span snapshot differs' using errcode='23514';
        end if;
    end loop;
end; $$;

create or replace function public.record_source_partial_review(p_expected_register jsonb,p_receipt jsonb)
returns jsonb language plpgsql volatile security invoker set search_path='' as $$
declare
    ev jsonb; e jsonb; c jsonb; f jsonb; s jsonb; fields jsonb; x jsonb;
    actual jsonb; stored jsonb; proposed jsonb; target jsonb; projected jsonb;
    saved_receipt jsonb; chunk_row jsonb; span_rows jsonb;
    key text; source_hash text; evidence_at timestamptz; span_number integer;
    event_ids text[] := '{}'; used_events text[] := '{}'; chunk_ids text[] := '{}';
begin
    perform bintanong_private.validate_partial_review_receipt(p_expected_register,p_receipt,true);
    ev := p_receipt->'evidence';
    proposed := jsonb_set(jsonb_set(p_expected_register,'{content_review_state}',
        jsonb_build_object('state','partially_reviewed','evidence_ref',ev->'evidence_id')),
        '{evidence}',(p_expected_register->'evidence') || jsonb_build_array(ev));
    perform bintanong_private.publication_lock();
    select to_jsonb(v)-'created_at' into actual from public.document_versions v
        where v.version_id=p_receipt->>'version_id' for update;
    if not found or jsonb_typeof(actual->'source_register') is distinct from 'object' then
        raise exception 'Registered nonlegacy C1 source required' using errcode='23514';
    end if;
    if exists(select 1 from public.release_document_versions rv join public.knowledge_releases r using(release_id)
        where rv.version_id=p_receipt->>'version_id' and r.published_at is not null) then
        raise exception 'Published C1 source is immutable' using errcode='55000';
    end if;
    stored := actual->'source_register';
    if stored=proposed then target := proposed;
    elsif stored=p_expected_register then target := p_expected_register;
    else raise exception 'C1 expected source register conflict' using errcode='23514';
    end if;
    projected := bintanong_private.review_source_projection(target);
    if actual is distinct from projected then
        raise exception 'C1 source relational projection differs' using errcode='23514';
    end if;
    perform bintanong_private.validate_partial_review_chunks(target,p_receipt,true);
    select receipt into saved_receipt from public.source_partial_reviews
        where version_id=p_receipt->>'version_id' and evidence_id=ev->>'evidence_id';
    if stored=proposed then
        if saved_receipt is distinct from p_receipt then
            raise exception 'C1 replay receipt missing or changed' using errcode='23514';
        end if;
        return stored;
    end if;
    if saved_receipt is not null then
        raise exception 'C1 receipt exists without its source transition' using errcode='23514';
    end if;
    insert into public.source_partial_reviews(version_id,evidence_id,receipt)
        values(p_receipt->>'version_id',ev->>'evidence_id',p_receipt);
    update public.document_versions set content_review_state='partially_reviewed',source_register=proposed
        where version_id=p_receipt->>'version_id';
    return proposed;
end; $$;


-- Immutable parent links prove supplementary receipts descend from registered C1 evidence.
create table public.source_review_supplements (
    version_id text not null,
    evidence_id text not null check (evidence_id ~ '[^[:space:]]'),
    base_evidence_id text not null check (base_evidence_id ~ '[^[:space:]]' and base_evidence_id<>evidence_id),
    created_at timestamptz not null default now(),
    primary key(version_id,evidence_id),
    foreign key(version_id,evidence_id) references public.source_partial_reviews(version_id,evidence_id)
        on delete restrict on update restrict,
    foreign key(version_id,base_evidence_id) references public.source_partial_reviews(version_id,evidence_id)
        on delete restrict on update restrict
);
create index p11_supplement_parent on public.source_review_supplements(version_id,base_evidence_id);
alter table public.source_review_supplements enable row level security;
revoke all on public.source_review_supplements from public,anon,authenticated,service_role;
grant select,insert on public.source_review_supplements to service_role;
create policy p11_supplement_runtime_denial on public.source_review_supplements
    as restrictive for all to anon,authenticated using(false) with check(false);
create trigger p11_supplement_immutable before update or delete or truncate
    on public.source_review_supplements for each statement execute function bintanong_private.partial_review_immutable();
create trigger p11_supplement_lock before insert on public.source_review_supplements
    for each statement execute function bintanong_private.lock_publication();

create function bintanong_private.partial_review_is_bound(p_register jsonb,p_evidence_id text) returns boolean
language sql stable security invoker set search_path='' as $$
    with recursive ancestors(evidence_id,visited) as (
        select p_evidence_id,array[p_evidence_id]
        union all
        select s.base_evidence_id,a.visited||s.base_evidence_id
        from ancestors a join public.source_review_supplements s
            on s.version_id=p_register->>'version_id' and s.evidence_id=a.evidence_id
        where not s.base_evidence_id=any(a.visited)
    )
    select exists(select 1 from ancestors a join public.source_partial_reviews r
        on r.version_id=p_register->>'version_id' and r.evidence_id=a.evidence_id
        where r.receipt->'source_sha256'=p_register->'byte_sha256'
          and r.receipt#>>'{evidence,evidence_id}'=r.evidence_id
          and p_register->'evidence' @> jsonb_build_array(r.receipt->'evidence'))
$$;

create function bintanong_private.validate_source_supplement(
    p_expected_register jsonb,p_receipt jsonb,p_base_evidence_id text) returns void
language plpgsql volatile security invoker set search_path='' as $$
declare actual jsonb; parent jsonb; c jsonb; v_evidence_id text;
begin
    perform bintanong_private.publication_lock();
    perform bintanong_private.validate_partial_review_receipt(p_expected_register,p_receipt,false,true);
    v_evidence_id := p_receipt#>>'{evidence,evidence_id}';
    if p_base_evidence_id is null or p_base_evidence_id !~ '[^[:space:]]'
       or p_base_evidence_id=v_evidence_id then
        raise exception 'Distinct base partial review required' using errcode='23514';
    end if;
    select to_jsonb(v)-'created_at' into actual from public.document_versions v
        where v.version_id=p_expected_register->>'version_id' for update;
    if not found or actual->'source_register' is distinct from p_expected_register
       or actual is distinct from bintanong_private.review_source_projection(p_expected_register)
       or actual->>'content_review_state'<>'partially_reviewed'
       or not exists(select 1 from public.release_document_versions rv
           join public.knowledge_releases r using(release_id)
           where rv.version_id=p_expected_register->>'version_id' and r.published_at is not null) then
        raise exception 'Unchanged published partially-reviewed source required' using errcode='23514';
    end if;
    select r.receipt into parent from public.source_partial_reviews r
        where r.version_id=p_expected_register->>'version_id' and r.evidence_id=p_base_evidence_id;
    if parent is null or not bintanong_private.partial_review_is_bound(p_expected_register,p_base_evidence_id)
       or parent->'source_sha256' is distinct from p_receipt->'source_sha256'
       or bintanong_private.partial_review_time(parent#>>'{evidence,recorded_at}') >
          bintanong_private.partial_review_time(p_receipt#>>'{evidence,recorded_at}')
       or not ((p_receipt->'source_events') @> (parent->'source_events'))
       or jsonb_array_length(p_receipt->'chunks')<=jsonb_array_length(parent->'chunks') then
        raise exception 'Source-bound cumulative parent review required' using errcode='23514';
    end if;
    for c in select value from jsonb_array_elements(parent->'chunks') loop
        if not exists(select 1 from jsonb_array_elements(p_receipt->'chunks') n where n=c) then
            raise exception 'Prior reviewed chunks must be retained exactly' using errcode='23514';
        end if;
    end loop;
    perform bintanong_private.validate_partial_review_chunks(p_expected_register,p_receipt,false);
end; $$;

create function public.record_source_supplementary_review(
    p_expected_register jsonb,p_receipt jsonb,p_base_evidence_id text) returns jsonb
language plpgsql volatile security invoker set search_path='' as $$
declare saved jsonb; saved_parent text; v_evidence_id text;
begin
    perform bintanong_private.validate_source_supplement(p_expected_register,p_receipt,p_base_evidence_id);
    v_evidence_id := p_receipt#>>'{evidence,evidence_id}';
    select r.receipt into saved from public.source_partial_reviews r
        where r.version_id=p_expected_register->>'version_id' and r.evidence_id=v_evidence_id;
    select s.base_evidence_id into saved_parent from public.source_review_supplements s
        where s.version_id=p_expected_register->>'version_id' and s.evidence_id=v_evidence_id;
    if saved is not null or saved_parent is not null then
        if saved=p_receipt and saved_parent=p_base_evidence_id then return saved; end if;
        raise exception 'Supplementary review replay conflict' using errcode='23514';
    end if;
    insert into public.source_partial_reviews(version_id,evidence_id,receipt)
        values(p_expected_register->>'version_id',v_evidence_id,p_receipt);
    insert into public.source_review_supplements(version_id,evidence_id,base_evidence_id)
        values(p_expected_register->>'version_id',v_evidence_id,p_base_evidence_id);
    return p_receipt;
end; $$;

-- Enforce the same proof on direct privileged INSERTs, not just RPC calls.
create function bintanong_private.validate_supplement_link() returns trigger
language plpgsql security invoker set search_path='' as $$
declare current_register jsonb; review jsonb;
begin
    select v.source_register into current_register from public.document_versions v
        where v.version_id=NEW.version_id;
    select r.receipt into review from public.source_partial_reviews r
        where r.version_id=NEW.version_id and r.evidence_id=NEW.evidence_id;
    if review#>>'{evidence,evidence_id}' is distinct from NEW.evidence_id then
        raise exception 'Exact supplementary link receipt required' using errcode='23514';
    end if;
    perform bintanong_private.validate_source_supplement(current_register,review,NEW.base_evidence_id);
    return NEW;
end; $$;
create trigger p11_supplement_validate before insert on public.source_review_supplements
    for each row execute function bintanong_private.validate_supplement_link();

create or replace function bintanong_private.validate_selected_review(p_receipt jsonb) returns void
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
           or not bintanong_private.partial_review_is_bound(dv.source_register,src->>'partial_review_evidence_id')
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
    perform bintanong_private.validate_selected_context(p_receipt);
end; $$;

-- Complete disciplinary topics exceed32 rows; other filter bounds stay32.
create or replace function public.retrieve_context(
    p_release_id text,
    p_config jsonb,
    query_embedding extensions.vector(1024),
    p_top_k integer default 5,
    p_min_similarity double precision default 0.5,
    p_scope jsonb default '[]'::jsonb,
    p_entity_hints jsonb default '[]'::jsonb,
    p_version_ids jsonb default '[]'::jsonb,
    p_chunk_ids jsonb default '[]'::jsonb
) returns jsonb
language plpgsql stable security invoker
set search_path = public, extensions
as $$
declare
    v_set public.embedding_sets%rowtype;
    v_set_id text;
    v_scope text[];
    v_hints text[];
    v_versions text[];
    v_chunks text[];
    v_items jsonb;
begin
    if p_top_k is null or p_top_k not in (3,5,8)
       or p_min_similarity is null or p_min_similarity not between -1 and 1
       or query_embedding is null or extensions.vector_dims(query_embedding) <> 1024
       or abs(extensions.vector_norm(query_embedding)-1) > 0.000001 then
        raise exception 'invalid retrieval parameters' using errcode='22023';
    end if;
    if p_config is null or jsonb_typeof(p_config) <> 'object' then
        raise exception 'configuration must be an object' using errcode='22023';
    end if;
    if p_scope is null or jsonb_typeof(p_scope) <> 'array'
       or p_entity_hints is null or jsonb_typeof(p_entity_hints) <> 'array'
       or p_version_ids is null or jsonb_typeof(p_version_ids) <> 'array'
       or p_chunk_ids is null or jsonb_typeof(p_chunk_ids) <> 'array' then
        raise exception 'retrieval filters must be arrays' using errcode='22023';
    end if;
    if jsonb_array_length(p_scope)>32 or jsonb_array_length(p_entity_hints)>32
       or jsonb_array_length(p_version_ids)>32 or jsonb_array_length(p_chunk_ids)>128 or exists (
          select 1 from jsonb_array_elements(p_scope || p_entity_hints || p_version_ids || p_chunk_ids) x
          where jsonb_typeof(x) <> 'string' or length(x#>>'{}') not between 1 and 256
             or btrim(x#>>'{}')=''
       ) or exists (
          select 1 from jsonb_array_elements_text(p_chunk_ids) x
          where x !~ '[^[:space:]]'
       ) then
        raise exception 'invalid retrieval filters' using errcode='22023';
    end if;
    select r.embedding_set_id into v_set_id
    from public.active_release a join public.knowledge_releases r on r.release_id=a.release_id
    where a.id=1 and a.release_id=p_release_id and r.status='active';
    if v_set_id is null then
        return jsonb_build_object('status','release_changed','release_id',p_release_id,'items','[]'::jsonb);
    end if;
    select * into v_set from public.embedding_sets where embedding_set_id=v_set_id;
    if not found or not p_config @> jsonb_build_object(
       'model_id',v_set.model_id,'model_revision',v_set.model_revision,
       'dimension',v_set.dimension,'normalization',v_set.normalization,
       'prompt_fingerprint',v_set.prompt_fingerprint,
       'preprocessing_fingerprint',v_set.preprocessing_fingerprint,
       'tokenizer_fingerprint',v_set.tokenizer_fingerprint
    ) then
        return jsonb_build_object('status','configuration_mismatch','release_id',p_release_id,'items','[]'::jsonb);
    end if;
    select coalesce(array_agg(x),'{}') into v_scope from jsonb_array_elements_text(p_scope) x;
    select coalesce(array_agg(x),'{}') into v_hints from jsonb_array_elements_text(p_entity_hints) x;
    select coalesce(array_agg(x),'{}') into v_versions from jsonb_array_elements_text(p_version_ids) x;

    select coalesce(array_agg(x),'{}') into v_chunks from jsonb_array_elements_text(p_chunk_ids) x;

    with recursive eligible as materialized (
        select c.*, (1-(e.embedding <=> query_embedding))::double precision as similarity
        from public.release_chunks rc
        join public.chunks c on c.chunk_id=rc.chunk_id
        join public.chunk_embeddings e on e.chunk_id=c.chunk_id and e.embedding_set_id=v_set_id
        where rc.release_id=p_release_id
          and (cardinality(v_scope)=0 or c.scope <@ v_scope)
          and (cardinality(v_versions)=0 or c.version_id=any(v_versions))
          and (cardinality(v_chunks)=0 or c.chunk_id=any(v_chunks))
    ), ranked as (
        select * from eligible c
        where c.similarity >= p_min_similarity
          and (cardinality(v_hints)=0 or (c.type_fields->'entity_hints') ?| v_hints)
        order by c.similarity desc, c.chunk_id limit p_top_k
    ), dependencies(root_id,chunk_id,version_id) as (
        select c.chunk_id,c.chunk_id,c.version_id from ranked c
        union
        select d.root_id,n.chunk_id,d.version_id
        from dependencies d join eligible parent on parent.chunk_id=d.chunk_id
        join eligible n on n.version_id=d.version_id
          and (parent.type_fields->'required_neighbor_chunk_ids') ? n.chunk_id
    ), payload as (
        select c.chunk_id, c.similarity, jsonb_build_object(
          'chunk', to_jsonb(c)-'similarity', 'similarity', c.similarity,
          'version', to_jsonb(v),
          'spans', coalesce((select jsonb_agg(to_jsonb(s) order by s.span_order,s.span_id)
                            from public.source_spans s where s.chunk_id=c.chunk_id),'[]'::jsonb)
        ) as item
        from eligible c join public.document_versions v on v.version_id=c.version_id
    )
    select coalesce(jsonb_agg(p.item || jsonb_build_object('neighbors',coalesce((
       select jsonb_agg(n.item order by n.chunk_id) from payload n
       join dependencies d on d.chunk_id=n.chunk_id and d.root_id=c.chunk_id
       where n.chunk_id<>c.chunk_id
    ),'[]'::jsonb)) order by c.similarity desc,c.chunk_id),'[]'::jsonb)
    into v_items from ranked c join payload p on p.chunk_id=c.chunk_id;
    return jsonb_build_object('status','ok','release_id',p_release_id,
        'embedding_set_id',v_set_id,'embedding_config',to_jsonb(v_set),'items',v_items);
end;
$$;


revoke all on function bintanong_private.validate_partial_review_receipt(jsonb,jsonb,boolean,boolean),
    bintanong_private.review_source_projection(jsonb),
    bintanong_private.validate_partial_review_chunks(jsonb,jsonb,boolean),
    bintanong_private.partial_review_is_bound(jsonb,text),
    bintanong_private.validate_source_supplement(jsonb,jsonb,text),
    bintanong_private.validate_supplement_link() from public,anon,authenticated;
grant execute on function bintanong_private.validate_partial_review_receipt(jsonb,jsonb,boolean,boolean),
    bintanong_private.review_source_projection(jsonb),
    bintanong_private.validate_partial_review_chunks(jsonb,jsonb,boolean),
    bintanong_private.partial_review_is_bound(jsonb,text),
    bintanong_private.validate_source_supplement(jsonb,jsonb,text),
    bintanong_private.validate_supplement_link() to service_role;
revoke all on function public.record_source_supplementary_review(jsonb,jsonb,text) from public,anon,authenticated;
grant execute on function public.record_source_supplementary_review(jsonb,jsonb,text) to service_role;
notify pgrst, 'reload schema';
