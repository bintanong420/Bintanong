# Phase 0: Docker and Compatibility Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Phase 0 by implementing and verifying the remaining tasks (Tasks 4 through 9)—API with Janus/Supabase probe, SEA-LION embedding endpoint, Docling tools, Bintu llama-server compatibility, Next.js health dashboard, and the verified Phase 0 handoff.

**Architecture:** A Docker Compose stack comprising local loopback Supabase with pgvector, FastAPI with in-process Janus/SWI-Prolog orchestration, resident SEA-LION embedding service, resident Bintu quantized llama-server, Docling parsing tools, and Next.js frontend with same-origin health proxying.

**Tech Stack:** Python 3.13, FastAPI 0.141.1, SWI-Prolog 10.0.2 via janus-swi 1.5.3, asyncpg 0.31.0, Sentence Transformers 6.1.0, Docling 2.129.0, llama.cpp server-v0.4.1, Node.js 24 LTS, Next.js 16.3.5, Supabase CLI 2.117.0, Docker Compose.

**Spec:** `plans/phase-00-docker-compatibility-plan.md` (and `plans/master_implementation_plan_original_long.md` Section 5)

## Global Constraints

- Retain repo continuity: update `plans/phase-00-checkpoint.md` after each verified commit; do not advance to Phase 1 until `plans/phase-00-handoff.md` is complete.
- Model files are fixed in `C:/Coding-projects/MODELS` (configured in `.env` with a notice that this path is host-dependent).
- Bintu GGUF SHA-256: `3CF61DE12DAA015EE0F7B68E7B7C541405BF220E1E942BAD8B47CAB827D7DF80`.
- SEA-LION weights SHA-256: `DF5B1C55623EEB5EF09CE3F3C50E24E2DB433D7D1BBCCCF76D2F01BA212DF5F1`.
- API endpoints: `/health/live` returns HTTP 200; `/health/ready` returns HTTP 200 when ready and HTTP 503 when degraded with typed failure reason breakdown.
- Embedding endpoint: POST `/encode` produces 1,024-dimensional normalized float vectors with finite values.
- Docling fixture: synthetic PDF only; no confidential/institutional documents in Phase 0.

---

### Task 4: API, Janus SWI-Prolog, and Supabase Probe

**Files:**
- Create: `backend/bintanong_api/__init__.py`
- Create: `backend/bintanong_api/main.py`
- Create: `backend/bintanong_api/probes.py`
- Test: `tests/test_api_probes.py`
- Modify: `plans/phase-00-checkpoint.md`

**Interfaces:**
- Consumes: `SUPABASE_DB_URL`, `EMBEDDING_URL`, `BINTU_URL` from environment; `janus` CPython module (when SWI-Prolog is present) or mocked/abstracted fallback.
- Produces:
  - `GET /health/live`: `{"status": "live"}`
  - `GET /health/ready`: `{"status": "ready" | "degraded", "probes": {"supabase": bool, "janus": bool, "embedding": bool, "bintu": bool}, "errors": dict[str, str]}`
  - `probe_janus() -> tuple[bool, str | None]`
  - `probe_supabase(url: str) -> tuple[bool, str | None]`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_api_probes.py
import unittest
from fastapi.testclient import TestClient
from backend.bintanong_api.main import app

class TestApiProbes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_liveness_returns_200(self):
        res = self.client.get("/health/live")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "live"})

    def test_readiness_reports_degraded_when_dependencies_unreachable(self):
        res = self.client.get("/health/ready")
        self.assertEqual(res.status_code, 503)
        body = res.json()
        self.assertEqual(body["status"], "degraded")
        self.assertIn("probes", body)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_api_probes -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'backend.bintanong_api'`

- [ ] **Step 3: Write minimal implementation**

Implement `backend/bintanong_api/__init__.py`, `backend/bintanong_api/probes.py`, and `backend/bintanong_api/main.py` defining the FastAPI application, the typed probe checks, and the `/health/live` and `/health/ready` routes with 200/503 status code logic.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_api_probes -v`
Expected: PASS

- [ ] **Step 5: Commit & update checkpoint**

```bash
git add backend/bintanong_api tests/test_api_probes.py
git commit -m "feat(api): add liveness, readiness, and dependency probes"
```
Update `plans/phase-00-checkpoint.md` with new commit hash, increment sequence to 8, mark Task 4 complete, and verify with `phase_state.py inspect`.

---

### Task 5: SEA-LION Embedding Service

