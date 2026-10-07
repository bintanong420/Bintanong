"""Shared base for every contract: explicit schema version, no unknown fields, immutable, strict.

The closed vocabularies are loaded from knowledge/manifests/governance-vocabulary.json, the single
source of truth. Nothing here approves a source, an edition or a curriculum.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
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



def canonical_json(model: BaseModel) -> str:
    """Sorted keys, two-space indent, LF line ends, one trailing newline."""
    return json.dumps(model.model_dump(mode="json"), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------------------------
# Namespaces: institutional ids and private session ids never mix.
# --------------------------------------------------------------------------------------------
def namespace_of(identifier: str) -> str | None:
    for name, spec in VOCAB["namespaces"].items():
        if any(identifier.startswith(p) and len(identifier) > len(p) for p in spec["id_prefixes"]):
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
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, (list, tuple)):
        for value in node:
            yield from _strings(value)


def foreign_ids(data: Any, namespace: str) -> list[str]:
    """Every string in `data` that is an id of a namespace other than `namespace`."""
    foreign = [p for other, spec in VOCAB["namespaces"].items() if other != namespace for p in spec["id_prefixes"]]
    return [s for s in _strings(data) if any(re.fullmatch(re.escape(p) + r"[a-z0-9-]+", s) for p in foreign)]


def reject_foreign_ids(model: Any, namespace: str) -> None:
    data = model.model_dump(mode="json") if isinstance(model, BaseModel) else model
    found = foreign_ids(data, namespace)
    if found:
        raise ValueError(f"id(s) {sorted(set(found))} belong to another namespace than {namespace}")


__all__ = ["VOCAB", "VOCAB_PATH", "Contract", "ContractError", "Record", "ValidationError", "canonical_json",
           "foreign_ids", "load_vocabulary", "namespace_of", "reject_foreign_ids", "require_namespace",
           "State", "Role", "EvidenceKind", "Outcome"]
