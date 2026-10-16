"""Persist only an evidence-bound A1 acquisition observation, never approval."""
import copy

from backend.bintanong_contracts.base import VOCAB
from backend.bintanong_contracts.governance import Evidence, SourceDocumentVersion, STATE_FIELDS, evidence_authorizes
from .client import SupabaseStorageClient


class SourceAcquisitionLoader:
    def __init__(self, client=None):
        self.client = client or SupabaseStorageClient()

    def observe(self, current, check):
        current = SourceDocumentVersion.parse(current.model_dump(mode='json')
            if isinstance(current, SourceDocumentVersion) else current).model_dump(mode='json')
        if (any(current[k]['state'] != VOCAB['initial_states'][k] for k in STATE_FIELDS)
                or current['approval_id'] is not None):
            raise ValueError('A1 requires initial source lifecycle states')
        if not isinstance(check, dict) or set(check) != {
                'version_id', 'source_sha256', 'acquisition_locators', 'evidence'}:
            raise ValueError('Exact source-bound byte-check envelope required')
        check = copy.deepcopy(check)
        if (check['version_id'] != current['version_id'] or check['source_sha256'] != current['byte_sha256']
                or check['acquisition_locators'] != current['acquisition_locators']):
            raise ValueError('Byte-check source identity/hash/locators must match')
        evidence = Evidence.model_validate(check['evidence'])
        if (not evidence.evidence_id.strip()
                or not evidence_authorizes('acquisition_state', 'observed', evidence, 'pending')
                or any(e['evidence_id'] == evidence.evidence_id for e in current['evidence'])):
            raise ValueError('Distinct A1 byte-check evidence required')
        check['evidence'] = evidence.model_dump(mode='json')
        proposed = copy.deepcopy(current)
        proposed['evidence'].append(check['evidence'])
        proposed['acquisition_state'] = dict(state='observed', evidence_ref=evidence.evidence_id)
        expected = SourceDocumentVersion.parse(proposed)
        result = self.client.rpc('observe_source_acquisition',
            dict(p_expected_register=current, p_check=check), role='admin')
        observed = SourceDocumentVersion.parse(result)
        if observed != expected:
            raise ValueError('Stored acquisition observation differs from the expected record')
        return observed
