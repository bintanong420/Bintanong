"""Review sheets and a decision ledger for the year/semester sections of a prospectus candidate.

    python -m backend.bintanong_tools.prospectus_fixer sheet --candidate candidate.json --pdf original.pdf
"""

from __future__ import annotations

from .prospectus_extractor.fixer_cli import fixer_main as main

if __name__ == "__main__":
    raise SystemExit(main())