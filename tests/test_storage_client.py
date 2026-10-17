import json
import unittest
from unittest.mock import patch
import httpx
from backend.bintanong_storage.client import SupabaseStorageClient, PermissionDeniedError, StorageError
from backend.bintanong_storage.config import StorageConfig


class TestSupabaseStorageClient(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.response = httpx.Response(200, json=[])
        self.transport_error = None
        self.client = SupabaseStorageClient(StorageConfig('https://storage.invalid', 'test-runtime', 'test-admin', 'unused'))
        self.client._http.close()
        self.client._http = httpx.Client(transport=httpx.MockTransport(self.handle))
        self.addCleanup(self.client.close)

    def handle(self, request):
        self.requests.append(request)
        if self.transport_error is not None:
            raise self.transport_error('synthetic-private-transport-details', request=request)
        return self.response

    def test_runtime_read_and_rpc_default_to_runtime_credentials(self):
        self.client.select('chunks', filters={'chunk_id': 'eq.example'})
        self.client.rpc('match_chunks', {'match_count': 2})
        for request in self.requests:
            self.assertEqual(request.headers['apikey'], 'test-runtime')
            self.assertEqual(request.headers['authorization'], 'Bearer test-runtime')
        self.assertEqual(self.requests[0].url.params['chunk_id'], 'eq.example')
        self.assertEqual(json.loads(self.requests[1].content), {'match_count': 2})

    def test_admin_rpc_and_mutation_request_shapes(self):
        self.response = httpx.Response(204)
        self.client.rpc('load_chunk_batch', {'p_chunks': [], 'p_spans': []}, role='admin')
        self.client.upsert('chunks', {'chunk_id': 'example'}, on_conflict='chunk_id')
        self.client.delete('documents', {'document_id': 'eq.example'})
        self.client.insert('documents', {'document_id': 'example'})
        for request in self.requests:
            self.assertEqual(request.headers['apikey'], 'test-admin')
        self.assertEqual(json.loads(self.requests[0].content), {'p_chunks': [], 'p_spans': []})
        self.assertEqual(self.requests[1].url.params['on_conflict'], 'chunk_id')
        self.assertIn('resolution=merge-duplicates', self.requests[1].headers['prefer'])
        self.assertEqual(json.loads(self.requests[3].content), [{'document_id': 'example'}])

    def test_permission_and_other_errors_are_distinct(self):
        for status, payload in [(401, {}), (403, {}), (400, {'code': '42501'})]:
            self.response = httpx.Response(status, json=payload)
            with self.subTest(status=status), self.assertRaises(PermissionDeniedError):
                self.client.rpc('activate_knowledge_release', role='runtime')
        self.response = httpx.Response(400, json={'code': '23514', 'message': 'Incomplete release'})
        with self.assertRaisesRegex(StorageError, 'Incomplete release'):
            self.client.rpc('activate_knowledge_release', role='admin')

    def test_transport_failures_use_storage_error_without_retrying_any_operation(self):
        operations = (
            lambda: self.client.select('chunks'),
            lambda: self.client.rpc('retrieve_context'),
            lambda: self.client.insert('documents', {'document_id': 'synthetic'}),
            lambda: self.client.upsert('documents', {'document_id': 'synthetic'}),
            lambda: self.client.delete('documents', {'document_id': 'eq.synthetic'}),
        )
        for error in (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError):
            for index, operation in enumerate(operations):
                with self.subTest(error=error.__name__, operation=index):
                    self.transport_error = error
                    before = len(self.requests)
                    with self.assertRaises(StorageError) as caught:
                        operation()
                    self.assertIsInstance(caught.exception.__cause__, error)
                    self.assertIsNone(caught.exception.status_code)
                    self.assertIsNone(caught.exception.details)
                    self.assertNotIn('synthetic-private', str(caught.exception))
                    self.assertEqual(len(self.requests), before + 1)

    def test_non_request_programming_errors_are_not_wrapped(self):
        with patch.object(self.client._http, 'request', side_effect=ValueError('synthetic programming error')):
            with self.assertRaisesRegex(ValueError, 'synthetic programming error'):
                self.client.select('chunks')


if __name__ == '__main__':
    unittest.main()
