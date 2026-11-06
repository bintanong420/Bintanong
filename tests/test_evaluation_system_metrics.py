"""Benchmark roster and metric definitions (master 17.3). Synthetic chunk ids and runs only."""
import json

import pytest

from evaluation.system_metrics import (answer_metrics, build_report, load_roster, main, normalize_question,
                                       retrieval_case_metrics, route_metrics, select_runs)


def run(run_id, case_id, outcome='completed', commit='c', release='r', **extra):
    return dict(record_type='run', run_id=run_id, case_id=case_id, outcome=outcome, code_commit=commit,
                release_id=release, **extra)


def test_roster_is_exactly_24_rows_by_3_languages():
    rows = load_roster()
    assert len(rows) == 72 and len({normalize_question(r['question']) for r in rows}) == 72
    assert {r['row'] for r in rows} == set(range(1, 25))
    assert {r['case_id'] for r in rows if r['row'] == 7} == {'A07-EN', 'A07-TG', 'A07-TL'}
    assert {r['case_id'] for r in rows if r['row'] == 24} == {'B24-EN', 'B24-TG', 'B24-TL'}


def test_each_row_carries_the_curriculum_the_picker_would_hold():
    scopes = {row['row']: (row['program_id'], row['curriculum_id']) for row in load_roster()}
    assert scopes[1] == ('palsu-bscs', 'bscs-2018-2019') and scopes[2] == ('palsu-bsit', 'bsit-2018-2019')
    assert scopes[3] == ('palsu-bsce', 'bsce-2018-2019') and scopes[4] == ('palsu-bsed-math', 'bsed-math-2018-2019')
    assert scopes[5] == ('palsu-bsn', 'bsn-2018-2019') and scopes[6] == ('palsu-bstm', 'bstm-2018-2019')
    assert scopes[8] == ('palsu-bsit', 'bsit-2018-2019') and scopes[9] == ('palsu-bscrim', 'bscrim-2018-2019')
    assert scopes[7] == (None, None)
    assert all(scopes[row] == ('palsu-bscs', 'bscs-2018-2019') for row in range(10, 25))


def test_normalize_question_ignores_case_and_spacing_only():
    assert normalize_question('  How to\n DROP  subjects? ') == 'how to drop subjects?'
    assert normalize_question('How to drop subject?') != normalize_question('How to drop subjects?')


def test_retrieval_example_and_single_chunk_ceiling():
    m = retrieval_case_metrics(['a', 'x', 'b'], {'a', 'b', 'c', 'd'}, searches=1)
    assert (m['precision_at_3'], m['recall_at_3']) == (2/3, 1/2) and round(m['f1_at_3'], 2) == .57
    one = retrieval_case_metrics(['a'], {'a'}, searches=1)
    assert one['precision_at_3'] == 1/3 and one['precision_returned'] == 1 and one['f1_at_3'] == .5


def test_no_search_scores_zero_not_skipped():
    m = retrieval_case_metrics([], {'a'}, searches=0)
    assert (m['precision_at_3'], m['recall_at_3'], m['hit_at_3']) == (0, 0, False)
    assert m['f1_at_3'] == 0 and m['precision_returned'] == 0


def test_two_searches_use_k_of_six():
    assert retrieval_case_metrics(['a', 'b', 'c', 'd', 'e', 'f'], {'a'}, searches=2)['precision_at_3'] == 1/6


def test_the_same_chunk_in_two_searches_counts_once():
    assert retrieval_case_metrics(['a', 'a'], {'a', 'b'}, searches=2)['hits'] == 1


def test_unkeyed_empty_relevant_set_has_undefined_recall():
    m = retrieval_case_metrics(['a'], set(), searches=1)
    assert m['recall_at_3'] is None and m['f1_at_3'] is None


def test_macro_f1_uses_classes_with_gold_and_keeps_predicted_only_in_confusion():
    m = route_metrics([('RAG', 'RAG'), ('RAG', 'Hybrid'), ('Symbolic', 'Symbolic')])
    assert m['accuracy'] == 2/3 and 'Hybrid' not in m['macro_classes'] and m['confusion']['RAG']['Hybrid'] == 1
    assert m['per_class']['RAG'] == dict(precision=1, recall=1/2, f1=2/3, support=2)
    assert m['macro_f1'] == (2/3 + 1) / 2


