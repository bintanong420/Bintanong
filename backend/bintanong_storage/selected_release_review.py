"""Exact selected-review coverage; never a source-authority transition."""
import copy
import json
from pathlib import PurePosixPath
import re

from backend.bintanong_contracts.base import parse_timestamp
from backend.bintanong_contracts.reviewed_policy_context import (
    context_chunker_version, render_reviewed_policy_context, serialize_reviewed_fields)
from backend.bintanong_contracts.reviewed_record_groups import validate_record_group
from .client import SupabaseStorageClient


RECEIPT_KEYS = {'receipt_format','review_scope_id','supported_scope','decision','sources','chunks'}
DECISION_KEYS = {'evidence_id','reviewer_label','compiler_label','recorded_at','timestamp_meaning',
    'owner_response','decision_document','acceptance_record_sha256','coverage_inventory_sha256','draft_chunks_sha256'}
SPAN_KEYS = {'chunk_id','span_order','version_id','byte_sha256','page','printed_page_label',
    'locator','text','bbox','bbox_origin','page_size','extraction'}


def _object(value, keys):
    if not isinstance(value,dict) or set(value) != keys:
        raise ValueError('Closed selected-review object required')


def _text(value):
    if not isinstance(value,str) or not value.strip():
        raise ValueError('Nonblank selected-review text required')


def _hash(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):
        raise ValueError('Exact selected-review digest required')


