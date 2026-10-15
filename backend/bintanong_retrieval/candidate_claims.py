"""Offline exact matching of trusted caller claims to declared source limits."""
import copy

from .candidate_subject import select_candidate_subject


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 2048


def _strings(value):
    return (isinstance(value, list) and all(_text(v) for v in value)
            and len(set(value)) == len(value))


def build_candidate_claim_report(catalogue, chunks, *, subject_id=None,
                                 requested_claims=None, emitted_chunk_ids=None):
    """Report declared limitations, never infer support from a matching subject.

    Claims use exact source-limit wording supplied by a trusted caller. Unknown
    claims remain unassessed; this cannot discover undeclared gaps or establish
    affirmative support. Context IDs are literal identities, not proof of emitted
    text/citations. Source limitations are inspected across the selected snapshot,
    including chunks absent from context. No benchmark labels or scores are used.
    """
    selection = select_candidate_subject(catalogue, chunks, subject_id=subject_id)
    if requested_claims is not None and not _strings(requested_claims):
        raise ValueError('distinct explicit requested claim strings required')
    by_id = {c['chunk_id']: c for c in chunks}
    if (emitted_chunk_ids is not None and (not _strings(emitted_chunk_ids)
            or any(i not in by_id for i in emitted_chunk_ids))):
        raise ValueError('distinct context IDs from the current snapshot required')
    requested = [] if requested_claims is None else list(requested_claims)
    emitted = [] if emitted_chunk_ids is None else list(emitted_chunk_ids)
    selected = set(selection['chunk_ids'])
    limits = []
    for identity in selection['chunk_ids']:
        chunk = by_id[identity]
        declared = chunk['type_fields'].get('source_limits', [])
        if not isinstance(declared, list):
            raise ValueError('declared source limit list required')
        seen = set()
        for limit in declared:
            if (not isinstance(limit, dict)
                    or any(not _text(limit.get(k)) for k in ('gap_id', 'issue', 'message'))
                    or limit.get('resolution') != 'unresolved'
                    or not _strings(limit.get('affected_claims')) or not limit['affected_claims']
                    or limit.get('source_sha256') != chunk['byte_sha256']
                    or limit.get('version_id') != chunk['version_id']):
                raise ValueError('unresolved source-bound limitation metadata required')
            if limit['gap_id'] in seen:
                raise ValueError('unambiguous source limit IDs required per chunk')
            seen.add(limit['gap_id'])
            limits.append(dict(chunk_id=identity, reading_id=chunk['type_fields']['reading_id'],
                chunk_emitted=None if emitted_chunk_ids is None else identity in emitted,
                limit=copy.deepcopy(limit)))
    claims = []
    for claim in requested:
        matches = [i for i, row in enumerate(limits) if claim in row['limit']['affected_claims']]
        claims.append(dict(claim=claim, status='not_established' if matches else 'unassessed',
                           source_limit_indexes=matches))
    blocked = any(c['status'] == 'not_established' for c in claims)
    status = ('needs_subject' if subject_id is None else
              'unavailable_subject' if selection['status'] == 'unavailable' else
              'needs_claims' if not requested else
              'insufficient_evidence' if blocked else 'unassessed')
    return dict(schema_version='bintanong-candidate-claim-report-v1', candidate_only=True,
        activation_eligible=False, runtime_filter_implemented=False,
        claim_inference_implemented=False, source_content_verified=False,
        assessment_method='exact_declared_source_limit_match',
        limitation_scope='selected_subject_candidate_snapshot',
        context_validation_scope='literal_chunk_ids_only',
        catalogue_sha256=selection['catalogue_sha256'], subject_id=subject_id,
        status=status, claim_coverage='not_established' if blocked else 'unassessed',
        claims=claims, source_limits=limits, context_ids_provided=emitted_chunk_ids is not None,
        emitted_chunk_ids=emitted, subject_context_chunk_ids=[i for i in emitted if i in selected],
        other_context_chunk_ids=[i for i in emitted if i not in selected])