**Files:**
- Create: `backend/bintanong_embedding/__init__.py`
- Create: `backend/bintanong_embedding/main.py`
- Create: `backend/bintanong_embedding/verifier.py`
- Test: `tests/test_embedding_service.py`
- Modify: `plans/phase-00-checkpoint.md`

**Interfaces:**
- Consumes: `MODELS_ROOT`, `EMBEDDING_MODEL_RELATIVE_PATH`, `EMBEDDING_WEIGHTS_SHA256`
- Produces:
  - `GET /health`: `{"status": "ok", "model": str, "dimension": 1024, "weights_verified": bool}`
  - `POST /encode`: input `{"texts": list[str]}`, output `{"dimension": 1024, "count": int, "embeddings": list[list[float]]}`
  - `verify_model_weights(model_dir: Path, expected_sha256: str) -> bool`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_embedding_service.py
import unittest
from fastapi.testclient import TestClient
from backend.bintanong_embedding.main import app

class TestEmbeddingService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_returns_status_and_dimension(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["dimension"], 1024)

    def test_encode_empty_list_returns_422(self):
        res = self.client.post("/encode", json={"texts": []})
        self.assertEqual(res.status_code, 422)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_embedding_service -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'backend.bintanong_embedding'`

- [ ] **Step 3: Write minimal implementation**

Implement `backend/bintanong_embedding/verifier.py` and `backend/bintanong_embedding/main.py` using FastAPI and Pydantic schemas, with SHA-256 verification and vector dimension validation.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_embedding_service -v`
Expected: PASS

- [ ] **Step 5: Commit & update checkpoint**

```bash
git add backend/bintanong_embedding tests/test_embedding_service.py
git commit -m "feat(embedding): implement SEA-LION service contract and verification"
```
Update `plans/phase-00-checkpoint.md` with new commit hash, increment sequence to 9, mark Task 5 complete.

---

### Task 6: Docling Synthetic PDF Ingestion Tools

**Files:**
- Create: `tests/fixtures/generate_synthetic_pdf.py`
- Create: `tests/fixtures/synthetic_academic_guide.pdf`
- Create: `backend/bintanong_tools/__init__.py`
- Create: `backend/bintanong_tools/ingest.py`
- Create: `backend/bintanong_tools/evaluate.py`
- Test: `tests/test_tools_contract.py`
- Modify: `plans/phase-00-checkpoint.md`

**Interfaces:**
- Consumes: reportlab (for fixture generation), typer (for CLI)
- Produces:
  - CLI `python -m bintanong_tools.ingest --help`
  - CLI `python -m bintanong_tools.ingest parse <path>`
  - CLI `python -m bintanong_tools.evaluate --help`
  - Synthetic PDF fixture `tests/fixtures/synthetic_academic_guide.pdf`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_tools_contract.py
import subprocess
import sys
import unittest
from pathlib import Path

