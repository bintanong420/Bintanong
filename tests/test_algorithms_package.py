"""Public algorithm entry points preserve existing math and import compatibility."""
import importlib

import pytest


@pytest.mark.parametrize('left,right,expected', [
    ((1.0,0.0),(1.0,0.0),1.0),
    ((1.0,0.0),(0.0,1.0),0.0),
    ((1.0,0.0),(-1.0,0.0),-1.0),
    ((1.0,1.0),(2.0,0.0),2**-0.5),
    ((0.0,0.0),(1.0,0.0),0.0),
])
def test_canonical_cosine_keeps_existing_mathematical_results(left,right,expected):
    algorithms=importlib.import_module('backend.algorithms.similarity')
    assert algorithms.cosine_similarity(left,right)==pytest.approx(expected)


def test_canonical_normalization_preserves_zero_rejection_and_old_imports():
    algorithms=importlib.import_module('backend.algorithms.similarity')
    legacy=importlib.import_module('backend.bintanong_embedding.adapter')
    assert algorithms.normalize_l2((3.0,4.0))==pytest.approx((0.6,0.8))
    with pytest.raises(ValueError,match='zero vector'):
        algorithms.normalize_l2((0.0,0.0))
    assert legacy.cosine_similarity is algorithms.cosine_similarity
    assert legacy.normalize_l2 is algorithms.normalize_l2
