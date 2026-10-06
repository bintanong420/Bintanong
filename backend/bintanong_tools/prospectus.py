"""Hash-bound source identity for review-only prospectus work."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .prospectus_extractor import identity


@dataclass(frozen=True)
class ProvisionalSource:
    pdf_sha256: str
    source_locator: str
    source_verification: Literal["pending"] = field(default="pending", init=False)

    def verify_pdf(self, pdf_path: Path) -> None:
        actual_hash = identity.file_sha256(pdf_path)  # the one PDF-hash owner
        self.verify_digest(actual_hash)

    def verify_digest(self, actual_hash: str) -> None:
        if actual_hash != self.pdf_sha256:
            raise ValueError(f"PDF hash mismatch for {self.source_locator}")
