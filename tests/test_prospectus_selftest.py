"""The extractor's built-in 80-check suite, run under pytest."""

from backend.bintanong_tools.prospectus_extractor import run_self_tests


def test_builtin_self_tests_pass():
    assert run_self_tests(verbose=False) == 0
