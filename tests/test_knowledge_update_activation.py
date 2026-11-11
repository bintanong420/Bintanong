"""Local activation and rollback of tool-staged drafts; in-memory fake client only, never a database."""
import json
import re

import pytest

from backend.bintanong_storage.client import StorageError
from backend.bintanong_tools.knowledge_update.build import load_package
from test_knowledge_update_build import reviewed  # noqa: F401 (fixture)
from test_knowledge_update_local_release import (LOCAL, SECRET, FakeClient, Fingerprint, Reports, api,
                                                 assert_no_secret, cli_fakes, package, report, stage)  # noqa: F401

REF = 'research-owner-20261112'
DRAFT = 'local-draft-test'


class ReleaseClient(FakeClient):
    """Adds the activation RPCs with the migrations' status rules (phase4 security, phase9 research)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tables['knowledge_releases'][0].update(published_at='2026-11-01', release_kind='institutional',
                                                    review_scope_id=None, research_authorization_ref=None)

    def _row(self, release_id):
        rows = [r for r in self.tables['knowledge_releases'] if r['release_id'] == release_id]
        return rows[0] if rows else None

    def _designate_research_release(self, p):
        row = self._row(p['p_release_id'])
        if not re.fullmatch(r'research-owner-[0-9]{8}', p['p_authorization_ref'] or ''):
            raise StorageError('Owner research authorization reference required', 400)
        if not row or row['status'] != 'draft' or row.get('published_at') or not row.get('review_scope_id'):
            raise StorageError('Unpublished draft with a bound selected review required', 400)
        row.update(release_kind='research', research_authorization_ref=p['p_authorization_ref'])
        return {'release_id': row['release_id'], 'release_kind': 'research'}

    def _activate_knowledge_release(self, p):
        row = self._row(p['p_release_id'])
        if not row or row['status'] == 'revoked':
            raise StorageError('Release is missing or revoked', 400)
        if row.get('review_scope_id') and row.get('release_kind') != 'research':
            raise StorageError('Release contains unapproved document evidence', 400)
        for other in self.tables['knowledge_releases']:
            if other['status'] == 'active' and other is not row:
                other['status'] = 'superseded'
        row.update(status='active', published_at=row.get('published_at') or '2026-11-12',
                   published_by=row.get('published_by') or p['p_actor'])
        self.tables['active_release'][:] = [{'release_id': row['release_id']}]

    def _rollback_knowledge_release(self, p):
        row = self._row(p['p_target_release_id'])
        if not row or row['status'] not in ('active', 'superseded') or not row.get('published_at'):
            raise StorageError('Rollback requires a previously published release', 400)
        self._activate_knowledge_release({'p_release_id': row['release_id'], 'p_actor': p['p_actor']})

    def mark(self):
        self.mark_at = len(self.rpc_names())

    def new_rpcs(self):
        return self.rpc_names()[self.mark_at:]


def checks_report(package, path, binding=None, **overrides):
    pkg = load_package(package)
    files = pkg['manifest']['files']
    data = {'schema_version': 'bintanong-draft-checks-v1', 'package_id': pkg['manifest']['package_id'],
            'passed': True, 'cases': [{'case_id': 'c1', 'passed': True}], 'created_at': '2026-11-12T00:00:00Z',
            'scope': 'retrieval', 'encoder': {'model_id': 'synthetic'},
            'package_binding': {'package_id': pkg['manifest']['package_id'],
                                'chunks_sha256': files['chunks.jsonl'], 'embeddings_sha256': files['embeddings.jsonl'],
                                'embedding_manifest_sha256': files['embedding_manifest.json'],
                                'embedding_set_id': pkg['embedding_manifest']['embedding_set_id']}}
    data['package_binding'].update(binding or {})
    data.update(overrides)
    path.write_text(json.dumps(data), encoding='utf-8')
    return path


@pytest.fixture
def staged(package):  # noqa: F811
    client = ReleaseClient()
    stage(package, client)
    client.mark()
    return client, package


def activate(package, client, **overrides):
    kwargs = dict(client=client, target_url=LOCAL, package_path=package, authorization_ref=REF,
                  actor='Synthetic operator', fingerprint_check=Fingerprint(), baseline_dir=package.parent / 'baselines')
    if 'checks_report' not in overrides:
        kwargs['checks_report'] = checks_report(package, package.parent / 'checks.json')
    kwargs.update(overrides)
    return api().activate_draft(DRAFT, **kwargs)


def rollback(package, client, target='prior-active', **overrides):
    kwargs = dict(client=client, target_url=LOCAL, authorization_ref=REF, actor='Synthetic operator',
                  fingerprint_check=Fingerprint(), baseline_dir=package.parent / 'baselines')
    kwargs.update(overrides)
    return api().rollback_to(target, **kwargs)


def active(client):
    return client.tables['active_release'][0]['release_id']


def test_activates_the_checked_draft_and_records_the_previous_release(staged):
    client, package = staged
    result = activate(package, client)
    assert client.new_rpcs() == ['activate_knowledge_release']
    assert all(c[2] == 'admin' for c in client.calls)
    assert active(client) == DRAFT and client._row(DRAFT)['status'] == 'active'
    assert client._row('prior-active')['status'] == 'superseded'
    assert result['active_release_id'] == DRAFT and result['previous_active_release_id'] == 'prior-active'
    assert result['authorization_ref'] == REF and result['target'] == LOCAL
    pointer = json.loads((package.parent / 'baselines' / 'fingerprint-baseline.json').read_text(encoding='utf-8'))
    assert pointer['release_id'] == DRAFT and pointer['action'] == 'activate' and pointer['authorization_ref'] == REF
    assert_no_secret(result)


def test_bound_selected_draft_is_designated_research_before_activation(staged):
    client, package = staged
    client._row(DRAFT)['review_scope_id'] = 'scope-1'
    activate(package, client)
    assert client.new_rpcs() == ['designate_research_release', 'activate_knowledge_release']
    assert client._row(DRAFT)['research_authorization_ref'] == REF


def test_designation_needs_the_owner_reference_format_before_any_write(staged):
    client, package = staged
    client._row(DRAFT)['review_scope_id'] = 'scope-1'
    with pytest.raises(api().LocalReleaseError, match='authorization'):
        activate(package, client, authorization_ref='owner said yes')
    assert client.new_rpcs() == []


def test_rollback_restores_the_previous_release(staged):
    client, package = staged
    previous = activate(package, client)['previous_active_release_id']
    client.mark()
    result = rollback(package, client, previous)
    assert client.new_rpcs() == ['rollback_knowledge_release']
    assert active(client) == 'prior-active' and client._row(DRAFT)['status'] == 'superseded'
    assert result['active_release_id'] == 'prior-active' and result['previous_active_release_id'] == DRAFT
    pointer = json.loads((package.parent / 'baselines' / 'fingerprint-baseline.json').read_text(encoding='utf-8'))
    assert pointer['release_id'] == 'prior-active' and pointer['action'] == 'rollback'
    assert_no_secret(result)


@pytest.mark.parametrize('target', [None, 'https://abcd.supabase.co', 'http://localhost:54321', 'http://127.0.0.1:54322'])
def test_refuses_other_targets_before_any_call(staged, target):
    client, package = staged
    calls, check = len(client.calls), Fingerprint()
    with pytest.raises(api().LocalReleaseError, match='target'):
        activate(package, client, target_url=target, fingerprint_check=check)
    with pytest.raises(api().LocalReleaseError, match='target'):
        rollback(package, client, target_url=target, fingerprint_check=check)
    assert len(client.calls) == calls and check.calls == 0


def test_refuses_a_client_bound_elsewhere(package):  # noqa: F811
    client = ReleaseClient(base_url='https://abcd.supabase.co/rest/v1')
    with pytest.raises(api().LocalReleaseError, match='client'):
        activate(package, client)
    with pytest.raises(api().LocalReleaseError, match='client'):
        rollback(package, client)
    assert client.calls == []


@pytest.mark.parametrize('ref', ['', '   ', None, 'a\nb', 42])
def test_authorization_reference_is_required(staged, ref):
    client, package = staged
    calls = len(client.calls)
    with pytest.raises(api().LocalReleaseError, match='authorization'):
        activate(package, client, authorization_ref=ref)
    with pytest.raises(api().LocalReleaseError, match='authorization'):
        rollback(package, client, authorization_ref=ref)
    assert len(client.calls) == calls


@pytest.mark.parametrize('overrides', [{'passed': False}, {'passed': 'true'}, {'schema_version': 'other'},
    {'package_id': 'f' * 64}, {'cases': []}, {'cases': [{'case_id': 'c1', 'passed': False}]},
    {'cases': [{'case_id': 'c1'}]}, {'cases': ['c1']},
    {'created_at': None}, {'package_binding': None}])
def test_refuses_a_failed_forged_or_mismatched_checks_report(staged, overrides):
    client, package = staged
    path = checks_report(package, package.parent / 'checks.json', **overrides)
    with pytest.raises(api().LocalReleaseError, match='checks report'):
        activate(package, client, checks_report=path)
    assert client.new_rpcs() == [] and active(client) == 'prior-active'


@pytest.mark.parametrize('field', ['package_id', 'chunks_sha256', 'embeddings_sha256',
                                   'embedding_manifest_sha256', 'embedding_set_id'])
def test_refuses_a_checks_report_bound_to_different_package_bytes(staged, field):
    client, package = staged
    path = checks_report(package, package.parent / 'checks.json', binding={field: '0' * 64})
    with pytest.raises(api().LocalReleaseError, match=field):
        activate(package, client, checks_report=path)
    assert client.new_rpcs() == []


@pytest.mark.parametrize('content', [None, 'not json', '[]'])
def test_refuses_a_missing_or_unreadable_checks_report(staged, content):
    client, package = staged
    path = package.parent / 'checks.json'
    if content is not None:
        path.write_text(content, encoding='utf-8')
    with pytest.raises(api().LocalReleaseError, match='checks report'):
        activate(package, client, checks_report=path)
    assert client.new_rpcs() == []


def test_refuses_a_package_that_no_longer_verifies(staged):
    client, package = staged
    path = checks_report(package, package.parent / 'checks.json')
    (package / 'chunks.jsonl').write_bytes(b'{}\n')
    with pytest.raises(api().LocalReleaseError, match='package'):
        activate(package, client, checks_report=path)
    assert client.new_rpcs() == []


def test_refuses_a_release_not_staged_by_this_tool(staged):
    client, package = staged
    client._row(DRAFT)['release_version'] = 'v-hand-made'
    with pytest.raises(api().LocalReleaseError, match='this tool'):
        activate(package, client)
    assert client.new_rpcs() == []


def test_refuses_when_the_draft_embedding_set_differs_from_the_package(staged):
    client, package = staged
    client._row(DRAFT)['embedding_set_id'] = 'other-set'
    with pytest.raises(api().LocalReleaseError, match='embedding set'):
        activate(package, client)
    assert client.new_rpcs() == []


def test_refuses_a_missing_release_or_one_already_active(staged):
    client, package = staged
    activate(package, client)
    client.mark()
    with pytest.raises(api().LocalReleaseError, match='draft'):
        activate(package, client)
    with pytest.raises(api().LocalReleaseError, match='already active'):
        rollback(package, client, DRAFT)
    with pytest.raises(api().LocalReleaseError, match='not found'):
        rollback(package, client, 'no-such-release')
    assert client.new_rpcs() == []


def test_rollback_refuses_a_never_published_draft(staged):
    client, package = staged
    with pytest.raises(api().LocalReleaseError, match='published'):
        rollback(package, client, DRAFT)
    assert client.new_rpcs() == []


def test_fingerprint_refusal_comes_before_any_write(staged):
    client, package = staged
    with pytest.raises(api().LocalReleaseError, match='fingerprint'):
        activate(package, client, fingerprint_check=Reports(report('h2', 'l9')))
    with pytest.raises(api().LocalReleaseError, match='fingerprint'):
        rollback(package, client, fingerprint_check=Reports(report('h2', 'l9')))
    assert client.new_rpcs() == [] and active(client) == 'prior-active'


@pytest.mark.parametrize('tamper', [lambda c: c.tables['active_release'].__setitem__(0, {'release_id': 'prior-active'}),
                                    lambda c: c._row(DRAFT).update(status='draft')])
def test_activation_readback_mismatch_raises_and_keeps_the_baseline(staged, tamper):
    client, package = staged
    pointer = package.parent / 'baselines' / 'fingerprint-baseline.json'
    before = pointer.read_text(encoding='utf-8')
    client.after['activate_knowledge_release'] = tamper
    with pytest.raises(api().LocalReleaseError, match='read-back') as caught:
        activate(package, client)
    assert caught.value.written['activation'] == 'requested'
    assert pointer.read_text(encoding='utf-8') == before


def test_rollback_readback_mismatch_raises(staged):
    client, package = staged
    activate(package, client)
    pointer = package.parent / 'baselines' / 'fingerprint-baseline.json'
    before = pointer.read_text(encoding='utf-8')
    client.after['rollback_knowledge_release'] = lambda c: c.tables['active_release'].__setitem__(
        0, {'release_id': DRAFT})
    with pytest.raises(api().LocalReleaseError, match='read-back'):
        rollback(package, client)
    assert pointer.read_text(encoding='utf-8') == before


def test_a_failed_readback_query_is_reported_not_raised_raw(staged, monkeypatch):
    client, package = staged
    original, armed = client.select, []

    def failing(table, *args, **kwargs):
        if table == 'knowledge_releases' and armed:
            raise StorageError('Storage transport request failed ' + SECRET)
        return original(table, *args, **kwargs)
    client.after['activate_knowledge_release'] = lambda c: armed.append(True)
    monkeypatch.setattr(client, 'select', failing)
    with pytest.raises(api().LocalReleaseError, match='read-back') as caught:
        activate(package, client)
    assert SECRET not in str(caught.value)


def test_database_rejection_and_transport_failure_report_the_write_state(staged):
    client, package = staged
    client.fail['activate_knowledge_release'] = StorageError('Release contains unapproved document evidence', 400)
    with pytest.raises(api().LocalReleaseError, match='unapproved') as caught:
        activate(package, client)
    assert caught.value.written['activation'] == 'not_written'
    client.fail['activate_knowledge_release'] = StorageError('Storage transport request failed ' + SECRET)
    with pytest.raises(api().LocalReleaseError) as caught:
        activate(package, client)
    assert caught.value.written['activation'] == 'unknown'
    assert SECRET not in str(caught.value) and SECRET not in repr(caught.value)
    assert_no_secret(caught.value.written)


def test_activate_and_rollback_commands(staged, monkeypatch, capsys):
    from backend.bintanong_tools.knowledge_update.__main__ import main
    client, package = staged
    tmp = package.parent
    cli_fakes(monkeypatch, client, Fingerprint())
    common = ['--authorization-ref', REF, '--actor', 'Synthetic operator', '--baseline-dir', str(tmp / 'baselines'),
              '--fingerprint-script', str(tmp / 'fingerprint.py'), '--fingerprint-report', str(tmp / 'report.json')]
    checks = checks_report(package, tmp / 'checks.json')
    assert main(['activate', DRAFT, '--package', str(package), '--checks-report', str(checks)] + common) == 0
    assert json.loads(capsys.readouterr().out)['active_release_id'] == DRAFT
    assert main(['rollback', 'prior-active'] + common) == 0
    out = capsys.readouterr()
    assert json.loads(out.out)['active_release_id'] == 'prior-active'
    assert main(['rollback', 'prior-active'] + common) == 1
    out = capsys.readouterr()
    assert 'already active' in out.err and '"written"' in out.err and SECRET not in out.out + out.err
    with pytest.raises(SystemExit):
        main(['rollback', 'prior-active'] + common[2:])  # --authorization-ref is required
