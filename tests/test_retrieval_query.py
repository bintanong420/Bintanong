import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from backend.bintanong_embedding.adapter import EmbeddingConfig, DEFAULT_QUERY_PROMPT
from backend.bintanong_retrieval.types import RetrievalRequest, RetrievalSettings
from backend.bintanong_retrieval.query import QueryEncoder, EncoderUnavailable, configuration_identity, validate_vector


class QueryTests(unittest.TestCase):
    def test_request_and_settings_refuse_invalid_or_fabricated_scope(self):
        self.assertEqual(RetrievalRequest('hello', 'release-test').scope, ())
        for query in ('', '  ', 'x'*16001):
            with self.assertRaises(ValueError):
                RetrievalRequest(query, 'release-test')
        for kwargs in ({'top_k':4}, {'context_budget':0}, {'min_similarity':math.nan}, {'top_k':True}):
            with self.assertRaises(ValueError):
                RetrievalSettings(**kwargs)
        with self.assertRaises(ValueError):
            RetrievalRequest('hello', 'release-test', scope=(' ',))

    def test_configuration_identity_carries_all_matching_fields(self):
        cfg = EmbeddingConfig()
        identity = configuration_identity(cfg)
        self.assertEqual(identity['prompt_fingerprint'], cfg.prompt_fingerprint)
        self.assertEqual(len(identity), 8)
        self.assertEqual(cfg.query_prompt, DEFAULT_QUERY_PROMPT)

    def test_vector_rejects_dimension_nonfinite_zero_and_nonunit(self):
        validate_vector([1.0]+[0.0]*1023)
        for vector in ([1.0], [0.0]*1024, [2.0]+[0.0]*1023, [math.nan]+[0.0]*1023):
            with self.assertRaises(ValueError):
                validate_vector(vector)

    def test_missing_or_unverified_model_never_falls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict('os.environ', {'MODELS_DIR':directory}):
                encoder = QueryEncoder(model_path=Path(directory)/'missing', asset_digests={})
                with self.assertRaises(EncoderUnavailable):
                    encoder.encode('hello')
                with self.assertRaises(EncoderUnavailable):
                    encoder.count_context_tokens('hello')

    def test_query_prompt_applied_once_and_exact_overflow_refused(self):
        class Tokenizer:
            def encode(self, text, **kwargs):
                return list(range(len(text.split())+2))
        class Model:
            tokenizer = Tokenizer()
            def encode(self, texts, **kwargs):
                self.texts, self.kwargs = texts, kwargs
                return [[1.0]+[0.0]*1023]
        encoder = QueryEncoder()
        model = Model()
        with patch.object(encoder, 'load_model', return_value=model):
            vector = encoder.encode('hello')
            self.assertEqual(len(vector), 1024)
            self.assertEqual(model.texts, [DEFAULT_QUERY_PROMPT+'hello'])
            self.assertEqual(model.kwargs['prompt'], '')
            self.assertEqual(encoder.count_context_tokens('one two'), 4)
            with self.assertRaises(ValueError):
                encoder.encode('word '*512)


if __name__ == '__main__':
    unittest.main()
