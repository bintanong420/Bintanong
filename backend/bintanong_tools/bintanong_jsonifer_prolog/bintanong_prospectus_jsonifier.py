#!/usr/bin/env python3
"""Compatibility entry point for the PalSU prospectus extractor.

The code now lives in ``bintanong_tools/prospectus_extractor/``. This file keeps
older commands and imports working: it re-exports every name the single-file
version defined and runs the same CLI.

    python bintanong_prospectus_jsonifier.py --self-test
    python bintanong_prospectus_jsonifier.py -i prospectus.pdf --export-pl --export-csv
"""

import importlib
import pkgutil
import sys
from pathlib import Path

if __package__:
    _package = importlib.import_module("..prospectus_extractor", __package__)
else:  # started by path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    _package = importlib.import_module("prospectus_extractor")

for _info in pkgutil.iter_modules(_package.__path__):
    if _info.name != "__main__":
        _module = importlib.import_module(f"{_package.__name__}.{_info.name}")
        globals().update({k: v for k, v in vars(_module).items() if not k.startswith("__")})

if __name__ == "__main__":
    sys.exit(main())  # noqa: F821 - re-exported from prospectus_extractor.cli
