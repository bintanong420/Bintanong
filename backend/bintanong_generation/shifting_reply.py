"""Thesis leader, 4 Nov 2026: a shifting/changing-program answer ends by referring the student to the offices the
retrieved Handbook text prints for that step (4.1/4.2/4.3 and FAQ 8). Host wording, one office phrase per printed role,
only for roles found in the retrieved cards; Bintanong never evaluates credits or approves a shift."""
import json
import re

from ..bintanong_routing.topic_selection import SHIFT_TOPICS

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


def shifting_referral(pack):
    """One closing line naming the printed offices, or None when the question is not about shifting or no printed
    office is in the retrieved text."""
    if not asks_shifting(pack):
        return None
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
    found = [(en, tl) for key, pattern, en, tl in _OFFICES if re.search(pattern, text, re.IGNORECASE)
             and not (key == 'dean' and re.search(_OFFICES[0][1], text, re.IGNORECASE))]
    if not found:
        return None
    names = [tl if taglish else en for en, tl in found]
    joined = names[0] if len(names) == 1 else ', '.join(names[:-1]) + (' at ' if taglish else ' and ') + names[-1]
    return _WORDS['taglish' if taglish else 'en'].format(offices=joined)
