"""Evaluation case schema and strict checker (Phase 1 Task 5).

A case is plain JSON. Closed lists for routes, controls and the five symbolic outcomes are loaded from
knowledge/manifests/governance-vocabulary.json through the contracts package, never retyped here.
`case_findings` returns a list of human-readable findings; an empty list means the case is well formed.
Well formed is not verified: status `verified` additionally needs independent, source-backed review
evidence, and the set-level check in protocol.py resolves gold spans against a source registry.
Everything committed under evaluation/cases is synthetic.
"""

from __future__ import annotations

import re

from backend.bintanong_contracts.base import VOCAB

SCHEMA_VERSION = "bintanong-evaluation-case-v1"
ROUTES = tuple(VOCAB["runtime"]["routes"])
CONTROLS = tuple(VOCAB["runtime"]["controls"])
OUTCOMES = tuple(VOCAB["decision"]["outcomes"])
CATEGORIES = ("enrollment", "prerequisites", "grades", "academic_standing", "discipline")
LANGUAGES = ("en", "tl", "taglish")
STATUSES = ("synthetic", "candidate", "verified")
SPLITS = ("dev", "final")
ADVERSARIAL_KINDS = ("ambiguity", "negation", "missing_facts", "wrong_edition", "conflicting_evidence",
                     "unknown_course", "incomplete_coverage", "unsupported_operation", "operational_failure")
CASE_KEYS = ("schema_version", "case_id", "group_id", "category", "language", "query", "adversarial_kinds",
             "scope", "scope_null_reason", "expected_route", "expected_control", "expected_outcome",
             "required_facts", "missing_facts", "gold_spans", "gold_rules", "synthetic_policy",
             "acceptable_claims", "must_abstain", "split", "status", "review")
SCOPE_KEYS = ("institution", "edition", "version_id")
SPAN_KEYS = ("byte_sha256", "version_id", "page", "locator_ref", "text_sha256")
SPAN_REF_KEYS = SPAN_KEYS[:-1]
REVIEW_KEYS = ("author", "reviewer", "evidence_ref", "review_version")

CASE_ID = re.compile(r"[a-z0-9][a-z0-9-]{2,63}")
GROUP_ID = re.compile(r"grp-[a-z0-9][a-z0-9-]{2,48}")
VERSION_ID = re.compile(r"ver-[a-z0-9][a-z0-9-]*")
SHA256 = re.compile(r"[0-9a-f]{64}")
# Committed evaluation data carries no private identity: reject an email or a long digit run (student number).
PRIVATE_IDENTITY = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+|\d{9,}")
# Control outcomes that mean "do not answer the policy question".
ABSTAINING_CONTROLS = ("clarify", "unsupported_scope", "evidence_unavailable")
# Adversarial kinds whose correct behaviour is never a determinate answer.
ABSTAINING_KINDS = ("ambiguity", "wrong_edition", "conflicting_evidence", "unknown_course",
                    "incomplete_coverage", "unsupported_operation", "operational_failure", "missing_facts")


def _str(value, nonblank=True):
    return isinstance(value, str) and (not nonblank or bool(value.strip()))


def _strs(value):
    return isinstance(value, list) and all(_str(v) for v in value)


def _exact_keys(obj, keys, label, out):
    if not isinstance(obj, dict):
        out.append(f"{label} must be an object")
        return False
    if set(obj) != set(keys):
        out.append(f"{label} keys must be exactly {sorted(keys)}; got {sorted(obj, key=str)}")
        return False
    return True


def _walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _walk_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _walk_strings(v)


def case_findings(case) -> list[str]:
    out: list[str] = []
    if not _exact_keys(case, CASE_KEYS, "case", out):
        return out
    c = case
    if c["schema_version"] != SCHEMA_VERSION:
        out.append(f"schema_version must be {SCHEMA_VERSION!r}")
    if not (isinstance(c["case_id"], str) and CASE_ID.fullmatch(c["case_id"])):
        out.append("case_id must match [a-z0-9][a-z0-9-]{2,63}")
    if not (isinstance(c["group_id"], str) and GROUP_ID.fullmatch(c["group_id"])):
        out.append("group_id must match grp-[a-z0-9][a-z0-9-]{2,48}")
    for key, allowed in (("category", CATEGORIES), ("language", LANGUAGES), ("status", STATUSES),
                         ("split", SPLITS)):
        if c[key] not in allowed:
            out.append(f"{key} {c[key]!r} is not one of {list(allowed)}")
    if not (_str(c["query"]) and re.search(r"\w", c["query"])):
        out.append("query must be a non-blank string with at least one word")
    if not isinstance(c["must_abstain"], bool):
        out.append("must_abstain must be a boolean")
    for key in ("required_facts", "missing_facts", "gold_rules", "acceptable_claims"):
        if not _strs(c[key]):
            out.append(f"{key} must be a list of non-blank strings")
    for text in _walk_strings({k: c[k] for k in ("query", "required_facts", "missing_facts", "gold_rules",
                                                 "acceptable_claims", "synthetic_policy")}):
        if PRIVATE_IDENTITY.search(text):
            out.append("text looks like a private identity (email or long digit run); use fictional data only")
            break

    kinds = c["adversarial_kinds"]
    if not (isinstance(kinds, list) and all(k in ADVERSARIAL_KINDS for k in kinds) and len(set(kinds)) == len(kinds)):
        out.append(f"adversarial_kinds must be a duplicate-free list drawn from {list(ADVERSARIAL_KINDS)}")
        kinds = []

    _check_scope(c, out)
    _check_route(c, kinds, out)
    _check_status(c, out)
    return out


