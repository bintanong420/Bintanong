"""Shared setup for the memory/eligibility gates (plans/2026-11-03-memory-eligibility-results.md).

Environment (no machine paths are stored in the repository):
- BINTANONG_RESEARCH_CONFIG: the hosted research API config JSON (as for `research_app.load_research_app`).
- BINTANONG_LEDGER_CACHE: an ignored directory for the release's reviewed ledgers. When it holds no `roster.json`,
  ledgers are read once, read-only, with SUPABASE_URL/SUPABASE_ANON_KEY and cached there.
- The live gates also need the Gemma server named by the config's `model_url` to be running.

Documents are not retrievable through this harness (no encoder), so only structured questions are asked. Timings
are warm backend turn times only (no browser, network, queueing or Supabase).
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from functools import cached_property
from pathlib import Path

from backend.bintanong_api import research_app
from backend.bintanong_api.chat import ChatRequest, ChatTurns, CurriculumOption
from backend.bintanong_api.presentation import student_text
from backend.bintanong_api.session import ApiError, Session


def _required(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f'set {name} (see evaluation/memory_eligibility/README.md)')
    return value


class Harness:
    def __init__(self):
        self.config = research_app.ResearchApiConfig.model_validate_json(
            Path(_required('BINTANONG_RESEARCH_CONFIG')).read_text(encoding='utf-8'))
        self.cache = Path(_required('BINTANONG_LEDGER_CACHE'))

    @cached_property
    def pin_and_package(self):
        return research_app._package(self.config)

    @cached_property
    def ledgers(self):
        roster = self.cache / 'roster.json'
        if not roster.exists():
            from backend.bintanong_runtime.hosted_curricula import load_release_curricula
            from backend.bintanong_storage.client import StorageConfig, SupabaseStorageClient
            pin, _ = self.pin_and_package
            client = SupabaseStorageClient(StorageConfig(api_url=_required('SUPABASE_URL'),
                anon_key=_required('SUPABASE_ANON_KEY'), service_role_key='', db_url=''))
            loaded = load_release_curricula(client, release_id=pin['release_id'],
                                            authorization_ref=pin['research_authorization_ref'])
            self.cache.mkdir(parents=True, exist_ok=True)
            for curriculum, ledger in loaded.items():
                (self.cache / f'{curriculum}.json').write_text(json.dumps(ledger), encoding='utf-8')
            roster.write_text(json.dumps(sorted(loaded)), encoding='utf-8')
        return {c: json.loads((self.cache / f'{c}.json').read_text(encoding='utf-8'))
                for c in json.loads(roster.read_text(encoding='utf-8'))}

    @cached_property
    def resources(self):
        from backend.bintanong_runtime.research import build_multi_research_resources
        pin, package = self.pin_and_package
        return build_multi_research_resources(self.ledgers, package, encoder=object(),
            authorization_ref=pin['research_authorization_ref'], program_names=self.config.program_names,
            curriculum_names=self.config.curriculum_names, routing_context=True)

    @cached_property
    def turns(self):
        from backend.bintanong_api.research_pipeline import ResearchPipeline
        from backend.bintanong_generation.generator import Generator
        from backend.bintanong_orchestration.ports import SyntheticReleaseProvider
        from backend.bintanong_private_context.sessions import SessionStore
        from backend.bintanong_routing.transport import LlamaTransport
        pipeline = ResearchPipeline(lambda: LlamaTransport(self.config.model_url, prefix_cache=True),
            SyntheticReleaseProvider(self.resources), topic_selection=True,
            generator_factory=lambda model: Generator(model, reference_profile='short', review_reference_profile='short'))
        self.store = SessionStore()
        curricula = tuple(CurriculumOption(l['scope']['program_id'], c, c, c) for c, l in sorted(self.ledgers.items()))
        return ChatTurns(self.store, pipeline, curricula, course_labels=dict(self.resources.course_labels))

    def chat(self):
        """A fresh chat; returns ask(text, curriculum) -> result dict for each turn."""
        turns = self.turns
        issued = self.store.issue()

        def ask(text, curriculum):
            program = self.ledgers[curriculum]['scope']['program_id']
            request = ChatRequest.model_validate(dict(messages=[dict(id=f'm-{time.time_ns()}', role='user',
                parts=[dict(type='text', text=text)])], programId=program, curriculumId=curriculum))
            started = time.monotonic()
            try:
                answer = asyncio.run(turns.answer(Session(issued.credential, self.store.resolve(issued.credential)),
                                                  request))
                result = dict(status=answer.status, outcome=answer.decision.outcome if answer.decision else None,
                              reply=student_text(answer), explanation_check=answer.explanation_check,
                              explanation_errors=list(answer.explanation_errors))
            except ApiError as error:
                result = dict(status=f'error {error.code}', outcome=None, reply='', explanation_check=None,
                              explanation_errors=[])
            result['seconds'] = round(time.monotonic() - started, 1)
            view = self.store.resolve(issued.credential)
            result['remembered'] = [(f.course_id, f.state) for f in view.facts]
            return result
        return ask


def write(out: Path, name: str, rows):
    out.mkdir(parents=True, exist_ok=True)
    path = out / f'{name}-{int(time.time())}.json'
    path.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding='utf-8')
    return path


def first_line(reply):
    return (reply.splitlines() or [''])[0]
