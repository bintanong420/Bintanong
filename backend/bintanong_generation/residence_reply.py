"""Owner 2 Nov 2026 (#2, option B): "how many years before I graduate" gets a program-length pointer (host wording,
no claim) and the Student Handbook's printed residence rule (1.4) quoted exactly from the retrieved card."""
import json
import re

from ..bintanong_routing.topic_selection import YEARS_TO_GRADUATE

_RULE = re.compile(r'1\.4 RESIDENCE REQUIREMENTS\.\s*(No student shall be graduated.*?immediately prior to graduation\.)',
                   re.DOTALL)
_TAGLISH = ('Depende sa ibig mong sabihin. Ang haba ng program mo ay nasa prospectus ng curriculum mo (piliin ang '
            'program mo para ma-check ko). Para maka-graduate sa PalSU, sabi ng Student Handbook:')
POINTER = {'en': 'It depends on what you mean. How long your program takes is in your curriculum\'s prospectus '
                 '(choose your program and I can check it). To graduate from PalSU, the Student Handbook says:',
           'fil': _TAGLISH, 'taglish': _TAGLISH}


def residence_reply(pack, part):
    """The quoted rule as one host claim, or None when the question or the printed rule is not there."""
    if part is None or part.subject_id != 'handbook_graduation' or not YEARS_TO_GRADUATE(part.text):
        return None
    for card in pack.cards:
        if card.kind != 'document':
            continue
        try:
            fields = json.loads(card.text)['fields']
        except (ValueError, TypeError, KeyError):
            continue
        for field in fields:
            found = _RULE.search(' '.join(str(field.get('value', '')).split()))
            if found and not field.get('source_blank'):
                # Taglish needs Filipino connecting words around the English quote (reply-style rule, live 2 Nov).
                text = (f'Ayon sa Student Handbook 1.4: "{found.group(1)}"' if pack.language in ('taglish', 'fil')
                        else f'"{found.group(1)}" (Student Handbook 1.4)')
                return (dict(text=text, evidence_ids=[card.evidence_id]),)
    return None


def asks_years_to_graduate(pack):
    return pack.understanding is not None and any(
        p.subject_id == 'handbook_graduation' and YEARS_TO_GRADUATE(p.text) for p in pack.understanding.parts)
