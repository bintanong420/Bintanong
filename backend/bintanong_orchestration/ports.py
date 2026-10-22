"""Dependency boundaries and explicit synthetic release injection."""
from dataclasses import dataclass
from typing import Protocol

from ..bintanong_contracts.runtime import PredicateRequest
from ..bintanong_contracts.symbolic import CapabilityRegistry, SymbolicResult
from ..bintanong_retrieval.types import RetrievalRequest
from ..bintanong_routing.contracts import CatalogEntry, RequestContext
from ..bintanong_symbolic.runtime import DependencyResult
from .contracts import DocumentResult, ReleasePin


class RetrievalPort(Protocol):
    async def retrieve(self, request: RetrievalRequest) -> DocumentResult: ...


class SymbolicPort(Protocol):
    release_id: str
    rule_bundle_version: str

    async def execute(self, request: PredicateRequest, context: RequestContext
                      ) -> SymbolicResult | DependencyResult: ...


@dataclass(frozen=True)
class ReleaseResources:
    pin: ReleasePin
    catalog: tuple[CatalogEntry, ...]
    registry: CapabilityRegistry
    retrieval: RetrievalPort | None = None
    symbolic: SymbolicPort | None = None

    def __post_init__(self):
        object.__setattr__(self, 'pin', ReleasePin.parse(self.pin.model_dump(mode='json')))
        object.__setattr__(self, 'catalog', tuple(CatalogEntry.parse(c.model_dump(mode='json'))
                                                 for c in self.catalog))
        versions = {s.version_id for s in self.pin.sources}
        if any(c.source_ref not in versions for c in self.catalog):
            raise ValueError('catalog_source_outside_release')
        if self.symbolic is not None and (self.symbolic.release_id != self.pin.release_id
                or self.symbolic.rule_bundle_version != self.pin.rule_bundle_version):
            raise ValueError('symbolic_runtime_outside_release')


class ReleaseProvider(Protocol):
    async def pin(self) -> ReleaseResources: ...


class ReleaseUnavailable(RuntimeError):
    pass


class HeldReleaseProvider:
    async def pin(self) -> ReleaseResources:
        raise ReleaseUnavailable('institutional_release_held')


@dataclass(frozen=True)
class SyntheticReleaseProvider:
    resources: ReleaseResources

    async def pin(self) -> ReleaseResources:
        return self.resources
