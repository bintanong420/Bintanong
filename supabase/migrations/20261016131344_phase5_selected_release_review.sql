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

-- Match the reviewed-context codec's canonical JSON and printed whitespace.
create function bintanong_private.selected_json(v jsonb) returns text
language plpgsql immutable security invoker set search_path='' as $$
begin
    if jsonb_typeof(v)='object' then
        return '{'||coalesce((select string_agg(to_jsonb(key)::text||':'||bintanong_private.selected_json(value),
            ',' order by key collate "C") from jsonb_each(v)),'')||'}';
    elsif jsonb_typeof(v)='array' then
        return '['||coalesce((select string_agg(bintanong_private.selected_json(value),',' order by ordinality)
            from jsonb_array_elements(v) with ordinality),'')||']';
    end if;
    return coalesce(v::text,'null');
end; $$;
create function bintanong_private.selected_text(v text) returns text
language sql immutable security invoker set search_path='' as $$
    select pg_catalog.normalize(btrim(regexp_replace(translate(v,
        U&'\0009\000A\000B\000C\000D\001C\001D\001E\001F\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000',
        repeat(' ',28)), ' +',' ','g')), 'NFC');
$$;

create function bintanong_private.validate_selected_context(p_receipt jsonb) returns void
language plpgsql volatile security invoker set search_path='' as $$
declare c jsonb; f jsonb; g jsonb; lim jsonb; x jsonb; edge jsonb; src jsonb; item jsonb;
    payload jsonb; display_fields jsonb; displayed_limits jsonb; members jsonb; meta jsonb;
    origin jsonb; original jsonb; base jsonb; values_by_name jsonb; name text; names jsonb;
    visible jsonb; refs jsonb; pages jsonb; actual_pages jsonb; manifest jsonb;
    printed text; rendered text; at_index integer; total integer; count_parts integer; kind text;
    hashes text[]; gap_ids text[];
