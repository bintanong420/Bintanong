-- Phase 12 (owner 30 Oct 2026): the selected-review context check accepts reviewed flowchart groups
-- (`flow_manifest`, Python codec since 27 Oct). Reproduces reviewed_policy_context's flow payload and binds
-- each manifest to its source, page, review event, field inventory, limits and completeness.
create or replace function bintanong_private.validate_selected_context(p_receipt jsonb) returns void
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
                or bintanong_private.partial_review_object(g,array['logical_step_id','part_order','part_count','part_reading_id','record_manifest'])
                or bintanong_private.partial_review_object(g,array['logical_step_id','part_order','part_count','part_reading_id','flow_manifest']))
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
                   or meta->'flow_manifest' is distinct from g->'flow_manifest'
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
            if g ? 'flow_manifest' then
                -- Binds the displayed flow to its reviewed annotation; image geometry and span
                -- digests stay checked by the Python codec (reviewed_flow_evidence.py).
                manifest := g->'flow_manifest';
                if jsonb_typeof(manifest) is distinct from 'object'
                   or manifest->>'schema_version' is distinct from 'bintanong-flow-evidence-v1'
                   or manifest->'logical_step_id' is distinct from g->'logical_step_id'
                   or manifest->'version_id' is distinct from c#>'{spans,0,version_id}'
                   or manifest->'source_sha256' is distinct from c#>'{spans,0,byte_sha256}'
                   or jsonb_typeof(manifest->'physical_page') is distinct from 'number'
                   or exists(select 1 from jsonb_array_elements(c->'spans') s where s->'page' is distinct from manifest->'physical_page')
                   or jsonb_typeof(manifest->'review_event_json') is distinct from 'string'
                   or encode(sha256(convert_to(manifest->>'review_event_json','UTF8')),'hex') is distinct from manifest->>'review_event_sha256'
                   or jsonb_typeof(manifest->'nodes') is distinct from 'array' or jsonb_typeof(manifest->'edges') is distinct from 'array'
                   or jsonb_typeof(manifest->'unresolved_outgoing') is distinct from 'array'
                   or jsonb_typeof(manifest->'labels') is distinct from 'object'
                   or jsonb_typeof(manifest->'field_bindings') is distinct from 'object'
                   or jsonb_typeof(manifest->'source_complete') is distinct from 'boolean'
                   or exists(select 1 from jsonb_array_elements(c#>'{type_fields,field_associations}') a
                       where a ? 'field_kind' or not (manifest->'field_bindings') ? (a->>'name')) then
                    raise exception 'Bound selected flow manifest required' using errcode='23514';
                end if;
                original := (manifest->>'review_event_json')::jsonb;
                if jsonb_typeof(original) is distinct from 'object' or original->'source_sha256' is distinct from manifest->'source_sha256'
                   or original->>'flow_evidence_sha256' is distinct from encode(sha256(convert_to(bintanong_private.selected_json(
                       manifest-'review_event_sha256'-'review_event_json'),'UTF8')),'hex') then
                    raise exception 'Selected flow manifest differs from its review event' using errcode='23514';
                end if;
                select coalesce(jsonb_agg(a->'name'),'[]') into names from jsonb_array_elements(members) m
                    cross join lateral jsonb_array_elements(m#>'{type_fields,field_associations}') a;
                select coalesce(jsonb_agg(l.x-'source_sha256'-'version_id'-'span_indexes'-'resolution'-'message' order by m.mo,l.lo),'[]')
                    into refs from jsonb_array_elements(members) with ordinality m(v,mo)
                    cross join lateral jsonb_array_elements(m.v#>'{type_fields,source_limits}') with ordinality l(x,lo);
                if (select count(distinct value) from jsonb_array_elements(names))<>jsonb_array_length(names)
                   or (select count(*) from jsonb_object_keys(manifest->'field_bindings'))<>jsonb_array_length(names)
                   or exists(select 1 from jsonb_object_keys(manifest->'field_bindings') k where not names @> jsonb_build_array(k))
                   or encode(sha256(convert_to(bintanong_private.selected_json(refs),'UTF8')),'hex') is distinct from manifest->>'limits_sha256'
                   or (manifest->'source_complete')::boolean is distinct from (jsonb_array_length(refs)=0
                       and jsonb_array_length(manifest->'unresolved_outgoing')=0
                       and exists(select 1 from jsonb_array_elements(manifest->'nodes') n where n->>'id'='END')) then
                    raise exception 'Complete selected flow fields, limits and completeness required' using errcode='23514';
                end if;
                payload := payload||jsonb_build_object('flow_evidence',jsonb_build_object(
                    'source_complete',manifest->'source_complete',
                    'nodes',coalesce((select jsonb_agg(jsonb_build_object('id',nn.n->'id','kind',nn.n->'kind','field',nn.n->'field',
                        'outgoing',coalesce((select jsonb_agg(jsonb_build_object('to',ee.e->'to',
                            'label',coalesce(manifest->'labels'->(ee.e->>'label'),'null'::jsonb)) order by ee.eo)
                            from jsonb_array_elements(manifest->'edges') with ordinality ee(e,eo) where ee.e->'from'=nn.n->'id'),'[]'),
                        'outgoing_unresolved',exists(select 1 from jsonb_array_elements(manifest->'unresolved_outgoing') u
                            where u->'from'=nn.n->'id')) order by nn.no)
                        from jsonb_array_elements(manifest->'nodes') with ordinality nn(n,no)
                        where exists(select 1 from jsonb_array_elements(c#>'{type_fields,field_associations}') a
                            where a->'name'=nn.n->'field')),'[]'),
                    'value_origin','reviewed_visible_flow_geometry',
                    'limitation','Visible source structure only; missing conditions or endpoints must not be inferred.'));
            end if;
            payload := payload||jsonb_build_object('service_group',case when kind='reviewed-policy-fields-v2'
                then g-'record_manifest'-'flow_manifest' else g-'flow_manifest' end);
        end if;
        if (kind='reviewed-policy-fields-v2' and (jsonb_array_length(c#>'{type_fields,source_limits}')>0 or g is not null))
           or coalesce(g ? 'flow_manifest',false) then
            payload := payload||jsonb_build_object('evidence_sha256',encode(sha256(convert_to(bintanong_private.selected_json(
                jsonb_build_object('source_limits',c#>'{type_fields,source_limits}','service_group',g)),'UTF8')),'hex'));
        end if;
        select text into rendered from public.chunks where chunk_id=c->>'chunk_id';
        if rendered::jsonb is distinct from payload then
            raise exception 'Selected rendered fields or source limitations differ' using errcode='23514';
        end if;
    end loop;
end; $$;
