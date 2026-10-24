"""Read shared institutional research data, preserving the prior review boundary."""
import copy
import re

from backend.bintanong_contracts.reviewed_policy_context import render_reviewed_policy_context
from backend.bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue
from backend.bintanong_retrieval.candidate_claims import prepare_candidate_claim_reviews
from backend.bintanong_storage.selected_release_review import SPAN_KEYS


def load_document_snapshot(client, *, release_id, authorization_ref):
    def rows(table, filters=None):
        return client.select(table, filters=filters, role='runtime')

    releases = rows('knowledge_releases', {'release_id': 'eq.' + release_id})
    if (len(releases) != 1 or releases[0].get('status') != 'active' or
            releases[0].get('release_kind') != 'research' or
            releases[0].get('research_authorization_ref') != authorization_ref):
        raise ValueError('hosted_release_not_active_research')
    release = releases[0]
    # Runtime uses anon/RLS and the published release's immutable review binding.
    # Full reviewer receipts are intentionally not readable by the runtime role.
    if not re.fullmatch(r'[0-9a-f]{64}', release.get('review_scope_id') or ''):
        raise ValueError('selected_review_required')
    links = rows('release_chunks', {'release_id': 'eq.' + release_id})
    version_links = rows('release_document_versions', {'release_id': 'eq.' + release_id})
    reviewed = {c['chunk_id'] for c in links}
    source_ids = {v['version_id'] for v in version_links}
    if (not reviewed or not source_ids or len(links) != len(reviewed) or
            len(version_links) != len(source_ids) or
            release.get('expected_chunk_count') != len(reviewed) or
            release.get('expected_document_version_count') != len(source_ids)):
        raise ValueError('release_review_membership_differs')
    versions = {v['version_id']: v for v in rows('document_versions') if v['version_id'] in source_ids}
    if set(versions) != source_ids:
        raise ValueError('reviewed_source_identity_differs')
    source_hashes = {key: value['byte_sha256'] for key, value in versions.items()}
    sets = rows('embedding_sets', {'embedding_set_id': 'eq.' + release['embedding_set_id']})
    if len(sets) != 1 or sets[0]['embedding_set_id'] != release['embedding_set_id']:
        raise ValueError('release_embedding_set_required')
    spans = {}
    for span in rows('source_spans'):
        if span['chunk_id'] in reviewed:
            spans.setdefault(span['chunk_id'], []).append({key: span[key] for key in SPAN_KEYS})
    chunks = []
    for raw in rows('chunks'):
        if raw['chunk_id'] not in reviewed:
            continue
        located = sorted(spans.get(raw['chunk_id'], []), key=lambda s: s['span_order'])
        if (source_hashes.get(raw['version_id']) != raw['byte_sha256'] or
                {s for s in raw['scope'] if s.startswith('audience:')} != {'audience:undergraduate'}):
            raise ValueError('reviewed_document_snapshot_differs')
        render_reviewed_policy_context(raw, located)
        chunk = {key: value for key, value in raw.items() if key != 'created_at'}
        chunk['spans'] = located
        chunks.append(chunk)
    if len(chunks) != len(reviewed) or len({c['chunk_id'] for c in chunks}) != len(reviewed):
        raise ValueError('reviewed_document_snapshot_incomplete')
    return dict(manifest=sets[0], chunks=sorted(chunks, key=lambda c: c['chunk_id']), versions=versions)


def bind_document_policy(snapshot, metadata):
    if metadata is None:
        raise ValueError('source_claim_index_unavailable')
    if not isinstance(metadata, dict) or set(metadata) != {'assignments', 'reviews'}:
        raise ValueError('source_claim_index_invalid')
    package = copy.deepcopy(snapshot)
    package['catalogue'] = prepare_candidate_subject_catalogue(package['chunks'], metadata['assignments'])
    package['register'] = prepare_candidate_claim_reviews(package['catalogue'], package['chunks'], metadata['reviews'])
    return package
