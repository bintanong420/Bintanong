"""Prompt reuse is the runtime default (owner, 23 Oct 2026, after run 13) and can be switched off."""
import asyncio

import pytest

from backend.bintanong_runtime.application import RuntimeSettings, RuntimeSpec, build_application
from test_orchestration_pipeline import ctx
from test_runtime_composition import spec, Database


def test_runtime_default_enables_prompt_reuse():
    assert RuntimeSettings().prefix_cache is True
    assert RuntimeSettings(prefix_cache=False).prefix_cache is False
    with pytest.raises(ValueError, match='prefix_cache'):
        RuntimeSettings(prefix_cache='yes')


@pytest.mark.parametrize('enabled', [True, False])
def test_application_builds_its_model_transport_with_the_setting(monkeypatch, enabled):
    import backend.bintanong_runtime.application as module
    original, seen = module.LlamaTransport, []
    def observe(*args, **kwargs):
        seen.append(kwargs.get('prefix_cache'))
        return original(*args, **kwargs)
    monkeypatch.setattr(module, 'LlamaTransport', observe)
    class Held(Database):
        def select(self, *args, **kwargs): return []
    data = spec()
    app = build_application(RuntimeSpec.parse(data), client=Held(data), settings=RuntimeSettings(prefix_cache=enabled))
    asyncio.run(app.run('A1', ctx()))
    assert seen == [enabled]
