"""Pure, inactive curriculum authoring records; review labels confer no authority."""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any

from ..bintanong_contracts.base import reject_foreign_ids
from ..bintanong_contracts.governance import SourceDocumentVersion, check_register
from ..bintanong_contracts.source import SourceSpan, canonical_text, check_span_binding

SCHEMA_VERSION = 'curriculum-authoring-ledger-v1'
SCOPE_KEYS = {'program_id', 'curriculum_id'}
COURSE_KEYS = {'course_id', *SCOPE_KEYS, 'source_version_id', 'facts',
               'prerequisites', 'review_state', 'review_refs'}
FACT_FIELDS = {'course_code', 'course_title', 'units.total', 'units.lecture',
               'units.lab', 'year_level', 'semester'}


def _record(value: Any, keys: set[str], label: str) -> Mapping:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise ValueError(f'{label} requires exactly {sorted(keys)}')
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f'{label} must be nonblank, unpadded text')
    if any(ord(c) < 32 for c in value):
        raise ValueError(f'{label} contains control characters')
    reject_foreign_ids(value, 'institutional')
    return value


def _items(value: Any, label: str) -> list:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f'{label} must be a sequence')
    return list(value)


def _identities(value: Any, label: str) -> list[str]:
    result = [_text(x, label) for x in _items(value, label)]
    if len(result) != len(set(result)):
        raise ValueError(f'duplicate {label}')
    return sorted(result)


def _spans(value: Any, source: SourceDocumentVersion) -> list[dict]:
    result = []
    for value in _items(value, 'source_spans'):
        parsed = SourceSpan.parse(value.model_dump(mode='json') if isinstance(value, SourceSpan) else value)
        check_span_binding(parsed, source)
        reject_foreign_ids(parsed, 'institutional')
        if not parsed.is_complete or parsed.version_id != source.version_id:
            raise ValueError('complete version-bound source spans are required')
        result.append(parsed.model_dump(mode='json'))
    if not result:
        raise ValueError('source_spans must not be empty')
    return result


def _facts(value: Any, source: SourceDocumentVersion) -> dict:
    if not isinstance(value, Mapping) or 'course_code' not in value or not set(value) <= FACT_FIELDS:
        raise ValueError('facts require course_code and only supported field names')
    result = {}
    for name, fact in value.items():
        _record(fact, {'value', 'source_spans'}, 'fact')
        field_value = fact['value']
        spans = _spans(fact['source_spans'], source)
        printed = [canonical_text(s['text']) for s in spans]
        printed.append(canonical_text(' '.join(s['text'] for s in spans)))
        if name.startswith('units.'):
            if type(field_value) not in (int, float) or not math.isfinite(field_value) or field_value < 0:
                raise ValueError('units must be finite nonnegative numbers')
            supported = any(_printed_number(s, field_value) for s in printed)
        else:
            _text(field_value, name)
            supported = canonical_text(field_value) in printed
        if not supported:
            raise ValueError(f'{name} is not supported by the complete printed field')
        result[name] = {'value': field_value, 'source_spans': spans}
    return result


