"""Reviewed raw text partitions and inactive original-image body regions.

Raw character offsets index the retained item string, not native PDF glyph arrays.
Furniture provenance is retained; only confirmed programme segments become body spans.
"""
from __future__ import annotations

import copy,hashlib,json,re
from collections.abc import Mapping

from ...bintanong_contracts.source import canonical_text
from .register import load_pending_register
from .reviewed_policy import build_reviewed_policy_bundle
from .reviewed_image_spans import _numbers,_region,_span,_transform


def reviewed_body_partition(row):
    """Validate the complete confirmed body/furniture correction without mutation."""
    if row.get("intended_audience") != "undergraduate" or row.get("applicability") == "excluded":
        raise ValueError("undergraduate reviewed body required")
    fields = {f["name"]: f for f in row["fields"]}
    body,seg = fields.get("body"),fields.get("segmentation")
    if (body is None or seg is None or body["source_blank"] or seg["source_blank"]
            or not isinstance(body["reviewed_value"],str) or not body["reviewed_value"].strip()
            or any(f["decision"] not in {"accepted","corrected"} for f in (body,seg))
            or body["review_event_sha256"] != seg["review_event_sha256"]
            or body["locator"]["field"] != "body" or seg["locator"]["field"] != "segmentation"):
        raise ValueError("confirmed linked body and segmentation review required")
    raw = body["locator"].get("evidence")
    if (not isinstance(raw,dict) or not isinstance(raw.get("text"),str)
            or raw["text"] != body["original_value"] or not isinstance(raw.get("self_ref"),str)
            or not re.fullmatch(r"#/texts/\d+",raw["self_ref"])):
        raise ValueError("original raw text item required")
    prov,segments = raw.get("prov"),seg["reviewed_value"]
    if (not isinstance(prov,list) or not prov or not isinstance(segments,list)
            or len(prov) != len(segments) or seg["original_value"] != prov
            or seg["locator"].get("evidence") != prov):
        raise ValueError("complete original raw provenance partition required")
    body_parts,furniture,last,pages = [],[],0,[]
    for original,segment in zip(prov,segments):
        if (not isinstance(original,dict) or not isinstance(segment,dict)
                or segment.get("raw_provenance") != original
                or type(original.get("page_no")) is not int or original["page_no"] < 1
                or not isinstance(segment.get("kind"),str)
                or segment["kind"] not in {"programme_name","page_furniture"}
                or not isinstance(segment.get("text"),str) or not segment["text"].strip()):
            raise ValueError("invalid reviewed raw segment")
        ranges = original.get("charspan")
        if (not isinstance(ranges,list) or len(ranges) != 2 or any(type(n) is not int for n in ranges)
                or not last <= ranges[0] < ranges[1] <= len(raw["text"])
                or raw["text"][last:ranges[0]].strip()
                or canonical_text(raw["text"][ranges[0]:ranges[1]]) != canonical_text(segment["text"])):
            raise ValueError("raw character partition differs from reviewed text")
        last = ranges[1];pages.append(original["page_no"])
        (body_parts if segment["kind"] == "programme_name" else furniture).append(copy.deepcopy(segment))
    if (raw["text"][last:].strip() or not body_parts
            or set(body["locator"]["physical_pages"]) != set(pages)
            or set(seg["locator"]["physical_pages"]) != set(pages)
            or canonical_text(" ".join(p["text"] for p in body_parts)) != canonical_text(body["reviewed_value"])):
        raise ValueError("body text/pages differ from complete reviewed partition")
    return {"raw_item_ref":raw["self_ref"],"raw_text":raw["text"],
        "body_text":body["reviewed_value"],"body_pages":list(dict.fromkeys(p["raw_provenance"]["page_no"] for p in body_parts)),
        "body_segments":body_parts,"furniture_segments":furniture,"segments":copy.deepcopy(segments),
        "event_sha256":body["review_event_sha256"]}


def _raw_region(original,page):
    box = original.get("bbox")
    if not isinstance(box,dict) or box.get("coord_origin") != "BOTTOMLEFT":
        raise ValueError("explicit original BOTTOMLEFT PDF point box required")
    l,b,r,t = _numbers([box.get(k) for k in ("l","b","r","t")],4)
    height,scale = page["page_size"][1],page["scale"]
    region = [l*scale,(height-t)*scale,r*scale,(height-b)*scale]
    _region(region,page)
    return region


