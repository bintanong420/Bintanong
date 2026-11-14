"""Quote complete reviewed conflict groups without choosing a controlling deadline."""
import json


_WORDS = {
    'en': ('The source contains conflicting timing statements and does not establish which deadline applies. '
           'Please confirm with the relevant university office. ', 'Printed statement (quoted): ', 'unspecified'),
    'fil': ('May magkaibang timing statements sa source; hindi malinaw kung aling deadline ang susundin. '
            'Pakitanong sa tamang opisina ng unibersidad. ', 'Naka-print na statement (sipi): ', 'hindi tinukoy'),
    'taglish': ('May conflicting timing statements sa source; hindi clear kung aling deadline ang applicable. '
                'Paki-confirm sa tamang university office. ', 'Ang printed statement (quoted): ', 'unspecified')}


def _conflict(card):
    if card.kind != 'document':
        return None
    try:
        record = json.loads(card.text)
        if any(isinstance(limit, dict) and limit.get('issue') == 'conflicting_deadlines'
               and limit.get('resolution') == 'unresolved'
               for limit in record.get('source_limits', [])):
            return record
    except (ValueError, TypeError, AttributeError):
        pass
    return None


def _group(record):
    group = record.get('service_group', {})
    name = group.get('logical_step_id') if isinstance(group, dict) else None
    return name if isinstance(name, str) and name.strip() else None


def _record(card):
    try:
        record = json.loads(card.text) if card.kind == 'document' else None
    except (ValueError, TypeError):
        return None
    return record if isinstance(record, dict) else None


def conflict_group_ids(pack):
    """Evidence ids quoted as one conflicting-statement group: a printed group of two or more parts whose every
    present record carries the conflict. Other conflicting records are quoted alone (owner 30 Oct 2026)."""
    members = {}
    for card in pack.cards:
        record = _record(card)
        if record is not None and _group(record) is not None:
            members.setdefault(_group(record), []).append((card, record))
    grouped = set()
    for group in members.values():
        counts = [r.get('service_group', {}).get('part_count') for _, r in group]
        if (all(type(c) is int and c >= 2 for c in counts)
                and all(_conflict(card) is not None for card, _ in group)):
            grouped.update(card.evidence_id for card, _ in group)
    return grouped


def _quotes(members, words):
    counts, orders, gaps, sources = set(), set(), set(), set()
    statements = []
    for card, record in members:
        group = record.get('service_group', {})
        count, order = group.get('part_count'), group.get('part_order')
        if type(count) is not int or not 2 <= count <= 8 or type(order) is not int or order in orders:
            return None
        counts.add(count); orders.add(order)
        raw_limits = record.get('source_limits', [])
        if not isinstance(raw_limits, list) or any(not isinstance(v, dict) for v in raw_limits):
            return None
        limits = [v for v in raw_limits if v.get('resolution') == 'unresolved']
        if (len(limits) != 1 or limits[0].get('issue') != 'conflicting_deadlines'
                or not isinstance(limits[0].get('gap_id'), str) or not limits[0]['gap_id'].strip()):
            return None
        gaps.add(limits[0]['gap_id'])
        identities = {(c.version_id, c.byte_sha256) for c in card.citations}
        if len(identities) != 1:
            return None
        sources.update(identities)
        fields = record.get('fields', [])
        if not isinstance(fields, list) or not fields:
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
            quoted.append(name+': '+(words[2] if blank else '"'+value+'"'))
        statements.append((order, words[1]+'; '.join(quoted), card.evidence_id))
    if (len(counts) != 1 or len(gaps) != 1 or len(sources) != 1
            or orders != set(range(next(iter(counts))))):
        return None
    return sorted(statements)


def _group_quotations(pack, records, groups):
    if pack.language not in _WORDS or None in groups:
        return ()
    quoted = []
    words = _WORDS[pack.language]
    for group in sorted(groups):
        statements = _quotes([records[ref] for ref in records if _group(records[ref][1]) == group], words)
        if statements is None:
            return ()
        for _, text, ref in statements:
            if not quoted:
                text = words[0]+text
            if len(text) > 1200:
                return ()
            if quoted and len(quoted[-1]['text'])+1+len(text) <= 1200:
                quoted[-1]['text'] += ' '+text
                quoted[-1]['evidence_ids'].append(ref)
            else:
                quoted.append(dict(text=text, evidence_ids=[ref]))
    return tuple(quoted)


def deadline_conflict_reply(pack, proposed, *, max_claims=8, existing_claims=()):
    """Quote affected groups before ordinary relevance/support review;never choose a deadline.
    A conflicting record outside a conflict group is quoted by malformed_condition.py (owner 30 Oct 2026)."""
    grouped = conflict_group_ids(pack)
    records = {c.evidence_id: (c, record) for c in pack.cards
               if c.evidence_id in grouped and (record := _conflict(c)) is not None}
    cited = {ref for claim in proposed for ref in claim.evidence_ids}
    touched = cited.intersection(records)
    if not touched:
        return None
    groups = {_group(records[ref][1]) for ref in touched}
    quoted = _group_quotations(pack, records, groups)
    if not quoted:
        return ()
    affected = {ref for ref, (_, record) in records.items() if _group(record) in groups}
    independent = [dict(text=c.text, evidence_ids=list(c.evidence_ids)) for c in proposed
                   if not affected.intersection(c.evidence_ids)]
    result = (*quoted, *independent)
    additional = {(c['text'], tuple(c['evidence_ids'])) for c in result} - set(existing_claims)
    return result if len(additional) <= max(0, max_claims) else ()


def unresolved_deadline_context(pack):
    """Literal explanatory context for one withheld gap;never an answered policy decision."""
    parts = pack.understanding.parts if pack.understanding else ()
    if (pack.status != 'no_evidence' or pack.route != 'RAG' or len(parts) != 1
            or parts[0].evidence_need != 'document' or not parts[0].requested_claims
            or pack.decision is not None or pack.dependencies is not None):
        return None
    requested = set(parts[0].requested_claims)
    records = {c.evidence_id:(c,record) for c in pack.cards if (record := _conflict(c)) is not None}
    matching = set()
    for ref,(_,record) in records.items():
        for limit in record.get('source_limits', []):
            affected = limit.get('affected_claims') if isinstance(limit, dict) else None
            if (isinstance(affected, list) and all(isinstance(v,str) for v in affected)
                    and limit.get('issue') == 'conflicting_deadlines'
                    and limit.get('resolution') == 'unresolved' and requested <= set(affected)):
                matching.add(ref)
    groups = {_group(records[ref][1]) for ref in matching}
    if len(groups) != 1:
        return None
    quotes = _group_quotations(pack, records, groups)
    return quotes if len(quotes) <= 8 else ()
