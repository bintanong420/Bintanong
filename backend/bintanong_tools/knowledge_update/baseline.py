from __future__ import annotations

import copy

from ...bintanong_retrieval.candidate_claims import prepare_candidate_claim_reviews
from ...bintanong_retrieval.candidate_subject import prepare_candidate_subject_catalogue


def retained_ids(baseline: dict, membership: dict, selected: list[str]) -> list[str]:
    if not isinstance(membership, dict) or set(membership) != {'retained', 'replaced', 'removed'}:
        raise ValueError('explicit retained/replaced/removed baseline membership required')
    retained, replaced, removed = (membership[k] for k in ('retained', 'replaced', 'removed'))
    if (not isinstance(retained, list) or not isinstance(replaced, dict) or not isinstance(removed, list)
            or any(not isinstance(i, str) for i in [*retained, *replaced, *removed])):
        raise ValueError('invalid baseline membership')
    all_ids = [*retained, *replaced, *removed]
    if len(set(all_ids)) != len(all_ids) or set(all_ids) != {c['chunk_id'] for c in baseline['chunks']}:
        raise ValueError('membership must partition every baseline chunk exactly once')
    if any(not isinstance(i, str) or i not in selected for i in replaced.values()):
        raise ValueError('each replacement must identify an explicitly selected new reading')
    return retained


def combine(chunks: list, catalogue: dict, claims: dict, baseline: dict, membership: dict):
    retained = retained_ids(baseline, membership, [c['type_fields']['reading_id'] for c in chunks])
    old = [copy.deepcopy(c) for c in baseline['chunks'] if c['chunk_id'] in retained]
    if {c['chunk_id'] for c in chunks} & set(retained):
        raise ValueError('a retained baseline chunk cannot also be rebuilt')
    reading_ids = {c['type_fields']['reading_id'] for c in old}
    assignments = [a for a in baseline['catalogue']['assignments'] if a['reading_id'] in reading_ids]
    subjects = {a['subject_id'] for a in assignments}
    if subjects & {a['subject_id'] for a in catalogue['assignments']}:
        raise ValueError('changed subjects require cumulative source review; replace their baseline readings')
    for review in baseline['claim_reviews']['reviews']:
        if review['subject_id'] in subjects and not set(review['reviewed_chunk_ids']) <= set(retained):
            raise ValueError('retain a complete subject review or replace/remove it in full')
    merged = chunks + old
    catalogue = prepare_candidate_subject_catalogue(merged, catalogue['assignments'] + assignments)
    reviews = claims['reviews'] + [r for r in baseline['claim_reviews']['reviews'] if r['subject_id'] in subjects]
    claims = prepare_candidate_claim_reviews(catalogue, merged, reviews)
    return merged, catalogue, claims
