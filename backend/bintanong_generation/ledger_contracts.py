"""Shared ledger records;model support and canonical witnesses remain distinct."""
from typing import Annotated, Literal
from pydantic import Field, model_validator
from ..bintanong_contracts.base import Contract, Record

PartID = Annotated[str, Field(pattern=r'^r[1-8]$')]
ClaimID = Annotated[str, Field(pattern=r'^c[1-8]$')]
Digest = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]


class ReviewIdentity(Contract):
    SCHEMA_VERSION = 'bintanong-part-review-identity-v1'
    requirements_sha256: Digest
    draft_sha256: Digest


class LedgerEntry(Record):
    part_id: PartID
    status: Literal['mapped', 'missing', 'unavailable', 'uncertain', 'unresolved']
    claim_ids: tuple[ClaimID, ...] = Field(default=(), max_length=8)
    reason: Literal['not_in_evidence', 'source_gap', 'structured_check_not_run', 'uncertain',
                    'missing_mapping', 'unknown_requirement_kind'] | None = None


class RequirementLedger(Contract):
    SCHEMA_VERSION = 'bintanong-requirement-ledger-v1'
    candidate_only: Literal[True] = True
    institutional_use_allowed: Literal[False] = False
    activation_allowed: Literal[False] = False
    semantic_completeness: Literal['unverified'] = 'unverified'
    status: Literal['all_declared_parts_mapped', 'unresolved']
    identity: ReviewIdentity
    entries: tuple[LedgerEntry, ...] = Field(min_length=1, max_length=8)
    errors: tuple[Literal['incomplete_support_verdicts', 'unsupported_claim', 'language_unsupported',
                          'scope_unsupported', 'unmapped_claim'], ...] = ()


class BoundRequirementLedger(RequirementLedger):
    SCHEMA_VERSION = 'bintanong-bound-requirement-ledger-v1'
    canonical_parts: tuple[PartID, ...] = Field(max_length=8)

    @model_validator(mode='after')
    def _canonical(self):
        ids = {e.part_id for e in self.entries}
        if len(ids) != len(self.entries) or len(set(self.canonical_parts)) != len(self.canonical_parts):
            raise ValueError('duplicate_ledger_part')
        if not set(self.canonical_parts) <= ids:
            raise ValueError('unknown_canonical_part')
        for entry in self.entries:
            if entry.part_id in self.canonical_parts:
                if entry.status != 'mapped' or entry.claim_ids or entry.reason is not None:
                    raise ValueError('invalid_canonical_witness')
            elif entry.status == 'mapped' and not entry.claim_ids:
                raise ValueError('document_mapping_needs_claim')
        complete = not self.errors and all(e.status == 'mapped' for e in self.entries)
        if (self.status == 'all_declared_parts_mapped') != complete:
            raise ValueError('ledger_status_mismatch')
        return self
