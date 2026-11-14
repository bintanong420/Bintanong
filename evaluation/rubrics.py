"""Machine-checkable rubrics, strict scoring and the run record (Phase 1 Task 5).

Scoring is deterministic and strict. The rule everything rests on: `unknown`, `unsupported` and `error`
are never an approval and never a denial. Only `eligible` counts as approval and only `ineligible` as
denial. An answer that approves or denies without a determinate gold outcome is a critical error that
zeroes the case total. Axis scores are 0 or 1 (or None when the axis does not apply). Human adjudication
of claim wording is a later step; here an acceptable claim matches by normalised exact text only.
"""

from __future__ import annotations

import re
import unicodedata

from pydantic import Field, field_validator

from backend.bintanong_contracts.base import Contract, Record, canonical_json, is_pinned_revision

from .case import LANGUAGES, OUTCOMES, ROUTES, CONTROLS, SPAN_REF_KEYS, case_findings, span_reference_findings

NEVER_APPROVAL_OR_DENIAL = ("unknown", "unsupported", "error")
STANCES = ("approve", "deny", "abstain", "clarify", "info")
FLAGS = ("false_approval", "false_denial", "false_abstention", "error_as_policy", "unsupported_claim",
         "route_mismatch", "silent_rag_fallback", "missing_gold_span", "extra_span", "outcome_mismatch",
         "unexpected_outcome", "stance_outcome_mismatch", "language_mismatch")
CRITICAL_FLAGS = ("false_approval", "false_denial", "error_as_policy", "unsupported_claim")
OUTPUT_KEYS = ("route", "control", "outcome", "stance", "language", "claims", "cited_spans", "operational_error")

RUBRICS = {
    "route": {
        "description": "The route and control outcome equal the expected pair; an unavailable Symbolic or Hybrid path never becomes RAG.",
        "scoring": "1 when route and control both equal the case's expected values, else 0.",
        "failure_flags": ["route_mismatch", "silent_rag_fallback"]},
    "evidence": {
        "description": "Cited spans equal the gold spans (hash, version, page, locator); a citation alone does not prove support.",
        "scoring": "1 when the set of cited spans equals the set of gold spans, else 0. With no gold spans, any citation scores 0.",
        "failure_flags": ["missing_gold_span", "extra_span"]},
    "symbolic": {
        "description": "The five-outcome result equals the expected outcome. unknown, unsupported and error never count as approval or denial.",
        "scoring": "1 when outcomes are equal, else 0; applies when either side has an outcome.",
        "failure_flags": ["false_approval", "false_denial", "false_abstention", "error_as_policy",
                          "outcome_mismatch", "unexpected_outcome"]},
    "answer": {
        "description": "The stance matches the gold decision (approve, deny, abstain or clarify, info), agrees with the reported outcome and uses the case language.",
        "scoring": "1 when the stance is acceptable, consistent with the outcome and in the case language, else 0.",
        "failure_flags": ["false_approval", "false_denial", "false_abstention", "stance_outcome_mismatch",
                          "language_mismatch"]},
    "unsupported_claims": {
        "description": "Every claim is one of the case's acceptable claims (normalised exact match). Any other claim is an invented claim.",
        "scoring": "1 when no claim is unsupported, else 0; the count is reported separately.",
        "failure_flags": ["unsupported_claim"]},
}


class RubricError(ValueError):
    """The case or the system output is malformed, so it cannot be scored."""


def counts_as_approval(outcome) -> bool:
    return outcome == "eligible"


def counts_as_denial(outcome) -> bool:
    return outcome == "ineligible"


def _norm(text: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold()))


