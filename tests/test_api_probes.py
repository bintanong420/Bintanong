from __future__ import annotations

import unittest
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

# We expect this import to fail in Step 2 before implementation
from backend.bintanong_api.main import app
from backend.bintanong_api.probes import probe_janus, probe_supabase_pgvector


class ApiProbesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_liveness_returns_200(self) -> None:
        res = self.client.get("/health/live")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "live"})

    @patch("backend.bintanong_api.main.probe_supabase_pgvector", new_callable=AsyncMock)
    @patch("backend.bintanong_api.main.probe_janus")
    @patch("backend.bintanong_api.main.probe_http_service", new_callable=AsyncMock)
    def test_readiness_all_healthy_returns_200(
        self, mock_http: AsyncMock, mock_janus: unittest.mock.MagicMock, mock_supa: AsyncMock
    ) -> None:
        mock_supa.return_value = (True, "pgvector 0.8.0")
        mock_janus.return_value = (True, "SWI-Prolog 10.0.2")
        mock_http.return_value = (True, "healthy")

        res = self.client.get("/health/ready")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ready")
        self.assertTrue(data["probes"]["supabase"])
        self.assertTrue(data["probes"]["janus"])
        self.assertTrue(data["probes"]["embedding"])
        self.assertTrue(data["probes"]["bintu"])
        self.assertEqual(data["errors"], {})

    @patch("backend.bintanong_api.main.probe_supabase_pgvector", new_callable=AsyncMock)
    @patch("backend.bintanong_api.main.probe_janus")
    @patch("backend.bintanong_api.main.probe_http_service", new_callable=AsyncMock)
    def test_readiness_degraded_returns_503(
        self, mock_http: AsyncMock, mock_janus: unittest.mock.MagicMock, mock_supa: AsyncMock
    ) -> None:
        mock_supa.return_value = (False, "connection refused")
        mock_janus.return_value = (True, "SWI-Prolog 10.0.2")
        mock_http.return_value = (False, "connection refused")

        res = self.client.get("/health/ready")
        self.assertEqual(res.status_code, 503)
        data = res.json()
        self.assertEqual(data["status"], "degraded")
        self.assertFalse(data["probes"]["supabase"])
        self.assertIn("supabase", data["errors"])



class ProbeErrorTextTests(unittest.TestCase):
    """Security review S7: /health/ready is unauthenticated, so failure reasons are fixed text without exception
    details (hosts, users or DSNs)."""

    LEAK = "postgresql://postgres:hunter2@db.internal:5432"

    def test_database_connection_failure_hides_the_exception_text(self) -> None:
        import asyncio
        from backend.bintanong_api import probes
        with patch.object(probes, "asyncpg") as driver:
            driver.connect = AsyncMock(side_effect=OSError(self.LEAK))
            ok, detail = asyncio.run(probe_supabase_pgvector("postgresql://x"))
        self.assertFalse(ok)
        self.assertEqual(detail, "database connection error")

    def test_unreachable_service_hides_the_exception_text(self) -> None:
        import asyncio
        import httpx
        from backend.bintanong_api.probes import probe_http_service
        with patch.object(httpx.AsyncClient, "get", AsyncMock(side_effect=httpx.ConnectError(self.LEAK))):
            ok, detail = asyncio.run(probe_http_service("http://bintu:8080"))
        self.assertFalse(ok)
        self.assertEqual(detail, "service unreachable")

    def test_prolog_failure_hides_the_exception_text(self) -> None:
        from backend.bintanong_api import probes
        with patch.object(probes, "janus") as bridge:
            bridge.query_once.side_effect = RuntimeError(self.LEAK)
            ok, detail = probe_janus()
        self.assertFalse(ok)
        self.assertEqual(detail, "Prolog execution error")

@pytest.mark.parametrize('outcome', ['ready', 'unavailable', 'exception'])
def test_student_readiness_checks_its_configured_storage(outcome):
    from backend.bintanong_api.app import ApiServices, ApiSettings, create_app
    from backend.bintanong_private_context.sessions import SessionStore

    storage = AsyncMock(return_value=(True, None) if outcome == 'ready' else
                        (False, 'hosted retrieval unavailable'))
    if outcome == 'exception':
        storage.side_effect = RuntimeError(ProbeErrorTextTests.LEAK)
    runtime = AsyncMock(return_value=True)
    student = create_app(ApiServices(sessions=SessionStore(), pipeline=object(), ready=runtime,
                                    supabase_probe=storage), ApiSettings(allowed_origins=()))
    with patch('backend.bintanong_api.main.probe_supabase_pgvector', new_callable=AsyncMock) as docker, \
         patch('backend.bintanong_api.main.probe_janus', return_value=(True, None)), \
         patch('backend.bintanong_api.main.probe_http_service', new_callable=AsyncMock,
               return_value=(True, None)):
        response = TestClient(student).get('/health/ready')
    docker.assert_not_awaited()
    storage.assert_awaited_once()
    runtime.assert_awaited_once()
    assert response.status_code == (200 if outcome == 'ready' else 503)
    assert response.json()['status'] == ('ready' if outcome == 'ready' else 'degraded')
    assert response.json()['probes']['supabase'] is (outcome == 'ready')
    assert response.json()['probes']['student_runtime'] is True
    assert ProbeErrorTextTests.LEAK not in response.text
    if outcome == 'ready':
        assert response.json()['errors'] == {}


def test_healthy_storage_does_not_hide_an_unavailable_student_runtime():
    from backend.bintanong_api.app import ApiServices, ApiSettings, create_app
    from backend.bintanong_private_context.sessions import SessionStore

    student = create_app(ApiServices(sessions=SessionStore(), pipeline=object(),
        ready=AsyncMock(return_value=False), supabase_probe=AsyncMock(return_value=(True, None))),
        ApiSettings(allowed_origins=()))
    with patch('backend.bintanong_api.main.probe_janus', return_value=(True, None)), \
         patch('backend.bintanong_api.main.probe_http_service', new_callable=AsyncMock,
               return_value=(True, None)):
        response = TestClient(student).get('/health/ready')
    assert response.status_code == 503
    assert response.json()['probes']['supabase'] is True
    assert response.json()['probes']['student_runtime'] is False


if __name__ == "__main__":
    unittest.main()
