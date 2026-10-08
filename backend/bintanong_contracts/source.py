"""SourceSpan, Chunk and token counts.

A span points at exact printed text in one byte identity. A chunk keeps the printed source_text apart
from explanatory text, which must equal the text of its spans; an anchored chunk needs at least one
located span, and an unanchored chunk can never assert a verified source. A verified or rejected claim
needs a register binding, and binding a chunk to a register version is explicit and checked.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Mapping
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, Field, model_validator

from .base import (Contract, ContractError, Record, State, is_pinned_revision, is_plain_filename,
                   reject_foreign_ids, scan_form)
from .governance import ID_DOC, ID_EDITION, ID_VER, SHA256, SourceDocumentVersion

_Finite = Annotated[float, Field(allow_inf_nan=False)]
_Name = Annotated[str, Field(min_length=1)]
# Keys that would claim a privileged status. A chunk carries none, at any depth; the register is the only
# authority. Keys are compared case-insensitively with spaces and hyphens read as underscores.
PRIVILEGED_KEYS = frozenset({
    "approved", "approval", "approval_id", "verified", "verification", "source_verification",
    "promotion_status", "status", "institutional_approval", "authorized", "extractor_status", "review_status"})
# Stems of words that claim a status ("is_approved", "promotionstatus", "reviewed_by", "verified_by",
# "authorized"). A key containing one, after invisible characters, punctuation, case and look-alike letters
# are removed, is privileged too. A short closed list, owner-reviewable; none of the keys the extractor
# emits ("course_code", "derived_fields", "content_review", ...) contains a stem.
PRIVILEGED_STEMS = ("approv", "verif", "promot", "reviewed", "authoriz")
_TOKENIZER_METHOD = re.compile(r"tokenizer:(?P<id>[^@\s]+)@(?P<revision>[^@\s]+)")


def normalized_key(key: Any) -> str:
    return re.sub(r"[\s\-]+", "_", str(key).strip().casefold())


def is_privileged_key(key: Any) -> bool:
    squashed = re.sub(r"[^a-z0-9]", "", scan_form(str(key)))
    return normalized_key(key) in PRIVILEGED_KEYS or any(stem in squashed for stem in PRIVILEGED_STEMS)


def privileged_key_paths(node: Any, path: str = "") -> list[str]:
    """Paths of every privileged status key anywhere inside `node` (dicts and lists, any depth)."""
    found: list[str] = []
    if isinstance(node, Mapping):
        for key, value in node.items():
            here = f"{path}/{key}"
            if is_privileged_key(key):
                found.append(here)
            found += privileged_key_paths(value, here)
    elif isinstance(node, (list, tuple)):
        for value in node:
            found += privileged_key_paths(value, path)
    return found


class FrozenDict(dict):
    """A dict that refuses every mutation, so a validated mapping stays as validated."""

    def _blocked(self, *args, **kwargs):
        raise TypeError("this mapping is immutable")

    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = __ior__ = _blocked

    def __reduce__(self):
        return (FrozenDict, (dict(self),))


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return FrozenDict({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    return value


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
        elif self.exact:
            m = _TOKENIZER_METHOD.fullmatch(self.method)
            if m is None or not is_pinned_revision(m.group("revision")):
                raise ValueError("an exact count must name its tokenizer as 'tokenizer:<id>@<pinned revision>' "
                                 "with a non-empty id and a full lowercase commit or digest")
            if self.count == 0:
                raise ValueError("an exact count of 0 is not a count (a tokenized chunk has at least one token)")
        if not self.exact and self.includes_prefix_and_special_tokens:
            raise ValueError("only an exact count can claim prefix/special-token coverage")
        return self


# --------------------------------------------------------------------------------------------
# SourceSpan
# --------------------------------------------------------------------------------------------
class SpanLocator(Record):
    kind: Literal["table_cells", "text_item", "docling_ref", "section"]
    table_index: int | None = Field(ge=0)
    cell_ids: tuple[_Name, ...]
    item_ids: tuple[_Name, ...]
    ref: str | None
    section_path: tuple[_Name, ...] = ()

    @model_validator(mode="after")
    def _by_kind(self):
        for ids in (self.cell_ids, self.item_ids):
            if len(set(ids)) != len(ids):
                raise ValueError("duplicate ids in one locator")
        if self.kind == "table_cells":
            ok = (self.table_index is not None and self.cell_ids and not self.item_ids and self.ref is None
                  and not self.section_path)
        elif self.kind == "text_item":
            ok = (self.item_ids and not self.cell_ids and self.table_index is None and self.ref is None
                  and not self.section_path)
        elif self.kind == "section":
            ok = (self.section_path and not self.cell_ids and not self.item_ids and self.table_index is None
                  and self.ref is None)
        else:
            ok = (bool(self.ref) and not self.cell_ids and not self.item_ids and self.table_index is None
                  and not self.section_path)
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
    # `page` is the physical page of the cited bytes. When those bytes are one part of a split PDF,
    # these name the page in the original document (original_page = page + page_offset).
    original_page: int | None = Field(default=None, ge=1)
    page_offset: int | None = Field(default=None, ge=0)

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
        if (self.original_page is not None or self.page_offset is not None) and (self.page is None or self.byte_sha256 is None):
            raise ValueError("original_page and page_offset need the physical page and the byte digest")
        if self.page_offset is not None and self.original_page is not None and self.original_page != self.page + self.page_offset:
            raise ValueError("original_page must equal the physical page plus page_offset")
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


def compute_content_hash(source_text: str | None, text: str) -> str:
    """Same algorithm as the prospectus extractor's content_hash, so ids and hashes carry over. A chunk with
    no printed text (a table serialization) hashes its own text in the printed slot: the extractor hashes
    Docling's serialization as source_text and drops source_text afterwards."""
    payload = json.dumps([canonical_text(text if source_text is None else source_text), canonical_text(text)],
                         ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def joined_span_text(spans) -> str:
    """The printed text the spans carry, in span order (spans without text contribute nothing)."""
    return canonical_text(" ".join(canonical_text(s.text) for s in spans if s.text is not None))


def span_identity(span: SourceSpan) -> tuple:
    """Two spans with the same identity are the same span written twice. Distinct spans may share a cell."""
    return (span.byte_sha256, span.page, span.locator.model_dump_json(), span.text)


class RegisterBinding(Record):
    """Which register evidence a chunk's verification and content-review claims rest on."""

    verification_evidence_ref: str | None
    content_review_evidence_ref: str | None


def _freeze_fields(value: dict[str, Any]) -> dict[str, Any]:
    return _freeze(value)


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
    source_text: str | None
    spans: tuple[SourceSpan, ...]
    section_path: tuple[_Name, ...]
    scope: tuple[_Name, ...]
    content_hash: str = Field(pattern=SHA256)
    token_count: TokenCount
    source_label: str
    type_fields: Annotated[dict[str, Any], AfterValidator(_freeze_fields)]
    register_binding: RegisterBinding | None = None

    @model_validator(mode="after")
    def _rules(self):
        errs: list[str] = []
        try:
            reject_foreign_ids(self, "institutional")
        except ValueError as exc:
            errs.append(str(exc))
        if self.content_hash != compute_content_hash(self.source_text, self.text):
            errs.append("content_hash does not match source_text and text (stale or altered)")
        paths = privileged_key_paths(self.type_fields)
        if paths:
            errs.append(f"type_fields carries privileged status key(s) {sorted(paths)}; only the register can")
        if self.source_label and not is_plain_filename(self.source_label):
            errs.append("source_label is not a plain file name (path, drive, scheme or control character)")
        errs += self._status_claims()
        if self.anchored != (self.byte_sha256 is not None):
            errs.append("anchored must be true exactly when byte_sha256 is present")
        if self.anchored:
            errs += self._anchored_rules()
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

    def _status_claims(self) -> list[str]:
        errs, rb, bound = [], self.register_binding, self.version_id is not None
        if rb is not None:
            if not bound:
                errs.append("register_binding on a chunk bound to no version")
            if (rb.verification_evidence_ref is None) != (self.source_verification == "pending"):
                errs.append("register_binding.verification_evidence_ref must be present exactly when "
                            "source_verification is not pending")
            if (rb.content_review_evidence_ref is None) != (self.content_review == "pending"):
                errs.append("register_binding.content_review_evidence_ref must be present exactly when "
                            "content_review is not pending")
        else:
            if self.source_verification not in ("pending", "observed"):
                errs.append(f"source_verification {self.source_verification!r} needs a register_binding")
            if bound and self.content_review != "pending":
                errs.append(f"content_review {self.content_review!r} on a bound chunk needs a register_binding")
        return errs

    def _anchored_rules(self) -> list[str]:
        errs = []
        if not self.spans:
            errs.append("an anchored chunk needs at least one source span")
        for i, s in enumerate(self.spans):
            if s.byte_sha256 != self.byte_sha256:
                errs.append(f"span {i} digest differs from the chunk digest")
            if s.page is None:
                errs.append(f"span {i} has no physical page")
            if self.source_text is not None and not (s.text and s.text.strip()):
                errs.append(f"span {i} carries no printed text but the chunk asserts source_text")
            if self.source_text is None and s.text is not None:
                errs.append(f"span {i} carries printed text but the chunk has no source_text")
        if self.source_text is not None:
            if not self.source_text.strip():
                errs.append("an anchored chunk with a source_text needs printed source_text, not blank text")
            elif not errs and canonical_text(self.source_text) != joined_span_text(self.spans):
                errs.append("source_text differs from the span text (printed text must be the spans' text, in order)")
        if any(s.version_id not in (None, self.version_id) for s in self.spans):
            errs.append("a span names a different source version than the chunk")
        identities = [span_identity(s) for s in self.spans]
        if len(set(identities)) != len(identities):
            errs.append("identical span repeated within one chunk")
        if self.source_verification != "pending" and (self.version_id is None or self.edition_id is None):
            errs.append("a verification claim needs a bound version and edition")
        return errs


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
    if chunk.content_review != version.content_review_state.state:
        errs.append(f"stale or inflated content review claim {chunk.content_review!r}; "
                    f"register says {version.content_review_state.state!r}")
    rb = chunk.register_binding
    for label, got, want in (
            ("verification", rb.verification_evidence_ref if rb else None, version.verification_state.evidence_ref),
            ("content review", rb.content_review_evidence_ref if rb else None, version.content_review_state.evidence_ref)):
        if got != want:
            errs.append(f"{label} evidence reference {got!r} differs from the register's {want!r}")
    if errs:
        raise ContractError("; ".join(errs))


def bind_chunk(chunk: Chunk, version: SourceDocumentVersion) -> Chunk:
    """A copy of `chunk` bound to `version`. Both states and their evidence references are copied from the
    register, never raised: an extractor's content-review label is replaced by the register's state."""
    if not chunk.anchored:
        raise ContractError("an unanchored chunk cannot be bound to a source version")
    data = chunk.model_dump(mode="json")
    data.update(version_id=version.version_id, edition_id=version.edition_id, document_id=version.document_id,
                source_verification=version.verification_state.state,
                content_review=version.content_review_state.state,
                register_binding={"verification_evidence_ref": version.verification_state.evidence_ref,
                                  "content_review_evidence_ref": version.content_review_state.evidence_ref})
    for s in data["spans"]:
        s["version_id"] = version.version_id
    bound = Chunk.parse(data)
    check_chunk_binding(bound, version)
    return bound


__all__ = ["Chunk", "SourceSpan", "SpanLocator", "Extraction", "TokenCount", "RegisterBinding", "FrozenDict",
           "PRIVILEGED_KEYS", "bind_chunk", "canonical_text", "check_chunk_binding", "check_span_binding",
           "compute_content_hash", "joined_span_text", "privileged_key_paths"]