def _check_output(o) -> None:
    if not isinstance(o, dict) or set(o) != set(OUTPUT_KEYS):
        raise RubricError(f"system output keys must be exactly {sorted(OUTPUT_KEYS)}")
    if o["route"] is not None and o["route"] not in ROUTES:
        raise RubricError("output route is not a known route")
    if o["control"] is not None and o["control"] not in CONTROLS:
        raise RubricError("output control is not a known control")
    if o["outcome"] is not None and o["outcome"] not in OUTCOMES:
        raise RubricError("output outcome is not one of the five outcomes")
    if o["stance"] not in STANCES:
        raise RubricError(f"output stance must be one of {list(STANCES)}")
    if o["language"] not in LANGUAGES:
        raise RubricError(f"output language must be one of {list(LANGUAGES)}")
    if not (isinstance(o["claims"], list) and all(isinstance(c, str) for c in o["claims"])):
        raise RubricError("output claims must be a list of strings")
    if not isinstance(o["operational_error"], bool):
        raise RubricError("output operational_error must be a boolean")
    spans = o["cited_spans"]
    if not isinstance(spans, list):
        raise RubricError("cited_spans must be a list")
    for span in spans:
        problems = span_reference_findings(span)
        if problems:
            raise RubricError(f"cited span is malformed: {problems[0]}")


def _ref(span) -> tuple:
    return tuple(span[k] for k in SPAN_REF_KEYS)


def score_case(case, output) -> dict:
    problems = case_findings(case)
    if problems:
        raise RubricError(f"case is malformed: {problems[0]}")
    _check_output(output)
    flags: set[str] = set()
    gold_outcome = case["expected_outcome"]
    out_outcome, stance = output["outcome"], output["stance"]

    # route / control
    route_ok = output["route"] == case["expected_route"] and output["control"] == case["expected_control"]
    if not route_ok:
        flags.add("route_mismatch")
        if case["expected_route"] in ("Symbolic", "Hybrid") and output["route"] == "RAG":
            flags.add("silent_rag_fallback")

    # evidence
    gold = {_ref(s) for s in case["gold_spans"]}
    cited = {_ref(s) for s in output["cited_spans"]}
    if gold - cited:
        flags.add("missing_gold_span")
    if cited - gold:
        flags.add("extra_span")
    evidence_ok = gold == cited

    # decision flags, from the reported outcome and from the stance
    gold_decision = "approve" if counts_as_approval(gold_outcome) else "deny" if counts_as_denial(gold_outcome) else None
    if counts_as_approval(out_outcome) and gold_outcome != "eligible":
        flags.add("false_approval")
    if counts_as_denial(out_outcome) and gold_outcome != "ineligible":
        flags.add("false_denial")
    if gold_decision and out_outcome in NEVER_APPROVAL_OR_DENIAL:
        flags.add("false_abstention")
    if stance == "approve" and gold_decision != "approve":
        flags.add("false_approval")
    if stance == "deny" and gold_decision != "deny":
        flags.add("false_denial")
    if gold_decision and stance in ("abstain", "clarify"):
        flags.add("false_abstention")
    decided = counts_as_approval(out_outcome) or counts_as_denial(out_outcome) or stance in ("approve", "deny")
    if decided and (gold_outcome == "error" or output["operational_error"]):
        flags.add("error_as_policy")
    if out_outcome is not None and (counts_as_approval(out_outcome) != (stance == "approve")
                                    or counts_as_denial(out_outcome) != (stance == "deny")):
        flags.add("stance_outcome_mismatch")
    if gold_outcome is None and out_outcome is not None:
        flags.add("unexpected_outcome")
    elif gold_outcome != out_outcome and not (flags & {"false_approval", "false_denial", "false_abstention"}):
        flags.add("outcome_mismatch")
    symbolic_ok = gold_outcome == out_outcome

    # answer
    control = case["expected_control"]
    if control == "clarify":
        stance_ok = stance == "clarify"
    elif control in ("unsupported_scope", "evidence_unavailable") or case["must_abstain"]:
        stance_ok = stance in ("abstain", "clarify")
    elif gold_decision:
        stance_ok = stance == gold_decision
    else:
        stance_ok = stance == "info"
    if output["language"] != case["language"]:
        flags.add("language_mismatch")
    answer_ok = (stance_ok and "stance_outcome_mismatch" not in flags and "language_mismatch" not in flags)

    # claims
    allowed = {_norm(c) for c in case["acceptable_claims"]}
    unsupported = sum(1 for c in output["claims"] if _norm(c) not in allowed)
    if unsupported:
        flags.add("unsupported_claim")

    axes = {"route": int(route_ok), "evidence": int(evidence_ok),
            "symbolic": int(symbolic_ok) if (gold_outcome is not None or out_outcome is not None) else None,
            "answer": int(answer_ok), "unsupported_claims": int(unsupported == 0)}
    critical = bool(flags & set(CRITICAL_FLAGS))
    applicable = [v for v in axes.values() if v is not None]
    total = 0.0 if critical else sum(applicable) / len(applicable)
    return {"case_id": case["case_id"], "axes": axes, "flags": sorted(flags), "critical": critical,
            "unsupported_claim_count": unsupported, "total": total}


