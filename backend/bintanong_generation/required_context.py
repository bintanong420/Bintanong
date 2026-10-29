"""Exact required source context; no interpretation of individual applicability."""
import json
import re

from .precedence_reply import precedence_sources


_ISSUES = {'claim_not_stated', 'printed_total_discrepancy'}
_OFFENSES = {'1st Offense', '2nd Offense', '3rd Offense', 'Subsequent Offenses'}
_WORDS = {
    'en': ('Reviewed source fields (quoted): ', 'Recorded source limitation: ',
           'Please confirm with the relevant university office.', 'unspecified'),
    'fil': ('Mga field sa reviewed source (original wording): ', 'Limitasyon sa source: ',
            'Pakitanong sa tamang opisina ng unibersidad.', 'hindi tinukoy'),
    'taglish': ('Ang reviewed source fields (quoted): ', 'Limit sa source: ',
                'Paki-confirm sa tamang university office.', 'unspecified')}


def _record(card):
    try:
        value = json.loads(card.text)
        return value if card.kind == 'document' and isinstance(value, dict) else None
    except (ValueError, TypeError):
        return None


def _quote(record, words):
    fields, limits = record.get('fields'), record.get('source_limits', [])
    if (not isinstance(fields, list) or not fields or not isinstance(limits, list)
            or any(not isinstance(v, dict) for v in limits)):
        return None
    names, quoted = set(), []
    for field in fields:
        if not isinstance(field, dict):
            return None
        name, value, blank = field.get('name'), field.get('value'), field.get('source_blank')
        if (not isinstance(name, str) or not name.strip() or name in names
                or not isinstance(value, str) or type(blank) is not bool or blank != (not value.strip())):
            return None
        names.add(name)
        quoted.append(name.replace('_',' ')+': '+(words[3] if blank else '"'+value+'"'))
    text = words[0]+'; '.join(quoted)
    for limit in limits:
        if limit.get('resolution') != 'unresolved':
            continue
        message = limit.get('message')
        if limit.get('issue') not in _ISSUES or not isinstance(message, str) or not message.strip():
            return None
        # Drop only the redundant machine issue label, retaining the specific recorded limitation.
        message = re.sub(r' Source limitation remains unresolved \([a-z_]+\)\.$', '', message)
        text += ' '+words[1]+'"'+message+'" '+words[2]
    return text if len(text) <= 1200 else None


def context_quotes(pack, required):
    """None when irrelevant; empty if unsafe; exact quotes keyed to required records otherwise."""
    owned = precedence_sources(pack)
    records = {c.evidence_id:(c,record) for c in pack.cards
        if c.evidence_id in required and (record := _record(c)) is not None}
    contexts = {ref for ref,(_,record) in records.items() if ref not in owned
        and isinstance(record.get('source_limits', []), list)
        and any(isinstance(v, dict) and v.get('resolution') == 'unresolved' and v.get('issue') in _ISSUES
                for v in record.get('source_limits', []))}
    # Printed penalty rows are always quoted exactly (owner 29 Oct 2026: keep the exact source); a shared
    # applicability gap also must not turn a paraphrase into an invented sanction condition.
    penalties = {ref for ref,(_,record) in records.items() if ref not in owned
        and isinstance(record.get('fields'), list)
        and any(v.get('name') == 'Cause' for v in record['fields'] if isinstance(v, dict))
        and any(isinstance(v.get('name'), str) and v['name'] in _OFFENSES
                for v in record['fields'] if isinstance(v, dict))}
    if not contexts and not penalties:
        return None
    if pack.language not in _WORDS:
        return ()
    identities = {(c.version_id,c.byte_sha256) for card in pack.cards if card.evidence_id in required
                  for c in card.citations}
    if len(identities) != 1:
        return ()
    result = []
    for ref in [*sorted(penalties-contexts), *sorted(contexts)]:
        card, record = records[ref]
        text = _quote(record, _WORDS[pack.language])
        if text is None:
            return ()
        result.append(dict(text=text,evidence_ids=[card.evidence_id]))
    return tuple(result)


def context_reply(pack, proposed, required, *, max_claims=8, existing_claims=()):
    quotes = context_quotes(pack, required)
    if not quotes:
        return quotes
    quoted = {ref for claim in quotes for ref in claim['evidence_ids']}
    independent = [dict(text=c.text,evidence_ids=list(c.evidence_ids)) for c in proposed
                   if not quoted.intersection(c.evidence_ids)]
    result = (*independent, *quotes)
    additional = {(c['text'],tuple(c['evidence_ids'])) for c in result}-set(existing_claims)
    return result if len(additional) <= max(0,max_claims) else ()


def context_errors(pack, claims, required):
    quotes = context_quotes(pack, required)
    if quotes is None:
        return ()
    actual = {(c.text,tuple(c.evidence_ids)) for c in claims}
    if not quotes or any((c['text'],tuple(c['evidence_ids'])) not in actual for c in quotes):
        return ('source_context_not_preserved',)
    return ()
