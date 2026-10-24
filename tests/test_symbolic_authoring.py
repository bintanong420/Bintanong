"""Synthetic authoring validation; no institutional rules or student decisions."""
from __future__ import annotations

import copy
import importlib
import json

import pytest

from backend.bintanong_contracts.symbolic import EMPTY_REGISTRY
from backend.bintanong_tools.document_ingest.register import mint_pending_register
from contracts_fixtures import span


def build(*args, **kwargs):
    return importlib.import_module('backend.bintanong_symbolic.authoring').build_curriculum_ledger(*args, **kwargs)


def fixture():
    source = mint_pending_register([{'filename': 'fictional.pdf', 'sha256': 'a' * 64,
                                    'acquisition_locator': 'shelf:fictional'}], synthetic=True)[0]
    scope = {'program_id': 'program-synthetic', 'curriculum_id': 'curriculum-synthetic-1'}

    def evidence(text):
        s = span(source.byte_sha256, text=text)
        s['version_id'] = source.version_id
        return [s]

    courses = []
    for number in [1, 2]:
        cid, code = f'course-{number}', f'SYN{number}01'
        requirement = {'kind': 'verified_none', 'source_spans': evidence('None')}
        if number == 2:
            requirement = {'kind': 'course', 'course_id': 'course-1', 'source_spans': evidence('SYN101')}
        courses.append({'course_id': cid, **scope, 'source_version_id': source.version_id,
                        'facts': {'course_code': {'value': code, 'source_spans': evidence(code)},
                                  'units.total': {'value': 3, 'source_spans': evidence('3')}},
                        'prerequisites': requirement, 'review_state': 'reviewed', 'review_refs': ['review-1']})
    drafts = copy.deepcopy(courses)
    for c in drafts:
        c['review_state'], c['review_refs'] = 'draft', []
    prepared = build(scope, [source], drafts)
    reviews = [{'review_id': 'review-1', 'source_version_id': source.version_id,
                'course_digests': {c['course_id']: c['content_sha256'] for c in prepared['courses']},
                'reviewer_label': 'Synthetic researcher'}]
    return scope, [source], courses, reviews


def run(data):
    scope, sources, courses, reviews = data
    return build(scope, sources, courses, reviews=reviews)


def test_preserves_source_bound_facts_and_never_authorizes_execution():
    data = fixture()
    before = copy.deepcopy(data)
    result = run(data)
    assert result['schema_version'] == 'curriculum-authoring-ledger-v1'
    assert result['activation_allowed'] is False and result['eligibility_executable'] is False
    assert result['approval_id'] is None and result['scope_status'] == 'declared'
    assert result['sources'][0] == data[1][0].model_dump(mode='json')
    assert result['courses'][0]['facts']['units.total']['value'] == 3
    assert result['courses'][0]['prerequisites']['kind'] == 'verified_none'
    assert result['courses'][1]['prerequisites']['course_id'] == 'course-1'
    assert len(result['content_sha256']) == 64
    assert data == before
    assert not EMPTY_REGISTRY.supports('check_prerequisite_eligibility')
    json.dumps(result, allow_nan=False)


def test_deterministic_identity_ignores_unordered_collections_and_detaches_inputs():
    data = fixture()
    baseline = run(data)
    data[2].reverse()
    data[3][0]['course_digests'] = dict(reversed(list(data[3][0]['course_digests'].items())))
    assert run(data) == baseline
    data[2][0]['facts']['course_code']['value'] = 'changed after build'
    assert baseline['courses'][1]['facts']['course_code']['value'] == 'SYN201'


def test_preserves_explicit_nested_logic_and_corequisite_without_evaluating():
    data = fixture()
    leaf = copy.deepcopy(data[2][1]['prerequisites'])
    concurrent = {**copy.deepcopy(leaf), 'kind': 'co_requisite'}
    choice = {'kind': 'any_of', 'items': [leaf, concurrent], 'source_spans': leaf['source_spans']}
    expression = {'kind': 'all_of', 'items': [choice], 'source_spans': leaf['source_spans']}
    data[2][1]['review_state'], data[2][1]['review_refs'] = 'draft', []
    data[2][1]['prerequisites'] = expression
    result = run(data)
    actual = result['courses'][1]['prerequisites']
    assert actual['kind'] == 'all_of' and actual['items'][0]['kind'] == 'any_of'
    assert [(x['kind'], x['course_id']) for x in actual['items'][0]['items']] == [
        ('course', 'course-1'), ('co_requisite', 'course-1')]
    assert actual['source_spans'][0]['text'] == expression['source_spans'][0]['text']
    data[2][1]['prerequisites']['items'][0]['items'].reverse()
    assert run(data)['content_sha256'] != result['content_sha256']
    assert run(data)['courses'][1]['prerequisites']['items'][0]['items'][0]['kind'] == 'co_requisite'


