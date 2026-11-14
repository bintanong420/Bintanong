"""The default suite leaves out the offline ingestion-tool tests unless asked for or named directly."""

from __future__ import annotations

import pytest

import conftest


@pytest.mark.parametrize("filename", ["test_prospectus_fixer.py", "test_review_gui_api.py", "test_ocr_bench_cli.py"])
def test_an_ingestion_tool_test_is_left_out_by_default(filename):
    assert conftest.left_out_of_default_run(filename, include_ingestion=False, named_files=set())


@pytest.mark.parametrize("filename", ["test_contracts_runtime.py", "test_routing_router.py", "test_symbolic_authoring.py",
                                      "test_private_context_isolation.py"])
def test_runtime_and_knowledge_build_tests_always_run(filename):
    assert not conftest.left_out_of_default_run(filename, include_ingestion=False, named_files=set())


def test_the_flag_brings_ingestion_tool_tests_back():
    assert not conftest.left_out_of_default_run("test_prospectus_fixer.py", include_ingestion=True, named_files=set())


def test_a_file_named_on_the_command_line_still_runs():
    assert not conftest.left_out_of_default_run("test_ocr_run.py", include_ingestion=False, named_files={"test_ocr_run.py"})
