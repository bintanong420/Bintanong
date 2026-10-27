"""Bind explicit flow annotations to existing reviewed scalar readings/events."""
from __future__ import annotations

from collections.abc import Mapping
import copy

from ...bintanong_contracts.reviewed_flow_evidence import (
    flow_digest,validate_flow_manifest,validate_flow_group,
)


def bind_flow_manifests(bindings,rows,anchors,events,event_bytes):
    if not isinstance(bindings,Mapping):raise ValueError('flow bindings must map logical groups')
    result={}
    for identity,supplied in bindings.items():
        manifest=copy.deepcopy(supplied)
        validate_flow_manifest(manifest)
        if identity!=manifest['logical_step_id']:raise ValueError('flow binding identity differs')
        event=events.get(manifest['review_event_sha256'],{})
        payload={k:v for k,v in manifest.items() if k not in ('review_event_sha256','review_event_json')}
        if (event.get('source_sha256')!=manifest['source_sha256']
                or event.get('flow_evidence_sha256')!=flow_digest(payload)):
            raise ValueError('flow annotation review event differs')
        manifest['review_event_json']=event_bytes[manifest['review_event_sha256']].decode('utf8')
        parts=sorted((r for r in rows.values() if r.get('original_reading_id')==identity),
            key=lambda r:r['part_order'])
        if not parts:raise ValueError('known complete flow readings required')
        members=[]
        for order,row in enumerate(parts):
            if row['part_order']!=order:raise ValueError('complete ordered flow readings required')
            spans=[];fields=[]
            for field in row['fields']:
                if field['decision'] not in ('accepted','corrected'):
                    raise ValueError('confirmed flow scalar readings required')
                located=anchors.get(row['reading_id'],{}).get(field['name'],[])
                fields.append({'name':field['name'],'value':field['reviewed_value'],
                    'source_blank':field['source_blank'],'span_indexes':list(range(len(spans),len(spans)+len(located)))})
                spans.extend(located)
            chunk={'byte_sha256':row['source_sha256'],'version_id':row['version_id'],
                'type_fields':{'reading_id':row['reading_id'],'field_associations':fields,'source_limits':row['gaps'],
                    'service_group':{'logical_step_id':identity,'part_order':order,'part_count':len(parts),
                        'part_reading_id':row['reading_id'],'flow_manifest':manifest}}}
            members.append({'chunk':chunk,'spans':spans})
        validate_flow_group(members);result[identity]=manifest
    return result
