"""Local review GUI for one prospectus candidate: PDF page, markup twin and extracted JSON side by side, one question
at a time, answers written to the decision ledger.

    python -m backend.bintanong_tools.prospectus_review --candidate candidate.json --pdf original.pdf
"""

from __future__ import annotations

from .prospectus_review_gui.cli import review_main as main

if __name__ == "__main__":
    raise SystemExit(main())
