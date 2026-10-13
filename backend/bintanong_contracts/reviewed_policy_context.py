"""Bound scalar policy fields and unresolved limits for offline cited context.

This codec carries evidence limitations, never source authority or policy decisions.
"""
from __future__ import annotations

import copy
import json
import re

from .source import Chunk, SourceSpan, canonical_text, compute_content_hash, joined_span_text, span_identity


CONTEXT_FORMAT = 'reviewed-policy-fields-v1'
CONTEXT_CHUNKER_VERSION = 'palsu-reviewed-policy-context-chunker-v1'
ISSUES = frozenset({'source_cutoff', 'malformed_source_condition',
    'conflicting_deadlines', 'printed_total_discrepancy', 'effectivity_currentness_unknown'})


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def _message(issue, claims):
    return 'Unavailable information: '+', '.join(claims)+'. Source limitation remains unresolved ('+issue+').'


def make_source_limits(row, associations, spans):
    """Bind exact recorded gaps to their complete located scalar fields."""
    fields = {f['name']: f for f in associations}
    limits, seen = [], set()
    for gap in row['gaps']:
        names = gap['field_names']
        visible = gap['visible_text']
        values = [visible] if isinstance(visible, str) else visible
        claims, pages = gap['affected_claims'], gap['locator']['physical_pages']
        if (gap['issue'] not in ISSUES or not isinstance(gap['gap_id'],str) or not gap['gap_id'].strip()
                or gap['gap_id'] in seen or not isinstance(claims,list) or not claims
                or any(not isinstance(c,str) or not c.strip() for c in claims)
                or len(set(names)) != len(names) or not names or any(n not in fields for n in names)
                or not isinstance(values, list) or len(values) != len(names)
                or any(not isinstance(v, str) or not v.strip() for v in values)
                or not isinstance(pages,list) or not pages or len(set(pages)) != len(pages)
                or any(type(p) is not int or p < 1 for p in pages)
                or gap['locator']['field'] != ','.join(names)):
            raise ValueError('unsupported source limitation')
        indexes = [i for name in names for i in fields[name]['span_indexes']]
        if (not indexes or set(gap['locator']['physical_pages']) != {spans[i].page for i in indexes}
                or any(canonical_text(v) not in canonical_text(fields[n]['value'])
                       for n, v in zip(names, values))):
            raise ValueError('source limitation differs from located visible fields')
        seen.add(gap['gap_id'])
        limits.append({**copy.deepcopy(gap), 'source_sha256':row['source_sha256'],
            'version_id':row['version_id'], 'span_indexes':indexes,
            'resolution':'unresolved', 'message':_message(gap['issue'],gap['affected_claims'])})
    return limits


def serialize_reviewed_fields(associations, limits, group=None):
    fields=[]
    for f in associations:
        display={k:f[k] for k in ('name','value','source_blank')}
        if 'field_kind' in f:
            display.update(field_kind=f['field_kind'],node_reading_ids=f.get('node_reading_ids'))
        if 'field_state' in f:
            display.update(field_state=f['field_state'],
                limitation='Additional conditions are not separately recorded; their absence is not established.')
        fields.append(display)
    payload={'fields':fields,'source_limits':limits}
    if group is not None:
        if (not isinstance(group,dict) or set(group)!= {'logical_step_id','part_order','part_count'}
                or not isinstance(group['logical_step_id'],str) or not group['logical_step_id']
                or type(group['part_order']) is not int or type(group['part_count']) is not int
                or not 0 <= group['part_order'] < group['part_count']):
            raise ValueError('invalid service context group')
        payload['service_group']=group
    return _json(payload)


def validate_reviewed_arrows(field, spans):
    """Validate structural endpoint IDs against exact cited labels and END text."""
    nodes,value,refs=(field.get(k) for k in ('node_reading_ids','value','span_indexes'))
    if (field.get('field_kind')!='arrows' or field.get('name')!='arrows' or field.get('source_blank') is not False
            or not isinstance(nodes,dict) or not nodes or 'END' in nodes
            or any(not isinstance(k,str) or not k.strip() or not isinstance(v,str) or not v.strip() for k,v in nodes.items())
            or len(set(nodes.values()))!=len(nodes) or not isinstance(value,list) or not value
            or not isinstance(refs,list) or len(refs)!=len(value)+1
            or any(type(i) is not int or not 0<=i<len(spans) for i in refs)):
        raise ValueError('invalid reviewed arrow association')
    seen=set()
    for edge,index in zip(value,refs):
        if (not isinstance(edge,dict) or set(edge)!= {'from','label','to'}
                or any(not isinstance(v,str) or not v.strip() for v in edge.values())
                or edge['from'] not in nodes or edge['to'] not in set(nodes)|{'END'}
                or spans[index].text!=edge['label'] or tuple(edge[k] for k in ('from','label','to')) in seen):
            raise ValueError('invalid reviewed arrow endpoint/label')
        seen.add(tuple(edge[k] for k in ('from','label','to')))
    if (not any(e['to']=='END' for e in value) or spans[refs[-1]].text!='END'
            or len({spans[i].page for i in refs})!=1):
        raise ValueError('invalid reviewed arrow terminal/page')