def test_answer_precision_recall_definitions():
    rows = [dict(expected='answer', given=True, mark='correct'),
            dict(expected='answer', given=True, mark='wrong'),
            dict(expected='answer', given=False, mark='wrong'),
            dict(expected='clarification', given=False, mark='correct')]
    m = answer_metrics(rows, partial_counts=False)
    assert (m['accuracy'], m['precision'], m['recall']) == (1/2, 1/2, 1/3) and m['n'] == 4


def test_partial_is_wrong_in_strict_and_right_in_lenient():
    rows = [dict(expected='answer', given=True, mark='partial')]
    assert answer_metrics(rows, partial_counts=False)['accuracy'] == 0
    assert answer_metrics(rows, partial_counts=True)['accuracy'] == 1


def test_no_answers_given_leaves_precision_undefined():
    m = answer_metrics([dict(expected='answer', given=False, mark='wrong')], partial_counts=False)
    assert m['precision'] is None and m['recall'] == 0 and m['f1'] is None


def test_first_completed_run_counts_and_failures_or_unmatched_do_not():
    selected = select_runs([run('r1', 'B11-EN', 'infrastructure_error'), run('r2', 'B11-EN'), run('r3', 'B11-EN'),
                            run('r4', None)])
    assert selected.scored['B11-EN']['run_id'] == 'r2'
    assert [r['run_id'] for r in selected.reruns] == ['r3']
    assert [r['run_id'] for r in selected.unmatched] == ['r4'] and [r['run_id'] for r in selected.failed] == ['r1']


def test_mixed_commit_or_release_is_refused():
    with pytest.raises(ValueError, match='mixed_runs'):
        select_runs([run('r1', 'B11-EN', commit='a'), run('r2', 'B12-EN', commit='b')])
    with pytest.raises(ValueError, match='mixed_runs'):
        select_runs([run('r1', 'B11-EN', release='a'), run('r2', 'B12-EN', release='b')])


def rows(*ids):
    return [dict(chunk_id=identity) for identity in ids]


def key(key_id, cases, status='keyed', relevant=(), route='RAG', outcome='answer'):
    return dict(key_id=key_id, case_ids=list(cases), expected_route=route, expected_outcome=outcome,
                key_status=status, relevant_chunk_ids=list(relevant), expected_facts=[], source_note='synthetic')


def scored_run(run_id, case_id, topic, everything, route='RAG', status='answered'):
    return run(run_id, case_id, route_label=route, answer=dict(status=status),
               searches=[dict(query='q', topic_bound=rows(*topic), all_chunks=rows(*everything))])


def judgment(run_id, mark='correct', **chunk_marks):
    return dict(record_type='judgment', run_id=run_id, answer_mark=mark, chunk_marks=chunk_marks, note='')


def test_report_scores_each_list_separately_from_the_key():
    report = build_report([scored_run('r1', 'B11-EN', ['a'], ['x', 'a', 'y']), judgment('r1')],
                          dict(keys=[key('k', ['B11-EN'], relevant=['a'])]))
    assert report['retrieval']['topic_bound']['overall']['precision_at_3'] == 1/3
    assert report['retrieval']['topic_bound']['overall']['precision_returned'] == 1
    assert report['retrieval']['all_chunks']['overall']['precision_at_3'] == 1/3
    assert report['retrieval']['all_chunks']['overall']['precision_returned'] == 1/3
    assert report['retrieval']['all_chunks']['by_language']['EN']['n'] == 1


def test_report_counts_a_misrouted_retrieval_question_as_a_topic_bound_miss():
    misrouted = run('r1', 'B11-EN', route_label='clarify', answer=dict(status='clarification_needed'),
                    searches=[dict(query='q', topic_bound=[], all_chunks=rows('a'))])
    report = build_report([misrouted, judgment('r1', 'wrong')], dict(keys=[key('k', ['B11-EN'], relevant=['a'])]))
    assert report['retrieval']['topic_bound']['overall']['recall_at_3'] == 0
    assert report['retrieval']['all_chunks']['overall']['recall_at_3'] == 1
    assert report['route']['confusion']['RAG']['clarify'] == 1


