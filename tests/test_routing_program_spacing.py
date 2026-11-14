"""Program aliases retain their identity when a student omits spaces."""
import pytest

from backend.bintanong_routing.contracts import CatalogEntry
from test_routing_contracts import context, proposal
from test_routing_validation import catalog, validate


def program(entity, alias):
    return CatalogEntry.parse(dict(kind='program', entity_id=entity, program_id=entity,
        curriculum_id=None, aliases=[alias], source_ref='ver-a', review_ref='review-a', reviewed=True))


@pytest.mark.parametrize('words', ['ZQArts', 'zqarts', 'ZQ Arts', 'ZQArts student'])
@pytest.mark.parametrize('scoped', [True, False])
def test_compact_program_alias_keeps_a_scoped_course_request_answerable(words, scoped):
    text = f'{words}: A1'
    value = proposal(text=text, mentions=[dict(kind='program', text=words, start=0, end=len(words)),
        dict(kind='course', text='A1', start=len(words)+2, end=len(text))],
        operations=[dict(name='check_prerequisite_eligibility', target=1)])
    result = validate(text, value=value,
        ctx=context() if scoped else context(program_id=None, curriculum_id=None),
        catalog=(*(e for e in catalog() if e.kind != 'program'), program('program-a', 'ZQ Arts')))
    assert result.diagnostic == 'validated'
    assert result.decision.predicate_request is not None
    assert result.program_id == 'program-a' and result.curriculum_id == 'curriculum-a'


@pytest.mark.parametrize('words', ['ZQArtsExtra', 'otherZQArts'])
def test_compact_program_alias_does_not_match_inside_an_unrelated_word(words):
    text = f'{words}: A1'
    value = proposal(text=text, mentions=[dict(kind='program', text=words, start=0, end=len(words)),
        dict(kind='course', text='A1', start=len(words)+2, end=len(text))],
        operations=[dict(name='check_prerequisite_eligibility', target=1)])
    result = validate(text, value=value, catalog=(*(e for e in catalog() if e.kind != 'program'), program('program-a', 'ZQ Arts')))
    assert result.decision.control == 'clarify'
    assert result.decision.predicate_request is None


def test_colliding_compact_program_aliases_still_need_clarification():
    text = 'ZQArts: A1'
    value = proposal(text=text, mentions=[dict(kind='program', text='ZQArts', start=0, end=6),
        dict(kind='course', text='A1', start=8, end=10)],
        operations=[dict(name='check_prerequisite_eligibility', target=1)])
    result = validate(text, value=value, ctx=context(program_id=None, curriculum_id=None),
        catalog=(*(e for e in catalog() if e.kind != 'program'), program('program-a', 'ZQ Arts'),
                                               program('program-b', 'ZQ Arts')))
    assert result.decision.control == 'clarify'
    assert result.decision.predicate_request is None
