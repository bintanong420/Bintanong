"""Owner 2 Nov 2026 (#10, "CC-first, with transparency"): for the recorded overdue-fine conflict, the Citizen's
Charter 2025 fee is answered first (RA 11032 Sec. 6 and 21(c): the Charter states the collectible fee) and the older
Student Handbook (2021) figure is quoted beside it with a Library referral. Only the recorded H101/C79 limitation
activates this; both amounts are copied from the retrieved cards, never stored here. Any missing piece keeps the
earlier behaviour (no answer)."""
import json
import re

HELD = 'H101/C79 overdue fine applicability and precedence unresolved'
_CHARTER_FINE = re.compile(r'Php\s*[\d,]+\.\d{2}/day')
_HANDBOOK_FINE = re.compile(r'General Circulation Books\s*[–-]\s*Php\s*[\d,]+\.\d{2}/day')
_TAGLISH = ("Ang overdue fine ay {fine}, ayon sa Citizen's Charter 2025 (University Library, Returning of Books).",
            'Heads-up: sa mas lumang Student Handbook (2021), "{handbook}" ang nakalista, at walang naka-print na '
            'amount para sa Reserved Books. Paki-confirm sa University Library.')
_WORDS = {
    'en': ("The overdue fine is {fine}, per the Citizen's Charter 2025 (University Library, Returning of Books).",
           'Heads-up: the older Student Handbook (2021) lists "{handbook}" and doesn\'t print the Reserved Books '
           'amount. Please confirm with the University Library.'),
    'fil': _TAGLISH, 'taglish': _TAGLISH}


def _fields(card):
    try:
        value = json.loads(card.text)
        return {f['name']: f['value'] for f in value['fields'] if not f.get('source_blank')}, value.get('source_limits') or []
    except (ValueError, TypeError, KeyError, AttributeError):
        return {}, []


def fee_precedence_reply(pack, part):
    """None when unaffected; otherwise the Charter-fee claim and the Handbook disclosure claim."""
    if part is None or HELD not in part.requested_claims or pack.language not in _WORDS:
        return None
    charter = handbook = None
    for card in pack.cards:
        if card.kind != 'document':
            continue
        fields, _ = _fields(card)
        # The H101/C79 note itself is owner-resolved (evidence.OWNER_RESOLVED_LIMITS) and removed from the card,
        # so the Charter record is recognised by its printed fee field and edition; the part's request gates this.
        fine = _CHARTER_FINE.search(fields.get('step2_fee', ''))
        if fine and 'Charter-2025' in (card.citations[0].filename or ''):
            charter = (card.evidence_id, fine.group(0))
        printed = _HANDBOOK_FINE.search(fields.get('body', ''))
        if printed and 'FINES' in fields.get('body', ''):
            handbook = (card.evidence_id, printed.group(0))
    if charter is None or handbook is None:
        return None
    fine, note = _WORDS[pack.language]
    return (dict(text=fine.format(fine=charter[1]), evidence_ids=[charter[0]]),
            dict(text=note.format(handbook=handbook[1]), evidence_ids=[handbook[0]]))
