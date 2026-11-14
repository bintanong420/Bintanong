# Short evidence references: software delivered, selection rejected

20 October 2026;Phase09 active. Plan5e63854/product42c5754 in p09.
[Plan](2026-10-20-short-evidence-references-plan.md) implements the previous
handoff's exact next action. [Response-time assessment](2026-10-20-response-time-research-assessment.md)
addresses the owner's architecture-specific research request. No accuracy/speed
trade is authorized. Canonical references and separate routing remain selected.

## Delivered boundary

The opt-in short profile gives each prepared evidence card a request-local e1..e32
label. A separate strict draft schema constrains actual allowed labels. Host code
restores canonical hashes before the existing draft/final guards and re-encodes
the canonical draft with the same mapping for the separate support checker.
Complete source text,kind,locators,source hashes/versions,structured context and
limitations survive. No arbitrary replacement in prose, global map, source
truncation, cache, checker bypass or unvalidated streaming was added.

Select only programmatically for developer experiments:
`Generator(...,reference_profile='short')` or
`RuntimeSettings(generation_reference_profile='short')`.
Both default to canonical. RuntimeRun records the generation profile separately
from routing. The existing CLI still uses canonical. Institutional contracts and
final claim/citation identities retain canonical hashes.

## Actual-model bounded observation

Reused exactly the three existing fictional RAG follow-up cases and six existing
structured Symbolic/Hybrid cases, each in English/Filipino/Taglish. No new
institutional question/label or settled source review. These are **generation-only**
inputs with prepared evidence; they do not execute routing,retrieval or Prolog.
The real local LLM performs draft generation and a separate support check.

| Existing case | Generation+checking,s | Output tokens,draft/check |
| --- | ---: | ---: |
| fictional-rag-en |9.933|83/52|
| fictional-rag-fil |9.778|94/52|
| fictional-rag-taglish |9.206|85/52|
| fictional-symbolic-en |9.674|85/52|
| fictional-symbolic-fil |9.588|85/52|
| fictional-symbolic-taglish |9.375|85/52|
| fictional-hybrid-en |12.340|115/64|
| fictional-hybrid-fil |13.321|131/64|
| fictional-hybrid-taglish |12.848|116/64|

All9returned answered/validated,18physical calls,one draft/check per case,zero
repairs. Reassembly checks independently verify all supplied passages/metadata,
canonical references and structured decisions unchanged. Agent language review
finds the requested styles acceptable in these9outputs;that is not owner review
or a general language-accuracy claim. Correct language/schema/mapping is not
correct content.

**Selection fails on actual claim scope despite positive checker verdicts:**

- `fictional-symbolic-taglish`,c1:"Eligible ang enrollment para sa FICTIONAL-101
  base sa supplied prerequisite check." The permitted result is the supplied
  prerequisite check, not full enrollment eligibility. Host-rendered narrow wording
  does not repair a broader generated claim.
- `fictional-hybrid-en`,c1:"To enroll in the fictional undergraduate service, one
  must submit Form Q at the Synthetic Student Desk." The cited documentary passage
  says to submit Form Q at that desk; it does not establish an enrollment purpose.
  Canonical eligibility metadata cannot silently add that purpose to the document.

The other Hybrid variants retain the generic service purpose. The English RAG
sentence is awkward ("To submit the ... service") but retains the supplied desk/
Form Q action; keep clarity distinct from a fabricated policy claim. These tiny
fictional families do not calibrate real-world correctness. No matched fresh
canonical control was run, so the two errors are absolute quality-gate failures,
not established causal regressions from shortening IDs. Earlier structured runs
already disclosed scope problems;this change does not claim to fix them.

Ruling:stop after the failed quality gate. The three planned full-service timing
requests are **NOT RUN**. No prompt/seed sweep or repair-prompt tuning. Short
references remain explicit experimental opt-in and are not selected for students.
These9–13second component observations are not complete-query measurements or a
controlled speedup. There is no new full-chain improvement or p95 established.
The selected historical full-service results remain35.662sRAG/35.058sSymbolic/
52.967sHybrid,with startup separately reported in the
[previous speed report](2026-10-20-fast-replies-results.md).

## Verification and independent assessment

Initial focused RED25failed on missing module/profile. Implementation GREEN129
passed2.67s. One test initially expected only its documentary citation;corrected
the expectation because canonical decision rendering also retains its rule source.
Additional wiring/support/outcome checks bring the new reference suite to29tests.
Product gate720passed3.58s,exit0,including existing generation/runtime and docs.
Raw commands/results are under workspace/audit-evidence/p09-short-references-20261020/.

One fresh independent reviewer inspected5e63854..42c5754 and all saved outputs;
no new P1/P2 software finding. It independently reproduced129passing focused tests
in2.79s and confirmed both semantic scope failures block selection. Equivalent
accuracy versus a matched canonical control,actual-model repairs,complete service
latency,p95 and student waiting acceptability remain unverified. Review does not
turn the positive same-model verdicts into correct claims.

Final explicit51-selection gate1963passed/66subtests89.42s,exit0. Exact command:
raw `verify-regressions.ps1`;complete output `final-regressions.log`. Delivery
manifest seals46raw/source files,all verified;SHA256
ce0f2e042f1e272dd6ebe58de3d2c75e5dc29ca1db90bcdc878bf167eee397fd.
Later delivery-doc logs are separate. The active [checkpoint](phase-09-checkpoint.md)
holds compact recovery state;this is not Phase09 completion or Phase10 advancement.

## Identities and recovery

Actual pre-inference source/input hashes and server props are in
`generation-pre-inference.json`;per-case traces retain exact message/schema hashes,
model outputs,usage/timings and effective sampler metadata. `assessment.json`
records the mechanical checks and agent scope observations. `observe.py generation`
is the executed bounded observer;`observe.py runtime` exists but was not executed.
It refuses overwriting prior outputs. All data are fictional and ignored.

Fresh runtime metadata:b11723-31288c9c6,context8192,output768,temperature0,seed0,
reasoningnone,cache_promptfalse,inference/generation240s. Docker image freshly
verified running asf66a5229a3e0586339d16155e9fe09c37834d7a7f4134bbdee7360b5a1f2546d.
Template SHA25674a88f94c57c14e22dcdbe08e94127f42b87c6f584cb73838e73e32126f3f6b3.
Prior selected placement35/43layers/512MiB fit was reused,not re-tuned. No new
image,model,dependency,lock or database changes. Existing owner weights remain
at workspace/MODELS/GEMMA_4_E4B/gemma-4-E4B-it-UD-Q4_K_XL.gguf;inherited GGUF
SHA2563cf61de12daa015ee0f7b68e7b7c541405bf220e1e942bad8b47cab827d7df80
was not freshly rehashed. Existing readiness Python3.13.7 reused.

Next action is a bounded design for associating generated decision explanations
with their canonical structured support and controlling scope, using these saved
failures before another speed experiment. Keep the existing Hybrid documentary-
only support hold,separate profile's prior Taglish issues and absent explicit
post-retrieval reconsideration visible. No75-case institutional evaluation,
activation,student API,push,merge or deployment occurred.
