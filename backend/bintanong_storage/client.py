"""Supabase PostgREST Storage Client.

Provides role-separated HTTP client wrappers adhering to Master Plan Section 9.2:
- Migration/loader operations execute via service_role key.
- Runtime query/evaluation operations execute via anon key with RLS enforcement.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import httpx

from .config import StorageConfig


class StorageError(Exception):
    """Base exception for Supabase storage errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class PermissionDeniedError(StorageError):
    """Raised when an operation violates RLS or schema grants."""
    pass


class SupabaseStorageClient:
    def __init__(self, config: Optional[StorageConfig] = None) -> None:
        self.config = config or StorageConfig.from_env()
        self.base_url = f"{self.config.api_url}/rest/v1"
        self._http = httpx.Client(timeout=self.config.timeout_seconds)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> SupabaseStorageClient:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _headers(self, role: str, prefer: Optional[str] = None) -> Dict[str, str]:
        key = self.config.service_role_key if role == "admin" else self.config.anon_key
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    def _handle_response(self, response: httpx.Response) -> Any:
        if response.is_success:
            if response.status_code == 204 or not response.content:
                return None
            return response.json()

        try:
            err_data = response.json()
            message = err_data.get("message") or str(err_data)
        except Exception:
            err_data = None
            message = response.text or f"HTTP {response.status_code}"

        if response.status_code in (401, 403) or (
            isinstance(err_data, dict) and err_data.get("code") == "42501"
        ):
            raise PermissionDeniedError(
                f"Permission denied: {message}",
                status_code=response.status_code,
                details=err_data,
            )

        raise StorageError(
            f"Storage request failed ({response.status_code}): {message}",
            status_code=response.status_code,
            details=err_data,
        )

    def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, str]] = None,
        role: str = "runtime",
    ) -> List[Dict[str, Any]]:
        """Query rows from a table. Defaults to runtime (anon) role to verify RLS."""
        url = f"{self.base_url}/{table}"
        params: Dict[str, str] = {"select": columns}
        if filters:
            params.update(filters)
        headers = self._headers(role=role)
        res = self._http.get(url, params=params, headers=headers)
        return self._handle_response(res) or []

    def insert(
        self,
        table: str,
        data: Dict[str, Any] | List[Dict[str, Any]],
        role: str = "admin",
        return_records: bool = False,
    ) -> Any:
        """Insert rows into a table."""
        url = f"{self.base_url}/{table}"
        prefer = "return=representation" if return_records else "return=minimal"
        headers = self._headers(role=role, prefer=prefer)
        payload = [data] if isinstance(data, dict) else data
        res = self._http.post(url, json=payload, headers=headers)
        return self._handle_response(res)

    def upsert(
        self,
        table: str,
        data: Dict[str, Any] | List[Dict[str, Any]],
        on_conflict: Optional[str] = None,
        role: str = "admin",
    ) -> Any:
        """Idempotently insert or update records."""
        url = f"{self.base_url}/{table}"
        params = {"on_conflict": on_conflict} if on_conflict else {}
        prefer = "resolution=merge-duplicates,return=minimal"
        headers = self._headers(role=role, prefer=prefer)
        payload = [data] if isinstance(data, dict) else data
        res = self._http.post(url, params=params, json=payload, headers=headers)
        return self._handle_response(res)

    def delete(
        self,
        table: str,
        filters: Dict[str, str],
        role: str = "admin",
    ) -> Any:
        """Delete rows matching filters."""
        url = f"{self.base_url}/{table}"
        headers = self._headers(role=role)
        res = self._http.delete(url, params=filters, headers=headers)
        return self._handle_response(res)

    def rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None,
        role: str = "runtime",
    ) -> Any:
        """Execute a PostgreSQL RPC function."""
        url = f"{self.base_url}/rpc/{function_name}"
        headers = self._headers(role=role)
        res = self._http.post(url, json=params or {}, headers=headers)
        return self._handle_response(res)
