"""Offline program/curriculum restrictions; never authorize runtime retrieval."""
from __future__ import annotations

import copy
import hashlib
import json
import re

from ...bintanong_contracts.source import Chunk, SourceSpan, check_chunk_binding
from ...bintanong_contracts.reviewed_policy_context import render_reviewed_policy_context, make_source_limits
from .register import load_pending_register
from .reviewed_policy import build_reviewed_policy_bundle


SCHEMA = 'bintanong-candidate-curriculum-catalogue-v1'
USAGES = {'single_supplied', 'older_coexisting', 'newer_incoming'}


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        allow_nan=False, separators=(',', ':')).encode('utf8')).hexdigest()


def _text(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 2048


def prepare_candidate_curriculum_catalogue(bundle, pending_chunks, *, sources,
        review_events, source_versions, version_assignments):
    """Bind explicit trusted programme assignments to unchanged reviewed candidates.

    Assignments are human-evidence preparation, not a discovery engine or register
    update. Scope tags here are proposed restrictions, never runtime authorization.
    """
    core = build_reviewed_policy_bundle(bundle['readings'], sources=sources, review_events=review_events)
    if core != bundle or (pending_chunks.get('candidate_only') is not True
            or pending_chunks.get('activation_eligible') is not False or pending_chunks.get('withheld')):
        raise ValueError('complete inactive reviewed preparation required')
    versions = {v.version_id:v for v in load_pending_register(source_versions)}
    rows = {r['reading_id']:r for r in core['readings']}
    if not rows or set(core['selection']['undergraduate']) != set(rows):
        raise ValueError('only explicitly applicable undergraduate candidate rows supported')
    raw_chunks = pending_chunks.get('chunks')
    if not isinstance(raw_chunks, list) or len(raw_chunks) != len(rows):
        raise ValueError('complete candidate row/chunk coverage required')
    grouped = {}; seen = set(); chunk_ids = set()
    for raw in raw_chunks:
        chunk = Chunk.parse(raw)
        identity = chunk.type_fields.get('reading_id')
        if identity not in rows or identity in seen or chunk.chunk_id in chunk_ids:
            raise ValueError('unique reviewed reading and chunk identities required')
        seen.add(identity); chunk_ids.add(chunk.chunk_id)
        row = rows[identity]; version = versions.get(row['version_id'])
        if any(f['decision'] not in ('accepted','corrected') for f in row['fields']):
            raise ValueError('every candidate field must have an actual accepted review')
        if version is None or (chunk.version_id, chunk.byte_sha256) != (row['version_id'],row['source_sha256']):
            raise ValueError('candidate source/version differs from its reviewed row')
        check_chunk_binding(chunk, version)
        render_reviewed_policy_context(raw, raw['spans'])
        fields = raw['type_fields']['field_associations']
        if [(f['name'],f['value'],f['event_sha256']) for f in fields] != [
                (f['name'],f['reviewed_value'],f['review_event_sha256']) for f in row['fields']]:
            raise ValueError('candidate fields differ from confirmed reviewed values')
        if make_source_limits(row,fields,[SourceSpan.parse(s) for s in raw['spans']]) != raw['type_fields']['source_limits']:
            raise ValueError('candidate must retain all reviewed source limitations')
        guidance = row.get('owner_cohort_guidance')
        if (not isinstance(guidance, dict) or not _text(guidance.get('condition'))
                or guidance.get('unknown_student_curriculum_requires_clarification') is not True
                or guidance.get('institutional_approval_inferred') is not False):
            raise ValueError('explicit conditional owner guidance required')
        owner_sha = guidance.get('event_sha256')
        event = core['review_events'].get(owner_sha)
        hashes = ({event.get('source_sha256')} if event and 'source_sha256' in event else
            set(event.get('source_hashes',{}).values()) if event else set())
        if (not event or event.get('decision_kind') != 'curriculum_validity_and_cohort_guidance'
                or row['source_sha256'] not in hashes
                or not any(e['sha256']==owner_sha and row.get('applicability_evidence_ref')==e['artifact']+'#'+identity
                    for e in row['preserved_evidence'])):
            raise ValueError('owner guidance is not bound to this source and reading')
        grouped.setdefault(row['version_id'], []).append((row, raw, owner_sha))
    if not isinstance(version_assignments, dict) or set(version_assignments) != set(grouped):
        raise ValueError('exact supplied version assignments required')
    entries = []
    for version_id, members in grouped.items():
        assignment = version_assignments[version_id]
        if (not isinstance(assignment, dict) or not isinstance(assignment.get('program_id'),str)
                or not re.fullmatch(r'[a-z][a-z0-9_-]{0,63}',assignment['program_id'])
                or not _text(assignment.get('program_label')) or not _text(assignment.get('curriculum_label'))
                or assignment.get('usage') not in USAGES):
            raise ValueError('explicit canonical program/label/usage required')
        evidence_sha = assignment.get('assignment_event_sha256')
        event = core['review_events'].get(evidence_sha)
        hashes = ({event.get('source_sha256')} if event and 'source_sha256' in event else
            set(event.get('source_hashes',{}).values()) if event else set())
        reference = assignment.get('assignment_evidence_ref')
        if (not event or members[0][0]['source_sha256'] not in hashes or not _text(reference)
                or evidence_sha not in reference or '#' not in reference
                or any(sha != assignment.get('owner_event_sha256') for _,_,sha in members)):
            raise ValueError('programme assignment and cohort evidence must bind this source')
        entries.append({**copy.deepcopy(assignment), 'version_id':version_id,
            'source_sha256':members[0][0]['source_sha256'],
            'chunk_ids':[chunk['chunk_id'] for _,chunk,_ in members],
            'row_conditions':[{'reading_id':r['reading_id'], 'condition':r['owner_cohort_guidance']['condition'],
                'applicability_evidence_ref':r['applicability_evidence_ref']} for r,_,_ in members],
            'proposed_scope_tags':['audience:undergraduate','program:'+assignment['program_id'],
                'curriculum:'+version_id], 'source_register_approval_inferred':False})
    for program in {e['program_id'] for e in entries}:
        members = [e for e in entries if e['program_id']==program]
        if (len({e['program_label'] for e in members}) != 1
                or (len(members)>1 and any(e['usage']=='single_supplied' for e in members))
                or sum(e['usage']=='newer_incoming' for e in members)>1):
            raise ValueError('incoherent supplied programme version usage')
    catalogue = {'schema_version':SCHEMA, 'candidate_only':True, 'activation_eligible':False,
        'runtime_filter_implemented':False, 'entries':entries}
    catalogue['catalogue_sha256'] = _digest(catalogue)
    return catalogue


def select_candidate_curriculum(catalogue, *, program_id=None, version_id=None, student_context=None):
    """Choose offline restrictions from explicit trusted hints, never from query text."""
    if (not isinstance(catalogue,dict) or catalogue.get('schema_version') != SCHEMA
            or catalogue.get('candidate_only') is not True or catalogue.get('activation_eligible') is not False
            or catalogue.get('runtime_filter_implemented') is not False
            or catalogue.get('catalogue_sha256') != _digest({k:v for k,v in catalogue.items() if k!='catalogue_sha256'})):
        raise ValueError('unaltered inactive curriculum catalogue required')
    for value in (program_id,version_id):
        if value is not None and not _text(value):raise ValueError('explicit nonempty canonical hint required')
    if student_context not in (None,'new_incoming','continuing'):
        raise ValueError('unsupported student context; no admission-year inference')
    result = {'candidate_only':True,'activation_eligible':False,'status':'needs_scope',
        'reason':'program_required','version_ids':[],'chunk_ids':[],'available_curricula':[]}
    if program_id is None:return result
    entries = [e for e in catalogue['entries'] if e['program_id']==program_id]
    result['available_curricula'] = [{'version_id':e['version_id'],'curriculum_label':e['curriculum_label'],
        'usage':e['usage']} for e in entries]
    if not entries:return {**result,'status':'unavailable','reason':'program_not_supplied'}
    if version_id is not None:
        chosen = [e for e in entries if e['version_id']==version_id]
        if not chosen:return {**result,'status':'unavailable','reason':'version_not_supplied_for_program'}
        if student_context=='new_incoming' and chosen[0]['usage']=='older_coexisting':
            return {**result,'reason':'contradictory_curriculum_context'}
    elif student_context=='new_incoming':
        chosen = [e for e in entries if e['usage'] in ('newer_incoming','single_supplied')]
        if len(chosen)!=1:return {**result,'reason':'incoming_curriculum_not_identified'}
    elif len(entries)==1 and entries[0]['usage']=='single_supplied':
        chosen = entries
    else:return {**result,'reason':'curriculum_required'}
    return {**result,'status':'matched','reason':'candidate_restrictions_selected',
        'version_ids':[e['version_id'] for e in chosen],
        'chunk_ids':[identity for e in chosen for identity in e['chunk_ids']],
        'proposed_scope_tags':copy.deepcopy(chosen[0]['proposed_scope_tags'])}
