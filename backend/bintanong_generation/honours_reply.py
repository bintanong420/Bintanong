"""Owner 2 Nov 2026 (#5): "how long ... to graduate with Latin honors" covers Student Handbook 5.1.3 (residence and
units) and 5.1.4 (academic load) in full. Both are quoted exactly from the retrieved cards; a 5.1.4 continuation on
the next record is kept. Any missing section leaves the question to the draft."""
import json
import re

_ASKS = re.compile(r'(how\s+long|how\s+many\s+years|ilang\s+taon|gaano\s+(ka)?tagal)', re.IGNORECASE)
_HONOURS = re.compile(r'honou?rs|latin|laude', re.IGNORECASE)
_RESIDENCE = re.compile(r'5\.1\.3 RESIDENCE AND UNIT REQUIREMENTS\..*?(?=\s*5\.1\.4|$)', re.DOTALL)
_LOAD = re.compile(r'5\.1\.4 MINIMUM ACADEMIC LOAD REQUIREMENT\..*?(?=\s*5\.1\.5|$)', re.DOTALL)
_CONTINUED = re.compile(r'^(It shall be the responsibility of the student to establish the veracity of the cause for '
                        r'under load.*?\.)(?=\s|$)', re.DOTALL)
_LEAD = {'en': 'To graduate with Latin honors, the Student Handbook (5.1.3 and 5.1.4) requires the following, '
               'quoted exactly:',
         'taglish': 'Para maka-graduate with Latin honors, ito ang nakalista sa Student Handbook (5.1.3 at 5.1.4):'}


def _bodies(pack):
    for card in pack.cards:
        if card.kind != 'document':
            continue
        try:
            fields = json.loads(card.text)['fields']
        except (ValueError, TypeError, KeyError):
            continue
        for field in fields:
            if not field.get('source_blank') and isinstance(field.get('value'), str):
                yield card.evidence_id, ' '.join(field['value'].split())


def honours_reply(pack, part):
    if (part is None or part.subject_id != 'handbook_undergraduate_honors_policy'
            or not (_ASKS.search(part.text) and _HONOURS.search(part.text))):
        return None
    bodies = list(_bodies(pack))
    residence = next(((e, m.group(0)) for e, b in bodies if (m := _RESIDENCE.search(b))), None)
    load = next(((e, m.group(0)) for e, b in bodies if (m := _LOAD.search(b))), None)
    if residence is None or load is None:
        return None
    rest = next(((e, m.group(1)) for e, b in bodies if (m := _CONTINUED.search(b))), None)
    load_text, load_ids = load[1], [load[0]]
    if rest is not None and load[1].rstrip().endswith('.') and rest[0] != load[0]:
        load_text, load_ids = f'{load[1]} {rest[1]}', [load[0], rest[0]]
    lead = _LEAD['taglish' if pack.language in ('taglish', 'fil') else 'en']
    return (dict(text=lead, evidence_ids=[residence[0]]),
            dict(text=f'"{residence[1]}"', evidence_ids=[residence[0]]),
            dict(text=f'"{load_text}"', evidence_ids=load_ids))
