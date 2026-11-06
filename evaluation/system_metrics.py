"""Route, retrieval and final-answer metrics for the 72-query benchmark (master 17.3).

Each metric names its unit, positive class and denominator. Chunk-level accuracy is deliberately absent: about 557
true negatives per query would put it near 100% whatever the quality. Results are development evidence, not
institutional validation.
"""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re

ROSTER_PATH = Path(__file__).with_name('benchmark') / 'roster-72.json'
RETRIEVAL_ROUTES = ('RAG', 'Hybrid')
LISTS = (('topic_bound', 'Topic-bound'), ('all_chunks', 'All chunks'))
DISCLOSURES = (
    'These are development results: the 72 questions informed earlier fixes.',
    'One author prepared the keys and judged the answers; no inter-rater agreement was measured.',
    'The roster has no out-of-scope or unanswerable question, so correct refusal is not measured.',
    'Precision@3 cannot exceed 1/3, and F1@3 cannot exceed 0.5, when only one chunk is relevant.',
    'Recall labelled pooled covers only chunks a person saw, so it can overstate true recall.',
)


def load_roster(path=ROSTER_PATH):
    document = json.loads(Path(path).read_text(encoding='utf-8'))
    return [dict(case_id=f"{row['subset']}{row['row']:02d}-{language.upper()}", row=row['row'], subset=row['subset'],
                 category=row['category'], language=language.upper(), question=row[language])
            for row in document['rows'] for language in ('en', 'tg', 'tl')]


def normalize_question(text):
    return re.sub(r'\s+', ' ', text).strip().casefold()


def _ratio(part, whole):
    return part / whole if whole else None


def _f1(precision, recall):
    if precision is None or recall is None:
        return None
    return 2 * precision * recall / (precision + recall) if precision + recall else 0


def retrieval_case_metrics(returned_ids, relevant_ids, searches):
    """One query's ranked chunks. k is 3 per search, so a missed or small search is not flattered."""
    returned = set(returned_ids)
    hits = len(returned & set(relevant_ids))
    precision = hits / (3 * max(searches, 1))
    recall = _ratio(hits, len(relevant_ids))
    return dict(hits=hits, precision_at_3=precision, precision_returned=_ratio(hits, len(returned)) or 0,
                recall_at_3=recall, f1_at_3=_f1(precision, recall), hit_at_3=hits > 0)


def route_metrics(pairs):
    """One expected and one selected route per query. Macro-F1 averages only classes with expected queries."""
    expected_classes = sorted({expected for expected, _ in pairs})
    classes = sorted({label for pair in pairs for label in pair})
    confusion = {expected: {} for expected in expected_classes}
    for expected, predicted in pairs:
        confusion[expected][predicted] = confusion[expected].get(predicted, 0) + 1
    per_class = {}
    for label in classes:
        correct = sum(1 for pair in pairs if pair == (label, label))
        support = sum(1 for expected, _ in pairs if expected == label)
        precision = _ratio(correct, sum(1 for _, predicted in pairs if predicted == label))
        recall = _ratio(correct, support)
        per_class[label] = dict(precision=precision, recall=recall, f1=_f1(precision, recall), support=support)
    scores = [per_class[label]['f1'] or 0 for label in expected_classes]
    return dict(accuracy=_ratio(sum(1 for expected, predicted in pairs if expected == predicted), len(pairs)),
                per_class=per_class, macro_classes=expected_classes, macro_f1=_ratio(sum(scores), len(scores)),
                confusion=confusion)


def answer_metrics(rows, partial_counts):
    """Accuracy over all questions; precision over answers given; recall over questions that expect an answer."""
    def correct(row):
        return row['mark'] == 'correct' or (partial_counts and row['mark'] == 'partial')
    right_answers = sum(1 for row in rows if row['expected'] == 'answer' and row['given'] and correct(row))
    precision = _ratio(right_answers, sum(1 for row in rows if row['given']))
    recall = _ratio(right_answers, sum(1 for row in rows if row['expected'] == 'answer'))
    return dict(accuracy=_ratio(sum(1 for row in rows if correct(row)), len(rows)), precision=precision, recall=recall,
                f1=_f1(precision, recall), n=len(rows))


