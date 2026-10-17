"""Carry checked decision arrows and complete original node readings together."""
from __future__ import annotations

import copy

from ...bintanong_contracts.reviewed_policy_context import validate_reviewed_arrows
from ...bintanong_contracts.source import SourceSpan
from .reviewed_image_spans import bind_reviewed_flowchart


def prepare_reviewed_flowchart_context(mapping, *, arrow_reading_id, row_reading_ids,
        edge_regions, terminal_region):
    """Reuse trusted original-layout annotations; never infer routes or approve scope."""
    graph=bind_reviewed_flowchart(mapping,arrow_reading_id=arrow_reading_id,
        row_reading_ids=row_reading_ids,edge_regions=edge_regions,terminal_region=terminal_region)
    originals={r['reading_id']:r for r in mapping['preparation']['readings']}
    identities=[arrow_reading_id,*row_reading_ids.values()]
    if len(set(identities))!=len(identities):
        raise ValueError('distinct arrow and node readings required')
    readings,anchors,required=[],{},{}
    for order,identity in enumerate(identities):
        row=copy.deepcopy(originals[identity])
        if row['intended_audience']!='undergraduate' or row['applicability']=='excluded':
            raise ValueError('undergraduate node reading required')
        row.update(original_reading_id=arrow_reading_id,part_order=order)
        readings.append(row)
        anchors[identity]=copy.deepcopy(mapping['field_spans'].get(identity,{}))
        required[identity]=identities[1:] if order==0 else [arrow_reading_id]
    anchors[arrow_reading_id]={'arrows':[copy.deepcopy(e['label_span']) for e in graph['edges']]
        +[copy.deepcopy(graph['terminal']['span'])]}
    validate_reviewed_flowchart_binding(graph,{r['reading_id']:r for r in readings},anchors)
    return {'schema_version':'bintanong-reviewed-flowchart-context-preparation-v1',
        'candidate_only':True,'activation_eligible':False,'source_governance_changed':False,
        'original_readings':[copy.deepcopy(originals[i]) for i in identities],
        'readings':readings,'field_spans':anchors,'required_readings':required,
        'flowchart_bindings':{arrow_reading_id:graph}}


def validate_reviewed_flowchart_binding(graph, rows, anchors):
    """Bind saved graph fields/events/spans to the exact current reviewed readings.

    Original-layout annotations remain trusted caller inputs. This checks their
    internal agreement with previously verified evidence, not institutional authority.
    """
    try:
        identity=graph['arrow_reading_id'];root=rows[identity]
        nodes=graph['nodes'];mapping={n['node_id']:n['reading_id'] for n in nodes}
        ids=[identity,*mapping.values()]
        if (graph['schema_version']!='bintanong-reviewed-flowchart-v1'
                or graph['candidate_only'] is not True or graph['activation_eligible'] is not False
                or graph['source_governance_changed'] is not False or graph['source_limits']
                or graph['source_sha256']!=root['source_sha256'] or graph['version_id']!=root['version_id']
                or len(mapping)!=len(nodes) or len(set(ids))!=len(ids) or len(root['fields'])!=1):
            raise ValueError('invalid checked flowchart')
        field=root['fields'][0]
        located=[e['label_span'] for e in graph['edges']]+[graph['terminal']['span']]
        association={'name':'arrows','value':field['reviewed_value'],'source_blank':field['source_blank'],
            'field_kind':'arrows','node_reading_ids':mapping,'span_indexes':list(range(len(located)))}
        validate_reviewed_arrows(association,[SourceSpan.parse(s) for s in located])
        if (field['name']!='arrows' or field['decision'] not in {'accepted','corrected'}
                or field['locator']['physical_pages']!=[located[0]['page']]
                or graph['terminal']['label']!='END'
                or any(e['event_sha256']!=field['review_event_sha256'] for e in graph['edges'])
                or graph['terminal']['event_sha256']!=field['review_event_sha256']
                or [{k:e[k] for k in ('from','label','to')} for e in graph['edges']]!=field['reviewed_value']
                or anchors.get(identity,{}).get('arrows')!=located):
            raise ValueError('arrow evidence differs')
        for order,reading_id in enumerate(ids):
            row=rows[reading_id]
            if (row['original_reading_id']!=identity or row['part_order']!=order
                    or row['source_sha256']!=root['source_sha256'] or row['version_id']!=root['version_id']
                    or row['intended_audience']!='undergraduate' or row['applicability']=='excluded' or row['gaps']):
                raise ValueError('node source/group or applicability differs')
            if order:
                expected=[{'name':f['name'],'value':f['reviewed_value'],
                    'spans':anchors.get(reading_id,{}).get(f['name']),
                    'event_sha256':f['review_event_sha256']} for f in row['fields']]
                if expected!=nodes[order-1]['fields'] or any(f['decision'] not in {'accepted','corrected'} for f in row['fields']):
                    raise ValueError('node field evidence differs')
        if any(s['byte_sha256']!=root['source_sha256'] or s['version_id']!=root['version_id'] for s in located):
            raise ValueError('arrow span source/version differs')
        return mapping
    except (KeyError,TypeError,IndexError,ValueError) as exc:
        raise ValueError('invalid reviewed flowchart binding') from exc
