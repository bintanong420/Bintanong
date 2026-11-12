"""On-demand, local vision advice without changing a sealed packet or review journal."""
from __future__ import annotations

import math
from urllib.parse import urlsplit

from .advisory import assist
from .files import contained
from .intake import Refusal
from .prepare import load_packet
from .vision import VisionProvider


def audit_field(review, command, renderer):
    if (not isinstance(command, dict) or set(command) != {'packet_id', 'revision', 'item_id', 'field'}
            or type(command['revision']) is not int or command['revision'] < 0
            or any(not isinstance(command[k], str) or not command[k] for k in ('packet_id', 'item_id', 'field'))):
        raise ValueError('audit needs a packet, revision, item and field')
    with review.guard:
        state = review.state()
        if command['packet_id'] != state['packet_id'] or command['revision'] != state['revision']:
            raise Refusal('The review changed. Reload before auditing.', 'stale_audit', 409)
        row = next((r for r in state['items'] if r['id'] == command['item_id']), None)
        field = next((f for f in row['fields'] if f['name'] == command['field']), None) if row else None
        if not field or row.get('reference_only'):
            raise ValueError('choose an editable field in this review packet')
        pages = field['locator']['physical_pages']
        if not pages or len(pages) > 8 or field.get('source_blank'):
            raise ValueError('audit needs a nonblank field located on 1..8 source pages')
        packet = load_packet(review.root, reuse_checked=True)
        doc = next(d for d in packet['documents'] if d['id'] == row['document_id'])
        source = contained(review.root, doc['source'])
    try:
        provider = VisionProvider.from_environment()
        address = urlsplit(provider.url)
        if address.scheme != 'http' or address.hostname not in {'127.0.0.1', 'localhost'}:
            raise ValueError('review audits require local inference')
    except ValueError:
        raise Refusal('Gemma auditing is not configured for a local vision server. Manual review remains available.',
                      'audit_unavailable', 503) from None
    with renderer(source) as original:
        def render(document, page):
            width, height = original.size(page)
            scale = min(1.5, math.sqrt(2_000_000 / (width * height)))
            return original.png(page, scale)
        result = assist([row], [doc], provider, render, mode='all', field_names=[command['field']])[0]
    with review.guard:
        if review.state()['revision'] != command['revision']:
            raise Refusal('The review changed during the audit. Run it again on the current field.', 'stale_audit', 409)
    return {'packet_id': state['packet_id'], 'revision': state['revision'], 'item_id': row['id'],
            'field': next(f for f in result['fields'] if f['name'] == command['field'])}
