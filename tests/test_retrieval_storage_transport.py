"""Composed HTTP storage failures with synthetic requests and no external I/O."""
import unittest

import httpx

from backend.bintanong_retrieval.engine import RetrievalEngine
from backend.bintanong_retrieval.evidence_policy import SourceAwareEvidencePolicy
from backend.bintanong_retrieval.query import configuration_identity
from backend.bintanong_retrieval.types import RetrievalRequest
from backend.bintanong_storage.client import SupabaseStorageClient
from backend.bintanong_storage.config import StorageConfig
from tests.test_retrieval_engine import Encoder
from tests.test_retrieval_evidence_policy import policy_fixture


class RetrievalStorageTransportTests(unittest.TestCase):
    def test_each_runtime_request_failure_returns_storage_error_without_evidence(self):
        for source_aware in (False, True):
            for stage in (1, 2, 3):
                for error in (httpx.ConnectError, httpx.ReadTimeout):
                    with self.subTest(source_aware=source_aware, stage=stage, error=error.__name__):
                        encoder = Encoder()
                        inputs, _ = policy_fixture()
                        policy = SourceAwareEvidencePolicy(**inputs) if source_aware else None
                        with SupabaseStorageClient(StorageConfig(
                            'https://storage.invalid', 'synthetic-runtime', 'synthetic-admin', 'unused'
                        )) as client:
                            requests = []

                            def respond(request):
                                requests.append(request)
                                if len(requests) == stage:
                                    raise error('synthetic-private-transport-details', request=request)
                                if request.url.path.endswith('/knowledge_releases'):
                                    return httpx.Response(200, json=[dict(release_id='release-test', embedding_set_id='set')])
                                if request.url.path.endswith('/embedding_sets'):
                                    return httpx.Response(200, json=[dict(embedding_set_id='set', **configuration_identity(encoder.config))])
                                self.fail('unexpected request before the injected transport error')

                            client._http.close()
                            client._http = httpx.Client(transport=httpx.MockTransport(respond))
                            engine = RetrievalEngine(client, encoder, evidence_policy=policy)
                            intent = dict(subject_id='fees', requested_claims=('printed amount',)) if source_aware else {}
                            out = engine.retrieve(RetrievalRequest('Synthetic question', 'release-test'), **intent)

                            self.assertEqual(out['status'], 'storage_error')
                            self.assertEqual(out['gaps'], ['storage_error'])
                            self.assertEqual(out['evidence'], [])
                            self.assertEqual(out['context'], '')
                            self.assertEqual(out['coverage'], 'none')
                            self.assertEqual(encoder.calls, int(stage == 3))
                            self.assertEqual(len(requests), stage)
                            for request in requests:
                                self.assertEqual(request.headers['apikey'], 'synthetic-runtime')
                                self.assertEqual(request.headers['authorization'], 'Bearer synthetic-runtime')
                            if source_aware:
                                self.assertIsNone(out['evidence_policy']['assessment'])
                                self.assertEqual(out['evidence_policy']['not_run_reason'], 'storage_error')
                                self.assertIs(out['candidate_only'], True)
                                self.assertIs(out['activation_eligible'], False)
                                self.assertIs(out['runtime_authorization_verified'], False)
                                self.assertEqual(out['answer_sufficiency'], 'unassessed')
