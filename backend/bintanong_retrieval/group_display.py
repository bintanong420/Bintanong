"""Share display metadata of validated groups; original evidence stays intact."""
import hashlib
import json


def _json(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':'))


def _common(values):
    common=dict(values[0])
    for value in values[1:]:
        for key in list(common):
            if key not in value or _json(common[key])!=_json(value[key]):
                del common[key]
    return common


def prepare_group_display(items, reviewed_group_chunk_ids):
    """Pool only complete groups explicitly qualified by contract admission.

    Display integrity uses one digest of the original ordered member IDs/text.
    Original per-part digests remain in each returned evidence item's text.
    """
    grouped={}
    for item in items:
        if item['chunk_id'] not in reviewed_group_chunk_ids:
            continue
        payload=json.loads(item['text'])
        key=(payload['service_group']['logical_step_id'],item['version_id'],
             item['citations'][0]['byte_sha256'])
        grouped.setdefault(key,[]).append((item,payload))
    defaults,texts=[],{}
    for members in grouped.values():
        count=members[0][1]['service_group']['part_count']
        # Mixed legacy/marked evidence is not a fully reviewed display group.
        if len(members)<2 or len(members)!=count:
            continue
        shared_group=_common([payload['service_group'] for item,payload in members])
        shared_payload=_common([{'source_limits':payload['source_limits']} for item,payload in members])
        index=len(defaults)
        originals=[{'chunk_id':item['chunk_id'],'text':item['text']} for item,payload in members]
        defaults.append(dict(service_group=shared_group,payload_defaults=shared_payload,
            evidence_sha256=hashlib.sha256(_json(originals).encode('utf8')).hexdigest()))
        for item,payload in members:
            display={k:v for k,v in payload.items() if k not in shared_payload and k!='evidence_sha256'}
            display['service_group']={k:v for k,v in payload['service_group'].items() if k not in shared_group}
            display['group_index']=index
            texts[item['chunk_id']]=_json(display)
    return defaults,texts