def render_reviewed_policy_context(chunk, spans):
    """Validate the complete marked record before displaying its exact text.

    Reject partial span selections; associations and limitations travel atomically.
    Callers still enforce authorized release/scope and exact context token budget.
    """
    try:
        fields = chunk['type_fields']
        if fields.get('context_format') != CONTEXT_FORMAT:
            raise ValueError('unsupported reviewed context format')
        associations, limits = fields['field_associations'], fields['source_limits']
        if 'spans' in chunk:
            bound = Chunk.parse(chunk).model_dump(mode='json')['spans']
        else:
            # RPC returns stored chunk and span rows separately, with database
            # metadata instead of contract schema markers. Validate their order
            # and contract fields without treating stored authority as approval.
            keys=('byte_sha256','version_id','page','printed_page_label','locator','text',
                'bbox','bbox_origin','page_size','extraction')
            if (not isinstance(spans,list) or not spans
                    or any(s.get('chunk_id') != chunk['chunk_id'] or type(s.get('span_order')) is not int
                           or s['span_order'] != i for i,s in enumerate(spans))):
                raise ValueError('invalid stored source span order')
            bound=[SourceSpan.parse({'schema_version':SourceSpan.SCHEMA_VERSION,
                **{k:s[k] for k in keys}}).model_dump(mode='json') for s in spans]
        located=[SourceSpan.parse(b) for b in bound]
        if (any(not s.is_complete or s.byte_sha256 != chunk['byte_sha256']
                or s.version_id != chunk['version_id'] or s.bbox is None or s.page_size is None for s in located)
                or len({span_identity(s) for s in located}) != len(located)
                or canonical_text(chunk['source_text']) != joined_span_text(located)
                or chunk['content_hash'] != compute_content_hash(chunk['source_text'],chunk['text'])):
            raise ValueError('reviewed context source or content binding differs')
        if (not isinstance(spans, list) or len(spans) != len(bound)
                or any(any(s.get(k,SourceSpan.SCHEMA_VERSION if k=='schema_version' else None) != b[k]
                    for k in b) for s,b in zip(spans,bound))
                or not isinstance(associations,list) or not associations or not isinstance(limits,list)):
            raise ValueError('complete reviewed context spans required')
        indexes, names = [], set()
        for field in associations:
            name, value, blank, refs = (field[k] for k in ('name','value','source_blank','span_indexes'))
            unrecorded=(value is None and isinstance(name,str) and name.endswith('/condition_note')
                and field.get('field_state')=='not_recorded' and blank is False and refs==[])
            structured=field.get('field_kind')=='arrows'
            if (not isinstance(name,str) or not name or name in names or (not isinstance(value,str) and not unrecorded and not structured)
                    or ('field_state' in field and not unrecorded)
                    or ('field_kind' in field and not structured) or ('node_reading_ids' in field and not structured)
                    or type(blank) is not bool or not isinstance(refs,list)
                    or any(type(i) is not int or not 0 <= i < len(bound) for i in refs)
                    or not re.fullmatch(r'[0-9a-f]{64}',field['event_sha256'])):
                raise ValueError('invalid reviewed context field association')
            names.add(name); indexes.extend(refs)
            if structured:
                if fields.get('service_group') is None:
                    raise ValueError('complete flowchart group required')
                validate_reviewed_arrows(field,located)
                continue
            if unrecorded:
                continue
            if blank:
                if value != '' or refs:
                    raise ValueError('source blank differs from located fields')
            elif (not refs or canonical_text(' '.join(bound[i]['text'] for i in refs)) != canonical_text(value)):
                raise ValueError('reviewed context field differs from located text')
        if indexes != list(range(len(bound))):
            raise ValueError('complete ordered reviewed context fields required')
        # Reuse exact gap checks, including pages and visible field values. No
        # instruction/message supplied by a caller can replace the fixed limitation.
        row = {'source_sha256':chunk['byte_sha256'],'version_id':chunk['version_id'],
            'gaps':[{k:v for k,v in g.items() if k not in
                    {'source_sha256','version_id','span_indexes','resolution','message'}}
                    for g in limits]}
        regenerated = make_source_limits(row, associations, located)
        if limits != regenerated or chunk['text'] != serialize_reviewed_fields(associations,limits,fields.get('service_group')):
            raise ValueError('reviewed context text or source limits differ')
        return chunk['text']
    except (KeyError,TypeError,IndexError,ValueError) as exc:
        raise ValueError('invalid reviewed context record') from exc
