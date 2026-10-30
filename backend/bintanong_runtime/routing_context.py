"""Opt-in routing hints copied only from assigned, review-bound source fields."""
from __future__ import annotations

import json
import re

LABEL_FIELDS = frozenset(('service_title', 'service_title_and_description', 'service_context'))
COLUMN_FIELDS = frozenset(('grade', 'descriptive_rating', 'percentage_equivalent'))
OPENING_FIELD = 'body'
MAX_OPENING = 100
ITEM_FIELD = 'Cause'  # printed row name of a penalty table
MAX_ITEM, MAX_ITEMS = 60, 48
MAX_CLAIM_HEADINGS = 8
# A not-stated claim is offered separately as not_stated; other unresolved limits are source defects.
OPENING_ALLOWED_LIMITS = frozenset(('claim_not_stated',))


def _opening(text, limit=MAX_OPENING):
    if len(text) <= limit:
        return text
    cut = text[:limit]
    return cut[:cut.rfind(' ')].rstrip() + '…' if ' ' in cut else cut + '…'


def _reviewed_fields(register, catalogue, chunks, field_name):
    """(subject, claims, value, defective) of one review-bound, nonblank field per chunk, in chunk order;
    claims are the reviewed claims binding that field on that chunk."""
    assigned = {a['reading_id']: a['subject_id'] for a in (catalogue or {}).get('assignments', [])}
    reviewed = {}
    for review in register['reviews']:
        if review.get('finding') != 'visible_fields':
            continue
        for ref in review.get('field_refs', []):
            if (isinstance(ref, dict) and ref.get('field_name') == field_name
                    and assigned.get(ref.get('reading_id')) == review['subject_id']):
                for chunk_id in review.get('reviewed_chunk_ids', ()):
                    claims = reviewed.setdefault((ref['reading_id'], chunk_id), [])
                    if review['claim'] not in claims:
                        claims.append(review['claim'])
    for chunk in chunks:
        reading = chunk.get('type_fields', {}).get('reading_id')
        subject = assigned.get(reading)
        claims = reviewed.get((reading, chunk.get('chunk_id')))
        if subject is None or not claims:
            continue
        try:
            record = json.loads(chunk['text'])
            field = {f['name']: f for f in record['fields']}.get(field_name, {})
            limits = record['source_limits']
        except (KeyError, TypeError, AttributeError, ValueError):
            continue
        value = field.get('value')
        if field.get('source_blank') is not False or not isinstance(value, str) or not value.strip():
            continue
        defective = any(not isinstance(limit, dict) or limit.get('resolution') != 'resolved'
                        and limit.get('issue') not in OPENING_ALLOWED_LIMITS for limit in limits)
        yield subject, tuple(claims), value.strip(), defective


def _reviewed_values(register, catalogue, chunks, field_name):
    """(subject, value) of one review-bound, nonblank field per chunk, in chunk order; defects withhold it."""
    for subject, _, value, defective in _reviewed_fields(register, catalogue, chunks, field_name):
        if not defective:
            yield subject, value


def _headings(value, defective):
    """Printed section headings of a body; a recorded defect keeps them (owner 30 Oct 2026), except one
    ending that body, which may be cut."""
    return [h.group(0) for h in _HEADING.finditer(value) if not (defective and h.end() == len(value))]


def reviewed_openings(register, catalogue, chunks):
    """The first review-bound body field of each subject, cut verbatim at a word; defects withhold it."""
    openings = {}
    for subject, value in _reviewed_values(register, catalogue, chunks, OPENING_FIELD):
        openings.setdefault(subject, _opening(value))
    return openings


def reviewed_items(register, catalogue, chunks):
    """Printed row names (review-bound Cause fields) and printed numbered section headings (review-bound body
    fields, owner 30 Oct 2026) of each subject, cut verbatim at a word; routing context only. A recorded defect
    elsewhere in a body keeps its headings (owner 30 Oct 2026), except one ending that body, which may be cut."""
    items = {}
    def add(subject, value):
        values = items.setdefault(subject, [])
        item = _opening(value, MAX_ITEM)
        if item not in values and len(values) < MAX_ITEMS:
            values.append(item)
    for subject, value in _reviewed_values(register, catalogue, chunks, ITEM_FIELD):
        add(subject, value)
    for subject, _, value, defective in _reviewed_fields(register, catalogue, chunks, OPENING_FIELD):
        for heading in _headings(value, defective):
            add(subject, heading)
    return {s: tuple(v) for s, v in items.items()}


def reviewed_claim_headings(register, catalogue, chunks):
    """Each reviewed claim's own printed section headings (owner 30 Oct 2026); router routing context only."""
    headings = {}
    for subject, claims, value, defective in _reviewed_fields(register, catalogue, chunks, OPENING_FIELD):
        for claim in claims:
            values = headings.setdefault(subject, {}).setdefault(claim, [])
            for heading in _headings(value, defective):
                heading = _opening(heading, MAX_ITEM)
                if heading not in values and len(values) < MAX_CLAIM_HEADINGS:
                    values.append(heading)
    return {s: {c: tuple(v) for c, v in claims.items() if v} for s, claims in headings.items()}


# A printed heading: a dotted section number (3. or 3.1), then an all-capitals title ending before ". ", the next number or a sentence.
_HEADING = re.compile(r'(?<!\S)(?:\d+(?:\.\d+)+\.?|\d+\.)\s+[A-Z][A-Z0-9 /&(),\'"‘’“”-]*[A-Z0-9)\'"’”]'
                      r'(?=\.\s|\.$|\s+\d+(?:\.\d+)*\.?\s|\s+[A-Z][a-z]|$)')


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
