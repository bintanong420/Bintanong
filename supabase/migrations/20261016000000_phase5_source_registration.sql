-- Preserve complete candidate source contracts without changing legacy rows.
alter table public.document_versions add column source_register jsonb
    check (source_register is null or jsonb_typeof(source_register) = 'object');

-- Initial-state insertion only. Authorized transitions use a separate workflow.
create function public.register_pending_sources(p_documents jsonb, p_versions jsonb)
returns void language plpgsql security invoker set search_path='' as $$
declare d jsonb; v jsonb; proposed jsonb; prior jsonb;
begin
    perform bintanong_private.publication_lock();
    if jsonb_typeof(p_documents) is distinct from 'array'
       or jsonb_typeof(p_versions) is distinct from 'array'
       or jsonb_array_length(p_documents)=0 or jsonb_array_length(p_versions)=0
       or jsonb_array_length(p_documents)<>(select count(distinct x->>'document_id') from jsonb_array_elements(p_documents) x)
       or jsonb_array_length(p_versions)<>(select count(distinct x->>'version_id') from jsonb_array_elements(p_versions) x)
       or exists(select 1 from jsonb_array_elements(p_documents) x where not exists
           (select 1 from jsonb_array_elements(p_versions) y where y->>'document_id'=x->>'document_id')) then
        raise exception 'Invalid source registration identities' using errcode='23514';
    end if;
    for d in select * from jsonb_array_elements(p_documents) loop
        if jsonb_typeof(d) is distinct from 'object'
           or (select count(*) from jsonb_object_keys(d))<>5
           or not d ?& array['document_id','namespace','synthetic','document_category','title']
           or d->>'namespace' is distinct from 'institutional'
           or jsonb_typeof(d->'synthetic') is distinct from 'boolean'
           or jsonb_typeof(d->'title') is distinct from 'string' or btrim(d->>'title')=''
           or jsonb_typeof(d->'document_id') is distinct from 'string' then
            raise exception 'Explicit institutional document metadata required' using errcode='23514';
        end if;
        select to_jsonb(t)-'created_at' into prior from public.documents t where t.document_id=d->>'document_id';
        if found then
            if prior<>d then
                raise exception 'Document identity conflicts with registered metadata' using errcode='23514';
            end if;
        else
            insert into public.documents(document_id,namespace,synthetic,document_category,title)
                values(d->>'document_id',d->>'namespace',(d->>'synthetic')::boolean,d->>'document_category',d->>'title');
        end if;
    end loop;
    for v in select * from jsonb_array_elements(p_versions) loop
        if jsonb_typeof(v) is distinct from 'object'
           or v->>'schema_version' is distinct from 'bintanong-source-register-v1'
           or v->>'namespace' is distinct from 'institutional'
           or v#>>'{acquisition_state,state}' is distinct from 'pending'
           or v#>>'{verification_state,state}' is distinct from 'pending'
           or v#>>'{approval_state,state}' is distinct from 'not_requested'
           or v#>>'{content_review_state,state}' is distinct from 'pending'
           or v->'approval_id' is distinct from 'null'::jsonb
           or exists(select 1 from unnest(array['acquisition_state','verification_state','approval_state','content_review_state']) k
               where v#>>array[k,'evidence_ref'] is not null) then
            raise exception 'Registration accepts only initial pending source states' using errcode='23514';
        end if;
        if not exists(select 1 from jsonb_array_elements(p_documents) x
            where x->'document_id'=v->'document_id' and x->'namespace'=v->'namespace'
                and x->'synthetic'=v->'synthetic') then
            raise exception 'Source parent metadata mismatch' using errcode='23514';
        end if;
        proposed := jsonb_build_object(
            'version_id',v->'version_id','document_id',v->'document_id','edition_id',v->'edition_id',
            'filename',v->'filename','byte_sha256',v->'byte_sha256','acquisition_locators',v->'acquisition_locators',
            'acquisition_state',v#>'{acquisition_state,state}','verification_state',v#>'{verification_state,state}',
            'approval_state',v#>'{approval_state,state}','content_review_state',v#>'{content_review_state,state}',
            'source_register',v) || (select jsonb_object_agg(key,value) from jsonb_each(v)
                where key=any(array['issuer','campus','college','program','cohort','printed_revision',
                    'effective_from','effective_to','supersession']));
        select to_jsonb(t)-'created_at' into prior from public.document_versions t where t.version_id=v->>'version_id';
        if found then
            if prior is distinct from proposed then
                raise exception 'Source version identity conflicts with registered evidence' using errcode='23514';
            end if;
        else
            insert into public.document_versions(version_id,document_id,edition_id,filename,byte_sha256,
                acquisition_locators,issuer,campus,college,program,cohort,printed_revision,effective_from,effective_to,
                supersession,acquisition_state,verification_state,approval_state,content_review_state,source_register)
                select r.version_id,r.document_id,r.edition_id,r.filename,r.byte_sha256,r.acquisition_locators,
                    r.issuer,r.campus,r.college,r.program,r.cohort,r.printed_revision,r.effective_from,r.effective_to,
                    r.supersession,r.acquisition_state,r.verification_state,r.approval_state,r.content_review_state,r.source_register
                from jsonb_populate_record(null::public.document_versions,proposed) r;
        end if;
    end loop;
end; $$;

revoke all on function public.register_pending_sources(jsonb,jsonb) from public,anon,authenticated;
grant execute on function public.register_pending_sources(jsonb,jsonb) to service_role;
