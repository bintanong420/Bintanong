"""Merge RAGAS outputs into docs/evaluation/ragas/ragas_scores.csv and ragas_summary.json. Usage: python merge_results.py <run dir> <docs dir>"""
import csv, json, pathlib, sys
run, docs = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
load = lambda p: [json.loads(x) for x in (run / p).read_text(encoding='utf-8').splitlines() if x.strip()]
base = load('ragas_scores.jsonl')
fielded = {r['id']: r for r in load('faithfulness_writer_fielded_text.jsonl')}
plain = {r['id']: r for r in load('faithfulness_writer_text.jsonl')}
METRICS = {'faithfulness': 'Faithfulness (writer evidence, reviewed fields) - headline',
           'faithfulness_writer_plain_text': 'Faithfulness (writer evidence, plain chunk text)',
           'faithfulness_top3_only': 'Faithfulness (top-3 chunks only)',
           'answer_relevancy': 'Answer relevancy', 'context_precision': 'Context precision (with reference, top-3)',
           'context_recall': 'Context recall (top-3)', 'factual_correctness_precision': 'Factual correctness (precision mode)'}
rows = []
for b in base:
    rows.append({'id': b['id'], 'query_no': b['query_no'], 'benchmark_row': f"row-{b['query_no'] + 10:02d}",
                 'language': b['language'], 'writer_chunks': fielded[b['id']]['contexts'],
                 'faithfulness': fielded[b['id']]['faithfulness'],
                 'faithfulness_writer_plain_text': plain[b['id']]['faithfulness'],
                 'faithfulness_top3_only': b['faithfulness'], 'answer_relevancy': b['answer_relevancy'],
                 'context_precision': b['llm_context_precision_with_reference'], 'context_recall': b['context_recall'],
                 'factual_correctness_precision': b['factual_correctness(mode=precision)']})
assert len(rows) == 42 and all(r[m] is not None for r in rows for m in METRICS)
with (docs / 'ragas_scores.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, list(rows[0])); w.writeheader()
    for r in rows:
        w.writerow({k: round(v, 4) if isinstance(v, float) else v for k, v in r.items()})
mean = lambda xs: round(sum(xs) / len(xs), 3)
groups = {'Overall': rows, **{g: [r for r in rows if r['language'] == g] for g in ('English', 'Tagalog', 'Taglish')}}
zero = [r['id'] for r in rows if r['answer_relevancy'] == 0]
summary = {'metrics': METRICS, 'n_rows': len(rows),
           'by_language': {g: {m: mean([r[m] for r in rs]) for m in METRICS} for g, rs in groups.items()},
           'answer_relevancy_zero_rows': zero,
           'answer_relevancy_excluding_zero_rows': {g: mean([r['answer_relevancy'] for r in rs if r['answer_relevancy'] > 0])
                                                    for g, rs in groups.items()},
           'excluding_q11': {m: mean([r[m] for r in rows if r['query_no'] != 11]) for m in METRICS},
           'by_query': {q: {m: mean([r[m] for r in rows if r['query_no'] == q]) for m in METRICS} for q in range(1, 15)}}
(docs / 'ragas_summary.json').write_text(json.dumps(summary, indent=1), encoding='utf-8')
print(json.dumps({k: summary[k] for k in ('by_language', 'answer_relevancy_excluding_zero_rows', 'excluding_q11')}, indent=1))
for q, v in summary['by_query'].items():
    print(q, {k[:12]: x for k, x in v.items()})
