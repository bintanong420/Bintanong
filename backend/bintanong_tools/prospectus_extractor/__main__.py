"""Entry point for ``python -m …prospectus_extractor`` and ``python path/to/prospectus_extractor``."""

import sys
from pathlib import Path

if __package__:
    from .cli import main
else:  # started by path: make the package importable by its own name
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from prospectus_extractor.cli import main

sys.exit(main())
