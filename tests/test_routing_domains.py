"""Host-owned domain ownership: policy-only questions must never require Prolog."""
import pytest

from backend.bintanong_routing.domains import (
    CURRICULUM_CATALOG_OPERATIONS, CURRICULUM_CONSTRAINT_OPERATIONS,
    OPERATIONS, operation_domain, route_for_evidence_needs,
)
from backend.bintanong_routing.validation import OPERATIONS as VALIDATED_OPERATIONS
from backend.bintanong_generation.render import _PART_TOPIC_UNRESOLVED, _PART_UNAVAILABLE


def test_all_registered_symbolic_operations_have_exactly_one_curriculum_owner():
    assert tuple(VALIDATED_OPERATIONS) == OPERATIONS
    assert not (CURRICULUM_CATALOG_OPERATIONS & CURRICULUM_CONSTRAINT_OPERATIONS)
    assert {op for op in OPERATIONS if operation_domain(op)} == set(OPERATIONS)
    assert operation_domain('check_prerequisite_eligibility') == 'curriculum_constraints'
    assert operation_domain('course_facts') == 'curriculum_catalog'
    assert operation_domain('issue_tor') is None
    assert operation_domain('compute_student_fee') is None


@pytest.mark.parametrize('needs,expected', [
    (('document',), 'RAG'),
    (('structured',), 'Symbolic'),
    (('structured', 'document'), 'Hybrid'),
    (('document', 'document'), 'RAG'),
    (('document', 'structured', 'document'), 'Hybrid'),
    (('document', 'unknown'), None),
    (('unknown',), None),
    ((), None),
    (('policy',), None),
])
def test_routes_are_derived_from_evidence_needs_not_policy_keywords(needs, expected):
    assert route_for_evidence_needs(needs) == expected


@pytest.mark.parametrize('language', ['en', 'fil', 'taglish'])
def test_unmatched_topic_notice_does_not_claim_source_absence(language):
    notice = _PART_TOPIC_UNRESOLVED[language].format(words='Form Q')
    assert 'Form Q' in notice
    assert notice != _PART_UNAVAILABLE[language].format(words='Form Q')
    if language == 'en':
        assert 'was not checked' in notice
        assert 'not in Bintanong' not in notice
    else:
        assert 'na-check' in notice


def test_adapter_runtime_and_router_agree_on_supported_symbolic_operations():
    from backend.bintanong_orchestration.adapters import SIGNATURES
    from backend.bintanong_symbolic.runtime import _LOOKUPS
    assert set(SIGNATURES) == set(OPERATIONS)
    assert set(_LOOKUPS) == set(CURRICULUM_CATALOG_OPERATIONS)

