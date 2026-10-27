"""Opt-in routing hints copied only from assigned, review-bound source fields."""
from __future__ import annotations

import json

LABEL_FIELDS = frozenset(('service_title', 'service_title_and_description', 'service_context'))
COLUMN_FIELDS = frozenset(('grade', 'descriptive_rating', 'percentage_equivalent'))


def reviewed_context(register, catalogue, chunks):
    assigned = {a['reading_id']: a['subject_id'] for a in (catalogue or {}).get('assignments', [])}
    available = {}
    for chunk in chunks:
        reading = chunk.get('type_fields', {}).get('reading_id')
        if reading not in assigned:
            continue
        try:
            record = json.loads(chunk['text'])
            fields, limits = record['fields'], record['source_limits']
            if (not isinstance(fields, list) or not isinstance(limits, list)
                    or any(not isinstance(f, dict) or not isinstance(f.get('name'), str) for f in fields)
                    or any(not isinstance(limit, dict) for limit in limits)):
                raise ValueError('invalid_routing_context')
            by_name = {f['name']: f for f in fields}
            if len(by_name) != len(fields) or reading in available:
                raise ValueError('invalid_routing_context')
        except (KeyError, TypeError, AttributeError, ValueError):
            raise ValueError('invalid_routing_context') from None
        # Labels/column hints never launder a held or unknown source condition.
        available[reading] = (chunk['chunk_id'], by_name,
            any(limit.get('resolution') != 'resolved' for limit in limits))

    labels, columns = {}, {}
    for review in register['reviews']:
        if review.get('finding') != 'visible_fields':
            continue
        subject, claim = review['subject_id'], review['claim']
        for ref in review.get('field_refs', []):
            if not isinstance(ref, dict):
                raise ValueError('invalid_routing_context')
            reading, name = ref.get('reading_id'), ref.get('field_name')
            if not isinstance(name, str) or assigned.get(reading) != subject:
                continue
            identity, fields, held = available.get(reading, (None, {}, True))
            field = fields.get(name, {})
            value = field.get('value')
            if (held or identity not in review.get('reviewed_chunk_ids', ())
                    or field.get('source_blank') is not False
                    or not isinstance(value, str) or not value.strip()):
                continue
            if name in LABEL_FIELDS:
                if len(value) > 1024:
                    raise ValueError('routing_context_capacity')
                values = labels.setdefault(subject, [])
                if value not in values:
                    values.append(value)
                if len(values) > 4:
                    raise ValueError('routing_context_capacity')
            if name in COLUMN_FIELDS:
                values = columns.setdefault(subject, {}).setdefault(claim, {})
                if len(value) > 1024 or len(values) >= 8 and name not in values:
                    raise ValueError('routing_context_capacity')
                if name in values and values[name] != value:
                    raise ValueError('invalid_routing_context')
                values[name] = value
    return {s: tuple(v) for s, v in labels.items()}, columns
