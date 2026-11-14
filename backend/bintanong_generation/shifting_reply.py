"""Thesis leader, 4 Nov 2026: a shifting/changing-program answer ends by referring the student to the offices the
retrieved Handbook text prints for that step (4.1/4.2/4.3 and FAQ 8). Host wording, one office phrase per printed role,
only for roles found in the retrieved cards; Bintanong never evaluates credits or approves a shift."""
import json
import re

from ..bintanong_routing.topic_selection import SHIFT, SHIFT_TOPICS


def generic_program_shifting(part):
    return (part.subject_id in SHIFT_TOPICS and part.detail == 'whole' and SHIFT.search(part.text)
            and not re.search(r'\b(?:college|kolehiyo|department|departamento)\b', part.text, re.I))


def complete_program_shifting_reply(pack, part, required):
    """Keep both printed college branches for a program change whose destination is unspecified."""
    if part is None or not generic_program_shifting(part) or not required:
        return None
    records = [card for card in pack.cards if card.kind == 'document' and card.evidence_id in required]
    if len(records) > 8 or {card.evidence_id for card in records} != set(required):
        return None
    reply, policy = [], False
    lead = 'Ayon sa Handbook: ' if pack.language in ('fil', 'taglish') else 'The Handbook states: '
    for card in records:
        try:
            record = json.loads(card.text)
            fields, limits = record['fields'], record['source_limits']
            if (len(fields) != 1 or fields[0].get('name') != 'body' or fields[0].get('source_blank') is not False
                    or not isinstance(limits, list) or any(not isinstance(limit, dict)
                        or limit.get('resolution') != 'resolved' for limit in limits)):
                return None
            body = fields[0]['value']
            if not isinstance(body, str) or not body.strip() or len(lead + body) + 2 > 1200:
                return None
            policy |= bool(re.search(r'\bREQUEST TO SHIFT TO ANOTHER COLLEGE\b', body, re.I)
                           and re.search(r'\bREQUEST TO SHIFT WITHIN THE SAME COLLEGE\b', body, re.I))
            reply.append(dict(text=lead + '"' + body + '"', evidence_ids=[card.evidence_id]))
        except (ValueError, TypeError, KeyError, AttributeError):
            return None
    return tuple(reply) if policy else None

# printed role -> (pattern in the retrieved text, English phrase, Taglish phrase)
_OFFICES = (
    ('deans', r'Dean of the College where he intends to shift', 'the Deans of your current college and the college you want to shift to',
     'ang Deans ng current college mo at ng college na gusto mong lipatan'),
    ('dean', r'\bDean\b', 'your College Dean', 'ang College Dean mo'),
    ('head', r'Department Head', 'the Department Head of your course', 'ang Department Head ng course mo'),
    ('guidance', r'Guidance Practitioner', 'the College Guidance Practitioner', 'ang College Guidance Practitioner'),
    ('registrar', r'\bregistrar', 'the Office of the University Registrar', 'ang Office of the University Registrar'))
_WORDS = {'en': 'To shift, take your request to {offices}, as the Handbook prints. Bintanong cannot evaluate your '
                'credits or approve a shift; those offices decide.',
          'taglish': 'Para mag-shift, dalhin ang request mo sa {offices}, ayon sa naka-print sa Handbook. Hindi kayang '
                     'i-evaluate ng Bintanong ang credits mo o aprubahan ang shift; ang mga office na ito ang magpapasya.'}


def asks_shifting(pack):
    return pack.understanding is not None and any(p.subject_id in SHIFT_TOPICS for p in pack.understanding.parts)


def shifting_referral(pack, claims=()):
    """One closing line naming the printed offices, or None when the question is not about shifting or no printed
    office is in the retrieved text."""
    if not asks_shifting(pack):
        return None
    stated = {(claim.text, tuple(claim.evidence_ids)) for claim in claims}
    for part in pack.understanding.parts:
        required = {ref for subject, claim, refs in pack.record_coverage
                    if SHIFT_TOPICS.get(subject) == claim for ref in refs}
        complete = complete_program_shifting_reply(pack, part, required)
        if complete and {(item['text'], tuple(item['evidence_ids'])) for item in complete} <= stated:
            return ('Dalhin ang request mo sa mga office na nabanggit sa applicable process. Hindi kayang '
                    'i-evaluate ng Bintanong ang credits mo o aprubahan ang shift.'
                    if pack.language in ('fil', 'taglish') else
                    'Take your request to the offices named above for the applicable process. '
                    'Bintanong cannot evaluate your credits or approve a shift.')
    text = ''
    for card in pack.cards:
        if card.kind != 'document':
            continue
        try:
            fields = json.loads(card.text)['fields']
        except (ValueError, TypeError, KeyError):
            continue
        text += ' '.join(str(f.get('value', '')) for f in fields if not f.get('source_blank')) + ' '
    taglish = pack.language in ('taglish', 'fil')
    found = [(key, en, tl) for key, pattern, en, tl in _OFFICES if re.search(pattern, text, re.IGNORECASE)
             and not (key == 'dean' and re.search(_OFFICES[0][1], text, re.IGNORECASE))]
    if not found:
        return None
    conditional = (any(generic_program_shifting(part) for part in pack.understanding.parts)
                   and re.search(r'\bREQUEST TO SHIFT WITHIN THE SAME COLLEGE\b', text, re.I))
    names = []
    for key, en, tl in found:
        name = tl.removeprefix('ang ') if taglish else en
        if conditional and key == 'deans':
            name += ' (kung ibang college ang lilipatan)' if taglish else ' (if moving to another college)'
        elif conditional and key == 'head':
            name += ' (kung same college ang lilipatan)' if taglish else ' (if staying within the same college)'
        names.append(name)
    joined = names[0] if len(names) == 1 else ', '.join(names[:-1]) + (' at ' if taglish else ' and ') + names[-1]
    return _WORDS['taglish' if taglish else 'en'].format(offices=joined)
