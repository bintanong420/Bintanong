"""Research catalog and topic menu are derived from reviewed records only (fictional data)."""
import json
import pytest
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
    assert resources.course_labels == research.course_labels(ledger)


def test_course_labels_cover_every_printed_code_including_drafts():
    from backend.bintanong_runtime.research import course_labels
    assert course_labels(ledger(course('course-a', 'ZZ 5/L'), course('course-b', 'ZZ 1/L', state='draft'))) == (
        ('course-a', 'ZZ 5/L'), ('course-b', 'ZZ 1/L'))


def test_topic_menu_adds_recorded_not_stated_claims_per_subject():
    register = dict(reviews=[dict(subject_id='fees', claim='printed amount')])
    catalogue = dict(assignments=[dict(reading_id='R1', subject_id='fees')])
    chunks = [dict(chunk_id='a', type_fields=dict(reading_id='R1'), text=json.dumps(dict(fields=[],
        source_limits=[dict(affected_claims=['individual share'], issue='claim_not_stated',
                            resolution='unresolved')])))]
    menu = topic_menu(register, catalogue=catalogue, chunks=chunks)
    assert [(t.subject_id, t.claims, t.not_stated) for t in menu] == [
        ('fees', ('printed amount',), ('individual share',))]


def test_claim_reviewed_as_not_stated_is_offered_as_not_stated_only():
    # Run 10 (23 Oct 2026): the pre-enrollment deadline was reviewed not_stated_in_selected_fields but
    # was offered as an answerable claim; the router requested it unasked and every answer was withheld.
    register = dict(reviews=[dict(subject_id='enrol', claim='first-step fields', finding='visible_fields'),
                             dict(subject_id='enrol', claim='deadline', finding='not_stated_in_selected_fields')])
    menu = topic_menu(register)
    assert [(t.subject_id, t.claims, t.not_stated) for t in menu] == [('enrol', ('first-step fields',), ('deadline',))]


def titled(cid, code, title):
    c = course(cid, code); c['facts']['course_title'] = dict(value=title); return c


def test_repeated_printed_code_is_cataloged_twice_so_a_code_only_question_must_choose():
    # Owner, 23 Oct 2026: keep both printed rows; a code-only mention matches two entries (clarify).
    # Each row's unique printed title still names it.
    catalog = research_catalog(ledger(titled('course-a', 'ZZ 5', 'Fictional Geo'), titled('course-b', 'ZZ 5', 'Fictional Fiscal')))
    assert aliases(catalog) == {'course-a': {'ZZ 5', 'ZZ5', 'Fictional Geo'}, 'course-b': {'ZZ 5', 'ZZ5', 'Fictional Fiscal'}}


def test_repeated_printed_code_is_labelled_with_its_title():
    from backend.bintanong_runtime.research import course_labels
    labels = course_labels(ledger(titled('course-a', 'ZZ 5', 'Fictional Geo'), titled('course-b', 'ZZ 5', 'Fictional Fiscal'),
                                  course('course-c', 'ZZ 6')))
    assert labels == (('course-a', 'ZZ 5 (Fictional Geo)'), ('course-b', 'ZZ 5 (Fictional Fiscal)'), ('course-c', 'ZZ 6'))


def test_repeated_printed_code_without_titles_is_still_refused():
    import pytest
    with pytest.raises(ValueError, match='duplicate_printed_course_code'):
        research_catalog(ledger(course('course-a', 'ZZ 5'), course('course-b', 'ZZ 5')))


def test_repeated_code_and_title_are_labelled_with_units():
    from backend.bintanong_runtime.research import course_labels
    a, b = titled('course-a', 'ZZ 13', 'Fictional Assessment'), titled('course-b', 'ZZ 13', 'Fictional Assessment')
    a['facts']['units.total'], b['facts']['units.total'] = dict(value=5), dict(value=3)
    assert course_labels(ledger(a, b)) == (('course-a', 'ZZ 13 (Fictional Assessment, 5 units)'),
                                           ('course-b', 'ZZ 13 (Fictional Assessment, 3 units)'))


def test_individual_assessment_gets_the_owner_approved_per_person_cues():
    register = dict(reviews=[dict(subject_id='fees', claim='printed example', finding='visible_fields'),
                             dict(subject_id='fees', claim='official individual student assessment',
                                  finding='not_stated_in_selected_fields')])
    (topic,) = topic_menu(register)
    (cue,) = topic.cues
    assert cue.claim == 'official individual student assessment'
    assert {'each student', 'per student', 'bawat isa'} <= set(cue.phrases)


def test_a_printed_title_unique_in_the_curriculum_names_its_course():
    catalog = research_catalog(ledger(titled('course-a', 'ZZ 7', 'Fictional Data Structures'),
                                      titled('course-b', 'ZZ 8', 'Fictional Writing')))
    assert aliases(catalog) == {'course-a': {'ZZ 7', 'ZZ7', 'Fictional Data Structures'},
                                'course-b': {'ZZ 8', 'ZZ8', 'Fictional Writing'}}


def test_a_title_printed_on_two_courses_is_not_an_alias():
    catalog = research_catalog(ledger(titled('course-a', 'ZZ 7', 'Fictional Seminar'),
                                      titled('course-b', 'ZZ 8', 'fictional  seminar')))
    assert aliases(catalog) == {'course-a': {'ZZ 7', 'ZZ7'}, 'course-b': {'ZZ 8', 'ZZ8'}}


def test_a_title_spelled_like_another_course_code_is_not_an_alias():
    catalog = research_catalog(ledger(titled('course-a', 'ZZ 7', 'zz 8'), course('course-b', 'ZZ 8')))
    assert aliases(catalog) == {'course-a': {'ZZ 7', 'ZZ7'}, 'course-b': {'ZZ 8', 'ZZ8'}}


@pytest.mark.parametrize('issue', ['source_cutoff', 'malformed_source_condition',
    'conflicting_deadlines', 'printed_total_discrepancy', 'effectivity_currentness_unknown', 'claim_not_stated'])
def test_router_can_select_every_recorded_unresolved_source_limitation(issue):
    register = {'reviews':[dict(subject_id='synthetic_policy',claim='visible printed field',finding='visible_fields')]}
    catalogue = {'assignments':[dict(reading_id='synthetic-row',subject_id='synthetic_policy')]}
    chunks = [dict(type_fields=dict(reading_id='synthetic-row'),text=json.dumps(dict(source_limits=[
        dict(issue=issue,resolution='unresolved',affected_claims=['the missing or uncertain condition'])])))]
    topic, = topic_menu(register,catalogue=catalogue,chunks=chunks)
    assert topic.claims == ('visible printed field',)
    assert topic.not_stated == ('the missing or uncertain condition',)
