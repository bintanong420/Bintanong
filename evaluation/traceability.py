"""One pending source/chunk -> synthetic rule draft -> synthetic case exercise.

The source passage is provenance evidence, not support for the invented policy. A maintainer's
cached-extraction content check is separate from the source register's review and authorization.
This checker neither verifies sources nor activates capabilities in the runtime registry.
"""

import hashlib

from backend.bintanong_contracts.base import is_logical_locator, reject_foreign_ids
from backend.bintanong_contracts.governance import SourceDocumentVersion
from backend.bintanong_contracts.source import Chunk, check_chunk_binding
from backend.bintanong_contracts.symbolic import Capability, CapabilityRegistry, SymbolicResult

from .case import case_findings
from .protocol import canonical_json, case_digest

SCHEMA_VERSION = "bintanong-evaluation-traceability-v1"
_REGISTRY = CapabilityRegistry({"synthetic_prerequisite": Capability("synthetic_traceability", ("course",))})
_KEYS = {"schema_version", "verification_state", "relation", "document", "chunk", "rule_draft",
         "case", "binding", "content_check"}


def check_trace(trace: dict) -> None:
    """Raise ValueError on a broken/ambiguous link or a source-authority assertion. No I/O."""
    if not isinstance(trace, dict) or set(trace) != _KEYS:
        raise ValueError("trace keys must match the traceability contract exactly")
    if trace["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unknown trace schema_version")
    if trace["verification_state"] != "synthetic_only":
        raise ValueError("trace verification_state must remain synthetic_only")
    if trace["relation"] != "synthetic_exercise_only":
        raise ValueError("relation must remain synthetic_exercise_only; printed text does not support invented policy")
    version = SourceDocumentVersion.parse(trace["document"])
    chunk = Chunk.parse(trace["chunk"])
    check_chunk_binding(chunk, version)
    if version.verification_state.state != "pending" or version.approval_state.state != "not_requested" \
            or version.approval_id is not None:
        raise ValueError("synthetic exercise requires pending source verification and no requested approval")
    result = SymbolicResult.parse(trace["rule_draft"])
    _REGISTRY.check_result(result)
    if not result.decision.synthetic or result.decision.outcome != "unknown" \
            or result.decision.rule_coverage != "absent" or result.scope is not None:
        raise ValueError("rule draft must be synthetic unknown with absent policy coverage and no applicability scope")
    if len(result.rule_ids) != 1 or not result.rule_bundle_version:
        raise ValueError("trace needs exactly one rule draft and a rule bundle version")
    if any(i.fact_ref is not None for i in result.inputs):
        raise ValueError("synthetic exercise cannot carry private session facts")
    if result.rule_spans != chunk.spans:
        raise ValueError("rule spans must equal all chunk source spans exactly, once and in order")
    case = trace["case"]
    findings = case_findings(case)
    if findings:
        raise ValueError("invalid case: " + "; ".join(findings))
    reject_foreign_ids(case, "institutional")
    if case["status"] != "synthetic" or case["scope"] is not None:
        raise ValueError("case must remain synthetic with null source applicability scope")
    if case["expected_route"] != "Symbolic" or case["expected_outcome"] != result.decision.outcome:
        raise ValueError("case route/outcome differs from the synthetic rule draft")
    if result.decision.unknown_conditions != (case["synthetic_policy"],):
        raise ValueError("synthetic policy must match the rule draft's explicit invented assumption")
    if tuple(case["missing_facts"]) != result.decision.missing_facts:
        raise ValueError("case missing facts differ from the rule draft")
    expected = {"chunk_id": chunk.chunk_id, "chunk_content_hash": chunk.content_hash,
                "rule_id": result.rule_ids[0], "rule_bundle_version": result.rule_bundle_version,
                "rule_draft_digest": hashlib.sha256(canonical_json(result.model_dump(mode="json")).encode("utf-8")).hexdigest(),
                "case_id": case["case_id"], "case_digest": case_digest(case),
                "source_spans": [s.model_dump(mode="json") for s in chunk.spans]}
    if canonical_json(trace["binding"]) != canonical_json(expected):
        raise ValueError("binding differs from the exact chunk/hash, source spans, rule/bundle or case/digest")
    check = trace["content_check"]
    if not isinstance(check, dict) or set(check) != {"state", "evidence_ref", "chunk_id", "content_hash"}:
        raise ValueError("content_check keys must name state, evidence_ref, chunk_id and content_hash")
    if check["state"] != "checked_against_cached_extraction":
        raise ValueError("content_check records only a check against cached_extraction")
    if not isinstance(check["evidence_ref"], str) or not is_logical_locator(check["evidence_ref"]):
        raise ValueError("content_check evidence_ref must be a nonblank logical locator")
    reject_foreign_ids(check, "institutional")
    if check["chunk_id"] != chunk.chunk_id or check["content_hash"] != chunk.content_hash:
        raise ValueError("content_check does not name the bound chunk and content_hash")


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()
    check_trace(json.loads(args.trace.read_text(encoding="utf-8")))
    print("Trace links valid; synthetic exercise only, source verification pending, approval not requested.")
