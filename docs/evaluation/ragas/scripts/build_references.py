"""Reference answers for Q1-Q14 (benchmark rows 11-24), shared by RAGAS and BERTScore.

Reference for query N = verbatim text of every chunk judged relevant (TP or FN) for N in any of its
three language variants of the 7 Nov final-metrics judgments (owner-agreed, 7 Nov 2026).
Chunk texts come from the saved run logs (topic_bound and all_chunks lists); nothing is retyped.
Usage: python build_references.py <final-metrics dir> <out dir>
"""
import collections
import csv
import json
import pathlib
import sys

METRICS, OUT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
LANG = {'English': 'en', 'Tagalog': 'tl-tagalog', 'Taglish': 'tl-taglish'}

judgments = json.loads((METRICS / 'judgments.json').read_text(encoding='utf-8'))
records = []
for name in ('results.jsonl', 'results-q11.jsonl'):
    records += [json.loads(x) for x in (METRICS / name).read_text(encoding='utf-8').splitlines() if x.strip()]

chunks = {}
for record in records:
    for search in record.get('searches') or []:
        for chunk in (search.get('topic_bound') or []) + (search.get('all_chunks') or []):
            prior = chunks.setdefault(chunk['chunk_id'], chunk)
            assert prior['text'] == chunk['text'], chunk['chunk_id']


def full_id(prefix):
    matches = [cid for cid in chunks if cid.startswith(prefix)]
    assert len(matches) == 1, (prefix, matches)
    return matches[0]


relevant, irrelevant = collections.defaultdict(set), collections.defaultdict(set)
for label, judged in judgments.items():
    if label == 'rule':
        continue
    query_no = int(label.rsplit(' ', 1)[1])
    relevant[query_no] |= {full_id(p) for p in judged['tp'] + judged['fn']}
    irrelevant[query_no] |= {full_id(p) for p in judged['fp']}

questions = collections.defaultdict(dict)
for record in records:
    language, number = record['label'].rsplit(' ', 1)
    questions[int(number)][language] = record['question']

conflicts = {q: sorted(relevant[q] & irrelevant[q]) for q in relevant if relevant[q] & irrelevant[q]}


def order(cid):
    c = chunks[cid]
    return (c['source_label'], min(c['pages'] or [0]), cid)


references = []
for query_no in sorted(relevant):
    ids = sorted(relevant[query_no], key=order)
    references.append({
        'query_no': query_no,
        'benchmark_row': f'row-{query_no + 10:02d}',
        'questions': questions[query_no],
        'reference_answer': '\n\n'.join(chunks[cid]['text'].strip() for cid in ids),
        'reference_chunks': [{'chunk_id': cid, 'source': chunks[cid]['source_label'], 'pages': chunks[cid]['pages'],
                              'section_path': chunks[cid].get('section_path'), 'text': chunks[cid]['text']}
                             for cid in ids],
        'judged_both_ways': [cid[:8] for cid in conflicts.get(query_no, [])],
    })
assert len(references) == 14, len(references)

OUT.mkdir(parents=True, exist_ok=True)
with (OUT / 'reference_answers.jsonl').open('w', encoding='utf-8', newline='\n') as f:
    for ref in references:
        f.write(json.dumps(ref, ensure_ascii=False) + '\n')
with (OUT / 'reference_answers.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['query_no', 'benchmark_row', 'question_en', 'reference_chunk_ids', 'sources_pages', 'reference_answer'])
    for ref in references:
        w.writerow([ref['query_no'], ref['benchmark_row'], ref['questions'].get('English', ''),
                    '; '.join(c['chunk_id'][:8] for c in ref['reference_chunks']),
                    '; '.join(f"{c['source']} p.{','.join(map(str, c['pages'] or []))}" for c in ref['reference_chunks']),
                    ref['reference_answer']])
for ref in references:
    print(ref['query_no'], len(ref['reference_chunks']), 'chunks', len(ref['reference_answer']), 'chars',
          'CONFLICT ' + ','.join(ref['judged_both_ways']) if ref['judged_both_ways'] else '')
