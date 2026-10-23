-- Owner-authorized research releases (owner decision 22 October 2026, option A).
-- The authorization lives on the release; source registers keep their true states and are
-- never marked approved. Institutional release rules are unchanged.
alter table public.knowledge_releases
    add column release_kind text not null default 'institutional'
        check (release_kind in ('institutional','research')),
    add column research_authorization_ref text,
    add constraint p9_research_authorization check (
        (release_kind='research') = (research_authorization_ref is not null)
        and (research_authorization_ref is null or research_authorization_ref ~ '^research-owner-[0-9]{8}$'));

create function public.designate_research_release(p_release_id text,p_authorization_ref text) returns jsonb
language plpgsql volatile security invoker set search_path='' as $$
declare rel public.knowledge_releases%rowtype;
begin
    perform bintanong_private.publication_lock();
    if p_authorization_ref is null or p_authorization_ref !~ '^research-owner-[0-9]{8}$' then
        raise exception 'Owner research authorization reference required' using errcode='23514';
    end if;
    select * into rel from public.knowledge_releases where release_id=p_release_id for update;
    if not found or rel.status<>'draft' or rel.published_at is not null or rel.review_scope_id is null then
        raise exception 'Unpublished draft with a bound selected review required' using errcode='23514';
    end if;
    if rel.release_kind='research' and rel.research_authorization_ref is distinct from p_authorization_ref then
        raise exception 'Research authorization reference is already set' using errcode='23514';
    end if;
    update public.knowledge_releases set release_kind='research',research_authorization_ref=p_authorization_ref
        where release_id=p_release_id;
    return jsonb_build_object('release_id',p_release_id,'release_kind','research',
        'research_authorization_ref',p_authorization_ref);
end; $$;

revoke all on function public.designate_research_release(text,text) from public,anon,authenticated;
grant execute on function public.designate_research_release(text,text) to service_role;

-- Research sources: bytes verified, printed spans observed (V1) or verified, approval not yet
-- requested or approved. Their chunks may be observed instead of verified. Nothing else changes.
alter policy p4_document_versions_select_active on public.document_versions using (
    exists(select 1 from public.release_document_versions rdv
        join public.knowledge_releases kr using(release_id)
        where rdv.version_id=document_versions.version_id
          and (document_versions.content_review_state='reviewed'
            or (document_versions.content_review_state='partially_reviewed' and kr.review_scope_id is not null))
          and ((document_versions.approval_state='approved' and document_versions.verification_state='verified')
            or (kr.release_kind='research' and document_versions.acquisition_state='verified'
                and document_versions.verification_state in ('observed','verified')
                and document_versions.approval_state in ('not_requested','approved')))));
alter policy p4_chunks_select_active on public.chunks using (
    anchored
    and exists(select 1 from public.release_chunks rc join public.knowledge_releases kr using(release_id)
        where rc.chunk_id=chunks.chunk_id
          and (chunks.content_review='reviewed'
            or (chunks.content_review='partially_reviewed' and kr.review_scope_id is not null))
          and (chunks.source_verification='verified'
            or (kr.release_kind='research' and chunks.source_verification='observed')))
    and exists(select 1 from public.document_versions dv where dv.version_id=chunks.version_id
        and dv.document_id=chunks.document_id and dv.byte_sha256=chunks.byte_sha256
        and dv.edition_id=chunks.edition_id and dv.content_review_state=chunks.content_review));

create or replace function bintanong_private.validate_release(p_release_id text) returns void
language plpgsql security invoker set search_path='' as $$
declare rel public.knowledge_releases%rowtype; cfg public.embedding_sets%rowtype; selected boolean; research boolean;
begin
    perform bintanong_private.publication_lock();
    select * into rel from public.knowledge_releases where release_id=p_release_id;
    if not found or rel.status='revoked' then
        raise exception 'Release is missing or revoked' using errcode='23514';
    end if;
    selected := rel.review_scope_id is not null;
    research := rel.release_kind='research';
    if research and (not selected or rel.research_authorization_ref is null) then
        raise exception 'Research release requires a selected review and owner authorization' using errcode='23514';
    end if;
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
        ((dv.content_review_state<>'reviewed' and (not selected or dv.content_review_state<>'partially_reviewed'))
         or (not research and (dv.approval_state<>'approved' or dv.verification_state<>'verified'))
         or (research and (dv.acquisition_state<>'verified' or dv.verification_state not in ('observed','verified')
             or dv.approval_state not in ('not_requested','approved'))))) then
        raise exception 'Release contains unapproved document evidence' using errcode='23514';
    end if;
    if exists(select 1 from public.release_chunks rc join public.chunks c on c.chunk_id=rc.chunk_id
        left join public.document_versions dv on dv.version_id=c.version_id
        left join public.release_document_versions rdv on rdv.version_id=c.version_id and rdv.release_id=p_release_id
        left join public.chunk_embeddings ce on ce.chunk_id=c.chunk_id and ce.embedding_set_id=rel.embedding_set_id
        where rc.release_id=p_release_id and
        (not c.anchored or (c.source_verification<>'verified' and not (research and c.source_verification='observed'))
         or (c.content_review<>'reviewed' and (not selected or c.content_review<>'partially_reviewed'))
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
