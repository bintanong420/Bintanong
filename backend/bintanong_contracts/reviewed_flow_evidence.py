"""Checked visible flow geometry; source completeness remains an explicit limit."""
from __future__ import annotations

import hashlib
import json
import math
import re

from .source import SourceSpan


def flow_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
        allow_nan=False,separators=(',',':')).encode()).hexdigest()


def _sha(value):
    if not isinstance(value,str) or not re.fullmatch(r'[0-9a-f]{64}',value):
        raise ValueError('flow evidence digest required')


def _numbers(value,count):
    if (not isinstance(value,list) or len(value)!=count
            or any(type(n) not in (int,float) or not math.isfinite(n) for n in value)):
        raise ValueError('finite flow geometry required')
    return value


def _region(value,image):
    l,t,r,b=_numbers(value,4)
    if not 0<=l<r<=image['image_size'][0] or not 0<=t<b<=image['image_size'][1]:
        raise ValueError('flow region outside original image')


def validate_flow_manifest(manifest):
    """Validate the explicit annotation structure, without inferring any route."""
    try:
        if (not isinstance(manifest,dict) or manifest['schema_version']!='bintanong-flow-evidence-v1'
                or not isinstance(manifest['logical_step_id'],str) or not manifest['logical_step_id']
                or not isinstance(manifest['version_id'],str) or not manifest['version_id']
                or type(manifest['physical_page']) is not int or manifest['physical_page']<1
                or type(manifest['source_complete']) is not bool):
            raise ValueError('invalid flow identity')
        for key in ('source_sha256','limits_sha256','review_event_sha256'):_sha(manifest[key])
        image=manifest['image'];_sha(image['image_sha256'])
        size=_numbers(image['page_size'],2);pixels=image['image_size'];scale=image['scale']
        if (min(size)<=0 or not isinstance(pixels,list) or len(pixels)!=2
                or any(type(n) is not int or n<1 for n in pixels)
                or type(scale) not in (int,float) or not math.isfinite(scale) or scale<=0
                or pixels!=[math.ceil(n*scale) for n in size]
                or type(image['rotation']) is not int or image['rotation']!=0 or image['crop'] is not None):
            raise ValueError('original flow image transform required')
        fields=manifest['field_bindings'];nodes=manifest['nodes'];labels=manifest['labels']
        if (not isinstance(fields,dict) or not fields or any(not isinstance(k,str) or not k for k in fields)
                or not isinstance(nodes,list) or not nodes or not isinstance(labels,dict)
                or any(k not in fields or not isinstance(v,str) or not v.strip() for k,v in labels.items())):
            raise ValueError('bound flow fields required')
        for value in fields.values():_sha(value)
        by_id={};node_fields=set()
        for node in nodes:
            identity=node['id'];field=node['field'];kind=node['kind']
            if (not isinstance(identity,str) or not identity or identity in by_id
                    or not isinstance(field,str) or field not in fields or field in node_fields
                    or kind not in ('start','process','decision','terminal')
                    or (identity=='START')!=(kind=='start') or (identity=='END')!=(kind=='terminal')):
                raise ValueError('distinct bound flow nodes required')
            _region(node['region'],image);by_id[identity]=node;node_fields.add(field)
        if 'START' not in by_id:raise ValueError('visible START required')
        edges=manifest['edges'];unknown=manifest['unresolved_outgoing']
        if not isinstance(edges,list) or not isinstance(unknown,list):raise ValueError('flow connectors required')
        seen=set();outgoing=set();used_labels=set()
        for edge in edges+unknown:
            origin=edge['from'];_region(edge['region'],image)
            route=edge['route']
            if (not isinstance(route,list) or len(route)<2 or origin not in by_id or origin=='END'):
                raise ValueError('flow origin or route unresolved')
            l,t,r,b=edge['region']
            for point in route:
                x,y=_numbers(point,2)
                if not l<=x<=r or not t<=y<=b:raise ValueError('connector route outside its region')
            def near(point,node):
                x,y=point;a,c,d,e=node['region']
                return a-12<=x<=d+12 and c-12<=y<=e+12
            if not near(route[0],by_id[origin]):raise ValueError('connector misses origin node')
            outgoing.add(origin)
            if edge in unknown:
                if 'to' in edge or 'label' in edge:raise ValueError('unknown connector cannot invent endpoint/label')
                continue
            target=edge['to'];label=edge['label']
            if target not in by_id or target=='START' or not near(route[-1],by_id[target]):
                raise ValueError('connector misses destination node')
            key=(origin,label,target)
            if key in seen:raise ValueError('duplicate flow connector')
            seen.add(key)
            if label is not None:
                if not isinstance(label,str) or label not in labels:raise ValueError('printed flow label required')
                _region(edge['label_region'],image);used_labels.add(label)
            elif 'label_region' in edge:raise ValueError('unlabelled connector has no printed label region')
        if (set(labels)!=used_labels or set(by_id)-{'END'}!=outgoing
                or ('END' not in by_id and not unknown)):
            raise ValueError('incomplete visible connector inventory')
        reached={'START'}
        while True:
            expanded=reached|{e['to'] for e in edges if e['from'] in reached}
            if expanded==reached:break
            reached=expanded
        if reached!=set(by_id):raise ValueError('unreachable flow node')
        return manifest
    except (KeyError,TypeError,IndexError,ValueError,OverflowError) as exc:
        raise ValueError('invalid reviewed flow evidence') from exc


