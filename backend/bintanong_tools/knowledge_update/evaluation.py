from __future__ import annotations

import csv
import math
from pathlib import Path
import re

from ..document_ingest.inspection import check_out
from ..prospectus_review_gui.render import PageRenderer
from .files import digest, read_json, write_json

STRATEGIES = ('native', 'native_vision', 'llamaparse')
METRICS = ('human_corrections', 'review_minutes', 'unresolved', 'omissions', 'hierarchy_errors',
    'table_errors', 'reading_order_errors', 'wrong_numbers', 'source_mismatches', 'correct_suggestions',
    'false_positives', 'bad_suggestions', 'hallucinated_suggestions', 'uncertain', 'ignored',
    'provider_calls', 'parser_calls', 'latency_seconds', 'retries', 'failures', 'observed_cost', 'estimated_cost')


def differences(expected, actual, prefix=''):
    if type(expected) is not type(actual):
        return [prefix or 'value']
    if isinstance(expected, dict):
        return [path for key in sorted(set(expected) | set(actual))
                for path in ([(prefix + '.' + key).lstrip('.')] if key not in expected or key not in actual
                    else differences(expected[key], actual[key], (prefix + '.' + key).lstrip('.')))]
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return [prefix or 'value']
        return [path for i, (left, right) in enumerate(zip(expected, actual))
                for path in differences(left, right, (prefix + '.' + str(i)).lstrip('.'))]
    return [] if expected == actual else [prefix or 'value']


def create_sample(sample_path: Path, out: Path):
    sample = read_json(Path(sample_path))
    rows, seen = [], set()
    for doc in sample['documents']:
        source = Path(doc['source'])
        if digest(source.read_bytes()) != doc['sha256']:
            raise ValueError('evaluation source identity mismatch')
        with PageRenderer(source) as renderer:
            for selected in doc['pages']:
                page = selected['page']
                if type(page) is not int or not 1 <= page <= renderer.page_count or not selected['reason'].strip():
                    raise ValueError('evaluation needs physical pages and sampling rationale')
                key = (doc['sha256'], page)
                if key in seen:
                    raise ValueError('duplicate sample page')
                seen.add(key)
                for strategy in STRATEGIES:
                    rows.append({'strategy': strategy, 'source_sha256': doc['sha256'], 'page': page,
                        'sampling_reason': selected['reason'], **{name: '' for name in METRICS}})
    if not rows:
        raise ValueError('empty evaluation sample')
    out = Path(out)
    check_out(Path(sample_path).parent, out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'measurements.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    write_json(out / 'sample.json', sample)
    return {'pages': len(seen), 'measurement_rows': len(rows), 'status': 'NOT MEASURED'}


def summarize(path: Path, out: Path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError('empty measurements')
    keys = {s: set() for s in STRATEGIES}
    groups = {s: [] for s in STRATEGIES}
    for row in rows:
        strategy = row.get('strategy')
        if strategy not in groups or not re.fullmatch('[a-f0-9]{64}', row.get('source_sha256', '')):
            raise ValueError('unknown strategy or source digest')
        try:
            page = int(row['page'])
        except (ValueError, TypeError, KeyError):
            raise ValueError('invalid measurement page') from None
        key = (row['source_sha256'], page)
        if page < 1 or key in keys[strategy]:
            raise ValueError('invalid or duplicate measurement page')
        keys[strategy].add(key)
        values = {}
        for name in METRICS:
            raw = row.get(name, '')
            value = float(raw) if raw != '' else None
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError('measurements must be finite, nonnegative or blank')
            values[name] = value
        groups[strategy].append(values)
    if not keys['native'] or any(keys[s] != keys['native'] for s in STRATEGIES):
        raise ValueError('strategies require matched source pages')
    summary = {}
    for strategy, records in groups.items():
        totals = {name: sum(r[name] for r in records) if all(r[name] is not None for r in records) else None
                  for name in METRICS}
        for name in ('human_corrections', 'review_minutes'):
            totals[name + '_per_page'] = None if totals[name] is None else totals[name] / len(records)
            totals[name + '_per_100_pages'] = None if totals[name] is None else totals[name] * 100 / len(records)
        summary[strategy] = {'pages': len(records), **totals}
    report = {'candidate_only': True, 'strategies': summary,
              'limitation': 'Blank metrics are not measured. Confidence is not accuracy. Human review/timing required.'}
    out = Path(out)
    check_out(Path(path).parent, out)
    write_json(out / 'summary.json', report)
    columns = ['strategy', 'pages', 'human_corrections', 'table_errors', 'review_minutes', 'provider_calls', 'failures']
    with (out / 'summary.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows({k: strategy if k == 'strategy' else values[k] for k in columns}
                         for strategy, values in summary.items())
    text = '| ' + ' | '.join(columns) + ' |\n|' + '|'.join(['---'] * len(columns)) + '|\n'
    for strategy, values in summary.items():
        text += '| ' + ' | '.join(str(strategy if k == 'strategy' else values[k])
                                 if k == 'strategy' or values[k] is not None else 'NOT MEASURED' for k in columns) + ' |\n'
    (out / 'summary.md').write_text(text + '\n' + report['limitation'] + '\n', encoding='utf-8')
    return report
