"""Internal retrieval request and configuration; scope is supplied by a trusted caller."""
from dataclasses import asdict, dataclass
import hashlib
import json
import math


@dataclass(frozen=True)
class RetrievalRequest:
    query: str
    release_id: str
    scope: tuple[str, ...] = ()
    entity_hints: tuple[str, ...] = ()
    document_version_ids: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.query, str) or not self.query.strip() or len(self.query) > 16000:
            raise ValueError('query must contain 1..16000 characters')
        if not isinstance(self.release_id, str) or not self.release_id.strip():
            raise ValueError('release_id must be pinned')
        for name in ('scope', 'entity_hints', 'document_version_ids'):
            values = getattr(self, name)
            if not isinstance(values, tuple) or len(values) > 32 or any(
                not isinstance(v, str) or not v.strip() or len(v) > 256 for v in values
            ):
                raise ValueError(f'{name} must contain at most 32 nonempty canonical values')


@dataclass(frozen=True)
class RetrievalSettings:
    top_k: int = 5
    context_budget: int = 2048
    min_similarity: float = 0.5
    policy_id: str = 'uncalibrated-v1'

    def __post_init__(self):
        if type(self.top_k) is not int or self.top_k not in (3, 5, 8):
            raise ValueError('top_k must be 3, 5 or 8')
        if type(self.context_budget) is not int or not 1 <= self.context_budget <= 32768:
            raise ValueError('context_budget must be 1..32768')
        if not math.isfinite(self.min_similarity) or not -1 <= self.min_similarity <= 1:
            raise ValueError('min_similarity must be finite and within [-1,1]')
        if not self.policy_id:
            raise ValueError('policy_id must be explicit')

    @property
    def fingerprint(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()