@dataclass(frozen=True)
class SelectedRuns:
    scored: dict
    reruns: list
    unmatched: list
    failed: list


def select_runs(records):
    """The first completed run per case counts, so a poor result cannot be rerun away. One commit and release only."""
    runs = [record for record in records if record.get('record_type', 'run') == 'run']
    completed = [run for run in runs if run['outcome'] == 'completed']
    if len({(run['code_commit'], run['release_id']) for run in completed}) > 1:
        raise ValueError('mixed_runs')
    scored, reruns = {}, []
    for run in completed:
        if run['case_id'] is None:
            continue
        if run['case_id'] in scored:
            reruns.append(run)
        else:
            scored[run['case_id']] = run
    return SelectedRuns(scored, reruns, [run for run in completed if run['case_id'] is None],
                        [run for run in runs if run['outcome'] != 'completed'])


def _returned(run, list_name):
    searches = [search[list_name] for search in run['searches'] if search[list_name]]
    return [row['chunk_id'] for rows in searches for row in rows], len(searches)


def _mean(rows, field):
    return _ratio(sum(row[field] for row in rows if row[field] is not None),
                  sum(1 for row in rows if row[field] is not None))


def _summary(rows):
    fields = ('precision_at_3', 'precision_returned', 'recall_at_3', 'f1_at_3', 'hit_at_3')
    return dict(n=len(rows), **{field: _mean(rows, field) for field in fields})


def _grouped(rows, field):
    return {value: _summary([row for row in rows if row[field] == value]) for value in sorted({r[field] for r in rows})}


def build_report(records, keys_document, roster=None):
    roster = {row['case_id']: row for row in (roster or load_roster())}
    selected = select_runs(records)
    keys = {case_id: key for key in keys_document['keys'] for case_id in key['case_ids']}
    judgments = {record['run_id']: record for record in records if record.get('record_type') == 'judgment'}
    pools = {}
    for case_id, run in selected.scored.items():
        key = keys.get(case_id)
        if key is not None:
            marks = judgments.get(run['run_id'], {}).get('chunk_marks', {})
            pools.setdefault(key['key_id'], set()).update(chunk for chunk, marked in marks.items() if marked)
    measured = {name: [] for name, _ in LISTS}
    pairs, answers, unjudged, disagreements, pooled = [], [], [], [], []
    for case_id, run in sorted(selected.scored.items()):
        key = keys.get(case_id)
        if key is None:
            continue
        pairs.append((key['expected_route'], run.get('route_label') or 'none'))
        judgment = judgments.get(run['run_id'])
        if judgment is None or judgment.get('answer_mark') is None:
            unjudged.append(case_id)
        else:
            answers.append(dict(expected=key['expected_outcome'], given=run['answer']['status'] == 'answered',
                                mark=judgment['answer_mark']))
        keyed = key['key_status'] == 'keyed'
        relevant = set(key['relevant_chunk_ids']) if keyed else pools.get(key['key_id'], set())
        if keyed and judgment is not None:
            for chunk, marked in sorted(judgment.get('chunk_marks', {}).items()):
                if marked != (chunk in relevant):
                    disagreements.append(dict(case_id=case_id, chunk_id=chunk, key=chunk in relevant, owner=marked))
        if key['expected_route'] not in RETRIEVAL_ROUTES:
            continue
        if not keyed:
            pooled.append(case_id)
        case = roster[case_id]
        for name, _ in LISTS:
            returned, searches = _returned(run, name)
            measured[name].append(dict(retrieval_case_metrics(returned, relevant, searches), case_id=case_id,
                                       language=case['language'], category=case['category']))
    return dict(schema_version='bintanong-system-metrics-v1',
                code_commit=next((run['code_commit'] for run in selected.scored.values()), None),
                release_id=next((run['release_id'] for run in selected.scored.values()), None),
                scored_cases=len(selected.scored), route=route_metrics(pairs),
                retrieval={name: dict(overall=_summary(rows), by_language=_grouped(rows, 'language'),
                                      by_category=_grouped(rows, 'category'), cases=rows)
                           for name, rows in measured.items()},
                answer=dict(strict=answer_metrics(answers, partial_counts=False),
                            lenient=answer_metrics(answers, partial_counts=True)),
                unjudged_answers=unjudged, key_disagreements=disagreements, pooled_recall_cases=pooled,
                reruns=[run['run_id'] for run in selected.reruns], failed_runs=[run['run_id'] for run in selected.failed],
                unmatched_runs=[run['run_id'] for run in selected.unmatched],
                cases_without_key=sorted(set(selected.scored) - set(keys)),
                missing_cases=sorted(set(roster) - set(selected.scored)), disclosures=list(DISCLOSURES))


