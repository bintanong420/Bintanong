"""Assemble complete source clauses under the exact serialized context budget."""
import json
from ..bintanong_contracts.reviewed_policy_context import CONTEXT_CHUNKER_VERSION, render_reviewed_policy_context


def _citation(span, chunk, version):
    locator = span.get('locator') or {}
    has_locator = any(locator.get(key) for key in ('cell_ids','item_ids','section_path','ref'))
    if (not has_locator or not locator.get('kind') or type(span.get('page')) is not int
        or span['page'] < 1 or not chunk.get('document_id') or not chunk.get('edition_id')
        or not version.get('filename') or span.get('version_id') != chunk.get('version_id')
        or version.get('version_id') != chunk.get('version_id')
        or span.get('byte_sha256') != chunk.get('byte_sha256')
        or version.get('byte_sha256') != chunk.get('byte_sha256')):
        raise ValueError('unresolvable citation')
    return {key:span.get(key) for key in ('span_id','byte_sha256','version_id','page','printed_page_label','locator')} | {
        'document_id':chunk['document_id'], 'edition_id':chunk['edition_id'], 'filename':version['filename'],
        'acquisition_locators':version.get('acquisition_locators',[]),
    }


def _span_key(span):
    # Span UUIDs differ when overlapping chunks carry the same source location.
    return json.dumps({key:span.get(key) for key in (
        'byte_sha256','version_id','page','locator','bbox','text'
    )},sort_keys=True)


def _serialize(items):
    blocks=[]
    for item in items:
        cites='; '.join(f"{c['version_id']}#{c['byte_sha256']}#p{c['page']}:"+
                        json.dumps(c['locator'],sort_keys=True,ensure_ascii=False) for c in item['citations'])
        blocks.append(f"[{item['chunk_id']} | {cites}]\n{item['text']}")
    return '\n\n'.join(blocks)


def build_context(candidates, budget: int, count_tokens):
    accepted, seen_chunks, seen_spans, gaps = [], set(), set(), []
    for candidate in candidates:
        main_id = candidate['chunk']['chunk_id']
        if main_id in seen_chunks:
            continue
        available={row['chunk']['chunk_id']:row for row in [candidate]+candidate.get('neighbors',[])}
        group=[candidate]
        required=candidate['chunk'].get('type_fields',{}).get('required_neighbor_chunk_ids',[])
        if not isinstance(required,list) or any(not isinstance(x,str) for x in required):
            gaps.append(f'missing_required_neighbor:{main_id}')
            continue
        missing=False
        for row in group:
            dependencies=row['chunk'].get('type_fields',{}).get('required_neighbor_chunk_ids',[])
            if not isinstance(dependencies,list) or any(not isinstance(x,str) for x in dependencies):
                missing=True
                break
            for dependency in dependencies:
                if dependency not in available:
                    missing=True
                elif available[dependency] not in group:
                    group.append(available[dependency])
        if missing:
            gaps.append(f'missing_required_neighbor:{main_id}')
            continue
        trial, trial_chunks, trial_spans=[],set(seen_chunks),set(seen_spans)
        try:
            grouped={}
            for row in group:
                meta=row['chunk'].get('type_fields',{}).get('service_group')
                if meta is not None:
                    grouped.setdefault(meta['logical_step_id'],[]).append(row)
            for members in grouped.values():
                metas=[r['chunk']['type_fields']['service_group'] for r in members]
                count=metas[0]['part_count']
                if (type(count) is not int or any(type(m['part_order']) is not int or m['part_count']!=count for m in metas)
                        or sorted(m['part_order'] for m in metas)!=list(range(count))
                        or len({r['chunk']['version_id'] for r in members})!=1):
                    raise ValueError('invalid reviewed context record')
                ordered=iter(sorted(members,key=lambda r:r['chunk']['type_fields']['service_group']['part_order']))
                member_ids={r['chunk']['chunk_id'] for r in members}
                group=[next(ordered) if r['chunk']['chunk_id'] in member_ids else r for r in group]
            for row in group:
                chunk=row['chunk']
                if chunk['chunk_id'] in trial_chunks:
                    continue
                spans=row.get('spans',[])
                if not spans:
                    raise ValueError('missing source spans')
                # Validate all spans, even those already represented by another chunk.
                citations=[_citation(s,chunk,row['version']) for s in spans]
                fresh=[(s,c) for s,c in zip(spans,citations) if _span_key(s) not in trial_spans]
                trial_chunks.add(chunk['chunk_id'])
                marked = (chunk.get('chunker_version') == CONTEXT_CHUNKER_VERSION
                    or 'context_format' in chunk.get('type_fields',{})
                    or 'source_limits' in chunk.get('type_fields',{}))
                if marked:
                    text = render_reviewed_policy_context(chunk,spans)
                    fresh = list(zip(spans,citations))
                if not fresh:
                    continue
                if not marked:
                    text='\n'.join(s['text'] for s,c in fresh if s.get('text'))
                if not text:
                    if len(fresh)!=len(spans):
                        # Empty table spans have no row-to-cell text mapping. A
                        # full table fallback cannot be attributed to fresh cells.
                        raise ValueError('partial_table_overlap')
                    text=chunk['source_text'] or chunk['text']
                if not text.strip():
                    raise ValueError('empty evidence')
                trial.append(dict(chunk_id=chunk['chunk_id'], document_id=chunk['document_id'],
                    version_id=chunk['version_id'],edition_id=chunk['edition_id'],
                    similarity=row['similarity'],text=text,scope=chunk.get('scope',[]),
                    section_path=chunk.get('section_path',[]),citations=[c for s,c in fresh],
                    selection='primary' if row is candidate else 'required_neighbor'))
                trial_spans.update(_span_key(s) for s,c in fresh)
        except (KeyError,ValueError,TypeError) as exc:
            reason=('partial_table_overlap' if str(exc)=='partial_table_overlap' else
                    'invalid_reviewed_context' if str(exc)=='invalid reviewed context record' else 'invalid_citation')
            gaps.append(f'{reason}:{main_id}')
            continue
        context=_serialize(accepted+trial)
        tokens=count_tokens(context) if context else 0
        if type(tokens) is not int or tokens<0:
            raise ValueError('context tokenizer must return an exact nonnegative integer')
        if tokens>budget:
            gaps.append(f'context_budget:{main_id}')
            continue
        accepted.extend(trial)
        seen_chunks,seen_spans=trial_chunks,trial_spans
    context=_serialize(accepted)
    return dict(evidence=accepted, context=context,
                context_tokens=count_tokens(context) if context else 0, gaps=gaps)
