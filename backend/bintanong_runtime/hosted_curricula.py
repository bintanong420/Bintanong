"""Reviewed curriculum ledgers read from the hosted research release (owner decision, 23 Oct 2026).

Runtime reads only. Each stored ledger is rebuilt by the authoring/compiler validation before use, so
a ledger whose rules, facts or review digests were changed after review is refused, never executed.
"""
import httpx

from ..bintanong_storage.client import StorageError
from ..bintanong_symbolic.bundle import prepare_runtime_bundle

READ_ATTEMPTS = 3


def _read_ledger(client, ledger_sha256):
    """The storage client never retries; this is a startup read, so resending it is safe."""
    for attempt in range(1, READ_ATTEMPTS + 1):
        try:
            return client.select('curriculum_ledgers', filters={'ledger_sha256': 'eq.' + ledger_sha256}, role='runtime')
        except StorageError as exc:
            if attempt == READ_ATTEMPTS or not isinstance(exc.__cause__, httpx.RequestError):
                raise
    raise AssertionError('unreachable')


def load_release_curricula(client, *, release_id, authorization_ref):
    """Return {curriculum_id: ledger} for the active owner-authorized research release."""
    releases = client.select('knowledge_releases', filters={'release_id': 'eq.' + release_id}, role='runtime')
    if (len(releases) != 1 or releases[0].get('status') != 'active'
            or releases[0].get('release_kind') != 'research'
            or releases[0].get('research_authorization_ref') != authorization_ref):
        raise ValueError('hosted_release_not_active_research')
    links = client.select('release_curriculum_ledgers', filters={'release_id': 'eq.' + release_id}, role='runtime')
    curricula = {}
    for link in links:
        # One ledger per read: each is about 0.5 MB, the whole table about 19 MB.
        rows = _read_ledger(client, link['ledger_sha256'])
        if len(rows) != 1 or rows[0]['curriculum_id'] != link['curriculum_id']:
            raise ValueError('hosted_curriculum_missing')
        ledger = rows[0]['ledger']
        if (ledger.get('content_sha256') != link['ledger_sha256']
                or ledger.get('scope', {}).get('curriculum_id') != link['curriculum_id']):
            raise ValueError('hosted_curriculum_differs')
        # Rebuilds every course record and review digest; raises if the stored ledger was altered.
        if prepare_runtime_bundle(ledger)['ledger']['content_sha256'] != link['ledger_sha256']:
            raise ValueError('hosted_curriculum_differs')
        curricula[link['curriculum_id']] = ledger
    return curricula
