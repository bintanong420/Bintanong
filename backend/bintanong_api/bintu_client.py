from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Literal
import httpx
from pydantic import BaseModel, Field


class RoutingDecision(BaseModel):
    route: Literal["RAG", "Hybrid", "Symbolic", "Direct"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str


class BintuError(Exception):
    """Base exception for Bintu client operations."""


class BintuTimeoutError(BintuError):
    """Raised when Bintu inference request times out."""


class BintuConnectionError(BintuError):
    """Raised when unable to reach Bintu llama-server."""


def verify_gguf_checksum(path: Path | str, expected_sha256: str, chunk_size: int = 4 * 1024 * 1024) -> bool:
    file_path = Path(path)
    if not file_path.is_file():
        return False
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest().upper() == expected_sha256.upper()


ROUTING_SYSTEM_PROMPT = (
    "You are Bintu, the academic guide query router for Palawan State University (PalSU).\n"
    "Classify the student's query into one of four routes:\n"
    "- 'Symbolic': Exact rule/prerequisite/eligibility verification against institutional rules.\n"
    "- 'RAG': Institutional policy explanation, handbook lookup, or general guidelines.\n"
    "- 'Hybrid': Complex queries requiring both policy context and rule evaluation.\n"
    "- 'Direct': Simple conversational greetings or out-of-scope questions.\n"
    "Output strict JSON with keys 'route', 'confidence', and 'reason'."
)


class BintuClient:
    def __init__(self, base_url: str | None = None, timeout_seconds: float | None = None) -> None:
        self.base_url = (base_url or os.environ.get("BINTU_URL", "http://127.0.0.1:8080")).rstrip("/")
        timeout_env = os.environ.get("BINTU_REQUEST_TIMEOUT_SECONDS", "120")
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else float(timeout_env)

    async def route_query(self, query: str) -> RoutingDecision:
        endpoint = f"{self.base_url}/v1/chat/completions"
        payload = {
            "messages": [
                {"role": "system", "content": ROUTING_SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            "temperature": 0.1,
            "max_tokens": 128,
            "response_format": {"type": "json_object"},
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                res = await client.post(endpoint, json=payload)
                if res.status_code != 200:
                    raise BintuError(f"Bintu server error HTTP {res.status_code}: {res.text}")
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return RoutingDecision(**parsed)
        except (httpx.TimeoutException, TimeoutError) as exc:
            raise BintuTimeoutError(f"Request to Bintu timed out after {self.timeout_seconds}s: {exc}") from exc
        except httpx.RequestError as exc:
            raise BintuConnectionError(f"Connection error reaching Bintu server: {exc}") from exc
        except Exception as exc:
            if "timeout" in str(exc).lower():
                raise BintuTimeoutError(f"Bintu operation timed out: {exc}") from exc
            raise BintuError(f"Failed to route query: {exc}") from exc

    def route_query_sync(self, query: str) -> RoutingDecision:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If in an existing async loop, use run_until_complete in a separate thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                return executor.submit(asyncio.run, self.route_query(query)).result()
        return asyncio.run(self.route_query(query))