def _check_scope(c, out):
    scope, reason = c["scope"], c["scope_null_reason"]
    if scope is None:
        if not _str(reason):
            out.append("scope is null, so scope_null_reason must say why")
    else:
        if reason is not None:
            out.append("scope_null_reason must be null when scope is given")
        if _exact_keys(scope, SCOPE_KEYS, "scope", out):
            if not (_str(scope["institution"]) and _str(scope["edition"])):
                out.append("scope institution and edition must be non-blank strings")
            if not (scope["version_id"] is None or (isinstance(scope["version_id"], str) and VERSION_ID.fullmatch(scope["version_id"]))):
                out.append("scope version_id must be null or ver-...")


def _check_route(c, kinds, out):
    route, control, outcome = c["expected_route"], c["expected_control"], c["expected_outcome"]
    if route is not None and route not in ROUTES:
        out.append(f"expected_route {route!r} is not one of {list(ROUTES)}")
    if control is not None and control not in CONTROLS:
        out.append(f"expected_control {control!r} is not one of {list(CONTROLS)}")
    if outcome is not None and outcome not in OUTCOMES:
        out.append(f"expected_outcome {outcome!r} is not one of {list(OUTCOMES)}")
    if (route is None) == (control is None):
        out.append("exactly one of expected_route and expected_control must be set")
    if outcome is not None and route not in ("Symbolic", "Hybrid"):
        out.append("expected_outcome needs a Symbolic or Hybrid route")
    if route == "Symbolic" and outcome is None:
        out.append("a Symbolic route needs an expected_outcome")
    if not isinstance(c["must_abstain"], bool):
        return
    abstain = c["must_abstain"]
    if outcome in ("eligible", "ineligible") and abstain:
        out.append(f"outcome {outcome} is determinate, so must_abstain must be false")
    if outcome in ("unknown", "unsupported", "error") and not abstain:
        out.append(f"outcome {outcome} is never an approval or denial, so must_abstain must be true")
    if control in ABSTAINING_CONTROLS and not abstain:
        out.append(f"control {control} must abstain")
    if control == "greeting" and abstain:
        out.append("a greeting is not an abstention")
    for kind in kinds:
        if kind in ABSTAINING_KINDS and not abstain:
            out.append(f"adversarial kind {kind} must abstain")
    if "missing_facts" in kinds and not c["missing_facts"]:
        out.append("adversarial kind missing_facts needs a non-empty missing_facts list")
    if "unsupported_operation" in kinds and not (outcome == "unsupported" or control == "unsupported_scope"):
        out.append("unsupported_operation needs outcome unsupported or control unsupported_scope")
    if "operational_failure" in kinds and not (outcome == "error" or control == "evidence_unavailable"):
        out.append("operational_failure needs outcome error or control evidence_unavailable")


def span_reference_findings(span) -> list[str]:
    """Validate the four locator fields shared by gold spans and output citations."""
    out: list[str] = []
    if not _exact_keys(span, SPAN_REF_KEYS, "span reference", out):
        return out
    if not (isinstance(span["byte_sha256"], str) and SHA256.fullmatch(span["byte_sha256"])):
        out.append("span reference byte_sha256 must be 64 lowercase hex")
    if not (isinstance(span["version_id"], str) and VERSION_ID.fullmatch(span["version_id"])):
        out.append("span reference version_id must be ver-...")
    if not (isinstance(span["page"], int) and not isinstance(span["page"], bool) and span["page"] >= 1):
        out.append("span reference page must be an integer >= 1")
    if not _str(span["locator_ref"]):
        out.append("span reference locator_ref must be a non-blank string")
    return out


def _check_span(span, out):
    if not _exact_keys(span, SPAN_KEYS, "gold span", out):
        return
    out.extend(span_reference_findings({key: span[key] for key in SPAN_REF_KEYS}))
    if not (isinstance(span["text_sha256"], str) and SHA256.fullmatch(span["text_sha256"])):
        out.append("gold span text_sha256 must be 64 lowercase hex (the passage itself stays outside Git)")


def _check_status(c, out):
    status, review = c["status"], c["review"]
    spans = c["gold_spans"]
    if not isinstance(spans, list):
        out.append("gold_spans must be a list")
        spans = []
    for s in spans:
        _check_span(s, out)
    if not _exact_keys(review, REVIEW_KEYS, "review", out):
        return
    for key in REVIEW_KEYS:
        if review[key] is not None and not _str(review[key]):
            out.append(f"review.{key} must be null or a non-blank string")
    author, reviewer = review["author"], review["reviewer"]
    if _str(author) and _str(reviewer) and author.strip().casefold() == reviewer.strip().casefold():
        out.append("reviewer must be independent of the author")
    if status == "synthetic":
        if spans or c["gold_rules"]:
            out.append("a synthetic case has no gold spans or rules")
        if not _str(c["synthetic_policy"]):
            out.append("a synthetic case states its invented rule in synthetic_policy")
        if review["reviewer"] is not None or review["evidence_ref"] is not None or review["review_version"] is not None:
            out.append("a synthetic case carries no review evidence")
        if c["split"] != "dev":
            out.append("a synthetic case belongs to the dev split only")
        return
    if c["synthetic_policy"] is not None:
        out.append("only a synthetic case has synthetic_policy")
    if status == "verified":
        if not spans:
            out.append("a verified case needs source-backed gold spans")
        if c["scope"] is None:
            out.append("a verified case needs an applicable scope")
        missing = [k for k in REVIEW_KEYS if review[k] is None]
        if missing:
            out.append(f"a verified case needs review evidence; missing {missing}")
