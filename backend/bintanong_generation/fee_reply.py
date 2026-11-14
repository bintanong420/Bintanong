"""Owner, 24 Oct 2026 ("Rate + example"): a special class fee question gets one host-written reply in
every language. The printed rate and printed example are copied from the reviewed fields, never computed;
the student's own charge is not stated, so the reply refers them to the office. F04 stays held."""
import json
import re

SUBJECT = 'special_class_fees'
RATE_FIELDS = ('printed_rate_php_per_hour',)
EXAMPLE_FIELDS = ('lecture_units', 'lecture_hours', 'amount_php_as_printed')

_TEXT = {
 'en': ('The printed special class rate is PHP {printed_rate_php_per_hour} per hour.',
        'The printed example is a {lecture_units}-lecture-unit class of {lecture_hours} hours: '
        'PHP {amount_php_as_printed}.',
        'Your own charge is not stated in the source. Please ask the right university office.'),
 'fil': ('Ang naka-print na rate ng special class ay PHP {printed_rate_php_per_hour} kada oras.',
         'Ang naka-print na halimbawa ay klase na may {lecture_units} lecture units at {lecture_hours} oras: '
         'PHP {amount_php_as_printed}.',
         'Hindi nakasulat sa source kung magkano ang babayaran mo mismo. '
         'Pakitanong sa tamang opisina ng unibersidad.'),
 'taglish': ('Ang printed rate ng special class ay PHP {printed_rate_php_per_hour} per hour.',
             'Ang printed example ay class na {lecture_units} lecture units at {lecture_hours} hours: '
             'PHP {amount_php_as_printed}.',
             'Hindi naka-state sa source kung magkano ang babayaran mo mismo. '
             'Paki-ask sa tamang university office.')}


# Owner, 25 Oct 2026 (roster 18, accepted T2): asking whether the fee still applies (now or for a school year) gets
# the memo's printed date, "cannot confirm" and the office referral, never the rate. The date is bound to the
# reviewed memo version (F0, visibly dated 4 August 2023, intake report 15 Oct 2026); another version gets no date.
MEMO_DATES = {'ver-d35323d042e730038f6cc0401d2c294654f8158c68d86a6e17308df80ff5bf94': '4 August 2023'}
CURRENCY = re.compile(r"\b(?:(?:19|20)\d{2}|still|in effect|effective|valid|validity|current|currently|applicable|"
                      r"applies|bisa|ngayon|ngayong|this year|updated|latest)\b", re.I)
_CURRENCY_TEXT = {
 'en': ("The special class fee in Bintanong's reviewed sources comes from a memo dated {date}.",
        'Bintanong cannot confirm whether it still applies now or for the school year you asked about. '
        'Please ask the right university office.'),
 'fil': ('Ang special class fee sa mga na-review na source ng Bintanong ay galing sa memo na may petsang {date}.',
         'Hindi makumpirma ng Bintanong kung may bisa pa ito ngayon o sa school year na tinanong mo. '
         'Pakitanong sa tamang opisina ng unibersidad.'),
 'taglish': ('Yung special class fee sa reviewed sources ng Bintanong ay galing sa memo na dated {date}.',
             'Hindi ma-confirm ng Bintanong kung valid pa ito ngayon o sa school year na tinanong mo. '
             'Paki-ask sa tamang university office.')}

_EFFECTIVITY_TEXT = {
 'en': 'The source states effectivity as "{effectivity}"; Bintanong cannot confirm that it still applies now.',
 'fil': 'Ang effectivity na nakalagay sa source ay "{effectivity}"; hindi makumpirma kung may bisa pa ito ngayon.',
 'taglish': 'Ang printed effectivity ay "{effectivity}"; hindi ma-confirm kung valid pa ito ngayon.'}


def _currency_claims(language, rate):
    dated, referral = _CURRENCY_TEXT[language]
    date = MEMO_DATES.get(rate.citations[0].version_id) if rate.citations else None
    return tuple((text, rate.evidence_id) for text in ((dated.format(date=date),) if date else ()) + (referral,))


def _printed_fields(card):
    try:
        fields = json.loads(card.text).get('fields', [])
        return {f['name']: f['value'] for f in fields if not f.get('source_blank') and f.get('value')}
    except (ValueError, TypeError, AttributeError, KeyError):
        return {}


def _card_with(pack, names):
    for card in pack.cards:
        fields = _printed_fields(card)
        if card.kind == 'document' and all(n in fields for n in names):
            return card, fields
    return None, {}


def fee_claims(pack):
    """{part_id: ((text, evidence_id), ...)} for each special-class-fee document part when both printed
    cards are present; empty otherwise (the model then explains the part as before)."""
    parts = [p for p in (pack.understanding.parts if pack.understanding else ())
             if p.evidence_need == 'document' and p.subject_id == SUBJECT]
    if not parts or pack.language not in _TEXT:
        return {}
    rate, rate_fields = _card_with(pack, RATE_FIELDS)
    example, example_fields = _card_with(pack, EXAMPLE_FIELDS)
    if rate is None or example is None:
        return {}
    values = {**rate_fields, **example_fields}
    claims = tuple((text.format(**values), card.evidence_id)
                   for text, card in zip(_TEXT[pack.language], (rate, example, example)))
    effectivity, fields = _card_with(pack, ('printed_effectivity',))
    if (effectivity is not None and effectivity.citations and rate.citations
            and {(c.version_id,c.byte_sha256) for c in effectivity.citations}
                == {(c.version_id,c.byte_sha256) for c in rate.citations}):
        try:
            limits = json.loads(effectivity.text).get('source_limits', [])
        except (ValueError, AttributeError):
            limits = []
        if any(isinstance(limit,dict) and limit.get('issue') == 'effectivity_currentness_unknown'
                and limit.get('resolution') == 'unresolved' for limit in limits):
            claims += ((_EFFECTIVITY_TEXT[pack.language].format(effectivity=fields['printed_effectivity']),
                        effectivity.evidence_id),)
    return {p.part_id: _currency_claims(pack.language, rate) if CURRENCY.search(p.text) else claims for p in parts}
