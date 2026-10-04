"""Keeps the extractor's audit, content review, and source verification as separate states.

Nothing here approves anything. Content review is "pending" unless a decision ledger for
the same PDF says otherwise, and source verification is whatever the source record carries
(always "pending" for ProvisionalSource), so eligibility_executable is False for every
payload the extractor produces today.
"""

from __future__ import annotations

from typing import Any
from typing import Mapping
from typing import Sequence

from .prerequisites import EXECUTABLE_PREREQUISITE_STATES
from .text import clean_str


# The only value that counts as a verified source; a source record that says anything else blocks.
VERIFIED_SOURCE = "verified"


# The metadata fields that can identify a prospectus. Anything else in an approved scope is unknown.
IDENTITY_FIELDS = ("campus", "college_code", "program_name", "effective_school_year")


def _has_evidence(observation: Mapping[str, Any] | None) -> bool:
    """An observation the extractor read from the document or path, not one it assumed."""
    observation = observation or {}
    return bool(observation.get("basis")) and observation.get("basis") != "extractor_default" and bool(
        observation.get("evidence")
    )


def check_identity(
    metadata: Mapping[str, Any], approved_scope: Mapping[str, str] | None
) -> dict[str, Any]:
    """Compare observed metadata with an approved identity, when one was supplied.

    consistent needs every approved field to be a known identity field with a non-empty value, backed
    by an observation with evidence, and equal. A difference is a mismatch. Unknown keys, empty values,
    assumed or unevidenced observations, and an empty scope never confirm an identity."""
    if not approved_scope:
        return {"state": "pending", "approved_scope": None, "mismatched_fields": [], "unverified_fields": []}
    observations = metadata.get("observations") or {}
    mismatched: list[str] = []
    unverified: list[str] = []
    for name, wanted in approved_scope.items():
        wanted_text = clean_str(wanted)
        if name not in IDENTITY_FIELDS or not wanted_text:
            unverified.append(name)
        elif not clean_str(metadata.get(name)):
            unverified.append(name)  # nothing was observed to compare with
        elif wanted_text.casefold() != clean_str(metadata.get(name)).casefold():
            mismatched.append(name)
        elif not _has_evidence(observations.get(name)):
            unverified.append(name)
    state = "mismatch" if mismatched else "unverified" if unverified else "consistent"
    return {
        "state": state,
        "approved_scope": dict(approved_scope),
        "mismatched_fields": mismatched,
        "unverified_fields": unverified,
    }

def build_authority(
    *,
    audit_status: str,
    metadata: Mapping[str, Any],
    courses: Sequence[Mapping[str, Any]],
    source: Any = None,
    approved_scope: Mapping[str, str] | None = None,
    pdf_hash_check: str = "not_checked",
    content_review: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """The three status fields plus the `authority` block, ready to merge into a payload.

    `source` is duck-typed (pdf_sha256, source_locator, source_verification) so the
    package does not import the tools adapter that defines ProvisionalSource.
    `content_review` is the result of ledger.content_review_state, or None when no
    decision ledger was supplied (the state is then "pending").
    """
    identity = check_identity(metadata, approved_scope)
    verification = getattr(source, "source_verification", "pending")
    if not isinstance(verification, str):
        verification = "unknown"
    review_state = content_review["state"] if content_review else "pending"
    record = None
    if source is not None:
        record = {
            "pdf_sha256": source.pdf_sha256,
            "source_locator": source.source_locator,
            "pdf_hash_check": pdf_hash_check,
        }

    blocked: list[str] = []
    if audit_status == "error":
        blocked.append("extraction_audit_error")
    if review_state == "pending":
        blocked.append("content_review_pending")
    elif review_state != "reviewed":
        blocked.append("content_review_incomplete")
    if verification == "pending":
        blocked.append("source_verification_pending")
    elif verification != VERIFIED_SOURCE:
        blocked.append("source_not_verified")
    if pdf_hash_check != "matched":
        blocked.append("pdf_hash_not_checked")
    if identity["state"] == "pending":
        blocked.append("identity_pending")
    elif identity["state"] == "mismatch":
        blocked.append("identity_mismatch")
    elif identity["state"] == "unverified":
        blocked.append("identity_unverified")
    incomplete = [
        item for item in courses if item.get("prerequisite_state") not in EXECUTABLE_PREREQUISITE_STATES
    ]
    if incomplete:
        blocked.append("prerequisite_rules_incomplete")

    return {
        "extraction_audit": audit_status,
        "content_review": review_state,
        "source_verification": verification,
        "authority": {
            "source_record": record,
            "identity_check": identity,
            "content_review_detail": dict(content_review) if content_review else None,
            "eligibility_executable": not blocked,
            "blocked_by": blocked,
            "courses_with_incomplete_prerequisite_rule": len(incomplete),
            "note": (
                "audit.promotion_status is a legacy extractor label, not approval of the curriculum, "
                "the source, or any eligibility result. Read extraction_audit, content_review and "
                "source_verification."
            ),
        },
    }
