# Bintanong: selective symbolic domain boundary (candidate)

Source: Nov 2026 thesis manuscript, Chapter III (FOL activation cases) and the current
runtime architecture diagram in `Context/bintanong_current_runtime_architecture.png`.
This candidate copies the evaluated image unchanged from `p12-evaluation-harness`
and starts from the code fixes in `p12-post-gathering-fixes`.

## Invariant

**Prolog is a bounded curriculum constraint executor.** Being a university policy,
an official procedure, or a documentary question is not, by itself, permission to
run Prolog. A request invokes the symbolic path only when it contains a separately
supported and validated curriculum operation. Simple printed course facts may use
the structured catalog path without evaluating a Prolog constraint.

- **Institutional documents:** RAG (Student Handbook, Citizen's Charter, USG/CSG
  rules, forms, fees, office processes). Verify source-specific claims and cite.
- **Curriculum catalog:** reviewed facts, course identity, prerequisites as printed,
  and term course listings. This does not imply a student-specific eligibility
  conclusion.
- **Curriculum constraints:** prerequisite/eligibility checks, dependency/impact
  analysis, term assessment, study plans, earliest possible prerequisite path.
  Evaluate only typed, registry-accepted operations on the selected curriculum.
- **Hybrid:** a single student message *independently requests* a documentary
  answer and a structured curriculum operation. Run each on its own sources and
  merge only after identity, release and answer support checks.

`backend/bintanong_routing/domains.py` is the central host-owned allowlist and
evidence-to-route mapping, not a model-generated goal. Adding a new symbolic
operation requires assigning it an explicit curriculum domain and extending
registry/runtime/gold tests. Do not add policy operation names merely because a
Charter or Handbook contains a conditional sentence.

## Known limitations of this first port

- The LLM still decides the meaning of requested parts and operations. The
  allowlist cannot prove *correct intent*; tests must use independent gold labels.
- This does not add arbitrary institutional policy reasoning to Prolog.
- Compound structured requests are still bounded by the current single-operation
  dispatch, and are not silently split by this patch.
- A document part with no selected topic may still be withheld; the wording now
  states it was not checked, rather than asserting the sources lack an answer.
- No runtime restart, live-model benchmark, PDF-to-ledger adjudication or source
  activation occurs in this commit.

## Required validation before promotion

```powershell
python -m pytest tests/test_routing_domains.py tests/test_routing_validation.py tests/test_routing_operation_coverage.py tests/test_routing_compile.py -q
python -m pytest tests/test_orchestration_pipeline.py tests/test_generation_pipeline.py -q
```

Compare the same cases under `BINTANONG_ROUTER_COMPILE=0` and `=1` on the
isolated development stack: policy-only (RAG, zero symbolic calls), catalog-only
(structured fact lookup, no constraint decision), prerequisite check (Symbolic),
and separately requested prerequisite plus form-processing procedure (Hybrid).
Capture the actual compiled profile, branch SHA, curriculum release and model
config. Use separate manually reviewed PDF-derived expected answers. Do not
deploy from this candidate branch until those tests are green.

## Follow-up risk controls (Aurora comparison / FM-07)

The candidate now constrains research-mode `uncalibrated -> ok` retrieval
promotion: only the calibration marker may be present, and every explicitly
requested claim must map to nonblank reviewed fields inside actually emitted
passages for the same topic. This is **not** an independent semantic-sufficiency
verdict. Generation still needs claim support, and live regression tests remain
necessary. The operation-domain allowlist also gates the symbolic adapter's
execution, not only router validation; the reviewed catalog operations do not
execute constraint rules. The original P12 protections for unknown student grades,
curriculum identity and Hybrid fail-closed errors are preserved.

Run:
```powershell
python -m pytest tests/test_retrieval_calibration_gate.py tests/test_routing_domains.py tests/test_orchestration_adapters.py tests/test_orchestration_pipeline.py tests/test_orchestration_research_evidence.py -q
```

The remaining independently adjudicated target/intent selection, multi-operation
fan-out and PDF-to-rule consistency checks should not be represented as fixed by
this PR.
