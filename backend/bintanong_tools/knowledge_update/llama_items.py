from __future__ import annotations

import json

from ...bintanong_contracts.source import SourceSpan
from ..prospectus_review_gui.render import PageRenderer
from .templates import template_items


def items(payload, doc, source):
    if (not isinstance(payload, dict) or payload.get('schema_version') != 'bintanong-llamaparse-candidate-v1'
            or payload.get('source_sha256') != doc['sha256']
            or not isinstance(payload.get('pages'), list)
            or not isinstance(payload.get('failed_pages'), list)):
        raise ValueError('LlamaParse candidate source/format mismatch')
    requested = payload.get('config', {}).get('pages', [])
    if (not requested or any(type(p) is not int or p < 1 for p in requested)
            or len(requested) != len(set(requested))):
        raise ValueError('LlamaParse physical selection missing')
    template = {'readings': [], 'field_spans': {}, 'required_readings': {}}
    seen, headings = set(), []
    with PageRenderer(doc['source']) as pdf:
        if max(requested) > pdf.page_count:
            raise ValueError('LlamaParse selection exceeds original')
        for page in payload['pages']:
            physical = page.get('page_number')
            if (type(physical) is not int or physical not in requested or physical in seen
                    or page.get('success') is not True or not isinstance(page.get('items'), list)):
                raise ValueError('invalid LlamaParse page result')
            seen.add(physical)
            width, height = pdf.size(physical)
            for index, raw in enumerate(page['items']):
                if not isinstance(raw, dict) or any(k in raw for k in ('approved', 'decision', 'verified', 'reviewed')):
                    raise ValueError('invalid or privileged parser item metadata')
                kind = raw.get('type')
                if kind in ('text', 'heading', 'code'):
                    text = raw.get('value')
                    if not isinstance(text, str):
                        raise ValueError('invalid parser text')
                    if kind == 'heading':
                        level = raw.get('level')
                        if type(level) is not int or not 1 <= level <= 6:
                            raise ValueError('invalid parser heading')
                        headings = headings[:level - 1] + [text]
                else:
                    # Keep tables/merged cells/continuations together; never zip unrelated columns.
                    text = json.dumps(raw, ensure_ascii=False, sort_keys=True, allow_nan=False)
                if len(text) > 256 * 1024:
                    raise ValueError('parser item exceeds review field limit')
                identity = f"{doc['id']}:llama-p{physical}-i{index}"
                field = {'name': 'body', 'original_value': text, 'reviewed_value': text,
                    'decision': 'pending', 'source_blank': False,
                    'locator': {'physical_pages': [physical], 'field': 'body'}}
                template['readings'].append({'reading_id': identity, 'title': ' / '.join(headings) or f'{kind} · page {physical}',
                    'source_sha256': doc['sha256'], 'version_id': 'ver-' + doc['sha256'],
                    'fields': [field], 'gaps': []})
                spans = []
                boxes = raw.get('bbox')
                if (isinstance(boxes, list) and len(boxes) == 1 and isinstance(boxes[0], dict)
                        and page.get('page_width') == width and page.get('page_height') == height
                        and pdf.rotation(physical) == 0):
                    try:
                        b = boxes[0]
                        span = SourceSpan.parse({'schema_version': 'bintanong-source-span-v1',
                            'byte_sha256': doc['sha256'], 'version_id': 'ver-' + doc['sha256'],
                            'page': physical, 'printed_page_label': None,
                            'text': text, 'bbox': [b['x'], b['y'], b['x'] + b['w'], b['y'] + b['h']],
                            'bbox_origin': 'TOPLEFT', 'page_size': [width, height],
                            'locator': {'kind': 'text_item', 'item_ids': [identity], 'cell_ids': [],
                                        'table_index': None, 'ref': None},
                            'extraction': {'source_kind': 'llamaparse', 'resolution_method': 'parser_candidate',
                                           'repair_id': None, 'ocr_confidence': None}})
                        spans.append(span.model_dump(mode='json'))
                    except (ValueError, KeyError, TypeError):
                        pass
                template['field_spans'][identity] = {'body': spans}
        missing = set(requested) - seen
        if set(payload['failed_pages']) != missing:
            raise ValueError('LlamaParse missing-page accounting mismatch')
        for page in sorted(missing):
            identity = f"{doc['id']}:llama-p{page}-missing"
            template['readings'].append({'reading_id': identity, 'title': f'Parser unavailable · page {page}',
                'source_sha256': doc['sha256'], 'version_id': 'ver-' + doc['sha256'], 'gaps': [],
                'fields': [{'name': 'body', 'original_value': '', 'reviewed_value': '', 'source_blank': False,
                            'decision': 'pending', 'locator': {'physical_pages': [page], 'field': 'body'}}]})
    if not template['readings']:
        raise ValueError('empty parser output requires manual extraction')
    if doc['kind'] == 'charter':
        ids = [r['reading_id'] for r in template['readings']]
        template['required_readings'] = {i: [j for j in ids if j != i] for i in ids}
    output = template_items(template, doc, source)
    for row in output:
        row['findings'].append('parser_associations_require_manual_review')
        if not row['fields'][0]['spans']:
            row['findings'].append('missing_original_geometry_build_withheld')
    return output
