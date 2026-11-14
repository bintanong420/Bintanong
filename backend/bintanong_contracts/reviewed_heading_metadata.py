"""Bound heading projections; formatted metadata is never a source quotation."""
from __future__ import annotations

import copy
import re

from .source import SourceSpan, canonical_text, check_span_binding


KINDS = {'placement': 'year_term_heading_metadata',
    'edition_status': 'proposed_edition_heading_metadata'}


def _top_box(span):
    l, t, r, b = span.bbox
    if span.bbox_origin == 'BOTTOMLEFT':
        height = span.page_size[1]
        return l, height-t, r, height-b
    if span.bbox_origin != 'TOPLEFT':
        raise ValueError('explicit heading coordinate origin required')
    return l, t, r, b


def _project(name, kind, headings, anchors):
    if name not in KINDS or KINDS[name] != kind or len(headings) != 2 or not anchors:
        raise ValueError('unsupported heading metadata projection')
    all_spans = headings + anchors
    first = all_spans[0]
    if any(not s.is_complete or s.bbox is None or s.page_size is None
            or (s.byte_sha256, s.version_id, s.page, s.page_size)
            != (first.byte_sha256, first.version_id, first.page, first.page_size) for s in all_spans):
        raise ValueError('complete same-page heading and row geometry required')
    for span in headings:
        refs = span.locator.item_ids
        match = re.fullmatch(r'native-pdf:p'+str(span.page)+r':chars(\d+)-(\d+)', refs[0]) if len(refs)==1 else None
        if (span.extraction.source_kind != 'native_pdf' or not match
                or int(match[1]) >= int(match[2])):
            raise ValueError('literal native heading ranges required')
    boxes = [_top_box(s) for s in anchors]
    row_top = min(b[1] for b in boxes)
    row_x = sum((b[0]+b[2])/2 for b in boxes)/len(boxes)
    heading_boxes = [_top_box(s) for s in headings]
    if any(box[3] >= row_top for box in heading_boxes):
        raise ValueError('heading must be above the bound course row')
    texts = [canonical_text(s.text) for s in headings]
    if name == 'placement':
        if (not re.fullmatch(r'(FIRST|SECOND|THIRD|FOURTH|FIFTH) YEAR', texts[0])
                or not re.fullmatch(r'(FIRST|SECOND) SEMESTER|SUMMER', texts[1])
                or heading_boxes[0][3] >= heading_boxes[1][1]):
            raise ValueError('ordered literal year/term headings required')
        term_x = (heading_boxes[1][0]+heading_boxes[1][2])/2
        if texts[1] != 'SUMMER' and (term_x < first.page_size[0]/2) != (row_x < first.page_size[0]/2):
            raise ValueError('semester heading is in another column')
        return texts[0].title() + ' / ' + texts[1].title()
    match = re.fullmatch(r'Proposed Date of Implementation: (First|Second) Semester, SY (\d{4})-(\d{4})', texts[1])
    if (not re.fullmatch(r'PROPOSED BACHELOR .+ PROGRAM OF STUDY', texts[0])
            or not match or int(match[3]) != int(match[2])+1):
        raise ValueError('explicit proposed programme and implementation year required')
    return 'PROPOSED '+match[2]+'-'+match[3]


def bind_reviewed_heading_metadata(row, field, binding, field_spans, version):
    """Validate trusted source-mapping input against the actual reviewed field."""
    expected = {'reading_id': row['reading_id'], 'field_name': field['name'],
        'source_sha256': row['source_sha256'], 'version_id': row['version_id'],
        'owner_event_sha256': field['review_event_sha256'], 'confirmed_value': field['reviewed_value']}
    if (not isinstance(binding, dict) or any(binding.get(k) != v for k,v in expected.items())
            or binding.get('is_literal_scalar_quote') is not False
            or binding.get('effectivity_inferred', False) is not False or field['source_blank'] is not False
            or field['decision'] not in ('accepted', 'corrected')):
        raise ValueError('heading metadata differs from the reviewed field')
    expected_anchors = [SourceSpan.parse(s) for n in ('course_code','course_title')
        for s in field_spans.get(n, [])]
    supplied = binding.get('row_anchor_spans')
    raw_headings = binding.get('literal_source_spans')
    if not isinstance(supplied, list) or not isinstance(raw_headings, list):
        raise ValueError('explicit heading and course-row spans required')
    anchors = [SourceSpan.parse(s) for s in supplied]
    if ([s.model_dump(mode='json') for s in anchors] != [s.model_dump(mode='json') for s in expected_anchors]
            or not field_spans.get('course_code') or not field_spans.get('course_title')):
        raise ValueError('complete unchanged course-code/title anchors required')
    headings = [SourceSpan.parse(s) for s in raw_headings]
    for span in headings + anchors:
        check_span_binding(span, version)
    kind = binding.get('projection_kind')
    if (_project(field['name'],kind,headings,anchors) != field['reviewed_value']
            or set(field['locator']['physical_pages']) != {s.page for s in headings}):
        raise ValueError('projected metadata differs from the accepted value or pages')
    return headings, {'name': field['name'], 'value': field['reviewed_value'], 'source_blank': False,
        'event_sha256': field['review_event_sha256'], 'field_kind': 'heading_metadata',
        'projection_kind': kind, 'source_headings': [s.text for s in headings],
        'is_literal_scalar_quote': False}


def validate_reviewed_heading_metadata(field, associations, spans):
    """Revalidate stored projections and their exact course-row citation references."""
    refs = field.get('span_indexes')
    anchor_refs = field.get('row_anchor_indexes')
    course_fields = {f['name']: f for f in associations if f['name'] in ('course_code','course_title')}
    if set(course_fields) != {'course_code','course_title'}:
        raise ValueError('complete course-row context required')
    expected = [i for n in ('course_code','course_title') for i in course_fields[n]['span_indexes']]
    if (field.get('field_kind') != 'heading_metadata' or field.get('source_blank') is not False
            or field.get('is_literal_scalar_quote') is not False
            or not isinstance(refs,list) or len(refs) != 2 or len(set(refs)) != 2
            or not isinstance(anchor_refs,list) or anchor_refs != expected or not expected
            or any(type(i) is not int or not 0 <= i < len(spans) for i in refs+anchor_refs)
            or set(refs) & set(anchor_refs)
            or any(not course_fields[n]['span_indexes'] or course_fields[n].get('field_kind') is not None
                or course_fields[n]['source_blank'] is not False
                or course_fields[n]['event_sha256'] != field['event_sha256'] for n in course_fields)):
        raise ValueError('invalid heading metadata association')
    headings = [spans[i] for i in refs]
    anchors = [spans[i] for i in anchor_refs]
    if (field.get('source_headings') != [s.text for s in headings]
            or field['value'] != _project(field['name'],field.get('projection_kind'),headings,anchors)):
        raise ValueError('stored metadata differs from literal headings or row context')


def heading_metadata_display(field):
    """Fixed display labels preserve the distinction between value and quotation."""
    return {'projection_kind': field['projection_kind'],
        'source_headings': copy.deepcopy(field['source_headings']),
        'value_origin': 'derived_from_printed_headings',
        'limitation': ('Proposed implementation; effectivity is not established.'
            if field['projection_kind'] == 'proposed_edition_heading_metadata'
            else 'Heading formatting does not establish curriculum applicability.')}
