-- A2 byte acquisition only, after existing C1; never issuing-office verification.
-- Python's existing datetime parser normalizes offset minutes through 99 when
-- their total displacement stays below 24 hours. Keep that contract's acceptance
-- without changing the earlier C1 parser or original timestamp text in JSON.
create function bintanong_private.acquisition_check_time(v text) returns timestamptz
language plpgsql immutable security invoker set search_path='' as $$
declare displacement text; minutes integer; normalized text;
begin
    if v is null then
        raise exception 'Real A2 timestamp required' using errcode='23514';
    end if;
    if right(v,1)='Z' then
        return bintanong_private.partial_review_time(v);
    end if;
    displacement:=right(v,6);
    if displacement !~ '^[+-][0-9]{2}:[0-9]{2}$' then
        raise exception 'Real A2 timestamp offset required' using errcode='23514';
    end if;
    minutes:=substring(displacement,2,2)::integer*60+substring(displacement,5,2)::integer;
    if minutes>=1440 then
        raise exception 'A2 timestamp displacement must be less than 24 hours' using errcode='23514';
    end if;
    normalized:=left(v,length(v)-6)||left(displacement,1)||lpad((minutes/60)::text,2,'0')||':'||lpad((minutes%60)::text,2,'0');
    return bintanong_private.partial_review_time(normalized);
end; $$;

revoke all on function bintanong_private.acquisition_check_time(text) from public,anon,authenticated;
grant execute on function bintanong_private.acquisition_check_time(text) to service_role;

create function public.verify_source_acquisition(p_expected_register jsonb,p_check jsonb)
returns jsonb language plpgsql volatile security invoker set search_path='' as $$
declare
    ev jsonb; prior jsonb; e jsonb;
    proposed jsonb; actual jsonb; stored jsonb; target jsonb; projected jsonb;
    evidence_at timestamptz; prior_at timestamptz;
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
    ev:=p_check->'evidence';
    if (select count(*) from jsonb_object_keys(ev))<>5
       or not ev ?& array['evidence_id','kind','recorded_by','recorded_at','authorization_ref']
       or jsonb_typeof(ev->'evidence_id') is distinct from 'string'
       or ev->>'evidence_id' !~ '[^[:space:]]'
       or ev->'kind' is distinct from '"byte_hash_check"'::jsonb
       or jsonb_typeof(ev->'recorded_by') is distinct from 'string'
       or ev->>'recorded_by' not in ('reviewer','system')
       or ev->'authorization_ref' is distinct from 'null'::jsonb
       or jsonb_typeof(ev->'recorded_at') is distinct from 'string' then
        raise exception 'Distinct A2 byte-check evidence required' using errcode='23514';
    end if;
    -- Reuse the existing contract-compatible parser: calendar validation, wide
    -- offsets and microsecond truncation, without changing original JSON text.
    evidence_at:=bintanong_private.acquisition_check_time(ev->>'recorded_at');
    if p_expected_register->'verification_state' is distinct from
           '{"state":"pending","evidence_ref":null}'::jsonb
       or p_expected_register->'approval_state' is distinct from
           '{"state":"not_requested","evidence_ref":null}'::jsonb
       or p_expected_register->'approval_id' is distinct from 'null'::jsonb
       or p_expected_register#>'{acquisition_state,state}' is distinct from '"observed"'::jsonb
       or jsonb_typeof(p_expected_register#>'{acquisition_state,evidence_ref}') is distinct from 'string'
       or p_expected_register#>'{content_review_state,state}' is distinct from '"partially_reviewed"'::jsonb
       or jsonb_typeof(p_expected_register#>'{content_review_state,evidence_ref}') is distinct from 'string'
       or jsonb_typeof(p_expected_register->'evidence') is distinct from 'array' then
        raise exception 'A2 requires observed acquisition and existing partial content review only' using errcode='23514';
    end if;
    if p_expected_register->'acquisition_state' is distinct from jsonb_build_object(
           'state','observed','evidence_ref',p_expected_register#>'{acquisition_state,evidence_ref}')
       or p_expected_register->'content_review_state' is distinct from jsonb_build_object(
           'state','partially_reviewed','evidence_ref',p_expected_register#>'{content_review_state,evidence_ref}') then
        raise exception 'Closed A2 source state references required' using errcode='23514';
    end if;
    if exists(select 1 from jsonb_array_elements(p_expected_register->'evidence') x
        where jsonb_typeof(x) is distinct from 'object'
           or jsonb_typeof(x->'evidence_id') is distinct from 'string'
           or x->>'evidence_id'=ev->>'evidence_id')
       or (select count(*) from jsonb_array_elements(p_expected_register->'evidence'))<>
           (select count(distinct x->>'evidence_id') from jsonb_array_elements(p_expected_register->'evidence') x) then
        raise exception 'Distinct A2 evidence IDs required' using errcode='23514';
    end if;
    select x into prior from jsonb_array_elements(p_expected_register->'evidence') x
        where x->'evidence_id'=p_expected_register#>'{acquisition_state,evidence_ref}';
    if prior is null then
        raise exception 'Cited A1 observation required' using errcode='23514';
    end if;
    if (select count(*) from jsonb_object_keys(prior))<>5
       or not prior ?& array['evidence_id','kind','recorded_by','recorded_at','authorization_ref']
       or prior->>'evidence_id' !~ '[^[:space:]]'
       or prior->'kind' is distinct from '"byte_hash_check"'::jsonb
       or jsonb_typeof(prior->'recorded_by') is distinct from 'string'
       or prior->>'recorded_by' not in ('researcher','reviewer','system')
       or prior->'authorization_ref' is distinct from 'null'::jsonb
       or jsonb_typeof(prior->'recorded_at') is distinct from 'string' then
        raise exception 'Cited valid A1 byte observation required' using errcode='23514';
    end if;
    prior_at:=bintanong_private.acquisition_check_time(prior->>'recorded_at');
    if evidence_at<prior_at then
        raise exception 'A2 check precedes the cited A1 observation' using errcode='23514';
    end if;
    -- Retain the actual existing C1 reference; acquisition does not create a review.
    select x into e from jsonb_array_elements(p_expected_register->'evidence') x
        where x->'evidence_id'=p_expected_register#>'{content_review_state,evidence_ref}';
    if e is null or e->'kind' is distinct from '"content_review_record"'::jsonb
       or e->'recorded_by' is distinct from '"reviewer"'::jsonb
       or e->'authorization_ref' is distinct from 'null'::jsonb then
        raise exception 'Existing C1 partial-review evidence required' using errcode='23514';
    end if;
    proposed:=jsonb_set(jsonb_set(p_expected_register,'{acquisition_state}',
        jsonb_build_object('state','verified','evidence_ref',ev->'evidence_id')),
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
    stored:=actual->'source_register';
    if jsonb_typeof(stored) is distinct from 'object' then
        raise exception 'Legacy null source registers cannot be verified' using errcode='23514';
    end if;
    if stored=proposed then
        target:=proposed;
    elsif stored=p_expected_register then
        target:=p_expected_register;
    else
        raise exception 'Source register changed; expected record conflict' using errcode='23514';
    end if;
    projected:=jsonb_build_object(
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
    update public.document_versions set acquisition_state='verified',source_register=proposed
        where version_id=p_expected_register->>'version_id';
    return proposed;
end; $$;

revoke all on function public.verify_source_acquisition(jsonb,jsonb) from public,anon,authenticated;
grant execute on function public.verify_source_acquisition(jsonb,jsonb) to service_role;
