"""Carry the reviewed admission-fraud overlap without adjudicating a sanction.

Only the recorded unresolved precedence limitation activates this reply. Printed
values come from the retrieved cards; no sanctions are maintained here.
"""
import json


_CLAIM = 'precedence between overlapping admission-fraud sanctions'
_ROWS = {f'handbook-disciplinary-{label}-fraud-precedence': label for label in ('II.6', 'II.8a')}
_PENALTIES = ('1st Offense', '2nd Offense', '3rd Offense', 'Subsequent Offenses')
_WORDS = {
    'en': dict(row='Printed row {label} (quoted): {fields}', blank='unspecified',
        notice='These rows overlap; the source does not establish which sanction applies. '
               'I cannot choose a sanction for your case. Please confirm with the right university office.'),
    'fil': dict(row='Naka-print na hanay {label} (sipi): {fields}', blank='hindi tinukoy',
        notice='Magkapatong ang saklaw ng mga hanay na ito; hindi malinaw kung aling parusa ang susundin. '
               'Hindi ako makakapili ng parusa para sa iyo. Pakitanong sa tamang opisina ng unibersidad.'),
    'taglish': dict(row='Ang printed row {label} (quoted): {fields}', blank='unspecified',
        notice='May overlap ang rows na ito; hindi clear kung aling sanction ang applicable. '
               'Hindi ako makakapili ng sanction para sa case mo. Paki-confirm sa tamang university office.')}


def _record(card):
    if card.kind != 'document':
        return None
    try:
        value = json.loads(card.text)
        limits = value.get('source_limits', [])
        matching = [limit for limit in limits if isinstance(limit, dict)
            and limit.get('issue') == 'claim_not_stated' and limit.get('resolution') == 'unresolved'
            and _CLAIM in limit.get('affected_claims', [])]
        if not matching:
            return None
        label = _ROWS.get(matching[0].get('gap_id')) if len(matching) == 1 else None
        fields = value.get('fields', [])
        return label, fields
    except (ValueError, TypeError, AttributeError):
        return None


def precedence_reply(pack, proposed, *, max_claims=2):
    """None if unaffected; empty if incomplete; otherwise two cited host claims.

    Replace the entire affected slot before numbering/review, so even a positive
    model verdict cannot release its chosen sanction. Independent slots survive.
    """
    records = {c.evidence_id: (c, record) for c in pack.cards if (record := _record(c)) is not None}
    cited = {ref for claim in proposed for ref in claim.evidence_ids}
    if not cited.intersection(records):
        return None
    independent = [dict(text=claim.text,evidence_ids=list(claim.evidence_ids)) for claim in proposed
                   if not set(claim.evidence_ids).intersection(records)]
    max_claims -= len(independent)
    if pack.language not in _WORDS or len(records) != 2:
        return ()
    labelled = {record[0]: (card, record[1]) for card, record in records.values()}
    if set(labelled) != set(_ROWS.values()):
        return ()
    sources = [{(c.version_id, c.byte_sha256) for c in card.citations} for card, _ in labelled.values()]
    if not sources[0] or len(sources[0]) != 1 or sources[0] != sources[1]:
        return ()
    words = _WORDS[pack.language]
    claims = []
    for label in _ROWS.values():
        card, fields = labelled[label]
        if not isinstance(fields, list) or any(not isinstance(f, dict) for f in fields):
            return ()
        by_name = {f.get('name'): f for f in fields}
        if len(by_name) != len(fields) or not {'Cause', '1st Offense'} <= by_name.keys():
            return ()
        quoted = []
        for name in ('Heading', 'Cause', *_PENALTIES):
            if name not in by_name:
                continue
            field = by_name[name]
            value, blank = field.get('value'), field.get('source_blank')
            if not isinstance(value, str) or type(blank) is not bool or blank != (not value.strip()):
                return ()
            if name == 'Cause' and blank:
                return ()
            quoted.append(f'{name}: '+(words['blank'] if blank else f'"{value}"'))
        text = words['row'].format(label=label, fields='; '.join(quoted))
        if not claims:
            text = words['notice']+' '+text
        if len(text) > 1200:
            return ()
        claims.append(dict(text=text, evidence_ids=[card.evidence_id]))
    if len(claims) > max_claims:
        combined = ' '.join(c['text'] for c in claims)
        if max_claims < 1 or len(combined) > 1200:
            return ()
        return (dict(text=combined, evidence_ids=[c['evidence_ids'][0] for c in claims]), *independent)
    return (*claims, *independent)
