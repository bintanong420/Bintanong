"""Read-only stand-in for runtime retrieval reads over a reviewed package; no database.

Mirrors the retrieve_context RPC (cosine similarity, scope containment, threshold,
similarity/chunk ordering, top-k, required neighbors) so research mode can use
reviewed real chunks without loading them into Supabase or recording approval.
"""
import copy
import math

_CONFIG_KEYS = ('model_id', 'model_revision', 'dimension', 'normalization', 'prompt_fingerprint',
                'preprocessing_fingerprint', 'tokenizer_fingerprint')


def _cosine(a, b):
    norm = math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
    return sum(x * y for x, y in zip(a, b)) / norm if norm else 0.0


class PackageStorage:
    def __init__(self, *, release_id, manifest, chunks, versions, vectors):
        self.release_id, self.embedding_set_id = release_id, manifest['embedding_set_id']
        self._config = {key: manifest[key] for key in _CONFIG_KEYS}
        self._chunks = {c['chunk_id']: copy.deepcopy(c) for c in chunks}
        if set(vectors) != set(self._chunks):
            raise ValueError('package_vector_mismatch')
        if any(c['version_id'] not in versions for c in self._chunks.values()):
            raise ValueError('package_version_missing')
        self._vectors, self._versions = dict(vectors), copy.deepcopy(versions)

    def select(self, table, *, filters, role):
        if role != 'runtime':
            raise ValueError('runtime_reads_only')
        if table == 'knowledge_releases':
            return ([dict(embedding_set_id=self.embedding_set_id)]
                    if filters == {'release_id': 'eq.' + self.release_id} else [])
        if table == 'embedding_sets':
            return ([dict(self._config)]
                    if filters == {'embedding_set_id': 'eq.' + self.embedding_set_id} else [])
        raise ValueError('unsupported_table')

    def rpc(self, name, params, *, role):
        if role != 'runtime' or name != 'retrieve_context':
            raise ValueError('unsupported_rpc')
        if params['p_release_id'] != self.release_id:
            return dict(status='release_changed')
        chunk_ids = params.get('p_chunk_ids', [])
        if (not isinstance(chunk_ids, list) or len(chunk_ids) > 128
                or any(not isinstance(cid, str) or not 1 <= len(cid) <= 256 or not cid.strip()
                       for cid in chunk_ids)):
            raise ValueError('invalid retrieval filters')
        selected_ids = set(chunk_ids)
        scope = set(params['p_scope'])
        versions = set(params.get('p_version_ids', []))
        scored = [(cid, _cosine(params['query_embedding'], self._vectors[cid])) for cid, c in self._chunks.items()
                  if (not selected_ids or cid in selected_ids) and (not scope or set(c['scope']) <= scope)
                  and (not versions or c['version_id'] in versions)]
        kept = sorted(((cid, s) for cid, s in scored if s >= params['p_min_similarity']),
                      key=lambda item: (-item[1], item[0]))[:params['p_top_k']]
        similarity = dict(scored)
        items = []
        for cid, score in kept:
            row = self._row(cid, score)
            needed, pending = {cid}, [cid]
            for current in pending:
                for neighbor in self._chunks[current]['type_fields'].get('required_neighbor_chunk_ids', []):
                    if (neighbor not in needed and neighbor in similarity
                            and self._chunks[neighbor]['version_id'] == self._chunks[cid]['version_id']):
                        needed.add(neighbor)
                        pending.append(neighbor)
            row['neighbors'] = [self._row(n, similarity[n]) for n in sorted(needed - {cid})]
            items.append(row)
        return dict(status='ok', release_id=self.release_id, embedding_set_id=self.embedding_set_id, items=items)

    def _row(self, cid, score):
        chunk = copy.deepcopy(self._chunks[cid])
        spans = chunk.pop('spans')
        for order, span in enumerate(spans):
            span.update(chunk_id=cid, span_order=order, span_id=f'{cid}:{order}')
        return dict(chunk=chunk, spans=spans, version=copy.deepcopy(self._versions[chunk['version_id']]),
                    similarity=score)
