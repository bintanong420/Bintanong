"""Hand-computed geometry checks for the paper demonstration, not retrieval accuracy."""
import json
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize('module',['scripts.demo_cosine_top_k','backend.algorithms.nearest_neighbors'])
def test_demo_shows_cosine_distance_ranking_and_threshold_before_top_k(module):
    result = subprocess.run(
        [sys.executable, '-B', '-m', module],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        timeout=20, check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report['synthetic'] is True
    assert [r['candidate_id'] for r in report['ranked']] == ['vector-a', 'vector-b', 'vector-c', 'vector-d']
    assert [r['similarity'] for r in report['ranked']] == pytest.approx([1.0, 0.8, 0.0, -1.0])
    assert [r['distance'] for r in report['ranked']] == pytest.approx([0.0, 0.2, 1.0, 2.0])
    assert report['k'] == 3 and report['min_similarity'] == 0.5
    assert [r['candidate_id'] for r in report['selected']] == ['vector-a', 'vector-b']
