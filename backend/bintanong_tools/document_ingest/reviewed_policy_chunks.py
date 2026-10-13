"""Separate pending chunks from explicitly applicable, fully located scalar readings.

Original review artifacts remain a sidecar. Nothing here raises source governance,
repairs raw extraction, guesses geometry, or makes a bundle eligible for activation.
Readings with source gaps wait for an interface that carries their limits into
retrieval context; retaining them only in metadata would currently lose the limits.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from ...bintanong_contracts.source import (Chunk, SourceSpan, bind_chunk, canonical_text,
    check_span_binding, compute_content_hash, span_identity)
from ...bintanong_contracts.reviewed_policy_context import (CONTEXT_FORMAT, CONTEXT_CHUNKER_VERSION,
    make_source_limits, serialize_reviewed_fields)
from ..prospectus_extractor.chunking import estimate_tokens
from .policy_chunks import TOKEN_CAP
from .register import load_pending_register
from .reviewed_policy import build_reviewed_policy_bundle
from .reviewed_text_segments import reviewed_body_partition
from .reviewed_flowchart_context import validate_reviewed_flowchart_binding


CHUNKER_VERSION = "palsu-reviewed-policy-chunker-v1"


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _field_spans(field, supplied, version, row):
    spans = []
    for raw in supplied:
        data = raw.model_dump(mode="json") if isinstance(raw, SourceSpan) else raw
        if not isinstance(data, dict) or type(data.get("page")) is not int:
            raise ValueError("physical page must be explicit")
        span = SourceSpan.parse(data)
        check_span_binding(span, version)
        if (span.version_id != version.version_id or not span.is_complete
                or span.bbox is None or span.bbox_origin is None or span.page_size is None):
            raise ValueError("complete original geometry and source version required")
        spans.append(span)
    pages = field["locator"]["physical_pages"]
    if field["name"] == "body" and any(f["name"] == "segmentation" for f in row["fields"]):
        pages = reviewed_body_partition(row)["body_pages"]
    if (set(s.page for s in spans) != set(pages)
            or canonical_text(" ".join(s.text for s in spans)) != canonical_text(field["reviewed_value"])):
        raise ValueError("field text or physical pages differ from supplied spans")
    return spans


def build_reviewed_policy_chunks(
    bundle: dict[str, Any], *, sources: Mapping[str, bytes], review_events: Mapping[str, bytes],
    source_versions: Sequence[Any], field_spans: Mapping[str, Mapping[str, Sequence[Any]]] | None = None,
    required_readings: Mapping[str, Sequence[str]] | None = None, token_cap: int = TOKEN_CAP,
    include_source_limits: bool = False,
    flowchart_bindings: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Recheck preparation evidence and produce pending chunks or explicit withholding.

    Applicability declarations and field-to-source mapping are trusted caller
    inputs, not university approval. Synthetic tests exercise the eligible branch;
    actual unknown applicability is withheld. Exact model token counts and governed
    publication remain later gates. All inputs are read-only.
    """
    if type(token_cap) is not int or not 0 < token_cap <= TOKEN_CAP:
        raise ValueError("token cap must be an integer in 1..480")
    if type(include_source_limits) is not bool:
        raise ValueError("include_source_limits must be a boolean")
    if not isinstance(bundle, dict) or not isinstance(bundle.get("readings"), list):
        raise ValueError("invalid reviewed preparation")
    core = build_reviewed_policy_bundle(bundle["readings"], sources=sources, review_events=review_events)
    # Do not trust cached selection, event contents, counts, or inactive flags.
    if any(_json(bundle.get(key)) != _json(value) for key, value in core.items()):
        raise ValueError("reviewed preparation differs from original evidence or derived selection")
    versions = {v.version_id: v for v in load_pending_register(source_versions)}
    rows = {r["reading_id"]: r for r in core["readings"]}
    for row in rows.values():
        version = versions.get(row["version_id"])
        if version is None or version.byte_sha256 != row["source_sha256"]:
            raise ValueError("reading source/version absent or mismatched in pending register")
    anchors = {} if field_spans is None else field_spans
    dependencies = {} if required_readings is None else required_readings
    if not isinstance(anchors, Mapping) or any(identity not in rows for identity in anchors):
        raise ValueError("field span mapping has an unknown reading")
    for identity, values in anchors.items():
        names = {f["name"] for f in rows[identity]["fields"]}
        if not isinstance(values, Mapping) or any(name not in names for name in values):
            raise ValueError("field span mapping has an unknown field")
    if not isinstance(dependencies, Mapping) or any(identity not in rows for identity in dependencies):
        raise ValueError("required readings contain an unknown root")
    required = {}
    for identity in rows:
        refs = dependencies.get(identity, [])
        if (not isinstance(refs, (list, tuple)) or any(not isinstance(r, str) or r not in rows for r in refs)
                or len(set(refs)) != len(refs)):
            raise ValueError("required readings must name distinct known readings")
        required[identity] = [r for r in refs if r != identity]
    graphs={} if flowchart_bindings is None else flowchart_bindings
    if not isinstance(graphs,Mapping) or any(i not in rows for i in graphs):
        raise ValueError('flowchart binding has an unknown reading')
    node_mappings={}
    for identity,graph in graphs.items():
        if not isinstance(graph,dict) or graph.get('arrow_reading_id')!=identity:
            raise ValueError('flowchart binding identity differs')
        node_mappings[identity]=validate_reviewed_flowchart_binding(graph,rows,anchors)
        # Graph parts are mandatory even when the caller omits dependencies.
        for part,refs in [(identity,list(node_mappings[identity].values())),
                *[(i,[identity]) for i in node_mappings[identity].values()]]:
            required[part]=list(dict.fromkeys(required[part]+refs))
    reasons, drafts = {}, {}
    for identity, row in rows.items():
        errors = []
        reasons[identity] = errors
        if identity not in core["selection"]["undergraduate"]:
            errors.append("undergraduate_applicability_required")
        if row["gaps"] and not include_source_limits:
            errors.append("source_gap_requires_context_support")
        if any(rows[r]["version_id"] != row["version_id"] for r in required[identity]):
            errors.append("required_context_other_version")
        spans, associations = [], []
        version = versions[row["version_id"]]
        for field in row["fields"]:
            name, value = field["name"], field["reviewed_value"]
            if field["decision"] not in {"accepted", "corrected"}:
                errors.append(f"field_not_confirmed:{name}")
            supplied = anchors.get(identity, {}).get(name, [])
            if not isinstance(supplied, (list, tuple)):
                errors.append(f"invalid_field_spans:{name}")
                continue
            if include_source_limits and name=='arrows' and identity in node_mappings:
                try:
                    located=[SourceSpan.parse(s) for s in supplied]
                    for span in located:
                        check_span_binding(span,version)
                        if not span.is_complete or span.bbox is None or span.page_size is None:
                            raise ValueError('complete arrow geometry required')
                except ValueError:
                    errors.append(f'invalid_field_spans:{name}')
                    continue
                indexes=list(range(len(spans),len(spans)+len(located)));spans.extend(located)
                associations.append({'name':name,'value':copy.deepcopy(value),'source_blank':False,
                    'span_indexes':indexes,'event_sha256':field['review_event_sha256'],
                    'field_kind':'arrows','node_reading_ids':copy.deepcopy(node_mappings[identity])})
                continue
            if (include_source_limits and value is None and field['original_value'] is None
                    and name.endswith('/condition_note') and field['source_blank'] is False and not supplied):
                associations.append({'name':name,'value':None,'source_blank':False,
                    'span_indexes':[],'event_sha256':field['review_event_sha256'],'field_state':'not_recorded'})
                continue
            if not isinstance(value, str):
                errors.append(f"field_requires_scalar_mapping:{name}")
                continue
            if field["source_blank"]:
                if supplied:
                    errors.append(f"blank_field_has_spans:{name}")
                located = []
            elif not supplied:
                errors.append(f"missing_field_spans:{name}")
                continue
            else:
                try:
                    located = _field_spans(field, supplied, version, row)
                except ValueError:
                    errors.append(f"invalid_field_spans:{name}")
                    continue
            indexes = list(range(len(spans), len(spans) + len(located)))
            spans.extend(located)
            associations.append({"name": name, "value": value, "source_blank": field["source_blank"],
                "span_indexes": indexes, "event_sha256": field["review_event_sha256"]})
        if not spans:
            errors.append("no_located_source_text")
        if len({span_identity(s) for s in spans}) != len(spans):
            errors.append("duplicate_source_span")
        source_text = "\n".join(s.text for s in spans)
        text = _json({"fields": [{k: f[k] for k in ("name", "value", "source_blank")} for f in associations]})
        limits = []
        group = None
        if include_source_limits:
            try:
                limits = make_source_limits(row, associations, spans)
                if 'original_reading_id' in row or 'part_order' in row:
                    members=[r for r in rows.values() if r.get('original_reading_id')==row.get('original_reading_id')]
                    orders=[r.get('part_order') for r in members]
                    if (any(type(i) is not int for i in orders) or sorted(orders)!=list(range(len(members)))
                            or any(r['version_id'] != row['version_id'] for r in members)):
                        raise ValueError('incomplete service parts')
                    group={'logical_step_id':row['original_reading_id'],'part_order':row['part_order'],
                        'part_count':len(members)}
                text = serialize_reviewed_fields(associations,limits,group)
            except (ValueError,KeyError,TypeError,IndexError):
                errors.append("source_gap_requires_context_support")
        count = max(estimate_tokens(source_text), estimate_tokens(text))
        if count > token_cap:
            errors.append("over_token_cap")
        if errors:
            continue
        fields = {"reading_id": identity, "field_associations": associations,
            "applicability_basis_ref": row["applicability_evidence_ref"]}
        if include_source_limits:
            fields.update(context_format=CONTEXT_FORMAT,source_limits=limits)
            if group is not None:fields['service_group']=group
        data = {"schema_version": Chunk.SCHEMA_VERSION, "chunk_type": "policy",
            "chunker_version": CONTEXT_CHUNKER_VERSION if include_source_limits else CHUNKER_VERSION, "edition_id": version.edition_id,
            "document_id": version.document_id, "version_id": version.version_id,
            "byte_sha256": version.byte_sha256, "anchored": True, "source_verification": "pending",
            "content_review": "pending", "source_text": source_text, "text": text,
            "spans": [s.model_dump(mode="json") for s in spans], "section_path": [],
            "scope": ["audience:undergraduate"], "content_hash": compute_content_hash(source_text, text),
            "source_label": version.filename, "token_count": {"count": count, "method": "estimate-v1",
                "exact": False, "includes_prefix_and_special_tokens": False}, "type_fields": fields}
        # Dependency reading identities break cyclic-ID recursion and invalidate changed context.
        data["chunk_id"] = _digest({"chunk": data, "required_readings": required[identity]})
        drafts[identity] = data
    # A withheld continuation/condition withholds every dependent, including cycles.
    changed = True
    while changed:
        changed = False
        for identity in rows:
            if reasons[identity]:
                continue
            blocked = [r for r in required[identity] if reasons[r]]
            if blocked:
                reasons[identity].extend(f"required_context_withheld:{r}" for r in blocked)
                changed = True
    # Commit identities to the entire required context, using base IDs to handle
    # cycles without hashing recursively changing final IDs.
    base_ids = {identity: data["chunk_id"] for identity, data in drafts.items()}
    for identity, data in drafts.items():
        if reasons[identity]:
            continue
        closure, pending = {identity}, [identity]
        while pending:
            current = pending.pop()
            for ref in required[current]:
                if ref not in closure:
                    closure.add(ref)
                    pending.append(ref)
        data["chunk_id"] = _digest({"base_id": base_ids[identity],
            "required_context": {r: base_ids[r] for r in sorted(closure)}})
    chunks, coverage, withheld = [], [], []
    for identity, row in rows.items():
        if reasons[identity]:
            withheld.append({"reading_id": identity, "reasons": reasons[identity], "gaps": copy.deepcopy(row["gaps"])})
            continue
        data = drafts[identity]
        data["type_fields"]["required_neighbor_chunk_ids"] = [drafts[r]["chunk_id"] for r in required[identity]]
        chunk = bind_chunk(Chunk.parse(data), versions[row["version_id"]])
        chunks.append(chunk.model_dump(mode="json"))
        coverage.append({"reading_id": identity, "chunk_ids": [chunk.chunk_id]})
    return {"schema_version": "bintanong-reviewed-policy-pending-chunks-v1", "candidate_only": True,
        "activation_eligible": False, "source_governance_changed": False,
        "chunker_version": CONTEXT_CHUNKER_VERSION if include_source_limits else CHUNKER_VERSION,
        "preparation_fingerprint": _digest(core), "token_cap": token_cap, "chunks": chunks,
        "item_coverage": coverage, "withheld": withheld, "preparation": copy.deepcopy(bundle),
        "coverage": {"supplied_readings": len(rows), "emitted_readings": len(coverage),
            "withheld_readings": len(withheld), "scope": "supplied reviewed readings only"}}
