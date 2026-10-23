"""Phase 11 task 9: the chat port over the real answer path (Orchestrator -> AnswerPipeline -> Generator).
Synthetic release and fake model only; the real-data launcher lives in ignored workspace evidence."""
import asyncio

from backend.bintanong_api.research_pipeline import ResearchPipeline
from test_generation_loop import api as generation
from test_generation_pipeline import EchoEvidence
from test_orchestration_pipeline import ctx, ports, resources, transport


def pipeline(route='Hybrid'):
    return ResearchPipeline(lambda: transport(route), ports().SyntheticReleaseProvider(resources()),
                            generator_factory=lambda model: generation().Generator(EchoEvidence(),
                                                                                    explanation_profile='legacy'))


def test_answers_through_the_real_path_and_reports_the_routing_result():
    routed, stages = [], []
    answer = asyncio.run(pipeline().run('A1 policy', ctx(), routed_sink=routed.append, progress=stages.append))
    assert answer.status == 'answered' and answer.validation == 'validated'
    assert len(routed) == 1 and routed[0].diagnostic == 'validated'
    assert stages == ['understanding', 'writing']


def test_each_request_gets_a_fresh_model_transport():
    made = []

    def factory():
        made.append(transport('RAG'))
        return made[-1]
    p = ResearchPipeline(factory, ports().SyntheticReleaseProvider(resources()),
                         generator_factory=lambda model: generation().Generator(EchoEvidence(),
                                                                                 explanation_profile='legacy'))
    for _ in range(2):
        asyncio.run(p.run('A1 policy', ctx(), routed_sink=lambda r: None, progress=lambda s: None))
    assert len(made) == 2 and made[0] is not made[1]
