"""Local-only inactive draft staging; every test uses an in-memory fake client, never a database."""
import copy
import importlib
import json

import pytest

from backend.bintanong_storage.client import StorageError
from backend.bintanong_tools.knowledge_update.build import build, load_package
from test_knowledge_update_build import reviewed, SyntheticEncoder  # noqa: F401 (fixture)

LOCAL = 'http://127.0.0.1:54321'
SECRET = 'service-role-secret-that-must-never-appear'


def api():
    return importlib.import_module('backend.bintanong_tools.knowledge_update.local_release')


def _values(spec):
    inner = spec[len('in.('):-1]
    return {v.strip('"') for v in inner.split(',')} if inner else set()


class FakeClient:
    """Emulates the PostgREST surface the loaders use, with the migrations' identity rules."""

    def __init__(self, base_url=LOCAL + '/rest/v1'):
        self.base_url = base_url
        self.config = type('Config', (), {'service_role_key': SECRET, 'anon_key': 'anon-' + SECRET})()
        self.tables = {name: [] for name in ('documents', 'document_versions', 'embedding_sets', 'chunks',
            'chunk_embeddings', 'knowledge_releases', 'release_chunks', 'release_document_versions',
            'active_release')}
        self.tables['active_release'].append({'release_id': 'prior-active'})
        self.tables['knowledge_releases'].append({'release_id': 'prior-active', 'release_version': 'v-prior',
            'status': 'active', 'embedding_set_id': 'x'})
        self.calls, self.fail, self.after = [], {}, {}

    def select(self, table, columns='*', filters=None, role='runtime'):
        self.calls.append(('select', table, role))
        filters = dict(filters or {})
        limit, offset = int(filters.pop('limit', 10 ** 9)), int(filters.pop('offset', 0))
        order = filters.pop('order', None)
        rows = [r for r in self.tables[table] if all(
            str(r.get(k)) == v[3:] if v.startswith('eq.') else str(r.get(k)) in _values(v)
            for k, v in filters.items())]
        if order:
            rows.sort(key=lambda r: str(r[order.split('.')[0]]))
        cols = None if columns == '*' else columns.split(',')
        return [copy.deepcopy(r if cols is None else {c: r.get(c) for c in cols}) for r in rows[offset:offset + limit]]

    def rpc(self, name, params=None, role='runtime'):
        self.calls.append(('rpc', name, role))
        if name in self.fail:
            raise self.fail[name]
        result = getattr(self, '_' + name)(params)
        if name in self.after:
            self.after[name](self)
        return result

    def _register_pending_sources(self, p):
        for d in p['p_documents']:
            prior = [r for r in self.tables['documents'] if r['document_id'] == d['document_id']]
            if prior and prior[0] != d:
                raise StorageError('Document identity conflicts with registered metadata', 400)
            if not prior:
                self.tables['documents'].append(dict(d))
        for v in p['p_versions']:
            prior = [r for r in self.tables['document_versions'] if r['version_id'] == v['version_id']]
            if prior and prior[0]['source_register'] != v:
                raise StorageError('Source version identity conflicts with registered evidence', 400)
            if not prior:
                self.tables['document_versions'].append({'version_id': v['version_id'], 'document_id': v['document_id'],
                    'byte_sha256': v['byte_sha256'], 'source_register': copy.deepcopy(v)})

    def _load_knowledge_batch(self, p):
        set_id = p['p_embedding_set']['embedding_set_id']
        present = {(r['chunk_id'], r['embedding_set_id']) for r in self.tables['chunk_embeddings']}
        already = sum((r['chunk_id'], set_id) in present for r in p['p_embeddings'])
        if not any(r['embedding_set_id'] == set_id for r in self.tables['embedding_sets']):
            self.tables['embedding_sets'].append(dict(p['p_embedding_set']))
        for table, rows, key in (('chunks', p['p_chunks'], ('chunk_id',)),
                                 ('chunk_embeddings', p['p_embeddings'], ('chunk_id', 'embedding_set_id'))):
            for new in rows:  # upsert in place, as on conflict do update
                old = [r for r in self.tables[table] if all(r[k] == new[k] for k in key)]
                if old:
                    old[0].update(new)
                else:
                    self.tables[table].append(dict(new))
        return {'embedding_set_id': set_id, 'total_chunks_loaded': len(p['p_chunks']),
                'total_embeddings_loaded': len(p['p_embeddings']), 'total_spans_loaded': len(p['p_spans']),
                'total_documents_loaded': 0, 'duplicate_avoided_count': already}

    def _create_knowledge_release(self, p):
        if any(r['release_id'] == p['p_release_id'] or r['release_version'] == p['p_release_version']
               for r in self.tables['knowledge_releases']):
            raise StorageError('duplicate key value violates unique constraint', 409)
        self.tables['knowledge_releases'].append({'release_id': p['p_release_id'],
            'release_version': p['p_release_version'], 'description': p['p_description'],
            'embedding_set_id': p['p_embedding_set_id'], 'status': 'draft',
            'expected_chunk_count': len(p['p_chunk_ids']),
            'expected_document_version_count': len(p['p_document_version_ids']),
            'expected_rule_count': len(p['p_rule_ids'])})
        self.tables['release_chunks'] += [{'release_id': p['p_release_id'], 'chunk_id': c} for c in p['p_chunk_ids']]
        self.tables['release_document_versions'] += [{'release_id': p['p_release_id'], 'version_id': v}
                                                      for v in p['p_document_version_ids']]

    def _activate_knowledge_release(self, p):  # present so a mutation is caught by assertion, not AttributeError
        self.tables['active_release'][:] = [{'release_id': p['p_release_id']}]

    _rollback_knowledge_release = _designate_research_release = _activate_knowledge_release

    def rpc_names(self):
        return [c[1] for c in self.calls if c[0] == 'rpc']

    def close(self):
        self.closed = True


