"""Quote source-bound service fields instead of completing a cut-off agency action.

Only explicit unresolved agency_action/source_cutoff metadata activates this rule.
These are excerpts, not a reconstructed procedure or a source-order determination.
"""
import json


_NAMES = ('client_step', 'agency_action', 'responsible_person', 'office', 'fee', 'processing_time')
_WORDS = {
    'en': ('The agency action is cut off; its continuation is unavailable. Visible source fields '
           '(original wording quoted): ', 'not printed',
           ('Client step', 'Agency action', 'Person in charge', 'Office', 'Fee', 'Processing time')),
    'fil': ('Putol ang gagawin ng office sa source; hindi available ang kasunod. Ito lang ang '
            'nakikita sa source (original na wording): ', 'walang naka-print',
            ('Gagawin ng estudyante', 'Gagawin ng office', 'Naka-assign', 'Office', 'Bayad', 'Oras')),
    'taglish': ('Cut off yung agency action sa source; hindi available yung continuation. Ito yung '
               'visible fields (original na wording): ', 'not printed',
               ('Client step', 'Agency action', 'Person in charge', 'Office', 'Fee', 'Processing time'))}


def cutoff_records(pack):
    """Evidence id -> exact safe excerpt, or None when the affected record is unusable."""
    records = {}
    for card in pack.cards:
        if card.kind != 'document':
            continue
        try:
            payload = json.loads(card.text)
            limits = payload.get('source_limits', [])
            matching = [s for s in limits if isinstance(s, dict)
                and s.get('issue') == 'source_cutoff' and s.get('resolution') == 'unresolved'
                and isinstance(s.get('field_names'), (list, str)) and 'agency_action' in s['field_names']]
        except (ValueError, TypeError, AttributeError):
            continue
        if not matching:
            continue
        records[card.evidence_id] = None
        fields = payload.get('fields')
        if (pack.language not in _WORDS or not isinstance(fields, list)
                or any(not isinstance(f, dict) or f.get('name') not in _NAMES for f in fields)
                or len({(c.version_id, c.byte_sha256) for c in card.citations}) != 1):
            continue
        by_name = {f['name']: f for f in fields}
        if (len(by_name) != len(fields) or not {'client_step', 'agency_action'} <= by_name.keys()
                or any(not isinstance(s['field_names'], list) or not s['field_names']
                       or any(not isinstance(n, str) or n not in by_name
                              for n in s['field_names']) for s in matching)):
            continue
        if any(not isinstance(f.get('value'), str) or type(f.get('source_blank')) is not bool
               or f['source_blank'] != (not f['value'].strip()) for f in fields):
            continue
        if any(by_name[n]['source_blank'] for n in ('client_step', 'agency_action')):
            continue
        prefix, blank, labels = _WORDS[pack.language]
        quoted = [label + ': ' + (blank if by_name[n]['source_blank'] else
                  json.dumps(by_name[n]['value'], ensure_ascii=False))
                  for n, label in zip(_NAMES, labels) if n in by_name]
        text = prefix + '; '.join(quoted)
        if len(text) <= 1200:
            records[card.evidence_id] = text
    return records


def cutoff_reply(pack, proposed, *, max_claims=8):
    """Replace each affected record once; None is unaffected, empty means source_gap."""
    records = cutoff_records(pack)
    if not any(set(c.evidence_ids).intersection(records) for c in proposed):
        return None
    claims, seen = [], set()
    for claim in proposed:
        affected = [ref for ref in claim.evidence_ids if ref in records]
        if not affected:
            claims.append(claim.model_dump(mode='json'))
        for ref in affected:
            if records[ref] is None:
                return ()
            if ref not in seen:
                claims.append(dict(text=records[ref], evidence_ids=[ref]))
                seen.add(ref)
    return tuple(claims) if len(claims) <= max_claims else ()


def cutoff_errors(pack, claims):
    """A positive model verdict cannot authorize a different rendering of these fields."""
    records = cutoff_records(pack)
    for claim in claims:
        for ref in set(claim.evidence_ids).intersection(records):
            if records[ref] is None or claim.text != records[ref] or tuple(claim.evidence_ids) != (ref,):
                return ('service_cutoff_fidelity',)
    return ()
