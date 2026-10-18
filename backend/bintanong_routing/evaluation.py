"""Synthetic offline development evaluation; gold labels never enter router prompts."""
from __future__ import annotations

import argparse
import asyncio
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, model_validator

from ..bintanong_contracts.base import Record, VOCAB
from ..bintanong_contracts.symbolic import Capability, CapabilityRegistry
from .contracts import CatalogEntry, RequestContext, prepare_query
from .prompt import PROMPT_SHA256, PROMPT_VERSION, digest, output_schema
from .router import Router
from .transport import LlamaTransport
from .validation import OPERATIONS, _matches


class DevelopmentCase(Record):
    case_id: str = Field(min_length=1, max_length=128)
    family_id: str = Field(min_length=1, max_length=128)
    split: Literal['dev']
    synthetic: Literal[True]
    synthetic_policy: str = Field(min_length=1, max_length=2048)
    text: str
    language: Literal['en', 'fil', 'taglish']
    context: RequestContext
    expected: str
    expected_effective: str | None = None
    expected_entities: tuple[str, ...]
    expected_claims: tuple[str, ...]
    expected_operations: tuple[str, ...]
    expected_style: Literal['en', 'fil', 'taglish']

    @model_validator(mode='after')
    def _valid(self):
        prepare_query(self.text)
        if self.expected not in (*VOCAB['runtime']['routes'], *VOCAB['runtime']['controls']):
            raise ValueError('invalid_expected_label')
        if self.expected_effective is not None and self.expected_effective not in (
                *VOCAB['runtime']['routes'], *VOCAB['runtime']['controls']):
            raise ValueError('invalid_expected_effective_label')
        return self


Digest = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]


class RunMetadata(Record):
    model_sha256: Digest
    runtime_image_digest: Digest
    code_commit: str = Field(pattern=r'^[0-9a-f]{40}$')
    evaluation_kind: Literal['mock', 'synthetic_model']


