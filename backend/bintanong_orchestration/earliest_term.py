"""Bound evidence for an earliest prescribed-term calculation; never a confirmed offering."""
from typing import Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Contract
from ..bintanong_contracts.runtime import BoundInput
from ..bintanong_contracts.source import SourceSpan
from ..bintanong_contracts.symbolic import DecisionScope
from ..bintanong_planning.contracts import TermRef, StatedFact


class EarliestTermAssessment(Contract):
    SCHEMA_VERSION = 'bintanong-earliest-term-assessment-v1'
    synthetic: bool
    predicate: Literal['earliest_course_term'] = 'earliest_course_term'
    inputs: tuple[BoundInput, ...]
    checked_facts: tuple[StatedFact, ...] = Field(max_length=256)
    request_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    curriculum_id: str = Field(min_length=1, max_length=128)
    course_id: str = Field(min_length=1, max_length=128)
    start_term: TermRef
    term: TermRef | None
    status: Literal['found', 'unknown']
    assumed_passes: tuple[str, ...]
    reason: str | None = None
    scope: DecisionScope | None = None
    rule_ids: tuple[str, ...] = ()
    rule_spans: tuple[SourceSpan, ...] = ()

    @model_validator(mode='after')
    def _bound(self):
        from ..bintanong_planning.chat import earliest_request_digest
        expected = dict(curriculum_id=self.curriculum_id, course_id=self.course_id,
                        year_level=str(self.start_term.year), semester=self.start_term.semester)
        if ({i.name:i.value for i in self.inputs} != expected or len(self.inputs) != 4
                or any(i.fact_ref is not None for i in self.inputs)):
            raise ValueError('earliest_request_mismatch')
        if self.request_sha256 != earliest_request_digest(self.curriculum_id,self.course_id,
                tuple((f.course_id,f.state) for f in self.checked_facts),
                (self.start_term.year,self.start_term.semester)):
            raise ValueError('earliest_checked_facts_mismatch')
        if ((self.status == 'found') != (self.term is not None)
                or self.status == 'found' and (self.scope is None or not self.rule_spans or not self.rule_ids)):
            raise ValueError('earliest_result_requires_checked_rules')
        return self
