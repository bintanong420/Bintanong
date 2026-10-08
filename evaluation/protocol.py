"""Split/group validation for evaluation case sets (Phase 1 Task 5). No CLI, no I/O except `load_cases`.

What it enforces
- Each group_id belongs to exactly one split, and that split is DERIVED from the group_id and a documented
  salt (never from case content or order), so adding cases never moves an existing group.
- Paraphrases, English/Tagalog/Taglish variants and near-duplicate scenarios share one group_id. A
  near-duplicate pair (normalised token-set Jaccard >= NEAR_DUPLICATE_THRESHOLD) with different group ids
  is a finding. Cross-language variants share few tokens, so those depend on the author; see the decision record.
- A freeze record stores the sorted final group ids, a digest per final case and an overall digest. Once
  given, a moved final group, an edited/removed/added final case or a tampered record is a finding.
- A final case's text may not appear in a prompt/few-shot example list.
- Coverage (>= 10 verified final Taglish cases per category, >= 50 total) is REPORTED with an honest
  status line. It is never a pass/fail of the integrity check, and a claim of MET that the data does not
  support is a finding.

Defaults below are strict and owner-reviewable. Nothing here verifies a case or approves a source.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

from .case import CATEGORIES, case_findings

REPORT_VERSION = "bintanong-evaluation-report-v1"
FREEZE_VERSION = "bintanong-evaluation-freeze-v1"
# Owner-reviewable defaults.
SPLIT_SALT = "bintanong-eval-split-v1"
FINAL_PERCENT = 30                 # share of groups whose derived split is "final"
NEAR_DUPLICATE_THRESHOLD = 0.8     # token-set Jaccard on normalised text
TARGET_PER_CATEGORY = 10
TARGET_TAGLISH_TOTAL = 50

FINDING_CODES = (
    "case_invalid", "duplicate_case_id", "split_not_derived", "group_split_leak", "group_mixed_category",
    "near_duplicate_group_mismatch", "unregistered_source", "freeze_malformed", "freeze_digest_mismatch",
    "freeze_salt_mismatch", "freeze_group_moved", "freeze_case_missing", "freeze_case_edited",
    "freeze_case_added", "freeze_group_added", "final_text_in_prompt_example", "coverage_claim_false",
)


def canonical_json(value) -> str:
    """Sorted keys, two-space indent, LF line ends, one trailing newline."""
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def _sha(value) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def case_digest(case) -> str:
    return _sha(case)


def derive_split(group_id: str, salt: str = SPLIT_SALT, final_percent: int = FINAL_PERCENT) -> str:
    """'final' when sha256(salt:group_id) falls in the first final_percent of 100 buckets, else 'dev'."""
    bucket = int.from_bytes(hashlib.sha256(f"{salt}:{group_id}".encode("utf-8")).digest()[:8], "big") % 100
    return "final" if bucket < final_percent else "dev"


def tokens(text: str) -> frozenset[str]:
    return frozenset(re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold()))


def similarity(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    union = ta | tb
    return len(ta & tb) / len(union) if union else 0.0


def _finding(code: str, subject: str, detail: str) -> dict:
    assert code in FINDING_CODES, code
    return {"code": code, "subject": subject, "detail": detail}


def load_cases(directory: Path) -> list[dict]:
    """Every *.json under `directory` is a list of cases; read in sorted path order."""
    cases: list[dict] = []
    for path in sorted(Path(directory).rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"{path.name}: a case file is a JSON list of cases")
        cases.extend(data)
    return cases


# --------------------------------------------------------------------------------------------
# per-case problems: schema findings and source resolution
# --------------------------------------------------------------------------------------------
def _case_problems(cases, registry) -> tuple[list[dict], set[int]]:
    """Findings for malformed cases and unresolved gold spans, plus indexes of the cases that are clean."""
    out, clean = [], set()
    for i, c in enumerate(cases):
        subject = c.get("case_id", f"#{i}") if isinstance(c, dict) else f"#{i}"
        problems = case_findings(c)
        for p in problems:
            out.append(_finding("case_invalid", str(subject), p))
        if not problems and c["status"] == "verified":
            for s in c["gold_spans"]:
                if (registry or {}).get(s["version_id"]) != s["byte_sha256"]:
                    out.append(_finding("unregistered_source", c["case_id"],
                                        f"gold span {s['version_id']} does not resolve to a registered source version"))
                    problems = ["unresolved span"]
        if not problems:
            clean.add(i)
    return out, clean


# --------------------------------------------------------------------------------------------
# freeze
# --------------------------------------------------------------------------------------------
def freeze_digest(freeze: dict) -> str:
    return _sha({k: freeze[k] for k in ("schema_version", "salt", "final_group_ids", "final_case_digests")})


def make_freeze(cases, *, registry=None, salt: str = SPLIT_SALT) -> dict:
    """Seal the final set. Refuses an empty set, an unverified or unresolved final case."""
    problems, clean = _case_problems(cases, registry)
    final = [(i, c) for i, c in enumerate(cases) if isinstance(c, dict) and c.get("split") == "final"]
    if not final:
        raise ValueError("nothing to freeze: no final-split case")
    bad = [c.get("case_id") for i, c in final if i not in clean or c["status"] != "verified"]
    if bad:
        raise ValueError(f"only verified, source-resolved final cases can be frozen; refused {sorted(map(str, bad))}")
    rec = {"schema_version": FREEZE_VERSION, "salt": salt,
           "final_group_ids": sorted({c["group_id"] for _, c in final}),
           "final_case_digests": {c["case_id"]: case_digest(c) for _, c in final}}
    rec["digest"] = freeze_digest(rec)
    return rec


def _freeze_findings(cases, freeze, salt) -> list[dict]:
    ok = (isinstance(freeze, dict)
          and set(freeze) == {"schema_version", "salt", "final_group_ids", "final_case_digests", "digest"}
          and freeze["schema_version"] == FREEZE_VERSION
          and isinstance(freeze["salt"], str) and isinstance(freeze["digest"], str)
          and isinstance(freeze["final_group_ids"], list) and all(isinstance(g, str) for g in freeze["final_group_ids"])
          and freeze["final_group_ids"] == sorted(set(freeze["final_group_ids"]))
          and isinstance(freeze["final_case_digests"], dict)
          and all(isinstance(k, str) and isinstance(v, str) for k, v in freeze["final_case_digests"].items()))
    if not ok:
        return [_finding("freeze_malformed", "freeze", "freeze record has the wrong shape")]
    out = []
    if freeze_digest(freeze) != freeze["digest"]:
        out.append(_finding("freeze_digest_mismatch", "freeze", "freeze record does not match its digest"))
    if freeze["salt"] != salt:
        out.append(_finding("freeze_salt_mismatch", "freeze", "freeze salt differs from the current split salt"))
    groups, frozen = set(freeze["final_group_ids"]), freeze["final_case_digests"]
    current = {c["case_id"]: c for c in cases if isinstance(c, dict) and isinstance(c.get("case_id"), str)}
    for cid, digest in sorted(frozen.items()):
        if cid not in current:
            out.append(_finding("freeze_case_missing", cid, "a frozen final case is gone"))
        elif case_digest(current[cid]) != digest:
            out.append(_finding("freeze_case_edited", cid, "a frozen final case was edited"))
    for cid, c in sorted(current.items()):
        g, split = c.get("group_id"), c.get("split")
        if g in groups and split != "final":
            out.append(_finding("freeze_group_moved", cid, f"frozen final group {g} has a case outside the final split"))
        if split == "final" and cid not in frozen:
            out.append(_finding("freeze_group_added" if g not in groups else "freeze_case_added", cid,
                                "a final case was added after the freeze"))
    return out


# --------------------------------------------------------------------------------------------
# prompt-example leakage and coverage
# --------------------------------------------------------------------------------------------
def prompt_example_findings(cases, examples, threshold: float = NEAR_DUPLICATE_THRESHOLD) -> list[dict]:
    """A final case's query or acceptable claim, exactly or nearly, inside a prompt/few-shot example."""
    out = []
    for c in cases:
        if not (isinstance(c, dict) and c.get("split") == "final"):
            continue
        texts = [c.get("query", "")] + [t for t in c.get("acceptable_claims", []) if isinstance(t, str)]
        for text in texts:
            if any(isinstance(e, str) and text and similarity(text, e) >= threshold for e in examples):
                out.append(_finding("final_text_in_prompt_example", str(c.get("case_id")),
                                    "final-case text appears in a prompt example"))
                break
    return out


