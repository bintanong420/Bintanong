---
artifact: phase-handoff
phase: 12
status: complete
plan: plans/phase-12-evaluation-writeup-plan.md
final_commit: 62ecb96
next_phase: 13
completed_at: 2026-10-29T23:38:51+08:00
completion_scope: research/software evaluation write-up with disclosed gaps; participant research not completed; deployment cancelled
---

# Phase 12 final handoff

The frozen evaluation report and hosted 560 research activation are delivered. This closes the planned
research/software write-up milestone, with the limitations below. It does not complete participant research,
establish institutional accuracy, or authorize public deployment. Owner cancelled Phase 13 (29 Oct).

## Exit evidence

| Gate | Evidence | Result |
| --- | --- | --- |
| Frozen benchmark/report with uncertainty and error analysis | [Report](../docs/evaluation/phase12-evaluation-report.md), [results](2026-10-29-phase12-benchmark-results.md) | delivered |
| Numbers traceable to saved outputs | fresh `report-number-verification.json` over existing results.jsonl/statistics | PASS; no new benchmark run |
| Relevant suite evidence | merged `a3ff208`: 7314 pass/1608 subtests, 6 skip/2 xfail, four batch exits 0; `48330f7` related 108 pass | inherited; merge logs re-read |
| Hosted staging/activation/readback | [Activation results](2026-10-30-hosted-560-activation-results.md) | PASS; 560 chunks/vectors, 39 links, existing rows preserved |
| Hosted website smoke | HTTP 3/3 answered with citations; browser smoking penalty + p.93 source panel, 0 console errors/warnings | PASS, single runs |
| Phase artifacts/links | `phase_state.py validate`, `can-advance`, local relative-link check, `git diff --check` | PASS; no deployment authorization |

Full suite evidence: `audit-evidence/merge-p11-into-dev-20261030/{head.txt,batches.exit,batch-00.log,...}`;
counts 2561+1530+1709+1514 = 7314; subtests 227+19+432+930 = 1608. Original frozen report suite
at `0d6ebac`: 7271/1608. Production changes after `a3ff208`: flowchart selected-review migration
(`5739bee`, schema function only; related storage/flow tests 261 pass / 1000 subtests) and the backend
release pin (`48330f7`; related 108 pass). Codex's continuation changed no production code or schema; it used
sealed artifact checks, hosted readbacks, API/browser smoke and documentation checks. Full suite on the final
code `35629a1` (A/../p12-fullsuite-20261029, 4 batches): 2563+1530+1709+1520 = 7322 pass / 1608 subtests,
6 skip / 2 xfail, all four batches exit 0 (an earlier attempt hit a full C: drive and was discarded; the extra
`*.log exit 4` lines are the batch loop matching stale log files, which ran no tests). Lint/build/security
suites were not repeated; no dependency changes. Hosted query validation: [results](2026-10-30-hosted-query-validation-results.md).

## Evaluation delivered

Main v2: 38/50 (76%; English 20/24, Taglish 9/16, Tagalog 9/10). Original paired set: C 40/50,
C rerun 39/50, A strict 3/50/content 8/50; exact McNemar 37/0, p≈1.46e-11 for C versus A strict.
Wilson intervals, category tables, single-run variability, robustness sets and 12 v2 failures are disclosed.
Warm inner latency median 26.4 s; no student-visible SLA. Hosted smoke outer requests 51.0/26.7/49.5 s
are separate single observations, excluding startup/browser. Backend construction 110.88 s.

## Commits and recovery

Report `36ae881`; plan/research `f2b00dc`; dev merge `a3ff208`; hosted flow migration `222d9ab`
(hosted version 20261029145841); backend pin `48330f7`; Codex preflight `acbb0b9`, staged `0b4aef9`,
activated `62ecb96`. Frontmatter final_commit anchors the verified activation milestone; the subsequent
closure commit carries this handoff and the superseded checkpoint. No history rewrite or remote push.

Hosted active: `p12-research-faqsplit-20261030`; corrected78 superseded, retained as rollback.
Ignored evidence `A = audit-evidence/p12-hosted-560-activation-20261030` contains scripts/results/logs.
Backend uses `A/hosted-research-api-config.json` on :8021; frontend runs from p12 on :3216; existing
model container on :18088. Restart via the exact commands in the activation results. Old local-documents
config expects corrected78 and fails after this switch. Rollback: `PY A/hosted.py rollback`, then restore
corrected78 backend config. Do not regenerate receipts/snapshot or edit bound artifacts. .env is never tracked.

## Versions and digests

Python 3.13; Pydantic 2.13.5, HTTPX 0.28.1, pytest 9.1.1, uvicorn 0.53.0. Frontend uses locked Next.js
16.4.3/React 19.3.0; no installs or dependency/model changes during this continuation.
Gemma 4 E4B Q4_K_XL, llama.cpp b11723-31288c9c6, ctx8192/out768, greedy/seed0/prefix cache.
Running image `sha256:f66a5229a3e0586339d16155e9fe09c37834d7a7f4134bbdee7360b5a1f2546d` verified.
Model `C:/Coding-projects/bintanong_workspace/MODELS/GEMMA_4_E4B/gemma-4-E4B-it-UD-Q4_K_XL.gguf`,
SHA256 `3cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80` inherited from Phase09, not rehashed.
SEA-LION E5 remains at external MODELS/SEA-LION-E5-Embedding-600M; verified-assets manifest SHA256
`cbaa707524cb89e928e5730bc59410e8dbb1b5dab9f4e37b40018084000c0f39` (weights unchanged).

Package draft-chunks SHA256 `480a0ff621991e6b06f89b2042a6c5c603c68eeb6672d65111f32e96f07c9fbf`;
seal `954d376e3c47e55856f2e7c959f4dd9b98f5195a2fb25242807e6081e4cabb8e`;
embedding set `f7a7f1b01770834c71838eccd6347ab1db798f0fe37917c9426fb79d93592218`.
Pin/config hashes and selected-review scope: activation results. All protected hashes rechecked unchanged.

## Deviations, owner rulings and risks

- 40 development cases, author-written expectations/single scorer; no independent ratings. Disciplinary fixes
  and shorthand list saw their probes. Single runs (owner), no condition B; main benchmark not rerun hosted.
- Route/entity F1, retrieval metrics, RAGAS/BATAYAN, claim annotations, SUS/UAT with 30 students, cold-start
  benchmark, throughput/peak memory were not measured. Report section 7 distinguishes these from measured results.
- 257 re-authored records use the owner activation directive, no per-chunk human approval. Source states,
  source gaps, undergraduate scope, unknown-versus-unmet and private-input separation preserved.
- Photos unsupported; real PSU sign-in remains owner-deferred. No institutional validation or deployment approval.
- Initial database password rejected; owner corrected it, read-only connection passed. Slow RPCs used existing
  functions through session-pooler psql with local timeout; no role/global timeout or RLS/grant changes.
- Machine local date is 29 Oct; predecessor records/release names say 30 Oct and were preserved unchanged.

## Next-phase boundary

No implementation phase is authorized next: Phase 13 deployment is cancelled. The structural validator may
return next_phase 13; that is not permission to create its plan or deploy. Hosted answer-quality benchmarking
remains an owner/Claude follow-up, separate from delivered smoke evidence. Do not repeat completed evaluations
or change prompts/models/scope without a new applicable decision.
