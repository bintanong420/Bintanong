"""Every simulated prerequisite pass contributing to an earliest term keeps its rule evidence."""
import pytest
from test_planning_check import curriculum
from backend.bintanong_planning.chat import earliest_term


def test_earliest_term_keeps_intermediate_chain_rules_and_source_regions(curriculum):
    key, runtime, c = curriculum
    spans = {}
    class DistinctRegions:
        def look_up(self, request):
            return runtime.look_up(request)
        def check(self, request, facts):
            result = runtime.check(request, facts)
            course = next(i.value for i in request.inputs if i.name == 'course_id')
            region = result.rule_spans[0].model_copy(update={'locator':result.rule_spans[0].locator.model_copy(
                update={'kind':'docling_ref', 'ref':'fictional-rule/' + course,
                        'cell_ids':(), 'item_ids':(), 'table_index':None})})
            spans[course] = region
            return result.model_copy(update={'rule_spans':(region,)})
    result = earliest_term(DistinctRegions(), key, c('Z'), [(c('X'), 'failed')], (2, 'second_semester'))
    assert result.status == 'found'
    assert {f'rule-{c(name)}' for name in ('X', 'D1', 'Z')} <= set(result.rule_ids)
    assert all(spans[c(name)] in result.rule_spans for name in ('X', 'D1', 'Z'))


def test_earliest_chain_cannot_combine_rules_from_different_releases(curriculum):
    key, runtime, c = curriculum
    class ForeignRule:
        def look_up(self, request):
            return runtime.look_up(request)
        def check(self, request, facts):
            result = runtime.check(request, facts)
            course = next(i.value for i in request.inputs if i.name == 'course_id')
            if course == c('D1') and result.decision.outcome == 'eligible':
                result = result.model_copy(update={'scope':result.scope.model_copy(
                    update={'knowledge_release_id':'release-foreign'})})
            return result
    with pytest.raises(ValueError, match='earliest_rule_release_mismatch'):
        earliest_term(ForeignRule(), key, c('Z'), [(c('X'), 'failed')], (2, 'second_semester'))
