"""One observable LLM proposal, validation, and at most one format repair."""
from __future__ import annotations

import json
from dataclasses import replace

from pydantic import ValidationError

from ..bintanong_contracts.runtime import NormalizedQuery
from ..bintanong_contracts.symbolic import EMPTY_REGISTRY
from .contracts import Interpretation, RequestContext, prepare_query
from .prompt import build_messages, output_schema
from .transport import RuntimeFailure
from .validation import RoutingResult, _decision, anchor_unique_quotes, validate_interpretation


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate_json_key')
        result[key] = value
    return result


class Router:
    def __init__(self, transport, *, catalog=(), registry=EMPTY_REGISTRY,
                 documents_available=False, synthetic=False):
        self.transport = transport
        self.catalog = tuple(catalog)
        self.registry = registry
        self.documents_available = documents_available
        self.synthetic = synthetic

    async def route(self, text: str, context: RequestContext) -> RoutingResult:
        normalized = prepare_query(text)
        context = RequestContext.parse(context.model_dump(mode='json'))
        messages = build_messages(text, context, self.catalog, self.registry)
        proposed = None

        def failure(code, attempts):
            query = NormalizedQuery(schema_version=NormalizedQuery.SCHEMA_VERSION,
                original_text=text, normalized_text=normalized, language_hints=(), intent=None,
                entities=(), ambiguities=(), negations=(), time_qualifiers=(),
                session_fact_refs=tuple(f.fact_id for f in context.facts))
            return RoutingResult(query, _decision(control='evidence_unavailable', reason=code),
                proposed, (), proposed.language if proposed else 'unknown', code, attempts)

        for attempt in (1, 2):
            try:
                raw = await self.transport.infer(messages, output_schema())
            except RuntimeFailure as error:
                return failure(str(error), attempt)
            try:
                if not isinstance(raw, str) or len(raw.encode('utf-8')) > 65536:
                    raise ValueError('invalid_output_size')
                data = json.loads(raw, object_pairs_hook=_unique_object)
                data, offset_corrections = anchor_unique_quotes(data, text)
                proposed = Interpretation.parse(data)
            except (ValueError, ValidationError):
                if attempt == 2:
                    return failure('invalid_model_output', attempt)
                messages = [*messages, dict(role='assistant', content=raw[:65536]),
                    dict(role='user', content='This is a formatting repair, not a new student question. '
                         'Return valid JSON matching the original schema for the ORIGINAL student request '
                         'in the payload below. Correct formatting only; preserve its meaning and facts.\n'
                         + messages[1]['content'])]
                continue
            try:
                result = validate_interpretation(text, context, proposed, catalog=self.catalog,
                    registry=self.registry, documents_available=self.documents_available,
                    synthetic=self.synthetic)
                return replace(result, attempts=attempt, offset_corrections=offset_corrections)
            except ValueError:
                return failure('invalid_grounding', attempt)
        raise AssertionError('unreachable')