def coverage(cases, registry=None) -> dict:
    """Counts of valid, source-resolved, verified final cases against the targets."""
    _, clean = _case_problems(cases, registry)
    ok = [c for i, c in enumerate(cases) if i in clean and c["status"] == "verified" and c["split"] == "final"]
    taglish = [c for c in ok if c["language"] == "taglish"]
    by_cat = {cat: sum(c["category"] == cat for c in taglish) for cat in CATEGORIES}
    met = len(taglish) >= TARGET_TAGLISH_TOTAL and all(n >= TARGET_PER_CATEGORY for n in by_cat.values())
    detail = ", ".join(f"{cat} {n}/{TARGET_PER_CATEGORY}" for cat, n in by_cat.items())
    line = (f"{'MET' if met else 'NOT MET'}: {len(ok)} verified final cases, {len(taglish)} Taglish "
            f"(target {TARGET_TAGLISH_TOTAL} Taglish, >= {TARGET_PER_CATEGORY} per category: {detail})")
    return {"met": met, "status_line": line, "verified_final_total": len(ok),
            "verified_final_taglish_total": len(taglish), "verified_final_taglish_by_category": by_cat,
            "targets": {"per_category": TARGET_PER_CATEGORY, "taglish_total": TARGET_TAGLISH_TOTAL}}


