# Quoted-reference router implementation plan

> **For agentic workers:** Use executing-plans inline,focused TDD and one fresh
> whole-change review. No implementer agents or repeated review loops.

**Goal:** move character spans and numeric course-reference construction from the
LLM into a deterministic host normalizer,without weakening semantic/evidence guards.
**Architecture:** a strict quoted-reference wire packet normalizes to existing
Interpretation v2. Selected separate router and explicit combined experiment use
one normalizer;existing orchestration/generation contracts and Prolog stay unchanged.
**Tech stack:** existing Python3.13/Pydantic/pytest;no dependency/runtime changes.
**Spec:** [approved design](2026-10-20-router-correction-diagnosis-and-design.md).
Owner20October2026:"ye i approve";inline implementation continues without another
plan-approval pause. Conditional-grade execution remains excluded and pending.

## Global constraints

- Phase09 only;undergraduate/read-only,RAG+reviewed structured Prolog,all release holds.
- Wire bintanong-interpretation-wire-v1;normalized Interpretation v2 unchanged.
- Quotes {text,occurrence};exact original text,zero-based overlapping occurrences.
- At most32mentions/claims,4operations,8parts;existing route/control/part rules.
- No invented/fuzzy quotes or first-occurrence fallback;no source/session IDs.
- Shared one routing repair,separate style,answer repair/deadlines remain unchanged.
- No reasoning-budget/model/seed/cache changes,extra classifier or inference sweep.
- Prior55observation/10research seals and accepted75institutional variants unchanged.
- No new inference here;software success does not establish semantic accuracy/latency.
- System Python3.13,-B,pytest no cache,workspace TEMP/TMP/basetemp;explicit staging.

## Review focus

- Repeated/overlapping quote text resolves its declared occurrence,never guesses.
- Reordered mentions cannot change a quoted target's identity or fact entity.
- Missing/foreign/non-course targets and claim/part containment reject before dispatch.
- Asserted/hypothetical/reported modes retain their existing dispatch boundaries.
- Separate/combined malformed packets retain their shared repair and call limits.

## Task1 - strict wire contract and normalizer

Files:create backend/bintanong_routing/wire.py and tests/test_routing_wire.py.
Interface:WireInterpretation.parse(data);normalize_interpretation(text,wire)->Interpretation.
QuoteReference(text,occurrence) uses text length1-4096,occurrence0-8191;the original
question limit bounds practical matches. Booleans/string occurrences reject strictly.
Wire mentions/claims/operations/parts preserve existing semantic field limits;
normalize exact quoted identities to existing mention indices and original spans.

- [x] Write literal synthetic regressions for target/fact identity after mention
  reordering,repeated/overlapping text,invalid occurrence/type,duplicate references,
  invented/non-course targets,claim and structured-part containment and mode retention.
- [x] Run focused pytest;observe expected missing-module/implementation RED:15fail0.72s.
- [x] Implement minimal models and normalization;reuse Interpretation v2 validators.
- [x] Run focused GREEN plus normalized routing contracts/validation:58pass0.59s.

## Task2 - connect model boundary and migrate fixtures

Files:modify backend/bintanong_routing/{prompt,router,combined}.py and routing README;
tests/test_routing_wire.py,tests/test_routing_router.py,tests/test_routing_combined.py,
tests/test_prompt_schema_display.py and necessary runtime model fixtures.
Create tests/routing_wire_fixtures.py only if shared fixture migration warrants it.
Interface:prompt.output_schema exposes wire contract;routers normalize before the
existing host interpretation validator. Combined packet/version references wire;
no legacy model-wire fallback. Host normalized-contract fixtures stay v2.

- [ ] Add RED:wire schema contains no spans/numeric course target;actual routers
  accept literal wire packets,share bounded repair and reject legacy/foreign refs.
- [ ] Integrate both routers and new prompt identity. One short fictional role
  contrast only;retain scope/mode/injection guards and separate requested details.
- [ ] Migrate model-output fixtures explicitly;never call production normalization
  to manufacture expected answers. Keep independent literal wire regressions.
- [ ] Run relevant routing,combined,prompt-schema,orchestration and generation
  regressions;inspect all failures,correct migration errors,rerun affected gate.
- [ ] One fresh whole-change review;one correction pass with RED/GREEN if needed.
- [ ] Verify code/prompt/schema bindings,prior seals,docs/phase/local links;commit
  compact results/progress/checkpoint. No further review/inference sweep.

## Delivery

Record exact commands/results and source hashes in ignored workspace audit-evidence/
p09-router-wire-20261020/. Keep current snapshots compact. Phase09 remains active;
next actual-model experiment needs a separately frozen protocol,including resolution
of conditional-reference expectations. No semantic improvement or speedup claimed
from tests,representation changes or fewer fields alone.
