"""Schema versions and optional Rich console objects."""

from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "palsu-prospectus-v3.0"


MANIFEST_SCHEMA_VERSION = "palsu-prospectus-batch-manifest-v3.0"


try:  # optional pretty terminal output
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import track
    from rich.prompt import Confirm, Prompt
    from rich.table import Table

    RICH_AVAILABLE = True
    console: Any = Console()
except Exception:  # pragma: no cover - cosmetic only
    RICH_AVAILABLE = False
    console = None
