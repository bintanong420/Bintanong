"""Reviewed curriculum ledgers read from the hosted research release (owner decision, 23 Oct 2026).

Runtime reads only. Each stored ledger is rebuilt by the authoring/compiler validation before use, so
a ledger whose rules, facts or review digests were changed after review is refused, never executed.
"""
from ..bintanong_symbolic.bundle import prepare_runtime_bundle


def load_release_curricula(client, *, release_id, authorization_ref):
    """Return {curriculum_id: ledger} for the active owner-authorized research release."""
    releases = client.select('knowledge_releases', filters={'release_id': 'eq.' + release_id}, role='runtime')
    if (len(releases) != 1 or releases[0].get('status') != 'active'
            or releases[0].get('release_kind') != 'research'
            or releases[0].get('research_authorization_ref') != authorization_ref):
        raise ValueError('hosted_release_not_active_research')
    links = client.select('release_curriculum_ledgers', filters={'release_id': 'eq.' + release_id}, role='runtime')
    stored = {r['ledger_sha256']: r for r in client.select('curriculum_ledgers', role='runtime')}
    curricula = {}
    for link in links:
        row = stored.get(link['ledger_sha256'])
        if row is None or row['curriculum_id'] != link['curriculum_id']:
            raise ValueError('hosted_curriculum_missing')
        ledger = row['ledger']
        if (ledger.get('content_sha256') != link['ledger_sha256']
                or ledger.get('scope', {}).get('curriculum_id') != link['curriculum_id']):
            raise ValueError('hosted_curriculum_differs')
        # Rebuilds every course record and review digest; raises if the stored ledger was altered.
        if prepare_runtime_bundle(ledger)['ledger']['content_sha256'] != link['ledger_sha256']:
            raise ValueError('hosted_curriculum_differs')
        curricula[link['curriculum_id']] = ledger
    return curricula