def coverage_claim_findings(cases, claim, registry=None) -> list[dict]:
    """A claimed coverage report must agree, key by key, with the recomputed one."""
    actual = coverage(cases, registry)
    if not (isinstance(claim, dict) and "met" in claim):
        return [_finding("coverage_claim_false", "coverage", "a coverage claim is an object with a 'met' key")]
    wrong = sorted(k for k, v in claim.items() if k in actual and actual[k] != v)
    if wrong:
        return [_finding("coverage_claim_false", "coverage",
                         f"claimed {wrong} disagree with the data: {actual['status_line']}")]
    return []


# --------------------------------------------------------------------------------------------
# the set check
# --------------------------------------------------------------------------------------------
def validate_case_set(cases, *, registry=None, freeze=None, prompt_examples=(), coverage_claim=None,
                      threshold: float = NEAR_DUPLICATE_THRESHOLD, salt: str = SPLIT_SALT,
                      final_percent: int = FINAL_PERCENT) -> dict:
    cases = list(cases)
    findings, clean = _case_problems(cases, registry)
    ids: dict[str, int] = {}
    for c in cases:
        cid = c.get("case_id") if isinstance(c, dict) else None
        if isinstance(cid, str):
            ids[cid] = ids.get(cid, 0) + 1
    findings += [_finding("duplicate_case_id", cid, f"case_id used {n} times") for cid, n in sorted(ids.items()) if n > 1]

    valid = [c for c in cases if _structurally_valid(c)]
    splits_of: dict[str, set[str]] = {}
    cats_of: dict[str, set[str]] = {}
    for c in valid:
        splits_of.setdefault(c["group_id"], set()).add(c["split"])
        cats_of.setdefault(c["group_id"], set()).add(c["category"])
        if c["split"] != derive_split(c["group_id"], salt, final_percent):
            findings.append(_finding("split_not_derived", c["case_id"],
                                     f"group {c['group_id']} derives to {derive_split(c['group_id'], salt, final_percent)}, case says {c['split']}"))
    for g, s in sorted(splits_of.items()):
        if len(s) > 1:
            findings.append(_finding("group_split_leak", g, "one group appears in both dev and final"))
    for g, s in sorted(cats_of.items()):
        if len(s) > 1:
            findings.append(_finding("group_mixed_category", g, f"one scenario family spans categories {sorted(s)}"))

    # ponytail: O(n^2) pairwise scan; fine for hundreds of cases, add a token index if sets grow past ~5k.
    by_id = sorted(valid, key=lambda c: c["case_id"])
    for i, a in enumerate(by_id):
        for b in by_id[i + 1:]:
            if a["group_id"] != b["group_id"] and similarity(a["query"], b["query"]) >= threshold:
                findings.append(_finding("near_duplicate_group_mismatch", f"{a['case_id']}|{b['case_id']}",
                                         "near-duplicate queries sit in different groups"))
    if freeze is not None:
        findings += _freeze_findings(cases, freeze, salt)
    findings += prompt_example_findings(valid, list(prompt_examples), threshold)
    if coverage_claim is not None:
        findings += coverage_claim_findings(cases, coverage_claim, registry)
    findings.sort(key=lambda f: (f["code"], f["subject"], f["detail"]))
    split_counts = {s: sum(1 for c in valid if c["split"] == s) for s in ("dev", "final")}
    return {"schema_version": REPORT_VERSION, "integrity_ok": not findings, "case_count": len(cases),
            "group_count": len(splits_of), "split_counts": split_counts, "findings": findings,
            "coverage": coverage(cases, registry)}


def _structurally_valid(case) -> bool:
    return not case_findings(case)
