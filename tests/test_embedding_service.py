from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# We expect this import to fail in Step 2 before implementation
from backend.bintanong_embedding.main import app
from backend.bintanong_embedding.verifier import verify_model_weights


class EmbeddingServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    @patch("backend.bintanong_embedding.main.get_model_status")
    def test_health_endpoint_returns_ok_and_dimension(self, mock_status: MagicMock) -> None:
        mock_status.return_value = {
            "status": "ok",
            "model": "SEA-LION-E5-Embedding-600M",
            "dimension": 1024,
            "weights_verified": True,
        }
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["dimension"], 1024)
        self.assertTrue(data["weights_verified"])

    def test_encode_empty_list_returns_422(self) -> None:
        res = self.client.post("/encode", json={"texts": []})
        self.assertEqual(res.status_code, 422)

    @patch("backend.bintanong_embedding.main.encode_texts")
    def test_encode_returns_1024_dimensional_vectors(self, mock_encode: MagicMock) -> None:
        # Mock 1024-dimensional normalized float vectors
        mock_vec_1 = [0.1] * 1024
        mock_vec_2 = [-0.05] * 1024
        mock_encode.return_value = [mock_vec_1, mock_vec_2]

        payload = {"texts": ["What are the curriculum requirements?", "Anong mga requirements sa thesis?"]}
        res = self.client.post("/encode", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["dimension"], 1024)
        self.assertEqual(len(data["embeddings"]), 2)
        self.assertEqual(len(data["embeddings"][0]), 1024)
        self.assertEqual(len(data["embeddings"][1]), 1024)
        # Verify finite float values
        for val in data["embeddings"][0]:
            self.assertIsInstance(val, float)
            self.assertFalse(val != val)  # not NaN


if __name__ == "__main__":
    unittest.main()
