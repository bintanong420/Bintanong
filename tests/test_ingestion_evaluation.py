import csv
import json

import pytest

from backend.bintanong_tools.knowledge_update import evaluation


def test_relational_error_is_visible_even_with_perfect_word_recall():
    expected = {'service': 'Undergraduate records', 'rows': [
        {'step': 'A', 'fee': '25', 'time': '5 days', 'office': 'Registrar'},
        {'step': 'B', 'fee': '50', 'time': '10 days', 'office': 'Registrar'}]}
    wrong = {'service': 'Undergraduate records', 'rows': [
        {'step': 'A', 'fee': '50', 'time': '10 days', 'office': 'Registrar'},
        {'step': 'B', 'fee': '25', 'time': '5 days', 'office': 'Registrar'}]}
    assert sorted(json.dumps(expected).split()) == sorted(json.dumps(wrong).split())
    assert evaluation.differences(expected, wrong) == [
        'rows.0.fee', 'rows.0.time', 'rows.1.fee', 'rows.1.time']
    assert not evaluation.differences(expected, expected)
    assert evaluation.differences({'fee': None}, {}) == ['fee']


def test_summary_preserves_unknown_measurements_and_matched_pages(tmp_path):
    rows = []
    for strategy in ['native', 'native_vision', 'llamaparse']:
        row = {k: '' for k in evaluation.METRICS}
        row.update(strategy=strategy, source_sha256='a' * 64, page='1')
        rows.append(row)
    inputs = tmp_path / 'inputs'
    inputs.mkdir()
    path = inputs / 'measurements.csv'
    def write():
        with path.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    write()
    report = evaluation.summarize(path, tmp_path / 'report')
    assert report['strategies']['native']['human_corrections'] is None
    assert report['strategies']['llamaparse']['review_minutes_per_page'] is None
    rows[0].update(human_corrections='2', review_minutes='3')
    write()
    report = evaluation.summarize(path, tmp_path / 'measured')
    assert report['strategies']['native']['human_corrections_per_100_pages'] == 200
    assert report['strategies']['native']['review_minutes_per_page'] == 3
    rows[-1]['page'] = '2'; write()
    with pytest.raises(ValueError, match='matched'):
        evaluation.summarize(path, tmp_path / 'invalid')


@pytest.mark.parametrize('value', ['-1', 'nan', 'inf', 'pretend'])
def test_bad_measurements_cannot_be_reported_as_accuracy(tmp_path, value):
    path = tmp_path / 'measurements.csv'
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['strategy', 'source_sha256', 'page', 'human_corrections'])
        w.writeheader()
        for strategy in ['native', 'native_vision', 'llamaparse']:
            w.writerow({'strategy': strategy, 'source_sha256': 'a' * 64, 'page': '1', 'human_corrections': value})
    with pytest.raises(ValueError):
        evaluation.summarize(path, tmp_path / 'report')


def test_recorded_extraction_mismatch_count_is_not_dropped(tmp_path):
    inputs = tmp_path / 'inputs'
    inputs.mkdir()
    path = inputs / 'measurements.csv'
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['strategy', 'source_sha256', 'page', 'extraction_mismatches'])
        writer.writeheader()
        for strategy, count in [('native', '2'), ('native_vision', '1'), ('llamaparse', '')]:
            writer.writerow({'strategy': strategy, 'source_sha256': 'a' * 64, 'page': 1,
                             'extraction_mismatches': count})
    report = evaluation.summarize(path, tmp_path / 'report')
    assert report['strategies']['native']['extraction_mismatches'] == 2
    assert report['strategies']['native_vision']['extraction_mismatches'] == 1
    assert report['strategies']['llamaparse']['extraction_mismatches'] is None