def test_unknown_requirement_and_absent_units_stay_unknown():
    data = fixture()
    course = data[2][1]
    course['facts'].pop('units.total')
    course['review_state'], course['review_refs'] = 'draft', []
    course['prerequisites'] = {'kind': 'unresolved', 'reason': 'Source condition is clipped',
                               'source_spans': course['prerequisites']['source_spans']}
    result = run(data)['courses'][1]
    assert 'units.total' not in result['facts']
    assert result['prerequisites']['kind'] == 'unresolved'
    assert result['review_state'] == 'draft'


@pytest.mark.parametrize('field,value', [
    ('program_id', 'other-program'), ('curriculum_id', 'other-curriculum'),
    ('source_version_id', 'ver-other'), ('course_id', 'course-1'),
    ('review_state', 'approved'), ('review_refs', []), ('review_refs', ['missing-review']),
    ('activation_allowed', True), ('rule_text', 'arbitrary Prolog'),
])
def test_rejects_identity_review_and_privilege_conflicts(field, value):
    data = fixture()
    data[2][1][field] = value
    with pytest.raises(ValueError):
        run(data)


@pytest.mark.parametrize('change', [
    {'version_id': 'ver-other'}, {'version_id': None}, {'byte_sha256': 'b' * 64},
    {'page': None}, {'text': None}, {'text': 'different course'},
])
def test_rejects_foreign_or_incomplete_fact_evidence(change):
    data = fixture()
    data[2][1]['facts']['course_code']['source_spans'][0].update(change)
    with pytest.raises(ValueError):
        run(data)


@pytest.mark.parametrize('value', [True, -1, float('nan'), float('inf'), '3', 4])
def test_units_are_supported_finite_numbers_not_defaults_or_coercions(value):
    data = fixture()
    data[2][1]['facts']['units.total']['value'] = value
    with pytest.raises(ValueError):
        run(data)


def test_numeric_evidence_must_be_the_complete_number():
    data = fixture()
    data[2][1]['facts']['units.total']['source_spans'][0]['text'] = '13'
    with pytest.raises(ValueError):
        run(data)


@pytest.mark.parametrize('node', [
    None, {}, {'kind': 'all_of', 'items': []}, {'kind': 'any_of', 'items': []},
    {'kind': 'unresolved', 'reason': ''}, {'kind': 'course', 'course_id': 'missing'},
    {'kind': 'course', 'course_id': 'course-2'}, {'kind': 'execute', 'text': 'call(user)'}
])
def test_missing_empty_or_dangling_requirements_never_become_none(node):
    data = fixture()
    if isinstance(node, dict):
        node['source_spans'] = data[2][1]['prerequisites']['source_spans']
    data[2][1]['prerequisites'] = node
    with pytest.raises(ValueError):
        run(data)


@pytest.mark.parametrize('change', [
    {'source_version_id': 'ver-other'}, {'course_digests': {}},
    {'reviewer_label': ''}, {'approval_id': 'forged'},
])
def test_review_reference_must_cover_the_exact_record_and_source(change):
    data = fixture()
    data[3][0].update(change)
    with pytest.raises(ValueError):
        run(data)


def test_private_source_and_private_identifiers_cannot_enter_institutional_ledger():
    data = fixture()
    record = data[1][0].model_dump(mode='json')
    record['namespace'] = 'private_session'
    data[1][0] = record
    with pytest.raises(ValueError):
        run(data)
    data = fixture()
    data[2][1]['course_id'] = 'fact-private-1'
    with pytest.raises(ValueError):
        run(data)


def test_duplicate_review_and_source_bindings_are_rejected():
    for collection in [1, 3]:
        data = fixture()
        data[collection].append(copy.deepcopy(data[collection][0]))
        with pytest.raises(ValueError):
            run(data)


def test_requirement_evidence_is_not_borrowed_from_another_source_version():
    data = fixture()
    data[2][1]['prerequisites']['source_spans'][0]['version_id'] = 'ver-other'
    with pytest.raises(ValueError):
        run(data)


def test_changed_translation_cannot_reuse_the_same_review_reference():
    data = fixture()
    node = data[2][1]['prerequisites']
    node['kind'] = 'co_requisite'
    with pytest.raises(ValueError, match='review.*(digest|content)'):
        run(data)


def test_review_coverage_cannot_be_borrowed_from_another_course():
    data = fixture()
    data[3][0]['course_digests'].pop('course-2')
    with pytest.raises(ValueError, match='review reference'):
        run(data)