async def evaluate_cases(router, cases, metadata, *, progress=None):
    cases = tuple(DevelopmentCase.parse(c.model_dump(mode='json') if isinstance(c, DevelopmentCase) else c)
                  for c in cases)
    metadata = RunMetadata.parse(metadata).model_dump(mode='json')
    if not cases or len({c.case_id for c in cases}) != len(cases):
        raise ValueError('empty_or_duplicate_cases')
    families = defaultdict(list)
    for c in cases:
        families[c.family_id].append(c)
    for family in families.values():
        gold = {(c.expected, tuple(sorted(c.expected_entities)), tuple(sorted(c.expected_claims)),
                 tuple(sorted(c.expected_operations))) for c in family}
        if len(gold) != 1:
            raise ValueError('inconsistent_family_labels')
    proposal_matrix, effective_matrix = defaultdict(Counter), defaultdict(Counter)
    diagnostics, per_language = Counter(), defaultdict(Counter)
    records = []
    for c in cases:
        started = time.monotonic()
        result = await router.route(c.text, c.context)  # no expected labels passed
        raw = result.proposed
        proposed = (raw.route or raw.control) if raw else 'invalid'
        effective = result.decision.route or result.decision.control
        entities = tuple(sorted(e.value for e in result.query.entities))
        claims = tuple(sorted(f'{f.course_id}:{f.state}:{f.mode}' for f in result.claims))
        operations = []
        if raw:
            for op in raw.operations:
                matches = (_matches(raw.mentions[op.target], router.catalog, result.program_id,
                    result.curriculum_id) if result.program_id and result.curriculum_id else ())
                target = matches[0].entity_id if len(matches) == 1 else 'unresolved'
                operations.append(f'{op.name}:{result.curriculum_id or "unresolved"}:{target}')
        operations = tuple(sorted(operations))
        expected_effective = c.expected_effective or c.expected
        row = dict(case_id=c.case_id, family_id=c.family_id, language=c.language,
            expected=c.expected, expected_effective=expected_effective, proposed=proposed, effective=effective,
            proposal_correct=proposed == c.expected, effective_correct=effective == expected_effective,
            entity_correct=entities == tuple(sorted(c.expected_entities)),
            claim_correct=claims == tuple(sorted(c.expected_claims)),
            operation_correct=operations == tuple(sorted(c.expected_operations)),
            style_correct=result.response_style == c.expected_style,
            diagnostic=result.diagnostic, attempts=result.attempts,
            entities=entities, claims=claims, operations=operations, response_style=result.response_style,
            seconds=time.monotonic() - started,
            interpretation=raw.model_dump(mode='json') if raw else None)
        records.append(row)
        proposal_matrix[c.expected][proposed] += 1
        effective_matrix[expected_effective][effective] += 1
        diagnostics[result.diagnostic] += 1
        lang = per_language[c.language]
        lang['total'] += 1
        for key in ('proposal_correct', 'effective_correct', 'entity_correct', 'claim_correct',
                    'operation_correct', 'style_correct'):
            lang[key] += int(row[key])
        if progress:
            progress(dict(case_id=c.case_id, proposed=proposed, effective=effective,
                          diagnostic=result.diagnostic, seconds=row['seconds']))
    family_signatures = defaultdict(list)
    for r in records:
        family_signatures[r['family_id']].append((r['proposed'], r['entities'], r['claims'], r['operations']))
    compared = [values for values in family_signatures.values() if len(values) > 1]
    report = dict(schema_version='bintanong-routing-evaluation-v1', total=len(cases),
        metadata=metadata, prompt_version=PROMPT_VERSION, prompt_sha256=PROMPT_SHA256,
        schema_sha256=digest(output_schema()), case_set_sha256=digest([c.model_dump(mode='json') for c in cases]),
        catalog_sha256=digest([c.model_dump(mode='json') for c in router.catalog]),
        runtime=dict(getattr(router.transport, 'metadata', {})),
        proposal_matrix={k:dict(v) for k,v in proposal_matrix.items()},
        effective_matrix={k:dict(v) for k,v in effective_matrix.items()},
        diagnostics=dict(diagnostics), per_language={k:dict(v) for k,v in per_language.items()},
        family_compared=len(compared),
        family_consistent=sum(len(set(v)) == 1 and v[0][0] != 'invalid' for v in compared),
        repair_attempts=sum(r['attempts'] - 1 for r in records), records=records,
        institutional_approval=False, activation_allowed=False)
    for key in ('proposal_correct', 'effective_correct', 'entity_correct', 'claim_correct',
                'operation_correct', 'style_correct'):
        report[key] = sum(r[key] for r in records)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Synthetic dev cases, catalog and run metadata JSON')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--evidence-root', type=Path,
        default=Path('C:/Coding-projects/bintanong_workspace/audit-evidence'))
    parser.add_argument('--url', default='http://127.0.0.1:18087')
    parser.add_argument('--timeout', type=float, default=120)
    parser.add_argument('--plain-json', action='store_true', help='Explicitly disable schema decoding; still validate')
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(args.evidence_root.resolve()):
        parser.error('output must stay in the ignored evidence root')
    data = json.loads(args.input.read_text(encoding='utf-8-sig'))
    registry = CapabilityRegistry({name:Capability('synthetic_' + name,
        ('curriculum_id','course_id')) for name in OPERATIONS})
    router = Router(LlamaTransport(args.url, timeout_seconds=args.timeout,
        constrained=not args.plain_json), catalog=tuple(CatalogEntry.parse(c) for c in data['catalog']),
        registry=registry, documents_available=True, synthetic=True)
    report = asyncio.run(evaluate_cases(router, data['cases'], data['metadata'],
        progress=lambda row: print(json.dumps(row), flush=True)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('total','proposal_correct','entity_correct','claim_correct','style_correct')}))


if __name__ == '__main__':
    main()
