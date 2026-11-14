-- Scoped V1 observations of existing confirmed printed evidence, never V2/P2 authority.
create table public.source_verification_observations (
    version_id text not null references public.document_versions(version_id) on delete restrict on update restrict,
    evidence_id text not null check(evidence_id ~ '[^[:space:]]'),
    partial_review_evidence_id text not null,
    review_scope_id text not null references public.selected_release_reviews(review_scope_id) on delete restrict on update restrict,
    receipt jsonb not null check(jsonb_typeof(receipt)='object'),
    created_at timestamptz not null default now(),
    primary key(version_id,evidence_id),
    foreign key(version_id,partial_review_evidence_id) references public.source_partial_reviews(version_id,evidence_id)
        on delete restrict on update restrict
);
create index p5_source_observation_scope on public.source_verification_observations(review_scope_id);
create index p5_source_observation_c1 on public.source_verification_observations(version_id,partial_review_evidence_id);
alter table public.source_verification_observations enable row level security;
revoke all on public.source_verification_observations from public,anon,authenticated,service_role;
grant select,insert on public.source_verification_observations to service_role;
create policy p5_source_observation_runtime_denial on public.source_verification_observations
    as restrictive for all to anon,authenticated using(false) with check(false);
create trigger p5_source_observation_lock before insert on public.source_verification_observations
    for each statement execute function bintanong_private.lock_publication();
create trigger p5_source_observation_immutable before update or delete or truncate on public.source_verification_observations
    for each statement execute function bintanong_private.partial_review_immutable();

create function public.observe_source_verification(p_expected_register jsonb,p_observation jsonb)
returns jsonb language plpgsql volatile security invoker set search_path='' as $$
declare
    ev jsonb; c1 jsonb; selection jsonb; selected_source jsonb;
    actual jsonb; stored jsonb; proposed jsonb; target jsonb; projected jsonb; saved jsonb;
    at_time timestamptz; key text; selected_chunks jsonb; c1_chunks jsonb;