@pytest.fixture
def package(reviewed, tmp_path):  # noqa: F811
    root, _ = reviewed
    out = tmp_path / 'package'
    build(root, out, encoder=SyntheticEncoder())
    return out


def documents_for(package):
    ids = {v['document_id']: v['synthetic'] for v in load_package(package)['sources']}
    return [{'document_id': i, 'namespace': 'institutional', 'synthetic': s,
             'document_category': 'academic_handbook', 'title': 'Synthetic student guide'} for i, s in sorted(ids.items())]


class Fingerprint:
    def __init__(self, same=True):
        self.same, self.calls = same, 0

    def __call__(self):
        self.calls += 1
        return {'chunks': {'same': True}, 'knowledge_releases': {'same': self.same}}


def stage(package, client, **overrides):
    kwargs = dict(client=client, target_url=LOCAL, fingerprint_check=Fingerprint(),
                  release_label='local-draft-test', actor='Synthetic operator',
                  baseline_dir=package.parent / 'baselines')
    kwargs.update(overrides)
    if 'documents' not in kwargs:
        kwargs['documents'] = documents_for(package)
    return api().stage_draft(package, **kwargs)


def assert_no_secret(value):
    assert SECRET not in json.dumps(value, default=str)


@pytest.mark.parametrize('target', [None, '', 'https://abcd.supabase.co', 'http://abcd.supabase.co:54321',
    'http://localhost:54321', 'http://127.0.0.1:54322', 'http://127.0.0.1:55433', 'https://127.0.0.1:54321',
    'http://[::1]:54321', 'http://127.0.0.2:54321', 'http://user@127.0.0.1:54321', 'http://127.0.0.1:54321/rest/v1',
    'http://127.0.0.1:54321?x=1', ' http://127.0.0.1:54321', 'http://127.0.0.1:54321.evil.example'])
def test_refuses_any_target_other_than_local_supabase_before_any_call(package, target):
    client, check = FakeClient(), Fingerprint()
    with pytest.raises(api().LocalReleaseError, match='target'):
        stage(package, client, target_url=target, fingerprint_check=check)
    assert client.calls == [] and check.calls == 0


def test_refuses_client_pointed_elsewhere_than_the_target(package):
    client = FakeClient(base_url='https://abcd.supabase.co/rest/v1')
    with pytest.raises(api().LocalReleaseError, match='client'):
        stage(package, client)
    assert client.calls == []


def test_refuses_unverifiable_package_before_fingerprint_or_writes(package):
    documents = documents_for(package)
    (package / 'chunks.jsonl').write_bytes(b'{}\n')
    client, check = FakeClient(), Fingerprint()
    with pytest.raises(api().LocalReleaseError, match='verif'):
        stage(package, client, fingerprint_check=check, documents=documents)
    assert client.calls == [] and check.calls == 0


