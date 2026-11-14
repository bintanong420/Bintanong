-- C1 selected-field coverage is administrative evidence, never source approval.
create table public.source_partial_reviews (
    version_id text not null references public.document_versions(version_id) on delete restrict on update restrict,
    evidence_id text not null check (evidence_id ~ '[^[:space:]]'),
    receipt jsonb not null check (jsonb_typeof(receipt)='object'),
    created_at timestamptz not null default now(),
    primary key(version_id,evidence_id)
);
alter table public.source_partial_reviews enable row level security;
revoke all on public.source_partial_reviews from public,anon,authenticated,service_role;
grant select,insert on public.source_partial_reviews to service_role;
create policy p5_partial_review_runtime_denial on public.source_partial_reviews
    as restrictive for all to anon,authenticated using(false) with check(false);

create function bintanong_private.partial_review_immutable() returns trigger
language plpgsql security invoker set search_path='' as $$
begin
    perform bintanong_private.publication_lock();
    raise exception 'Partial-review receipts are immutable' using errcode='55000';
end; $$;
create trigger p5_partial_review_immutable before update or delete or truncate
    on public.source_partial_reviews for each statement execute function bintanong_private.partial_review_immutable();

create function bintanong_private.partial_review_object(v jsonb, keys text[]) returns boolean
language sql immutable security invoker set search_path='' as $$
    select case when jsonb_typeof(v)='object' then
        v ?& keys and (select count(*) from jsonb_object_keys(v))=cardinality(keys) else false end
$$;

-- Existing Python contract: real 2000..2100 timestamp, offsets through 23:59,
-- fractional seconds truncated to microseconds, original text retained in JSON.
create function bintanong_private.partial_review_time(v text) returns timestamptz
language plpgsql immutable security invoker set search_path='' as $$
declare result timestamptz; displacement text; fraction text;
begin
    if v is null or v !~ '^(20[0-9]{2}|2100)-[0-9]{2}-[0-9]{2}T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?(Z|[+-]([01][0-9]|2[0-3]):[0-5][0-9])$' then
        raise exception 'Real partial-review timestamp required' using errcode='23514';
    end if;
    result := substring(v,1,19)::timestamp at time zone 'UTC';
    fraction := substring(v from '\.([0-9]+)');
    if fraction is not null then
        result := result + (('0.' || substring(fraction,1,6))::numeric * interval '1 second');
    end if;
    if right(v,1)<>'Z' then
        displacement := right(v,6);
        result := result - make_interval(mins =>
            (substring(displacement,2,2)::integer*60+substring(displacement,5,2)::integer)
            *case when left(displacement,1)='-' then -1 else 1 end);
    end if;
    return result;
end; $$;

create function public.record_source_partial_review(p_expected_register jsonb,p_receipt jsonb)
returns jsonb language plpgsql volatile security invoker set search_path='' as $$
declare
    ev jsonb; e jsonb; c jsonb; f jsonb; s jsonb; fields jsonb; x jsonb;
    actual jsonb; stored jsonb; proposed jsonb; target jsonb; projected jsonb;
    saved_receipt jsonb; chunk_row jsonb; span_rows jsonb;
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
               or jsonb_typeof(f->'span_indexes') is distinct from 'array' or jsonb_array_length(f->'span_indexes')=0 then
                raise exception 'Complete C1 field/event/span binding required' using errcode='23514';
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
    projected := jsonb_build_object('version_id',target->'version_id','document_id',target->'document_id',
        'edition_id',target->'edition_id','filename',target->'filename','byte_sha256',target->'byte_sha256',
        'acquisition_locators',target->'acquisition_locators','acquisition_state',target#>'{acquisition_state,state}',
        'verification_state',target#>'{verification_state,state}','approval_state',target#>'{approval_state,state}',
        'content_review_state',target#>'{content_review_state,state}','source_register',target)
        || (select jsonb_object_agg(pair.key,pair.value) from jsonb_each(target) pair where pair.key=any(array[
            'issuer','campus','college','program','cohort','printed_revision','effective_from','effective_to','supersession']));
    if actual is distinct from projected then
        raise exception 'C1 source relational projection differs' using errcode='23514';
    end if;
    for c in select value from jsonb_array_elements(p_receipt->'chunks') loop
        select to_jsonb(v) into chunk_row from public.chunks v where v.chunk_id=c->>'chunk_id';
        if chunk_row is null or chunk_row->'version_id' is distinct from target->'version_id'
           or chunk_row->'document_id' is distinct from target->'document_id'
           or chunk_row->'edition_id' is distinct from target->'edition_id'
           or chunk_row->'byte_sha256' is distinct from target->'byte_sha256'
           or chunk_row->>'source_verification' is distinct from 'pending'
           or chunk_row->>'content_review' is distinct from 'pending'
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

revoke all on function bintanong_private.partial_review_object(jsonb,text[]),
    bintanong_private.partial_review_time(text),bintanong_private.partial_review_immutable()
    from public,anon,authenticated;
grant execute on function bintanong_private.partial_review_object(jsonb,text[]),
    bintanong_private.partial_review_time(text),bintanong_private.partial_review_immutable() to service_role;
revoke all on function public.record_source_partial_review(jsonb,jsonb) from public,anon,authenticated;
grant execute on function public.record_source_partial_review(jsonb,jsonb) to service_role;
