-- Phase 4: Supabase Vector and Relational Knowledge Schema
-- Compliant with Master Implementation Plan Section 9.1 & 9.2

-- Ensure pgvector extension is available in schema extensions
create extension if not exists vector with schema extensions;

-- ============================================================================
-- 1. Documents & Document Versions
-- ============================================================================
create table if not exists public.documents (
    document_id text primary key,
    namespace text not null default 'institutional' check (namespace in ('institutional')),
    synthetic boolean not null default false,
    document_category text not null check (document_category in (
        'curriculum_prospectus', 'academic_handbook', 'institutional_statute',
        'administrative_order', 'enrollment_guideline'
    )),
    title text not null,
    created_at timestamptz not null default now()
);

create table if not exists public.document_versions (
    version_id text primary key,
    document_id text not null references public.documents(document_id) on delete cascade,
    edition_id text not null,
    filename text not null,
    byte_sha256 text not null check (byte_sha256 ~ '^[0-9a-f]{64}$'),
    acquisition_locators text[] not null default '{}',
    issuer jsonb not null default '{}'::jsonb,
    campus jsonb not null default '{}'::jsonb,
    college jsonb not null default '{}'::jsonb,
    program jsonb not null default '{}'::jsonb,
    cohort jsonb not null default '{}'::jsonb,
    printed_revision jsonb not null default '{}'::jsonb,
    effective_from jsonb not null default '{}'::jsonb,
    effective_to jsonb not null default '{}'::jsonb,
    supersession jsonb not null default '{}'::jsonb,
    acquisition_state text not null default 'discovered',
    verification_state text not null default 'pending',
    approval_state text not null default 'unapproved',
    content_review_state text not null default 'unreviewed',
    created_at timestamptz not null default now()
);
create index if not exists idx_document_versions_doc_id on public.document_versions(document_id);
create index if not exists idx_document_versions_sha256 on public.document_versions(byte_sha256);

-- ============================================================================
-- 2. Chunks & Source Spans
-- ============================================================================
create table if not exists public.chunks (
    chunk_id text primary key check (chunk_id ~ '^[0-9a-f]{64}$'),
    chunk_type text not null check (chunk_type in (
        'policy', 'prospectus_schedule', 'prospectus_note',
        'administrative_procedure', 'curriculum_table'
    )),
    chunker_version text not null default 'palsu-chunker-v1',
    document_id text references public.documents(document_id) on delete set null,
    version_id text references public.document_versions(version_id) on delete set null,
    edition_id text,
    byte_sha256 text not null check (byte_sha256 ~ '^[0-9a-f]{64}$'),
    anchored boolean not null default true,
    source_verification text not null default 'pending',
    content_review text not null default 'pending',
    text text not null,
    source_text text not null,
    section_path text[] not null default '{}',
    scope text[] not null default '{}',
    content_hash text not null check (content_hash ~ '^[0-9a-f]{64}$'),
    token_count jsonb not null default '{}'::jsonb,
    source_label text not null default '',
    type_fields jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);
create index if not exists idx_chunks_version_id on public.chunks(version_id);
create index if not exists idx_chunks_sha256 on public.chunks(byte_sha256);
create index if not exists idx_chunks_content_hash on public.chunks(content_hash);
create index if not exists idx_chunks_type on public.chunks(chunk_type);

create table if not exists public.source_spans (
    span_id uuid primary key default gen_random_uuid(),
    chunk_id text not null references public.chunks(chunk_id) on delete cascade,
    byte_sha256 text not null check (byte_sha256 ~ '^[0-9a-f]{64}$'),
    version_id text references public.document_versions(version_id) on delete set null,
    page integer,
    printed_page_label text,
    locator jsonb not null default '{}'::jsonb,
    text text not null,
    bbox jsonb,
    bbox_origin text,
    page_size jsonb,
    extraction jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);
create index if not exists idx_source_spans_chunk_id on public.source_spans(chunk_id);
create index if not exists idx_source_spans_sha256 on public.source_spans(byte_sha256);

-- ============================================================================
-- 3. Embedding Sets & Chunk Embeddings (pgvector 1024 dims)
-- ============================================================================
create table if not exists public.embedding_sets (
    embedding_set_id text primary key,
    schema_version text not null default 'bintanong-embedding-manifest-v1',
    model_id text not null,
    model_revision text not null,
    dimension integer not null check (dimension = 1024),
    normalization text not null check (normalization in ('l2', 'none')),
    prompt_fingerprint text not null check (prompt_fingerprint ~ '^[0-9a-f]{64}$'),
    preprocessing_fingerprint text not null check (preprocessing_fingerprint ~ '^[0-9a-f]{64}$'),
    tokenizer_fingerprint text not null check (tokenizer_fingerprint ~ '^[0-9a-f]{64}$'),
    total_chunks integer not null default 0,
    created_at timestamptz not null default now()
);

create table if not exists public.chunk_embeddings (
    chunk_id text not null references public.chunks(chunk_id) on delete cascade,
    embedding_set_id text not null references public.embedding_sets(embedding_set_id) on delete cascade,
    chunk_content_hash text not null check (chunk_content_hash ~ '^[0-9a-f]{64}$'),
    embedding extensions.vector(1024) not null,
    token_count jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    primary key (chunk_id, embedding_set_id)
);
create index if not exists idx_chunk_embeddings_set on public.chunk_embeddings(embedding_set_id);