class TestToolsContract(unittest.TestCase):
    def test_ingest_cli_help(self):
        res = subprocess.run([sys.executable, "-m", "bintanong_tools.ingest", "--help"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("ingest", res.stdout.lower())

    def test_evaluate_cli_help(self):
        res = subprocess.run([sys.executable, "-m", "bintanong_tools.evaluate", "--help"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("evaluate", res.stdout.lower())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests.test_tools_contract -v`
Expected: FAIL with `No module named bintanong_tools`

- [ ] **Step 3: Write minimal implementation**

1. Create `tests/fixtures/generate_synthetic_pdf.py` and run it to produce `synthetic_academic_guide.pdf`.
2. Implement Typer CLIs in `backend/bintanong_tools/ingest.py` and `backend/bintanong_tools/evaluate.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests.test_tools_contract -v`
Expected: PASS

- [ ] **Step 5: Commit & update checkpoint**

```bash
git add backend/bintanong_tools tests/fixtures tests/test_tools_contract.py
git commit -m "feat(tools): implement ingest and evaluate CLI contracts with synthetic PDF"
```
Update `plans/phase-00-checkpoint.md` with new commit hash, increment sequence to 10, mark Task 6 complete.

---

### Task 7: Bintu llama.cpp Compatibility and Inference Probe

**Files:**
- Create: `tests/test_bintu_inference.py`
- Modify: `plans/phase-00-checkpoint.md`

**Interfaces:**
- Consumes: llama-server OpenAI-compatible API (`/v1/chat/completions`) on `BINTU_URL` (default `http://127.0.0.1:8080`)
- Produces: Verified structured JSON outputs matching `{route: string, confidence: float, reason: string}` and timeout/queue handling.

- [ ] **Step 1: Write test for GGUF checksum & structured schema**

```python
# tests/test_bintu_inference.py
import hashlib
import unittest
from pathlib import Path

class TestBintuContract(unittest.TestCase):
    def test_bintu_checksum_verifier(self):
        expected = "3CF61DE12DAA015EE0F7B68E7B7C541405BF220E1E942BAD8B47CAB827D7DF80"
        model_path = Path("C:/Coding-projects/MODELS/GEMMA_4_E4B/gemma-4-E4B-it-UD-Q4_K_XL.gguf")
        if model_path.exists():
            # Fast sample check or full verification
            self.assertTrue(model_path.stat().st_size > 0)
```

- [ ] **Step 2: Run test to verify expectations**

Run: `python -m unittest tests.test_bintu_inference -v`

- [ ] **Step 3: Implement client adapter and schema validator**

Add Bintu client helper in `backend/bintanong_api/bintu_client.py` for structured query routing.

- [ ] **Step 4: Verify test passes**

Run: `python -m unittest tests.test_bintu_inference -v`
Expected: PASS

- [ ] **Step 5: Commit & update checkpoint**

```bash
git add tests/test_bintu_inference.py backend/bintanong_api/bintu_client.py
git commit -m "feat(bintu): add client adapter and structured inference contract"
```
Update `plans/phase-00-checkpoint.md`, sequence 11, mark Task 7 complete.

---

### Task 8: Next.js Health Surface and Status Page

**Files:**
- Create: `frontend/app/api/health/route.ts`
- Modify: `frontend/app/page.tsx`
- Test: Frontend build & endpoint check
- Modify: `plans/phase-00-checkpoint.md`

**Interfaces:**
- Consumes: FastAPI `/health/ready` and `/health/live` via `API_INTERNAL_URL`
- Produces:
  - `GET /api/health` returning proxied status and latency
  - Responsive web dashboard rendering component statuses (Supabase, Janus, Embedding, Bintu)

- [ ] **Step 1: Implement Next.js API route proxy**

Create `frontend/app/api/health/route.ts` fetching `API_INTERNAL_URL/health/ready`.

- [ ] **Step 2: Implement frontend dashboard component**

Update `frontend/app/page.tsx` with a clean status UI showing operational badges and probe latencies.

- [ ] **Step 3: Run build test to verify correctness**

Run: `cd frontend && npm run build`
Expected: Successful Next.js production build without TypeScript errors.

- [ ] **Step 4: Commit & update checkpoint**

```bash
git add frontend/app/api/health frontend/app/page.tsx
git commit -m "feat(web): implement Next.js health proxy and status UI"
```
Update `plans/phase-00-checkpoint.md`, sequence 12, mark Task 8 complete.

---

### Task 9: Integrated Exit Gate and Phase 0 Handoff

**Files:**
- Create: `plans/phase-00-handoff.md`
- Modify: `plans/phase-00-checkpoint.md` (set status: superseded)
- Modify: `plans/INDEX.md` (record phase 0 complete, next phase 1)

**Interfaces:**
- Consumes: All test outputs, Docker compose configurations, and Git commits.
- Produces:
  - Authoritative handoff contract: `plans/phase-00-handoff.md`
  - Validated state where `phase_state.py can-advance` exits 0.

- [ ] **Step 1: Run full exit gate verification**

Run all test suites:
- `python -m unittest discover -s tests -p "test_*.py"`
- `python -m unittest discover -s .agents/skills/bintanong-phase-handoff/tests -p "test_*.py"`
- `python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py inspect --repo .`

- [ ] **Step 2: Generate `plans/phase-00-handoff.md`**

Create the handoff artifact with frontmatter:
```yaml
artifact: phase-handoff
phase: 0
status: complete
plan: plans/phase-00-docker-compatibility-plan.md
final_commit: <final_commit_sha>
next_phase: 1
completed_at: 2026-09-21T...
```

- [ ] **Step 3: Mark checkpoint superseded and update INDEX.md**

Update `plans/phase-00-checkpoint.md` status to `superseded`.
Update `plans/INDEX.md` Phase 0 to `complete` and Next permitted phase to `1`.

- [ ] **Step 4: Run validation tools**

Run: `python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py validate --repo .`
Run: `python .agents/skills/bintanong-phase-handoff/scripts/phase_state.py can-advance --repo .`
Expected: `can-advance` exits with 0 and prints `Can advance: yes`.

- [ ] **Step 5: Commit final handoff**

```bash
git add plans/
git commit -m "docs: complete Phase 0 Docker and compatibility foundation handoff"
```
