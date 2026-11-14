"""Strict local-only SEA-LION query execution. No legacy synthetic fallback."""
import hashlib
import json
import math
import os
from pathlib import Path

from backend.bintanong_embedding.adapter import EmbeddingConfig, SeaLionEmbeddingAdapter


class EncoderUnavailable(RuntimeError):
    pass


def configuration_identity(config: EmbeddingConfig) -> dict:
    return {name: getattr(config, name) for name in (
        'model_id', 'model_revision', 'dimension', 'normalization',
        'prompt_fingerprint', 'preprocessing_fingerprint', 'tokenizer_fingerprint',
        'max_context_length',
    )}


def validate_vector(vector):
    if len(vector) != 1024 or any(not math.isfinite(v) for v in vector):
        raise ValueError('query vector must have 1024 finite dimensions')
    if not math.isclose(math.sqrt(sum(v*v for v in vector)), 1.0, abs_tol=1e-6):
        raise ValueError('query vector must be l2 normalized')


class QueryEncoder(SeaLionEmbeddingAdapter):
    def __init__(self, config=None, model_path=None, asset_digests=None):
        super().__init__(config=config, model_path=model_path)
        self.asset_digests = dict(asset_digests or {})

    def load_model(self):
        if self._model is not None:
            return self._model
        root = Path(os.environ.get('MODELS_DIR', 'C:/Coding-projects/MODELS')).resolve()
        path = self.model_path.resolve()
        if not path.is_relative_to(root) or not path.is_dir():
            raise EncoderUnavailable('model must exist below MODELS_DIR')
        required = {'model.safetensors', 'tokenizer.json', 'tokenizer_config.json',
                    'config.json', 'config_sentence_transformers.json', 'modules.json',
                    'sentence_bert_config.json', 'special_tokens_map.json', '1_Pooling/config.json'}
        if not required.issubset(self.asset_digests):
            raise EncoderUnavailable('verified asset manifest is required')
        for name, expected in self.asset_digests.items():
            asset = (path/name).resolve()
            if not asset.is_relative_to(path) or not asset.is_file():
                raise EncoderUnavailable(f'missing or invalid model asset: {name}')
            with asset.open('rb') as stream:
                actual = hashlib.file_digest(stream, 'sha256').hexdigest()
            if actual != expected:
                raise EncoderUnavailable(f'model asset digest mismatch: {name}')
        if self.asset_digests['model.safetensors'] != self.config.model_revision:
            raise EncoderUnavailable('local weights do not match the pinned model revision')
        model_config = json.loads((path/'config_sentence_transformers.json').read_text())
        if model_config['prompts']['Retrieval'] != self.config.query_prompt:
            raise EncoderUnavailable('query prompt does not match local Retrieval configuration')
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(str(path), device='cpu', local_files_only=True)
        except Exception as exc:
            raise EncoderUnavailable(f'local encoder unavailable: {exc}') from exc
        if self._model.max_seq_length != self.config.max_context_length:
            self._model = None
            raise EncoderUnavailable('local context length differs from pinned configuration')
        return self._model

    def encode(self, query: str):
        if not query.strip():
            raise ValueError('query must not be empty')
        model = self.load_model()
        text = self.config.query_prompt + query
        if len(model.tokenizer.encode(text, add_special_tokens=True, truncation=False)) > self.config.max_context_length:
            raise ValueError('query exceeds the encoder context; truncation is forbidden')
        vector = tuple(float(v) for v in model.encode([text], prompt='', normalize_embeddings=True)[0])
        validate_vector(vector)
        return vector

    def count_context_tokens(self, text: str) -> int:
        return len(self.load_model().tokenizer.encode(text, add_special_tokens=True, truncation=False))
