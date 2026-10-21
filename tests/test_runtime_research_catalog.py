"""Research catalog and topic menu are derived from reviewed records only (fictional data)."""
from backend.bintanong_runtime.research import research_catalog, topic_menu


def course(cid, code, state='reviewed', refs=('review-fictional',)):
    return dict(course_id=cid, curriculum_id='curriculum-fictional', program_id='program-fictional',
                source_version_id='ver-fictional', review_state=state, review_refs=list(refs),
                facts=dict(course_code=dict(value=code)))


def ledger(*courses):
    return dict(scope=dict(curriculum_id='curriculum-fictional', program_id='program-fictional'),
                courses=list(courses))


def aliases(catalog):
    return {e.entity_id: set(e.aliases) for e in catalog}


def test_owner_alias_rule_adds_spacing_and_lab_suffix_variants():
    catalog = research_catalog(ledger(course('course-a', 'ZZ 5/L')))
    assert aliases(catalog) == {'course-a': {'ZZ 5/L', 'ZZ5/L', 'ZZ 5', 'ZZ5'}}
    entry = catalog[0]
    assert entry.kind == 'course' and entry.curriculum_id == 'curriculum-fictional'
    assert entry.source_ref == 'ver-fictional' and entry.review_ref == 'review-fictional'


def test_draft_identities_are_left_out():
    assert research_catalog(ledger(course('course-a', 'ZZ 1/L', state='draft', refs=()))) == ()


def test_short_forms_that_would_match_two_courses_are_not_created():
    catalog = research_catalog(ledger(course('course-a', 'ZZ 2/L'), course('course-b', 'ZZ 2')))
    assert aliases(catalog) == {'course-a': {'ZZ 2/L', 'ZZ2/L'}, 'course-b': {'ZZ 2', 'ZZ2'}}


def test_topic_menu_groups_every_reviewed_claim_by_subject():
    register = dict(reviews=[dict(subject_id='fees', claim='printed amount'),
                             dict(subject_id='office', claim='filing office'),
                             dict(subject_id='fees', claim='payment channel')])
    menu = topic_menu(register)
    assert [(t.subject_id, t.claims) for t in menu] == [
        ('fees', ('printed amount', 'payment channel')), ('office', ('filing office',))]


def test_research_release_wires_pin_adapters_registry_menu_and_scope(monkeypatch):
    from backend.bintanong_runtime import research
    from backend.bintanong_symbolic.bundle import prepare_runtime_bundle
    from test_symbolic_offline_research import real_fixture
    monkeypatch.setattr(research, 'SourceAwareEvidencePolicy', lambda **kw: object())
    # Real engine+policy are exercised by the equivalence check and the real-data run.
    monkeypatch.setattr(research, 'RetrievalEngine', lambda *a, **kw: object())
    ledger = real_fixture()
    chunk = dict(chunk_id='c' * 64, version_id='ver-doc-fictional', byte_sha256='d' * 64,
                 scope=['audience:undergraduate'], type_fields={}, spans=[], text='Fictional.')
    package = dict(chunks=[chunk], versions={'ver-doc-fictional': {}}, vectors={'c' * 64: [1.0, 0.0]},
                   manifest=dict(embedding_set_id='set-fictional', model_id='m', model_revision='r',
                       dimension=2, normalization='l2', prompt_fingerprint='p',
                       preprocessing_fingerprint='q', tokenizer_fingerprint='t'),
                   catalogue={}, register=dict(reviews=[dict(subject_id='fees', claim='printed amount')]))
    resources = research.build_research_resources(ledger, package, encoder=object(),
                                                   authorization_ref='research-fictional-test')
    pin = resources.pin
    assert pin.synthetic is False and pin.research_ref == 'research-fictional-test'
    assert pin.release_id == resources.symbolic.release_id
    assert {d.chunk_id for d in pin.documents} == {'c' * 64}
    assert {s.version_id for s in pin.sources} >= {'ver-doc-fictional'} | {
        s['version_id'] for s in prepare_runtime_bundle(ledger)['ledger']['sources']}
    assert resources.retrieval.research and resources.symbolic.research
    assert resources.registry._capabilities['check_prerequisite_eligibility'].name == 'offline_research_prerequisite_check'
    assert [t.subject_id for t in resources.topics] == ['fees']
    assert resources.document_scope == ('audience:undergraduate',)
