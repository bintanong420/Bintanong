"""Whole-field partitions with immutable original readings and mandatory context."""
from __future__ import annotations

import copy

from ...bintanong_contracts.source import SourceSpan,canonical_text
from ...bintanong_contracts.reviewed_record_groups import make_record_manifest,project_record_gaps
from .reviewed_policy import build_reviewed_policy_bundle


def prepare_reviewed_record_context(bundle, *, reading_id, field_groups, field_spans, sources, review_events):
    core=build_reviewed_policy_bundle(bundle['readings'],sources=sources,review_events=review_events)
    if any(bundle.get(k)!=v for k,v in core.items()):raise ValueError('reviewed preparation differs')
    try:
        row=next(r for r in core['readings'] if r['reading_id']==reading_id)
        fields=row['fields'];names=[f['name'] for f in fields];anchors=field_spans[reading_id]
        manifest=make_record_manifest(row,field_groups)
        if (row['intended_audience']!='undergraduate' or row['applicability']=='excluded'
                or [n for group in field_groups for n in group]!=names or set(anchors)!=set(names)):
            raise ValueError('complete undergraduate field partition required')
        for field in fields:
            name=field['name'];value=field['reviewed_value'];supplied=anchors[name]
            if (field['decision'] not in ('accepted','corrected') or not isinstance(value,str)
                    or not isinstance(supplied,list)):
                raise ValueError('confirmed scalar fields required')
            spans=[SourceSpan.parse(s) for s in supplied]
            if field['source_blank']:
                if field['original_value']!='' or value!='' or spans:raise ValueError('literal source blank required')
            elif (not value.strip() or not spans or any(not s.is_complete or s.bbox is None or s.page_size is None
                    or s.byte_sha256!=row['source_sha256'] or s.version_id!=row['version_id'] for s in spans)
                    or {s.page for s in spans}!=set(field['locator']['physical_pages'])
                    or canonical_text(' '.join(s.text for s in spans))!=canonical_text(value)):
                raise ValueError('field source text or location differs')
        identities=[reading_id+'::part:'+str(i) for i in range(len(field_groups))]
        readings,maps,required=[],{},{}
        by_name={f['name']:f for f in fields}
        for index,group in enumerate(field_groups):
            if not any(anchors[n] for n in group):raise ValueError('located content required for every part')
            part=copy.deepcopy(row);identity=identities[index]
            part.update(reading_id=identity,original_reading_id=reading_id,part_order=index,
                record_manifest=copy.deepcopy(manifest),fields=[copy.deepcopy(by_name[n]) for n in group],
                gaps=project_record_gaps(row,group,anchors))
            readings.append(part);maps[identity]={n:copy.deepcopy(anchors[n]) for n in group}
            required[identity]=identities[1:] if index==0 else identities[:1]
        binding={'original_reading':copy.deepcopy(row),'field_groups':copy.deepcopy(field_groups),
            'original_field_spans':copy.deepcopy(anchors)}
        return {'schema_version':'bintanong-reviewed-record-context-v1','candidate_only':True,
            'activation_eligible':False,'source_governance_changed':False,'original_reading':copy.deepcopy(row),
            'readings':readings,'field_spans':maps,'required_readings':required,
            'record_bindings':{reading_id:binding}}
    except (StopIteration,KeyError,TypeError,IndexError,ValueError,OverflowError) as exc:
        raise ValueError('invalid reviewed record partition') from exc


def validate_reviewed_record_binding(identity,binding,rows,anchors,*,sources,review_events):
    try:
        original=binding['original_reading']
        if original['reading_id']!=identity:raise ValueError('original reading identity differs')
        bundle=build_reviewed_policy_bundle([original],sources=sources,review_events=review_events)
        expected=prepare_reviewed_record_context(bundle,reading_id=identity,field_groups=binding['field_groups'],
            field_spans={identity:binding['original_field_spans']},sources=sources,review_events=review_events)
        current=[r for r in rows.values() if r.get('original_reading_id')==identity]
        current.sort(key=lambda r:r['part_order'])
        if current!=expected['readings'] or any(anchors.get(i)!=v for i,v in expected['field_spans'].items()):
            raise ValueError('record derivation differs from original evidence')
        return expected
    except (KeyError,TypeError,IndexError,ValueError,OverflowError) as exc:
        raise ValueError('invalid reviewed record binding') from exc
