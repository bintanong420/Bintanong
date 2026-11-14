"""Trusted researcher subject metadata for inactive offline candidates only."""
import copy
import hashlib
import json
import re


SCHEMA = 'bintanong-candidate-subject-catalogue-v1'


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 2048


def _subject(value):
    return isinstance(value, str) and re.fullmatch(r'[a-z][a-z0-9_]{0,127}', value) is not None


def _digest(value):
    try:
        payload = json.dumps(value, sort_keys=True, ensure_ascii=False,
                             allow_nan=False, separators=(',', ':'))
    except (ValueError, TypeError) as exc:
        raise ValueError('JSON source bindings required') from exc
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _bindings(chunks):
    if not isinstance(chunks, list):
        raise ValueError('complete candidate chunk list required')
    rows = []
    for chunk in chunks:
        try:
            fields = chunk['type_fields']
            identity, reading, version = chunk['chunk_id'], fields['reading_id'], chunk['version_id']
            source_hash, scope = chunk['byte_sha256'], chunk['scope']
            required = fields.get('required_neighbor_chunk_ids', [])
            if (not all(_text(v) for v in (identity, reading, version))
                    or not isinstance(source_hash, str) or re.fullmatch(r'[0-9a-f]{64}', source_hash) is None
                    or not isinstance(scope, list) or any(not _text(v) for v in scope)
                    or not isinstance(required, list) or any(not _text(v) for v in required)
                    or len(set(required)) != len(required)):
                raise ValueError('invalid candidate metadata')
            rows.append(dict(chunk_id=identity, reading_id=reading, version_id=version,
                source_sha256=source_hash, chunk_sha256=_digest(chunk), scope=copy.deepcopy(scope),
                applicability_basis_ref=copy.deepcopy(fields.get('applicability_basis_ref')),
                required_chunk_ids=sorted(required)))
        except (KeyError, TypeError, AttributeError) as exc:
            raise ValueError('complete candidate metadata required') from exc
    if len({r['chunk_id'] for r in rows}) != len(rows) or len({r['reading_id'] for r in rows}) != len(rows):
        raise ValueError('unambiguous chunk and reading identities required')
    return sorted(rows, key=lambda r: r['chunk_id'])


def prepare_candidate_subject_catalogue(chunks, assignments):
    """Bind explicit source-reading assignments; do not certify their truth.

    Inputs must come from a trusted research preparation workflow. The digest
    detects accidental changes, not forged assignments. No source content,
    citation validity, institutional approval or requested claim is verified here.
    """
    bindings = _bindings(chunks)
    if not isinstance(assignments, list):
        raise ValueError('explicit source-reading assignments required')
    by_reading = {r['reading_id']: r for r in bindings}
    by_chunk = {r['chunk_id']: r for r in bindings}
    classified = {}
    for assignment in assignments:
        if (not isinstance(assignment, dict) or set(assignment) != {'reading_id', 'subject_id', 'basis_ref'}
                or not _text(assignment['reading_id']) or not _subject(assignment['subject_id'])
                or not _text(assignment['basis_ref'])):
            raise ValueError('explicit canonical subject and provenance reference required')
        reading = assignment['reading_id']
        if reading not in by_reading or reading in classified:
            raise ValueError('one assignment per available source reading required')
        row = by_reading[reading]
        audiences = {tag for tag in row['scope'] if tag.startswith('audience:')}
        if audiences != {'audience:undergraduate'} or not _text(row['applicability_basis_ref']):
            raise ValueError('undergraduate applicability metadata required')
        classified[reading] = copy.deepcopy(assignment)
    for reading, assignment in classified.items():
        for dependency in by_reading[reading]['required_chunk_ids']:
            target = by_chunk.get(dependency)
            if (target is None or target['reading_id'] not in classified
                    or classified[target['reading_id']]['subject_id'] != assignment['subject_id']):
                raise ValueError('complete same-subject dependency assignments required')
    catalogue = dict(schema_version=SCHEMA, candidate_only=True, activation_eligible=False,
        runtime_filter_implemented=False, claim_coverage='unknown',
        validation_scope='metadata_bindings_only', bindings=bindings,
        assignments=sorted(classified.values(), key=lambda r: r['reading_id']),
        unassigned_chunk_ids=sorted(r['chunk_id'] for r in bindings if r['reading_id'] not in classified))
    catalogue['catalogue_sha256'] = _digest(catalogue)
    return catalogue


def select_candidate_subject(catalogue, chunks, *, subject_id=None):
    """Select an explicit trusted subject; never parse queries or infer validity."""
    if (not isinstance(catalogue, dict) or catalogue.get('schema_version') != SCHEMA
            or catalogue.get('candidate_only') is not True or catalogue.get('activation_eligible') is not False
            or catalogue.get('runtime_filter_implemented') is not False):
        raise ValueError('inactive source-bound subject catalogue required')
    expected = prepare_candidate_subject_catalogue(chunks, catalogue.get('assignments'))
    if catalogue != expected:
        raise ValueError('unchanged catalogue and current candidate bindings required')
    if subject_id is not None and not _subject(subject_id):
        raise ValueError('explicit canonical subject hint required')
    assignments = [r for r in expected['assignments'] if r['subject_id'] == subject_id]
    by_reading = {r['reading_id']: r for r in expected['bindings']}
    rows = [by_reading[r['reading_id']] | r for r in assignments]
    return dict(schema_version='bintanong-candidate-subject-selection-v1', candidate_only=True,
        activation_eligible=False, runtime_filter_implemented=False, claim_coverage='unknown',
        validation_scope='metadata_bindings_only', subject_id=subject_id,
        status='needs_subject' if subject_id is None else 'matched' if rows else 'unavailable',
        reason='subject_hint_required' if subject_id is None else 'candidate_subject_metadata_selected'
            if rows else 'subject_not_in_candidate_catalogue',
        chunk_ids=[r['chunk_id'] for r in rows], rows=copy.deepcopy(rows),
        catalogue_sha256=expected['catalogue_sha256'])
