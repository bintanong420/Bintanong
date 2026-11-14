"""PalSU prospectus extractor: original PDF (via Docling) to source-linked curriculum JSON.

Outputs are review candidates. An extractor audit of ``ok`` is not institutional
approval; see plans/2026-09-26-prospectus-phase2-implementation-draft.md.

Run it with any of::

    python -m bintanong_tools.prospectus_extractor --self-test
    python path/to/prospectus_extractor -i prospectus.pdf -o out.json --export-csv --strict
    python -m backend.bintanong_tools.prospectus_batch -i PDF_FOLDER -o NEW_RUN_FOLDER

Status fields: ``extraction_audit`` (ok, warn or error) is the extractor's own check.
``content_review`` is ``pending`` unless a decision ledger for the same PDF says otherwise. ``source_verification`` comes
from the source record and is ``pending`` unless a human verified the source. The legacy
``promotion_status`` is not approval; ``authority.eligibility_executable`` is false for
everything the extractor produces.
"""

from .batch import BatchConfig, build_batch_items, run_batch, scan_inputs
from .cli import main
from .common import MANIFEST_SCHEMA_VERSION, SCHEMA_VERSION
from .evidence import LoadedDocument, NormalizedCell, NormalizedTable, ProspectusEvidence
from .loader import evidence_adapter, load_document
from .parse import parse_curriculum_evidence
from .pipeline import build_essentials, build_payload, process_prospectus
from .selftest import run_self_tests

__all__ = [
    "BatchConfig", "LoadedDocument", "MANIFEST_SCHEMA_VERSION", "NormalizedCell", "NormalizedTable",
    "ProspectusEvidence", "SCHEMA_VERSION", "build_batch_items", "build_essentials", "build_payload",
    "evidence_adapter", "load_document", "main", "parse_curriculum_evidence", "process_prospectus",
    "run_batch", "run_self_tests", "scan_inputs",
]
