from __future__ import annotations

import unittest
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

if __name__ == "__main__":
    unittest.main()
