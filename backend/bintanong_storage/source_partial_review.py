"""Persist C1 selected-field coverage without complete review or authority."""
import copy
import json
import re

from backend.bintanong_contracts.base import parse_timestamp
from backend.bintanong_contracts.governance import Evidence, SourceDocumentVersion, evidence_authorizes
from backend.bintanong_contracts.source import SpanLocator
from .client import SupabaseStorageClient


_RECEIPT = {'receipt_format','version_id','source_sha256','acquisition_locators','evidence',
    'reviewer_label','compiler_label','review_scope','source_events','chunks'}
_EVENT = {'event_sha256','representation','source_sha256','owner_event_sha256',
    'actual_owner_label','recorded_at','timestamp_meaning'}
_SPAN = {'chunk_id','span_order','version_id','byte_sha256','page','printed_page_label',
    'locator','text','bbox','bbox_origin','page_size','extraction'}


def _object(value, keys):
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError('Closed partial-review object required')


def _text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Nonblank partial-review label required')


def _hash(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Exact partial-review digest required')


def _list(value):
    if not isinstance(value, list) or not value:
        raise ValueError('Nonempty partial-review list required')


def _validate_receipt(current, receipt):
    _object(receipt, _RECEIPT)
    if (receipt['receipt_format'] != 'selected-source-partial-review-v1'
            or receipt['review_scope'] != 'selected_fields'
            or receipt['version_id'] != current['version_id']
            or receipt['source_sha256'] != current['byte_sha256']
            or receipt['acquisition_locators'] != current['acquisition_locators']):
        raise ValueError('Exact selected-field source binding required')
    for key in ('reviewer_label','compiler_label'):
        _text(receipt[key])
    evidence = Evidence.model_validate(receipt['evidence'])
    if (not evidence.evidence_id.strip()
            or not evidence_authorizes('content_review_state','partially_reviewed',evidence,'pending')
            or any(e['evidence_id'] == evidence.evidence_id for e in current['evidence'])):
        raise ValueError('Distinct C1 reviewer evidence required')
    at = parse_timestamp(evidence.recorded_at)
    _list(receipt['source_events'])
    events = {}
    for event in receipt['source_events']:
        _object(event, _EVENT)
        for key in ('event_sha256','owner_event_sha256'):
            _hash(event[key])
        for key in ('actual_owner_label','timestamp_meaning'):
            _text(event[key])
        when = parse_timestamp(event['recorded_at']) if isinstance(event['recorded_at'],str) else None
        if (event['event_sha256'] in events or event['source_sha256'] != current['byte_sha256']
                or event['representation'] not in ('original_file_bytes','existing_indent2_encoded_event_object')
                or when is None or when > at):
            raise ValueError('Distinct source-bound original review event required')
        events[event['event_sha256']] = event
    if receipt['reviewer_label'] not in {e['actual_owner_label'] for e in events.values()}:
        raise ValueError('Reviewer label must retain an actual bound event label')
    _list(receipt['chunks'])
    ids, used_events, neighbors = set(), set(), set()
    for chunk in receipt['chunks']:
        _object(chunk, {'chunk_id','content_hash','type_fields','spans'})
        for key in ('chunk_id','content_hash'):
            _hash(chunk[key])
        if chunk['chunk_id'] in ids:
            raise ValueError('Duplicate selected chunk')
        ids.add(chunk['chunk_id'])
        fields = chunk['type_fields']
        if (not isinstance(fields,dict) or not {'reading_id','field_associations','source_limits',
                'required_neighbor_chunk_ids','applicability_basis_ref','context_format'} <= set(fields)
                or not isinstance(fields['source_limits'],list)
                or not isinstance(fields['required_neighbor_chunk_ids'],list)):
            raise ValueError('Complete reviewed field metadata required')
        _text(fields['reading_id']); _text(fields['context_format'])
        for neighbor in fields['required_neighbor_chunk_ids']:
            _hash(neighbor)
            neighbors.add(neighbor)
        if len(set(fields['required_neighbor_chunk_ids'])) != len(fields['required_neighbor_chunk_ids']):
            raise ValueError('Duplicate required neighbor')
        _list(chunk['spans'])
        for i, span in enumerate(chunk['spans']):
            _object(span, _SPAN)
            if (span['chunk_id'] != chunk['chunk_id'] or type(span['span_order']) is not int
                    or span['span_order'] != i or span['version_id'] != current['version_id']
                    or span['byte_sha256'] != current['byte_sha256']
                    or type(span['page']) is not int or span['page'] < 1
                    or not isinstance(span['locator'],dict) or not isinstance(span['extraction'],dict)
                    or (span['text'] is not None and not isinstance(span['text'],str))):
                raise ValueError('Ordered source-bound span projection required')
            SpanLocator.parse({'table_index':None,'cell_ids':[],'item_ids':[],'ref':None,
                'section_path':[],**span['locator']})
        _list(fields['field_associations'])
        names = set()
        for field in fields['field_associations']:
            if not isinstance(field,dict) or not {'name','value','source_blank','event_sha256','span_indexes'} <= set(field):
                raise ValueError('Complete selected field association required')
            _text(field['name'])
            indexes = field['span_indexes']
            if (field['name'] in names or type(field['source_blank']) is not bool
                    or not isinstance(field['event_sha256'],str) or field['event_sha256'] not in events
                    or not isinstance(indexes,list) or not indexes
                    or any(type(i) is not int or i < 0 or i >= len(chunk['spans']) for i in indexes)
                    or len(set(indexes)) != len(indexes)):
                raise ValueError('Distinct field/event/span binding required')
            names.add(field['name']); used_events.add(field['event_sha256'])
    if not neighbors <= ids or used_events != set(events):
        raise ValueError('Complete same-source neighbor and event coverage required')
    return evidence


class SourcePartialReviewLoader:
    def __init__(self, client=None):
        self.client = client or SupabaseStorageClient()

    def record(self, current, receipt):
        current = SourceDocumentVersion.parse(current.model_dump(mode='json')
            if isinstance(current,SourceDocumentVersion) else current).model_dump(mode='json')
        if (any(current[k]['state'] != state for k,state in dict(acquisition_state='observed',
                verification_state='pending',approval_state='not_requested',content_review_state='pending').items())
                or current['approval_id'] is not None):
            raise ValueError('C1 requires acquired bytes and initial review/authority states')
        receipt = copy.deepcopy(receipt)
        evidence = _validate_receipt(current,receipt)
        try:
            json.dumps(receipt,allow_nan=False)
        except (TypeError,ValueError) as exc:
            raise ValueError('JSON partial-review receipt required') from exc
        proposed = copy.deepcopy(current)
        proposed['evidence'].append(evidence.model_dump(mode='json'))
        proposed['content_review_state'] = dict(state='partially_reviewed',evidence_ref=evidence.evidence_id)
        expected = SourceDocumentVersion.parse(proposed)
        result = self.client.rpc('record_source_partial_review',dict(
            p_expected_register=current,p_receipt=receipt),role='admin')
        stored = SourceDocumentVersion.parse(result)
        if stored != expected:
            raise ValueError('Stored partial review differs from the expected record')
        return stored
