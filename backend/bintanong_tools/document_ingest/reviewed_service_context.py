"""Separate complete logical service-step parts; never mutate original readings."""
from __future__ import annotations

import copy

from .reviewed_service_steps import bind_reviewed_service_step


def prepare_reviewed_service_context(mapping, *, reading_id, subaction_ids, fee_region):
    """Project a checked parent and ordered actions with atomic dependencies.

    Consumes trusted verified original maps under the existing binder's contract.
    Applicability is copied, not granted. Full original fee and row stay preserved.
    """
    step=bind_reviewed_service_step(mapping,reading_id=reading_id,
        subaction_ids=subaction_ids,fee_region=fee_region)
    original=next(r for r in mapping['preparation']['readings'] if r['reading_id']==reading_id)
    fields={f['name']:f for f in original['fields']}
    parent_id=reading_id+'::parent'
    children=[reading_id+'::action:'+identity for identity in subaction_ids]
    parent=copy.deepcopy(original)
    parent.update(reading_id=parent_id,original_reading_id=reading_id,part_order=0)
    fee=copy.deepcopy(fields['shared_fee'])
    fee.update(original_value=step['shared_fee']['value']['text'],
        reviewed_value=step['shared_fee']['value']['text'])
    fee['locator']['evidence']={'projection':'confirmed parent fee text',
        'original_field':copy.deepcopy(fields['shared_fee'])}
    parent['fields']=[copy.deepcopy(fields['client_instruction']),fee]
    readings=[parent]
    anchors={parent_id:{'client_instruction':copy.deepcopy(step['client_instruction']['spans']),
        'shared_fee':[copy.deepcopy(step['shared_fee']['span'])]}}
    dependencies={parent_id:children}
    for index,action in enumerate(step['subactions']):
        identity=children[index]
        row=copy.deepcopy(original)
        row.update(reading_id=identity,original_reading_id=reading_id,
            part_order=index+1,subaction_id=action['subaction_id'])
        row['fields']=[copy.deepcopy(fields[action['subaction_id']+'/'+part]) for part in action['fields']]
        readings.append(row)
        anchors[identity]={action['subaction_id']+'/'+part:copy.deepcopy(field['spans'])
            for part,field in action['fields'].items()}
        dependencies[identity]=[parent_id]
    return {'schema_version':'bintanong-reviewed-service-context-preparation-v1',
        'candidate_only':True,'activation_eligible':False,'source_governance_changed':False,
        'original_reading':copy.deepcopy(original),'parent_reading_id':parent_id,
        'readings':readings,'field_spans':anchors,'required_readings':dependencies,
        'checked_step':step}
