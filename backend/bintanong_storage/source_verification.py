"""Record scoped V1 observations of existing reviewed spans, never office authority."""
import copy
import re

from backend.bintanong_contracts.base import parse_timestamp
from backend.bintanong_contracts.governance import Evidence, SourceDocumentVersion, evidence_authorizes
from .client import SupabaseStorageClient


_OBSERVATION={'receipt_format','version_id','source_sha256','acquisition_locators',
    'partial_review_evidence_id','review_scope_id','observation_scope','evidence',
    'reviewer_label','compiler_label','timestamp_meaning'}


class SourceVerificationLoader:
    def __init__(self,client=None):
        self.client=client or SupabaseStorageClient()

    def observe(self,current,observation):
        current=SourceDocumentVersion.parse(current.model_dump(mode='json')
            if isinstance(current,SourceDocumentVersion) else current).model_dump(mode='json')
        if (any(current[k]['state']!=state for k,state in (
                ('acquisition_state','verified'),('verification_state','pending'),
                ('content_review_state','partially_reviewed'),('approval_state','not_requested')))
                or current['approval_id'] is not None):
            raise ValueError('V1 requires verified acquisition, partial content review and no source verification/approval')
        if not isinstance(observation,dict) or set(observation)!=_OBSERVATION:
            raise ValueError('Closed selected-source observation required')
        observation=copy.deepcopy(observation)
        if (observation['receipt_format']!='selected-source-observation-v1'
                or observation['observation_scope']!='selected_reviewed_spans'
                or observation['version_id']!=current['version_id']
                or observation['source_sha256']!=current['byte_sha256']
                or observation['acquisition_locators']!=current['acquisition_locators']
                or observation['partial_review_evidence_id']!=current['content_review_state']['evidence_ref']):
            raise ValueError('Exact selected C1/source observation binding required')
        for key in ('partial_review_evidence_id','reviewer_label','compiler_label','timestamp_meaning'):
            if not isinstance(observation[key],str) or not observation[key].strip():
                raise ValueError('Nonblank source-observation references and labels required')
        if not isinstance(observation['review_scope_id'],str) or not re.fullmatch('[0-9a-f]{64}',observation['review_scope_id']):
            raise ValueError('Exact selected-review scope identity required')
        evidence=Evidence.model_validate(observation['evidence'])
        prior=next(e for e in current['evidence'] if e['evidence_id']==current['content_review_state']['evidence_ref'])
        if (not evidence.evidence_id.strip() or evidence.recorded_by!='reviewer'
                or not evidence_authorizes('verification_state','observed',evidence,'pending')
                or any(e['evidence_id']==evidence.evidence_id for e in current['evidence'])
                or parse_timestamp(evidence.recorded_at)<parse_timestamp(prior['recorded_at'])):
            raise ValueError('Distinct V1 reviewer evidence no earlier than C1 required')
        observation['evidence']=evidence.model_dump(mode='json')
        proposed=copy.deepcopy(current)
        proposed['verification_state']=dict(state='observed',evidence_ref=evidence.evidence_id)
        proposed['evidence'].append(observation['evidence'])
        expected=SourceDocumentVersion.parse(proposed)
        result=self.client.rpc('observe_source_verification',dict(
            p_expected_register=current,p_observation=observation),role='admin')
        stored=SourceDocumentVersion.parse(result)
        if stored!=expected:
            raise ValueError('Stored source observation differs from expected record')
        return stored
