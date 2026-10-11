"""Configuration for Supabase Storage & Database Connections.

Provides environment variable resolution with local Supabase stack defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_LOCAL_URL = "http://127.0.0.1:54321"
DEFAULT_LOCAL_DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

# Standard local demo credentials provided by Supabase CLI
DEFAULT_LOCAL_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9."
    "CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
)

DEFAULT_LOCAL_SERVICE_ROLE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0."
    "EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
)


@dataclass(frozen=True)
class StorageConfig:
    api_url: str
    anon_key: str
    service_role_key: str
    db_url: str
    timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls) -> StorageConfig:
        return cls(
            api_url=os.getenv("SUPABASE_URL", DEFAULT_LOCAL_URL).rstrip("/"),
            anon_key=os.getenv("SUPABASE_ANON_KEY", DEFAULT_LOCAL_ANON_KEY),
            service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", DEFAULT_LOCAL_SERVICE_ROLE_KEY),
            db_url=os.getenv("SUPABASE_DB_URL", DEFAULT_LOCAL_DB_URL),
            timeout_seconds=float(os.getenv("SUPABASE_TIMEOUT_SECONDS", "30.0")),
        )
