"""One research release serving several reviewed curricula (owner, 23 Oct 2026; fictional data).

Each curriculum keeps its own runtime, release identity and rule-bundle version; the pin lists them,
checks run on the curriculum named by the request, and a result is admitted only with the pinned
identity of that curriculum.
"""
import asyncio

import pytest

from backend.bintanong_contracts.runtime import PredicateRequest
from backend.bintanong_routing.contracts import RequestContext
from test_symbolic_authoring import fixture
from test_symbolic_compiler import rereview

C1, C2 = 'curriculum-synthetic-1', 'curriculum-synthetic-2'


def real_ledger(curriculum, first, second):
    data = fixture()
    data[0]['curriculum_id'] = curriculum
    rename = {'course-1': first, 'course-2': second}
    for c in data[2]:
        c['curriculum_id'] = curriculum
        c['course_id'] = rename[c['course_id']]
        if c['prerequisites'].get('course_id') in rename:
            c['prerequisites']['course_id'] = rename[c['prerequisites']['course_id']]
    source = data[1][0].model_dump(mode='json'); source['synthetic'] = False
    return rereview((data[0], [source], data[2], data[3]))


def build(monkeypatch, *, single=False, change_package=None, engine_factory=None):
    from backend.bintanong_runtime import research
    monkeypatch.setattr(research, 'SourceAwareEvidencePolicy', lambda **kw: object())
    monkeypatch.setattr(research, 'RetrievalEngine', engine_factory or (lambda *a, **kw: object()))
    chunk = dict(chunk_id='c' * 64, version_id='ver-doc-fictional', byte_sha256='d' * 64,
                 scope=['audience:undergraduate'], type_fields={}, spans=[], text='Fictional.')
    package = dict(chunks=[chunk], versions={'ver-doc-fictional': {}}, vectors={'c' * 64: [1.0, 0.0]},
                   manifest=dict(embedding_set_id='set-fictional', model_id='m', model_revision='r',
                       dimension=2, normalization='l2', prompt_fingerprint='p',
                       preprocessing_fingerprint='q', tokenizer_fingerprint='t'),
                   catalogue={}, register=dict(reviews=[dict(subject_id='fees', claim='printed amount')]))
    ledgers = {C1: real_ledger(C1, 'course-1', 'course-2'), C2: real_ledger(C2, 'course-3', 'course-4')}
    if change_package:
        change_package(package)
    if single:
        return research.build_research_resources(ledgers[C1], package, encoder=object(),
            authorization_ref='research-fictional-test'), ledgers
    return research.build_multi_research_resources(ledgers, package, encoder=object(),
                                                   authorization_ref='research-fictional-test'), ledgers


@pytest.mark.parametrize('single', [False, True])
def test_only_pre_enrollment_gets_the_approved_larger_context_budget(monkeypatch, single):
    captured = []
    def engine_factory(*args, **kwargs):
        captured.append(kwargs.get('subject_context_budgets', {}))
        return object()
    build(monkeypatch, single=single, engine_factory=engine_factory)
    assert captured[-1] == {}
    def add_procedure(package):
        package['register']['reviews'].append(dict(subject_id='pre_enrollment', claim='printed steps'))
    build(monkeypatch, single=single, change_package=add_procedure, engine_factory=engine_factory)
    assert captured[-1] == {'pre_enrollment':4096}


@pytest.mark.parametrize('single', [False, True])
def test_document_only_changes_get_a_new_root_without_changing_curriculum_rules(monkeypatch, single):
    original, _ = build(monkeypatch, single=single)
    for change in ('embedding_set', 'claim_review'):
        def change_package(package):
            if change == 'embedding_set':
                package['manifest']['embedding_set_id'] = 'set-fictional-expanded'
            else:
                package['register']['reviews'].append(dict(subject_id='fees', claim='printed fee scope'))
        changed, _ = build(monkeypatch, single=single, change_package=change_package)
        assert changed.pin.release_id != original.pin.release_id, change
        assert changed.pin.rule_bundle_version == original.pin.rule_bundle_version
        assert changed.pin.sources == original.pin.sources
    unchanged, _ = build(monkeypatch, single=single)
    assert unchanged.pin == original.pin


def check(resources, curriculum, course):
    request = PredicateRequest.parse({'predicate': 'check_prerequisite_eligibility', 'inputs': [
        {'name': 'course_id', 'value': course, 'fact_ref': None},
        {'name': 'curriculum_id', 'value': curriculum, 'fact_ref': None}]})
    context = RequestContext.parse(dict(session_id='sess-fictional', request_id='req-fictional',
                                        program_id='program-synthetic', curriculum_id=curriculum, facts=[]))
    return asyncio.run(resources.symbolic.execute(request, context))


