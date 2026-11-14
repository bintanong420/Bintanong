from __future__ import annotations

import hashlib
from pathlib import Path


def compute_file_sha256(file_path: Path, chunk_size: int = 4 * 1024 * 1024) -> str:
    """Compute SHA-256 hash of a file streaming in chunks."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest().upper()


def verify_model_weights(
    model_dir: Path | str,
    expected_sha256: str,
    weights_filename: str = "model.safetensors",
) -> bool:
    """Verify that model weights file exists and matches the expected SHA-256 digest."""
    path = Path(model_dir) / weights_filename
    if not path.is_file():
        return False
    actual_sha = compute_file_sha256(path)
    return actual_sha.upper() == expected_sha256.upper()
