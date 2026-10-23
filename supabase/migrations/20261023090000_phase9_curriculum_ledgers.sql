-- Reviewed curriculum prerequisite ledgers (owner decision 23 October 2026: load the reviewed
-- programs into hosted Supabase). Each ledger is stored verbatim as authored and reviewed; the
-- runtime rebuilds and re-verifies it before generating its Prolog bundle. Ledgers never carry
-- activation, and runtime roles read only ledgers linked to an active research release.
create table public.curriculum_ledgers (
    ledger_sha256 text primary key check (ledger_sha256 ~ '^[0-9a-f]{64}$'),
    program_id text not null,
    curriculum_id text not null,
    ledger jsonb not null,
    created_at timestamptz not null default now(),
    unique (ledger_sha256, curriculum_id),
    constraint p9_ledger_binding check (
        ledger->>'content_sha256' = ledger_sha256
        and ledger#>>'{scope,curriculum_id}' = curriculum_id
        and ledger#>>'{scope,program_id}' = program_id
        and ledger->'activation_allowed' = 'false'::jsonb)
);

create table public.release_curriculum_ledgers (
    release_id text not null references public.knowledge_releases(release_id) on delete cascade,
    curriculum_id text not null,
    ledger_sha256 text not null,
    primary key (release_id, curriculum_id),
    foreign key (ledger_sha256, curriculum_id)
        references public.curriculum_ledgers(ledger_sha256, curriculum_id) on delete restrict
);
create index idx_release_curriculum_ledgers_ledger on public.release_curriculum_ledgers(ledger_sha256);

alter table public.curriculum_ledgers enable row level security;
alter table public.release_curriculum_ledgers enable row level security;
revoke insert, update, delete, truncate on public.curriculum_ledgers, public.release_curriculum_ledgers
    from anon, authenticated;
grant select on public.curriculum_ledgers, public.release_curriculum_ledgers to anon, authenticated;

create policy p9_release_curriculum_ledgers_select_active on public.release_curriculum_ledgers
    for select to anon, authenticated using (
        exists(select 1 from public.knowledge_releases kr
            where kr.release_id = release_curriculum_ledgers.release_id
              and kr.status = 'active' and kr.release_kind = 'research'));

create policy p9_curriculum_ledgers_select_active on public.curriculum_ledgers
    for select to anon, authenticated using (
        exists(select 1 from public.release_curriculum_ledgers rcl
            join public.knowledge_releases kr on kr.release_id = rcl.release_id
            where rcl.ledger_sha256 = curriculum_ledgers.ledger_sha256
              and kr.status = 'active' and kr.release_kind = 'research'));
