"""Owner-authorized research mode carries real-rule results with their research labels.

Fixtures are Phase 06's fictional "real-labelled" ledger; not PalSU policy.
"""
import asyncio

import pytest

from backend.bintanong_orchestration.adapters import SymbolicAdapter
from backend.bintanong_symbolic.runtime import ResearchDependencyResult, ResearchSymbolicResult
from test_orchestration_adapters import context
from test_symbolic_offline_research import research
from test_symbolic_runtime import request


def run(adapter, operation='check_prerequisite_eligibility', state='failed'):
    return asyncio.run(adapter.execute(request(predicate=operation), context(state=state)))


def test_research_adapter_returns_labelled_real_rule_results():
    result = run(SymbolicAdapter(research(), research=True))
    assert type(result) is ResearchSymbolicResult and result.decision.synthetic is False
    assert result.research.mode == 'offline_research' and result.research.institutional_use_allowed is False


def test_research_adapter_returns_labelled_dependency_results():
    result = run(SymbolicAdapter(research(), research=True), 'list_affected_courses')
    assert type(result) is ResearchDependencyResult and result.synthetic is False


def test_default_adapter_still_refuses_a_research_runtime():
    with pytest.raises(ValueError, match='synthetic'):
        SymbolicAdapter(research())


def test_research_adapter_requires_a_research_runtime():
    from test_orchestration_adapters import CurriculumRuntime, fixture, ledger
    with pytest.raises(ValueError, match='research'):
        SymbolicAdapter(CurriculumRuntime(ledger(fixture())), research=True)
