import unittest
from backend.bintanong_embedding.adapter import EmbeddingConfig
from backend.bintanong_retrieval.engine import RetrievalEngine
from backend.bintanong_retrieval.query import configuration_identity, EncoderUnavailable
from backend.bintanong_retrieval.types import RetrievalRequest, RetrievalSettings
from tests.test_retrieval_context import evidence


class Encoder:
    config = EmbeddingConfig()
    calls = 0
    def encode(self, query):
        self.calls += 1
        return [1.0]+[0.0]*1023
    def count_context_tokens(self, text):
        return len(text)


class Client:
    def close(self):
        pass
    def __init__(self):
        self.config = configuration_identity(EmbeddingConfig())
        self.payload = dict(status='ok', release_id='release-test',embedding_config=self.config,
                            embedding_set_id='set',items=[evidence()])
        self.roles = []
    def select(self, table, **kwargs):
        self.roles.append(kwargs['role'])
        return [dict(embedding_set_id='set',**self.config)]
    def rpc(self, name, params=None, role=None):
        self.roles.append(role)
        self.params = params
        return self.payload


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.client, self.encoder = Client(), Encoder()
        self.engine = RetrievalEngine(self.client,self.encoder,RetrievalSettings(context_budget=1000))
        self.request = RetrievalRequest('hello','release-test')

    def test_runtime_only_source_linked_response_and_fingerprints(self):
        out = self.engine.retrieve(self.request)
        self.assertEqual(out['status'], 'uncalibrated')
        self.assertEqual(out['schema_version'],'bintanong-retrieval-debug-v1')
        self.assertEqual(out['release_id'],'release-test')
        self.assertEqual(out['coverage'],'partial')
        self.assertTrue(all(role=='runtime' for role in self.client.roles))
        self.assertEqual(self.client.params['p_scope'], [])
        self.assertEqual(out['configuration']['fingerprint'],self.engine.settings.fingerprint)
        self.assertTrue(out['evidence'][0]['citations'])

    def test_configuration_checked_before_embedding(self):
        self.client.config['prompt_fingerprint'] = '0'*64
        out = self.engine.retrieve(self.request)
        self.assertEqual(out['status'],'configuration_mismatch')
        self.assertEqual(self.encoder.calls,0)

    def test_stale_snapshot_and_empty_candidates_do_not_leak_evidence(self):
        self.client.payload['status']='release_changed'
        out = self.engine.retrieve(self.request)
        self.assertEqual(out['evidence'],[])
        self.assertEqual(out['status'],'release_changed')
        self.client.payload.update(status='ok', items=[])
        out = self.engine.retrieve(self.request)
        self.assertEqual(out['status'],'insufficient_evidence')
        self.assertEqual(out['coverage'],'none')

    def test_conflicting_editions_and_curriculum_ambiguity_are_preserved(self):
        second = evidence('b','Other edition',page=2)
        second['chunk'].update(version_id='version2',edition_id='edition2',byte_sha256='1'*64)
        second['version'].update(version_id='version2',byte_sha256='1'*64)
        second['spans'][0].update(version_id='version2',byte_sha256='1'*64)
        self.client.payload['items'].append(second)
        out = self.engine.retrieve(self.request)
        self.assertEqual(out['status'],'conflicting_sources')
        self.assertEqual(len(out['evidence']),2)
        self.client.payload['items'][0]['chunk']['scope']=['curriculum:v1']
        second['chunk']['scope']=['curriculum:v2']
        self.assertEqual(self.engine.retrieve(self.request)['status'],'needs_scope')

    def test_model_unavailable_returns_explicit_failure(self):
        def unavailable(query):
            raise EncoderUnavailable('missing')
        self.encoder.encode=unavailable
        out=self.engine.retrieve(self.request)
        self.assertEqual(out['status'],'encoder_unavailable')
        self.assertEqual(out['evidence'],[])

    def test_required_neighbor_curriculum_ambiguity_is_not_hidden(self):
        main=self.client.payload['items'][0]
        neighbor=evidence('b','Exception',page=2)
        main['chunk']['scope']=['curriculum:one']
        neighbor['chunk']['scope']=['curriculum:two']
        main['chunk']['type_fields']['required_neighbor_chunk_ids']=['b']
        main['neighbors']=[neighbor]
        out=self.engine.retrieve(self.request)
        self.assertEqual(out['status'],'needs_scope')


if __name__ == '__main__':
    unittest.main()
