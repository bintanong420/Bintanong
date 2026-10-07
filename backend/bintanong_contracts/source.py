"""SourceSpan, Chunk and token counts.

A span points at exact printed text in one byte identity. A chunk keeps the printed source_text apart
from explanatory text, needs at least one complete span when anchored, and an unanchored chunk can
never assert a verified source. Binding a chunk to a register version is explicit and checked.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Annotated, Any, Literal

from pydantic import Field, model_validator

from .base import Contract, ContractError, Record, State, reject_foreign_ids
from .governance import ID_DOC, ID_EDITION, ID_VER, SHA256, SourceDocumentVersion

_LOCAL_PATH = re.compile(r"^([A-Za-z]:[\\/]|[\\/])")
_Finite = Annotated[float, Field(allow_inf_nan=False)]
_Name = Annotated[str, Field(min_length=1)]
# Keys that would claim a privileged status. A chunk carries none; the register is the only authority.
PRIVILEGED_KEYS = frozenset({
    "approved", "approval", "approval_id", "verified", "verification", "source_verification",
    "promotion_status", "status", "institutional_approval", "authorized"})


# --------------------------------------------------------------------------------------------
# Token counts
# --------------------------------------------------------------------------------------------
class TokenCount(Record):
    """`exact` is true only for a tokenizer-defined count. An estimate never claims it."""

    count: int = Field(ge=0)
    method: _Name
    exact: bool
    includes_prefix_and_special_tokens: bool

    @model_validator(mode="after")
    def _honest(self):
        if self.method.startswith("estimate"):
            if self.exact or self.includes_prefix_and_special_tokens:
                raise ValueError("an estimate cannot claim an exact count or prefix/special-token coverage")
        elif self.exact and not self.method.startswith("tokenizer:"):
            raise ValueError("an exact count must name its tokenizer as 'tokenizer:<id>@<revision>'")
        if not self.exact and self.includes_prefix_and_special_tokens:
            raise ValueError("only an exact count can claim prefix/special-token coverage")
        return self


# --------------------------------------------------------------------------------------------
# SourceSpan
# --------------------------------------------------------------------------------------------
class SpanLocator(Record):
    kind: Literal["table_cells", "text_item", "docling_ref"]
    table_index: int | None = Field(ge=0)
    cell_ids: tuple[_Name, ...]
    item_ids: tuple[_Name, ...]
    ref: str | None

    @model_validator(mode="after")
    def _by_kind(self):
        for ids in (self.cell_ids, self.item_ids):
            if len(set(ids)) != len(ids):
                raise ValueError("duplicate ids in one locator")
        if self.kind == "table_cells":
            ok = self.table_index is not None and self.cell_ids and not self.item_ids and self.ref is None
        elif self.kind == "text_item":
            ok = self.item_ids and not self.cell_ids and self.table_index is None and self.ref is None
        else:
            ok = bool(self.ref) and not self.cell_ids and not self.item_ids and self.table_index is None
        if not ok:
            raise ValueError(f"locator fields do not fit kind {self.kind!r}")
        return self


class Extraction(Record):
    source_kind: _Name
    resolution_method: _Name
    repair_id: str | None
    ocr_confidence: float | None = Field(ge=0.0, le=1.0)


class SourceSpan(Contract):
    SCHEMA_VERSION = "bintanong-source-span-v1"
    byte_sha256: str | None = Field(pattern=SHA256)
    version_id: str | None = Field(pattern=ID_VER)
    page: int | None = Field(ge=1)
    printed_page_label: str | None = Field(min_length=1)
    locator: SpanLocator
    text: str | None
    bbox: tuple[_Finite, _Finite, _Finite, _Finite] | None
    bbox_origin: Literal["TOPLEFT", "BOTTOMLEFT"] | None
    page_size: tuple[_Finite, _Finite] | None
    extraction: Extraction

    @property
    def anchored(self) -> bool:
        return self.byte_sha256 is not None

    @property
    def is_complete(self) -> bool:
        return self.anchored and self.page is not None and bool(self.text and self.text.strip())

    @model_validator(mode="after")
    def _rules(self):
        if self.byte_sha256 is None and self.version_id is not None:
            raise ValueError("a span with no byte digest cannot claim a source version")
        if self.page_size is not None and min(self.page_size) <= 0:
            raise ValueError("page_size must be positive")
        if self.bbox is None:
            return self
        if self.bbox_origin is None or self.page_size is None or self.page is None or self.byte_sha256 is None:
            raise ValueError("a bounding box needs its origin, the page size, the page and the byte digest")
        left, top, right, bottom = self.bbox
        width, height = self.page_size
        if not left < right:
            raise ValueError("bbox x range is empty or inverted")
        low, high = (top, bottom) if self.bbox_origin == "TOPLEFT" else (bottom, top)
        if not low < high:
            raise ValueError(f"bbox y range is empty or inverted for origin {self.bbox_origin}")
        if left < 0 or right > width or low < 0 or high > height:
            raise ValueError("bbox lies outside the page")
        return self


def check_span_binding(span: SourceSpan, version: SourceDocumentVersion) -> None:
    if not span.anchored:
        raise ContractError("an unanchored span cannot be bound to a source version")
    if span.byte_sha256 != version.byte_sha256:
        raise ContractError("span digest does not match the registered bytes (source mutated or other edition)")
    if span.version_id is not None and span.version_id != version.version_id:
        raise ContractError(f"span names version {span.version_id}, register has {version.version_id}")


# --------------------------------------------------------------------------------------------
# Chunk
# --------------------------------------------------------------------------------------------
def canonical_text(text: Any) -> str:
    return unicodedata.normalize("NFC", " ".join(str(text).split()))


def compute_content_hash(source_text: str, text: str) -> str:
    """Same algorithm as the prospectus extractor's content_hash, so ids and hashes carry over."""
    payload = json.dumps([canonical_text(source_text), canonical_text(text)], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _locations(span: SourceSpan):
    loc = span.locator
    ids = [("cell", loc.table_index, i) for i in loc.cell_ids] + [("item", None, i) for i in loc.item_ids]
    if loc.ref:
        ids.append(("ref", None, loc.ref))
    return [(span.byte_sha256, span.page, *i) for i in ids]


class Chunk(Contract):
    SCHEMA_VERSION = "bintanong-chunk-v1"
    chunk_id: str = Field(pattern=SHA256)
    chunk_type: _Name
    chunker_version: _Name
    edition_id: str | None = Field(pattern=ID_EDITION)
    document_id: str | None = Field(pattern=ID_DOC)
    version_id: str | None = Field(pattern=ID_VER)
    byte_sha256: str | None = Field(pattern=SHA256)
    anchored: bool
    source_verification: State("verification_state")
    content_review: State("content_review_state")
    text: str
    source_text: str
    spans: tuple[SourceSpan, ...]
    section_path: tuple[_Name, ...]
    scope: tuple[_Name, ...]
    content_hash: str = Field(pattern=SHA256)
    token_count: TokenCount
    source_label: str
    type_fields: dict[str, Any]

    @model_validator(mode="after")
    def _rules(self):
        errs: list[str] = []
        try:
            reject_foreign_ids(self, "institutional")
        except ValueError as exc:
            errs.append(str(exc))
        if self.content_hash != compute_content_hash(self.source_text, self.text):
            errs.append("content_hash does not match source_text and text (stale or altered)")
        bad_keys = sorted(k for k in self.type_fields if k.lower() in PRIVILEGED_KEYS)
        if bad_keys:
            errs.append(f"type_fields carries privileged status key(s) {bad_keys}; only the register can")
        if _LOCAL_PATH.match(self.source_label):
            errs.append("source_label looks like a local path")
        if self.anchored != (self.byte_sha256 is not None):
            errs.append("anchored must be true exactly when byte_sha256 is present")
        if self.anchored:
            if not self.spans:
                errs.append("an anchored chunk needs at least one complete source span")
            for i, s in enumerate(self.spans):
                if not s.is_complete:
                    errs.append(f"span {i} is incomplete (needs byte digest, physical page and printed text)")
                if s.byte_sha256 != self.byte_sha256:
                    errs.append(f"span {i} digest differs from the chunk digest")
            if not self.source_text.strip():
                errs.append("an anchored chunk needs printed source_text")
            seen = [loc for s in self.spans for loc in _locations(s)]
            if len(set(seen)) != len(seen):
                errs.append("duplicate source location across spans")
            if self.source_verification != "pending" and (self.version_id is None or self.edition_id is None):
                errs.append("a verification claim needs a bound version and edition")
        else:
            if any(s.anchored for s in self.spans):
                errs.append("an unanchored chunk cannot hold anchored spans")
            if self.source_verification != "pending":
                errs.append("an unanchored chunk cannot assert a source verification state")
            if self.version_id or self.edition_id or self.document_id:
                errs.append("an unanchored chunk cannot name a source version, edition or document")
        if errs:
            raise ValueError("; ".join(errs))
        return self


def check_chunk_binding(chunk: Chunk, version: SourceDocumentVersion) -> None:
    """The chunk's claims must not exceed, or lag, what the register says."""
    if not chunk.anchored:
        raise ContractError("an unanchored chunk cannot be bound to a source version")
    errs = []
    if chunk.byte_sha256 != version.byte_sha256:
        errs.append("chunk digest does not match the registered bytes (source mutated or other edition)")
    for name in ("version_id", "edition_id", "document_id"):
        if getattr(chunk, name) != getattr(version, name):
            errs.append(f"{name} {getattr(chunk, name)!r} != register {getattr(version, name)!r}")
    if version.acquisition_state.state == "mismatch":
        errs.append("the register records an acquisition mismatch for these bytes")
    if chunk.source_verification != version.verification_state.state:
        errs.append(f"stale or inflated verification claim {chunk.source_verification!r}; "
                    f"register says {version.verification_state.state!r}")
    errs += [f"span {i}: {e}" for i, s in enumerate(chunk.spans) for e in _span_errors(s, version)]
    if errs:
        raise ContractError("; ".join(errs))


def _span_errors(span: SourceSpan, version: SourceDocumentVersion) -> list[str]:
    try:
        check_span_binding(span, version)
    except ContractError as exc:
        return [str(exc)]
    return []


def bind_chunk(chunk: Chunk, version: SourceDocumentVersion) -> Chunk:
    """A copy of `chunk` bound to `version`. The verification state is copied from the register, never raised."""
    if not chunk.anchored:
        raise ContractError("an unanchored chunk cannot be bound to a source version")
    if chunk.byte_sha256 != version.byte_sha256:
        raise ContractError("chunk digest does not match the registered bytes (source mutated or other edition)")
    data = chunk.model_dump(mode="json")
    data.update(version_id=version.version_id, edition_id=version.edition_id, document_id=version.document_id,
                source_verification=version.verification_state.state)
    for s in data["spans"]:
        s["version_id"] = version.version_id
    bound = Chunk.parse(data)
    check_chunk_binding(bound, version)
    return bound


__all__ = ["Chunk", "SourceSpan", "SpanLocator", "Extraction", "TokenCount", "PRIVILEGED_KEYS",
           "bind_chunk", "canonical_text", "check_chunk_binding", "check_span_binding", "compute_content_hash"]