def test_identical_code_from_other_version_cannot_supply_a_prerequisite():
    data = fixture()
    second = mint_pending_register([{'filename': 'other.pdf', 'sha256': 'b' * 64,
                                     'acquisition_locator': 'shelf:other'}], synthetic=True)[0]
    data[1].append(second)
    c = data[2][0]
    c['source_version_id'] = second.version_id
    c['review_state'], c['review_refs'] = 'draft', []
    for value in c['facts'].values():
        for s in value['source_spans']:
            s['byte_sha256'], s['version_id'] = second.byte_sha256, second.version_id
    c['prerequisites']['source_spans'][0].update(byte_sha256=second.byte_sha256, version_id=second.version_id)
    data[2][1]['review_state'], data[2][1]['review_refs'] = 'draft', []
    data[3].clear()
    with pytest.raises(ValueError, match='another source version'):
        run(data)


def repeated_code(titles=None, units=(3, 3)):
    """Two printed rows sharing one code (owner decision 23 Oct 2026: keep both, told apart by facts)."""
    scope, sources, courses, _ = fixture()
    for n, c in enumerate(courses):
        evidence = c['facts']['units.total']['source_spans'][0]
        c['facts']['course_code'] = {'value': 'SYN101', 'source_spans': [{**evidence, 'text': 'SYN101'}]}
        c['facts']['units.total'] = {'value': units[n], 'source_spans': [{**evidence, 'text': str(units[n])}]}
        if titles:
            c['facts']['course_title'] = {'value': titles[n], 'source_spans': [{**evidence, 'text': titles[n]}]}
        c['review_state'], c['review_refs'] = 'draft', []
    return scope, sources, courses


@pytest.mark.parametrize('titles,units', [(('Fictional Geopolitics', 'Fictional Fiscal Administration'), (3, 3)),
                                          (('Fictional Assessment', 'Fictional Assessment'), (5, 3))])
def test_repeated_printed_code_is_kept_when_title_or_units_differ(titles, units):
    scope, sources, courses = repeated_code(titles, units)
    result = build(scope, sources, courses)
    assert [c['facts']['course_code']['value'] for c in result['courses']] == ['SYN101', 'SYN101']
    assert len({c['course_id'] for c in result['courses']}) == 2


@pytest.mark.parametrize('titles', [None, ('Fictional Same', 'Fictional Same')])
def test_repeated_printed_code_without_distinguishing_facts_is_rejected(titles):
    scope, sources, courses = repeated_code(titles)
    with pytest.raises(ValueError, match='duplicate course code'):
        build(scope, sources, courses)


def test_explicit_printed_zero_units_is_not_missing_units():
    data = fixture()
    c = data[2][1]
    c['review_state'], c['review_refs'] = 'draft', []
    c['facts']['units.lab'] = copy.deepcopy(c['facts']['units.total'])
    c['facts']['units.lab']['value'] = 0
    c['facts']['units.lab']['source_spans'][0]['text'] = '0'
    assert run(data)['courses'][1]['facts']['units.lab']['value'] == 0


@pytest.mark.parametrize('location', ['text', 'locator', 'repair'])
def test_private_session_identifiers_in_span_metadata_are_rejected(location):
    data = fixture()
    c = data[2][1]
    c['review_state'], c['review_refs'] = 'draft', []
    evidence = c['prerequisites']['source_spans'][0]
    if location == 'text':
        evidence['text'] = 'fact-private-1'
    elif location == 'locator':
        evidence['locator']['cell_ids'] = ['fact-private-1']
    else:
        evidence['extraction']['repair_id'] = 'fact-private-1'
    with pytest.raises(ValueError, match='another namespace'):
        run(data)


def with_fact(name, value, printed):
    data = fixture()
    c = data[2][1]
    c['review_state'], c['review_refs'] = 'draft', []
    c['facts'][name] = copy.deepcopy(c['facts']['units.total'])
    c['facts'][name]['value'] = value
    c['facts'][name]['source_spans'][0]['text'] = printed
    return data


@pytest.mark.parametrize('value', ['2/1', '3 (2/1)'])
def test_printed_units_keep_the_printed_notation_as_text(value):
    facts = run(with_fact('units.printed', value, value))['courses'][1]['facts']
    assert facts['units.printed']['value'] == value


@pytest.mark.parametrize('value,printed', [('2/1', '2/1 3'), ('3', '2/1'), (3, '3')])
def test_printed_units_must_be_the_complete_printed_text(value, printed):
    with pytest.raises(ValueError):
        run(with_fact('units.printed', value, printed))


def test_rle_units_are_printed_numbers():
    assert run(with_fact('units.rle', 2, '2'))['courses'][1]['facts']['units.rle']['value'] == 2
    with pytest.raises(ValueError):
        run(with_fact('units.rle', '2', '2'))


def test_repeated_printed_code_is_kept_when_printed_units_differ():
    scope, sources, courses = repeated_code()
    for c, printed in zip(courses, ['2/1', '3/0']):
        evidence = c['facts']['units.total']['source_spans'][0]
        del c['facts']['units.total']
        c['facts']['units.printed'] = {'value': printed, 'source_spans': [{**evidence, 'text': printed}]}
    assert len(build(scope, sources, courses)['courses']) == 2
