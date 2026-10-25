# Supporting completion facts: three-line prompt trial

Owner explicitly requested applying the three proposed instructions after reviewing
the [frontend/API investigation](2026-10-25-clarification-routing-history.md).

## Change

Commit f68135c changes only backend/bintanong_routing/prompt.py at runtime:
three instructions distinguish supporting completion/enrollment facts from requested
answer parts. Prompt version moves v19 -> v20; SHA256 is
f2316f89e31ca6f46f0b8622da7ecf3f5f7eaa49079e9af7035fc7c3e1d3a45c.
Two test files add delivery checks for separate/combined router modes and update the
version expectation. No frontend, validation, Prolog, source, dependency or model edit.

## Verification

- New transport/prompt-contract check: RED2 before edit; focused suite GREEN26 after.
  It checks guidance delivery and preserves an explicitly requested second part;
  it is not a live model-accuracy test.
- Broader routing/generation and related API regression selection:902 PASS32.95s,
  including the focused tests. Initial invocation named two nonexistent test files;
  it ran zero tests, then the corrected selection above passed.
- Existing full research composition, seven topics, active19-chunk/39-curriculum
  release, real model/Prolog, isolated session and synthetic student premises:

| Input | v19 baseline | v20 observation |
| --- | --- | --- |
| Original prerequisite question | Lists prerequisites and asks two completion questions | Same intended response |
| Filipino popup follow-up | Generic clarification, invented unknown part | One part; answered, documented unmet condition |
| English popup follow-up | Router-only probe invalid_reference | Full pipeline one part; answered, documented unmet condition |
| English IM wording with previous course context | Full pipeline generic clarification | One part; answered, documented unmet condition |
| Prerequisite question, completion facts and separate shifting question | Paired router check invalid_reference | unknown_requirement; still invents a third part |

The live runner exits1 on its mixed-message assertion, not the three targeted
follow-ups. A separate paired v19/v20 check confirms that mixed case already failed
before this patch. This is a bounded improvement, not a general routing-quality pass.
No unsupported result is forced through the existing validation guards.

## Local activation and limits

Only local frontend checkout is changed; backend357aa80 worktree/remote untouched.
API worker87176 was stopped after matching its exact uvicorn command/port. Existing
launcher restarted it on8021 to load v20; temporary chat context resets. Models and
encoder remain running. Readiness receipt is in the ignored evidence below.
API readiness and frontend health return200, with all five dependency probes true.
No authenticated owner-browser replay, full accepted-roster evaluation, latency
claim, university approval, source activation, deployment or push. Mixed-question
behavior and completion-state semantics remain open. Retry in a fresh chat with
the curriculum selected; do not interpret this as a persistent academic-record update.

Evidence: workspace audit-evidence/p11-20261025/clarification-loop/prompt-v20/:
results.json, *-captured.json, mixed-request.json, mixed-comparison.json,
api-restart.json, API logs and readiness.json. Runners remain one level above:
try_three_prompt_lines.py and compare_mixed_prompt.py. Baseline evidence is retained.
