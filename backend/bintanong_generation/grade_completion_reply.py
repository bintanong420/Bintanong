"""Exact mark-specific method quotations with shared source limitations stated once."""
import json
import re


def concise_mark_reply(pack, part, required):
    if part is None or part.subject_id != 'grade_completion' or part.detail != 'whole':
        return None
    inc = bool(re.search(r'\b(?:inc|incomplete)\b', part.text, re.I))
    four = bool(re.search(r'(?<![\w.])4(?:\.0)?(?![\w.])', part.text))
    if inc == four:
        return None
    method, approval, context, limits, limit_refs = [], [], [], [], []
    conflict = False
    mark = 'INC' if inc else r'4(?:\.0)?'
    for card in pack.cards:
        if card.kind != 'document' or card.evidence_id not in required:
            continue
        try:
            record = json.loads(card.text)
            fields, notes = record['fields'], record['source_limits']
            if (not isinstance(notes, list) or any(not isinstance(n, dict) for n in notes)
                    or len(fields) != 1 or fields[0]['name'] != 'body'
                    or fields[0]['source_blank'] is not False or not isinstance(fields[0]['value'], str)):
                return None
            body = fields[0]['value'].strip()
            if re.search(r'\bREMOVAL\s+OF\s+[“‘"\']?' + mark + r'(?![\w.])', body, re.I):
                if inc:
                    found = re.search(r'\bRemoval of (?:the )?INC must\b.+\.$', body, re.S | re.I)
                    if found is None:
                        return None
                    body = found.group(0)
                else:
                    body = re.split(r'\s+\d+(?:\.\d+)*\s+NO IMPROVEMENT OF GRADE\.', body, maxsplit=1)[0]
                method.append((body, card.evidence_id))
            elif re.search(r'\bEXAMINATION FOR REMOVAL OR COMPLETION\b', body, re.I):
                approval.append((body, card.evidence_id))
            elif re.search(r'\bAPPROVAL OF THE REQUEST\b', body, re.I):
                context.append((body, card.evidence_id))
            for note in notes:
                if note.get('resolution') != 'unresolved':
                    continue
                if note.get('issue') not in ('conflicting_deadlines', 'claim_not_stated'):
                    return None
                affected = note.get('affected_claims')
                if not isinstance(affected, list) or not affected or any(not isinstance(v, str) for v in affected):
                    return None
                message = note.get('message')
                if message is not None and (not isinstance(message, str) or not message.strip()):
                    return None
                if message:
                    message = re.sub(r'^Unavailable information:\s*', '', message.strip())
                    message = re.sub(r'\s*Source limitation remains unresolved \([a-z_]+\)\.$', '', message).rstrip('. ')
                limits.extend([message] if message else affected)
                limit_refs.append(card.evidence_id)
                conflict |= note['issue'] == 'conflicting_deadlines'
        except (ValueError, TypeError, KeyError, AttributeError):
            return None
    if len(method) != 1 or len(approval) != 1 or len(context) > 1:
        return None
    taglish = pack.language in ('fil', 'taglish')
    lead = 'Ayon sa source: ' if taglish else 'The source states: '
    claims = [dict(text=lead + '"' + body + '"', evidence_ids=[ref])
              for body, ref in method + approval + context]
    if limits:
        notice = ('May conflicting completion deadlines; hindi settled sa source kung alin ang applicable. '
                  if taglish else 'Completion deadlines conflict; the source does not settle which applies. ') if conflict else ''
        notice += ('Source limitations: ' + '; '.join(dict.fromkeys(limits)) + '. ')
        notice += 'Paki-confirm sa relevant university office.' if taglish else 'Please confirm with the relevant university office.'
        claims.append(dict(text=notice, evidence_ids=list(dict.fromkeys(limit_refs))))
    if any(len(c['text']) > 1200 or len(c['evidence_ids']) > 8 for c in claims):
        return None
    return tuple(claims)


def concise_mark_claims(pack):
    """Only the exact canonical quotations computed from this request's reviewed record binding."""
    claims = set()
    for part in (pack.understanding.parts if pack.understanding else ()):
        required = {ref for subject, claim, refs in pack.record_coverage
                    if subject == part.subject_id and claim in part.requested_claims for ref in refs}
        for item in concise_mark_reply(pack, part, required) or ():
            claims.add((item['text'], tuple(item['evidence_ids'])))
    return claims
