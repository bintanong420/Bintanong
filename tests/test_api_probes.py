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


if __name__ == "__main__":
    unittest.main()