begin
    if jsonb_typeof(p_expected_register) is distinct from 'object'
       or not bintanong_private.partial_review_object(p_observation,array[
           'receipt_format','version_id','source_sha256','acquisition_locators',
           'partial_review_evidence_id','review_scope_id','observation_scope','evidence',
           'reviewer_label','compiler_label','timestamp_meaning']) then
        raise exception 'Closed selected-source observation required' using errcode='23514';
    end if;
    foreach key in array array['version_id','source_sha256','partial_review_evidence_id',
            'review_scope_id','reviewer_label','compiler_label','timestamp_meaning'] loop
        if jsonb_typeof(p_observation->key) is distinct from 'string'
           or p_observation->>key !~ '[^[:space:]]' then
            raise exception 'Nonblank observation identity/reference/label required' using errcode='23514';
        end if;
    end loop;
    if p_observation->'receipt_format' is distinct from '"selected-source-observation-v1"'::jsonb
       or p_observation->'observation_scope' is distinct from '"selected_reviewed_spans"'::jsonb
       or p_observation->>'review_scope_id' !~ '^[0-9a-f]{64}$'
       or p_observation->>'source_sha256' !~ '^[0-9a-f]{64}$'
       or jsonb_typeof(p_observation->'acquisition_locators') is distinct from 'array'
       or p_observation->'version_id' is distinct from p_expected_register->'version_id'
       or p_observation->'source_sha256' is distinct from p_expected_register->'byte_sha256'
       or p_observation->'acquisition_locators' is distinct from p_expected_register->'acquisition_locators'
       or p_observation->'partial_review_evidence_id' is distinct from p_expected_register#>'{content_review_state,evidence_ref}' then
        raise exception 'Exact selected C1/source observation binding required' using errcode='23514';
    end if;
    ev:=p_observation->'evidence';
    if not bintanong_private.partial_review_object(ev,array['evidence_id','kind','recorded_by','recorded_at','authorization_ref'])
       or jsonb_typeof(ev->'evidence_id') is distinct from 'string'
       or ev->>'evidence_id' !~ '[^[:space:]]'
       or ev->'kind' is distinct from '"printed_text_span"'::jsonb
       or ev->'recorded_by' is distinct from '"reviewer"'::jsonb
       or ev->'authorization_ref' is distinct from 'null'::jsonb
       or jsonb_typeof(ev->'recorded_at') is distinct from 'string' then
        raise exception 'Distinct V1 reviewer printed-span evidence required' using errcode='23514';
    end if;
    at_time:=bintanong_private.acquisition_check_time(ev->>'recorded_at');
    if p_expected_register->'verification_state' is distinct from '{"state":"pending","evidence_ref":null}'::jsonb
       or p_expected_register->'approval_state' is distinct from '{"state":"not_requested","evidence_ref":null}'::jsonb
       or p_expected_register->'approval_id' is distinct from 'null'::jsonb
       or p_expected_register#>'{acquisition_state,state}' is distinct from '"verified"'::jsonb
       or jsonb_typeof(p_expected_register#>'{acquisition_state,evidence_ref}') is distinct from 'string'
       or p_expected_register->'content_review_state' is distinct from jsonb_build_object(
           'state','partially_reviewed','evidence_ref',p_observation->'partial_review_evidence_id')
       or jsonb_typeof(p_expected_register->'evidence') is distinct from 'array' then
        raise exception 'V1 requires verified acquisition, partial review and pending verification/approval' using errcode='23514';
    end if;
    if p_expected_register->'acquisition_state' is distinct from jsonb_build_object(
        'state','verified','evidence_ref',p_expected_register#>'{acquisition_state,evidence_ref}')
       or exists(select 1 from jsonb_array_elements(p_expected_register->'evidence') e
           where jsonb_typeof(e) is distinct from 'object'
              or jsonb_typeof(e->'evidence_id') is distinct from 'string'
              or e->'evidence_id'=ev->'evidence_id')
       or (select count(*) from jsonb_array_elements(p_expected_register->'evidence'))<>
           (select count(distinct e->>'evidence_id') from jsonb_array_elements(p_expected_register->'evidence') e) then
        raise exception 'Closed acquisition state and distinct V1 evidence required' using errcode='23514';
    end if;
    proposed:=jsonb_set(jsonb_set(p_expected_register,'{verification_state}',
        jsonb_build_object('state','observed','evidence_ref',ev->'evidence_id')),
        '{evidence}',(p_expected_register->'evidence') || jsonb_build_array(ev));

    perform bintanong_private.publication_lock();
    select to_jsonb(v)-'created_at' into actual from public.document_versions v
        where v.version_id=p_observation->>'version_id' for update;
    if not found then
        raise exception 'Registered observation source required' using errcode='23514';
    end if;
    if exists(select 1 from public.release_document_versions rv join public.knowledge_releases r using(release_id)
        where rv.version_id=p_observation->>'version_id' and r.published_at is not null) then
        raise exception 'Published source versions are immutable' using errcode='55000';
    end if;
    stored:=actual->'source_register';
    if jsonb_typeof(stored) is distinct from 'object' then
        raise exception 'Nonlegacy source register required' using errcode='23514';
    end if;
    select receipt into c1 from public.source_partial_reviews
        where version_id=p_observation->>'version_id' and evidence_id=p_observation->>'partial_review_evidence_id';
    select receipt into selection from public.selected_release_reviews
        where review_scope_id=p_observation->>'review_scope_id';
    if c1 is null or selection is null then
        raise exception 'Stored C1 and selected-review receipts required' using errcode='23514';
    end if;
    perform bintanong_private.validate_selected_review(selection);
    select value into selected_source from jsonb_array_elements(selection->'sources')
        where value->'version_id'=p_observation->'version_id';
    if selected_source is null
       or selected_source->'source_sha256' is distinct from p_observation->'source_sha256'
       or selected_source->'partial_review_evidence_id' is distinct from p_observation->'partial_review_evidence_id'
       or c1->'source_sha256' is distinct from p_observation->'source_sha256'
       or c1->'acquisition_locators' is distinct from p_observation->'acquisition_locators'
       or c1->'reviewer_label' is distinct from p_observation->'reviewer_label'
       or not coalesce(p_expected_register->'evidence' @> jsonb_build_array(c1->'evidence'),false)
       or at_time<bintanong_private.acquisition_check_time(c1#>>'{evidence,recorded_at}')
       or at_time<bintanong_private.acquisition_check_time(selection#>>'{decision,recorded_at}') then
        raise exception 'Exact C1/source/selection attribution and ordered compilation required' using errcode='23514';
    end if;
    select jsonb_agg(value order by value->>'chunk_id' collate "C") into selected_chunks
        from jsonb_array_elements(selection->'chunks') where value#>'{spans,0,version_id}'=p_observation->'version_id';
    select jsonb_agg(value order by value->>'chunk_id' collate "C") into c1_chunks
        from jsonb_array_elements(c1->'chunks');
    if selected_chunks is null or selected_chunks is distinct from c1_chunks then
        raise exception 'Complete C1 selected source snapshots required' using errcode='23514';
    end if;
    if stored=proposed then target:=proposed;
    elsif stored=p_expected_register then target:=p_expected_register;
    else raise exception 'Source register changed; expected record conflict' using errcode='23514';
    end if;
    projected:=jsonb_build_object(
        'version_id',target->'version_id','document_id',target->'document_id','edition_id',target->'edition_id',
        'filename',target->'filename','byte_sha256',target->'byte_sha256','acquisition_locators',target->'acquisition_locators',
        'acquisition_state',target#>'{acquisition_state,state}','verification_state',target#>'{verification_state,state}',
        'approval_state',target#>'{approval_state,state}','content_review_state',target#>'{content_review_state,state}',
        'source_register',target) || (select jsonb_object_agg(attrs.key,attrs.value) from jsonb_each(target) attrs
            where attrs.key=any(array['issuer','campus','college','program','cohort','printed_revision',
                'effective_from','effective_to','supersession']));
    if actual is distinct from projected then
        raise exception 'Source relational metadata differs from its register' using errcode='23514';
    end if;
    select receipt into saved from public.source_verification_observations
        where version_id=p_observation->>'version_id' and evidence_id=ev->>'evidence_id';
    if stored=proposed then
        if saved is distinct from p_observation then
            raise exception 'V1 replay receipt missing or changed' using errcode='23514';
        end if;
        return stored;
    end if;
    if saved is not null then
        raise exception 'V1 receipt exists without its source transition' using errcode='23514';
    end if;
    insert into public.source_verification_observations(version_id,evidence_id,partial_review_evidence_id,review_scope_id,receipt)
        values(p_observation->>'version_id',ev->>'evidence_id',p_observation->>'partial_review_evidence_id',
            p_observation->>'review_scope_id',p_observation);
    update public.document_versions set verification_state='observed',source_register=proposed
        where version_id=p_observation->>'version_id';
    return proposed;
end; $$;

revoke all on function public.observe_source_verification(jsonb,jsonb) from public,anon,authenticated;
grant execute on function public.observe_source_verification(jsonb,jsonb) to service_role;