def validate_selected_receipt(receipt):
    """Validate receipt content locally; SQL binds it to actual C1/current rows."""
    _object(receipt,RECEIPT_KEYS)
    _hash(receipt['review_scope_id'])
    if (receipt['receipt_format'] != 'selected-release-review-v1'
            or receipt['supported_scope'] != 'undergraduate_academic_affairs'):
        raise ValueError('Undergraduate selected review required')
    decision = receipt['decision']; _object(decision,DECISION_KEYS)
    for value in decision.values(): _text(value)
    for name in ('acceptance_record_sha256','coverage_inventory_sha256','draft_chunks_sha256'):
        _hash(decision[name])
    if parse_timestamp(decision['recorded_at']) is None:
        raise ValueError('Real review recording time required')
    path = decision['decision_document']
    if ('\\' in path or ':' in path or PurePosixPath(path).is_absolute()
            or any(p in ('','.','..') for p in path.split('/'))):
        raise ValueError('Repository-relative decision path required')
    sources, chunks = receipt['sources'], receipt['chunks']
    if not isinstance(sources,list) or not sources or not isinstance(chunks,list) or not chunks:
        raise ValueError('Nonempty selected source/chunk coverage required')
    versions = {}
    for source in sources:
        _object(source,{'version_id','source_sha256','partial_review_evidence_id'})
        _text(source['version_id']); _hash(source['source_sha256']); _text(source['partial_review_evidence_id'])
        if not re.fullmatch('ver-[A-Za-z0-9_.:-]+', source['version_id']) or source['version_id'] in versions:
            raise ValueError('Distinct selected source version required')
        versions[source['version_id']] = source['source_sha256']
    if list(versions) != sorted(versions): raise ValueError('Sorted selected sources required')
    ids, used_sources, neighbors, groups = {}, set(), [], {}
    for chunk in chunks:
        _object(chunk,{'chunk_id','content_hash','type_fields','spans'})
        _hash(chunk['chunk_id']); _hash(chunk['content_hash'])
        if chunk['chunk_id'] in ids: raise ValueError('Distinct selected chunk required')
        spans = chunk['spans']
        if not isinstance(spans,list) or not spans: raise ValueError('Complete selected spans required')
        version = spans[0].get('version_id') if isinstance(spans[0],dict) else None
        if version not in versions: raise ValueError('Selected chunk source is not declared')
        for i,span in enumerate(spans):
            _object(span,SPAN_KEYS)
            if (span['chunk_id'] != chunk['chunk_id'] or type(span['span_order']) is not int
                    or span['span_order'] != i or span['version_id'] != version
                    or span['byte_sha256'] != versions[version]):
                raise ValueError('Exact ordered selected source spans required')
        fields = chunk['type_fields']
        if not isinstance(fields,dict): raise ValueError('Selected field metadata required')
        _text(fields.get('applicability_basis_ref'))
        if any(f.get('field_kind') not in (None,'arrows') or 'field_state' in f
                for f in fields.get('field_associations',[]) if isinstance(f,dict)):
            raise ValueError('Selected codec supports located scalar/arrow fields only')
        required = fields.get('required_neighbor_chunk_ids')
        if not isinstance(required,list) or len(set(required)) != len(required):
            raise ValueError('Distinct selected neighbors required')
        for neighbor in required:
            _hash(neighbor); neighbors.append((neighbor,version))
        # The C1 projection contains stored spans, not the complete Chunk contract.
        # Use the codec's stored-row path, which parses every SourceSpan itself.
        stored = dict(chunk_id=chunk['chunk_id'], byte_sha256=versions[version], version_id=version,
            chunker_version=context_chunker_version(fields.get('context_format')),
            source_text=' '.join(s['text'] for s in spans),
            text=serialize_reviewed_fields(fields['field_associations'], fields['source_limits'],
                fields.get('service_group'), context_format=fields['context_format']),
            content_hash=chunk['content_hash'],type_fields=fields)
        render_reviewed_policy_context(stored,spans)
        group = fields.get('service_group')
        if group is not None:
            groups.setdefault((version,group['logical_step_id']),[]).append({'chunk':stored,'spans':spans})
        ids[chunk['chunk_id']] = version; used_sources.add(version)
    if list(ids) != sorted(ids) or used_sources != set(versions):
        raise ValueError('Sorted exact source/chunk coverage required')
    if any(ids.get(neighbor) != version for neighbor,version in neighbors):
        raise ValueError('Complete same-source selected neighbors required')
    for members in groups.values():
        metas = [r['chunk']['type_fields']['service_group'] for r in members]
        count = metas[0]['part_count']
        if (type(count) is not int or count != len(members)
                or any(type(m['part_order']) is not int or m['part_count'] != count for m in metas)
                or sorted(m['part_order'] for m in metas) != list(range(count))):
            raise ValueError('Complete selected service group required')
        if any('record_manifest' in meta for meta in metas): validate_record_group(members)
        for row in members:
            for field in row['chunk']['type_fields']['field_associations']:
                if field.get('field_kind') == 'arrows':
                    others = [r for r in members if r is not row]
                    mapping = list(field['node_reading_ids'].values())
                    if (row['chunk']['type_fields']['service_group']['part_order'] != 0
                            or sorted(mapping) != sorted(r['chunk']['type_fields']['reading_id'] for r in others)
                            or any(r['chunk']['type_fields']['service_group'].get('part_reading_id')
                                != r['chunk']['type_fields']['reading_id'] for r in members)
                            or len({s['page'] for r in members for s in r['spans']}) != 1):
                        raise ValueError('Complete same-page selected flowchart required')
    json.dumps(receipt, allow_nan=False)


class SelectedReleaseReviewLoader:
    def __init__(self,client=None):
        self.client = client or SupabaseStorageClient()

    def record(self,receipt):
        receipt = copy.deepcopy(receipt)
        try:
            validate_selected_receipt(receipt)
        except (KeyError,TypeError,IndexError,OverflowError) as exc:
            raise ValueError('Invalid selected-review receipt') from exc
        stored = self.client.rpc('record_selected_release_review',{'p_receipt':receipt},role='admin')
        if stored != receipt: raise ValueError('Stored selected review differs')
        return stored

    def bind_release(self,release_id,review_scope_id):
        _text(release_id); _hash(review_scope_id)
        expected = dict(release_id=release_id,review_scope_id=review_scope_id)
        stored = self.client.rpc('bind_selected_release_review',dict(
            p_release_id=release_id,p_review_scope_id=review_scope_id),role='admin')
        if stored != expected: raise ValueError('Stored selected release binding differs')
        return stored
