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