@pytest.mark.parametrize('report', [{}, None, {'chunks': {'same': True}, 'courses': {'same': False}},
                                    {'chunks': {'same': 'yes'}}, ['same']])
def test_refuses_unless_fingerprint_reports_hosted_equal_local(package, report):
    client = FakeClient()
    with pytest.raises(api().LocalReleaseError, match='fingerprint'):
        stage(package, client, fingerprint_check=lambda: report)
    assert client.calls == []


def test_fingerprint_check_error_refuses_without_writes(package):
    def broken():
        raise RuntimeError('connection refused ' + SECRET)
    client = FakeClient()
    with pytest.raises(api().LocalReleaseError, match='fingerprint') as caught:
        stage(package, client, fingerprint_check=broken)
    assert client.calls == []
    assert SECRET not in str(caught.value) and SECRET not in repr(caught.value)


def test_stages_inactive_draft_in_order_and_reads_it_back(package):
    client = FakeClient()
    pkg = load_package(package)
    result = stage(package, client)
    assert client.rpc_names() == ['register_pending_sources', 'load_knowledge_batch', 'create_knowledge_release']
    assert all(c[2] == 'admin' for c in client.calls)
    assert not {'activate_knowledge_release', 'rollback_knowledge_release',
                'designate_research_release'} & set(client.rpc_names())
    release = [r for r in client.tables['knowledge_releases'] if r['release_id'] == 'local-draft-test'][0]
    assert release['status'] == 'draft'
    assert release['release_version'] == 'package-' + pkg['manifest']['package_id']
    assert release['embedding_set_id'] == pkg['embedding_manifest']['embedding_set_id']
    assert result['status'] == 'draft' and result['created'] is True
    assert result['chunks'] == result['embeddings'] == len(pkg['chunks'])
    assert result['document_versions'] == len(pkg['sources'])
    assert result['active_release_id'] == 'prior-active'
    assert result['activation_eligible'] is False and result['candidate_only'] is True
    assert client.tables['active_release'] == [{'release_id': 'prior-active'}]
    assert_no_secret(result)


def test_repeat_run_creates_no_duplicate_chunks_or_release(package):
    client = FakeClient()
    stage(package, client)
    snapshot = copy.deepcopy(client.tables)
    again = stage(package, client)
    assert again['created'] is False and again['status'] == 'draft'
    assert again['already_registered_versions'] and not again['registered_versions']
    assert client.tables == snapshot
    assert client.rpc_names().count('create_knowledge_release') == 1
    assert client.rpc_names().count('register_pending_sources') == 1


def test_label_or_package_already_used_by_another_release_refuses_before_writes(package):
    client = FakeClient()
    client.tables['knowledge_releases'].append({'release_id': 'local-draft-test', 'release_version': 'other',
        'status': 'draft', 'embedding_set_id': 'y'})
    with pytest.raises(api().LocalReleaseError, match='already'):
        stage(package, client)
    assert client.rpc_names() == []


def test_existing_release_for_package_that_is_not_draft_refuses(package):
    client = FakeClient()
    stage(package, client)
    client.tables['knowledge_releases'][-1]['status'] = 'active'
    calls = len(client.rpc_names())
    with pytest.raises(api().LocalReleaseError, match='draft'):
        stage(package, client)
    assert len(client.rpc_names()) == calls


def test_registered_version_with_conflicting_bytes_refuses_before_writes(package):
    client = FakeClient()
    version = load_package(package)['sources'][0]
    client.tables['document_versions'].append({'version_id': version['version_id'],
        'document_id': version['document_id'], 'byte_sha256': 'f' * 64, 'source_register': {}})
    with pytest.raises(api().LocalReleaseError, match='conflict'):
        stage(package, client)
    assert client.rpc_names() == []


def test_partial_failure_reports_what_was_written_and_never_activates(package):
    client = FakeClient()
    client.fail['load_knowledge_batch'] = StorageError('Embedding does not match chunk', 400)
    with pytest.raises(api().LocalReleaseError) as caught:
        stage(package, client)
    error = caught.value
    version_ids = [v['version_id'] for v in load_package(package)['sources']]
    assert error.written['registered_versions'] == version_ids
    assert error.written['artifacts'] == 'not_written'
    assert error.written['release'] == 'not_attempted'
    assert 'registered' in str(error) and 'not activated' in str(error)
    assert client.rpc_names() == ['register_pending_sources', 'load_knowledge_batch']
    assert_no_secret(error.written)
    assert SECRET not in str(error)


