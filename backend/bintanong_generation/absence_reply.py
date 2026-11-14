"""Owner 2 Nov 2026 (#3, p or q): an absence answer leads with the excuse-slip rule (attendance) and then gives the
"if you were sick" branch, quoted exactly from the retrieved sickness record. Live, the draft gave only the excuse slip."""
import json
import re

from ..bintanong_routing.topic_selection import ABSENCE

_SICK = re.compile(r'Certificate of sickness will be issued only.*?attending physicians\.')
_LEAD = {'en': 'If you were sick: "{quote}"', 'taglish': 'Kung may sakit ka: "{quote}"'}


def sickness_branch(pack, part, claims):
    """One host claim to append, or None when the part is not about an absence, the sickness record is missing, or
    the answer already cites it."""
    if part is None or part.subject_id != 'handbook_attendance' or not ABSENCE.search(part.text):
        return None
    cited = {ref for claim in claims for ref in claim.evidence_ids}
    for card in pack.cards:
        if card.kind != 'document':
            continue
        try:
            fields = json.loads(card.text)['fields']
        except (ValueError, TypeError, KeyError):
            continue
        for field in fields:
            found = _SICK.search(' '.join(str(field.get('value', '')).split()))
            if found and not field.get('source_blank'):
                if card.evidence_id in cited:
                    return None
                lead = _LEAD['taglish' if pack.language in ('taglish', 'fil') else 'en']
                return dict(text=lead.format(quote=found.group(0)), evidence_ids=[card.evidence_id])
    return None
