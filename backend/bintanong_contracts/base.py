"""Shared base for every contract: explicit schema version, no unknown fields, immutable, strict.

The closed vocabularies are loaded from knowledge/manifests/governance-vocabulary.json, the single
source of truth. Nothing here approves a source, an edition or a curriculum.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, ClassVar

from pydantic import AfterValidator, BaseModel, ConfigDict, ValidationError, field_validator

VOCAB_PATH = Path(__file__).resolve().parents[2] / "knowledge" / "manifests" / "governance-vocabulary.json"


class ContractError(ValueError):
    """A contract rule was broken outside a model validator; the message names the reason."""


def load_vocabulary(path: Path = VOCAB_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


VOCAB = load_vocabulary()


def State(group: str):
    """A string that must be one of VOCAB['states'][group]."""
    return _member(tuple(VOCAB["states"][group]), group)


def Role():
    return _member(tuple(VOCAB["roles"]), "role")


def EvidenceKind():
    ev = VOCAB["evidence_kinds"]
    return _member(tuple(ev["authorizing"]) + tuple(ev["non_authorizing"]), "evidence kind")


def Outcome():
    return _member(tuple(VOCAB["decision"]["outcomes"]), "decision outcome")


def Route():
    return _member(tuple(VOCAB["runtime"]["routes"]), "route")


def Control():
    return _member(tuple(VOCAB["runtime"]["controls"]), "control outcome")


def _member(values: tuple[str, ...], label: str):
    def check(value: str) -> str:
        if value not in values:
            raise ValueError(f"{value!r} is not a {label} in the governance vocabulary")
        return value
    return Annotated[str, AfterValidator(check)]


class Record(BaseModel):
    """A nested value: extra forbidden, frozen, strict. Top-level contracts add a schema version."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    @classmethod
    def parse(cls, data: Any):
        """Parse JSON text or a JSON-compatible mapping with strict types."""
        if isinstance(data, (str, bytes)):
            return cls.model_validate_json(data)
        if isinstance(data, Mapping):
            try:
                text = json.dumps(data, allow_nan=False)
            except (TypeError, ValueError) as exc:
                raise ContractError(f"not JSON-compatible: {exc}") from exc
            return cls.model_validate_json(text)
        raise ContractError(f"cannot parse {type(data).__name__} as {cls.__name__}")


class Contract(Record):
    """Base: extra forbidden, frozen, strict, and an exact schema_version."""

    SCHEMA_VERSION: ClassVar[str]
    schema_version: str

    @field_validator("schema_version")
    @classmethod
    def _known_version(cls, value: str) -> str:
        if value != cls.SCHEMA_VERSION:
            raise ValueError(f"unknown schema_version {value!r}; this contract is {cls.SCHEMA_VERSION}")
        return value



# --------------------------------------------------------------------------------------------
# Shared text rules: plain file names, logical locators, real timestamps
# --------------------------------------------------------------------------------------------
# A file name is a plain name: no directory part, drive, scheme, backslash or control character.
FILENAME_RE = re.compile(r"(?!\.{1,2}\Z)[^\\/:\x00-\x1f]+")
# A logical locator (shelf reference, https URL) must not be a local path, `file:` URL, `~`, `..` or have
# padding or control characters. The same rule as the JSON schema, plus case-insensitive.
LOCATOR_RE = re.compile(
    r"(?!.*(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|\\|(?<![A-Za-z0-9])file:|/Users/|/home/|\.\./))"
    r"(?![/~])[^\x00-\x1f\s][^\x00-\x1f]*", re.IGNORECASE)
TIMESTAMP = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$"
# Default, owner-reviewable: an evidence timestamp outside these years is not a plausible record date.
TIMESTAMP_YEARS = (2000, 2100)


def is_plain_filename(text: str) -> bool:
    return FILENAME_RE.fullmatch(text) is not None


def is_logical_locator(text: str) -> bool:
    return LOCATOR_RE.fullmatch(text) is not None