def test_transport_failure_reports_unknown_write_state(package):
    client = FakeClient()
    client.fail['create_knowledge_release'] = StorageError('Storage transport request failed ' + SECRET)
    with pytest.raises(api().LocalReleaseError) as caught:
        stage(package, client)
    assert caught.value.written['artifacts'] == 'loaded'
    assert caught.value.written['release'] == 'unknown'
    assert SECRET not in str(caught.value) and SECRET not in repr(caught.value)


@pytest.mark.parametrize('tamper, message', [
    (lambda c: c.tables['release_chunks'].pop(), 'chunk'),
    (lambda c: c.tables['chunk_embeddings'].pop(), 'embedding'),
    (lambda c: c.tables['knowledge_releases'][-1].update(status='active'), 'draft'),
    (lambda c: c.tables['knowledge_releases'][-1].update(expected_chunk_count=99), 'count'),
    (lambda c: c.tables['release_document_versions'].pop(), 'version'),
    (lambda c: c.tables['active_release'].__setitem__(0, {'release_id': 'local-draft-test'}), 'active'),
])
def test_readback_mismatch_raises(package, tamper, message):
    client = FakeClient()
    client.after['create_knowledge_release'] = tamper
    with pytest.raises(api().LocalReleaseError, match=message) as caught:
        stage(package, client)
    assert caught.value.written['release'] == 'created'
    if message == 'active':  # the static "nothing activated" claim would be false here
        assert 'Nothing was activated' not in str(caught.value)


def test_readback_detects_chunk_content_drift(package):
    client = FakeClient()
    client.after['load_knowledge_batch'] = lambda c: c.tables['chunks'][-1].update(content_hash='0' * 64)
    with pytest.raises(api().LocalReleaseError, match='chunk'):
        stage(package, client)


def test_no_prior_active_release_must_stay_absent(package):
    client = FakeClient()
    client.tables['active_release'].clear()
    assert stage(package, client)['active_release_id'] is None


@pytest.mark.parametrize('field, value', [('release_label', ''), ('release_label', 'Bad Label'),
    ('release_label', 'a,b'), ('actor', ''), ('actor', 'x\ny'), ('documents', [])])
def test_refuses_invalid_arguments_before_any_call(package, field, value):
    client = FakeClient()
    with pytest.raises(api().LocalReleaseError):
        stage(package, client, **{field: value})
    assert client.calls == []


def test_fingerprint_script_adapter_reads_a_fresh_report(tmp_path):
    report, seen = tmp_path / 'report.json', []
    report.write_text('{"stale": {"same": true}}', encoding='utf-8')

    def run(argv, **kwargs):
        seen.append(argv)
        assert not report.exists()  # a stale report can never satisfy the check
        report.write_text('{"chunks": {"same": true}}', encoding='utf-8')
    check = api().fingerprint_script_check(tmp_path / 'fingerprint.py', report, run=run)
    assert check() == {'chunks': {'same': True}}
    assert seen[0][-2:] == [str(tmp_path / 'fingerprint.py'), str(report)]


def test_local_client_reads_key_only_from_its_own_variable(monkeypatch):
    monkeypatch.setenv('SUPABASE_URL', 'https://abcd.supabase.co')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'hosted-key')
    monkeypatch.setenv('BINTANONG_LOCAL_SERVICE_ROLE_KEY', SECRET)
    client = api().local_client(LOCAL)
    try:
        assert client.base_url == LOCAL + '/rest/v1'
        assert client.config.service_role_key == SECRET
        assert 'hosted-key' not in (client.config.service_role_key, client.config.anon_key)
        assert SECRET not in repr(client.config)
    finally:
        client.close()
    with pytest.raises(api().LocalReleaseError, match='target'):
        api().local_client('https://abcd.supabase.co')


def test_local_client_ignores_the_generic_key_variable(monkeypatch):
    from backend.bintanong_storage.config import DEFAULT_LOCAL_SERVICE_ROLE_KEY
    monkeypatch.delenv('BINTANONG_LOCAL_SERVICE_ROLE_KEY', raising=False)
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'hosted-key')
    client = api().local_client(LOCAL)
    try:
        assert client.config.service_role_key == DEFAULT_LOCAL_SERVICE_ROLE_KEY
    finally:
        client.close()