def _number(value):
    if value is None:
        return 'n/a'
    return f'{value:.3f}'


def render_markdown(report):
    lines = ['# Benchmark metrics', '', f"Commit `{report['code_commit']}`, release `{report['release_id']}`, "
             f"{report['scored_cases']} of 72 cases scored.", '', '## Routing', '',
             f"Accuracy {_number(report['route']['accuracy'])}; macro-F1 {_number(report['route']['macro_f1'])}.", '',
             '| Route | Precision | Recall | F1 | Expected queries |', '| --- | ---: | ---: | ---: | ---: |']
    lines += [f"| {label} | {_number(row['precision'])} | {_number(row['recall'])} | {_number(row['f1'])} | {row['support']} |"
              for label, row in report['route']['per_class'].items()]
    lines += ['', '## Retrieval (rows expected to use documents)', '',
              '| List | Group | n | Precision@3 | Precision of returned | Recall@3 | F1@3 | Hit@3 |',
              '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for name, label in LISTS:
        section = report['retrieval'][name]
        groups = [('Overall', section['overall'])] + list(section['by_language'].items()) + list(section['by_category'].items())
        lines += [f"| {label} | {group} | {row['n']} | {_number(row['precision_at_3'])} | {_number(row['precision_returned'])} "
                  f"| {_number(row['recall_at_3'])} | {_number(row['f1_at_3'])} | {_number(row['hit_at_3'])} |"
                  for group, row in groups]
    lines += ['', '## Final answers', '', '| Counting | n | Accuracy | Precision | Recall | F1 |',
              '| --- | ---: | ---: | ---: | ---: | ---: |']
    for name, label in (('strict', 'Strict (partial is wrong)'), ('lenient', 'Lenient (partial is correct)')):
        row = report['answer'][name]
        lines.append(f"| {label} | {row['n']} | {_number(row['accuracy'])} | {_number(row['precision'])} "
                     f"| {_number(row['recall'])} | {_number(row['f1'])} |")
    lines += ['', '## Left out or needing review', '']
    for field, label in (('missing_cases', 'Cases with no completed run'), ('unjudged_answers', 'Answers not judged'),
                         ('cases_without_key', 'Cases with no key'), ('reruns', 'Later runs not counted'),
                         ('failed_runs', 'Infrastructure failures'), ('unmatched_runs', 'Typed text outside the 72'),
                         ('pooled_recall_cases', 'Cases using pooled recall')):
        lines.append(f"- {label}: {', '.join(report[field]) or 'none'}")
    lines.append(f"- Key disagreements: {len(report['key_disagreements'])}")
    lines += ['', '## Disclosures', ''] + [f'- {line}' for line in report['disclosures']]
    return '\n'.join(lines) + '\n'


def read_records(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def main(argv=None):
    parser = argparse.ArgumentParser(description='Score saved benchmark runs against answer keys')
    parser.add_argument('--runs', type=Path, required=True)
    parser.add_argument('--keys', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    report = build_report(read_records(args.runs), json.loads(args.keys.read_text(encoding='utf-8')))
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    (args.out / 'report.md').write_text(render_markdown(report), encoding='utf-8')


if __name__ == '__main__':
    main()
