"""Exact offering clauses need their pinned, reviewed source fields before display."""
import json
import hashlib


def source_digest(record):
    return hashlib.sha256(json.dumps(record.model_dump(mode='json'),sort_keys=True,
        separators=(',', ':'),ensure_ascii=False,allow_nan=False).encode('utf-8')).hexdigest()


def check_route_sources(pin, routes, documents):
    if routes is None:
        if documents is not None:
            raise ValueError('plan_sources_without_routes')
        return
    if (documents is None or documents.release_id != pin.release_id or documents.status != 'ok'
            or documents.gaps):
        raise ValueError('plan_routes_need_pinned_sources')
    if pin.plan_routes_sha256 != source_digest(routes):
        raise ValueError('plan_routes_reviewed_config_mismatch')
    members = {m.chunk_id:m for m in pin.documents}
    passages = {p.chunk_id:p for p in documents.passages}
    if not set(routes.source_chunk_ids) <= set(passages):
        raise ValueError('plan_routes_missing_source_chunk')
    fields = []
    for passage in documents.passages:
        member = members.get(passage.chunk_id)
        if (member is None or member.passage_sha256 != source_digest(passage)
                or any((member.version_id, member.byte_sha256) != (c.version_id, c.byte_sha256)
                       for c in passage.citations)):
            raise ValueError('plan_routes_source_outside_release')
        record = json.loads(passage.text)
        if (not isinstance(record, dict) or not isinstance(record.get('fields'), list)
                or any(not isinstance(limit, dict) or limit.get('resolution') == 'unresolved'
                       for limit in record.get('source_limits', []))):
            raise ValueError('plan_routes_source_unreviewed')
        for field in record['fields']:
            if not isinstance(field, dict) or field.get('source_blank') is not False:
                continue
            indexes = field.get('span_indexes')
            if (not isinstance(field.get('value'), str) or not isinstance(indexes, list) or not indexes
                    or any(type(i) is not int or not 0 <= i < len(passage.citations) for i in indexes)):
                raise ValueError('plan_route_field_needs_source_spans')
            fields.extend((passage.chunk_id, passage.citations[i].page, field['value']) for i in indexes)
    for clause in routes.clauses:
        if not any(cid in routes.source_chunk_ids and page == clause.page and clause.text in value
                   for cid,page,value in fields):
            raise ValueError('plan_route_clause_not_in_source_field')