def test_local_client_never_routes_through_environment_proxies(monkeypatch):
    from backend.bintanong_storage.client import SupabaseStorageClient
    for name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'):
        monkeypatch.setenv(name, 'http://proxy.invalid:9')
    monkeypatch.delenv('NO_PROXY', raising=False)
    monkeypatch.delenv('no_proxy', raising=False)
    local = api().local_client(LOCAL)
    default = SupabaseStorageClient()
    try:
        assert local._http._trust_env is False and not local._http._mounts
        assert default._http._trust_env is True  # other callers keep httpx defaults
    finally:
        local.close()
        default.close()


def test_unexpected_write_error_is_reported_unknown_and_redacted(package):
    client = FakeClient()
    client.fail['load_knowledge_batch'] = RuntimeError('socket died ' + SECRET)
    with pytest.raises(api().LocalReleaseError) as caught:
        stage(package, client)
    assert caught.value.written['artifacts'] == 'unknown'
    assert caught.value.written['release'] == 'not_attempted'
    assert 'not activated' in str(caught.value)
    assert SECRET not in str(caught.value) and SECRET not in repr(caught.value)


def report(hosted, local, tables=('chunks', 'knowledge_releases', 'courses')):
    return {t: {'same': hosted == local, 'hosted_rows': 3, 'local_rows': 3,
                'hosted_sha256': hosted + t, 'local_sha256': local + t} for t in tables}


class Reports:
    """Returns the given reports in order, one per fingerprint run."""

    def __init__(self, *reports):
        self.reports, self.calls = list(reports), 0

    def __call__(self):
        self.calls += 1
        return copy.deepcopy(self.reports.pop(0))


def test_freeze_rule_first_run_strict_then_matches_the_post_stage_baseline(package):
    client, base = FakeClient(), package.parent / 'baselines'
    stage(package, client, fingerprint_check=Reports(report('h', 'h'), report('h', 'l1')))
    pointer = json.loads((base / 'fingerprint-baseline.json').read_text(encoding='utf-8'))
    assert pointer['release_id'] == 'local-draft-test'
    saved = json.loads((base / 'fingerprint-after-local-draft-test.json').read_text(encoding='utf-8'))
    assert saved == report('h', 'l1')  # the post-write report, not the pre-write one
    again = stage(package, client, fingerprint_check=Reports(report('h', 'l1'), report('h', 'l1')))
    assert again['created'] is False


@pytest.mark.parametrize('second, message', [(report('h2', 'l1'), 'hosted'), (report('h', 'l2'), 'local')])
def test_freeze_rule_refuses_when_either_side_moved_from_the_baseline(package, second, message):
    client = FakeClient()
    stage(package, client, fingerprint_check=Reports(report('h', 'h'), report('h', 'l1')))
    calls = len(client.rpc_names())
    with pytest.raises(api().LocalReleaseError, match=message):
        stage(package, client, fingerprint_check=Reports(second))
    assert len(client.rpc_names()) == calls


def test_freeze_rule_refuses_a_baseline_with_a_different_table_set(package):
    client = FakeClient()
    stage(package, client, fingerprint_check=Reports(report('h', 'h'), report('h', 'l1')))
    with pytest.raises(api().LocalReleaseError, match='table'):
        stage(package, client, fingerprint_check=Reports(report('h', 'l1', tables=('chunks',))))


@pytest.mark.parametrize('pointer', ['not json', '[]', '{"schema_version": "other", "release_id": "x", '
    '"report": "fingerprint-after-x.json"}', '{"schema_version": "bintanong-fingerprint-baseline-v1", '
    '"release_id": "x", "report": "../elsewhere.json"}', '{"schema_version": "bintanong-fingerprint-baseline-v1", '
    '"release_id": "x", "report": "fingerprint-after-x.json"}'])
def test_freeze_rule_refuses_a_malformed_or_foreign_baseline(package, pointer):
    base = package.parent / 'baselines'
    base.mkdir()
    (base / 'fingerprint-baseline.json').write_text(pointer, encoding='utf-8')
    client = FakeClient()
    with pytest.raises(api().LocalReleaseError, match='baseline'):
        stage(package, client, fingerprint_check=Reports(report('h', 'l1')))
    assert client.calls == []


