from __future__ import annotations

import os
from typing import Tuple

try:
    import asyncpg
except ImportError:
    asyncpg = None

try:
    import janus_swi as janus
except ImportError:
    try:
        import janus
    except ImportError:
        janus = None

import httpx


async def probe_supabase_pgvector(db_url: str | None = None) -> Tuple[bool, str | None]:
    """Connect to Postgres/Supabase and verify the pgvector extension is installed."""
    if db_url is None:
        db_url = os.environ.get(
            "SUPABASE_DB_URL",
            "postgresql://postgres:postgres@supabase_db_bintanong:5432/postgres",
        )
    if asyncpg is None:
        return False, "asyncpg driver not installed"
    try:
        conn = await asyncpg.connect(db_url, timeout=2.0)
        try:
            row = await conn.fetchrow(
                "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
            )
            if row:
                return True, f"pgvector {row['extversion']}"
            return False, "pgvector extension is not installed in database"
        finally:
            await conn.close()
    except Exception as exc:
        return False, f"database connection error: {exc}"


def probe_janus() -> Tuple[bool, str | None]:
    """Execute a harmless query in SWI-Prolog via Janus to verify reasoning bridge."""
    if janus is None:
        return False, "janus-swi module is not installed"
    try:
        result = janus.query_once("X is 2 + 2")
        if result and result.get("X") == 4:
            return True, "SWI-Prolog 10.0.2 via Janus functional"
        return False, f"unexpected Prolog query result: {result}"
    except Exception as exc:
        return False, f"Prolog execution error: {exc}"


async def probe_http_service(url: str, path: str = "/health", timeout: float = 2.0) -> Tuple[bool, str | None]:
    """Check connectivity to a downstream HTTP service."""
    target = f"{url.rstrip('/')}{path}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(target)
            if response.status_code == 200:
                return True, "healthy"
            return False, f"HTTP status {response.status_code}"
    except Exception as exc:
        return False, f"service unreachable: {exc}"
