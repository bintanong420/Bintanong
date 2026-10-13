"""Runtime-only retrieval orchestration with explicit gaps and release binding."""
from dataclasses import asdict

from backend.bintanong_storage.client import StorageError
from .context import build_context
from .query import EncoderUnavailable, configuration_identity, validate_vector
from .types import RetrievalSettings


class RetrievalEngine:
    def __init__(self, client, encoder, settings=None):
        self.client, self.encoder = client, encoder
        self.settings = settings or RetrievalSettings()

    def retrieve(self, request):
        config=configuration_identity(self.encoder.config)
        response=dict(schema_version='bintanong-retrieval-debug-v1',release_id=request.release_id,
            status='insufficient_evidence',coverage='none',evidence=[],context='',context_tokens=0,gaps=[],
            configuration=asdict(self.settings)|{'fingerprint':self.settings.fingerprint,
                'embedding':config,'score_metric':'cosine_similarity','scores_are_probabilities':False},
            scope=list(request.scope),entity_hints=list(request.entity_hints))
        def fail(status, reason=None):
            response['status']=status
            response['gaps'].append(reason or status)
            return response
        try:
            releases=self.client.select('knowledge_releases',filters={'release_id':'eq.'+request.release_id},role='runtime')
            if len(releases)!=1:
                return fail('release_changed')
            sets=self.client.select('embedding_sets',filters={'embedding_set_id':'eq.'+releases[0]['embedding_set_id']},role='runtime')
            keys=set(config)-{'max_context_length'}
            if len(sets)!=1 or any(sets[0].get(key)!=config[key] for key in keys):
                return fail('configuration_mismatch')
            vector=self.encoder.encode(request.query)
            validate_vector(vector)
            raw=self.client.rpc('retrieve_context',dict(p_release_id=request.release_id,p_config=config,
                query_embedding=list(vector),p_top_k=self.settings.top_k,p_min_similarity=self.settings.min_similarity,
                p_scope=list(request.scope),p_entity_hints=list(request.entity_hints),
                p_version_ids=list(request.document_version_ids)),role='runtime')
            if raw.get('status')!='ok':
                return fail(raw.get('status','storage_error'))
            if raw.get('release_id')!=request.release_id:
                return fail('release_changed')
            response['embedding_set_id']=raw['embedding_set_id']
            candidates=raw['items']
            response.update(build_context(candidates,self.settings.context_budget,self.encoder.count_context_tokens))
        except EncoderUnavailable as exc:
            return fail('encoder_unavailable',str(exc))
        except ValueError as exc:
            return fail('invalid_query',str(exc))
        except StorageError:
            return fail('storage_error')
        if not response['evidence']:
            return fail('insufficient_evidence','no_complete_relevant_evidence')
        response['coverage']='partial'
        # Examine all ranked evidence, including clauses omitted for budget. Ranking
        # cannot adjudicate competing source editions or curriculum applicability.
        all_clauses=[clause for row in candidates for clause in [row]+row.get('neighbors',[])]
        curricula={tag for row in all_clauses for tag in row['chunk'].get('scope',[]) if tag.startswith('curriculum:')}
        by_document={}
        for row in all_clauses:
            chunk=row['chunk']
            by_document.setdefault(chunk['document_id'],set()).add(chunk['byte_sha256'])
        if len(curricula)>1 and not any(s.startswith('curriculum:') for s in request.scope):
            return fail('needs_scope','multiple_curriculum_versions')
        if any(len(hashes)>1 for hashes in by_document.values()):
            return fail('conflicting_sources','multiple_source_editions')
        if response['gaps']:
            return fail('insufficient_evidence','incomplete_context')
        if self.settings.policy_id.startswith('uncalibrated'):
            return fail('uncalibrated','development_calibration_pending')
        response.update(status='ok',coverage='sufficient')
        return response
