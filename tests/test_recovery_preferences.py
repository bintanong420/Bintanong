"""Recovery preference reaches the existing planner without changing its default."""
import pytest

from backend.bintanong_orchestration.adapters import SymbolicAdapter
from test_generation_recovery_reply import run, clarify_with_failure, RECOVERY_TEXT
from test_planning_recovery import CURRICULA
from test_routing_contracts import proposal


@pytest.mark.parametrize('preference,expected', [
    ('as soon as possible', True), ('the fastest way', True), ('the earliest return', True),
    ('pinakamabilis makabalik', True), ('makabalik agad', True),
    ('fewer special-class requests', False), ('not necessarily the fastest', False),
])
def test_chat_passes_explicit_recovery_preference(monkeypatch, preference, expected):
    observed = []

    async def recover(self, *args, **kwargs):
        observed.append(kwargs.get('fastest_asked', False))
        return None

    monkeypatch.setattr(SymbolicAdapter, 'recover', recover)
    text = RECOVERY_TEXT.replace('ako agad?', 'ako?') + ' ' + preference
    integration, _ = run(text, clarify_with_failure(text))
    assert integration.evidence.dependencies is not None
    assert observed == [expected]


@pytest.mark.parametrize('curriculum', CURRICULA)
def test_fastest_preference_keeps_each_selected_curriculum(monkeypatch, curriculum):
    observed = []

    async def recover(self, request, context, *args, **kwargs):
        observed.append((context.curriculum_id, kwargs['fastest_asked']))
        return None

    monkeypatch.setattr(SymbolicAdapter, 'recover', recover)
    code = CURRICULA[curriculum]['X']
    text = f'Bagsak ako sa {code}, how can I recover as soon as possible?'
    start = text.index(code)
    value = proposal(text=text, language='en', route='Symbolic',
        mentions=[dict(kind='course', text=code, start=start, end=start + len(code))],
        operations=[dict(name='list_affected_courses', target=0)],
        claims=[dict(text=text[:start + len(code)], start=0, end=start + len(code),
                     entity=0, state='failed', mode='asserted')])
    run(text, value, language='en', curriculum=curriculum)
    assert observed == [(curriculum, True)]

