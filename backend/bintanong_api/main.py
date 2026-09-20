from __future__ import annotations

import os
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

from backend.bintanong_api.probes import (
    probe_http_service,
    probe_janus,
    probe_supabase_pgvector,
)

app = FastAPI(title="Bintanong API", version="0.0.0")


class HealthStatus(BaseModel):
    status: str
    probes: dict[str, bool]
    errors: dict[str, str]


@app.get("/health/live")
async def health_live() -> dict[str, str]:
    """Liveness probe: verifies process is running and accepting HTTP requests."""
    return {"status": "live"}


@app.get("/health/ready", response_model=HealthStatus)
async def health_ready(response: Response) -> HealthStatus:
    """Readiness probe: verifies all upstream and downstream dependencies are healthy."""
    db_url = os.environ.get(
        "SUPABASE_DB_URL",
        "postgresql://postgres:postgres@supabase_db_bintanong:5432/postgres",
    )
    embedding_url = os.environ.get("EMBEDDING_URL", "http://embedding:8001")
    bintu_url = os.environ.get("BINTU_URL", "http://bintu:8080")

    supa_ok, supa_detail = await probe_supabase_pgvector(db_url)
    janus_ok, janus_detail = probe_janus()
    embed_ok, embed_detail = await probe_http_service(embedding_url, "/health")
    bintu_ok, bintu_detail = await probe_http_service(bintu_url, "/health")

    probes = {
        "supabase": supa_ok,
        "janus": janus_ok,
        "embedding": embed_ok,
        "bintu": bintu_ok,
    }
    errors: dict[str, str] = {}
    if not supa_ok and supa_detail:
        errors["supabase"] = supa_detail
    if not janus_ok and janus_detail:
        errors["janus"] = janus_detail
    if not embed_ok and embed_detail:
        errors["embedding"] = embed_detail
    if not bintu_ok and bintu_detail:
        errors["bintu"] = bintu_detail

    all_ready = all(probes.values())
    if not all_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthStatus(status="degraded", probes=probes, errors=errors)

    return HealthStatus(status="ready", probes=probes, errors={})