def _span(raw):
    # Stored RPC spans include database-only IDs/order; hash the source contract.
    if isinstance(raw,SourceSpan):return raw
    if not isinstance(raw,dict):raise ValueError('source span record required')
    return SourceSpan.parse({**{k:v for k,v in raw.items() if k in SourceSpan.model_fields},
        'schema_version':SourceSpan.SCHEMA_VERSION})


def flow_field_digest(field,spans):
    return flow_digest({'value':field['value'],'source_blank':field['source_blank'],
        'spans':[_span(spans[i]).model_dump(mode='json') for i in field['span_indexes']]})


def _pixel_box(span,image):
    l,t,r,b=span.bbox
    if span.bbox_origin=='BOTTOMLEFT':t,b=span.page_size[1]-t,span.page_size[1]-b
    elif span.bbox_origin!='TOPLEFT':raise ValueError('explicit flow citation origin required')
    return [n*image['scale'] for n in (l,t,r,b)]


def validate_flow_member(manifest,chunk,spans):
    """Check every local scalar against the immutable full-group field inventory."""
    validate_flow_manifest(manifest)
    receipt=manifest.get('review_event_json')
    if (not isinstance(receipt,str) or hashlib.sha256(receipt.encode('utf8')).hexdigest()!=manifest['review_event_sha256']):
        raise ValueError('original flow review receipt required')
    event=json.loads(receipt)
    if (not isinstance(event,dict) or event.get('source_sha256')!=manifest['source_sha256']
            or event.get('flow_evidence_sha256')!=flow_digest({k:v for k,v in manifest.items()
                if k not in ('review_event_sha256','review_event_json')})):
        raise ValueError('flow annotation differs from its review receipt')
    if (chunk['byte_sha256']!=manifest['source_sha256'] or chunk['version_id']!=manifest['version_id']
            or chunk['type_fields']['service_group']['logical_step_id']!=manifest['logical_step_id']):
        raise ValueError('flow source/group differs')
    associations=chunk['type_fields']['field_associations']
    if not isinstance(associations,list) or not associations or any(not isinstance(f,dict) for f in associations):
        raise ValueError('flow scalar associations required')
    for field in associations:
        if (field.get('field_kind') is not None or field['name'] not in manifest['field_bindings']
                or flow_field_digest(field,spans)!=manifest['field_bindings'][field['name']]):
            raise ValueError('flow scalar or original spans differ')
        for index in field['span_indexes']:
            span=_span(spans[index])
            if (span.page!=manifest['physical_page'] or list(span.page_size or ())!=manifest['image']['page_size']
                    or span.extraction.source_kind!='original_pdf_image' or not span.is_complete
                    or span.bbox is None or span.byte_sha256!=manifest['source_sha256']
                    or span.version_id!=manifest['version_id']):
                raise ValueError('flow scalar original page differs')


