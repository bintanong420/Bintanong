"""Runtime reads of one active hosted research release, under the local pin's release id.

The pin's release id also binds the reviewed rule bundle, so the hosted document release keeps
its own id; this adapter translates between them. It refuses to start unless the hosted release
is active, of kind research, carries the owner's authorization reference, and holds exactly the
reviewed package's chunks (ids and content hashes).
"""


class HostedReleaseStorage:
    def __init__(self, client, *, pin_release_id, hosted_release_id, authorization_ref, chunks):
        self.client, self.pin, self.hosted = client, pin_release_id, hosted_release_id
        releases = client.select('knowledge_releases', filters={'release_id': 'eq.' + hosted_release_id},
                                 role='runtime')
        if (len(releases) != 1 or releases[0].get('status') != 'active'
                or releases[0].get('release_kind') != 'research'
                or releases[0].get('research_authorization_ref') != authorization_ref):
            raise ValueError('hosted_release_not_active_research')
        hosted = {c['chunk_id']: c['content_hash'] for c in client.select('chunks', role='runtime')}
        if hosted != {c['chunk_id']: c['content_hash'] for c in chunks}:
            raise ValueError('hosted_release_differs')

    def select(self, table, *, filters, role):
        if role != 'runtime':
            raise ValueError('runtime_reads_only')
        if table == 'knowledge_releases':
            if filters != {'release_id': 'eq.' + self.pin}:
                return []
            filters = {'release_id': 'eq.' + self.hosted}
        return self.client.select(table, filters=filters, role='runtime')

    def rpc(self, name, params, *, role):
        if role != 'runtime':
            raise ValueError('runtime_reads_only')
        if params.get('p_release_id') != self.pin:
            return dict(status='release_changed')
        response = self.client.rpc(name, dict(params, p_release_id=self.hosted), role='runtime')
        if response.get('release_id') == self.hosted:
            response = dict(response, release_id=self.pin)
        return response
