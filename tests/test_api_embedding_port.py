import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.bintanong_embedding.adapter import EmbeddingConfig
from backend.bintanong_embedding.query_api import query_router
from backend.bintanong_retrieval.http_query import HttpQueryEncoder
from backend.bintanong_retrieval.query import EncoderUnavailable, configuration_identity

IDENTITY = configuration_identity(EmbeddingConfig())
VECTOR = [1.0] + [0.0] * 1023


def transport(query=None, metadata=None, count=42):
    def handler(request):
        if request.url.path == '/query/configuration':
            return httpx.Response(200, json=IDENTITY if metadata is None else metadata)
        if request.url.path == '/query':
            return httpx.Response(200, json={'configuration': IDENTITY, 'vector': VECTOR if query is None else query})
        assert request.url.path == '/query/token-count'
        return httpx.Response(200, json={'configuration': IDENTITY, 'count': count})
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_strict_http_encoder_checks_identity_and_vectors_without_generic_encode_fallback():
    with transport() as client:
        encoder = HttpQueryEncoder('http://embedding.test', client=client)
        assert encoder.encode('A question 🙂') == tuple(VECTOR)
        assert encoder.count_context_tokens('Source context') == 42


def test_mismatched_embedding_identity_refuses_startup():
    with transport(metadata={**IDENTITY, 'model_revision': 'wrong'}) as client:
        with pytest.raises(EncoderUnavailable): HttpQueryEncoder('http://embedding.test', client=client)


@pytest.mark.parametrize('vector', [[1.0], [0.0] * 1024, [True] + [0.0] * 1023, ['1'] + [0.0] * 1023])
def test_untrusted_vector_shapes_types_and_normalization_are_refused(vector):
    with transport(query=vector) as client:
        encoder = HttpQueryEncoder('http://embedding.test', client=client)
        with pytest.raises(EncoderUnavailable): encoder.encode('Question')


@pytest.mark.parametrize('count', [True, -1, '42'])
def test_token_count_requires_an_actual_nonnegative_integer(count):
    with transport(count=count) as client:
        encoder = HttpQueryEncoder('http://embedding.test', client=client)
        with pytest.raises(EncoderUnavailable): encoder.count_context_tokens('Context')


def test_response_byte_cap_is_not_taken_from_content_length():
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=b'x' * 131073)))
    with client, pytest.raises(EncoderUnavailable): HttpQueryEncoder('http://embedding.test', client=client)


def test_query_service_reuses_strict_encoder_and_sanitizes_failures():
    class Encoder:
        config = EmbeddingConfig()
        def load_model(self): return self
        def encode(self, text):
            if text == 'fail': raise EncoderUnavailable('private path must not leak')
            return VECTOR
        def count_context_tokens(self, text): return 42
    app = FastAPI(); app.include_router(query_router(encoder=Encoder()))
    with TestClient(app) as client:
        assert client.get('/query/configuration').json() == IDENTITY
        assert client.post('/query', json={'text': 'Question'}).json()['vector'] == VECTOR
        assert client.post('/query/token-count', json={'text': 'Context'}).json()['count'] == 42
        response = client.post('/query', json={'text': 'fail'})
        assert response.status_code == 503 and 'private path' not in response.text
        assert client.post('/query', json={'text': 'Question', 'prompt': 'override'}).status_code == 422