def test_report_leaves_rule_only_questions_out_of_retrieval_metrics():
    prolog = run('r1', 'A01-EN', route_label='Symbolic', answer=dict(status='answered'),
                 searches=[dict(query='q', topic_bound=[], all_chunks=rows('a'))])
    report = build_report([prolog, judgment('r1')], dict(keys=[key('k', ['A01-EN'], route='Symbolic')]))
    assert report['retrieval']['all_chunks']['overall']['n'] == 0 and report['route']['accuracy'] == 1


def test_unkeyed_row_pools_owner_marks_across_its_languages_and_says_so():
    records = [scored_run('r1', 'B11-EN', ['a'], ['a']), judgment('r1', a=True),
               scored_run('r2', 'B11-TL', ['b'], ['b']), judgment('r2', b=True)]
    report = build_report(records, dict(keys=[key('k', ['B11-EN', 'B11-TL'], status='human_judged')]))
    assert report['retrieval']['topic_bound']['overall']['recall_at_3'] == 1/2
    assert report['pooled_recall_cases'] == ['B11-EN', 'B11-TL']


def test_keyed_row_keeps_the_key_and_lists_a_disagreement():
    records = [scored_run('r1', 'B11-EN', ['a', 'b'], ['a', 'b']), judgment('r1', a=False, b=True)]
    report = build_report(records, dict(keys=[key('k', ['B11-EN'], relevant=['a'])]))
    assert report['retrieval']['topic_bound']['overall']['hit_at_3'] == 1
    assert report['key_disagreements'] == [dict(case_id='B11-EN', chunk_id='a', key=True, owner=False),
                                           dict(case_id='B11-EN', chunk_id='b', key=False, owner=True)]


def test_latest_judgment_wins_and_unjudged_answers_are_listed_not_scored():
    records = [scored_run('r1', 'B11-EN', ['a'], ['a']), judgment('r1', 'wrong'), judgment('r1', 'correct'),
               scored_run('r2', 'B12-EN', ['a'], ['a'])]
    report = build_report(records, dict(keys=[key('k', ['B11-EN', 'B12-EN'], relevant=['a'])]))
    assert report['answer']['strict']['accuracy'] == 1 and report['answer']['strict']['n'] == 1
    assert report['unjudged_answers'] == ['B12-EN']


def test_report_lists_what_was_left_out_and_carries_disclosures():
    records = [run('r1', 'B11-EN', 'infrastructure_error'), run('r2', None, question='typo')]
    report = build_report(records, dict(keys=[key('k', ['B11-EN'], relevant=['a'])]))
    assert report['failed_runs'] == ['r1'] and report['unmatched_runs'] == ['r2']
    assert report['missing_cases'] == sorted(r['case_id'] for r in load_roster())
    assert any('refusal' in line for line in report['disclosures'])


def test_cli_writes_json_and_markdown(tmp_path):
    runs = tmp_path / 'runs.jsonl'
    runs.write_text('\n'.join(json.dumps(r) for r in [scored_run('r1', 'B11-EN', ['a'], ['a']), judgment('r1')]) + '\n',
                    encoding='utf-8')
    keys = tmp_path / 'keys.json'
    keys.write_text(json.dumps(dict(keys=[key('k', ['B11-EN'], relevant=['a'])])), encoding='utf-8')
    main(['--runs', str(runs), '--keys', str(keys), '--out', str(tmp_path / 'out')])
    assert json.loads((tmp_path / 'out' / 'report.json').read_text(encoding='utf-8'))['route']['accuracy'] == 1
    markdown = (tmp_path / 'out' / 'report.md').read_text(encoding='utf-8')
    assert 'Topic-bound' in markdown and 'All chunks' in markdown and 'development results' in markdown