def _printed_number(text: str, value: int | float) -> bool:
    # Whole field comparison, never a digit substring or numeric default.
    return bool(re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', text)) and Decimal(text) == Decimal(str(value))


def _requirement(value: Any, course: Mapping, source: SourceDocumentVersion,
                 courses: Mapping, *, depth: int = 0) -> dict:
    if depth > 32:
        raise ValueError('requirement expression exceeds 32 levels')
    if not isinstance(value, Mapping):
        raise ValueError('prerequisites require an explicit expression')
    kind = value.get('kind')
    extra = {'course': {'course_id'}, 'co_requisite': {'course_id'},
             'all_of': {'items'}, 'any_of': {'items'}, 'verified_none': set(),
             'unresolved': {'reason'}}
    if not isinstance(kind, str) or kind not in extra:
        raise ValueError('unknown prerequisite expression kind')
    _record(value, {'kind', 'source_spans'} | extra[kind], 'requirement')
    result = {'kind': kind, 'source_spans': _spans(value['source_spans'], source)}
    if kind in {'all_of', 'any_of'}:
        items = _items(value['items'], 'requirement items')
        if not items:
            raise ValueError('empty conjunction/alternative is not verified no prerequisites')
        result['items'] = [_requirement(x, course, source, courses, depth=depth + 1) for x in items]
    elif kind in {'course', 'co_requisite'}:
        target = _text(value['course_id'], 'required course_id')
        if target == course['course_id'] or target not in courses:
            raise ValueError('unknown or self-referencing course requirement')
        if courses[target]['source_version_id'] != course['source_version_id']:
            raise ValueError('course requirements cannot borrow another source version')
        result['course_id'] = target
    elif kind == 'unresolved':
        result['reason'] = _text(value['reason'], 'unresolved reason')
    return result


def build_curriculum_ledger(scope, sources, courses, *, reviews=()) -> dict:
    """Validate trusted authoring input, preserving provenance and pending source states.

    Review references validate attribution/coverage, not reviewer authentication or
    the truth of a translation. No rules, decisions or runtime capability are emitted.
    """
    _record(scope, SCOPE_KEYS, 'scope')
    scope = {name: _text(scope[name], name) for name in sorted(SCOPE_KEYS)}
    parsed = [SourceDocumentVersion.parse(s.model_dump(mode='json')
              if isinstance(s, SourceDocumentVersion) else s) for s in _items(sources, 'sources')]
    if not parsed or len({s.version_id for s in parsed}) != len(parsed):
        raise ValueError('nonempty unique source versions are required')
    check_register(parsed)
    if len({s.synthetic for s in parsed}) != 1 or any(s.acquisition_state.state == 'mismatch' for s in parsed):
        raise ValueError('mixed synthetic sources or acquisition mismatch')
    source_by_id = {s.version_id: s for s in parsed}
    course_by_id = {}
    for c in _items(courses, 'courses'):
        _record(c, COURSE_KEYS, 'course')
        identity = _text(c['course_id'], 'course_id')
        if identity in course_by_id:
            raise ValueError('duplicate course_id')
        if any(c[name] != scope[name] for name in SCOPE_KEYS):
            raise ValueError('course program/curriculum differs from ledger scope')
        if c['source_version_id'] not in source_by_id:
            raise ValueError('unknown course source_version_id')
        course_by_id[identity] = c
    if not course_by_id:
        raise ValueError('at least one course is required')

    review_by_id = {}
    for review in _items(reviews, 'reviews'):
        _record(review, {'review_id', 'source_version_id', 'course_digests', 'reviewer_label'}, 'review')
        identity = _text(review['review_id'], 'review_id')
        version = _text(review['source_version_id'], 'review source_version_id')
        digests = review['course_digests']
        if not isinstance(digests, Mapping) or not digests:
            raise ValueError('review course_digests must name reviewed content')
        ids = _identities(list(digests), 'review course_ids')
        if any(not isinstance(v, str) or not re.fullmatch(r'[0-9a-f]{64}', v) for v in digests.values()):
            raise ValueError('review content digest must be a SHA-256')
        if identity in review_by_id or version not in source_by_id or not ids:
            raise ValueError('duplicate review or invalid review source/coverage')
        if any(cid not in course_by_id or course_by_id[cid]['source_version_id'] != version for cid in ids):
            raise ValueError('review coverage names a foreign course/source')
        review_by_id[identity] = {'review_id': identity, 'source_version_id': version,
                                  'course_digests': {cid: digests[cid] for cid in ids},
                                  'reviewer_label': _text(review['reviewer_label'], 'reviewer_label')}

    normalized, code_keys = [], set()
    for identity, c in sorted(course_by_id.items()):
        source = source_by_id[c['source_version_id']]
        state = c['review_state']
        if state not in ('draft', 'reviewed'):
            raise ValueError('authoring review_state must be draft or reviewed')
        refs = _identities(c['review_refs'], 'review_refs')
        if state == 'reviewed' and not refs:
            raise ValueError('reviewed authoring needs a review reference')
        for ref in refs:
            if ref not in review_by_id or identity not in review_by_id[ref]['course_digests']:
                raise ValueError('review reference does not cover this course')
        facts = _facts(c['facts'], source)
        key = (source.version_id, facts['course_code']['value'])
        if key in code_keys:
            raise ValueError('duplicate course code in one source version')
        code_keys.add(key)
        content = {'course_id': identity, **scope, 'source_version_id': source.version_id,
                   'facts': facts, 'prerequisites': _requirement(c['prerequisites'], c, source, course_by_id)}
        digest = hashlib.sha256(json.dumps(content, ensure_ascii=False, sort_keys=True,
                                separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()
        for ref in refs:
            if review_by_id[ref]['course_digests'][identity] != digest:
                raise ValueError('review content digest differs from current authored record')
        normalized.append({**content, 'content_sha256': digest, 'review_state': state, 'review_refs': refs})
    result = {'schema_version': SCHEMA_VERSION, 'scope': scope, 'scope_status': 'declared',
              'synthetic': parsed[0].synthetic, 'activation_allowed': False,
              'eligibility_executable': False, 'approval_id': None,
              'sources': [source_by_id[k].model_dump(mode='json') for k in sorted(source_by_id)],
              'courses': normalized, 'reviews': [review_by_id[k] for k in sorted(review_by_id)]}
    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    result['content_sha256'] = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    return result
