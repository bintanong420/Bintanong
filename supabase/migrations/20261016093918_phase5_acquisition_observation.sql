-- A1 only. Possession/byte checks do not verify or approve institutional sources.
create function public.observe_source_acquisition(p_expected_register jsonb, p_check jsonb)
returns jsonb language plpgsql volatile security invoker set search_path = '' as $$
declare
    ev jsonb;
    proposed jsonb;
    actual jsonb;
    stored jsonb;
    target jsonb;
    projected jsonb;
    lifecycle text;
begin
    if jsonb_typeof(p_expected_register) is distinct from 'object'
       or jsonb_typeof(p_check) is distinct from 'object' then
        raise exception 'Source register and byte-check objects required' using errcode='23514';
    end if;
    if (select count(*) from jsonb_object_keys(p_check))<>4
       or not p_check ?& array['version_id','source_sha256','acquisition_locators','evidence']
       or jsonb_typeof(p_check->'version_id') is distinct from 'string'
       or jsonb_typeof(p_check->'source_sha256') is distinct from 'string'
       or jsonb_typeof(p_check->'acquisition_locators') is distinct from 'array'
       or jsonb_typeof(p_check->'evidence') is distinct from 'object'
       or p_check->'version_id' is distinct from p_expected_register->'version_id'
       or p_check->'source_sha256' is distinct from p_expected_register->'byte_sha256'
       or p_check->'acquisition_locators' is distinct from p_expected_register->'acquisition_locators' then
        raise exception 'Exact source-bound byte-check envelope required' using errcode='23514';
    end if;
    ev := p_check->'evidence';
    if (select count(*) from jsonb_object_keys(ev))<>5
       or not ev ?& array['evidence_id','kind','recorded_by','recorded_at','authorization_ref']
       or jsonb_typeof(ev->'evidence_id') is distinct from 'string'
       or ev->>'evidence_id' !~ '[^[:space:]]'
       or ev->'kind' is distinct from '"byte_hash_check"'::jsonb
       or jsonb_typeof(ev->'recorded_by') is distinct from 'string'
       or ev->>'recorded_by' not in ('researcher','reviewer','system')
       or ev->'authorization_ref' is distinct from 'null'::jsonb
       or jsonb_typeof(ev->'recorded_at') is distinct from 'string' then
        raise exception 'Distinct A1 byte-check evidence required' using errcode='23514';
    end if;
    -- Match the existing contract's timezone-aware real timestamp/year boundary.
    if ev->>'recorded_at' !~ '^(20[0-9]{2}|2100)-[0-9]{2}-[0-9]{2}T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?(Z|[+-]([01][0-9]|2[0-3]):[0-5][0-9])$' then
        raise exception 'Real A1 evidence timestamp required' using errcode='23514';
    end if;
    -- Validate the calendar independently: the Python contract accepts offsets
    -- up to 23:59, wider than PostgreSQL's timestamptz displacement limit.
    -- Fraction/offset syntax is checked above; retain the exact original text.
    perform substring(ev->>'recorded_at',1,19)::timestamp;
    foreach lifecycle in array array['acquisition_state','verification_state','approval_state','content_review_state'] loop
        if p_expected_register->lifecycle is distinct from jsonb_build_object(
            'state',case when lifecycle='approval_state' then 'not_requested' else 'pending' end,
            'evidence_ref',null) then
            raise exception 'A1 requires initial source lifecycle states' using errcode='23514';
        end if;
    end loop;
    if p_expected_register->'approval_id' is distinct from 'null'::jsonb
       or jsonb_typeof(p_expected_register->'evidence') is distinct from 'array' then
        raise exception 'Initial source approval and evidence required' using errcode='23514';
    end if;
    if exists(select 1 from jsonb_array_elements(p_expected_register->'evidence') e
        where e->>'evidence_id'=ev->>'evidence_id') then
        raise exception 'Duplicate A1 evidence ID' using errcode='23514';
    end if;
    proposed := jsonb_set(jsonb_set(p_expected_register,'{acquisition_state}',
        jsonb_build_object('state','observed','evidence_ref',ev->'evidence_id')),
        '{evidence}',(p_expected_register->'evidence') || jsonb_build_array(ev));

    perform bintanong_private.publication_lock();
    select to_jsonb(v)-'created_at' into actual from public.document_versions v
        where v.version_id=p_expected_register->>'version_id' for update;
    if not found then
        raise exception 'Source version is not registered' using errcode='23514';
    end if;
    if exists(select 1 from public.release_document_versions rv join public.knowledge_releases r using(release_id)
        where rv.version_id=p_expected_register->>'version_id' and r.published_at is not null) then
        raise exception 'Published source versions are immutable' using errcode='55000';
    end if;
    stored := actual->'source_register';
    if jsonb_typeof(stored) is distinct from 'object' then
        raise exception 'Legacy null source registers cannot be observed' using errcode='23514';
    end if;
    if stored=proposed then
        target := proposed;
    elsif stored=p_expected_register then
        target := p_expected_register;
    else
        raise exception 'Source register changed; expected record conflict' using errcode='23514';
    end if;
    -- Same complete projection as pending registration; replay must match it too.
    projected := jsonb_build_object(
        'version_id',target->'version_id','document_id',target->'document_id','edition_id',target->'edition_id',
        'filename',target->'filename','byte_sha256',target->'byte_sha256','acquisition_locators',target->'acquisition_locators',
        'acquisition_state',target#>'{acquisition_state,state}','verification_state',target#>'{verification_state,state}',
        'approval_state',target#>'{approval_state,state}','content_review_state',target#>'{content_review_state,state}',
        'source_register',target) || (select jsonb_object_agg(key,value) from jsonb_each(target)
            where key=any(array['issuer','campus','college','program','cohort','printed_revision',
                'effective_from','effective_to','supersession']));
    if actual is distinct from projected then
        raise exception 'Source relational metadata differs from its register' using errcode='23514';
    end if;
    if stored=proposed then
        return stored;
    end if;
    update public.document_versions set acquisition_state='observed',source_register=proposed
        where version_id=p_expected_register->>'version_id';
    return proposed;
end; $$;

revoke all on function public.observe_source_acquisition(jsonb,jsonb) from public,anon,authenticated;
grant execute on function public.observe_source_acquisition(jsonb,jsonb) to service_role;
