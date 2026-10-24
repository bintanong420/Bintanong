"""Owner, 24 Oct 2026 ("Rate + example"): a special class fee question gets one host-written reply in
every language. The printed rate and printed example are copied from the reviewed fields, never computed;
the student's own charge is not stated, so the reply refers them to the office. F04 stays held."""
import json

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
    return {p.part_id: claims for p in parts}
