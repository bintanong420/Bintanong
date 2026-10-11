"""Disposable PostgreSQL database for storage integration tests (no shared reset)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import uuid

from backend.bintanong_storage.client import PermissionDeniedError, StorageError
from backend.bintanong_contracts.source import compute_content_hash

REPO = Path(__file__).resolve().parents[1]


class StorageDatabase:
    def __init__(self, migration_max=None):
        self.container = os.environ.get("BINTANONG_STORAGE_TEST_CONTAINER", "supabase_db_Bintanong")
        self.name = "bintanong_storage_test_" + uuid.uuid4().hex
        self.evidence = Path(os.environ.get("BINTANONG_STORAGE_EVIDENCE_DIR", tempfile.gettempdir())) / self.name
        self.evidence.mkdir(parents=True, exist_ok=True)
        self.sequence = 0
        created = self._command("postgres", f'create database "{self.name}";')
        if created.returncode:
            raise AssertionError(created.stderr)
        try:
            self.execute("""
                create schema extensions;
                grant usage on schema public, extensions to anon, authenticated, service_role;
                alter default privileges for role postgres in schema public
                    grant all on tables to anon, authenticated, service_role;
                alter default privileges for role postgres in schema public
                    grant all on sequences to anon, authenticated, service_role;
                alter default privileges for role postgres in schema public
                    grant execute on functions to anon, authenticated, service_role;
            """)
            for migration in sorted((REPO / "supabase/migrations").glob("*.sql")):
                if migration_max is None or migration.name.split('_', 1)[0] <= migration_max:
                    self.execute(migration.read_text(encoding="utf-8"))
        except BaseException:
            self.close()
            raise

    def _command(self, database: str, sql: str):
        self.sequence += 1
        prefix = self.evidence / f"{self.sequence:03d}"
        prefix.with_suffix(".sql").write_text(sql, encoding="utf-8")
        result = subprocess.run(
            ["docker", "exec", "-i", self.container, "psql", "-U", "postgres", "-d", database,
             "-X", "-A", "-t", "-q", "-v", "ON_ERROR_STOP=1"],
            input=sql, text=True, encoding="utf-8", capture_output=True, timeout=60,
        )
        prefix.with_suffix(".out").write_text(result.stdout + result.stderr, encoding="utf-8")
        return result

    def execute(self, sql: str):
        result = self._command(self.name, sql)
        if result.returncode:
            raise AssertionError(result.stderr)
        return result.stdout.strip()

    def json(self, sql: str):
        lines = self.execute(sql).splitlines()
        return json.loads(lines[-1])

    def close(self):
        if not re.fullmatch(r"bintanong_storage_test_[0-9a-f]{32}", self.name):
            raise RuntimeError("refusing to drop an unrecognized database")
        result = self._command("postgres", f'drop database if exists "{self.name}" with (force);')
        if result.returncode:
            raise AssertionError(result.stderr)


def sql_literal(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


class DatabaseStorageClient:
    """Exercise the production loader/release methods against real role SQL.

    HTTP request construction has separate MockTransport tests; this adapter
    does not connect the shared PostgREST instance to a test database.
    """

    def __init__(self, db):
        self.db = db

    def rpc(self, function_name, params=None, role="runtime"):
        if not re.fullmatch(r"[a-z_]+", function_name):
            raise ValueError("invalid test function")
        arguments = []
        for key, value in (params or {}).items():
            if not re.fullmatch(r"[a-z_]+", key):
                raise ValueError("invalid test parameter")
            if key in ("p_chunk_ids", "p_document_version_ids", "p_rule_ids"):
                literal = "array[" + ",".join(sql_literal(x) for x in value) + "]::text[]"
            elif key == "query_embedding":
                literal = sql_literal(json.dumps(value)) + "::extensions.vector"
            elif isinstance(value, (dict, list)):
                literal = sql_literal(json.dumps(value)) + "::jsonb"
            else:
                literal = sql_literal(value)
            arguments.append(f"{key}=>{literal}")
        selected_role = "service_role" if role == "admin" else "anon"
        expression = f"public.{function_name}({','.join(arguments)})"
        if function_name == "match_chunks":
            query = f"select coalesce(jsonb_agg(to_jsonb(r)),'[]') from {expression} r;"
        else:
            query = f"select coalesce(to_jsonb({expression}),'null');"
        try:
            return self.db.json(f"begin; set local role {selected_role}; {query} commit;")
        except AssertionError as exc:
            error = PermissionDeniedError if "permission denied" in str(exc) else StorageError
            raise error(str(exc)) from exc

    def select(self, table, columns="*", filters=None, role="runtime"):
        if not re.fullmatch(r"[a-z_]+", table) or columns != "*":
            raise ValueError("unsupported test select")
        predicates = []
        for key, expression in (filters or {}).items():
            if not re.fullmatch(r"[a-z_]+", key) or not expression.startswith("eq."):
                raise ValueError("unsupported test filter")
            predicates.append(f"{key}={sql_literal(expression[3:])}")
        where = "where " + " and ".join(predicates) if predicates else ""
        selected_role = "service_role" if role == "admin" else "anon"
        return self.db.json(f"begin; set local role {selected_role}; select coalesce(jsonb_agg(to_jsonb(t)),'[]') from public.{table} t {where}; commit;")


FIXTURE = """
begin;
set local lock_timeout = '3s';
set local statement_timeout = '20s';
insert into public.documents(document_id,document_category,title,synthetic) values
 ('doc-test','academic_handbook','Synthetic test corpus',true);
