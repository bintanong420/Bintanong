"""Bounded synthetic prerequisite execution; institutional candidates remain inactive."""
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

from pydantic import AfterValidator, Field

from ..bintanong_contracts.base import Record
from ..bintanong_contracts.runtime import BoundInput, PredicateRequest
from ..bintanong_contracts.symbolic import Capability, CapabilityRegistry, SymbolicResult
from .compiler import compile_curriculum_review_bundle

_ADMISSION = threading.Lock()
_WORKER = Path(__file__).with_name('_janus_worker.py')
_ENGINE = Path(__file__).with_name('curriculum_runtime.pl')
_MAX_BYTES = 1_048_576
_PREDICATE = 'check_prerequisite_eligibility'


def _course_id(value: str) -> str:
    return BoundInput(name='course_id', value=value, fact_ref=None).value


_CourseID = Annotated[str, Field(min_length=1, max_length=128), AfterValidator(_course_id)]


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


class _WorkerFailure(RuntimeError):
    pass


def _json(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


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
    return _Evaluation.parse(reply['result'])


@dataclass(frozen=True, init=False)
class CurriculumRuntime:
    _ledger_json: str
    _bundle_json: str
    _version: str
    _engine_sha256: str
    _reviewed_rules: frozenset[str]
    timeout_seconds: float
    max_conditions: int

    def __init__(self, ledger, *, timeout_seconds=5.0, max_conditions=128):
        if type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 30:
            raise ValueError('timeout_seconds must be finite, positive and at most 30')
        if type(max_conditions) is not int or not 1 <= max_conditions <= 256:
            raise ValueError('max_conditions must be 1..256')
        bundle = compile_curriculum_review_bundle(ledger)
        checked = bundle['ledger']
        if not checked['synthetic']:
            raise ValueError('only synthetic research ledgers may execute; institutional release is not authorized')
        if bundle['status'] == 'blocked':
            raise ValueError('compiler holds prevent runtime preparation')
        def expression(node):
            result = {k:v for k,v in node.items() if k != 'source_spans' and k != 'items'}
            if 'items' in node:
                result['items'] = [expression(x) for x in node['items']]
            return result
        coverage = {c['course_id']:c for c in bundle['coverage']}
        compact = {'synthetic':True, 'curriculum_id':checked['scope']['curriculum_id'], 'courses':[
            {'id':c['course_id'], 'reviewed':c['review_state']=='reviewed',
             'rule':expression(c['prerequisites']) if coverage[c['course_id']]['direct_rule']=='reviewed'
                    else {'kind':'unresolved'}} for c in checked['courses']]}
        encoded = _json(compact)
        if len(encoded.encode()) > _MAX_BYTES // 2:
            raise ValueError('runtime bundle exceeds byte limit')
        object.__setattr__(self, '_ledger_json', _json(checked))
        object.__setattr__(self, '_bundle_json', encoded)
        engine_sha = hashlib.sha256(_ENGINE.read_bytes()).hexdigest()
        object.__setattr__(self, '_engine_sha256', engine_sha)
        object.__setattr__(self, '_reviewed_rules', frozenset(
            cid for cid,c in coverage.items() if c['direct_rule']=='reviewed'))
        object.__setattr__(self, '_version', 'synthetic-runtime-v1-'+hashlib.sha256(_json([bundle,engine_sha]).encode()).hexdigest())
        object.__setattr__(self, 'timeout_seconds', float(timeout_seconds))
        object.__setattr__(self, 'max_conditions', max_conditions)

    def check(self, request: PredicateRequest, facts: StudentFacts | None = None) -> SymbolicResult:
        request = PredicateRequest.parse(request.model_dump(mode='json'))
        if len(request.inputs) > 2 or len(_json(request.model_dump(mode='json')).encode()) > 8192:
            raise ValueError('runtime request exceeds input limit')
        facts = StudentFacts() if facts is None else StudentFacts.parse(facts.model_dump(mode='json'))
        registry = CapabilityRegistry({_PREDICATE:Capability('synthetic_prerequisite_check', ('curriculum_id','course_id'))})
        if not registry.supports(request.predicate):
            return self._result(request, outcome='unsupported', supported=False)
        goal = registry.goal(request)
        args = dict(goal.args)
        started = time.monotonic()
        if not _ADMISSION.acquire(timeout=self.timeout_seconds):
            return self._result(request, outcome='error', error='runtime_timeout')
        try:
            remaining = self.timeout_seconds - (time.monotonic()-started)
            if remaining <= 0:
                raise subprocess.TimeoutExpired('janus_worker', self.timeout_seconds)
            result = _invoke_worker({'bundle':json.loads(self._bundle_json), 'curriculum_id':args['curriculum_id'],
                'course_id':args['course_id'], 'facts':facts.model_dump(mode='json'),
                'engine_sha256':self._engine_sha256,
                'time_limit':remaining, 'max_conditions':self.max_conditions}, remaining)
            if sum(len(getattr(result,k)) for k in ('satisfied','violated','unknown','conflicts')) > self.max_conditions:
                raise _WorkerFailure('runtime_result_limit')
            answer = self._result(request, outcome=result.outcome, evaluation=result)
            registry.check_result(answer)
            return answer
        except subprocess.TimeoutExpired:
            return self._result(request, outcome='error', error='runtime_timeout')
        except OSError:
            return self._result(request, outcome='error', error='runtime_unavailable')
        except _WorkerFailure as exc:
            return self._result(request, outcome='error', error=str(exc))
        except (ValueError, TypeError, KeyError, AttributeError):
            return self._result(request, outcome='error', error='runtime_invalid_output')
        finally:
            _ADMISSION.release()

    def _result(self, request, *, outcome, supported=True, error=None, evaluation=None):
        ledger = json.loads(self._ledger_json)
        values = {i.name:i.value for i in request.inputs}
        target = next((c for c in ledger['courses'] if c['course_id']==values.get('course_id')), None) \
            if values.get('curriculum_id')==ledger['scope']['curriculum_id'] else None
        spans = []
        if outcome not in ('error','unsupported') and target is not None and target['review_state']=='reviewed':
            def collect(node):
                spans.extend(node['source_spans'])
                for child in node.get('items',[]): collect(child)
            collect(target['prerequisites'])
        spans = list({_json(s):s for s in spans}.values())
        refs = ['span-'+hashlib.sha256(_json(s).encode()).hexdigest() for s in spans]
        ev = evaluation
        unknown = () if ev is None else ev.unknown
        data = {'schema_version':'bintanong-symbolic-result-v1',
            'decision':{'schema_version':'bintanong-decision-v1','synthetic':True,'outcome':outcome,
                'predicate':request.predicate, 'predicate_supported':supported,
                'rule_coverage':'absent' if ev is None else ev.coverage,
                'prerequisite_rule_state':None if ev is None else (
                    'unresolved_reference' if target is None or target['course_id'] not in self._reviewed_rules else
                    'stated_none' if target and target['prerequisites']['kind']=='verified_none' else 'resolved'),
                'satisfied_conditions':() if ev is None else ev.satisfied,
                'violated_conditions':() if ev is None else ev.violated,
                'unknown_conditions':[x for x in unknown if not x.startswith('completion_unknown:')],
                'missing_facts':[x for x in unknown if x.startswith('completion_unknown:')],
                'evidence_refs':refs, 'unresolved_conflicts':() if ev is None else ev.conflicts,
                'error_code':error},
            'capability':'synthetic_prerequisite_check' if supported else 'unsupported',
            'inputs':[i.model_dump(mode='json') for i in request.inputs],
            'rule_ids':['rule-'+target['course_id']] if spans else [],
            'rule_bundle_version':None if outcome in ('unsupported','error') else self._version,
            'scope':None if outcome in ('unsupported','error') else {
                'knowledge_release_id':'release-synthetic-'+ledger['content_sha256'][:16],
                'edition_ids':[s['edition_id'] for s in ledger['sources']],
                'scope_ids':list(ledger['scope'].values())}, 'rule_spans':spans}
        if outcome != 'error' and len(_json(data).encode()) > 65_536:
            return self._result(request, outcome='error', error='runtime_result_limit')
        return SymbolicResult.parse(data)
