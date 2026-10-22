"""Hosted reviewed curriculum ledgers are read, rebuilt and re-verified before use (synthetic only)."""
from __future__ import annotations

import copy

import pytest

from test_symbolic_runtime import fixture, rereview

REF = 'research-owner-20261021'


class FakeClient:
    def __init__(self, ledger, *, status='active', kind='research', ref=REF, link=None):
        self.tables = {
            'knowledge_releases': [dict(release_id='release-r', status=status, release_kind=kind,
                                        research_authorization_ref=ref)],
            'release_curriculum_ledgers': [link or dict(release_id='release-r', curriculum_id=ledger['scope']['curriculum_id'],
                                                        ledger_sha256=ledger['content_sha256'])],
            'curriculum_ledgers': [dict(ledger_sha256=ledger['content_sha256'], program_id=ledger['scope']['program_id'],
                                        curriculum_id=ledger['scope']['curriculum_id'], ledger=ledger)]}
        self.roles = set()

    def select(self, table, *, filters=None, role):
        self.roles.add(role)
        rows = self.tables[table]
        for key, expression in (filters or {}).items():
            rows = [r for r in rows if str(r.get(key)) == expression[3:]]
        return copy.deepcopy(rows)


def load(client):
    from backend.bintanong_runtime.hosted_curricula import load_release_curricula
    return load_release_curricula(client, release_id='release-r', authorization_ref=REF)


def test_reads_verified_ledgers_of_the_active_research_release_as_runtime():
    ledger = rereview(fixture()); client = FakeClient(ledger)
    result = load(client)
    assert result == {ledger['scope']['curriculum_id']: ledger}
    assert client.roles == {'runtime'}


@pytest.mark.parametrize('change', [dict(status='draft'), dict(kind='institutional'), dict(ref='research-owner-20200101')])
def test_refuses_a_release_that_is_not_the_active_authorized_research_release(change):
    with pytest.raises(ValueError, match='hosted_release_not_active_research'):
        load(FakeClient(rereview(fixture()), **change))


def test_refuses_a_link_to_a_missing_or_other_curriculum_ledger():
    ledger = rereview(fixture())
    with pytest.raises(ValueError, match='hosted_curriculum_missing'):
        load(FakeClient(ledger, link=dict(release_id='release-r', curriculum_id=ledger['scope']['curriculum_id'],
                                          ledger_sha256='0' * 64)))


def test_refuses_a_stored_ledger_whose_rules_were_changed():
    ledger = rereview(fixture()); client = FakeClient(ledger)
    stored = client.tables['curriculum_ledgers'][0]['ledger']
    stored['courses'][1]['prerequisites']['kind'] = 'co_requisite'  # digest left as reviewed
    with pytest.raises(ValueError):
        load(client)