def validate_flow_group(members):
    """A partial/mutated group never supplies usable topology or scalar evidence."""
    try:
        ordered=sorted(members,key=lambda r:r['chunk']['type_fields']['service_group']['part_order'])
        manifest=ordered[0]['chunk']['type_fields']['service_group']['flow_manifest']
        fields={};limits=[]
        for order,row in enumerate(ordered):
            chunk=row['chunk'];meta=chunk['type_fields']['service_group']
            if (meta.get('flow_manifest')!=manifest or meta['part_order']!=order
                    or meta['part_count']!=len(ordered) or meta.get('part_reading_id')!=chunk['type_fields']['reading_id']):
                raise ValueError('complete identical flow manifests required')
            validate_flow_member(manifest,chunk,row['spans'])
            for field in chunk['type_fields']['field_associations']:
                if field['name'] in fields:raise ValueError('duplicate flow scalar')
                fields[field['name']]=(field,row['spans'])
            local_limits=chunk['type_fields']['source_limits']
            if not isinstance(local_limits,list) or any(not isinstance(g,dict) for g in local_limits):
                raise ValueError('flow source limits required')
            limits.extend({k:v for k,v in gap.items() if k not in
                ('source_sha256','version_id','span_indexes','resolution','message')}
                for gap in local_limits)
        if set(fields)!=set(manifest['field_bindings']) or flow_digest(limits)!=manifest['limits_sha256']:
            raise ValueError('complete original flow fields/limits required')
        complete=not limits and not manifest['unresolved_outgoing'] and any(n['id']=='END' for n in manifest['nodes'])
        if manifest['source_complete']!=complete:raise ValueError('flow source completeness differs')
        image=manifest['image']
        for node in manifest['nodes']:
            field,spans=fields[node['field']]
            if field['source_blank'] or not field['span_indexes']:raise ValueError('located flow node required')
            located=[_span(spans[i]) for i in field['span_indexes']]
            if node['id'] in ('START','END') and field['value']!=node['id']:
                raise ValueError('literal visible flow marker required')
            boxes=[_pixel_box(s,image) for s in located]
            box=[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]
            l,t,r,b=node['region']
            # A cited label region need not include the surrounding box/diamond
            # border. Its node centre must still lie in that scalar's region.
            x,y=(l+r)/2,(t+b)/2
            if not box[0]-0.001<=x<=box[2]+0.001 or not box[1]-0.001<=y<=box[3]+0.001:
                raise ValueError('flow node is not aligned with its cited scalar region')
        for edge in manifest['edges']:
            if edge['label'] is None:continue
            field,spans=fields[edge['label']]
            if (field['value']!=manifest['labels'][edge['label']] or len(field['span_indexes'])!=1
                    or any(abs(a-b)>0.001 for a,b in zip(edge['label_region'],
                        _pixel_box(_span(spans[field['span_indexes'][0]]),image)))):
                raise ValueError('flow branch label differs from cited print')
    except (KeyError,TypeError,IndexError,ValueError,OverflowError) as exc:
        raise ValueError('invalid reviewed context record') from exc


def flow_display(manifest,associations):
    """Small local-node projection; original geometry stays hash-bound metadata."""
    names={f['name'] for f in associations};nodes=[]
    for node in manifest['nodes']:
        if node['field'] not in names:continue
        nodes.append({'id':node['id'],'kind':node['kind'],'field':node['field'],
            'outgoing':[{'to':edge['to'],'label':manifest['labels'][edge['label']] if edge['label'] is not None else None}
                for edge in manifest['edges'] if edge['from']==node['id']],
            'outgoing_unresolved':any(e['from']==node['id'] for e in manifest['unresolved_outgoing'])})
    return {'source_complete':manifest['source_complete'],'nodes':nodes,
        'value_origin':'reviewed_visible_flow_geometry',
        'limitation':'Visible source structure only; missing conditions or endpoints must not be inferred.'}
