from __future__ import annotations

import copy
from datetime import datetime, timezone
import math

from .files import digest, encoded


def binding(row, field, doc):
    candidate = [{k: f.get(k) for k in ('name', 'original_value', 'locator', 'spans', 'source_blank')}
                 for f in row['fields']]
    return {'source_sha256': doc['sha256'], 'candidate_hash': digest(encoded(candidate)),
            'item_id': row['id'], 'field': field['name'],
            'pages': field['locator']['physical_pages']}


def result(value, original):
    allowed = {'outcome', 'proposed_value', 'rationale', 'confidence'}
    if (not isinstance(value, dict) or set(value) - allowed
            or value.get('outcome') not in ('proposal', 'no_change', 'uncertain', 'failed')
            or not isinstance(value.get('rationale', ''), str)
            or len(value.get('rationale', '')) > 4000):
        raise ValueError('invalid advisory response')
    if 'confidence' in value and (type(value['confidence']) not in (float, int)
            or not math.isfinite(value['confidence']) or not 0 <= value['confidence'] <= 1):
        raise ValueError('invalid advisory confidence')
    if value['outcome'] == 'proposal':
        if (type(value.get('proposed_value')) is not type(original)
                or len(encoded(value['proposed_value'])) > 256 * 1024):
            raise ValueError('invalid advisory value')
    elif 'proposed_value' in value:
        raise ValueError('only a proposal can suggest a value')
    return copy.deepcopy(value)


def validate(rows, documents):
    docs = {d['id']: d for d in documents}
    for row in rows:
        for field in row['fields']:
            advice = field.get('assistance')
            if advice is None:
                continue
            if (not isinstance(advice, dict) or set(advice) - {
                    'binding', 'provider', 'model', 'created_at', 'outcome',
                    'proposed_value', 'rationale', 'confidence'}
                    or advice.get('binding') != binding(row, field, docs[row['document_id']])):
                raise ValueError('stale or mismatched advisory proposal')
            checked = result({k: v for k, v in advice.items() if k in {
                'outcome', 'proposed_value', 'rationale', 'confidence'}}, field['original_value'])
            if checked['outcome'] == 'proposal' and field.get('proposed_value') != checked['proposed_value']:
                raise ValueError('stale advisory proposed value')


def assist(rows, documents, provider, render, *, mode='none', pages=(), item_ids=()):
    if (mode not in ('none', 'all', 'flagged', 'selected')
            or any(type(p) is not int or p < 1 for p in pages)
            or (mode == 'selected' and not pages and not item_ids)):
        raise ValueError('invalid assistance selection')
    rows = copy.deepcopy(rows)
    if mode == 'none':
        return rows
    if provider is None:
        raise ValueError('select an explicit assistance provider')
    docs = {d['id']: d for d in documents}
    images = {}
    for row in rows:
        if mode == 'flagged' and not row.get('findings') and not row.get('source_gaps'):
            continue
        for field in row['fields']:
            located = field['locator']['physical_pages']
            if (not located or field.get('source_blank') or (mode == 'selected'
                    and row['id'] not in item_ids and not set(located).intersection(pages))):
                continue
            doc = docs[row['document_id']]
            anchor = binding(row, field, doc)
            try:
                evidence = []
                for page in located:
                    key = (doc['id'], page)
                    if key not in images:
                        images[key] = render(doc, page)
                    evidence.append({'page': page, 'png': images[key]})
                checked = result(provider.inspect({**anchor, 'original_value': field['original_value'],
                    'images': evidence, 'related_items': row.get('companions', [])}), field['original_value'])
            except Exception:
                # Provider exception strings may contain credentials or response bodies.
                checked = {'outcome': 'failed', 'rationale': 'AI assistance unavailable. Review the original manually.'}
            field['assistance'] = {**checked, 'binding': anchor,
                'provider': provider.provider, 'model': provider.model,
                'created_at': datetime.now(timezone.utc).isoformat()}
            if checked['outcome'] == 'proposal':
                field['proposed_value'] = copy.deepcopy(checked['proposed_value'])
    validate(rows, documents)
    return rows
