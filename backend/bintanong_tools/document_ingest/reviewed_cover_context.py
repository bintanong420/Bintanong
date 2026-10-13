"""Original-image citations for a complete already accepted cover-label list."""
from __future__ import annotations

import copy
import hashlib
import json

from .register import load_pending_register
from .reviewed_policy import build_reviewed_policy_bundle
from .reviewed_image_spans import _span, _transform


def map_reviewed_cover_labels(bundle, *, sources, review_events, source_versions,
        image_page, read_page_image, label_regions, reading_id):
    """Check source/review/render identity; regions remain trusted caller annotations."""
    core=build_reviewed_policy_bundle(bundle['readings'],sources=sources,review_events=review_events)
    if any(bundle.get(k)!=v for k,v in core.items()):
        raise ValueError('reviewed preparation differs from original evidence')
    try:
        row=next(r for r in core['readings'] if r['reading_id']==reading_id)
        field=row['fields'][0];labels=field['reviewed_value'];pages=field['locator']['physical_pages']
        versions={v.version_id:v for v in load_pending_register(source_versions)}
        version=versions[row['version_id']]
        event=json.loads(review_events[field['review_event_sha256']])
        if (row['intended_audience']!='undergraduate' or row['applicability']=='excluded'
                or len(row['fields'])!=1 or field['name']!='cover_labels' or field['decision']!='accepted'
                or field['source_blank'] is not False or not isinstance(labels,list) or not labels
                or any(not isinstance(s,str) or not s.strip() for s in labels)
                or field['original_value']!=labels or len(pages)!=1
                or version.byte_sha256!=row['source_sha256']
                or event.get('source_sha256')!=row['source_sha256']
                or event.get('physical_page')!=pages[0] or event.get('accepted_cover_labels')!=labels
                or not isinstance(label_regions,list) or len(label_regions)!=len(labels)
                or not callable(read_page_image) or not isinstance(image_page,dict)):
            raise ValueError('complete accepted cover evidence required')
        _transform(image_page)
        observed=read_page_image(sources[row['source_sha256']],pages[0])
        if (not isinstance(observed,dict) or not isinstance(observed.get('image_bytes'),bytes)
                or hashlib.sha256(observed['image_bytes']).hexdigest()!=image_page['image_sha256']
                or any(observed.get(k)!=image_page.get(k) for k in ('image_size','page_size','scale','rotation','crop'))):
            raise ValueError('original cover render differs')
        page={**copy.deepcopy(image_page),'source_sha256':row['source_sha256'],'physical_page':pages[0]}
        spans=[_span(row,f'cover-label-{i}',label,region,page)
            for i,(label,region) in enumerate(zip(labels,label_regions))]
        return {'schema_version':'bintanong-reviewed-cover-labels-v1','candidate_only':True,
            'activation_eligible':False,'source_governance_changed':False,'original_reading':copy.deepcopy(row),
            'field_spans':{reading_id:{'cover_labels':spans}},'validated_page':page,
            'label_regions':copy.deepcopy(label_regions),'event_sha256':field['review_event_sha256']}
    except (StopIteration,KeyError,TypeError,IndexError,ValueError) as exc:
        raise ValueError('invalid reviewed cover binding') from exc
