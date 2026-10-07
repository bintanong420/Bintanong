"""EmbeddingRecord: validation of an embedding's identity and shape. It makes no embedding calls.

A record names the chunk and the chunk content it was computed from (so a changed chunk makes it
stale), the exact model revision, tokenizer/preprocessing/prompt fingerprints, dimension,
normalization and vector. Its token count must be an exact tokenizer count that includes prefixes
and special tokens; an estimate never satisfies that.
"""

from __future__ import annotations

import math
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .base import Contract, ContractError
from .governance import SHA256
from .source import Chunk, TokenCount

FLOATING_REFS = {"main", "master", "latest", "head"}
_Finite = Annotated[float, Field(allow_inf_nan=False)]


class EmbeddingRecord(Contract):
    SCHEMA_VERSION = "bintanong-embedding-record-v1"
    chunk_id: str = Field(pattern=SHA256)
    chunk_content_hash: str = Field(pattern=SHA256)
    model_id: str = Field(min_length=1)
    model_revision: str = Field(min_length=1)
    tokenizer_fingerprint: str = Field(pattern=SHA256)
    preprocessing_fingerprint: str = Field(pattern=SHA256)
    prompt_fingerprint: str = Field(pattern=SHA256)
    dimension: int = Field(ge=1)
    normalization: Literal["l2", "none"]
    vector: tuple[_Finite, ...]
    token_count: TokenCount

    @model_validator(mode="after")
    def _rules(self):
        errs = []
        if self.model_revision.lower() in FLOATING_REFS:
            errs.append("model_revision must be a pinned revision, not a floating reference")
        if len(self.vector) != self.dimension:
            errs.append(f"vector has {len(self.vector)} values, dimension says {self.dimension}")
        norm = math.sqrt(sum(v * v for v in self.vector))
        if self.normalization == "l2" and not math.isclose(norm, 1.0, abs_tol=1e-3):
            errs.append(f"declared l2-normalized but the norm is {norm:.6f}")
        if self.normalization == "none" and norm == 0.0:
            errs.append("a zero vector is not an embedding")
        tc = self.token_count
        if not (tc.exact and tc.includes_prefix_and_special_tokens):
            errs.append("token_count must be an exact tokenizer count including prefixes and special tokens")
        if errs:
            raise ValueError("; ".join(errs))
        return self


def check_embedding_matches_chunk(record: EmbeddingRecord, chunk: Chunk) -> None:
    if record.chunk_id != chunk.chunk_id:
        raise ContractError("embedding belongs to another chunk")
    if record.chunk_content_hash != chunk.content_hash:
        raise ContractError("embedding is stale: the chunk content changed after it was embedded")