insert into public.document_versions(version_id,document_id,edition_id,filename,byte_sha256,
 verification_state,approval_state,content_review_state) values
 ('ver-test1','doc-test','edition-test','test.pdf',repeat('0',64),'verified','approved','reviewed'),
 ('ver-test2','doc-test','edition-test2','test2.pdf',repeat('1',64),'verified','approved','reviewed');
insert into public.programs(program_code,name,college) values ('TEST','Synthetic','Synthetic');
insert into public.curriculum_versions(curriculum_version_id,program_code,document_version_id,approval_status) values
 ('curriculum-test','TEST','ver-test1','authorized'),('curriculum-draft','TEST','ver-test1','draft');
insert into public.courses(course_id,program_code,curriculum_version_id,course_code,course_title) values
 ('course-test','TEST','curriculum-test','TEST1','Approved test course'),
 ('course-draft','TEST','curriculum-draft','DRAFT1','Unapproved test course');
insert into public.course_aliases(canonical_course_id,raw_code) values ('course-test','TEST-ALIAS'),('course-draft','DRAFT-ALIAS');
insert into public.embedding_sets(embedding_set_id,model_id,model_revision,dimension,normalization,
 prompt_fingerprint,preprocessing_fingerprint,tokenizer_fingerprint,total_chunks) values
 ('set-test','synthetic-model',repeat('2',64),1024,'l2',repeat('3',64),repeat('4',64),repeat('5',64),2);
insert into public.chunks(chunk_id,chunk_type,document_id,version_id,edition_id,byte_sha256,text,
 source_text,content_hash,source_verification,content_review) values
 (repeat('a',64),'policy','doc-test','ver-test1','edition-test',repeat('0',64),'Test one','Test one',repeat('c',64),'verified','reviewed'),
 (repeat('b',64),'policy','doc-test','ver-test2','edition-test2',repeat('1',64),'Test two','Test two',repeat('d',64),'verified','reviewed');
insert into public.source_spans(span_id,chunk_id,version_id,byte_sha256,text,page,locator) values
 ('11111111-1111-4111-8111-111111111111',repeat('a',64),'ver-test1',repeat('0',64),'Test one',1,'{"kind":"section","section_path":["Test"]}'),
 ('22222222-2222-4222-8222-222222222222',repeat('b',64),'ver-test2',repeat('1',64),'Test two',1,'{"kind":"section","section_path":["Test"]}');
insert into public.chunk_embeddings(chunk_id,embedding_set_id,chunk_content_hash,embedding) values
 (repeat('a',64),'set-test',repeat('c',64),('[' || '1,' || repeat('0,',1022) || '0]')::extensions.vector),
 (repeat('b',64),'set-test',repeat('d',64),('[' || '0,1,' || repeat('0,',1021) || '0]')::extensions.vector);
insert into public.policy_rules(rule_id,rule_name,category,specification,approval_state) values
 ('rule-test','Synthetic rule','general_policy','Reviewed specification','authorized'),
 ('rule-unreleased','Unreleased rule','general_policy','Unreleased specification','authorized'),
 ('rule-candidate','Candidate rule','general_policy','Candidate specification','candidate');
insert into public.rule_source_spans(rule_id,span_id) values
 ('rule-test','11111111-1111-4111-8111-111111111111'),
 ('rule-candidate','22222222-2222-4222-8222-222222222222');
insert into public.knowledge_releases(release_id,release_version,description,embedding_set_id) values
 ('release-test1','v-test1','Synthetic release one','set-test'),
 ('release-test2','v-test2','Synthetic release two','set-test');
insert into public.release_chunks(release_id,chunk_id) values ('release-test1',repeat('a',64)),('release-test2',repeat('b',64));
insert into public.release_document_versions(release_id,version_id) values ('release-test1','ver-test1'),('release-test2','ver-test2');
insert into public.release_rules(release_id,rule_id) values ('release-test1','rule-test');
do $$ begin
 if exists(select 1 from information_schema.columns where table_schema='public' and table_name='knowledge_releases' and column_name='expected_chunk_count') then
  execute 'update public.knowledge_releases set expected_chunk_count=1,expected_document_version_count=1,expected_rule_count=case when release_id=''release-test1'' then 1 else 0 end';
 end if;
end $$;
"""
FIXTURE = FIXTURE.replace("repeat('c',64)", "'" + compute_content_hash("Test one", "Test one") + "'")
FIXTURE = FIXTURE.replace("repeat('d',64)", "'" + compute_content_hash("Test two", "Test two") + "'")
