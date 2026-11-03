"""Reviewed unit-load policy for plan checks, loaded from data; no limit is written in code.

A regular semester's ceiling is the curriculum ledger's prescribed total for that semester (owner working
assumption D5, 4 Nov 2026: shown as a major warning, never a block). The summer normal load comes from the policy
record. The real PalSU record is supplied only after the owner reviews the printed Student Handbook clauses (plan of
action, Step 1); until a reviewed record is given, every load check returns unknown with the reason
"load policy not reviewed". Tests use a synthetic fixture record only.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Contract
from .contracts import PolicyClauseRef, Text, Units

NOT_REVIEWED = 'load policy not reviewed'
TOPICS = {'regular': 0, 'summer': 1}  # clause order: the semester-load clause, then the summer-load clause


class LoadPolicy(Contract):
    SCHEMA_VERSION = 'bintanong-load-policy-v1'
    policy_id: Text
    synthetic: bool
    regular_ceiling: Literal['prescribed_semester_total']
    summer_normal_units: Units = Field(gt=0)
    clauses: tuple[PolicyClauseRef, PolicyClauseRef]  # (semester load, summer load), each a reviewed printed span
    review_refs: tuple[Text, ...] = Field(min_length=1)

    @model_validator(mode='after')
    def _distinct(self):
        if self.clauses[0] == self.clauses[1]:
            raise ValueError('semester and summer load cite their own clauses')
        return self

    def clause(self, kind: str) -> PolicyClauseRef:
        return self.clauses[TOPICS[kind]]


def load_policy(path: str | Path) -> LoadPolicy:
    return LoadPolicy.parse(json.loads(Path(path).read_text(encoding='utf-8')))
