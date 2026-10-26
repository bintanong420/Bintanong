"""Offline exact matching of trusted caller claims to declared source limits."""
import copy
import re

from .candidate_subject import _digest, select_candidate_subject


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 2048


def _strings(value):
    return (isinstance(value, list) and all(_text(v) for v in value)
            and len(set(value)) == len(value))


def _sha256(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def _review_fields(review, by_reading):
    rows = []
    for ref in review['field_refs']:
        chunk = by_reading[ref['reading_id']]
        fields = chunk['type_fields'].get('field_associations')
        matches = [f for f in fields if isinstance(f, dict) and f.get('name') == ref['field_name']] if isinstance(fields, list) else []
        if len(matches) != 1:
            raise ValueError('one existing source field association required')
        field = matches[0]
        indexes, spans = field.get('span_indexes'), chunk.get('spans')
        if (field.get('source_blank') is not False or field.get('value') is None
                or isinstance(field['value'], str) and not field['value'].strip()
                or not _sha256(field.get('event_sha256'))
                or not isinstance(spans, list) or not isinstance(indexes, list) or not indexes
                or any(type(i) is not int or not 0 <= i < len(spans) for i in indexes)
                or len(set(indexes)) != len(indexes)):
            raise ValueError('nonblank reviewed fields and source spans required')
        located = [spans[i] for i in indexes]
        if any(not isinstance(s, dict) or s.get('version_id') != chunk['version_id']
               or s.get('byte_sha256') != chunk['byte_sha256'] for s in located):
            raise ValueError('matching source field span identity required')
        rows.append(dict(chunk_id=chunk['chunk_id'], reading_id=ref['reading_id'],
            version_id=chunk['version_id'], source_sha256=chunk['byte_sha256'],
            field=copy.deepcopy(field), spans=copy.deepcopy(located)))
    return rows


def prepare_candidate_claim_reviews(catalogue, chunks, reviews):
    """Bind trusted source-side findings; metadata checks cannot certify truth."""
    select_candidate_subject(catalogue, chunks)
    if not isinstance(reviews, list):
        raise ValueError('explicit source review list required')
    by_reading = {c['type_fields']['reading_id']: c for c in chunks}
    subjects = {a['reading_id']: a['subject_id'] for a in catalogue['assignments']}
    keys = {'subject_id', 'claim', 'finding', 'reviewed_chunk_ids', 'field_refs', 'basis_ref', 'basis_sha256'}
    normalized, seen = [], set()
    for review in reviews:
        if (not isinstance(review, dict) or set(review) - {'procedure_order'} != keys
                or not all(_text(review[k]) for k in ('subject_id', 'claim', 'basis_ref'))
                or not _sha256(review['basis_sha256'])
                or review['finding'] not in ('visible_fields', 'not_stated_in_selected_fields')
                or not _strings(review['reviewed_chunk_ids']) or not isinstance(review['field_refs'], list)):
            raise ValueError('complete explicit source review metadata required')
        subject = review['subject_id']
        available = {c['chunk_id'] for reading, c in by_reading.items() if subjects.get(reading) == subject}
        key = (subject, review['claim'])
        if not available or set(review['reviewed_chunk_ids']) != available or key in seen:
            raise ValueError('one claim review over the complete subject snapshot required')
        seen.add(key)
        refs = set()
        for ref in review['field_refs']:
            if (not isinstance(ref, dict) or set(ref) != {'reading_id', 'field_name'}
                    or not all(_text(ref[k]) for k in ('reading_id', 'field_name'))
                    or subjects.get(ref['reading_id']) != subject
                    or (ref['reading_id'], ref['field_name']) in refs):
                raise ValueError('unique same-subject source field references required')
            refs.add((ref['reading_id'], ref['field_name']))
        if bool(refs) != (review['finding'] == 'visible_fields'):
            raise ValueError('visible reviews require fields; absence reviews cannot cite a value')
        if 'procedure_order' in review:
            try:
                fields = _review_fields(review, by_reading)
            except ValueError:
                raise ValueError('procedure_order_requires_reviewed_source_steps') from None
            steps = [f for f in fields if f['field']['name'] == 'client_step']
            order = review['procedure_order']
            if (not _strings(order) or len(order) < 2
                    or set(order) != {f['reading_id'] for f in steps}
                    or any(not isinstance(f['field']['value'], str) or not f['field']['value'].strip()
                           for f in steps)
                    or len({(f['version_id'], f['source_sha256']) for f in steps}) != 1):
                raise ValueError('procedure_order_requires_all_steps_from_one_source')
        else:
            _review_fields(review, by_reading)
        normalized.append(copy.deepcopy(review) | dict(reviewed_chunk_ids=sorted(available),
            field_refs=sorted(copy.deepcopy(review['field_refs']), key=lambda r: (r['reading_id'], r['field_name']))))
    register = dict(schema_version='bintanong-candidate-claim-reviews-v1',
        candidate_only=True, activation_eligible=False, runtime_filter_implemented=False,
        validation_scope='trusted_source_review_metadata', catalogue_sha256=catalogue['catalogue_sha256'],
        reviews=sorted(normalized, key=lambda r: (r['subject_id'], r['claim'])))
    register['reviews_sha256'] = _digest(register)
    return register


def build_candidate_claim_report(catalogue, chunks, *, subject_id=None,
                                 requested_claims=None, emitted_chunk_ids=None, claim_reviews=None):
    """Report declared limitations and optional trusted source-review metadata.

    Claims use exact source-limit wording supplied by a trusted caller. Unknown
    claims remain unassessed; this cannot discover undeclared gaps or establish
    affirmative support. Context IDs are literal identities, not proof of emitted
    text/citations. Source limitations are inspected across the selected snapshot,
    including chunks absent from context. Optional source reviews produce a v2
    report with field/context availability, never certified answer sufficiency.
    No benchmark labels or scores are used. Without reviews the v1 output is unchanged.
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
    report = dict(schema_version='bintanong-candidate-claim-report-v1', candidate_only=True,
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
    if claim_reviews is None:
        return report
    if not isinstance(claim_reviews, dict):
        raise ValueError('source-bound claim review register required')
    expected = prepare_candidate_claim_reviews(catalogue, chunks, claim_reviews.get('reviews'))
    if claim_reviews != expected:
        raise ValueError('unchanged source-bound claim review register required')
    by_reading = {c['type_fields']['reading_id']: c for c in chunks}
    reviews = {(r['subject_id'], r['claim']): r for r in expected['reviews']}
    for claim in claims:
        review = reviews.get((subject_id, claim['claim']))
        fields = _review_fields(review, by_reading) if review else []
        required = {r['chunk_id'] for r in fields}
        pending = list(required)
        for identity in pending:
            for dependency in by_id[identity]['type_fields'].get('required_neighbor_chunk_ids', []):
                if dependency not in required:
                    required.add(dependency)
                    pending.append(dependency)
        missing = None if emitted_chunk_ids is None else sorted(required - set(emitted))
        claim.update(source_review=copy.deepcopy(review), source_fields=fields,
                     required_chunk_ids=sorted(required), missing_required_chunk_ids=missing)
        if claim['source_limit_indexes']:
            continue
        if review and review['finding'] == 'not_stated_in_selected_fields':
            claim['status'] = 'not_established'
        elif review:
            claim['status'] = 'reviewed_fields_available' if missing == [] else 'reviewed_fields_not_in_context'
    blocked = any(c['status'] == 'not_established' for c in claims)
    if status not in ('needs_subject', 'unavailable_subject', 'needs_claims'):
        status = ('insufficient_evidence' if blocked else 'insufficient_context'
                  if any(c['status'] == 'reviewed_fields_not_in_context' for c in claims) else
                  'reviewed_fields_available' if all(c['status'] == 'reviewed_fields_available' for c in claims)
                  else 'unassessed')
    report.update(schema_version='bintanong-candidate-claim-report-v2',
        status=status, claim_coverage='not_established' if blocked else 'unassessed',
        claim_reviews_sha256=expected['reviews_sha256'], answer_sufficiency='unassessed',
        assessment_method='exact_source_bound_review_and_limit_match')
    return report
