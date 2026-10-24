"""Append cumulative selected-field evidence without changing the source register."""
import copy
import json

from backend.bintanong_contracts.governance import SourceDocumentVersion
from .client import SupabaseStorageClient
from .source_partial_review import _validate_receipt


class SourceSupplementaryReviewLoader:
    def __init__(self, client=None):
        self.client = client or SupabaseStorageClient()

    def record(self, current, receipt, *, base_evidence_id):
        current = SourceDocumentVersion.parse(current.model_dump(mode='json')
            if isinstance(current, SourceDocumentVersion) else current).model_dump(mode='json')
        if current['content_review_state']['state'] != 'partially_reviewed':
            raise ValueError('Existing partial source review required')
        if not isinstance(base_evidence_id, str) or not base_evidence_id.strip():
            raise ValueError('Explicit base partial-review evidence required')
        receipt = copy.deepcopy(receipt)
        evidence = _validate_receipt(current, receipt)
        if base_evidence_id == evidence.evidence_id:
            raise ValueError('Distinct supplementary evidence required')
        try:
            json.dumps(receipt, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError('JSON supplementary review receipt required') from exc
        stored = self.client.rpc('record_source_supplementary_review', dict(
            p_expected_register=current, p_receipt=receipt,
            p_base_evidence_id=base_evidence_id), role='admin')
        if stored != receipt:
            raise ValueError('Stored supplementary review differs from the expected receipt')
        return copy.deepcopy(stored)
