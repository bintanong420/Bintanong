"""Strict query/tokenizer port to the resident CPU embedding service."""
import json
import math

import httpx

from backend.bintanong_embedding.adapter import EmbeddingConfig
from .query import EncoderUnavailable, configuration_identity, validate_vector


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate_key')
        result[key] = value
    return result


class HttpQueryEncoder:
    def __init__(self, url, *, config=None, client=None):
        self.config = config or EmbeddingConfig()
        self.url = url.rstrip('/')
        self._owned = client is None
        self.client = client if client is not None else httpx.Client(timeout=15)
        try:
            self._check(self._request('GET', '/query/configuration'))
        except Exception:
            self.close()
            raise

    def close(self):
        if self._owned:
            self.client.close()

    def _request(self, method, path, payload=None):
        try:
            with self.client.stream(method, self.url + path, json=payload) as response:
                if response.status_code != 200:
                    raise ValueError('query_service_unavailable')
                body = bytearray()
                for chunk in response.iter_bytes():
                    if len(body) + len(chunk) > 131072:
                        raise ValueError('query_response_too_large')
                    body.extend(chunk)
                data = json.loads(body, object_pairs_hook=_unique)
                if not isinstance(data, dict):
                    raise ValueError('query_response_object_required')
                return data
        except Exception:
            raise EncoderUnavailable('strict_query_service_unavailable') from None

    def _check(self, configuration):
        if configuration != configuration_identity(self.config):
            raise EncoderUnavailable('query_configuration_mismatch')

    def encode(self, query):
        data = self._request('POST', '/query', {'text': query})
        self._check(data.get('configuration'))
        try:
            vector = data['vector']
            if not isinstance(vector, list) or any(type(v) not in (int, float) or not math.isfinite(v) for v in vector):
                raise ValueError('invalid_vector')
            validate_vector(vector)
            return tuple(float(v) for v in vector)
        except (KeyError, ValueError, TypeError):
            raise EncoderUnavailable('invalid_query_vector') from None

    def count_context_tokens(self, text):
        data = self._request('POST', '/query/token-count', {'text': text})
        self._check(data.get('configuration'))
        count = data.get('count')
        if type(count) is not int or not 0 <= count <= 1_000_000:
            raise EncoderUnavailable('invalid_token_count')
        return count
