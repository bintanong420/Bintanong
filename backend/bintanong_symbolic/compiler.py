"""Reproducible candidate data facts, never institutional decision rules."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from graphlib import CycleError, TopologicalSorter

from ..bintanong_contracts.base import ContractError
from ..bintanong_contracts.runtime import prolog_quote
from .authoring import build_curriculum_ledger

COMPILER_VERSION = 'curriculum-prolog-preview-v1'


def _json(value) -> str:
    # ASCII JSON carries literal spans (including line breaks) inside one atom.
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def _rebuild(ledger) -> dict:
    keys = {'schema_version', 'scope', 'scope_status', 'synthetic', 'activation_allowed',
            'eligibility_executable', 'approval_id', 'sources', 'courses', 'reviews', 'content_sha256'}
    if not isinstance(ledger, Mapping) or set(ledger) != keys:
        raise ValueError('expected a complete curriculum authoring ledger')
    if not isinstance(ledger['courses'], list) or any(
            not isinstance(c, Mapping) or 'content_sha256' not in c for c in ledger['courses']):
        raise ValueError('expected authoring courses with content digests')
    courses = [{k: v for k, v in c.items() if k != 'content_sha256'} for c in ledger['courses']]
    rebuilt = build_curriculum_ledger(ledger['scope'], ledger['sources'], courses, reviews=ledger['reviews'])
    if _json(rebuilt) != _json(ledger):
        raise ValueError('ledger differs from rebuilt content, digests or inactive flags')
    return rebuilt


def _walk(node, path='prerequisites'):
    yield path, node
    for index, child in enumerate(node.get('items', [])):
        yield from _walk(child, f'{path}.items[{index}]')


def _diagnostics(ledger) -> list[dict]:
    diagnostics, graph = [], {}
    for course in ledger['courses']:
        identity = course['course_id']
        if course['review_state'] != 'reviewed':
            diagnostics.append({'reason': 'course_review_required', 'course_id': identity})
        graph[identity] = []
        for path, node in _walk(course['prerequisites']):
            if node['kind'] == 'unresolved':
                diagnostics.append({'reason': 'unresolved_requirement', 'course_id': identity,
                                    'path': path, 'detail': node['reason']})
            elif node['kind'] == 'course':
                graph[identity].append(node['course_id'])
        graph[identity] = sorted(set(graph[identity]))
    try:
        TopologicalSorter(graph).prepare()
    except CycleError as error:
        # One deterministic witness suffices to hold the entire preview for review.
        diagnostics.append({'reason': 'prerequisite_cycle', 'course_ids': error.args[1]})
    return diagnostics


def _expression(node) -> str:
    kind = node['kind']
    if kind in ('course', 'co_requisite'):
        return f"{kind}({prolog_quote(node['course_id'])})"
    if kind in ('all_of', 'any_of'):
        return f"{kind}([{','.join(_expression(child) for child in node['items'])}])"
    if kind == 'verified_none':
        return kind
    raise ValueError('unresolved requirements cannot be rendered')


def _render(ledger) -> str:
    quote = prolog_quote
    scope = ledger['scope']
    lines = ['% Inactive candidate data only; no decision rules or release authorization.',
             f"candidate_scope({quote(scope['program_id'])},{quote(scope['curriculum_id'])})."]
    for source in ledger['sources']:
        lines.append(f"candidate_source({quote(source['version_id'])},{quote(_json(source))}).")
    for review in ledger['reviews']:
        lines.append(f"candidate_review({quote(review['review_id'])},{quote(_json(review))}).")
    for course in ledger['courses']:
        identity = quote(course['course_id'])
        lines.append(f"candidate_course({identity},{quote(course['source_version_id'])},"
                     f"{quote(course['content_sha256'])}).")
        lines.append(f"candidate_record({identity},{quote(_json(course))}).")
        for name, fact in sorted(course['facts'].items()):
            value = fact['value']
            rendered = quote(value) if isinstance(value, str) else _json(value)
            lines.append(f"candidate_fact({identity},{quote(name)},{rendered}).")
        lines.append(f"candidate_requirement({identity},{_expression(course['prerequisites'])}).")
    return '\n'.join(lines) + '\n'


def compile_curriculum_preview(ledger) -> dict:
    """Revalidate authoring output and prepare inactive candidate facts in memory.

    Drafts, unknown conditions and prior-completion cycles hold the entire preview.
    Source lifecycle states are carried as separate release holds, never promoted.
    This function neither consults Prolog nor registers an operation. Review and
    source declarations remain trusted researcher inputs, not authenticated truth.
    """
    ledger = _rebuild(ledger)
    diagnostics = _diagnostics(ledger)
    prolog = None
    if not diagnostics:
        try:
            prolog = _render(ledger)
        except ContractError as error:
            # Preserve the valid ledger verbatim; do not normalize source values
            # merely to fit the stricter executable-text quoting contract.
            diagnostics.append({'reason': 'unrenderable_text', 'detail': str(error)})
    holds = ['inactive_preview_only', 'declared_scope_not_institutionally_verified']
    for source in ledger['sources']:
        if source['synthetic']:
            holds.append(f"{source['version_id']}:synthetic_source")
        for field in ('acquisition_state', 'verification_state', 'content_review_state', 'approval_state'):
            holds.append(f"{source['version_id']}:{field}:{source[field]['state']}")
    result = {'compiler_version': COMPILER_VERSION, 'ledger_sha256': ledger['content_sha256'],
              'status': 'blocked' if diagnostics else 'review_candidate',
              'activation_allowed': False, 'eligibility_executable': False, 'approval_id': None,
              'ledger': ledger, 'source_states': ledger['sources'], 'release_holds': holds,
              'diagnostics': diagnostics, 'prolog': prolog,
              'prolog_sha256': None if prolog is None else _digest(prolog)}
    result['content_sha256'] = _digest(_json(result))
    return result
