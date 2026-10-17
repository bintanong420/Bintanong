"""Bound scalar policy fields and unresolved limits for offline cited context.

This codec carries evidence limitations, never source authority or policy decisions.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re

from .source import Chunk, SourceSpan, canonical_text, compute_content_hash, joined_span_text, span_identity
from .reviewed_record_groups import validate_record_manifest
from .reviewed_heading_metadata import validate_reviewed_heading_metadata, heading_metadata_display


CONTEXT_FORMAT = 'reviewed-policy-fields-v1'
CONTEXT_CHUNKER_VERSION = 'palsu-reviewed-policy-context-chunker-v1'
COMPACT_CONTEXT_FORMAT = 'reviewed-policy-fields-v2'
COMPACT_CONTEXT_CHUNKER_VERSION = 'palsu-reviewed-policy-context-chunker-v2'
_CONTEXT_VERSIONS = {CONTEXT_FORMAT: CONTEXT_CHUNKER_VERSION,
    COMPACT_CONTEXT_FORMAT: COMPACT_CONTEXT_CHUNKER_VERSION}
CONTEXT_CHUNKER_VERSIONS = frozenset(_CONTEXT_VERSIONS.values())
ISSUES = frozenset({'source_cutoff', 'malformed_source_condition',
    'conflicting_deadlines', 'printed_total_discrepancy', 'effectivity_currentness_unknown',
    'claim_not_stated'})


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def _message(issue, claims):
    return 'Unavailable information: '+', '.join(claims)+'. Source limitation remains unresolved ('+issue+').'


def context_chunker_version(context_format):
    if not isinstance(context_format,str) or context_format not in _CONTEXT_VERSIONS:
        raise ValueError('unsupported reviewed context format')
    return _CONTEXT_VERSIONS[context_format]


def make_source_limits(row, associations, spans):
    """Bind exact recorded gaps to their complete located scalar fields."""
    fields = {f['name']: f for f in associations}
    limits, seen = [], set()
    for gap in row['gaps']:
        names = gap['field_names']
        visible = gap['visible_text']
        values = [visible] if isinstance(visible, str) else visible
        cover=(isinstance(names,list) and len(names)==1 and isinstance(names[0],str)
            and names[0] in fields and fields[names[0]].get('field_kind')=='cover_labels')
        if cover:
            if (not isinstance(visible,list) or not visible
                    or any(not isinstance(v,str) or not v.strip() for v in visible)
                    or visible!=fields[names[0]]['value']):
                raise ValueError('cover limitation differs from complete label list')
            values=['\n'.join(visible)]
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
                or any(canonical_text(v) not in canonical_text('\n'.join(fields[n]['value']) if cover else fields[n]['value'])
                       for n, v in zip(names, values))):
            raise ValueError('source limitation differs from located visible fields')
        seen.add(gap['gap_id'])
        limits.append({**copy.deepcopy(gap), 'source_sha256':row['source_sha256'],
            'version_id':row['version_id'], 'span_indexes':indexes,
            'resolution':'unresolved', 'message':_message(gap['issue'],gap['affected_claims'])})
    return limits


def serialize_reviewed_fields(associations, limits, group=None, *, context_format=CONTEXT_FORMAT):
    context_chunker_version(context_format)
    compact = context_format == COMPACT_CONTEXT_FORMAT
    fields=[]
    for f in associations:
        display={k:f[k] for k in ('name','value','source_blank')}
        if 'field_kind' in f:
            display['field_kind']=f['field_kind']
            if f['field_kind']=='heading_metadata':display.update(heading_metadata_display(f))
            if f['field_kind']=='arrows':display['node_reading_ids']=f.get('node_reading_ids')
            if f['field_kind']=='body_partition':
                display.update(raw_text=f['raw_text'],raw_item_ref=f['raw_item_ref'],
                    field_role='extraction_metadata',
                    limitation='Page furniture is extraction metadata, not programme content or policy evidence.')
        if 'field_state' in f:
            display.update(field_state=f['field_state'],
                limitation='Additional conditions are not separately recorded; their absence is not established.')
        fields.append(display)
    record_group=isinstance(group,dict) and 'record_manifest' in group
    displayed_limits=[{k:v for k,v in limit.items() if k not in
        {'visible_text','source_sha256','version_id','span_indexes'}} for limit in limits] if compact or record_group else limits
    payload={'fields':fields,'source_limits':displayed_limits}
    if group is not None:
        if (not isinstance(group,dict) or set(group) not in (
                {'logical_step_id','part_order','part_count'},
                {'logical_step_id','part_order','part_count','part_reading_id'},
                {'logical_step_id','part_order','part_count','part_reading_id','record_manifest'})
                or not isinstance(group['logical_step_id'],str) or not group['logical_step_id']
                or ('part_reading_id' in group and (not isinstance(group['part_reading_id'],str)
                    or not group['part_reading_id'].strip()))
                or type(group['part_order']) is not int or type(group['part_count']) is not int
                or not 0 <= group['part_order'] < group['part_count']):
            raise ValueError('invalid service context group')
        if record_group:validate_record_manifest(group['record_manifest'],group['part_count'])
        payload['service_group']={k:v for k,v in group.items() if k!='record_manifest'} if compact else group
    if compact and (limits or group is not None):
        payload['evidence_sha256']=hashlib.sha256(_json({
            'source_limits':limits,'service_group':group}).encode('utf-8')).hexdigest()
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


def validate_reviewed_cover_labels(field, spans):
    labels,refs=field.get('value'),field.get('span_indexes')
    if (field.get('name')!='cover_labels' or field.get('source_blank') is not False
            or not isinstance(labels,list) or not labels
            or any(not isinstance(s,str) or not s.strip() for s in labels)
            or not isinstance(refs,list) or len(labels)!=len(refs)
            or any(type(i) is not int or not 0<=i<len(spans) for i in refs)
            or [spans[i].text for i in refs]!=labels or len({spans[i].page for i in refs})!=1):
        raise ValueError('complete ordered cover labels required')


def validate_reviewed_body_partition(field, associations, spans):
    """Bind complete extraction metadata to body-only original-image citations."""
    bodies=[f for f in associations if f['name']=='body']
    segments,raw,ref=(field.get(k) for k in ('value','raw_text','raw_item_ref'))
    if (field['name']!='segmentation' or field['source_blank'] is not False
            or field['span_indexes']!=[] or len(bodies)!=1
            or not isinstance(segments,list) or not segments or not isinstance(raw,str)
            or not isinstance(ref,str) or not re.fullmatch(r'#/texts/\d+',ref)):
        raise ValueError('invalid body partition metadata')
    body=bodies[0]
    if (not isinstance(body['value'],str) or body['source_blank'] is not False
            or body.get('field_kind') is not None or body['event_sha256']!=field['event_sha256']):
        raise ValueError('unlinked body partition metadata')
    last=0;programme=[]
    for segment in segments:
        if (not isinstance(segment,dict) or segment.get('kind') not in ('programme_name','page_furniture')
                or not isinstance(segment.get('text'),str) or not segment['text'].strip()
                or not isinstance(segment.get('raw_provenance'),dict)):
            raise ValueError('invalid raw segment')
        prov=segment['raw_provenance'];ranges=prov.get('charspan');box=prov.get('bbox')
        if (type(prov.get('page_no')) is not int or prov['page_no']<1
                or not isinstance(ranges,list) or len(ranges)!=2 or any(type(n) is not int for n in ranges)
                or not last<=ranges[0]<ranges[1]<=len(raw) or raw[last:ranges[0]].strip()
                or canonical_text(raw[ranges[0]:ranges[1]])!=canonical_text(segment['text'])
                or not isinstance(box,dict) or box.get('coord_origin')!='BOTTOMLEFT'
                or any(type(box.get(k)) not in (int,float) or not math.isfinite(box[k]) for k in ('l','b','r','t'))
                or not 0<=box['l']<box['r'] or not 0<=box['b']<box['t']):
            raise ValueError('raw partition text or geometry differs')
        last=ranges[1]
        if segment['kind']=='programme_name':programme.append(segment)
    if (raw[last:].strip() or not programme or len(programme)!=len(body['span_indexes'])
            or canonical_text(' '.join(s['text'] for s in programme))!=canonical_text(body['value'])):
        raise ValueError('incomplete programme partition')
    for segment,index in zip(programme,body['span_indexes']):
        span=spans[index];prov=segment['raw_provenance'];box=prov['bbox'];height=span.page_size[1]
        expected=[box['l'],height-box['t'],box['r'],height-box['b']]
        if (span.page!=prov['page_no'] or span.bbox_origin!='TOPLEFT'
                or canonical_text(span.text)!=canonical_text(segment['text'])
                or any(not math.isclose(a,b,rel_tol=0,abs_tol=1e-6) for a,b in zip(span.bbox,expected))):
            raise ValueError('programme citation differs from raw partition')


def render_reviewed_policy_context(chunk, spans):
    """Validate the complete marked record before displaying its exact text.

    Reject partial span selections; associations and limitations travel atomically.
    Callers still enforce authorized release/scope and exact context token budget.
    """
    try:
        fields = chunk['type_fields']
        context_format = fields.get('context_format')
        if chunk.get('chunker_version') != context_chunker_version(context_format):
            raise ValueError('reviewed context version markers differ')
        group=fields.get('service_group')
        if isinstance(group,dict) and 'part_reading_id' in group and group['part_reading_id']!=fields.get('reading_id'):
            raise ValueError('displayed reading identity differs')
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
            kind=field.get('field_kind')
            structured=kind in ('arrows','body_partition','cover_labels','heading_metadata')
            if (not isinstance(name,str) or not name or name in names or (not isinstance(value,str) and not unrecorded and not structured)
                    or ('field_state' in field and not unrecorded)
                    or ('field_kind' in field and not structured) or ('node_reading_ids' in field and kind!='arrows')
                    or type(blank) is not bool or not isinstance(refs,list)
                    or any(type(i) is not int or not 0 <= i < len(bound) for i in refs)
                    or not re.fullmatch(r'[0-9a-f]{64}',field['event_sha256'])):
                raise ValueError('invalid reviewed context field association')
            names.add(name); indexes.extend(refs)
            if structured:
                if kind=='heading_metadata':
                    validate_reviewed_heading_metadata(field,associations,located)
                    continue
                if kind=='cover_labels':
                    validate_reviewed_cover_labels(field,located)
                    continue
                if kind=='body_partition':
                    validate_reviewed_body_partition(field,associations,located)
                    continue
                if not isinstance(group,dict) or group.get('part_reading_id')!=fields.get('reading_id'):
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
        if limits != regenerated or chunk['text'] != serialize_reviewed_fields(associations,limits,
                fields.get('service_group'),context_format=context_format):
            raise ValueError('reviewed context text or source limits differ')
        return chunk['text']
    except (KeyError,TypeError,IndexError,ValueError,OverflowError) as exc:
        raise ValueError('invalid reviewed context record') from exc