def parse_timestamp(text: str) -> datetime | None:
    """A real, timezone-aware calendar timestamp inside TIMESTAMP_YEARS, or None."""
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        return None
    if moment.tzinfo is None or not TIMESTAMP_YEARS[0] <= moment.year <= TIMESTAMP_YEARS[1]:
        return None
    return moment


def canonical_json(model: BaseModel) -> str:
    """Sorted keys, two-space indent, LF line ends, one trailing newline."""
    return json.dumps(model.model_dump(mode="json"), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------------------------
# Namespaces: institutional ids and private session ids never mix.
# --------------------------------------------------------------------------------------------
def _all_prefixes() -> dict[str, str]:
    return {p: name for name, spec in VOCAB["namespaces"].items() for p in spec["id_prefixes"]}


def id_pattern(prefix: str) -> str:
    """The id pattern of a vocabulary prefix, so a pattern can never drift from the vocabulary file."""
    if prefix not in _all_prefixes():
        raise KeyError(f"{prefix!r} is not an id prefix in the governance vocabulary")
    return "^" + re.escape(prefix) + "[a-z0-9-]+$"


def namespace_of(identifier: str) -> str | None:
    """The namespace of a whole id: a vocabulary prefix followed by at least one [a-z0-9-] character."""
    for prefix, name in _all_prefixes().items():
        if re.fullmatch(re.escape(prefix) + "[a-z0-9-]+", identifier):
            return name
    return None


def require_namespace(identifier: str, namespace: str) -> str:
    actual = namespace_of(identifier)
    if actual != namespace:
        raise ContractError(f"id {identifier!r} is in namespace {actual!r}, required {namespace!r}")
    return identifier


def _strings(node: Any):
    if isinstance(node, str):
        yield node
    elif isinstance(node, Mapping):
        for key, value in node.items():
            yield from _strings(key)
            yield from _strings(value)
    elif isinstance(node, (list, tuple)):
        for value in node:
            yield from _strings(value)


_DASHES = dict.fromkeys(map(ord, "‐‑‒–—―−﹘﹣－"), "-")


def folded(text: str) -> str:
    """NFKC, dash variants to '-', casefold: what a person reads as the same id. Surrounding whitespace
    never hides a token because tokens are searched anywhere in the string."""
    return unicodedata.normalize("NFKC", text).translate(_DASHES).casefold()


def id_tokens(text: str, prefixes: list[str]) -> list[str]:
    """Id-like tokens starting with one of `prefixes` anywhere in `text`. A token is the prefix plus
    hyphen-joined segments that has a second segment or a digit, so prose such as 'fact-checking' or
    'edition-specific' is not an id. It must not continue a longer word ('xfact-1').
    Known limit: a one-word id without a digit ('doc-handbook') inside free text is not found by this scan;
    structured id fields are still checked by pattern."""
    pattern = r"(?<![a-z0-9])(" + "|".join(re.escape(p) for p in prefixes) + r")([a-z0-9]+(?:-[a-z0-9]+)*)"
    return [m.group(0) for m in re.finditer(pattern, folded(text))
            if "-" in m.group(2) or re.search(r"[0-9]", m.group(2))]


def foreign_ids(data: Any, namespace: str) -> list[str]:
    """Every id-like token, in every string of `data`, that belongs to a namespace other than `namespace`."""
    foreign = [p for p, name in _all_prefixes().items() if name != namespace]
    return [tok for s in _strings(data) for tok in id_tokens(s, foreign)]


def reject_foreign_ids(model: Any, namespace: str) -> None:
    data = model.model_dump(mode="json") if isinstance(model, BaseModel) else model
    found = foreign_ids(data, namespace)
    if found:
        raise ValueError(f"id(s) {sorted(set(found))} belong to another namespace than {namespace}")


__all__ = ["VOCAB", "VOCAB_PATH", "Contract", "ContractError", "Record", "ValidationError", "canonical_json",
           "foreign_ids", "load_vocabulary", "namespace_of", "reject_foreign_ids", "require_namespace",
           "State", "Role", "EvidenceKind", "Outcome", "Route", "Control", "id_pattern", "id_tokens", "folded",
           "is_plain_filename", "is_logical_locator", "parse_timestamp", "TIMESTAMP"]
