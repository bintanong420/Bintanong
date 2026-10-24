-- Narrow model-selected topics before cosine ranking; retain active-release RLS.
-- Default empty filter preserves existing callers; replace the old overload atomically.
drop function public.retrieve_context(text,jsonb,extensions.vector,integer,double precision,jsonb,jsonb,jsonb);

-- One STABLE statement snapshot binds rankings, spans, neighbors and versions.
-- A pin is valid only while authorized by existing active-release RLS.
create function public.retrieve_context(
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
       or jsonb_array_length(p_version_ids)>32 or jsonb_array_length(p_chunk_ids)>32 or exists (
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

revoke all on function public.retrieve_context(text,jsonb,extensions.vector,integer,double precision,jsonb,jsonb,jsonb,jsonb)
    from public, anon, authenticated, service_role;
grant execute on function public.retrieve_context(text,jsonb,extensions.vector,integer,double precision,jsonb,jsonb,jsonb,jsonb)
    to anon, authenticated;

notify pgrst, 'reload schema';
