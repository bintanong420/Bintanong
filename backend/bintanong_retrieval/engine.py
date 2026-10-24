"""Runtime-only retrieval orchestration with explicit gaps and release binding."""
from dataclasses import asdict

from backend.bintanong_storage.client import StorageError
from .context import build_context
from .query import EncoderUnavailable, configuration_identity, validate_vector
from .types import RetrievalSettings
from .evidence_policy import SourceAwareEvidencePolicy, PolicyBindingError


def _source_issue(candidates, scope):
    all_clauses=[clause for row in candidates for clause in [row]+row.get('neighbors',[])]
    curricula={tag for row in all_clauses for tag in row['chunk'].get('scope',[]) if tag.startswith('curriculum:')}
    by_document={}
    for row in all_clauses:
        chunk=row['chunk']
        by_document.setdefault(chunk['document_id'],set()).add(chunk['byte_sha256'])
    if len(curricula)>1 and not any(s.startswith('curriculum:') for s in scope):
        return 'needs_scope','multiple_curriculum_versions'
    if any(len(hashes)>1 for hashes in by_document.values()):
        return 'conflicting_sources','multiple_source_editions'
    return None


class RetrievalEngine:
    def __init__(self, client, encoder, settings=None, *, evidence_policy=None):
        if evidence_policy is not None and not isinstance(evidence_policy, SourceAwareEvidencePolicy):
            raise ValueError('prepared source-aware evidence policy required')
        self.client, self.encoder = client, encoder
        self.settings = settings or RetrievalSettings()
        self.evidence_policy = evidence_policy

    def retrieve(self, request, *, subject_id=None, requested_claims=None):
        config=configuration_identity(self.encoder.config)
        response=dict(schema_version='bintanong-retrieval-debug-v1',release_id=request.release_id,
            status='insufficient_evidence',coverage='none',evidence=[],context='',context_tokens=0,gaps=[],
            configuration=asdict(self.settings)|{'fingerprint':self.settings.fingerprint,
                'embedding':config,'score_metric':'cosine_similarity','scores_are_probabilities':False},
            scope=list(request.scope),entity_hints=list(request.entity_hints))
        if self.evidence_policy is not None:
            response.update(schema_version='bintanong-retrieval-debug-v2',candidate_only=True,
                activation_eligible=False,runtime_authorization_verified=False,
                answer_sufficiency='unassessed',evidence_policy=self.evidence_policy._metadata())
        def fail(status, reason=None):
            response['status']=status
            response['gaps'].append(reason or status)
            if 'evidence_policy' in response and response['evidence_policy']['assessment'] is None:
                response['evidence_policy']['not_run_reason']=reason or status
            return response
        try:
            if self.evidence_policy is not None:
                self.evidence_policy._validate_intent(subject_id,requested_claims)
                response['evidence_policy'].update(subject_id=subject_id,
                    requested_claims=None if requested_claims is None else list(requested_claims))
            elif subject_id is not None or requested_claims is not None:
                return fail('invalid_query','evidence_policy_required_for_intent')
            releases=self.client.select('knowledge_releases',filters={'release_id':'eq.'+request.release_id},role='runtime')
            if len(releases)!=1:
                return fail('release_changed')
            sets=self.client.select('embedding_sets',filters={'embedding_set_id':'eq.'+releases[0]['embedding_set_id']},role='runtime')
            keys=set(config)-{'max_context_length'}
            if len(sets)!=1 or any(sets[0].get(key)!=config[key] for key in keys):
                return fail('configuration_mismatch')
            vector=self.encoder.encode(request.query)
            validate_vector(vector)
            params=dict(p_release_id=request.release_id,p_config=config,
                query_embedding=list(vector),p_top_k=self.settings.top_k,p_min_similarity=self.settings.min_similarity,
                p_scope=list(request.scope),p_entity_hints=list(request.entity_hints),
                p_version_ids=list(request.document_version_ids))
            if self.evidence_policy is not None and subject_id is not None:
                params['p_chunk_ids']=self.evidence_policy._chunk_ids(subject_id)
            raw=self.client.rpc('retrieve_context',params,role='runtime')
            if raw.get('status')!='ok':
                return fail(raw.get('status','storage_error'))
            if raw.get('release_id')!=request.release_id:
                return fail('release_changed')
            if self.evidence_policy is not None:
                return self._retrieve_source_aware(request,raw,response,fail,subject_id,requested_claims)
            response['embedding_set_id']=raw['embedding_set_id']
            candidates=raw['items']
            response.update(build_context(candidates,self.settings.context_budget,self.encoder.count_context_tokens))
        except EncoderUnavailable as exc:
            return fail('encoder_unavailable',str(exc))
        except PolicyBindingError as exc:
            response.update(evidence=[],context='',context_tokens=0,coverage='none')
            return fail('policy_binding_error',str(exc))
        except ValueError as exc:
            return fail('invalid_query',str(exc))
        except StorageError:
            return fail('storage_error')
        if not response['evidence']:
            return fail('insufficient_evidence','no_complete_relevant_evidence')
        response['coverage']='partial'
        # Examine all ranked evidence, including clauses omitted for budget. Ranking
        # cannot adjudicate competing source editions or curriculum applicability.
        issue=_source_issue(candidates,request.scope)
        if issue:
            return fail(*issue)
        if response['gaps']:
            return fail('insufficient_evidence','incomplete_context')
        if self.settings.policy_id.startswith('uncalibrated'):
            return fail('uncalibrated','development_calibration_pending')
        response.update(status='ok',coverage='sufficient')
        return response

    def _retrieve_source_aware(self,request,raw,response,fail,subject_id,requested_claims):
        policy=self.evidence_policy
        policy._bind(request.release_id,raw)
        response['embedding_set_id']=raw['embedding_set_id']
        candidates=raw['items']
        issue=_source_issue(candidates,request.scope)
        if issue:
            return fail(*issue)
        if subject_id is None:
            return fail('needs_subject','subject_hint_required')
        if not policy._has_subject(subject_id):
            return fail('insufficient_evidence','subject_unavailable')
        if not requested_claims:
            return fail('needs_claims','requested_claims_required')
        selected=policy._select(candidates,subject_id)
        response.update(build_context(selected,self.settings.context_budget,self.encoder.count_context_tokens,
            shared_citations=True,shared_group_metadata=True))
        response['coverage']='partial' if response['evidence'] else 'none'
        report=policy._assess(subject_id,requested_claims,[e['chunk_id'] for e in response['evidence']],
                              emitted_evidence=response['evidence'])
        response['evidence_policy'].update(assessment=report,not_run_reason=None)
        if report['status']=='insufficient_evidence':
            return fail('insufficient_evidence','requested_claim_not_established')
        if not response['evidence']:
            return fail('insufficient_evidence','no_complete_relevant_evidence')
        if response['gaps'] or report['status']=='insufficient_context':
            return fail('insufficient_evidence','incomplete_context')
        if report['status']=='unassessed':
            return fail('unassessed','requested_claim_unassessed')
        return fail('uncalibrated','development_calibration_pending')