begin
    for c in select value from jsonb_array_elements(p_receipt->'chunks') loop
        display_fields := '[]'; displayed_limits := '[]'; g := nullif(c#>'{type_fields,service_group}','null'::jsonb);
        kind := c#>>'{type_fields,context_format}'; gap_ids := '{}';
        if kind not in ('reviewed-policy-fields-v1','reviewed-policy-fields-v2') or kind is null then
            raise exception 'Supported selected context codec required' using errcode='23514';
        end if;
        for f in select value from jsonb_array_elements(c#>'{type_fields,field_associations}') loop
            item := jsonb_build_object('name',f->'name','value',f->'value','source_blank',f->'source_blank');
            if f ? 'field_state' or (f ? 'field_kind' and f->>'field_kind'<>'arrows') then
                raise exception 'Selected codec supports located scalar/arrow fields only' using errcode='23514';
            end if;
            if f->>'field_kind'='arrows' then
                if g is null or f->>'name'<>'arrows' or f->'source_blank'<>'false'::jsonb
                   or jsonb_typeof(f->'value') is distinct from 'array'
                   or jsonb_typeof(f->'node_reading_ids') is distinct from 'object'
                   or (f->'node_reading_ids') ? 'END'
                   or jsonb_array_length(f->'value')=0
                   or jsonb_array_length(f->'span_indexes')<>jsonb_array_length(f->'value')+1
                   or (select count(*) from jsonb_each(f->'node_reading_ids'))<>
                      (select count(distinct value) from jsonb_each(f->'node_reading_ids')) then
                    raise exception 'Complete selected arrow mapping required' using errcode='23514';
                end if;
                at_index := 0; hashes := '{}';
                for edge in select value from jsonb_array_elements(f->'value') loop
                    if not bintanong_private.partial_review_object(edge,array['from','label','to'])
                       or exists(select 1 from jsonb_each(edge) where jsonb_typeof(value)<>'string' or value#>>'{}'='')
                       or not (f->'node_reading_ids') ? (edge->>'from')
                       or ((edge->>'to')<>'END' and not (f->'node_reading_ids') ? (edge->>'to'))
                       or edge->>'label' is distinct from c#>>array['spans',f#>>array['span_indexes',at_index::text],'text']
                       or edge::text=any(hashes) then
                        raise exception 'Selected arrow differs from located labels' using errcode='23514';
                    end if;
                    hashes := array_append(hashes,edge::text); at_index := at_index+1;
                end loop;
                if c#>>array['spans',f#>>array['span_indexes',at_index::text],'text'] is distinct from 'END' then
                    raise exception 'Selected arrow END label required' using errcode='23514';
                end if;
                item := item||jsonb_build_object('field_kind','arrows','node_reading_ids',f->'node_reading_ids');
            else
                select string_agg(c#>>array['spans',r.value#>>'{}','text'],' ' order by r.ordinality) into printed
                    from jsonb_array_elements(f->'span_indexes') with ordinality r;
                if (f->'source_blank'='true'::jsonb and (f->'value'<>'""'::jsonb or jsonb_array_length(f->'span_indexes')<>0))
                   or (f->'source_blank'='false'::jsonb and (jsonb_typeof(f->'value') is distinct from 'string'
                       or bintanong_private.selected_text(f->>'value') is distinct from bintanong_private.selected_text(printed))) then
                    raise exception 'Selected field value differs from located source text' using errcode='23514';
                end if;
            end if;
            display_fields := display_fields||jsonb_build_array(item);
        end loop;
        if jsonb_typeof(c#>'{type_fields,source_limits}') is distinct from 'array' then
            raise exception 'Selected source limits required' using errcode='23514';
        end if;
        for lim in select value from jsonb_array_elements(c#>'{type_fields,source_limits}') loop
            names := lim->'field_names'; visible := lim->'visible_text'; refs := '[]'; at_index := 0;
            if lim->>'issue' is null or lim->>'issue' not in ('source_cutoff','malformed_source_condition','conflicting_deadlines',
                'printed_total_discrepancy','effectivity_currentness_unknown','claim_not_stated')
               or jsonb_typeof(names) is distinct from 'array' or jsonb_array_length(names)=0
               or jsonb_typeof(lim->'affected_claims') is distinct from 'array' or jsonb_array_length(lim->'affected_claims')=0
               or coalesce(lim->>'gap_id','')='' or lim->>'gap_id'=any(gap_ids)
               or jsonb_typeof(lim#>'{locator,physical_pages}') is distinct from 'array'
               or jsonb_array_length(lim#>'{locator,physical_pages}')=0
               or (select count(*) from jsonb_array_elements(names))<>(select count(distinct value) from jsonb_array_elements(names))
               or exists(select 1 from jsonb_array_elements(lim->'affected_claims') where jsonb_typeof(value)<>'string' or value#>>'{}'='') then
                raise exception 'Complete distinct selected source limit required' using errcode='23514';
            end if;
            gap_ids := array_append(gap_ids,lim->>'gap_id');
            if jsonb_typeof(visible)='string' then visible := jsonb_build_array(visible); end if;
            if jsonb_typeof(visible) is distinct from 'array' or jsonb_array_length(visible)<>jsonb_array_length(names) then
                raise exception 'Complete visible selected limit fields required' using errcode='23514';
            end if;
            for x in select value from jsonb_array_elements(names) loop
                select value into f from jsonb_array_elements(c#>'{type_fields,field_associations}') where value->'name'=x;
                if f is null or jsonb_typeof(visible->at_index) is distinct from 'string'
                   or bintanong_private.selected_text(visible->>at_index)=''
                   or strpos(bintanong_private.selected_text(f->>'value'),bintanong_private.selected_text(visible->>at_index))=0 then
                    raise exception 'Source limit differs from visible field' using errcode='23514';
                end if;
                refs := refs||(f->'span_indexes'); at_index := at_index+1;
            end loop;
            select jsonb_agg(distinct (c#>>array['spans',value#>>'{}','page'])::integer) into pages from jsonb_array_elements(refs);
            select jsonb_agg(distinct value) into actual_pages from jsonb_array_elements(lim#>'{locator,physical_pages}');
            if refs is distinct from lim->'span_indexes' or not (pages @> actual_pages and actual_pages @> pages)
               or lim#>>'{locator,field}' is distinct from (select string_agg(value#>>'{}',',' order by ordinality) from jsonb_array_elements(names) with ordinality)
               or lim->'source_sha256' is distinct from c#>'{spans,0,byte_sha256}'
               or lim->'version_id' is distinct from c#>'{spans,0,version_id}' or lim->>'resolution' is distinct from 'unresolved'
               or lim->>'message' is distinct from 'Unavailable information: '||
                    (select string_agg(value#>>'{}',', ' order by ordinality) from jsonb_array_elements(lim->'affected_claims') with ordinality)
                    ||'. Source limitation remains unresolved ('||(lim->>'issue')||').' then
                raise exception 'Selected source limit binding or message differs' using errcode='23514';
            end if;
            displayed_limits := displayed_limits||jsonb_build_array(case when kind='reviewed-policy-fields-v2' or g ? 'record_manifest'
                then lim-'visible_text'-'source_sha256'-'version_id'-'span_indexes' else lim end);
        end loop;
        payload := jsonb_build_object('fields',display_fields,'source_limits',displayed_limits);
        if g is not null then
            if not (bintanong_private.partial_review_object(g,array['logical_step_id','part_order','part_count'])
                or bintanong_private.partial_review_object(g,array['logical_step_id','part_order','part_count','part_reading_id'])
                or bintanong_private.partial_review_object(g,array['logical_step_id','part_order','part_count','part_reading_id','record_manifest']))
               or jsonb_typeof(g->'logical_step_id') is distinct from 'string' or g->>'logical_step_id'=''
               or jsonb_typeof(g->'part_count') is distinct from 'number' or g->>'part_count' !~ '^[1-9][0-9]*$'
               or jsonb_typeof(g->'part_order') is distinct from 'number' or g->>'part_order' !~ '^[0-9]+$' then
                raise exception 'Selected service group metadata required' using errcode='23514';
            end if;
            select jsonb_agg(m order by (m#>>'{type_fields,service_group,part_order}')::integer) into members
                from jsonb_array_elements(p_receipt->'chunks') m where m#>'{spans,0,version_id}'=c#>'{spans,0,version_id}'
                and m#>'{type_fields,service_group,logical_step_id}'=g->'logical_step_id';
            count_parts := (g->>'part_count')::integer;
            if jsonb_array_length(members)<>count_parts then raise exception 'Incomplete selected service group' using errcode='23514'; end if;
            for at_index in 0..count_parts-1 loop
                meta := members#>array[at_index::text,'type_fields','service_group'];
                if meta->>'part_order' is distinct from at_index::text or meta->'part_count' is distinct from g->'part_count'
                   or meta->'record_manifest' is distinct from g->'record_manifest'
                   or (meta ? 'part_reading_id' and meta->'part_reading_id' is distinct from members#>array[at_index::text,'type_fields','reading_id']) then
                    raise exception 'Selected service group count/order/manifest differs' using errcode='23514';
                end if;
            end loop;
            for f in select value from jsonb_array_elements(c#>'{type_fields,field_associations}') where value->>'field_kind'='arrows' loop
                if g->>'part_order'<>'0'
                   or (select count(*) from jsonb_each(f->'node_reading_ids'))<>count_parts-1
                   or exists(select 1 from jsonb_each(f->'node_reading_ids') node where jsonb_typeof(node.value)<>'string'
                       or not exists(select 1 from jsonb_array_elements(members) m where m->'chunk_id'<>c->'chunk_id'
                           and m#>'{type_fields,reading_id}'=node.value))
                   or exists(select 1 from jsonb_array_elements(members) m where m#>'{type_fields,reading_id}'
                       is distinct from m#>'{type_fields,service_group,part_reading_id}')
                   or (select count(distinct s->'page') from jsonb_array_elements(members) m
                        cross join lateral jsonb_array_elements(m->'spans') s)<>1 then
                    raise exception 'Complete same-page selected flowchart nodes required' using errcode='23514';
                end if;
            end loop;
            if g ? 'record_manifest' then
                manifest := g->'record_manifest';
                if not bintanong_private.partial_review_object(manifest,array['parts','gaps'])
                   or jsonb_typeof(manifest->'parts') is distinct from 'array'
                   or jsonb_array_length(manifest->'parts')<>count_parts
                   or jsonb_typeof(manifest->'gaps') is distinct from 'object' then
                    raise exception 'Complete selected record manifest required' using errcode='23514';
                end if;
                for at_index in 0..count_parts-1 loop
                    meta := members->at_index;
                    if meta#>>'{type_fields,service_group,part_reading_id}' is distinct from
                        (g->>'logical_step_id')||'::part:'||at_index::text
                       or (select jsonb_agg(value->'name' order by ordinality)
                           from jsonb_array_elements(meta#>'{type_fields,field_associations}') with ordinality)
                           is distinct from manifest#>array['parts',at_index::text] then
                        raise exception 'Selected record fields or part identity differ' using errcode='23514';
                    end if;
                end loop;
                for name,origin in select key,value from jsonb_each(manifest->'gaps') loop
                    base := null; values_by_name := '{}'; pages := '[]';
                    for lim in select l from jsonb_array_elements(members) m
                        cross join lateral jsonb_array_elements(m#>'{type_fields,source_limits}') l where l->>'gap_id'=name loop
                        item := lim-'field_names'-'visible_text'-'locator'-'source_sha256'-'version_id'-'span_indexes'-'resolution'-'message';
                        if base is null then base := item;
                        elsif base is distinct from item then raise exception 'Selected record gap meaning differs' using errcode='23514'; end if;
                        at_index := 0;
                        for x in select value from jsonb_array_elements(lim->'field_names') loop
                            if values_by_name ? (x#>>'{}') then raise exception 'Duplicate selected record gap field' using errcode='23514'; end if;
                            values_by_name := values_by_name||jsonb_build_object(x#>>'{}',case when jsonb_typeof(lim->'visible_text')='array'
                                then lim#>array['visible_text',at_index::text] else lim->'visible_text' end);
                            at_index := at_index+1;
                        end loop;
                        pages := pages||(lim#>'{locator,physical_pages}');
                    end loop;
                    if base is null or jsonb_typeof(origin->'field_names') is distinct from 'array'
                       or jsonb_array_length(origin->'field_names')<>(select count(*) from jsonb_object_keys(values_by_name))
                       or not (pages @> (origin#>'{locator,physical_pages}') and (origin#>'{locator,physical_pages}') @> pages) then
                        raise exception 'Incomplete selected record gap' using errcode='23514';
                    end if;
                    select jsonb_agg(values_by_name->(value#>>'{}') order by ordinality) into visible
                        from jsonb_array_elements(origin->'field_names') with ordinality;
                    original := base||jsonb_build_object('field_names',origin->'field_names','locator',origin->'locator',
                        'visible_text',case when origin->>'visible_text_kind'='string' then visible->0 else visible end);
                    if encode(sha256(convert_to(bintanong_private.selected_json(original),'UTF8')),'hex') is distinct from origin->>'sha256' then
                        raise exception 'Selected original record gap digest differs' using errcode='23514';
                    end if;
                end loop;
            end if;
            payload := payload||jsonb_build_object('service_group',case when kind='reviewed-policy-fields-v2' then g-'record_manifest' else g end);
        end if;
        if kind='reviewed-policy-fields-v2' and (jsonb_array_length(c#>'{type_fields,source_limits}')>0 or g is not null) then
            payload := payload||jsonb_build_object('evidence_sha256',encode(sha256(convert_to(bintanong_private.selected_json(
                jsonb_build_object('source_limits',c#>'{type_fields,source_limits}','service_group',g)),'UTF8')),'hex'));
        end if;
        select text into rendered from public.chunks where chunk_id=c->>'chunk_id';
        if rendered::jsonb is distinct from payload then
            raise exception 'Selected rendered fields or source limitations differ' using errcode='23514';
        end if;
    end loop;
end; $$;

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
    perform bintanong_private.validate_selected_context(p_receipt);
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
    bintanong_private.selected_json(jsonb),bintanong_private.selected_text(text),bintanong_private.validate_selected_context(jsonb),
    bintanong_private.validate_selected_release(text,text),public.record_selected_release_review(jsonb),
    public.bind_selected_release_review(text,text) from public,anon,authenticated;
grant execute on function bintanong_private.validate_selected_review(jsonb),
    bintanong_private.selected_json(jsonb),bintanong_private.selected_text(text),bintanong_private.validate_selected_context(jsonb),
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
