"""Owner-resolved source limits (owner 28 Oct 2026): a limit the owner has settled stops holding its record and
is not shown. The reviewed package keeps the original limit; the resolution is applied when evidence is prepared."""
import json

from backend.bintanong_generation import evidence
from backend.bintanong_generation.evidence import prepare
from backend.bintanong_generation.malformed_condition import malformed_records
from test_generation_service_steps import record
from test_generation_service_steps_answer import integration

SETTLED = 'Unavailable information: fictional overlapping boundaries unresolved.'
OPEN = 'Unavailable information: fictional other gap.'


def limit(message, gap='limit-1'):
    return dict(affected_claims=['fictional'], field_names=['body'], gap_id=gap, issue='malformed_source_condition',
                locator=dict(field='body', physical_pages=[1]), message=message, resolution='unresolved')


def held_text(*limits):
    value = json.loads(record(('body', 'FIRST YEAR. Completed 25%. SECOND YEAR. 25% but not more than 50%.')))
    value['source_limits'] = list(limits)
    return json.dumps(value)


def test_an_owner_resolved_limit_no_longer_holds_or_shows(monkeypatch):
    monkeypatch.setattr(evidence, 'OWNER_RESOLVED_LIMITS', frozenset({SETTLED}))
    pack = prepare(integration(texts=(held_text(limit(SETTLED)),)))
    card = next(c for c in pack.cards if c.kind == 'document')
    assert json.loads(card.text)['source_limits'] == []
    assert not malformed_records(pack)


def test_other_limits_on_the_same_record_still_hold(monkeypatch):
    monkeypatch.setattr(evidence, 'OWNER_RESOLVED_LIMITS', frozenset({SETTLED}))
    pack = prepare(integration(texts=(held_text(limit(SETTLED), limit(OPEN, 'limit-2')),)))
    card = next(c for c in pack.cards if c.kind == 'document')
    assert [l['message'] for l in json.loads(card.text)['source_limits']] == [OPEN]
    assert malformed_records(pack)


def test_the_year_level_overlap_is_owner_resolved():
    assert any('overlapping year-level percentage boundaries' in m for m in evidence.OWNER_RESOLVED_LIMITS)
