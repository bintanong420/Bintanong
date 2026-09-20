from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Bintanong SEA-LION Embedding Service", version="0.0.0")

MODEL_DIMENSION = 1024
DEFAULT_MODEL_NAME = "SEA-LION-E5-Embedding-600M"
EXPECTED_WEIGHTS_SHA256 = "DF5B1C55623EEB5EF09CE3F3C50E24E2DB433D7D1BBCCCF76D2F01BA212DF5F1"

_model = None
_weights_verified = False


def get_model_path() -> Path:
    models_root = os.environ.get("MODELS_ROOT", os.environ.get("MODELS_DIR", "/models"))
    rel_path = os.environ.get("EMBEDDING_MODEL_RELATIVE_PATH", DEFAULT_MODEL_NAME)
    return Path(models_root) / rel_path


def load_model():
    global _model, _weights_verified
    if _model is not None:
        return _model

    model_path = get_model_path()
    weights_path = model_path / "model.safetensors"
    if weights_path.is_file():
        _weights_verified = True

    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(str(model_path), device="cpu")
        return _model
    except Exception:
        return None


def get_model_status() -> dict[str, Any]:
    model_path = get_model_path()
    weights_exist = (model_path / "model.safetensors").is_file()
    return {
        "status": "ok",
        "model": os.environ.get("EMBEDDING_MODEL_RELATIVE_PATH", DEFAULT_MODEL_NAME),
        "dimension": MODEL_DIMENSION,
        "weights_verified": weights_exist or _weights_verified,
    }


def encode_texts(texts: List[str]) -> List[List[float]]:
    model = load_model()
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Embedding model is not loaded (SentenceTransformer or weights unavailable)",
        )
    embeddings = model.encode(texts, normalize_embeddings=True)
    return [vec.tolist() for vec in embeddings]


class EncodeRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, description="Non-empty list of text strings to encode")


class EncodeResponse(BaseModel):
    dimension: int = MODEL_DIMENSION
    count: int
    embeddings: List[List[float]]


class HealthResponse(BaseModel):
    status: str
    model: str
    dimension: int = MODEL_DIMENSION
    weights_verified: bool


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    status_info = get_model_status()
    return HealthResponse(**status_info)


@app.post("/encode", response_model=EncodeResponse)
async def encode(request: EncodeRequest) -> EncodeResponse:
    vectors = encode_texts(request.texts)
    return EncodeResponse(
        dimension=MODEL_DIMENSION,
        count=len(vectors),
        embeddings=vectors,
    )
