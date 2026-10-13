"""Complete field manifests and hash-checked reconstruction of original source gaps."""
from __future__ import annotations

import copy
import hashlib
import json
import re


LIMIT_DERIVED=frozenset({'source_sha256','version_id','span_indexes','resolution','message'})


def record_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False,
        separators=(',',':')).encode()).hexdigest()


def make_record_manifest(row, groups):
    gaps={}
    for gap in row['gaps']:
        if gap['gap_id'] in gaps:raise ValueError('duplicate original gap')
        gaps[gap['gap_id']]={'sha256':record_digest(gap),'field_names':copy.deepcopy(gap['field_names']),
            'locator':copy.deepcopy(gap['locator']),
            'visible_text_kind':'list' if isinstance(gap['visible_text'],list) else 'string'}
    manifest={'parts':copy.deepcopy(groups),'gaps':gaps}
    validate_record_manifest(manifest,len(groups))
    return manifest


def validate_record_manifest(manifest, count):
    if not isinstance(manifest,dict) or set(manifest)!= {'parts','gaps'}:
        raise ValueError('invalid record manifest')
    parts,gaps=manifest['parts'],manifest['gaps']
    if (type(count) is not int or not isinstance(parts,list) or len(parts)!=count or not parts
            or any(not isinstance(p,list) or not p or any(not isinstance(n,str) or not n.strip() for n in p) for p in parts)
            or not isinstance(gaps,dict)):
        raise ValueError('invalid record field parts')
    names=[n for part in parts for n in part]
    if len(set(names))!=len(names):raise ValueError('duplicate record field')
    for identity,origin in gaps.items():
        if (not isinstance(identity,str) or not identity.strip() or not isinstance(origin,dict)
                or set(origin)!= {'sha256','field_names','locator','visible_text_kind'}
                or not isinstance(origin['sha256'],str) or not re.fullmatch(r'[0-9a-f]{64}',origin['sha256'])
                or not isinstance(origin['field_names'],list) or not origin['field_names']
                or any(not isinstance(n,str) or n not in names for n in origin['field_names'])
                or len(set(origin['field_names']))!=len(origin['field_names'])
                or origin['visible_text_kind'] not in ('list','string')
                or not isinstance(origin['locator'],dict)
                or origin['locator'].get('field')!=','.join(origin['field_names'])
                or not isinstance(origin['locator'].get('physical_pages'),list)
                or not origin['locator']['physical_pages']
                or any(type(p) is not int or p<1 for p in origin['locator']['physical_pages'])
                or len(set(origin['locator']['physical_pages']))!=len(origin['locator']['physical_pages'])
                or (origin['visible_text_kind']=='string' and len(origin['field_names'])!=1)):
            raise ValueError('invalid original gap declaration')


def project_record_gaps(row, names, anchors):
    result=[]
    for gap in row['gaps']:
        original=gap['field_names'];values=gap['visible_text']
        visible=values if isinstance(values,list) else [values]
        if len(visible)!=len(original):raise ValueError('complete original visible fields required')
        selected=[n for n in original if n in names]
        if not selected:continue
        projected=copy.deepcopy(gap);projected['field_names']=selected
        projected['visible_text']=[visible[original.index(n)] for n in selected] if isinstance(values,list) else values
        pages={s['page'] for n in selected for s in anchors[n]}
        projected['locator'].update(field=','.join(selected),
            physical_pages=[p for p in gap['locator']['physical_pages'] if p in pages])
        if set(projected['locator']['physical_pages'])!=pages or not pages:
            raise ValueError('projected gap source pages differ')
        result.append(projected)
    return result


def validate_record_group(members):
    """Reject incomplete field/limit groups before any part enters cited context."""
    try:
        ordered=sorted(members,key=lambda r:r['chunk']['type_fields']['service_group']['part_order'])
        manifest=ordered[0]['chunk']['type_fields']['service_group']['record_manifest']
        validate_record_manifest(manifest,len(ordered))
        pieces={identity:[] for identity in manifest['gaps']}
        for index,row in enumerate(ordered):
            fields=row['chunk']['type_fields'];group=fields['service_group'];associations=fields['field_associations']
            if (group.get('record_manifest')!=manifest or group.get('part_reading_id')!=fields.get('reading_id')
                    or group['part_reading_id']!=group['logical_step_id']+'::part:'+str(index)
                    or [f['name'] for f in associations]!=manifest['parts'][index]
                    or any('field_kind' in f for f in associations)):
                raise ValueError('record part identity or fields differ')
            local=fields['source_limits']
            if not isinstance(local,list):raise ValueError('record source limits required')
            for limit in local:
                identity=limit['gap_id']
                if identity not in pieces:raise ValueError('undeclared source gap')
                pieces[identity].append((index,{k:copy.deepcopy(v) for k,v in limit.items() if k not in LIMIT_DERIVED}))
        for identity,origin in manifest['gaps'].items():
            by_part={i:g for i,g in pieces[identity]}
            if len(by_part)!=len(pieces[identity]):raise ValueError('duplicate projected gap')
            base=None;values={}
            for index,names in enumerate(manifest['parts']):
                expected=[n for n in origin['field_names'] if n in names]
                if not expected:
                    if index in by_part:raise ValueError('gap on unrelated part')
                    continue
                gap=by_part.get(index)
                if gap is None or gap['field_names']!=expected:raise ValueError('missing projected gap fields')
                visible=gap['visible_text'];kind='list' if isinstance(visible,list) else 'string'
                text=visible if kind=='list' else [visible]
                locator=gap['locator'];extra_locator={k:v for k,v in locator.items() if k not in ('field','physical_pages')}
                original_extra={k:v for k,v in origin['locator'].items() if k not in ('field','physical_pages')}
                if (kind!=origin['visible_text_kind'] or len(text)!=len(expected)
                        or any(not isinstance(v,str) or not v.strip() for v in text)
                        or extra_locator!=original_extra):
                    raise ValueError('projected gap metadata differs')
                remainder={k:v for k,v in gap.items() if k not in ('field_names','visible_text','locator')}
                if base is None:base=remainder
                elif base!=remainder:raise ValueError('projected gap meaning differs')
                values.update(zip(expected,text))
            if set(values)!=set(origin['field_names']):raise ValueError('incomplete original gap')
            original={**base,'field_names':origin['field_names'],'locator':origin['locator'],
                'visible_text':[values[n] for n in origin['field_names']] if origin['visible_text_kind']=='list'
                    else values[origin['field_names'][0]]}
            if record_digest(original)!=origin['sha256']:raise ValueError('original source gap hash differs')
    except (KeyError,TypeError,IndexError,ValueError,OverflowError) as exc:
        raise ValueError('invalid reviewed context record') from exc
