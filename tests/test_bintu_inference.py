from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

# We expect this import to fail in Step 2 before implementation
from backend.bintanong_api.bintu_client import (
    BintuClient,
    BintuTimeoutError,
    RoutingDecision,
    verify_gguf_checksum,
)


class BintuInferenceTests(unittest.TestCase):
    def test_routing_decision_schema_validation(self) -> None:
        valid_data = {"route": "RAG", "confidence": 0.95, "reason": "Curriculum policy query"}
        decision = RoutingDecision(**valid_data)
        self.assertEqual(decision.route, "RAG")
        self.assertAlmostEqual(decision.confidence, 0.95)
        self.assertEqual(decision.reason, "Curriculum policy query")

    def test_routing_decision_rejects_invalid_route(self) -> None:
        with self.assertRaises(ValueError):
            RoutingDecision(route="InvalidRoute", confidence=0.5, reason="Testing")

    @patch("httpx.AsyncClient.post", new_callable=AsyncMock)
    def test_bintu_client_route_query_success(self, mock_post: AsyncMock) -> None:
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"route": "Symbolic", "confidence": 0.88, "reason": "Prerequisite eligibility query"}'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        client = BintuClient(base_url="http://127.0.0.1:8080")
        decision = client.route_query_sync("Can I take CS311 without CS221?")
        self.assertEqual(decision.route, "Symbolic")
        self.assertEqual(decision.confidence, 0.88)
        self.assertIn("Prerequisite", decision.reason)

    @patch("httpx.AsyncClient.post", side_effect=Exception("ReadTimeout"))
    def test_bintu_client_timeout_raises_bintu_timeout_error(self, mock_post: AsyncMock) -> None:
        client = BintuClient(base_url="http://127.0.0.1:8080", timeout_seconds=0.1)
        with self.assertRaises(BintuTimeoutError):
            client.route_query_sync("Test query that times out")

    def test_gguf_verifier_on_nonexistent_file(self) -> None:
        self.assertFalse(verify_gguf_checksum(Path("nonexistent.gguf"), "some-sha"))


if __name__ == "__main__":
    unittest.main()