-- ============================================================================
-- 4. Institutional Entities: Programs, Curricula, Courses, Aliases
-- ============================================================================
create table if not exists public.programs (
    program_code text primary key,
    name text not null,
    college text not null,
    campus text not null default 'Main',
    effective_years text,
    created_at timestamptz not null default now()
);

create table if not exists public.curriculum_versions (
    curriculum_version_id text primary key,
    program_code text not null references public.programs(program_code) on delete cascade,
    revision_year integer,
    document_version_id text references public.document_versions(version_id) on delete set null,
    total_units integer,
    approval_status text not null default 'draft' check (approval_status in ('draft', 'reviewed', 'authorized', 'superseded')),
    created_at timestamptz not null default now()
);
create index if not exists idx_curriculum_versions_program on public.curriculum_versions(program_code);

create table if not exists public.courses (
    course_id text primary key,
    program_code text not null references public.programs(program_code) on delete cascade,
    curriculum_version_id text references public.curriculum_versions(curriculum_version_id) on delete set null,
    course_code text not null,
    course_title text not null,
    units_lecture numeric(4, 1) not null default 0.0,
    units_lab numeric(4, 1) not null default 0.0,
    units_credit numeric(4, 1) not null default 0.0,
    year_level integer check (year_level between 1 and 6),
    semester text check (semester in ('1st Semester', '2nd Semester', 'Midyear', 'Summer')),
    raw_prerequisites text,
    is_elective boolean not null default false,
    created_at timestamptz not null default now()
);
create index if not exists idx_courses_program on public.courses(program_code);
create index if not exists idx_courses_curriculum on public.courses(curriculum_version_id);
create index if not exists idx_courses_code on public.courses(course_code);

create table if not exists public.course_aliases (
    alias_id uuid primary key default gen_random_uuid(),
    canonical_course_id text not null references public.courses(course_id) on delete cascade,
    raw_code text not null,
    alias_context text,
    created_at timestamptz not null default now(),
    unique (canonical_course_id, raw_code)
);
create index if not exists idx_course_aliases_raw on public.course_aliases(raw_code);

-- ============================================================================
-- 5. Policy Rules & Provenance Spans
-- ============================================================================
create table if not exists public.policy_rules (
    rule_id text primary key,
    rule_name text not null,
    category text not null check (category in (
        'admission', 'retention', 'prerequisite', 'graduation',
        'grading', 'shiftee', 'general_policy'
    )),
    scope jsonb not null default '{}'::jsonb,
    prolog_predicate text,
    specification text not null,
    approval_state text not null default 'candidate' check (approval_state in ('candidate', 'reviewed', 'authorized', 'rejected')),
    created_at timestamptz not null default now()
);

create table if not exists public.rule_source_spans (
    rule_id text not null references public.policy_rules(rule_id) on delete cascade,
    span_id uuid not null references public.source_spans(span_id) on delete cascade,
    provenance_role text not null default 'primary_source' check (provenance_role in ('primary_source', 'corroborating_source', 'superseded_source')),
    primary key (rule_id, span_id)
);
create index if not exists idx_rule_source_spans_span on public.rule_source_spans(span_id);

-- ============================================================================
-- 6. Knowledge Releases & Memberships
-- ============================================================================
create table if not exists public.knowledge_releases (
    release_id text primary key,
    release_version text not null unique,
    description text not null,
    embedding_set_id text not null references public.embedding_sets(embedding_set_id) on delete restrict,
    status text not null default 'draft' check (status in ('draft', 'active', 'superseded', 'revoked')),
    published_at timestamptz,
    published_by text,
    created_at timestamptz not null default now()
);

create table if not exists public.release_document_versions (
    release_id text not null references public.knowledge_releases(release_id) on delete cascade,
    version_id text not null references public.document_versions(version_id) on delete cascade,
    primary key (release_id, version_id)
);

create table if not exists public.release_chunks (
    release_id text not null references public.knowledge_releases(release_id) on delete cascade,
    chunk_id text not null references public.chunks(chunk_id) on delete cascade,
    primary key (release_id, chunk_id)
);
create index if not exists idx_release_chunks_chunk on public.release_chunks(chunk_id);

create table if not exists public.release_rules (
    release_id text not null references public.knowledge_releases(release_id) on delete cascade,
    rule_id text not null references public.policy_rules(rule_id) on delete cascade,
    primary key (release_id, rule_id)
);

-- ============================================================================
-- 7. Active Release Singleton Pointer
-- ============================================================================
create table if not exists public.active_release (
    id integer primary key default 1 check (id = 1),
    release_id text not null references public.knowledge_releases(release_id) on delete restrict,
    activated_at timestamptz not null default now(),
    activated_by text not null default 'system'
);

-- ============================================================================
-- 8. Run Logs (Ingestion & Evaluation)
-- ============================================================================
create table if not exists public.ingestion_runs (
    run_id text primary key,
    runner_version text not null,
    started_at timestamptz not null default now(),
    completed_at timestamptz,
    status text not null check (status in ('running', 'completed', 'failed')),
    summary jsonb not null default '{}'::jsonb
);

create table if not exists public.evaluation_runs (
    eval_id text primary key,
    release_id text references public.knowledge_releases(release_id) on delete set null,
    framework text not null default 'ragas-deepeval',
    metrics jsonb not null default '{}'::jsonb,
    executed_at timestamptz not null default now()
);