def test_freeze_rule_refuses_a_baseline_report_that_is_not_a_report(package):
    base = package.parent / 'baselines'
    base.mkdir()
    (base / 'fingerprint-baseline.json').write_text('{"schema_version": "bintanong-fingerprint-baseline-v1", '
        '"release_id": "x", "report": "fingerprint-after-x.json"}', encoding='utf-8')
    (base / 'fingerprint-after-x.json').write_text('{"chunks": "same"}', encoding='utf-8')
    with pytest.raises(api().LocalReleaseError, match='baseline'):
        stage(package, FakeClient(), fingerprint_check=Reports(report('h', 'l1')))


def test_baseline_is_never_written_on_a_failed_stage(package):
    client, base = FakeClient(), package.parent / 'baselines'
    client.fail['load_knowledge_batch'] = StorageError('Embedding does not match chunk', 400)
    with pytest.raises(api().LocalReleaseError):
        stage(package, client, fingerprint_check=Reports(report('h', 'h'), report('h', 'l1')))
    assert not base.exists() or not any(base.iterdir())


def test_post_stage_fingerprint_that_shows_hosted_moved_writes_no_baseline(package):
    client, base = FakeClient(), package.parent / 'baselines'
    with pytest.raises(api().LocalReleaseError, match='hosted') as caught:
        stage(package, client, fingerprint_check=Reports(report('h', 'h'), report('h2', 'l1')))
    assert caught.value.written['release'] == 'created'
    assert not base.exists() or not any(base.iterdir())


def test_baseline_dir_inside_a_git_checkout_is_refused_before_any_call(package, tmp_path):
    (tmp_path / 'repo' / '.git').mkdir(parents=True)
    client, check = FakeClient(), Fingerprint()
    with pytest.raises(api().LocalReleaseError, match='Git'):
        stage(package, client, fingerprint_check=check, baseline_dir=tmp_path / 'repo' / 'evidence')
    assert client.calls == [] and check.calls == 0


def cli_fakes(monkeypatch, client, check):
    seen = {}

    def fake_client(target):
        seen['target'] = target
        return client

    def fake_script(script, report_path):
        seen['script'] = (script, report_path)
        return check
    monkeypatch.setattr(api(), 'local_client', fake_client)
    monkeypatch.setattr(api(), 'fingerprint_script_check', fake_script)
    return seen


def stage_argv(package, tmp_path):
    docs = tmp_path / 'documents.json'
    docs.write_text(json.dumps(documents_for(package)), encoding='utf-8')
    return ['stage', str(package), '--documents', str(docs), '--release-label', 'local-draft-test',
            '--actor', 'Synthetic operator', '--baseline-dir', str(tmp_path / 'baselines'),
            '--fingerprint-script', str(tmp_path / 'fingerprint.py'),
            '--fingerprint-report', str(tmp_path / 'report.json')]


def test_stage_command_prints_the_draft_result(package, tmp_path, monkeypatch, capsys):
    from backend.bintanong_tools.knowledge_update.__main__ import main
    client = FakeClient()
    seen = cli_fakes(monkeypatch, client, Fingerprint())
    assert main(stage_argv(package, tmp_path)) == 0
    out = capsys.readouterr()
    result = json.loads(out.out)
    assert result['status'] == 'draft' and result['release_id'] == 'local-draft-test'
    assert seen['target'] == LOCAL and client.closed
    assert seen['script'] == (tmp_path / 'fingerprint.py', tmp_path / 'report.json')
    assert SECRET not in out.out + out.err


def test_stage_command_failure_exits_nonzero_with_what_was_written(package, tmp_path, monkeypatch, capsys):
    from backend.bintanong_tools.knowledge_update.__main__ import main
    client = FakeClient()
    client.fail['load_knowledge_batch'] = StorageError('Embedding does not match chunk ' + SECRET, 400)
    cli_fakes(monkeypatch, client, Fingerprint())
    assert main(stage_argv(package, tmp_path)) == 1
    out = capsys.readouterr()
    assert out.out == ''
    assert 'loading package chunks/vectors failed' in out.err
    assert '"artifacts": "not_written"' in out.err and '"registration": "registered"' in out.err
    assert SECRET not in out.err and client.closed


def test_stage_command_has_no_key_option(package, tmp_path, monkeypatch):
    from backend.bintanong_tools.knowledge_update.__main__ import main
    cli_fakes(monkeypatch, FakeClient(), Fingerprint())
    with pytest.raises(SystemExit):
        main(stage_argv(package, tmp_path) + ['--service-role-key', SECRET])