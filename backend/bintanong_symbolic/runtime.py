"""Bounded prerequisite research execution; institutional candidates remain inactive."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal

from pydantic import AfterValidator, Field, model_validator

from ..bintanong_contracts.base import Contract, Record
from ..bintanong_contracts.runtime import BoundInput, PredicateRequest
from ..bintanong_contracts.source import SourceSpan
from ..bintanong_contracts.symbolic import Capability, CapabilityRegistry, DecisionScope, SymbolicResult
from .bundle import prepare_runtime_bundle, validate_runtime_bundle

_ADMISSION = threading.Lock()
_WORKER = Path(__file__).with_name('_janus_worker.py')
_MAX_BYTES = 1_048_576
_PREDICATE = 'check_prerequisite_eligibility'
_DECISIONS = {_PREDICATE:'synthetic_prerequisite_check',
              'list_missing_prerequisites':'synthetic_missing_prerequisites'}


def _course_id(value: str) -> str:
    return BoundInput(name='course_id', value=value, fact_ref=None).value


_CourseID = Annotated[str, Field(min_length=1, max_length=128), AfterValidator(_course_id)]
_Text = Annotated[str, Field(min_length=1)]


class StudentFacts(Record):
    synthetic: Literal[True] = True
    passed: tuple[_CourseID, ...] = Field(default=(), max_length=256)
    failed: tuple[_CourseID, ...] = Field(default=(), max_length=256)
    enrolled: tuple[_CourseID, ...] = Field(default=(), max_length=256)
    not_enrolled: tuple[_CourseID, ...] = Field(default=(), max_length=256)


class _Evaluation(Record):
    outcome: Literal['eligible', 'ineligible', 'unknown']
    coverage: Literal['verified', 'partial', 'absent']
    satisfied: tuple[str, ...]
    violated: tuple[str, ...]
    unknown: tuple[str, ...]
    conflicts: tuple[str, ...]


class _DependencyEvaluation(Record):
    status: Literal['complete','partial']
    course_ids: tuple[_CourseID, ...]
    unknown_conditions: tuple[_Text, ...]

    @model_validator(mode='after')
    def _coverage(self):
        if (self.status=='complete') != (not self.unknown_conditions):
            raise ValueError('dependency completeness needs explicit coverage')
        if tuple(sorted(set(self.course_ids))) != self.course_ids:
            raise ValueError('dependency ids must be unique and ordered')
        return self


class DependencyResult(Contract):
    SCHEMA_VERSION = 'bintanong-synthetic-dependency-result-v1'
    synthetic: Literal[True]
    activation_allowed: Literal[False]
    eligibility_executable: Literal[False]
    relation: Literal['potential_prerequisite_or_corequisite_dependency']
    coverage_scope: Literal['supplied_bundle']
    status: Literal['complete','partial','unsupported','error']
    inputs: tuple[BoundInput, ...]
    course_ids: tuple[_CourseID, ...]
    unknown_conditions: tuple[_Text, ...]
    rule_bundle_version: _Text | None
    scope: DecisionScope | None
    rule_ids: tuple[_Text, ...]
    rule_spans: tuple[SourceSpan, ...]
    error_code: _Text | None

    @model_validator(mode='after')
    def _boundaries(self):
        if (self.status=='error') != (self.error_code is not None):
            raise ValueError('only errors carry error_code')
        if self.status in ('unsupported','error') and (
                self.course_ids or self.unknown_conditions or self.rule_ids or self.rule_spans
                or self.rule_bundle_version or self.scope):
            raise ValueError('non-results cannot cite dependency facts')
        if self.status=='complete' and self.unknown_conditions:
            raise ValueError('complete listing cannot have unknown coverage')
        if self.status=='partial' and not self.unknown_conditions:
            raise ValueError('partial listing needs a coverage reason')
        if self.status in ('complete','partial') and self.rule_bundle_version is None:
            raise ValueError('dependency listing needs its bundle version')
        if self.status=='complete' and self.scope is None:
            raise ValueError('complete listing needs its scope')
        if tuple(sorted(set(self.course_ids))) != self.course_ids:
            raise ValueError('dependency ids must be unique and ordered')
        if len(set(self.rule_ids)) != len(self.rule_ids):
            raise ValueError('duplicate rule ids')
        if any(not s.is_complete or s.version_id is None for s in self.rule_spans):
            raise ValueError('dependency spans need anchored printed text and source versions')
        if self.course_ids and not (self.rule_ids and self.rule_spans and self.scope):
            raise ValueError('dependency facts require scoped provenance')
        return self


class ResearchAuthorization(Record):
    purpose: Literal['offline_curriculum_acceptance']
    authorization_ref: str = Field(pattern=r'^research-[A-Za-z0-9_-]+$', max_length=128)
    bundle_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    operations: tuple[Literal['check_prerequisite_eligibility','list_missing_prerequisites',
                              'list_affected_courses'], ...] = Field(min_length=1, max_length=3)

    @model_validator(mode='after')
    def _unique(self):
        if len(set(self.operations)) != len(self.operations):
            raise ValueError('duplicate research operations')
        return self


class ResearchContext(Record):
    mode: Literal['offline_research']
    institutional_use_allowed: Literal[False]
    student_facts_synthetic: Literal[True]
    generated_output_review: Literal['pending']
    authorization: ResearchAuthorization
    release_holds: tuple[_Text, ...] = Field(min_length=1)
    payload_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')


class ResearchSymbolicResult(SymbolicResult):
    SCHEMA_VERSION = 'bintanong-offline-research-result-v1'
    research: ResearchContext

    @model_validator(mode='after')
    def _real_rules(self):
        if self.decision.synthetic:
            raise ValueError('offline real-rule result cannot label rules synthetic')
        return self


class ResearchDependencyResult(DependencyResult):
    SCHEMA_VERSION = 'bintanong-offline-research-dependency-result-v1'
    synthetic: Literal[False]
    research: ResearchContext


class _WorkerFailure(RuntimeError):
    pass


def _json(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


def _parse_request(request):
    request = PredicateRequest.parse(request.model_dump(mode='json'))
    if len(request.inputs) > 2 or len(_json(request.model_dump(mode='json')).encode()) > 8192:
        raise ValueError('runtime request exceeds input limit')
    return request


def _spans(courses):
    spans = []
    def collect(node):
        spans.extend(node['source_spans'])
        for child in node.get('items',[]): collect(child)
    for course in courses:
        collect(course['prerequisites'])
    return list({_json(s):s for s in spans}.values())


def _dependency_spans(courses):
    # One citation per affected course (its rule's first printed span) keeps large listings within the
    # result limit; eligibility results still cite every span of the checked rule (owner, 23 Oct 2026).
    spans = [c['prerequisites']['source_spans'][0] for c in courses]
    return list({_json(s):s for s in spans}.values())


def _scope(ledger, release_id):
    return {'knowledge_release_id':release_id,
            'edition_ids':[s['edition_id'] for s in ledger['sources']],
            'scope_ids':list(ledger['scope'].values())}


def _invoke_worker(payload, timeout):
    data = _json(payload).encode()
    if len(data) > _MAX_BYTES:
        raise ValueError('runtime input exceeds byte limit')
    child = subprocess.run([sys.executable, '-B', str(_WORKER)], input=data, capture_output=True,
                           timeout=timeout, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if child.returncode:
        raise _WorkerFailure('runtime_worker_failed')
    if len(child.stdout) > 65_536:
        raise _WorkerFailure('runtime_result_limit')
    reply = json.loads(child.stdout)
    if not isinstance(reply, dict) or set(reply) not in ({'result'}, {'error'}):
        raise ValueError('invalid worker envelope')
    if 'error' in reply:
        code = reply['error']
        if code not in {'runtime_timeout', 'runtime_result_limit', 'runtime_unavailable', 'runtime_worker_failed'}:
            raise ValueError('invalid worker error')
        raise _WorkerFailure(code)
    result_type = _DependencyEvaluation if payload.get('operation')=='dependencies' else _Evaluation
    return result_type.parse(reply['result'])


@dataclass(frozen=True, init=False)
class CurriculumRuntime:
    _ledger_json: str
    _bundle_json: str
    _version: str
    _engine_sha256: str
    _reviewed_rules: frozenset[str]
    _exported_rules: frozenset[str]
    _research_json: str | None
    _allowed_operations: frozenset[str]
    _release_id: str
    timeout_seconds: float
    max_conditions: int

    def __init__(self, ledger, *, timeout_seconds=5.0, max_conditions=128):
        self._initialize(prepare_runtime_bundle(ledger), timeout_seconds, max_conditions)

    def _initialize(self, bundle, timeout_seconds, max_conditions, authorization=None):
        if type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 30:
            raise ValueError('timeout_seconds must be finite, positive and at most 30')
        if type(max_conditions) is not int or not 1 <= max_conditions <= 256:
            raise ValueError('max_conditions must be 1..256')
        checked = bundle['ledger']
        if not checked['synthetic'] and authorization is None:
            raise ValueError('only synthetic research ledgers may execute; institutional release is not authorized')
        coverage = {c['course_id']:c for c in bundle['coverage']}
        encoded = _json(bundle['payload'])
        object.__setattr__(self, '_ledger_json', _json(checked))
        object.__setattr__(self, '_bundle_json', encoded)
        engine_sha = bundle['engine_sha256']
        object.__setattr__(self, '_engine_sha256', engine_sha)
        object.__setattr__(self, '_reviewed_rules', frozenset(
            cid for cid,c in coverage.items() if c['direct_rule']=='reviewed'))
        # Reviewed courses whose rule is exported, possibly with unknown leaves for unresolved parts.
        object.__setattr__(self, '_exported_rules', frozenset(
            cid for cid,c in coverage.items() if c['identity_review']=='reviewed'))
        research = None if authorization is None else ResearchContext.parse({
            'mode':'offline_research','institutional_use_allowed':False,'student_facts_synthetic':True,
            'generated_output_review':'pending','authorization':authorization.model_dump(mode='json'),
            'release_holds':bundle['release_holds'],'payload_sha256':bundle['payload_sha256']})
        if research is not None and len(_json(research.model_dump(mode='json')).encode()) > 8192:
            raise ValueError('research context exceeds byte limit')
        version = bundle['runtime_version'] if research is None else 'offline-research-runtime-v1-'+hashlib.sha256(
            _json([bundle['content_sha256'],research.model_dump(mode='json')]).encode()).hexdigest()
        object.__setattr__(self, '_version', version)
        object.__setattr__(self, '_research_json', None if research is None else _json(research.model_dump(mode='json')))
        object.__setattr__(self, '_allowed_operations', frozenset(
            (*_DECISIONS,'list_affected_courses') if authorization is None else authorization.operations))
        release = 'release-synthetic-'+checked['content_sha256'][:16] if research is None else (
            'release-offline-research-'+bundle['content_sha256'][:16])
        object.__setattr__(self, '_release_id', release)
        object.__setattr__(self, 'timeout_seconds', float(timeout_seconds))
        object.__setattr__(self, 'max_conditions', max_conditions)

    @classmethod
    def from_bundle(cls, bundle, *, timeout_seconds=5.0, max_conditions=128):
        checked = validate_runtime_bundle(bundle)
        runtime = cls(checked['ledger'], timeout_seconds=timeout_seconds, max_conditions=max_conditions)
        if runtime._version != checked['runtime_version']:
            raise ValueError('runtime engine or compiler changed during bundle loading')
        return runtime

    @classmethod
    def for_offline_research(cls, bundle, *, authorization, timeout_seconds=5.0, max_conditions=128):
        checked = validate_runtime_bundle(bundle)
        authorization = ResearchAuthorization.parse(authorization)
        if checked['ledger']['synthetic'] or authorization.bundle_sha256 != checked['content_sha256']:
            raise ValueError('research authorization must bind this exact non-synthetic bundle')
        runtime = cls.__new__(cls)
        runtime._initialize(checked, timeout_seconds, max_conditions, authorization)
        return runtime

    def _capability(self, name):
        return name if self._research_json is None else name.replace('synthetic_','offline_research_',1)

    @property
    def release_id(self) -> str:
        return self._release_id

    @property
    def rule_bundle_version(self) -> str:
        return self._version

    @property
    def synthetic(self) -> bool:
        return self._research_json is None

    def check(self, request: PredicateRequest, facts: StudentFacts | None = None) -> SymbolicResult:
        request = _parse_request(request)
        facts = StudentFacts() if facts is None else StudentFacts.parse(facts.model_dump(mode='json'))
        registry = CapabilityRegistry({name:Capability(self._capability(cap), ('curriculum_id','course_id'))
            for name,cap in _DECISIONS.items() if name in self._allowed_operations})
        if not registry.supports(request.predicate):
            return self._result(request, outcome='unsupported', supported=False)
        goal = registry.goal(request)
        args = dict(goal.args)
        try:
            result = self._execute(args, facts, 'eligibility', request.predicate)
            answer = self._result(request, outcome=result.outcome, evaluation=result)
            registry.check_result(answer)
            return answer
        except _WorkerFailure as exc:
            return self._result(request, outcome='error', error=str(exc))
        except (ValueError, TypeError, KeyError, AttributeError):
            return self._result(request, outcome='error', error='runtime_invalid_output')

    def list_affected_courses(self, request: PredicateRequest) -> DependencyResult:
        request = _parse_request(request)
        registry = CapabilityRegistry({'list_affected_courses':Capability(
            self._capability('synthetic_dependency_inspection'), ('curriculum_id','course_id'))}
            if 'list_affected_courses' in self._allowed_operations else {})
        if not registry.supports(request.predicate):
            return self._dependency_result(request, status='unsupported')
        args = dict(registry.goal(request).args)
        try:
            result = self._execute(args, StudentFacts(), 'dependencies', request.predicate)
            return self._dependency_result(request, evaluation=result)
        except _WorkerFailure as exc:
            return self._dependency_result(request, status='error', error=str(exc))
        except (ValueError, TypeError, KeyError, AttributeError):
            return self._dependency_result(request, status='error', error='runtime_invalid_output')

    def _execute(self, args, facts, operation, predicate):
        started = time.monotonic()
        if not _ADMISSION.acquire(timeout=self.timeout_seconds):
            raise _WorkerFailure('runtime_timeout')
        try:
            remaining = self.timeout_seconds - (time.monotonic()-started)
            if remaining <= 0:
                raise subprocess.TimeoutExpired('janus_worker', self.timeout_seconds)
            result = _invoke_worker({'bundle':json.loads(self._bundle_json), 'curriculum_id':args['curriculum_id'],
                'course_id':args['course_id'], 'facts':facts.model_dump(mode='json'),
                'engine_sha256':self._engine_sha256,
                'operation':operation, 'predicate':predicate,
                'research':None if self._research_json is None else json.loads(self._research_json),
                'time_limit':remaining, 'max_conditions':self.max_conditions}, remaining)
            fields = ('course_ids','unknown_conditions') if operation=='dependencies' else ('satisfied','violated','unknown','conflicts')
            if sum(len(getattr(result,k)) for k in fields) > self.max_conditions:
                raise _WorkerFailure('runtime_result_limit')
            return result
        except subprocess.TimeoutExpired:
            raise _WorkerFailure('runtime_timeout') from None
        except OSError:
            raise _WorkerFailure('runtime_unavailable') from None
        except (ValueError, TypeError, KeyError, AttributeError):
            raise _WorkerFailure('runtime_invalid_output') from None
        finally:
            _ADMISSION.release()

    def _result(self, request, *, outcome, supported=True, error=None, evaluation=None):
        ledger = json.loads(self._ledger_json)
        values = {i.name:i.value for i in request.inputs}
        target = next((c for c in ledger['courses'] if c['course_id']==values.get('course_id')), None) \
            if values.get('curriculum_id')==ledger['scope']['curriculum_id'] else None
        spans = _spans([target]) if outcome not in ('error','unsupported') and target is not None and target['review_state']=='reviewed' else []
        refs = ['span-'+hashlib.sha256(_json(s).encode()).hexdigest() for s in spans]
        ev = evaluation
        unknown = () if ev is None else ev.unknown
        result_type = SymbolicResult if self._research_json is None else ResearchSymbolicResult
        data = {'schema_version':result_type.SCHEMA_VERSION,
            'decision':{'schema_version':'bintanong-decision-v1','synthetic':ledger['synthetic'],'outcome':outcome,
                'predicate':request.predicate, 'predicate_supported':supported,
                'rule_coverage':'absent' if ev is None else ev.coverage,
                'prerequisite_rule_state':None if ev is None else (
                    'unresolved_reference' if target is None or target['course_id'] not in self._exported_rules else
                    'stated_none' if target['prerequisites']['kind']=='verified_none' else
                    # A partly unresolved rule is decided only by its reviewed parts.
                    'resolved' if target['course_id'] in self._reviewed_rules or outcome in ('eligible','ineligible')
                    else 'unresolved_reference'),
                'satisfied_conditions':() if ev is None else ev.satisfied,
                'violated_conditions':() if ev is None else ev.violated,
                'unknown_conditions':[x for x in unknown if not x.startswith('completion_unknown:')],
                'missing_facts':[x for x in unknown if x.startswith('completion_unknown:')],
                'evidence_refs':refs, 'unresolved_conflicts':() if ev is None else ev.conflicts,
                'error_code':error},
            'capability':self._capability(_DECISIONS.get(request.predicate,'unsupported')) if supported else 'unsupported',
            'inputs':[i.model_dump(mode='json') for i in request.inputs],
            'rule_ids':['rule-'+target['course_id']] if spans else [],
            'rule_bundle_version':None if outcome in ('unsupported','error') else self._version,
            'scope':None if outcome in ('unsupported','error') else _scope(ledger,self._release_id), 'rule_spans':spans}
        if self._research_json is not None:
            data['research'] = json.loads(self._research_json)
        if outcome != 'error' and len(_json(data).encode()) > 65_536:
            return self._result(request, outcome='error', error='runtime_result_limit')
        return result_type.parse(data)

    def _dependency_result(self, request, *, status=None, error=None, evaluation=None):
        ledger = json.loads(self._ledger_json)
        values = {i.name:i.value for i in request.inputs}
        matches_scope = values.get('curriculum_id')==ledger['scope']['curriculum_id']
        known_input = matches_scope and any(c['course_id']==values.get('course_id') for c in ledger['courses'])
        ids = () if evaluation is None else evaluation.course_ids
        if ids and (not known_input or not set(ids) <= self._exported_rules):
            raise ValueError('unbound dependency output')
        if evaluation is not None and evaluation.status=='complete' and (
                not known_input or len(self._reviewed_rules)!=len(ledger['courses'])):
            raise ValueError('unbound dependency completeness')
        courses = [c for c in ledger['courses'] if c['course_id'] in ids]
        result_type = DependencyResult if self._research_json is None else ResearchDependencyResult
        data = {'schema_version':result_type.SCHEMA_VERSION,'synthetic':ledger['synthetic'],
            'activation_allowed':False,'eligibility_executable':False,
            'relation':'potential_prerequisite_or_corequisite_dependency','coverage_scope':'supplied_bundle',
            'status':status if evaluation is None else evaluation.status,
            'inputs':[i.model_dump(mode='json') for i in request.inputs], 'course_ids':ids,
            'unknown_conditions':() if evaluation is None else evaluation.unknown_conditions,
            'rule_bundle_version':None if evaluation is None else self._version,
            'scope':_scope(ledger,self._release_id) if known_input and evaluation is not None else None,
            'rule_ids':['rule-'+c['course_id'] for c in courses], 'rule_spans':_dependency_spans(courses),
            'error_code':error}
        if self._research_json is not None:
            data['research'] = json.loads(self._research_json)
        if status != 'error' and len(_json(data).encode()) > 65_536:
            return self._dependency_result(request, status='error', error='runtime_result_limit')
        return result_type.parse(data)
