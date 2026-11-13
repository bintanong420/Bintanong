"""Diagnostic: rebuild each query's reference as its judged-relevant chunks PLUS their required-neighbour closure
(same rule as writer_context.py), in two renderings: plain source text and reviewed fields.
Usage (worktree root on sys.path): python expanded_reference.py <worktree> <dev config> <bertscore_pairs.jsonl> <out.json>"""
import json, os, pathlib, sys
sys.path.insert(0, sys.argv[1])
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('MODELS_DIR', 'C:/Coding-projects/bintanong_workspace/MODELS')
from backend.bintanong_api import research_app  # noqa: E402

worktree, config_path, pairs_path, out_path = sys.argv[1:5]
config = research_app.ResearchApiConfig.model_validate_json(pathlib.Path(config_path).read_text(encoding='utf-8'))
_, package = research_app._package(config)
chunks = {c['chunk_id']: c for c in package['chunks']}


def closure(cid):
    needed, pending = [cid], [cid]
    for current in pending:
        for n in chunks[current]['type_fields'].get('required_neighbor_chunk_ids', []):
            if n not in needed and n in chunks and chunks[n]['version_id'] == chunks[cid]['version_id']:
                needed.append(n); pending.append(n)
    return needed


def fielded(chunk):
    fields = chunk['type_fields'].get('field_associations') or []
    lines = [f"{f['name']}: {'(blank in the printed table)' if f.get('source_blank') else f['value']}" for f in fields]
    lines += [f"Recorded source limitation: {lim['message']}" for lim in chunk['type_fields'].get('source_limits') or []]
    return '\n'.join(lines) if fields else (chunk.get('source_text') or chunk['text'])


out = {}
for row in map(json.loads, open(pairs_path, encoding='utf-8')):
    if row['query_no'] in out:
        continue
    ordered = []
    for short in row['reference_chunk_ids']:
        matches = [c for c in chunks if c.startswith(short)]
        assert len(matches) == 1, (short, len(matches))
        for n in closure(matches[0]):
            if n not in ordered:
                ordered.append(n)
    out[row['query_no']] = {'reference_chunk_ids': row['reference_chunk_ids'], 'expanded_chunk_ids': ordered,
                            'plain': '\n\n'.join(chunks[c].get('source_text') or chunks[c]['text'] for c in ordered),
                            'fielded': '\n\n'.join(fielded(chunks[c]) for c in ordered)}
json.dump(out, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False)
print({q: (len(v['reference_chunk_ids']), len(v['expanded_chunk_ids'])) for q, v in sorted(out.items())})
