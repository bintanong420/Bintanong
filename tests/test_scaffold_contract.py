from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class ScaffoldContractTests(unittest.TestCase):
    def test_required_scaffold_files_exist(self) -> None:
        required = [
            "compose.yaml",
            "compose.gpu.yaml",
            ".dockerignore",
            ".env.example",
            "package.json",
            "docker/api.Dockerfile",
            "docker/embedding.Dockerfile",
            "docker/ingest.Dockerfile",
            "docker/web.Dockerfile",
            "backend/pyproject.toml",
            "frontend/package.json",
            "supabase/config.toml",
            "supabase/migrations/20260920000000_enable_vector.sql",
        ]
        missing = [path for path in required if not (ROOT / path).is_file()]
        self.assertEqual(missing, [], f"missing scaffold files: {missing}")

    def test_compose_base_has_required_services_and_tools_profiles(self) -> None:
        env = os.environ | {
            "MODELS_DIR": str(ROOT / ".missing-models"),
            "BINTU_MODEL_RELATIVE_PATH": "GEMMA_4_E4B/model.gguf",
            "EMBEDDING_MODEL_RELATIVE_PATH": "SEA-LION-E5-Embedding-600M",
        }
        result = subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                "compose.yaml",
                "--profile",
                "tools",
                "config",
                "--format",
                "json",
            ],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads(result.stdout)
        services = config["services"]
        self.assertTrue({"web", "api", "bintu", "embedding", "ingest", "evaluate"} <= services.keys())
        self.assertIn("tools", services["ingest"].get("profiles", []))
        self.assertIn("tools", services["evaluate"].get("profiles", []))
        for name in ("api", "bintu", "embedding"):
            self.assertIn("healthcheck", services[name])

    def test_gpu_override_requests_nvidia_and_partial_offload(self) -> None:
        text = (ROOT / "compose.gpu.yaml").read_text(encoding="utf-8")
        self.assertIn("driver: nvidia", text)
        self.assertIn("capabilities: [gpu]", text)
        self.assertIn("BINTU_GPU_LAYERS", text)

    def test_environment_example_contains_required_non_secret_configuration(self) -> None:
        text = (ROOT / ".env.example").read_text(encoding="utf-8")
        for key in (
            "MODELS_DIR=",
            "SUPABASE_DB_URL=",
            "BINTU_MODEL_RELATIVE_PATH=",
            "EMBEDDING_MODEL_RELATIVE_PATH=",
            "BINTU_REQUEST_TIMEOUT_SECONDS=",
            "BINTU_QUEUE_LIMIT=",
        ):
            self.assertIn(key, text)
        self.assertNotIn("service_role", text.lower())


if __name__ == "__main__":
    unittest.main()
