"""Quote a record with an unresolved malformed condition instead of interpreting it.

Owner 30 Oct 2026: answer the visible content and state the limitation. Only explicit
unresolved malformed_source_condition metadata, or conflicting_deadlines on a record outside
any printed group (grouped conflicts are quoted by deadline_conflict.py), activates this rule. The quotation is the
record's exact nonblank field wording, its recorded limitation and an office referral;
the host never explains, completes or reconciles the malformed wording.
"""
import json


_TAGLISH = ('May unresolved na limitation ang part na ito ng printed source{limits}, kaya quoted lang ito at '
            'hindi ini-interpret: {quoted} Paki-confirm sa relevant university office.')
_WORDS = {
    'en': ('This part of the printed source has an unresolved limitation{limits}, so it is quoted without '
           'interpretation: {quoted} Please confirm with the relevant university office.'),
    'fil': _TAGLISH,  # Filipino input receives a Taglish reply (owner 27 Oct 2026)
    'taglish': _TAGLISH}
MAX_TEXT = 1200


def _grouped(payload):
    group = payload.get('service_group')
    name = group.get('logical_step_id') if isinstance(group, dict) else None
    return isinstance(name, str) and bool(name.strip())


def malformed_records(pack):
    """Evidence id -> exact quotation, or None when the held record cannot be quoted safely."""
    records = {}
    for card in pack.cards:
        if card.kind != 'document':
            continue
        try:
            payload = json.loads(card.text)
            limits = payload.get('source_limits', [])
            held = ('malformed_source_condition',) + (() if _grouped(payload) else ('conflicting_deadlines',))
            matching = [s for s in limits if isinstance(s, dict)
                        and s.get('issue') in held and s.get('resolution') == 'unresolved']
        except (ValueError, TypeError, AttributeError):
            continue
        if not matching:
            continue
        records[card.evidence_id] = None
        fields = payload.get('fields')
        if (pack.language not in _WORDS or not isinstance(fields, list) or not fields
                or any(not isinstance(f, dict) or not isinstance(f.get('value'), str)
                       or type(f.get('source_blank')) is not bool or f['source_blank'] != (not f['value'].strip())
                       for f in fields)
                or len({(c.version_id, c.byte_sha256) for c in card.citations}) != 1):
            continue
        visible = [f for f in fields if not f['source_blank']]
        # One field quotes alone; several keep their printed field names, as precedence/deadline quotes do.
        quoted = '; '.join((f'{f["name"]}: ' if len(visible) > 1 else '')
                           + json.dumps(f['value'].strip(), ensure_ascii=False) for f in visible)
        affected = [a for s in matching for a in (s.get('affected_claims') or ()) if isinstance(a, str) and a.strip()]
        if not quoted:
            continue
        text = _WORDS[pack.language].format(limits=' ('+'; '.join(dict.fromkeys(affected))+')' if affected else '',
                                            quoted=quoted)
        if len(text) <= MAX_TEXT:
            records[card.evidence_id] = text
    return records


def malformed_reply(pack, proposed, *, max_claims=8):
    """Replace each held record once; None is unaffected, empty means source_gap."""
    records = malformed_records(pack)
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


def malformed_errors(pack, claims):
    """A positive model verdict cannot authorize any other wording attached to a held record."""
    records = malformed_records(pack)
    for claim in claims:
        for ref in set(claim.evidence_ids).intersection(records):
            if records[ref] is None or claim.text != records[ref] or tuple(claim.evidence_ids) != (ref,):
                return ('malformed_source_fidelity',)
    return ()
