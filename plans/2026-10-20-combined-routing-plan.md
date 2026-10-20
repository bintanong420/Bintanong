# Combined routing and style implementation plan

> Execute inline with executing-plans and TDD;one independent final review.

Goal:remove one normal model round trip while keeping separately validated route
and literal response-style evidence. Baseline30d1b17. Owner says continue the speed
work;[research/design choices](2026-10-20-fast-replies-results.md) and master12–14
are the specification. No claim of sub10s readiness;Phase09 remains active.

## Design and constraints

Create an explicit combined candidate beside the retained separate router. One
strict packet contains schema_version,interpretation (existing full Interpretation)
and style (existing StyleEvidence). Hoist existing referenced definitions into the
wrapper schema without dropping original audience/route/operation/style branches.
Compose scoped original task instructions and the same untrusted payload;route and
style remain distinct logical decisions,with no new keyword/language classifier.

Reuse exact quote anchoring,StyleEvidence.ground and validate_interpretation.
One whole-packet format repair maximum;no repair for a semantic/grounding failure,
timeout or capability hold. Physical call counts:attempts1or2,style_attempts0,
style_evidence retained. No silent fallback to the separate path or to RAG.

Trusted Orchestrator/RuntimeSettings/CLI select separate or combined. Retain
separate as default until the promotion check below passes. Keep transport,
support check,generation evidence,release/session/privacy/source guards and all
existing time/output/model/GPU settings. No downloads,dependencies,training or
accepted institutional benchmark edits. Known Hybrid citation flaw stays held;
the owner's current latency continuation prioritizes this isolated change,not
release activation or a claim that the quality flaw was corrected.

## Tasks

- [ ] RED/GREEN combined contract/schema/prompt/router in
  backend/bintanong_routing/combined.py;tests/test_routing_combined.py. Cover
  single-call style/route independence,strict fields/versions,shared repair bound,
  duplicate keys,grounding,missing capabilities,scope/unknown/session/quote guards,
  nested decoder constraints and honest evaluation metadata/call counts.
- [ ] RED/GREEN trusted profile selection in orchestrator.py,application.py,
  cli.py and evaluation.py;tests/test_combined_runtime_profile.py plus existing
  regression suites. No per-request/model-controlled profile selection.
- [ ] Run one fixed actual-model combined evaluation on the existing5fictional
  families/15English,Filipino,Taglish variants. Reuse p07 requested-work input and
  reference labels;keep gold outside prompts. Report every axis/per-language error,
  anchoring/repair/physical-call counts and actual prompt/schema/runtime hashes.
- [ ] Promotion requires all15route/effective/entity/claim/operation axes correct
  and no new style error on any previously correct case (baseline13/15styles).
  If unmet,retain separate default and combined opt-in;no prompt/seed sweep.
  These are software candidate acceptance checks,not institutional accuracy.
- [ ] One actual-service request per route using selected profile,with resident
  encoder startup separate. Compare measured call/tokens/latency and outputs to
  prior35–53s;do not infer speed benefit from fewer calls alone.
- [ ] Relevant regression gate,one independent final review,compact progress/
  checkpoint and dated results. Small explicit commits;preserve raw failures.

## Review focus and recovery

Check nested $ref resolution and full original constraints;both objects must parse
before dispatch. Wrong style quotes/foreign contexts cannot execute. Combined
repair reuses the original question,not the repair instruction. A language/route
disagreement remains visible as proposed vs effective;missing rules remain unknown.
Evaluation hashes must describe the combined packet rather than old separate calls.
Keep explicit separate mode for rollback and never relabel old captures as fresh.

Context consulted:thesis physical17–18/39–40,actual routing PNG,master12–14,standing
19October prompt decision. Undergraduate/advisory/structured-Prolog/source-gap rules
and one-week accuracy cap retained. Worktree p09 isolated;existing owner model root
workspace/MODELS and Python3.13 readiness environment reused. External raw/testtemp:
workspace/audit-evidence/p09-combined-routing-20261020/. No Phase10 work or API.
