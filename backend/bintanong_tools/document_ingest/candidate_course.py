"""Reviewed target-course restrictions for offline candidates only."""
from __future__ import annotations

import copy

from .candidate_curriculum import (
    _digest, _text, prepare_candidate_curriculum_catalogue, select_candidate_curriculum,
)


SCHEMA = 'bintanong-candidate-course-index-v1'


def _matching_keys(printed_code):
    key = ''.join(printed_code.upper().split())
    keys = [key]
    if key.endswith('/L') and len(key)>2:
        keys.append(key[:-2])
    return keys


def prepare_candidate_course_index(bundle, pending_chunks, *, sources,
        review_events, source_versions, version_assignments):
    """Replay complete reviewed candidates before deriving course identity keys.

    Index digests detect accidental changes; they are not institutional approval
    or signatures. Reprepare from trusted source/review inputs after any change.
    """
    catalogue = prepare_candidate_curriculum_catalogue(bundle,pending_chunks,
        sources=sources,review_events=review_events,source_versions=source_versions,
        version_assignments=version_assignments)
    rows = []
    for chunk in pending_chunks['chunks']:
        fields = [f for f in chunk['type_fields']['field_associations'] if f['name']=='course_code']
        if (len(fields)!=1 or not _text(fields[0]['value']) or not fields[0]['span_indexes']
                or fields[0].get('field_kind')=='heading_metadata'):
            raise ValueError('one nonblank reviewed source course-code field required')
        field = fields[0]
        rows.append({'reading_id':chunk['type_fields']['reading_id'],
            'chunk_id':chunk['chunk_id'],'version_id':chunk['version_id'],
            'source_sha256':chunk['byte_sha256'],'printed_code':field['value'],
            'matching_keys':_matching_keys(field['value']), 'field':copy.deepcopy(field),
            'spans':copy.deepcopy([chunk['spans'][i] for i in field['span_indexes']])})
    index = {'schema_version':SCHEMA,'candidate_only':True,'activation_eligible':False,
        'runtime_filter_implemented':False,'curriculum_catalogue':catalogue,'rows':rows}
    index['index_sha256'] = _digest(index)
    return index


def select_candidate_course(index, *, program_id=None, version_id=None,
        student_context=None, target_course=None):
    """Filter an explicit target role after curriculum selection, never parse a query.

    A missing code means only that the selected candidate subset has no matching
    identity. It makes no claim about the complete university curriculum.
    """
    if (not isinstance(index,dict) or index.get('schema_version')!=SCHEMA
            or index.get('candidate_only') is not True or index.get('activation_eligible') is not False
            or index.get('runtime_filter_implemented') is not False
            or index.get('index_sha256')!=_digest({k:v for k,v in index.items() if k!='index_sha256'})):
        raise ValueError('unaltered inactive reviewed course index required')
    if target_course is not None and not _text(target_course):
        raise ValueError('explicit nonempty target-course hint required')
    scope = select_candidate_curriculum(index['curriculum_catalogue'],program_id=program_id,
        version_id=version_id,student_context=student_context)
    if scope['status']!='matched':return scope
    result = {**scope,'chunk_ids':[],'course_identities':[]}
    if target_course is None:
        return {**result,'status':'needs_target_course','reason':'target_course_required'}
    key = ''.join(target_course.upper().split())
    matches = [row for row in index['rows'] if row['chunk_id'] in scope['chunk_ids']
        and key in row['matching_keys']]
    if not matches:
        return {**result,'status':'unavailable','reason':'target_course_not_in_candidates'}
    return {**result,'reason':'candidate_course_restrictions_selected',
        'chunk_ids':[row['chunk_id'] for row in matches],
        'course_identities':copy.deepcopy(matches)}
