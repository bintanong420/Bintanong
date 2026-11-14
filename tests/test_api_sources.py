"""Phase 11 `GET /sources/{source_id}` (master 16.1/16.2): a cited institutional excerpt with title and page.

Only cards cited by answers in this process are served (pinned release), never private facts or internal
locators. Blank source fields stay visibly blank (source-gap policy), never zero or "none"."""
import json

from fastapi.testclient import TestClient

from backend.bintanong_api.app import ApiServices, ApiSettings, create_app
from backend.bintanong_api.sources import SourceRegistry, source_view
from backend.bintanong_private_context.sessions import SessionStore
from test_api_presentation import answer_for
from test_api_stream import CURRICULA, ORIGIN, Pipeline, body, parse

ANSWER = answer_for('Hybrid')


def build():
    store = SessionStore()
    app = create_app(ApiServices(sessions=store, curricula=CURRICULA, pipeline=Pipeline(ANSWER)),
                     ApiSettings(allowed_origins=(ORIGIN,)))
    return app, store


def test_cited_sources_of_an_answer_can_be_fetched():
    app, _ = build()
    c = TestClient(app, base_url='https://testserver', headers={'Origin': ORIGIN})
    ids = [p['sourceId'] for p in parse(c.post('/chat', json=body()).content) if p['type'] == 'source-document']
    assert ids == [card.evidence_id for card in ANSWER.citations]
    for card in ANSWER.citations:
        response = c.get(f'/sources/{card.evidence_id}')
        assert response.status_code == 200
        data = response.json()
        assert data['sourceId'] == card.evidence_id and data['page'] == card.citations[0].page
        assert data['excerpt'] == card.text and data['kind'] == card.kind
        assert card.citations[0].locator.ref not in response.text if card.citations[0].locator.ref else True


def test_uncited_or_unknown_source_is_404_and_creates_no_session():
    app, store = build()
    response = TestClient(app, base_url='https://testserver').get('/sources/ev-' + '0' * 64)
    assert (response.status_code, response.json()) == (404, {'error': 'unknown_source'})
    assert len(store) == 0 and 'set-cookie' not in response.headers


def test_reviewed_fields_become_readable_pairs_and_blanks_stay_blank():
    card = ANSWER.citations[0].model_copy(update={'text': json.dumps({
        'fields': [{'name': 'grade', 'value': '1.0', 'source_blank': False},
                   {'name': 'percentage_equivalent', 'value': '98-100', 'source_blank': False},
                   {'name': 'remarks', 'value': '', 'source_blank': True}],
        'source_limits': [{'issue': 'source_cutoff', 'resolution': 'unresolved'}]})})
    view = source_view(card)
    assert view['excerpt'] == 'Grade: 1.0\nPercentage equivalent: 98-100\nRemarks: (blank in the source)'
    assert view['hasSourceLimits'] is True
    assert '_' not in view['excerpt']


def test_registry_keeps_only_the_most_recent_cards():
    first, second = ANSWER.citations[:2]
    registry = SourceRegistry(max_cards=1)
    registry.remember((first,))
    registry.remember((second,))
    assert registry.get(first.evidence_id) is None and registry.get(second.evidence_id) == second
