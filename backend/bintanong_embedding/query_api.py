"""Private strict port; the legacy generic encode endpoint is not used by student chat."""
import json
import os
from pathlib import Path
import threading

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.bintanong_retrieval.query import EncoderUnavailable, QueryEncoder, configuration_identity
from backend.bintanong_routing.contracts import prepare_query


class CountInput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    text: str = Field(max_length=65536)


class QueryInput(CountInput):
    text: str = Field(min_length=1, max_length=8192)

    @field_validator('text')
    @classmethod
    def valid_query(cls, value):
        prepare_query(value)
        return value


def query_router(*, encoder=None):
    router = APIRouter()
    gate = threading.BoundedSemaphore(1)
    resolved = encoder

    def run(call):
        nonlocal resolved
        if not gate.acquire(blocking=False):
            raise HTTPException(503, 'query_service_busy')
        try:
            if resolved is None:
                filename = os.environ.get('EMBEDDING_ASSET_MANIFEST')
                if not filename:
                    raise EncoderUnavailable('asset_manifest_required')
                with Path(filename).open('rb') as stream:
                    raw = stream.read(16385)
                if len(raw) > 16384:
                    raise EncoderUnavailable('invalid_asset_manifest')
                manifest = json.loads(raw)
                if not isinstance(manifest, dict) or any(type(k) is not str or type(v) is not str for k, v in manifest.items()):
                    raise EncoderUnavailable('invalid_asset_manifest')
                candidate = QueryEncoder(asset_digests=manifest)
                candidate.load_model()
                resolved = candidate
            resolved.load_model()
            return call(resolved)
        except Exception:
            raise HTTPException(503, 'strict_query_service_unavailable') from None
        finally:
            gate.release()

    @router.get('/query/configuration')
    def configuration():
        return run(lambda value: configuration_identity(value.config))

    @router.post('/query')
    def query(body: QueryInput):
        return run(lambda value: {'configuration': configuration_identity(value.config), 'vector': value.encode(body.text)})

    @router.post('/query/token-count')
    def count(body: CountInput):
        return run(lambda value: {'configuration': configuration_identity(value.config), 'count': value.count_context_tokens(body.text)})

    return router