def map_reviewed_body_segments(bundle, *, sources,review_events,source_versions,image_pages,read_page_image):
    """Map only reviewed body segments using retained PDF boxes and checked renders."""
    if not callable(read_page_image) or not isinstance(image_pages,Mapping):
        raise ValueError("original page reader and image descriptors required")
    core = build_reviewed_policy_bundle(bundle["readings"],sources=sources,review_events=review_events)
    dump = lambda v:json.dumps(v,sort_keys=True,ensure_ascii=False,allow_nan=False)
    if any(dump(bundle.get(k)) != dump(v) for k,v in core.items()):
        raise ValueError("reviewed preparation differs from original evidence")
    versions = {v.version_id:v for v in load_pending_register(source_versions)}
    for row in core["readings"]:
        version = versions.get(row["version_id"])
        if version is None or version.byte_sha256 != row["source_sha256"]:
            raise ValueError("source/version missing or mismatched")
    pages,anchors,mapped,withheld = {},{},{},[]
    def checked_page(row,number):
        key = (row["source_sha256"],number)
        if key in pages:return pages[key]
        declaration = image_pages.get(key)
        if not isinstance(declaration,dict):raise ValueError("original image unavailable")
        _transform(declaration)
        observed = read_page_image(sources[row["source_sha256"]],number)
        if (not isinstance(observed,dict) or not isinstance(observed.get("image_bytes"),bytes)
                or hashlib.sha256(observed["image_bytes"]).hexdigest() != declaration["image_sha256"]
                or any(observed.get(k) != declaration.get(k) for k in ("image_size","page_size","scale","rotation","crop"))):
            raise ValueError("original image mismatch")
        page = {k:copy.deepcopy(declaration[k]) for k in ("image_sha256","image_size","page_size","scale","rotation","crop")}
        page.update(source_sha256=row["source_sha256"],physical_page=number);pages[key]=page
        return page
    for row in core["readings"]:
        if not any(f["name"] == "body" for f in row["fields"]):continue
        try:
            partition = reviewed_body_partition(row)
            partition_regions = []
            for segment in partition["segments"]:
                original = segment["raw_provenance"];page = checked_page(row,original["page_no"])
                partition_regions.append({"kind":segment["kind"],"physical_page":original["page_no"],
                    "pixel_region":_raw_region(original,page),"image_sha256":page["image_sha256"]})
            spans,regions = [],[]
            for index,segment in enumerate(partition["body_segments"]):
                original = segment["raw_provenance"];page = checked_page(row,original["page_no"])
                region = _raw_region(original,page)
                spans.append(_span(row,f"body-segment-{index}",segment["text"],region,page))
                regions.append({"physical_page":original["page_no"],"pixel_region":region,
                    "image_sha256":page["image_sha256"],"original_provenance":copy.deepcopy(original)})
        except (ValueError,OSError,IndexError,RuntimeError):
            withheld.append({"reading_id":row["reading_id"],"field_name":"body","reason":"reviewed_body_mapping_unavailable"})
            continue
        body = next(f for f in row["fields"] if f["name"] == "body")
        anchors[row["reading_id"]] = {"body":spans}
        mapped[row["reading_id"]] = {"reading_id":row["reading_id"],"field_name":"body",
            "source_sha256":row["source_sha256"],"version_id":row["version_id"],
            "event_sha256":body["review_event_sha256"],"original_body_locator":copy.deepcopy(body["locator"]),
            "partition":partition,"regions":regions,"partition_regions":partition_regions,"spans":copy.deepcopy(spans)}
    return {"schema_version":"bintanong-reviewed-body-segments-v1","candidate_only":True,
        "activation_eligible":False,"source_governance_changed":False,"field_spans":anchors,
        "mapping_evidence":list(mapped.values()),"withheld_fields":withheld,
        "validated_pages":list(pages.values()),"preparation":copy.deepcopy(bundle),
        "coverage":{"mapped_body_fields":len(mapped),"withheld_body_fields":len(withheld)}}
