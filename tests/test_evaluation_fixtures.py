"""Synthetic case builders for the evaluation tests. Fictional students and synthetic policy only.

This module holds no tests; the name keeps it next to the evaluation tests that import it.
"""

from __future__ import annotations

import copy

SHA_A = "a" * 64
SHA_B = "b" * 64
VERSION_A = "ver-synth-handbook-1"
REGISTRY = {VERSION_A: SHA_A}


def case(**over):
    """A valid synthetic development case; override any field."""
    base = {
        "schema_version": "bintanong-evaluation-case-v1",
        "case_id": "syn-prereq-001",
        "group_id": "grp-syn-prereq",
        "category": "prerequisites",
        "language": "en",
        "query": "Can student Ana Fictional take COURSE-B before her COURSE-A grade is posted?",
        "adversarial_kinds": ["missing_facts"],
        "scope": None,
        "scope_null_reason": "synthetic case: no real edition applies",
        "expected_route": "Symbolic",
        "expected_control": None,
        "expected_outcome": "unknown",
        "required_facts": ["confirmed COURSE-A result"],
        "missing_facts": ["confirmed COURSE-A result"],
        "gold_spans": [],
        "gold_rules": [],
        "synthetic_policy": "Synthetic rule: COURSE-B needs a posted passing COURSE-A grade.",
        "acceptable_claims": ["The COURSE-A result is not available, so eligibility is unknown."],
        "must_abstain": True,
        "split": "dev",
        "status": "synthetic",
        "review": {"author": "author-a", "reviewer": None, "evidence_ref": None, "review_version": None},
    }
    base.update(copy.deepcopy(over))
    return base


def span(**over):
    s = {"byte_sha256": SHA_A, "version_id": VERSION_A, "page": 3, "locator_ref": "sec-2.1",
         "text_sha256": "c" * 64}
    s.update(over)
    return s


def verified(**over):
    """A structurally valid verified final case (only used inside tests; never committed as data)."""
    fields = {
        "case_id": "ver-final-001", "group_id": "grp-ver-final", "split": "final", "status": "verified",
        "language": "taglish", "synthetic_policy": None, "scope_null_reason": None,
        "scope": {"institution": "inst-x", "edition": "edition-x", "version_id": VERSION_A},
        "adversarial_kinds": [], "expected_outcome": "eligible", "must_abstain": False,
        "missing_facts": [], "gold_spans": [span()], "gold_rules": ["rule-x"],
        "acceptable_claims": ["Eligible under the cited rule."],
        "review": {"author": "author-a", "reviewer": "reviewer-b", "evidence_ref": "ev-1",
                   "review_version": "rv-1"},
    }
    fields.update(over)
    return case(**fields)