def summarise(cases, scores) -> dict:
    """Per-category and per-language means, flag counts and critical-case count."""
    if len(cases) != len(scores) or any(c["case_id"] != s["case_id"] for c, s in zip(cases, scores)):
        raise RubricError("scores must line up with cases, one each, in order")
    flag_counts: dict[str, int] = {}
    groups: dict[str, dict[str, list[float]]] = {"by_category": {}, "by_language": {}}
    for c, s in zip(cases, scores):
        for f in s["flags"]:
            flag_counts[f] = flag_counts.get(f, 0) + 1
        groups["by_category"].setdefault(c["category"], []).append(s["total"])
        groups["by_language"].setdefault(c["language"], []).append(s["total"])
    pack = {name: {k: {"cases": len(v), "mean_total": sum(v) / len(v)} for k, v in sorted(g.items())}
            for name, g in groups.items()}
    return {"cases": len(cases), "critical_cases": sum(s["critical"] for s in scores),
            "flag_counts": dict(sorted(flag_counts.items())), **pack}


# --------------------------------------------------------------------------------------------
# run record
# --------------------------------------------------------------------------------------------
_Text = Field(min_length=1, pattern=r"\S")


def _pinned(value: str) -> str:
    if not is_pinned_revision(value):
        raise ValueError("revision must be pinned: a full lowercase commit (40 hex) or digest (64 hex)")
    return value


class Decoding(Record):
    temperature: float = Field(ge=0, allow_inf_nan=False)
    top_p: float = Field(gt=0, le=1, allow_inf_nan=False)
    max_new_tokens: int = Field(ge=1)
    seed: int


class EmbeddingConfig(Record):
    embedding_model_id: str = _Text
    embedding_model_revision: str

    _pin = field_validator("embedding_model_revision")(_pinned)


class RunRecord(Contract):
    """Everything needed to reproduce an evaluation run. A missing field or a floating revision is refused."""

    SCHEMA_VERSION = "bintanong-evaluation-run-record-v1"
    code_version: str = Field(pattern=r"^[0-9a-f]{40}$")
    prompt_version: str = _Text
    model_id: str = _Text
    model_revision: str
    quantization: str = _Text
    embedding_config: EmbeddingConfig
    knowledge_release_id: str = Field(pattern=r"^release-[a-z0-9-]+$")
    rule_bundle_version: str = _Text
    decoding: Decoding
    evaluation_set_version: str = _Text
    grouping_digest: str = Field(pattern=r"^[0-9a-f]{64}$")

    _pin = field_validator("model_revision")(_pinned)


def run_record_json(record: RunRecord) -> str:
    return canonical_json(record)


__all__ = ["RUBRICS", "FLAGS", "CRITICAL_FLAGS", "NEVER_APPROVAL_OR_DENIAL", "OUTCOMES", "RubricError",
           "RunRecord", "counts_as_approval", "counts_as_denial", "run_record_json", "score_case", "summarise"]
