from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..prospectus_extractor.loader import _write_bytes_atomic


def encoded(value) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                       separators=(',', ':')) + '\n').encode('utf-8')


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError('non-finite JSON value')

    try:
        if path.stat().st_size > 32 * 1024 * 1024:
            raise ValueError('JSON artifact exceeds 32 MiB')
        return json.loads(path.read_bytes(), object_pairs_hook=unique, parse_constant=nonfinite)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('JSON artifact missing or unreadable') from exc


def contained(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError('artifact needs a relative path')
    path = root / name
    if any(p.is_symlink() for p in (path, *path.parents)) or root.resolve() not in path.resolve().parents:
        raise ValueError('artifact escapes its packet or uses a symlink')
    return path


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_bytes_atomic(path, encoded(value))
