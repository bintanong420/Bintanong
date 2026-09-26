"""Hash-bound source identity for review-only prospectus work."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class ProvisionalSource:
    pdf_sha256: str
    source_locator: str
    source_verification: Literal["pending"] = field(default="pending", init=False)

    def verify_pdf(self, pdf_path: Path) -> None:
        with pdf_path.open("rb") as pdf:
            actual_hash = hashlib.file_digest(pdf, "sha256").hexdigest()
        if actual_hash != self.pdf_sha256:
            raise ValueError(f"PDF hash mismatch for {pdf_path}")
