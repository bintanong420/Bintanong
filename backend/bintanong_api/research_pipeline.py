"""The chat port (`run(text, context, *, routed_sink, progress)`) over the real answer path.

Same composition the counted roster and multi-turn harnesses use: one model transport per request shared by
routing and generation, the Orchestrator for routing and evidence, then AnswerPipeline/Generator for the validated
answer. Release resources (hosted research release, encoder, Prolog) are built by the trusted launcher; nothing
here reads data paths, keys or request-supplied configuration.
"""
from __future__ import annotations

from backend.bintanong_generation.generator import AnswerPipeline, Generator
from backend.bintanong_orchestration.orchestrator import Orchestrator


class ResearchPipeline:
    def __init__(self, transport_factory, releases, *, generator_factory=None, stage_timeout=120.0,
                 generation_timeout=120.0, request_timeout=180.0):
        self._transport_factory, self._releases = transport_factory, releases
        self._generator_factory = generator_factory or (lambda model: Generator(model,
                                                                                timeout_seconds=generation_timeout))
        self._stage_timeout, self._request_timeout = stage_timeout, request_timeout

    async def run(self, text, context, *, routed_sink, progress):
        model = self._transport_factory()
        orchestrator = Orchestrator(model, releases=self._releases, stage_timeout=self._stage_timeout)

        class Staged:  # progress is reported around the evidence stage; the answer text is never streamed
            async def run(self, text, context):
                progress('understanding')
                integration = await orchestrator.run(text, context, routed_sink=routed_sink)
                progress('writing')
                return integration

        pipeline = AnswerPipeline(Staged(), self._generator_factory(model), timeout_seconds=self._request_timeout)
        return await pipeline.run(text, context)
