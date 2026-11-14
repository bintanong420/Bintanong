"""Owner 6 Nov 2026: quote general room guidance beside the library-only workflow."""
import json
import re

from ..bintanong_routing.topic_selection import FACILITY_TOPICS, general_facility_request
from .service_steps import parse_service, render_service

_GENERAL = re.compile(r'6\.\s+How to avail the use of university rooms and facilities\?\s*'
                      r'(?P<answer>A\.\s+.+?\s+B\.\s+.+?\.)(?=\s+\d+\.\s|$)', re.I)


def facilities_claims(pack):
    parts = [p for p in (pack.understanding.parts if pack.understanding else ())
             if p.evidence_need == 'document' and p.subject_id in FACILITY_TOPICS and p.detail == 'whole'
             and general_facility_request(p.text)]
    if not parts:
        return {}
    coverage = {subject: {ref for s, claim, refs in pack.record_coverage
                         if s == subject and claim == wanted for ref in refs}
                for subject, wanted in FACILITY_TOPICS.items()}
    cards = {c.evidence_id: c for c in pack.cards if c.kind == 'document'}
    general = []
    for ref in coverage['handbook_student_faq']:
        if ref not in cards:
            continue
        try:
            record = json.loads(cards[ref].text)
            if any(limit.get('resolution') == 'unresolved' for limit in record.get('source_limits', [])):
                continue
            for field in record['fields']:
                if field.get('name') == 'body' and field.get('source_blank') is False:
                    match = _GENERAL.search(' '.join(field['value'].split()))
                    if match:
                        general.append((match.group('answer'), ref))
        except (ValueError, TypeError, KeyError):
            continue
    if len(general) != 1:
        return {}
    records = [(ref, card.text) for ref, card in cards.items() if ref in coverage['charter_library_facilities']]
    table = parse_service(records)
    if table is None:
        return {}
    rendered = render_service(table, pack.language, max_claims=7)
    if not rendered:
        return {}
    taglish = pack.language in ('fil', 'taglish')
    lead = 'General university guidance (Handbook): ' if not taglish else 'Para sa university rooms at facilities (Handbook): '
    library = 'Library-specific guidance only: ' if not taglish else 'Para lang sa library facilities: '
    quote, ref = general[0]
    reply = [(lead + '"' + quote + '"', (ref,)),
             (library + rendered[0][0], rendered[0][1]), *rendered[1:]]
    return {p.part_id: reply for p in parts}
