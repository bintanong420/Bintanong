"""Default source locations follow the ignored repository-root dataset."""
from pathlib import Path

from backend.bintanong_tools.prospectus_extractor import paths


def test_default_inputs_use_root_dataset_without_requiring_real_sources():
    corpus = Path(__file__).resolve().parents[1] / 'dataset' / 'PalSU Undergraduate Prospectus Website Dump'
    assert paths.find_default_input_root() == corpus
    assert paths.DEFAULT_TARGET_PDF.is_relative_to(corpus)
    assert paths.DEFAULT_SEMANTIC_DOC.is_relative_to(corpus)