def test_one_release_pins_every_curriculum_and_catalogs_all_courses(monkeypatch):
    resources, ledgers = build(monkeypatch)
    members = {m.curriculum_id: m for m in resources.pin.curricula}
    assert set(members) == {C1, C2}
    assert len({m.rule_bundle_version for m in members.values()}) == 2
    assert resources.symbolic.release_id == resources.pin.release_id
    assert resources.symbolic.rule_bundle_version == resources.pin.rule_bundle_version
    assert {(e.curriculum_id, e.entity_id) for e in resources.catalog} == {
        (C1, 'course-1'), (C1, 'course-2'), (C2, 'course-3'), (C2, 'course-4')}


def test_check_runs_on_the_requested_curriculum_and_is_admitted(monkeypatch):
    from backend.bintanong_orchestration.integration import assemble
    resources, _ = build(monkeypatch)
    result = check(resources, C2, 'course-4')
    member = {m.curriculum_id: m for m in resources.pin.curricula}[C2]
    assert result.rule_bundle_version == member.rule_bundle_version
    assert result.scope.knowledge_release_id == member.release_id
    assert assemble(resources.pin, 'Symbolic', symbolic=result).status == 'unknown'  # no grades supplied


def test_result_with_another_curriculums_identity_is_refused(monkeypatch):
    from backend.bintanong_orchestration.integration import assemble
    resources, _ = build(monkeypatch)
    result = check(resources, C2, 'course-4')
    data = resources.pin.model_dump(mode='json')
    for m in data['curricula']:  # swap the pinned identities of the two curricula
        m['curriculum_id'] = C1 if m['curriculum_id'] == C2 else C2
    swapped = type(resources.pin).parse(data)
    assert assemble(swapped, 'Symbolic', symbolic=result).status == 'release_mismatch'


def test_check_for_a_curriculum_outside_the_release_is_refused(monkeypatch):
    resources, _ = build(monkeypatch)
    with pytest.raises(ValueError, match='curriculum_not_in_release'):
        check(resources, 'curriculum-synthetic-9', 'course-4')


def test_program_and_curriculum_names_are_cataloged_for_reviewed_curricula(monkeypatch):
    from backend.bintanong_runtime import research
    monkeypatch.setattr(research, 'SourceAwareEvidencePolicy', lambda **kw: object())
    monkeypatch.setattr(research, 'RetrievalEngine', lambda *a, **kw: object())
    _, ledgers = build(monkeypatch)
    package = dict(chunks=[], versions={}, vectors={}, catalogue={}, register=dict(reviews=[]),
                   manifest=dict(embedding_set_id='set-fictional', model_id='m', model_revision='r', dimension=2,
                       normalization='l2', prompt_fingerprint='p', preprocessing_fingerprint='q', tokenizer_fingerprint='t'))
    resources = research.build_multi_research_resources(ledgers, package, encoder=object(),
        authorization_ref='research-fictional-test', program_names={'program-synthetic': ['Fictional Program']},
        curriculum_names={C1: ['Year One'], C2: ['Year Two']})
    entries = {(e.kind, e.entity_id): set(e.aliases) for e in resources.catalog if e.kind != 'course'}
    assert entries == {('program', 'program-synthetic'): {'Fictional Program'},
                       ('curriculum', C1): {'Year One'}, ('curriculum', C2): {'Year Two'}}


def test_names_for_programs_outside_the_release_are_ignored(monkeypatch):
    from backend.bintanong_runtime import research
    monkeypatch.setattr(research, 'SourceAwareEvidencePolicy', lambda **kw: object())
    monkeypatch.setattr(research, 'RetrievalEngine', lambda *a, **kw: object())
    _, ledgers = build(monkeypatch)
    package = dict(chunks=[], versions={}, vectors={}, catalogue={}, register=dict(reviews=[]),
                   manifest=dict(embedding_set_id='set-fictional', model_id='m', model_revision='r', dimension=2,
                       normalization='l2', prompt_fingerprint='p', preprocessing_fingerprint='q', tokenizer_fingerprint='t'))
    resources = research.build_multi_research_resources(ledgers, package, encoder=object(),
        authorization_ref='research-fictional-test', program_names={'program-absent': ['Absent']}, curriculum_names={})
    assert not [e for e in resources.catalog if e.kind != 'course']


def test_course_fact_lookups_are_offered_with_their_own_inputs(monkeypatch):
    resources, _ = build(monkeypatch)
    term = PredicateRequest.parse({'predicate': 'list_term_courses', 'inputs': [
        {'name': 'curriculum_id', 'value': C1, 'fact_ref': None}, {'name': 'year_level', 'value': '1', 'fact_ref': None},
        {'name': 'semester', 'value': 'any', 'fact_ref': None}]})
    resources.registry.goal(term)  # fixed signature accepted
    context = RequestContext.parse(dict(session_id='sess-fictional', request_id='req-fictional',
                                        program_id='program-synthetic', curriculum_id=C1, facts=[]))
    result = asyncio.run(resources.symbolic.execute(term, context))
    # The fictional ledger has codes and units but no reviewed year/semester: unknown, never a partial list.
    assert result.status == 'not_reviewed' and result.synthetic is False
