"""Rebuild the evidence each saved answer's writer received: top-3 retrieved chunks plus their
required-neighbour closure (same rule as backend/bintanong_runtime/package_storage.py), from the served package.
Check: closure size per retrieved chunk must equal the logged attached_count.
Usage (worktree root on sys.path): python writer_context.py <worktree> <dev config> <final-metrics dir> <out.json>
Outputs plain chunk text and `fielded_text` (reviewed field labels + recorded source limitations)."""
import json, os, pathlib, sys
sys.path.insert(0, sys.argv[1])
os.environ.setdefault('MODELS_DIR', 'C:/Coding-projects/bintanong_workspace/MODELS')
from backend.bintanong_api import research_app  # noqa: E402

config = research_app.ResearchApiConfig.model_validate_json(pathlib.Path(sys.argv[2]).read_text(encoding='utf-8'))
_, package = research_app._package(config)
chunks = {c['chunk_id']: c for c in package['chunks']}
metrics = pathlib.Path(sys.argv[3])


def closure(cid):
    needed, pending = {cid}, [cid]
    for current in pending:
        for n in chunks[current]['type_fields'].get('required_neighbor_chunk_ids', []):
            if n not in needed and n in chunks and chunks[n]['version_id'] == chunks[cid]['version_id']:
                needed.add(n); pending.append(n)
    return sorted(needed - {cid})


def fielded(chunk):
    """Reviewed fields as the writer receives them: labelled values plus recorded source limitations."""
    fields = chunk['type_fields'].get('field_associations') or []
    lines = [f"{f['name']}: {'(blank in the printed table)' if f.get('source_blank') else f['value']}" for f in fields]
    lines += [f"Recorded source limitation: {lim['message']}" for lim in chunk['type_fields'].get('source_limits') or []]
    return '\n'.join(lines) if fields else (chunk.get('source_text') or chunk['text'])


records = {}
for name in ('results.jsonl', 'results-q11.jsonl'):
    for line in (metrics / name).read_text(encoding='utf-8').splitlines():
        if line.strip():
            r = json.loads(line); records[r['label']] = r
mismatch, out = [], {}
for label, r in records.items():
    ordered = []
    for s in r.get('searches') or []:
        for c in s.get('topic_bound') or []:
            neighbours = closure(c['chunk_id'])
            if len(neighbours) != c['attached_count']:
                mismatch.append((label, c['chunk_id'][:8], len(neighbours), c['attached_count']))
            for cid in [c['chunk_id']] + neighbours:
                if cid not in ordered:
                    ordered.append(cid)
    out[label] = [{'chunk_id': cid, 'text': chunks[cid].get('source_text') or chunks[cid]['text'],
                   'fielded_text': fielded(chunks[cid])} for cid in ordered]
json.dump(out, open(sys.argv[4], 'w', encoding='utf-8'), ensure_ascii=False)
print(len(out), 'records; attached_count mismatches:', mismatch)
print({k: len(v) for k, v in sorted(out.items())})
