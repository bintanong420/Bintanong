"""Assemble complete source clauses under the exact serialized context budget."""
import json
from ..bintanong_contracts.reviewed_policy_context import CONTEXT_CHUNKER_VERSIONS, render_reviewed_policy_context
from ..bintanong_contracts.reviewed_record_groups import validate_record_group
from .group_display import prepare_group_display


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


def _serialize_shared_citations(items, shared_group_metadata=False, reviewed_group_chunk_ids=()):
    if not items:
        return ''
    encode=lambda value:json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'))
    sources, source_indexes = [], {}
    for item in items:
        for citation in item['citations']:
            key=tuple(citation[k] for k in ('version_id','byte_sha256','page'))
            locator=citation['locator']
            if key not in source_indexes:
                source_indexes[key]=len(sources)
                sources.append(dict(version_id=key[0],byte_sha256=key[1],page=key[2],
                                    locator_defaults=dict(locator)))
            else:
                defaults=sources[source_indexes[key]]['locator_defaults']
                for field in list(defaults):
                    if field not in locator or encode(defaults[field])!=encode(locator[field]):
                        del defaults[field]
    metadata=dict(citation_format='shared-source-locators-v1',citation_sources=sources)
    texts={}
    if shared_group_metadata:
        groups,texts=prepare_group_display(items,reviewed_group_chunk_ids)
        if groups:
            metadata.update(citation_format='shared-source-groups-v1',policy_groups=groups)
    blocks=[encode(metadata)]
    for item in items:
        groups=[]
        for citation in item['citations']:
            key=tuple(citation[k] for k in ('version_id','byte_sha256','page'))
            index=source_indexes[key]
            defaults=sources[index]['locator_defaults']
            residual={k:v for k,v in citation['locator'].items() if k not in defaults}
            # Only combine adjacent citations so their original order survives.
            if not groups or groups[-1]['source_index']!=index:
                groups.append(dict(source_index=index,locators=[]))
            groups[-1]['locators'].append(residual)
        blocks.append(f"[{item['chunk_id']} | {encode(groups)}]\n{texts.get(item['chunk_id'],item['text'])}")
    return blocks[0]+'\n'+'\n\n'.join(blocks[1:])


def _serialize(items, compact_citations=False, shared_citations=False,
               shared_group_metadata=False, reviewed_group_chunk_ids=()):
    if shared_citations:
        return _serialize_shared_citations(items,shared_group_metadata,reviewed_group_chunk_ids)
    blocks=[]
    for item in items:
        if compact_citations:
            grouped={}
            for citation in item['citations']:
                key=(citation['version_id'],citation['byte_sha256'],citation['page'])
                group=grouped.setdefault(key,dict(version_id=key[0],byte_sha256=key[1],
                                                page=key[2],locators=[]))
                group['locators'].append(citation['locator'])
            cites=json.dumps(list(grouped.values()),sort_keys=True,ensure_ascii=False,separators=(',',':'))
        else:
            cites='; '.join(f"{c['version_id']}#{c['byte_sha256']}#p{c['page']}:"+
                            json.dumps(c['locator'],sort_keys=True,ensure_ascii=False) for c in item['citations'])
        blocks.append(f"[{item['chunk_id']} | {cites}]\n{item['text']}")
    return '\n\n'.join(blocks)


def build_context(candidates, budget: int, count_tokens, *, compact_citations=False, shared_citations=False,
                  shared_group_metadata=False):
    if type(compact_citations) is not bool:
        raise ValueError('compact_citations must be an explicit boolean')
    if type(shared_citations) is not bool:
        raise ValueError('shared_citations must be an explicit boolean')
    if type(shared_group_metadata) is not bool:
        raise ValueError('shared_group_metadata must be an explicit boolean')
    if shared_group_metadata and not shared_citations:
        raise ValueError('shared_group_metadata requires shared_citations')
    accepted, seen_chunks, seen_spans, gaps = [], set(), set(), []
    reviewed_group_chunk_ids=set()
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
        trial_group_chunk_ids=set(reviewed_group_chunk_ids)
        try:
            grouped={}
            for row in group:
                meta=row['chunk'].get('type_fields',{}).get('service_group')
                if meta is not None:
                    grouped.setdefault(meta['logical_step_id'],[]).append(row)
            for members in grouped.values():
                metas=[r['chunk']['type_fields']['service_group'] for r in members]
                count=metas[0]['part_count']
                if (type(count) is not int or count!=len(members)
                        or any(type(m['part_order']) is not int or m['part_count']!=count for m in metas)
                        or sorted(m['part_order'] for m in metas)!=list(range(count))
                        or len({r['chunk']['version_id'] for r in members})!=1):
                    raise ValueError('invalid reviewed context record')
                if any('record_manifest' in meta for meta in metas):validate_record_group(members)
                for row in members:
                    for field in row['chunk'].get('type_fields',{}).get('field_associations',[]):
                        if not isinstance(field,dict):
                            raise ValueError('invalid reviewed context record')
                        if field.get('field_kind')=='arrows':
                            mapping=field.get('node_reading_ids')
                            if not isinstance(mapping,dict) or any(not isinstance(v,str) for v in mapping.values()):
                                raise ValueError('invalid reviewed context record')
                            node_ids=list(mapping.values())
                            other_ids=[r['chunk']['type_fields']['reading_id'] for r in members if r is not row]
                            if (row['chunk']['type_fields']['service_group']['part_order']!=0
                                    or len(set(other_ids))!=len(other_ids)
                                    or len(node_ids)!=len(other_ids) or set(node_ids)!=set(other_ids)
                                    or any(r['chunk']['type_fields']['service_group'].get('part_reading_id')
                                        !=r['chunk']['type_fields'].get('reading_id') for r in members)):
                                raise ValueError('invalid reviewed context record')
                            arrow_pages={s['page'] for s in row['spans']}
                            if (len(arrow_pages)!=1 or any(
                                    {s['page'] for s in r['spans']}!=arrow_pages for r in members)):
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
                marked = (chunk.get('chunker_version') in CONTEXT_CHUNKER_VERSIONS
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
                if marked and chunk.get('type_fields',{}).get('service_group') is not None:
                    trial_group_chunk_ids.add(chunk['chunk_id'])
                trial_spans.update(_span_key(s) for s,c in fresh)
        except (KeyError,ValueError,TypeError) as exc:
            reason=('partial_table_overlap' if str(exc)=='partial_table_overlap' else
                    'invalid_reviewed_context' if str(exc)=='invalid reviewed context record' else 'invalid_citation')
            gaps.append(f'{reason}:{main_id}')
            continue
        context=_serialize(accepted+trial,compact_citations,shared_citations,
                           shared_group_metadata,trial_group_chunk_ids)
        tokens=count_tokens(context) if context else 0
        if type(tokens) is not int or tokens<0:
            raise ValueError('context tokenizer must return an exact nonnegative integer')
        if tokens>budget:
            gaps.append(f'context_budget:{main_id}')
            continue
        accepted.extend(trial)
        seen_chunks,seen_spans=trial_chunks,trial_spans
        reviewed_group_chunk_ids=trial_group_chunk_ids
    context=_serialize(accepted,compact_citations,shared_citations,
                       shared_group_metadata,reviewed_group_chunk_ids)
    return dict(evidence=accepted, context=context,
                context_tokens=count_tokens(context) if context else 0, gaps=gaps)
