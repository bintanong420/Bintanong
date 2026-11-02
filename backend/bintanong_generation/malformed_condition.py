"""Quote a record with an unresolved malformed condition instead of interpreting it.

Owner 30 Oct 2026: answer the visible content and state the limitation. Only explicit
unresolved malformed_source_condition metadata, or conflicting_deadlines on a record outside
a conflict group (those are quoted together by deadline_conflict.py), activates this rule. The quotation is the
record's exact nonblank field wording, its recorded limitation and an office referral;
the host never explains, completes or reconciles the malformed wording.
"""
import json
import re

from .deadline_conflict import conflict_group_ids


# Printed text first, then the limitation: a leading limitation notice made the real INC review judge the
# quotation as no answer (replayed 30 Oct 2026); the limitation and referral stay in every quotation.
# Owner 2 Nov 2026 (9A): plain field labels, a heading and a "Heads-up" line, printed values unchanged.
_TAGLISH = dict(heading='Ito yung nakalista sa {doc}{office}:',
                note='Heads-up: hindi malinaw sa source ito: {limits}. Paki-confirm muna sa {referral} bago ka pumunta.',
                generic='may unresolved na limitation ang part na ito', referral='relevant university office',
                you='ikaw', where='Saan kukunin')
_WORDS = {
    'en': dict(heading="Here's what the {doc} lists{office}:",
               note="Heads-up: the source doesn't settle this part: {limits}. Please confirm with {referral} before you go.",
               generic='this part has an unresolved source limitation', referral='the relevant university office',
               you='you', where='Where to secure'),
    'fil': _TAGLISH,  # Filipino input receives a Taglish reply (owner 27 Oct 2026)
    'taglish': _TAGLISH}
_STEP = re.compile(r'step(\d+)_(?:subaction\d+_)?(client_step|action|fee|time|person|office)$')
_STEP_LABELS = dict(action='Step {n}, office', fee='Step {n} fee', time='Step {n} processing time',
                    person='Step {n} person in charge', office='Step {n} office')
MAX_TEXT = 1200


def _label(name, words):
    step = _STEP.match(name)
    if step:
        n, kind = step.groups()
        return f'Step {n}, {words["you"]}' if kind == 'client_step' else _STEP_LABELS[kind].format(n=n)
    if re.fullmatch(r'requirement\d*', name):
        return 'Requirements'
    if re.fullmatch(r'where_to_secure\d*', name):
        return words['where']
    return name.replace('_', ' ').capitalize()


def quoted_lines(fields, language):
    """Each printed field as '- Label: "exact value"'; column headings and blank cells are left out."""
    words = _WORDS.get(language, _WORDS['en'])
    return [f'- {_label(f["name"], words)}: ' + json.dumps(f['value'].strip(), ensure_ascii=False)
            for f in fields if not f['source_blank'] and not f['name'].endswith(('_label', '_labels'))]


def _document(card):
    name = card.citations[0].filename or ''
    return "Citizen's Charter" if 'Charter' in name else 'Student Handbook' if 'Handbook' in name else 'printed source'


def _office(pack, payload):
    """The office printed in the same service's records (owner 25 Oct 2026); otherwise None."""
    step = (payload.get('service_group') or {}).get('logical_step_id')
    if not step:
        return None
    for card in pack.cards:
        try:
            other = json.loads(card.text)
            if (other.get('service_group') or {}).get('logical_step_id') != step:
                continue
            office = {f['name']: f for f in other.get('fields', [])}.get('office')
            if office and not office.get('source_blank') and office.get('value', '').strip():
                return office['value'].strip()
        except (ValueError, TypeError, AttributeError):
            continue
    return None


def clean_quote(card, language):
    """A record cited beside a held one, quoted exactly so its content is not lost (owner 2 Nov 2026, 9A)."""
    try:
        payload = json.loads(card.text)
        fields = payload['fields']
        if (not isinstance(fields, list) or any(not isinstance(f, dict) or not isinstance(f.get('value'), str)
                or type(f.get('source_blank')) is not bool for f in fields)):
            return None
        lines = quoted_lines(fields, language)
        text = '\n'.join(lines) if len(lines) > 1 else (lines[0].split(': ', 1)[1] if lines else '')
    except (ValueError, TypeError, AttributeError, KeyError):
        text = json.dumps(card.text.strip(), ensure_ascii=False)
    return text if text and len(text) <= MAX_TEXT else None


def malformed_records(pack):
    """Evidence id -> exact quotation, or None when the held record cannot be quoted safely."""
    records = {}
    grouped = conflict_group_ids(pack)
    for card in pack.cards:
        if card.kind != 'document':
            continue
        try:
            payload = json.loads(card.text)
            limits = payload.get('source_limits', [])
            held = ('malformed_source_condition',) + (() if card.evidence_id in grouped else ('conflicting_deadlines',))
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
        lines = quoted_lines(fields, pack.language)
        affected = [a for s in matching for a in (s.get('affected_claims') or ()) if isinstance(a, str) and a.strip()]
        if not lines:
            continue
        words = _WORDS[pack.language]
        office = _office(pack, payload)
        # One field quotes alone after the heading; several are listed with plain labels.
        body = lines[0].split(': ', 1)[1] if len(lines) == 1 else '\n'.join(lines)
        text = '\n'.join((words['heading'].format(doc=_document(card), office=f' ({office})' if office else ''),
                          body, words['note'].format(limits='; '.join(dict.fromkeys(affected)) if affected
                                                     else words['generic'], referral=office or words['referral'])))
        if len(text) <= MAX_TEXT:
            records[card.evidence_id] = text
    return records


def malformed_reply(pack, proposed, *, max_claims=8):
    """Replace each held record once; None is unaffected, empty means source_gap."""
    records = malformed_records(pack)
    if not any(set(c.evidence_ids).intersection(records) for c in proposed):
        return None
    cards = {c.evidence_id: c for c in pack.cards}
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
        # Owner 2 Nov 2026 (9A): clean records the replaced claim also cited are quoted, not dropped.
        for ref in claim.evidence_ids if affected else ():
            if ref not in records and ref not in seen and ref in cards and cards[ref].kind == 'document':
                quote = clean_quote(cards[ref], pack.language)
                if quote is not None:
                    claims.append(dict(text=quote, evidence_ids=[ref]))
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
