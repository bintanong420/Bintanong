"""Phase 11 O3: read-only program/curriculum list for the student's picker."""
from fastapi.testclient import TestClient

from backend.bintanong_api.app import ApiServices, ApiSettings, create_app
from backend.bintanong_api.chat import CurriculumOption
from backend.bintanong_private_context.sessions import SessionStore


def test_curricula_lists_names_and_ids_without_creating_a_session():
    store = SessionStore()
    curricula = (CurriculumOption('palsu-bscs', 'bscs-2018-2019', 'BS Computer Science', 'BSCS 2018-2019'),)
    app = create_app(ApiServices(sessions=store, curricula=curricula), ApiSettings(allowed_origins=()))
    response = TestClient(app, base_url='https://testserver').get('/curricula')
    assert response.status_code == 200
    assert response.json() == {'curricula': [dict(programId='palsu-bscs', curriculumId='bscs-2018-2019',
                                                  programName='BS Computer Science',
                                                  curriculumName='BSCS 2018-2019')]}
    assert 'set-cookie' not in response.headers and len(store) == 0
