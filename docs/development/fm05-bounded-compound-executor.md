# FM-05: bounded compound eligibility research executor

This is the first staged fix, not a full production FM-05 fix.
The existing P12 path still refuses compound_request, and this PR does not
change that guard, the candidate answer generator, or the student-facing API.

## Implemented

- Developer callable run_bounded_compound(text, context, transport, releases):
  one pinned synthetic release and one normal LLM routing pass.
- Exactly two independent check_prerequisite_eligibility operations, one
  program and one curriculum edition, each bound to its own question part.
- Each part is independently checked by P12's existing course identity,
  curriculum scope, user-fact, capability registry and signature validators.
- Sequential symbolic execution respects the per-runtime worker admission.
- One candidate-only CandidateEvidence per part, checked by release and
  rule provenance checks. Unknown grades do not become passed.
- A failed first check does not cause an unverified eligibility result
  and does not prevent the second check from being attempted.
- Result states complete, partial, withheld, not official enrollment approval.

## Test command

    python -m pytest tests/test_compound_symbolic.py tests/test_routing_validation.py tests/test_orchestration_pipeline.py tests/test_orchestration_adapters.py -q

Synthetic tests are not actual institutional correctness measurements.

## Uploaded 72-case benchmark coverage

The checklist contains 24 questions x three language versions. Its marks:
47 Y, 8 P, 14 N and 3 blank. Baseline columns remain unfilled. The 24
questions do not directly test two independent symbolic operations in one
student turn. This new set introduces synthetic two-target cases. Keep the
uploaded annotated CSV private; do not commit it into the public repository.

## Still not live

No CandidateAnswer or Generator integration, no frontend exposure, no
heterogeneous or mixed RAG+multiple-Prolog operations, and no original PDF
adjudication. Do not enable a serving route until per-part answer/citation
contracts are independently tested.
