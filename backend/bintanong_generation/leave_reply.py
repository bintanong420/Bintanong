"""Owner 2 Nov 2026: "how long can a leave of absence be" leads with the printed limit, quoted, then quotes the printed
rule. Live, a draft that buried "one (1) academic year" mid-sentence was rejected on some runs. Both quotes come from
the retrieved card; a missing rule or a maternity-leave question leaves the answer to the draft."""
import json
import re

_ASKS = re.compile(r'how\s+long|gaano\s+(ka)?tagal|how\s+many\s+(days|months|years|semesters)|'
                   r'ilang\s+(araw|buwan|taon|semester)|maximum|pinakamatagal', re.IGNORECASE)
_RULE = re.compile(r'Leave of absence shall be applied.*?approval by the Dean\.')
_LIMIT = re.compile(r'the period which must not exceed [^,.]+')
_WORDS = {'en': ('The Student Handbook says a leave of absence application indicates "{limit}".',
                 'The full printed rule: "{rule}"'),
          'taglish': ('Ayon sa Student Handbook, ang leave of absence application ay nagsasabi ng "{limit}".',
                      'Ang buong printed rule: "{rule}"')}


def leave_reply(pack, part):
    if (part is None or part.subject_id != 'handbook_leave' or not _ASKS.search(part.text)
            or 'maternity' in part.text.casefold()):
        return None
    for card in pack.cards:
        if card.kind != 'document':
            continue
        try:
            fields = json.loads(card.text)['fields']
        except (ValueError, TypeError, KeyError):
            continue
        for field in fields:
            rule = _RULE.search(' '.join(str(field.get('value', '')).split()))
            limit = rule and _LIMIT.search(rule.group(0))
            if rule and limit and not field.get('source_blank'):
                first, second = _WORDS['taglish' if pack.language in ('taglish', 'fil') else 'en']
                return (dict(text=first.format(limit=limit.group(0)), evidence_ids=[card.evidence_id]),
                        dict(text=second.format(rule=rule.group(0)), evidence_ids=[card.evidence_id]))
    return None
